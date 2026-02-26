from fastapi import APIRouter, Header, HTTPException, Depends
from reasoning.heartbeat import run_heartbeat
from reasoning.sentinel import run_sentinel
from reasoning.morning_brief import run_morning_analysis
from reasoning.proactor import run_proactive_briefing
from shared.config import settings
from shared.logging import setup_logger

logger = setup_logger("tasks")
router = APIRouter(prefix="/tasks", tags=["Background Tasks"])

async def verify_cron_auth(x_vercel_cron: str = Header(None)):
    """
    Simple verification to ensure the request is coming from Vercel Cron
    or has the correct internal secret.
    """
    # In production, you'd check a secret key from environment variables
    # Vercel Cron sends a CRON_SECRET header if configured.
    # For now, we'll check if the header exists or use a generic secret.
    expected_secret = getattr(settings, "cron_secret", "atlas_cron_secret_123")
    
    if x_vercel_cron != expected_secret and not settings.debug:
        logger.warning(f"Unauthorized task attempt with header: {x_vercel_cron}")
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.get("/sentinel", dependencies=[Depends(verify_cron_auth)])
async def task_sentinel():
    """Trigger the 5-minute Market Sentinel check."""
    logger.info("Task: Market Sentinel triggered via HTTP")
    await run_sentinel()
    return {"status": "success", "task": "sentinel"}

@router.get("/heartbeat", dependencies=[Depends(verify_cron_auth)])
async def task_heartbeat():
    """Trigger the 30-minute Heartbeat scan."""
    logger.info("Task: Heartbeat triggered via HTTP")
    await run_heartbeat()
    return {"status": "success", "task": "heartbeat"}

@router.get("/morning-brief", dependencies=[Depends(verify_cron_auth)])
async def task_morning_brief():
    """Trigger the daily Morning Brief analysis."""
    logger.info("Task: Morning Brief triggered via HTTP")
    await run_morning_analysis()
    return {"status": "success", "task": "morning_brief"}

@router.get("/proactor", dependencies=[Depends(verify_cron_auth)])
async def task_proactor():
    """Trigger the 15-minute Proactive Briefing check."""
    logger.info("Task: Proactive Briefing triggered via HTTP")
    await run_proactive_briefing()
    return {"status": "success", "task": "proactor"}
