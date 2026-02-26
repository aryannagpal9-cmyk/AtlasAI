from fastapi import APIRouter, Request
from backend.agents.chat import ChatAgent
from backend.shared.logging import setup_logger
from backend.api.services.broadcaster import broadcaster

logger = setup_logger("api.chat")
router = APIRouter()
chat_agent = ChatAgent()

@router.post("/chat")
async def chat(request: Request):
    """Conversational endpoint for Atlas."""
    data = await request.json()
    message = data.get("message")
    history = data.get("history", [])
    
    logger.info(f"Incoming chat message: {message[:50]}...")
    response = await chat_agent.get_response(message, history)
    
    # Broadcast an update just in case the chat agent performed an action
    await broadcaster.broadcast("update")
    
    return {"response": response}
