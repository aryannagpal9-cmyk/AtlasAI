from fastapi import APIRouter, Request
from agents.chat import ChatAgent
from shared.logging import setup_logger
from api.services.broadcaster import broadcaster

logger = setup_logger("api.chat")
router = APIRouter()
chat_agent = ChatAgent()

from fastapi.responses import StreamingResponse

@router.post("/chat")
async def chat(request: Request):
    """Conversational endpoint for Atlas with thinking stream."""
    data = await request.json()
    message = data.get("message")
    history = data.get("history", [])
    context = data.get("context", {})
    
    logger.info(f"Streaming chat for: {message[:50]}...")
    
    return StreamingResponse(
        chat_agent.stream_response(message, history, context),
        media_type="text/event-stream"
    )
