# Technical Requirements Document (TRD) - Atlas AI

## 1. Architecture Overview
Atlas is a highly modular, decoupled, **serverless-ready** web application. It transitions from traditional background long-lived scheduling (like APScheduler) to stateless, external HTTP-triggered executions, optimizing for Vercel deployment.

### 1.1 Stack
- **Frontend:** React (Vite), Framer Motion, Tailwind CSS
- **Backend:** FastAPI (Python 3.10+), LangChain, Groq LLMs
- **Tools Protocol:** Model Context Protocol (MCP) Server for tool registration
- **Database:** Supabase (PostgreSQL with pgvector for embeddings)
- **Deployment:** Vercel (Frontend & Serverless Backend)

## 2. Component Design

### 2.1 The MCP Server (`backend/mcp_server`)
All real-world database queries, API fetches, and side-effects are isolated via MCP.
- `search_market_news`: Fetches live UK headlines using DuckDuckGo search (`ddgs`).
- `fetch_live_market_data`: Extracts `yfinance` indices (FTSE 100/250).
- `get_client_portfolio_structure`: Executes Supabase JSON queries to extract GBP exposure.
- `retrieve_relevant_memory`: Performs vector similarity search on Supabase `client_memory`.

### 2.2 The Reasoning Engine (`backend/reasoning`)
Agentic workflows that process data but carry no long-lived state.
- **Sentinel (`sentinel.py`)**: Designed to be triggered every 5 minutes by Vercel Cron. Checks live markets for extreme deviations.
- **Heartbeat (`heartbeat.py`)**: Designed to be triggered every 30 minutes. Deep scans portfolios against recent memories.
- **Proactor (`proactor.py`)**: The AI opinion generator. It translates data into the bold opinions seen in the Intelligence UI.
- **Chat (`chat.py`)**: The interactive assistant bound to the UI drawer. Uses LangChain with memory context and drafts emails.

### 2.3 The HTTP API (`backend/api/routers`)
- **Stateless Routing**: `/tasks/sentinel` and `/tasks/heartbeat` securely await triggers (via configurable headers like `CRON_SECRET`).
- **SSE Stream (`/stream/live`)**: Server-Sent Events utilizing PostgreSQL listen/notify for pushing new hunches dynamically to the React client.
- **Live Strip (`/live-strip`)**: Provides real-time metrics and dynamic DDGS-cached news to power the UI ticker.

## 3. Data Model (Supabase)
- `clients`: ID, Name, Vulnerability Status, Metadata
- `portfolios`: Client relation, Asset tickers, Asset class mapping
- `client_memory`: Vectorized semantic long-term memory entries created when an adviser flags a conversation topic.
- `risk_events`: The "Hunch" output table. Polled by the UI stream. Stores classification and proactive AI interpretations.

## 4. Security & Compliance
- Read/Write operations on Supabase use the Service Role Key for backend administration.
- CORS is strictly governed by `VITE_API_URL` origins.
- Groq requests apply safe token maximums and strictly instructed system prompts to avoid API cost leaks.
