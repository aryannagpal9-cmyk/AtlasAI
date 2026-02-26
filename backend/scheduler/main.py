import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reasoning.heartbeat import run_heartbeat
from reasoning.sentinel import run_sentinel
from reasoning.morning_brief import run_morning_analysis
from reasoning.proactor import run_proactive_briefing
from shared.logging import setup_logger

logger = setup_logger("scheduler")

async def main():
    scheduler = AsyncIOScheduler()
    
    # 1. Market Sentinel: Every 5 minutes
    scheduler.add_job(run_sentinel, 'interval', minutes=5, id='market_sentinel')
    
    # 2. Heartbeat Engine: Every 30 minutes (Agent-Led)
    scheduler.add_job(run_heartbeat, 'interval', minutes=30, id='heartbeat_engine')
    
    # 3. Morning Brief: Daily at 07:30
    scheduler.add_job(run_morning_analysis, 'cron', hour=7, minute=30, id='morning_brief')
    
    # 4. Proactive Meeting Briefing: Every 15 minutes
    scheduler.add_job(run_proactive_briefing, 'interval', minutes=15, id='proactive_briefing')
    
    logger.info("Starting scheduler...")
    scheduler.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping scheduler...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
