from shared.database import db_manager
from api.services.formatters import _drawer_title, _format_time, _format_date

async def _get_client_memory(client_id: str, context_query: str = "general") -> list:
    """Fetch recent behavioural memory items for a client (chronological, fast)."""
    try:
        resp = db_manager.client.table("behavioural_memory")\
            .select("content, created_at").eq("client_id", client_id)\
            .order("created_at", desc=True).limit(5).execute()
        return [
            {
                "date": _format_date(m.get("created_at")),
                "text": m.get("content", "")
            }
            for m in (resp.data or [])
        ]
    except Exception:
        return []

async def _build_drawer_data(client_id: str, event: dict, client: dict) -> dict:
    return await _build_drawer_data_fast(client_id, event, client)

async def _build_drawer_data_fast(client_id: str, event: dict, client: dict, portfolio_override: dict = None, memory_override: list = None) -> dict:
    """Build drawer data for a risk event card. Optimized to use pre-fetched data."""
    event_type = event.get("event_type", "market_risk")
    classification = event.get("deterministic_classification") or {}
    interpretation = event.get("ai_interpretation") or {}
    
    # Special: Delegate Meeting Briefs
    if event_type == "meeting_brief":
        return await _build_meeting_drawer_fast(client_id, event, interpretation, portfolio_override, memory_override)
    
    is_macro = classification.get("is_macro_grouping", False)
    
    # Portfolio (Skip for macro group events)
    portfolio = {}
    portfolio_items = []
    
    # Behaviour (Skip for macro group events)
    behav_profile = {}
    risk_aversion = 50
    drawdown_tolerance = 50
    
    # Memory (Skip for macro group events)
    memory_items = []
    
    if not is_macro:
        # Use pre-fetched portfolio if available
        if portfolio_override:
            portfolio = portfolio_override
        else:
            try:
                port_resp = db_manager.client.table("portfolios")\
                    .select("holdings").eq("client_id", client_id).execute()
                if port_resp.data:
                    portfolio = port_resp.data[0]
            except Exception:
                 pass
        
        if portfolio:
            holdings = portfolio.get("holdings", [])
            colors = ["#1570ef", "#f79009", "#12b76a", "#7f56d9", "#d0d5dd"]
            
            # Aggregate exposures by sector
            sector_exposures = {}
            for h in holdings:
                sector = h.get("sector", h.get("name", "Other"))
                sector_exposures[sector] = sector_exposures.get(sector, 0.0) + h.get("exposure_percentage", 0.0)
            
            sorted_sectors = sorted(sector_exposures.items(), key=lambda x: x[1], reverse=True)
            
            for i, (sector, exposure) in enumerate(sorted_sectors[:5]):
                portfolio_items.append({
                    "label": sector,
                    "value": round(exposure * 100, 1),
                    "color": colors[i % len(colors)]
                })

        behav_profile = client.get("behavioural_profile", {})
        risk_aversion = behav_profile.get("risk_aversion", 50)
        drawdown_tolerance = behav_profile.get("drawdown_tolerance", 50)
        
        if memory_override is not None:
             memory_items = [
                {"date": _format_date(m.get("created_at")), "text": m.get("content", "")}
                for m in memory_override[:5]
            ]
        else:
            memory_items = await _get_client_memory(client_id, context_query=f"reaction to {event_type} conditions")
    
    # ... (rest of the formatting logic) ...
    process_trace = []
    if event_type == "morning_intelligence":
        process_trace.append("Agent: MorningIntelligenceAgent")
        process_trace.append("Tools: search_market_news, fetch_live_market_data, get_sector_performance")
    elif event_type == "market_interrupt":
        process_trace.append("Agent: MarketPulseAgent")
        process_trace.append("Tools: search_geopolitical_events, fetch_live_market_data")
    else:
        process_trace.append("Agent: RiskInterpretationAgent")
        process_trace.append("Tools: retrieve_relevant_memory, get_sector_performance")

    trace = []
    reason = classification.get("reason", "")
    if reason:
        trace.append(reason)
    if interpretation:
        if interpretation.get("consequence_if_ignored"):
            trace.append(f"Consequence: {interpretation['consequence_if_ignored']}")
        if interpretation.get("behavioural_nuance"):
            trace.append(f"Nuance: {interpretation['behavioural_nuance']}")
    trace.append(f"Urgency: {event.get('urgency', 'medium')}")
    
    volatility = None
    volatility_label = None
    if event_type in ("market_risk", "market_interrupt"):
        perf = classification.get("performance")
        if perf is not None:
            volatility = f"{perf*100:+.1f}%"
            volatility_label = "Live Breach Detected" if abs(perf) > 0.05 else "Approaching Threshold"
        elif classification.get("ftse_delta"):
            volatility = f"{classification['ftse_delta']*100:+.1f}%"
            volatility_label = "Significant Movement"
    elif event_type == "behavioural_risk":
        volatility = f"{classification.get('trigger_performance', 0)*100:+.1f}%"
        volatility_label = "Emotional Trigger Zone"
    
    drawer = {
        "title": _drawer_title(event_type),
        "portfolio": portfolio_items,
        "volatility": volatility,
        "volatilityLabel": volatility_label,
        "behaviour": {"riskAversion": risk_aversion, "drawdownTolerance": drawdown_tolerance} if behav_profile else None,
        "behaviourNote": interpretation.get("behavioural_nuance") or behav_profile.get("note", ""),
        "memory": memory_items[:3],
        "trace": trace,
        "processTrace": process_trace,
        "proactive_thought": interpretation.get("proactive_thought") or classification.get("proactive_thought", ""),
        "headline": interpretation.get("headline", ""),
        "consequence": interpretation.get("consequence_if_ignored", ""),
    }
    
    if event_type == "market_interrupt":
        drawer["isMarketInterrupt"] = True
        drawer["marketContext"] = classification.get("reason", "Market movement detected.")
        drawer["exposedClients"] = classification.get("exposed_clients", [])
    
    if event_type == "morning_intelligence":
        drawer["isMorningBrief"] = True
        drawer["summary"] = classification.get("impact_summary") or classification.get("market_summary", "")
        drawer["possibleImpact"] = drawer["summary"]
        drawer["suggestions"] = interpretation.get("suggested_actions", [])
        drawer["risks"] = interpretation.get("top_risks", []) or classification.get("top_risks", [])
        drawer["news"] = classification.get("key_news", [])
    
    if event_type == "behavioural_risk":
        drawer["trace"].append(f"Historical Context: {classification.get('historical_pattern', 'No previous pattern recorded.')}")
        drawer["trace"].append(f"Panic Score: {classification.get('panic_score', 0)}/10")
    
    return drawer


