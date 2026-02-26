# Atlas AI: The Proactive Advisory Engine

Atlas is an autonomous, intelligent financial advisory layer built for the modern UK Wealth Manager. It transforms the advisory experience from *reactive query-answering* to *proactive hunch generation*. Atlas wakes up before the adviser does, monitors live markets, connects global events to individual client portfolios, and drafts communications before being asked.

## Features

*   **Heartbeat Reasoning Loop**: A continuous, serverless cron-driven engine that reviews the entire client book.
*   **Live Market & News MCP**: Integrates directly with DuckDuckGo for live news (powers the real-time News Ticker) and Yahoo Finance for live market indices.
*   **Proactive Hunch Engine**: Analyzes market shifts, checks long-term client behavioral memory, and proactively highlights risks (e.g., *“James is about to panic over his Tech exposure”*).
*   **Autonomous Draft Action**: Instantly generates empathetic, compliant client emails inside the dashboard discussion tab.
*   **Serverless Ready**: 100% stateless backend designed to deploy instantly to Vercel with HTTP-triggered cron tasks.

## Getting Started

### Prerequisites

*   Python 3.10+
*   Node.js 18+
*   Supabase (PostgreSQL)

### Environment Variables (.env)
```env
# Backend .env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
GROQ_API_KEY=your_groq_api_key
CRON_SECRET=atlas_cron_secret_123

# Frontend .env
VITE_API_URL=http://localhost:8000
```

### Local Development

1.  **Clone and install dependencies:**
    ```bash
    # Backend
    cd backend
    pip install -r requirements.txt
    
    # Frontend
    cd frontend
    npm install
    ```

2.  **Start the services:**
    ```bash
    # Backend (Terminal 1)
    export PYTHONPATH=$(pwd)
    python -m backend.api.main
    
    # Frontend (Terminal 2)
    cd frontend
    npm run dev
    ```

## Architecture Map

*   `frontend/` - React, Framer Motion, Tailwind (Dashboard, Streaming UI, News Ticker)
*   `backend/api/` - FastAPI routing and Serverless entry points
*   `backend/mcp_server/` - Model Context Protocol Server (Live Market Data, Web Search, DB operations)
*   `backend/reasoning/` - The Intelligence logic (Sentinel, Heartbeat, Chat Agent, Proactor)
*   `backend/shared/` - Database connections, config, and logging

For deeper dives, see the `Architecture.md` and `TRD.md` docs.
