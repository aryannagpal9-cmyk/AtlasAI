from fastapi import APIRouter
from shared.database import db_manager
from shared.logging import setup_logger
from agents.interpreters import PreMeetingBriefAgent
from datetime import datetime

logger = setup_logger("api.meetings")
router = APIRouter()
brief_agent = PreMeetingBriefAgent()

@router.get("/clients/{client_id}/brief")
async def get_meeting_brief(client_id: str):
    """Generate or retrieve meeting brief."""
    try:
        # Fetch client details first to get the name
        client_data = db_manager.get_by_id("clients", client_id)
        if not client_data:
            return {"error": "Client not found"}
            
        client_name = f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}".strip()
        
        # Run Agent
        brief = await brief_agent.generate_brief(client_id, client_name)
        
        # Save to db
        db_manager.insert("meeting_briefs", {
            "client_id": client_id,
            "meeting_timestamp": datetime.utcnow().isoformat(),
            "brief_json": brief
        })
        
        # Also create a risk event of type meeting_brief to show it in the stream
        db_manager.insert("risk_events", {
            "client_id": client_id,
            "event_type": "meeting_brief",
            "status": "open",
            "deterministic_classification": {"trigger": "upcoming_meeting"},
            "ai_interpretation": brief
        })
        
        # Trigger broadcast
        from api.services.broadcaster import broadcaster
        await broadcaster.broadcast({
            "type": "meeting_brief_generated",
            "client_id": client_id
        })
        
        return brief
    except Exception as e:
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "traceback": traceback.format_exc()}