async def _build_meeting_drawer(client_id: str, meeting: dict, brief: dict) -> dict:
    return await _build_meeting_drawer_fast(client_id, meeting, brief)

async def _build_meeting_drawer_fast(client_id: str, meeting: dict, brief: dict, portfolio_override: dict = None, memory_override: list = None) -> dict:
    """Build drawer data for a meeting brief card. Optimized to avoid DB calls."""
    # Portfolio
    portfolio_items = []
    portfolio = None
    
    if portfolio_override:
        portfolio = portfolio_override
    else:
        try:
            port_resp = db_manager.client.table("portfolios")\
                .select("holdings").eq("client_id", client_id).execute()
            if port_resp.data:
                portfolio = port_resp.data[0]
        except Exception:
            pass
            
    if portfolio:
        holdings = portfolio.get("holdings", [])
        colors = ["#1570ef", "#7f56d9", "#12b76a", "#d0d5dd"]
        
        # Aggregate exposures by sector
        sector_exposures = {}
        for h in holdings:
            sector = h.get("sector", h.get("name", "Other"))
            sector_exposures[sector] = sector_exposures.get(sector, 0.0) + h.get("exposure_percentage", 0.0)
            
        sorted_sectors = sorted(sector_exposures.items(), key=lambda x: x[1], reverse=True)
        
        for i, (sector, exposure) in enumerate(sorted_sectors[:4]):
            portfolio_items.append({
                "label": sector,
                "value": round(exposure * 100, 1),
                "color": colors[i % len(colors)]
            })
    
    # Client behaviour logic (brief already has summary)
    memory_items = []
    if memory_override is not None:
         memory_items = [
            {"date": _format_date(m.get("created_at")), "text": m.get("content", "")}
            for m in memory_override[:5]
        ]
    else:
        memory_items = await _get_client_memory(client_id)
    
    return {
        "title": "Pre-Meeting Brief",
        "portfolio": portfolio_items,
        "volatility": None,
        "volatilityLabel": "Within Mandate",
        "behaviour": None,
        "behaviourNote": brief.get("client_summary", ""),
        "memory": memory_items[:3],
        "trace": [
            f"Meeting scheduled: {_format_time(meeting.get('meeting_timestamp'), time_only=True)} today",
            "Client brief auto-generated"
        ],
        "meetingContext": {
            "portfolioPerformance": brief.get("portfolio_performance"),
            "priorityTopic": brief.get("priority_strategic_talking_point"),
            "keyAssets": brief.get("key_asset_allocation", []),
            "taxes": brief.get("tax_opportunities", []),
            "memories": brief.get("recent_life_events_or_memories", []),
            "agenda": brief.get("suggested_agenda_items", []),
            "compliance": brief.get("compliance_reminders", [])
        },
        "proactive_thought": brief.get("proactive_thought")
    }
