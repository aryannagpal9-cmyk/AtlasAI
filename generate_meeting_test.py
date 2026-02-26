import asyncio
import json
from datetime import datetime
from backend.shared.database import db_manager
from backend.agents.interpreters import PreMeetingBriefAgent

async def main():
    clients = db_manager.client.table("clients").select("*").limit(1).execute()
    if not clients.data:
        print("No clients found.")
        return
        
    client = clients.data[0]
    client_id = client["id"]
    client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
    
    print(f"Generating meeting brief for {client_name} ({client_id})...")
    
    agent = PreMeetingBriefAgent()
    try:
        brief = await agent.generate_brief(client_id, client_name)
        print("Generated brief:")
        print(json.dumps(brief, indent=2))
        
        # Insert brief
        db_manager.insert("meeting_briefs", {
            "client_id": client_id,
            "meeting_timestamp": datetime.utcnow().isoformat(),
            "brief_json": brief
        })
        
        # Insert risk event so it shows up in UI stream
        db_manager.insert("risk_events", {
            "client_id": client_id,
            "event_type": "meeting_brief",
            "status": "open",
            "urgency": "high",
            "deterministic_classification": {"trigger": "upcoming_meeting", "title": f"Meeting Prep: {client_name}"},
            "ai_interpretation": brief
        })
        print("Successfully saved to database!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
