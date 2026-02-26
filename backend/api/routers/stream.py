from fastapi import APIRouter, Request
from datetime import datetime
from fastapi.responses import StreamingResponse
import asyncio
from backend.shared.database import db_manager
from backend.api.services.formatters import _event_to_text, _build_chips, _format_time, _format_date, _minutes_until
from backend.api.services.drawer import _build_drawer_data, _build_meeting_drawer, _build_drawer_data_fast, _build_meeting_drawer_fast
from backend.api.services.broadcaster import broadcaster
from backend.shared.logging import setup_logger

logger = setup_logger("api.stream")
router = APIRouter()

@router.get("/stream/live")
async def stream_live_events(request: Request):
    """
    SSE endpoint for real-time intelligence updates.
    The frontend connects to this and receives 'update' messages
    whenever new intelligence is generated.
    """
    async def event_generator():
        queue = await broadcaster.connect()
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {message}\n\n"
                except asyncio.TimeoutError:
                    yield f": keepalive\n\n"
        finally:
            broadcaster.disconnect(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )


@router.get("/stream")
async def get_stream(filter: str = "all", search: str = ""):
    """
    Returns the unified intelligence stream for the frontend.
    Aggregates: risk_events, meeting_briefs, draft_actions, heartbeat_logs.
    Returns { stream: [...], tabs: [...] } with dynamic action-cluster tabs.
    """
    logger.info(f"Fetching stream with filter: {filter}, search: {search}")
    messages = []
    
    # 1. Fetch basic client summary
    clients_resp = db_manager.client.table("clients")\
        .select("id, first_name, last_name, behavioural_profile")\
        .execute()
    clients_map = {c["id"]: c for c in (clients_resp.data or [])}
    
    # 2. Batch-fetch all pending drafts
    all_drafts = {}
    try:
        drafts_resp = db_manager.client.table("draft_actions")\
            .select("id, risk_event_id, draft_content")\
            .eq("status", "pending")\
            .limit(100)\
            .execute()
        for d in (drafts_resp.data or []):
            rid = d.get("risk_event_id")
            if rid:
                all_drafts.setdefault(rid, []).append(d)
    except Exception as e:
        logger.error(f"Error batch-fetching drafts: {e}")

    # 2a. Pre-fetch ALL portfolios and memory
    portfolios_resp = db_manager.client.table("portfolios").select("client_id, holdings").execute()
    portfolios_map = {p["client_id"]: p for p in (portfolios_resp.data or [])}
    
    memory_resp = db_manager.client.table("behavioural_memory")\
        .select("client_id, content, created_at")\
        .order("created_at", desc=True)\
        .limit(100)\
        .execute()
    memory_batch = {}
    for m in (memory_resp.data or []):
        cid = m.get("client_id")
        if cid:
            memory_batch.setdefault(cid, []).append(m)
    
    # 3. Risk Events (Unresolved)
    tab_counts = {}  # { event_type: { total, high, critical } }
    
    try:
        summary_cols = "id, client_id, event_type, urgency, deterministic_classification, ai_interpretation, created_at"
        events_resp = db_manager.client.table("risk_events")\
            .select(summary_cols)\
            .eq("status", "open")\
            .order("created_at", desc=True)\
            .limit(200)\
            .execute()
            
        grouped_events = {}
        morning_brief_msg = None
        morning_brief_cards = []
        
        for event in (events_resp.data or []):
            try:
                client = clients_map.get(event["client_id"]) or {}
                client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip() or "Unknown Client"
                cls = event.get("deterministic_classification") or {}
                interp = event.get("ai_interpretation") or {}
                
                is_master = cls.get("is_master_brief", False)
                is_macro = cls.get("is_macro_grouping", False)
                etype = event.get("event_type")
                is_morning = etype in ["morning_intelligence", "market_interrupt"]
                urgency = event.get("urgency", "medium")
                
                # Track tab counts for ALL non-master events
                if etype and not is_master:
                    if etype not in tab_counts:
                        tab_counts[etype] = {"total": 0, "high": 0, "critical": 0}
                    tab_counts[etype]["total"] += 1
                    if urgency in ("high", "critical"):
                        tab_counts[etype]["high"] += 1
                    if urgency == "critical":
                        tab_counts[etype]["critical"] += 1
                
                # Search filter
                if search:
                    sl = search.lower()
                    if (sl not in client_name.lower() and 
                        sl not in (etype or "").replace("_", " ").lower() and
                        sl not in cls.get("reason", "").lower()):
                        continue
                
                event_drafts = all_drafts.get(event["id"], [])
                client_port = portfolios_map.get(event["client_id"])
                client_mems = memory_batch.get(event["client_id"], [])
                
                drawer_data = await _build_drawer_data_fast(
                    event["client_id"], event, client, 
                    portfolio_override=client_port, 
                    memory_override=client_mems
                )
                
                card = {
                    "id": event["id"],
                    "type": etype or "market_risk",
                    "urgency": urgency,
                    "chips": _build_chips(etype or "", cls, event.get("urgency", 3)),
                    "drawerData": drawer_data,
                    "isDraft": False,
                    "isMasterBrief": is_master,
                    "isMacroGrouping": is_macro,
                    "client": client_name
                }
                
                draft_card = None
                if event_drafts and not (is_master or is_macro):
                    draft = event_drafts[0]
                    draft_card = {
                        "id": draft["id"],
                        "type": "draft",
                        "client": client_name,
                        "chips": ["Draft Ready", "Pending Approval"],
                        "drawerData": {
                            "title": "Draft Communication",
                            "isDraft": True,
                            "subject": (draft.get("draft_content") or {}).get("subject", ""),
                            "body": (draft.get("draft_content") or {}).get("body", ""),
                        },
                        "isDraft": True,
                    }

                if is_master and is_morning:
                    market_summary = cls.get("market_summary", "")
                    critical_news = cls.get("critical_news", [])
                    
                    summary_bullets = []
                    # 1. Critical News at the top
                    for news in critical_news:
                        summary_bullets.append(f"🚨 NEWS: {news}")
                    
                    # 2. Market Summary
                    if market_summary:
                        summary_bullets.append(market_summary)
                    
                    if not summary_bullets:
                        summary_bullets = ["Market analysis pending..."]
                        
                    logger.info(f"MORNING_INT_DEBUG: Sending {len(summary_bullets)} bullets to ID {event['id']}")
                        
                    morning_brief_msg = {
                        "id": event["id"],
                        "type": "morning_intelligence",
                        "timestamp": _format_time(event.get("created_at")),
                        "client": "Adviser Dashboard",
                        "text": f"Market Intelligence ({len(critical_news)})",
                        "summary": summary_bullets,
                        "timeAgo": _format_time(event.get("created_at")),
                    }
                elif is_morning and (is_macro or etype == "morning_intelligence"):
                    if is_macro:
                        card["client"] = cls.get("impact_title", "Macro Risk")
                        card["drawerData"]["title"] = card["client"]
                    else:
                        headline = _event_to_text(etype or "", client_name, cls, interp)
                        card["client"] = client_name
                        card["impact"] = headline
                    
                    morning_brief_cards.append(card)
                    if draft_card:
                        morning_brief_cards.append(draft_card)
                else:
                    if etype not in grouped_events:
                        grouped_events[etype] = []
                    grouped_events[etype].append({
                        "event": event,
                        "client_name": client_name,
                        "card": card,
                        "draft_card": draft_card,
                        "interpretation": interp,
                        "classification": cls
                    })
                    
            except Exception as item_err:
                logger.error(f"Error processing risk event {event.get('id')}: {item_err}")
                
        # Combine morning brief
        if morning_brief_msg:
            morning_brief_msg["cards"] = morning_brief_cards
            messages.append(morning_brief_msg)

        # Process grouped regular events
        for etype, items in grouped_events.items():
            # Filter by action-cluster tab
            if filter != "all" and filter != etype:
                continue
                
            if len(items) == 1:
                item = items[0]
                event = item["event"]
                messages.append({
                    "id": event["id"],
                    "type": etype,
                    "timestamp": _format_time(event.get("created_at")),
                    "client": item["client_name"],
                    "text": _event_to_text(etype, item["client_name"], item["classification"], item["interpretation"]),
                    "summary": _build_summary(item["interpretation"]),
                    "cards": [item["card"]] + ([item["draft_card"]] if item["draft_card"] else []),
                    "timeAgo": _format_time(event.get("created_at")),
                })
            else:
                first_item = items[0]
                event = first_item["event"]
                
                type_summary_labels = {
                    "compliance_exposure": f"Risk mandate drift detected for {len(items)} clients",
                    "pension_allowance": f"Pension Tapering alerts for {len(items)} high-income clients",
                    "isa_optimization": f"ISA allowance opportunities for {len(items)} clients",
                    "tax_opportunity": f"Tax optimization windows open for {len(items)} clients",
                    "vulnerability_alert": f"Consumer Duty: {len(items)} clients flagged for vulnerability assessment",
                    "market_risk": f"Market volatility thresholds breached for {len(items)} clients",
                    "behavioural_risk": f"Behavioural friction detected for {len(items)} clients",
                    "cgt_exposure": f"Capital Gains Tax exposure for {len(items)} clients",
                }
                
                summary_text = type_summary_labels.get(etype, f"Multiple {etype.replace('_', ' ').title()} events detected")
                
                cards = []
                summaries = []
                for itm in items:
                    cards.append(itm["card"])
                    if itm["draft_card"]:
                        cards.append(itm["draft_card"])
                    itm_summaries = _build_summary(itm["interpretation"])
                    if itm_summaries:
                        summaries.append(f"{itm['client_name']}: {itm_summaries[0]}")
                
                messages.append({
                    "id": f"group-{etype}-{event['id']}",
                    "type": etype,
                    "timestamp": _format_time(event.get("created_at")),
                    "client": "Strategic Alert",
                    "text": summary_text,
                    "summary": summaries[:3],
                    "cards": cards,
                    "timeAgo": _format_time(event.get("created_at")),
                    "clientCount": len(items),
                })
    except Exception as e:
        logger.error(f"Error fetching risk events: {e}")

    # 4. Upcoming Meetings
    if filter in ("all", "meeting"):
        try:
            brief_cols = "id, client_id, created_at, brief_json, meeting_timestamp"
            briefs_resp = db_manager.client.table("meeting_briefs")\
                .select(brief_cols).order("created_at", desc=True).limit(3).execute()
                
            for brief in (briefs_resp.data or []):
                try:
                    client = clients_map.get(brief["client_id"], {})
                    client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip() or "Unknown Client"
                    
                    if search and search.lower() not in client_name.lower():
                        continue
                    
                    brief_data = brief.get("brief_json", {})
                    
                    drawer_data = await _build_meeting_drawer_fast(
                        brief["client_id"], brief, brief_data, 
                        portfolio_override=portfolios_map.get(brief["client_id"]),
                        memory_override=memory_batch.get(brief["client_id"], [])
                    )
                    
                    card = {
                        "id": brief["id"],
                        "type": "meeting_brief",
                        "client": client_name,
                        "chips": ["Meeting Prep", f"Risk: {brief_data.get('risk_alignment_notes', 'Aligned')}"],
                        "drawerData": drawer_data,
                        "isDraft": False,
                    }
                    
                    messages.append({
                        "id": brief["id"],
                        "type": "meeting",
                        "timestamp": _format_time(brief.get("created_at")),
                        "client": client_name,
                        "text": f"Upcoming brief for {client_name} generated.",
                        "cards": [card],
                        "timeAgo": _format_time(brief.get("created_at")),
                    })
                except Exception as item_err:
                    logger.error(f"Error processing meeting brief {brief.get('id')}: {item_err}")
        except Exception as e:
            logger.error(f"Error fetching meeting briefs: {e}")

    # 5. Heartbeat Logs — only on "all" tab
    if filter == "all":
        try:
            logs_resp = db_manager.client.table("heartbeat_logs")\
                .select("*").order("created_at", desc=True).limit(2).execute()
            
            for log in (logs_resp.data or []):
                summary = log.get("result_summary", "")
                messages.append({
                    "id": str(log.get("id", "")),
                    "type": "heartbeat",
                    "timestamp": _format_time(log.get("created_at")),
                    "client": "System / AtlasEngine",
                    "text": f"{log.get('sweep_type', 'Heartbeat').replace('_', ' ').title()} completed. {summary}",
                    "cards": [],
                    "timeAgo": _format_time(log.get("created_at")),
                })
        except Exception as e:
            logger.error(f"Error fetching heartbeat logs: {e}")

    # Sort chronologically
    messages.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)

    # ─── BUILD DYNAMIC TABS ──────────────────────────────────
    TAB_LABELS = {
        "market_risk": "Market Risk",
        "isa_optimization": "ISA Optimization",
        "cgt_exposure": "CGT Exposure",
        "pension_allowance": "Pension Tapering",
        "compliance_exposure": "Compliance",
        "behavioural_risk": "Behavioural",
        "vulnerability_alert": "Vulnerability",
        "tax_opportunity": "Tax Window",
        "market_interrupt": "Market Alert",
        "morning_intelligence": "Morning Brief",
    }
    
    total_all = sum(v["total"] for v in tab_counts.values())
    high_all = sum(v["high"] for v in tab_counts.values())
    
    tabs = [{"key": "all", "label": "All", "count": total_all, "highCount": high_all}]
    for etype, counts in sorted(tab_counts.items(), key=lambda x: x[1]["total"], reverse=True):
        tabs.append({
            "key": etype,
            "label": TAB_LABELS.get(etype, etype.replace("_", " ").title()),
            "count": counts["total"],
            "highCount": counts["high"],
        })

    return {"stream": messages, "tabs": tabs}


