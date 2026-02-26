# Atlas AI: API Documentation

Atlas uses a modular REST API built with FastAPI. It handles synchronous action requests, asynchronous background triggers (Cron), and Server-Sent Events (SSE) for modern real-time capabilities.

## 1. System & Authentication
- **Base URL:** Defined via `VITE_API_URL` (Frontend) and deployed domain (Backend).
- **Authentication:** Currently open for internal MVP testing. Background tasks require an `x-vercel-cron` header matching `CRON_SECRET`.

---

## 2. Intelligence Streaming

### `GET /stream/live`
- **Description:** Server-Sent Events (SSE) endpoint connecting the frontend to the database's `LISTEN/NOTIFY` channels.
- **Returns:** Real-time JSON payloads containing UI-ready "Cards" whenever the Intelligence Engine registers a new event.

### `GET /live-strip`
- **Description:** Powers the dashboard header and the scrolling News Ticker.
- **Logic:** Fetches the latest `market_snapshots`. Reaches out to DuckDuckGo (cached in memory for 5 minutes) to grab live UK financial headlines.
- **Returns:**
  ```json
  {
    "ftse_100": 8021.5,
    "sectors": {"Technology": -0.05 ...},
    "news": ["UK Tech Plummets", "FCA releases new guidance...", "Inflation holds steady"]
  }
  ```

---

## 3. Background Task Triggers (Vercel Cron)

These endpoints run the heavy-lifting AI agents. They hold no internal schedules, operating purely when pinged.

### `GET /tasks/sentinel`
- **Description:** Triggers the fast, 5-minute Market Sentinel to watch for rapid market deviations.
- **Header Required:** `x-vercel-cron: <CRON_SECRET>`

### `GET /tasks/heartbeat`
- **Description:** Triggers the deep, 30-minute processing loop that checks portfolios against long-term semantic memory.
- **Header Required:** `x-vercel-cron: <CRON_SECRET>`

### `GET /tasks/morning-brief`
- **Description:** Compiles the daily `morning_intelligence` macro-economic brief.
- **Header Required:** `x-vercel-cron: <CRON_SECRET>`

---

## 4. Chat & Proactor Actions

### `POST /chat`
- **Description:** The primary conduit bridging the UI Drawer's Discussion tab with the robust LangChain reasoning agents.
- **Body:**
  ```json
  {
    "message": "User input text",
    "history": [{"role": "assistant", "content": "..."}],
    "context": {
      "client_id": "uuid",
      "risk_event_id": "uuid",
      "action": "generate_draft" // Special flag to trigger action execution
    }
  }
  ```
- **Returns:** Iterative NDJSON stream of the Proactor's thoughts and ultimate text chunks to render the ChatGPT-style "Thinking" UI.
