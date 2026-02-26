import asyncio
from typing import AsyncGenerator
from backend.shared.logging import setup_logger

logger = setup_logger("sse.broadcaster")

class EventBroadcaster:
    """
    Manages Server-Sent Event (SSE) subscriptions for real-time frontend updates.
    """
    def __init__(self):
        self.queues = []

    async def connect(self) -> asyncio.Queue:
        """Create a new connection queue."""
        queue = asyncio.Queue()
        self.queues.append(queue)
        logger.info(f"New SSE client connected. Active clients: {len(self.queues)}")
        return queue

    def disconnect(self, queue: asyncio.Queue):
        """Remove a connection queue."""
        if queue in self.queues:
            self.queues.remove(queue)
            logger.info(f"SSE client disconnected. Active clients: {len(self.queues)}")

    async def broadcast(self, message: str):
        """Send a message to all connected clients."""
        logger.debug(f"Broadcasting event: {message[:50]}...")
        for queue in self.queues:
            await queue.put(message)

# Global singleton
broadcaster = EventBroadcaster()
