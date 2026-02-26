# Atlas AI: System Architecture

Atlas AI is built fundamentally around the concept of a **Proactive Agentic Loop**, transitioning the traditional prompt-response AI model into a continuous, world-aware background worker.

## 1. High-Level Macro Architecture

The architecture is fully decoupled, event-driven, and Serverless-ready.

```mermaid
graph TD
    classDef frontend fill:#fcfcfd,stroke:#eaecf0,stroke-width:1px,color:#101828;
    classDef backend fill:#f8f9fb,stroke:#d0d5dd,stroke-width:1px,color:#101828;
    classDef agent fill:#f9f5ff,stroke:#e9d7fe,stroke-width:1px,color:#6941c6;
    classDef external fill:#fef3f2,stroke:#fecdca,stroke-width:1px,color:#b42318;
    classDef db fill:#ecfdf3,stroke:#a6f4c5,stroke-width:1px,color:#027a48;

    subgraph User_Interface ["Frontend (React/Vite)"]
        Dashboard[Adviser Dashboard]:::frontend
        StreamUI[Intelligence Stream]:::frontend
        DrawerUI[Proactive Discussion Drawer]:::frontend
        TickerUI[Live News Ticker]:::frontend
    end

    subgraph API_Gateway ["Backend (FastAPI)"]
        StreamAPI[SSE Stream Router]:::backend
        ChatAPI[Chat & Draft Router]:::backend
        TasksAPI[Tasks/Cron Router]:::backend
        LiveStripAPI[Live Strip Router]:::backend
    end

    subgraph Intelligence_Engine ["Reasoning Logic"]
        Heartbeat[Heartbeat Agent]:::agent
        Sentinel[Sentinel Agent]:::agent
        Proactor[Proactive Drafting Agent]:::agent
    end

    subgraph MCP_Layer ["Model Context Protocol (MCP)"]
        Tools[Live Search & DB Tools]:::backend
    end

    subgraph Storage ["Supabase PostgreSQL"]
        DB[(Atlas Database)]:::db
        Vectors[(Vector Memories)]:::db
    end

    subgraph External_World ["External Data"]
        DDG((DuckDuckGo News)):::external
        YF((Yahoo Finance)):::external
        LLM((Groq LLM)):::external
    end

    %% Flow connections
    VercelCron((Vercel Cron)) -.-> |HTTP GET| TasksAPI
    TasksAPI --> |Triggers| Heartbeat
    TasksAPI --> |Triggers| Sentinel

    Heartbeat --> |Calls| MCP_Layer
    Sentinel --> |Calls| MCP_Layer
    Proactor <--> |Calls| MCP_Layer

    MCP_Layer --> |Direct Queries| DB
    MCP_Layer --> |Similarity Search| Vectors
    MCP_Layer --> |Fetch| DDG
    MCP_Layer --> |Fetch| YF

    Heartbeat --> |Generates| DB
    Sentinel --> |Generates| DB

    DB -.-> |PostgreSQL LISTEN/NOTIFY| StreamAPI
    StreamAPI --> |SSE Updates| StreamUI

    Dashboard --> |Fetches| LiveStripAPI
    LiveStripAPI --> |Fetches| DDG
    LiveStripAPI --> |Fetches| DB
    LiveStripAPI --> |Populates| TickerUI

    DrawerUI <--> |HTTP POST| ChatAPI
    ChatAPI <--> |Invokes| Proactor
    Proactor <--> |Prompts| LLM
```

## 2. The Proactive Discussion Flow

Unlike standard chat, Atlas acts first when the adviser opens a client's risk drawer.

```mermaid
sequenceDiagram
    participant Adviser
    participant Frontend
    participant AtlasDB
    participant Proactor

    AtlasDB->>Frontend: Stream Pushes High-Urgency "Hunch"
    Adviser->>Frontend: Clicks on Risk Card
    Frontend->>Frontend: Opens Drawer & Auto-populates Proactive Message
    Adviser->>Frontend: Reads "I can generate a draft" message
    Adviser->>Frontend: Clicks "Take Action"
    Frontend->>Proactor: POST /chat {action: "generate_draft"}
    Proactor->>AtlasDB: Fetch Client Memory & Portfolio
    Proactor-->>Frontend: Stream Generated Draft
    Frontend-->>Adviser: Displays Draft Inline
    Adviser->>Frontend: Clicks "Send to Client"
    Frontend->>AtlasDB: Log Communication to Memory
```

## 3. Serverless Extensibility

By removing internal loops (e.g., `apscheduler`), Atlas's core reasoning functions are pure, parameterized scripts exposed via FastAPI routers (`/tasks/heartbeat`). This allows:
- **Zero-Cost Scaling:** The server scales to zero when no background tasks or advisers are active.
- **Micro-billing:** Vercel only charges for the exact compute seconds it takes Groq to process the Heartbeat.
- **Disaster Recovery:** A failed cron run doesn't crash a persistent process; the next HTTP trigger simply retries cleanly.
