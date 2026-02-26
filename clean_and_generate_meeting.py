import asyncio
import json
from datetime import datetime
from backend.shared.database import db_manager
from backend.agents.interpreters import PreMeetingBriefAgent

async def _main():
    print("1. Cleaning old meetings...")
    db_manager.client.table("meeting_briefs").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    db_manager.client.table("risk_events").delete().eq("event_type", "meeting_brief").execute()
    print("Old meetings cleared.")

    print("\n2. Finding target client...")
    clients = db_manager.client.table("clients").select("*").limit(1).execute()
    if not clients.data:
        print("No clients found.")
        return
        
    client = clients.data[0]
    client_id = client["id"]
    client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
    
    print(f"Generating detailed meeting brief for {client_name} ({client_id})...")
    
    agent = PreMeetingBriefAgent()
    brief = await agent.generate_brief(client_id, client_name)
    print("\nGenerated detailed brief:")
    print(json.dumps(brief, indent=2))
    
    db_manager.insert("meeting_briefs", {
        "client_id": client_id,
        "meeting_timestamp": datetime.utcnow().isoformat(),
        "brief_json": brief
    })
    
    db_manager.insert("risk_events", {
        "client_id": client_id,
        "event_type": "meeting_brief",
        "status": "open",
        "urgency": "high",
        "deterministic_classification": {"trigger": "upcoming_meeting", "title": f"Meeting Prep: {client_name}"},
        "ai_interpretation": brief
    })
    print("\nSuccessfully saved single detailed meeting to database!")
    
    from backend.api.services.broadcaster import broadcaster
    await broadcaster.broadcast({
        "type": "meeting_brief_generated",
        "client_id": client_id
    })
    print("Broadcast sent.")

async def main():
    try:
        await _main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
