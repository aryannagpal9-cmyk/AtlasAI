from fastapi import APIRouter, HTTPException, Request
from backend.shared.database import db_manager
from backend.shared.logging import setup_logger
from backend.agents.interpreters import DraftingAgent

logger = setup_logger("api.drafts")
router = APIRouter()
drafting_agent = DraftingAgent()

@router.post("/risk-events/{event_id}/draft")
async def generate_draft(event_id: str):
    """Generate client communication draft."""
    event = db_manager.get_by_id("risk_events", event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    draft = await drafting_agent.generate_draft(event["client_id"], event)
    
    db_manager.insert("draft_actions", {
        "risk_event_id": event_id,
        "client_id": event["client_id"],
        "action_type": "email",
        "draft_content": draft
    })
    
    return draft

@router.post("/drafts/{draft_id}/approve")
async def approve_draft(draft_id: str):
    """Approve and send a draft."""
    db_manager.update("draft_actions", draft_id, {"status": "approved"})
    db_manager.insert("action_logs", {
        "entity_id": draft_id,
        "entity_type": "draft_action",
        "decision": "approved",
        "action_type": "draft_approve"
    })
    return {"status": "approved"}

@router.put("/drafts/{draft_id}")
async def edit_draft(draft_id: str, request: Request):
    """Edit draft content (subject, body)."""
    data = await request.json()
    draft = db_manager.get_by_id("draft_actions", draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    content = draft.get("draft_content", {})
    if "subject" in data:
        content["subject"] = data["subject"]
    if "body" in data:
        content["body"] = data["body"]
    
    db_manager.update("draft_actions", draft_id, {"draft_content": content})
    return {"status": "updated", "draft_content": content}

@router.post("/drafts/{draft_id}/reject")
async def reject_draft(draft_id: str):
    """Dismiss/reject a draft."""
    db_manager.update("draft_actions", draft_id, {"status": "rejected"})
    db_manager.insert("action_logs", {
        "entity_id": draft_id,
        "entity_type": "draft_action",
        "decision": "dismissed",
        "action_type": "draft_reject"
    })
    return {"status": "dismissed"}
