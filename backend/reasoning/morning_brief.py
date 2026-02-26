import asyncio
from datetime import datetime, timezone
from backend.shared.database import db_manager
from backend.shared.logging import setup_logger
from backend.reasoning.classifiers import RiskClassifier
from backend.reasoning.workflows import intelligence_workflow
from backend.shared.models import EventType, UrgencyLevel, EventStatus
from backend.api.services.broadcaster import broadcaster
from backend.mcp_server.main import fetch_comprehensive_market_intel

logger = setup_logger("morning_brief")

async def run_morning_analysis():
    """
    Morning Intelligence: Runs daily at 07:30.
    1. Agent scans market news and sector data.
    2. Agent identifies general portfolio vulnerabilities.
    3. Creates a global intelligence card for all advisors.
    """
    logger.info("Starting morning intelligence analysis")
    
    try:
        # 1. Macro Analysis
        clients = db_manager.get_all("clients")
        if not clients:
            logger.warning("No clients found for morning brief.")
            return

        # SHARED CONTEXT: Fetch comprehensive market intel once for all polished insights
        logger.info("Fetching shared market intelligence context for workflow")
        try:
            market_intel = await asyncio.wait_for(fetch_comprehensive_market_intel(), timeout=15.0)
        except Exception as e:
            logger.warning(f"Market intel fetch failed or timed out: {e}. Using empty context.")
            market_intel = {"market_news": [], "geopolitical_events": [], "macro_indicators": {}}
        
        # 2. Generate Morning Report via Workflow
        report = await intelligence_workflow.generate_morning_report(clients, market_intel)
        
        if "error" in report:
            logger.error(f"Workflow report failed: {report['error']}")
            return

        # 2a. Insert THE MASTER BRIEF (Deduplicated)
        master_data = report.get("book_summary_card", {})
        if master_data:
            # Check if a Master Brief already exists for today
            existing_master = db_manager.client.table("risk_events")\
                .select("id")\
                .eq("event_type", EventType.MORNING_INTELLIGENCE.value)\
                .eq("status", EventStatus.OPEN.value)\
                .execute()
            
            if not existing_master.data:
                risk_data = {
                    "client_id": clients[0]["id"],
                    "event_type": EventType.MORNING_INTELLIGENCE,
                    "urgency": UrgencyLevel.HIGH,
                    "deterministic_classification": {
                        "is_master_brief": True,
                        "impact_title": master_data.get("title", "Full Client Book Review"),
                        "impact_summary": "\n".join([f"• {b}" for b in master_data.get("bullets", [])]),
                        "market_summary": report.get("market_summary", ""),
                        "critical_news": report.get("critical_news", []),
                    },
                    "status": EventStatus.OPEN
                }
                db_manager.insert("risk_events", risk_data)
            else:
                logger.info("Morning master brief already exists. Skipping insertion.")

        # 2b. Deterministic Scanning for all clients
        # Get latest market snapshot for deterministic rules
        snapshots = db_manager.client.table("market_snapshots").select("*").order("timestamp", desc=True).limit(1).execute()
        snapshot = snapshots.data[0] if snapshots.data else {}

        count = 0
        for client in clients:
            try:
                # 1. Fetch portfolio
                port_resp = db_manager.client.table("portfolios").select("*").eq("client_id", client["id"]).execute()
                if not port_resp.data:
                    continue
                portfolio = port_resp.data[0]

                # 2. Run Deterministic Classifiers
                findings = []
                
                # Market Risk (Concentration + Sensitivity)
                m_risk = RiskClassifier.classify_market_risk(portfolio, snapshot)
                if m_risk: findings.append(m_risk)
                
                # Pension Allowance (UK Tapering)
                p_risk = RiskClassifier.classify_pension_allowance(client)
                if p_risk: findings.append(p_risk)
                
                # Tax Opportunity (ISA/CGT focus)
                t_opp = RiskClassifier.classify_tax_opportunity(client, portfolio)
                if t_opp: findings.append(t_opp)
                
                # Behavioural Risk (Strategic Friction)
                b_risk = RiskClassifier.classify_behavioural_risk(client, snapshot)
                if b_risk: findings.append(b_risk)
                
                # Compliance (Mandate Drift)
                c_exp = RiskClassifier.classify_compliance_exposure(portfolio)
                if c_exp: findings.append(c_exp)

                if findings:
                    logger.info(f"Client {client['first_name']} has {len(findings)} deterministic findings.")
                else:
                    logger.debug(f"No findings for {client['first_name']}")

                # 2.5 Proactive Vulnerability Check
                if client.get("vulnerability_score", 0) > 0.5:
                    findings.append({
                        "event_type": "vulnerability_alert",
                        "urgency": UrgencyLevel.HIGH if client.get("vulnerability_score", 0) > 0.7 else UrgencyLevel.MEDIUM,
                        "deterministic_classification": {
                            "reason": f"High Vulnerability Score ({client.get('vulnerability_score')}): {client.get('vulnerability_notes')}",
                            "category": client.get("vulnerability_category")
                        }
                    })

                # 3. If any finding, use Workflow to POLISH it
                for finding in findings:
                    try:
                        print(f"DEBUG: Processing risk {finding['event_type']} for {client['first_name']}")
                        # DEDUPLICATION: Check if this risk already exists as OPEN
                        # Ensure event_type is a string for the query
                        etype = finding["event_type"]
                        etype_str = etype.value if hasattr(etype, "value") else str(etype)

                        existing_risk = db_manager.client.table("risk_events")\
                            .select("id")\
                            .eq("client_id", client["id"])\
                            .eq("event_type", etype_str)\
                            .eq("status", EventStatus.OPEN.value)\
                            .execute()
                        
                        if existing_risk.data:
                            print(f"DEBUG: Risk {etype_str} already open for {client['first_name']}. Skipping.")
                            continue

                        print(f"DEBUG: Interpreting risk {etype_str} for {client['first_name']}...")
                        # Polishing step: connecting memory to the deterministic risk
                        interpretation = await intelligence_workflow.interpret_risk(client["id"], finding, market_context=market_intel)
                        
                        risk_data = {
                            "client_id": client["id"],
                            "event_type": finding["event_type"],
                            "urgency": finding["urgency"],
                            "deterministic_classification": finding["deterministic_classification"],
                            "ai_interpretation": {
                                "headline": interpretation.get("headline"),
                                "consequence": interpretation.get("consequence_if_ignored"),
                                "behavioural_nuance": interpretation.get("behavioural_nuance"),
                                "suggested_actions": [interpretation.get("headline")] 
                            },
                            "status": EventStatus.OPEN
                        }
                        
                        print(f"DEBUG: Inserting risk {etype_str} for {client['first_name']} into DB...")
                        res = db_manager.insert("risk_events", risk_data)
                        if res:
                            print(f"DEBUG: Successfully inserted {etype_str} for {client['first_name']}")
                        else:
                            print(f"DEBUG: FAILED to insert {etype_str} for {client['first_name']}")

                    except Exception as ie:
                        print(f"DEBUG: EXCEPTION for {client['first_name']} risk {finding['event_type']}: {ie}")
                        logger.error(f"Workflow interpretation failed for {client['id']}: {ie}")
                
                count += 1
            except Exception as ce:
                logger.error(f"Error processing client {client.get('id')}: {ce}")

        logger.info(f"Deterministic scan completed for {count} clients.")
        await broadcaster.broadcast("update")
        
    except Exception as e:
        logger.error(f"Error in morning analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("STARTING MANUAL RUN")
    asyncio.run(run_morning_analysis())
    print("MANUAL RUN FINISHED")
