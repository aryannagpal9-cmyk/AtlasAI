from fastapi import APIRouter, HTTPException, BackgroundTasks
from shared.database import db_manager
from shared.logging import setup_logger
from agents.interpreters import RiskInterpretationAgent

logger = setup_logger("api.risks")
router = APIRouter()

# Initialize agent locally or pass as dependency
interpretation_agent = RiskInterpretationAgent()

@router.get("/risk-events")
async def list_risk_events(status: str = "open"):
    """List risk events (Optimized summary view)."""
    try:
        # Optimization: Fetch only ID/Type/Urgency. Exclude heavy JSON blobs from list view.
        summary_cols = "id, client_id, event_type, urgency, status, created_at"
        resp = db_manager.client.table("risk_events")\
            .select(summary_cols)\
            .eq("status", status)\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()
        return resp.data
    except Exception as e:
        logger.error(f"Error fetching risk events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk-events/{event_id}/interpret")
async def interpret_risk(event_id: str):
    """Trigger AI interpretation for a risk event."""
    # 1. Fetch Event
    event = db_manager.get_by_id("risk_events", event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # 2. Run interpretation agent
    interpretation = await interpretation_agent.interpret(event["client_id"], event)
    
    # 3. Save interpretation to DB
    db_manager.update("risk_events", event_id, {"ai_interpretation": interpretation})
    
    return interpretation

@router.post("/risk-events/{event_id}/resolve")
async def resolve_risk(event_id: str):
    """Mark a risk event as resolved/dismissed."""
    try:
        db_manager.update("risk_events", event_id, {"status": "adviser_resolved", "resolved_at": "now()"})
        # Log the resolution
        db_manager.insert("action_logs", {
            "entity_id": event_id,
            "entity_type": "risk_event",
            "decision": "resolved",
            "action_type": "manual_resolution"
        })
        return {"status": "success", "message": f"Risk {event_id} resolved"}
    except Exception as e:
        logger.error(f"Error resolving risk {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
