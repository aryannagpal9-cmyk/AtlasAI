# API Reference - Atlas Zero Intelligence Endpoints

This document details the core REST and SSE endpoints that power the Atlas Zero Advisory Desktop.

## 1. Intelligence Stream

### `GET /stream`
The primary endpoint for the advisor dashboard. Aggregates all open risks, upcoming meetings, drafted actions, and system logs into a chronological feed.

**Query Parameters:**
- `filter` (string): Options `all`, `risk`, `meeting`, `draft`.

**Response Example:**
```json
{
  "stream": [
    {
      "id": "uuid",
      "type": "atlas",
      "text": "FTSE 100 drop impacting high-exposure clients.",
      "timestamp": "10:30 AM",
      "cards": [
        {
          "id": "card-uuid",
          "type": "market_risk",
          "client": "John Doe",
          "impact": "Portfolio concentrated in Energy sector (-4%).",
          "urgency": "high"
        }
      ]
    },
    {
      "id": "hb-uuid",
      "type": "heartbeat",
      "text": "Completed book sweep: 45 portfolios scanned, 2 risks found.",
      "timestamp": "10:00 AM"
    }
  ],
  "tabs": [
    { "key": "all", "label": "All", "count": 12, "highCount": 2 },
    { "key": "risk", "label": "Risks", "count": 4, "highCount": 2 }
  ]
}
```

### `GET /stream/live` (SSE)
A Server-Sent Events endpoint that notifies the frontend of new intelligence events in real-time.

---

## 2. Market & Book Health

### `GET /live-strip`
Returns real-time market data (via `yfinance`) and book-wide metrics for the scrolling header.

**Response Example:**
```json
{
  "ftse_100": 7945.2,
  "ftse_250": 19230.5,
  "sectors": {
    "Financials": -0.012,
    "Energy": 0.005,
    "Technology": -0.021
  },
  "clients_impacted": 8,
  "open_risks": 4,
  "meetings_today": 3
}
```

### `GET /heartbeat-status`
Returns the status of the background reasoning engine.

**Response Example:**
```json
{
  "last_run_text": "12 minutes ago",
  "next_run_text": "in 18 minutes",
  "status": "idle"
}
```

---

## 3. Client Context & Actions

### `GET /clients/{id}/portfolio`
Returns the deep asset-allocation structure of a specific client.

### `GET /clients/{id}/memory`
Retrieves behavioural anchors and historical meeting context via vector similarity search.

### `POST /drafts/{id}/approve`
Approves a drafted AI action (e.g., email) and moves it to the audit log.

---

## 4. Reasoning Interface

### `POST /chat`
Sends a message to the Atlas Brain for ad-hoc book querying or research.

**Request Payload:**
```json
{
  "message": "Which clients are most exposed to the recent Energy sector drop?",
  "history": []
}
```
