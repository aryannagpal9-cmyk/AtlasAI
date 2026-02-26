# Product Requirements Document (PRD) - Atlas AI

## 1. Vision
Atlas AI intends to shift the financial advisory industry from strictly reactive interfaces (chatbots waiting for human input) into an era of **Proactive Autonomous Intelligence**. It runs persistently, gathering "hunches" about clients based on global market movements, and brings fully formed action items to the adviser.

## 2. The Core Problem
Advisers suffer from **Fragmented Tools** (5+ separate platforms with no single view), **World-Blindness** (software doesn't tell them when the FCA changes rules or inflation spikes), and **Reactive Design** (systems require human prompts). Atlas solves this.

## 3. Product Principles
- **Atlas Speaks First:** The system initiates the discussion.
- **Zero Cognitive Load:** Every problem flagged must have an action proposed.
- **Live Connection:** Atlas is natively connected to live financial news and indices.
- **The Book is Alive:** Atlas sweeps the entire client database continuously.

## 4. Key Functional Requirements

### 4.1 Proactive Hunch Engine & Heartbeat Loop
- Atlas must run a continuous "Heartbeat" logic across all clients.
- It must fetch real-time market data (via MCP), evaluate client exposures (portfolio structure), and parse long-term behavioral memory.
- If a risk or opportunity is found, Atlas must classify it (Tax Window, Behavioral Panic, Market Alert).

### 4.2 Proactive Discussion Generation
- The adviser dashboard must feature an Intelligence Stream of these risk cards.
- Clicking a card opens a Drawer. Inside the Drawer, Atlas must **auto-populate** a chat message containing the risk headline, the consequences of ignoring it, and an offer to help.

### 4.3 Action Execution
- Advisers must have a 1-click "Take Action" button.
- Atlas must rapidly generate an empathetic, factual client communication *directly inside the chat pane*.
- The adviser must be able to conversationally edit the draft ("Make it shorter", "Mention ISAs").
- The adviser must be able to permanently "Send to Client" with one click.

### 4.4 The News Ticker (World Context)
- The main dashboard must feature a highly visible, scrolling "News Ticker."
- It must fetch live UK market news from the web and scroll across the UI to ground the adviser in present reality.

## 5. Success Metrics
- **Context Switching:** Drastically reduce the time taken to draft client communications during market events (Target: Under 1 minute).
- **Proactive Interventions:** Number of client risks mitigated before the client even realizes they exist.
- **User Adoption:** "Painful to go back to the old way" is the primary design heuristic.
