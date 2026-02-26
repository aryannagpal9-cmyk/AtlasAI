import asyncio
from datetime import datetime, timedelta, timezone
from shared.database import db_manager
from shared.logging import setup_logger
from agents.interpreters import PreMeetingBriefAgent
from api.services.broadcaster import broadcaster

logger = setup_logger("proactor")
brief_agent = PreMeetingBriefAgent()

async def run_proactive_briefing():
    """
    Meeting Proactor: Runs every 15 minutes.
    1. Look for meetings scheduled in the next 1 hour that don't have a brief yet.
    2. Generate brief using PreMeetingBriefAgent.
    3. Store in meeting_briefs.
    """
    logger.info("Scanning for upcoming meetings requiring proactive briefs")
    
    try:
        # In this demo, we'll simulate 'scheduled' meetings by looking for 
        # brief records that have a meeting_timestamp in the future but potentially 
        # empty/placeholder brief_json. 
        # Or better: We assume there's a source of meetings (e.g. Outlook/CRM).
        # For now, let's look for any meeting scheduled today.
        
        # 1. Fetch all clients
        clients = db_manager.get_all("clients")
        
        # 2. To simulate "1 hour before", we'll check for any client 
        # who has a meeting record in our 'meeting_briefs' table 
        # with a 'pending' state (if we had one) or just generate one for a client 
        # as a 'proactive' demo.
        
        # REAL LOGIC:
        # target_time = datetime.utcnow() + timedelta(hours=1)
        # meetings = db_manager.client.table("scheduled_meetings")\
        #     .select("*").filter("start_time", "gte", target_time)\
        #     .filter("start_time", "lte", target_time + timedelta(minutes=15))\
        #     .execute()
        
        # DEMO LOGIC: 
        # Iterate over clients and generate a proactive brief for the first one that doesn't have one today.
        
        clients_resp = db_manager.client.table("clients").select("*").execute()
        
        for client in (clients_resp.data or []):
            client_id = client["id"]
            client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
            
            # Check if we already have a brief generated today
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            existing = db_manager.client.table("meeting_briefs")\
                .select("*").eq("client_id", client_id).gte("created_at", today_start).execute()
            
            if not existing.data:
                logger.info(f"Proactively generating brief for {client_name}")
                brief = await brief_agent.generate_brief(client_id, client_name)
                
                # Only save if it actually succeeded (avoid saving max iteration errors)
                if brief and "error" not in brief:
                    db_manager.insert("meeting_briefs", {
                        "client_id": client_id,
                        "meeting_timestamp": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                        "brief_json": brief
                    })
                    logger.info(f"Proactive brief ready for {client_name}")
                    
                    # Trigger SSE push
                    await broadcaster.broadcast("update")
                else:
                    logger.error(f"Failed to generate brief for {client_name}: {brief.get('error', 'Unknown Error')}")
                
                # Only do one client per cycle to protect rate limits!
                break
                
    except Exception as e:
        logger.error(f"Error in meeting proactor: {e}")

if __name__ == "__main__":
    asyncio.run(run_proactive_briefing())
