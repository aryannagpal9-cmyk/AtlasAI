from fastapi import APIRouter
from backend.shared.database import db_manager
from backend.shared.logging import setup_logger
from backend.agents.interpreters import PreMeetingBriefAgent
from datetime import datetime

logger = setup_logger("api.meetings")
router = APIRouter()
brief_agent = PreMeetingBriefAgent()

@router.get("/clients/{client_id}/brief")
async def get_meeting_brief(client_id: str):
    """Generate or retrieve meeting brief."""
    # Run Agent
    brief = await brief_agent.generate_brief(client_id)
    
    # Save to db
    db_manager.insert("meeting_briefs", {
        "client_id": client_id,
        "meeting_timestamp": datetime.utcnow().isoformat(),
        "brief_json": brief
    })
    
    return brief
