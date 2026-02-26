import asyncio
from datetime import datetime, timezone
from reasoning.classifiers import RiskClassifier
from reasoning.workflows import intelligence_workflow
from shared.models import EventStatus, EventType
from api.services.custodian import LiveCustodianClient
from api.services.broadcaster import broadcaster
from shared.database import db_manager
from shared.logging import setup_logger
from mcp_server.main import fetch_comprehensive_market_intel

logger = setup_logger("heartbeat")

async def run_heartbeat():
    """
    Heartbeat Engine: Every 30 minutes, detect new risk events.
    1. Check for global Market Interrupts via Agent (Pulse check).
    2. Scan all portfolios for deterministic risks.
    """
    logger.info("Starting agent-led heartbeat cycle")
    
    portfolios_scanned = 0
    risks_found = 0
    
    try:
        # 1. Pull market snapshot
        market_snapshot_resp = db_manager.client.table("market_snapshots")\
            .select("*")\
            .order("timestamp", desc=True)\
            .limit(1)\
            .execute()
        
        if not market_snapshot_resp.data:
            logger.warning("No market snapshot found. Skipping heartbeat.")
            return
            
        market_snapshot = market_snapshot_resp.data[0]
        
        # PROACTIVE: Fetch comprehensive market intel once for all agent analysis
        logger.info("Fetching shared market intelligence context for workflow")
        market_intel = await fetch_comprehensive_market_intel()
        
        # 2. PROACTIVE: Market Pulse Check (Deterministic)
        # We can move this to a deterministic rule or a simple LLM call if needed.
        # For now, we rely on deterministic RiskClassifier in the loop.
        
        # 3. Get all clients for proactive sweep
        all_clients = db_manager.get_all("clients")
        
        for client in all_clients:
            client_id = client["id"]
            
            # 4. Proactive Vulnerability Assessment
            memories_resp = db_manager.client.table("behavioural_memory")\
                .select("content").eq("client_id", client_id).execute()
            memories = [m["content"] for m in memories_resp.data] if memories_resp.data else []
            
            from reasoning.classifiers import VulnerabilityAssessor
            v_report = VulnerabilityAssessor.assess(client, memories)
            
            db_manager.update("clients", client_id, {
                **v_report,
                "last_proactive_check": datetime.now(timezone.utc).isoformat()
            })

            portfolio = LiveCustodianClient.get_live_portfolio(client_id)
            if not portfolio: continue
                
            portfolios_scanned += 1
            
            # 5. Standard deterministic filters (RiskClassifier)
            risks = []
            m_risk = RiskClassifier.classify_market_risk(portfolio, market_snapshot)
            if m_risk: risks.append(m_risk)
            
            t_opp = RiskClassifier.classify_tax_opportunity(client, portfolio)
            if t_opp: risks.append(t_opp)
            
            p_risk = RiskClassifier.classify_pension_allowance(client)
            if p_risk: risks.append(p_risk)
            
            c_exp = RiskClassifier.classify_compliance_exposure(portfolio)
            if c_exp: risks.append(c_exp)
            
            b_risk = RiskClassifier.classify_behavioural_risk(client, market_snapshot)
            if b_risk: risks.append(b_risk)
            
            # 6. Deduplicate and Insert
            for risk in risks:
                etype = risk["event_type"]
                etype_str = etype.value if hasattr(etype, "value") else str(etype)
                
                existing = db_manager.client.table("risk_events")\
                    .select("*")\
                    .eq("client_id", client_id)\
                    .eq("event_type", etype_str)\
                    .eq("status", EventStatus.OPEN.value)\
                    .execute()
                
                if not existing.data:
                    # PROACTIVE: Call IntelligenceWorkflow with SHARED market intel
                    interpretation = await intelligence_workflow.interpret_risk(client_id, risk, market_context=market_intel)
                    
                    risk_data = {
                        "client_id": client_id,
                        "event_type": risk["event_type"],
                        "urgency": risk["urgency"],
                        "deterministic_classification": risk["deterministic_classification"],
                        "ai_interpretation": interpretation,
                        "status": EventStatus.OPEN
                    }
                    db_manager.insert("risk_events", risk_data)
                    risks_found += 1

        summary = f"Proactive sweep complete. {portfolios_scanned} portfolios scanned. {risks_found} events found. Vulnerability assessments updated."
        _log_heartbeat("book_sweep", portfolios_scanned, risks_found, summary)
        
        if risks_found > 0:
            await broadcaster.broadcast("update")
        
    except Exception as e:
        logger.error(f"Error in heartbeat cycle: {e}")
        _log_heartbeat("book_sweep", portfolios_scanned, risks_found, f"Error: {str(e)}")

def _trigger_global_interrupt(pulse: dict):
    """Simplified helper to trigger a market interrupt for dummy reference."""
    try:
        # DEDUPLICATION: Check if a Market Interrupt already exists as OPEN
        existing = db_manager.client.table("risk_events")\
            .select("id")\
            .eq("event_type", EventType.MARKET_INTERRUPT.value)\
            .eq("status", EventStatus.OPEN.value)\
            .execute()
        
        if existing.data:
            logger.info("Market interrupt already open. Skipping.")
            return

        clients = db_manager.get_all("clients")
        if clients:
            risk_data = {
                "client_id": clients[0]["id"],
                "event_type": EventType.MARKET_INTERRUPT,
                "urgency": pulse.get("urgency", "high"),
                "deterministic_classification": {
                    "reason": pulse.get("reason", ""),
                    "context": pulse.get("context", ""),
                    "agent_pulse": True
                },
                "status": EventStatus.OPEN
            }
            db_manager.insert("risk_events", risk_data)
    except Exception as e:
        logger.error(f"Failed to trigger global interrupt: {e}")

def _log_heartbeat(sweep_type: str, portfolios_scanned: int, risks_found: int, summary: str):
    try:
        db_manager.insert("heartbeat_logs", {
            "sweep_type": sweep_type,
            "portfolios_scanned": portfolios_scanned,
            "risks_found": risks_found,
            "result_summary": summary
        })
    except Exception: pass

if __name__ == "__main__":
    asyncio.run(run_heartbeat())