def _build_summary(interpretation: dict) -> list:
    """Build summary bullet points from AI interpretation."""
    if not interpretation:
        return []
    bullets = []
    if interpretation.get("consequence_if_ignored"):
        bullets.append(interpretation["consequence_if_ignored"])
    if interpretation.get("behavioural_nuance"):
        bullets.append(interpretation["behavioural_nuance"])
    if interpretation.get("compliance_note"):
        bullets.append(interpretation["compliance_note"])
    return bullets


@router.get("/live-strip")
async def get_live_strip():
    """
    Returns live market data and aggregate counts for the intelligence strip.
    Field names match frontend expectations (flat structure).
    """
    try:
        resp = db_manager.client.table("market_snapshots")\
            .select("*").order("timestamp", desc=True).limit(1).execute()
        
        snapshot = resp.data[0] if resp.data else {}
        ftse = snapshot.get("ftse_100_value", 0)
        
        # Calculate impact metrics
        events_resp = db_manager.client.table("risk_events")\
            .select("id, client_id").eq("status", "open").execute()
            
        open_risks = len(events_resp.data) if events_resp.data else 0
        impacted_clients = len(set([e["client_id"] for e in (events_resp.data or [])]))
        
        # Dynamic meetings count for today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        meetings_resp = db_manager.client.table("meeting_briefs")\
            .select("id", count="exact")\
            .gte("created_at", today_start)\
            .execute()
        meetings_today = meetings_resp.count if meetings_resp.count is not None else 0
        
        # Sector performance from snapshot
        sector_perf = snapshot.get("sector_performance") or {}
        
        return {
            "ftse_100": ftse if ftse else None,
            "clients_impacted": impacted_clients,
            "open_risks": open_risks,
            "meetings_today": meetings_today,
            "sectors": sector_perf
        }
    except Exception as e:
        logger.error(f"Error fetching live strip: {e}")
        return {}

@router.get("/heartbeat-status")
async def get_heartbeat_status():
    """
    Returns when the last heartbeat ran and estimated next run.
    Field names match frontend expectations (last_run_text / next_run_text).
    """
    try:
        resp = db_manager.client.table("heartbeat_logs")\
            .select("*").eq("sweep_type", "book_sweep")\
            .order("created_at", desc=True).limit(1).execute()
            
        status = {"last_run_text": "Unknown", "next_run_text": "Pending"}
        if resp.data:
            last_run = resp.data[0].get("created_at")
            mins_ago = _minutes_until(last_run)
            status["last_run_text"] = f"{mins_ago} min ago"
            
            # Assume 30 min schedule
            next_run_mins = max(0, 30 - mins_ago)
            status["next_run_text"] = f"{next_run_mins} min"
            
        return status
    except Exception as e:
        logger.error(f"Error fetching heartbeat status: {e}")
        return {"last_run_text": "Error", "next_run_text": "Error"}
