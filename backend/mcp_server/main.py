import os
import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from shared.database import db_manager
from shared.logging import setup_logger
from datetime import datetime, timedelta, timezone

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

try:
    import yfinance as yf
except ImportError:
    yf = None

mcp = FastMCP("AtlasZero")
logger = setup_logger("mcp_server")


# ─── WEB SEARCH TOOLS ───────────────────────────────────────

@mcp.tool()
async def search_market_news(query: str = "UK financial markets FTSE today", max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Searches for the latest market and financial news using DuckDuckGo.
    Returns a list of news articles with title, body, source, date, and URL.
    """
    if not DDGS:
        return [{"error": "ddgs package not installed. Run: pip install ddgs"}]
    
    try:
        results = []
        with DDGS() as ddgs:
            news_results = ddgs.news(query, max_results=max_results)
            for item in news_results:
                results.append({
                    "title": item.get("title", ""),
                    "body": item.get("body", ""),
                    "source": item.get("source", ""),
                    "date": item.get("date", ""),
                    "url": item.get("url", ""),
                })
        logger.info(f"Web search for '{query}' returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return [{"error": str(e)}]


@mcp.tool()
async def search_geopolitical_events(query: str = "geopolitical risk oil energy conflict", max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Searches for geopolitical events that may impact UK financial markets.
    Useful for detecting market interrupts (oil shocks, trade wars, conflicts).
    """
    if not DDGS:
        return [{"error": "ddgs package not installed. Run: pip install ddgs"}]
    
    try:
        results = []
        with DDGS() as ddgs:
            news_results = ddgs.news(query, max_results=max_results)
            for item in news_results:
                results.append({
                    "title": item.get("title", ""),
                    "body": item.get("body", ""),
                    "source": item.get("source", ""),
                    "date": item.get("date", ""),
                    "url": item.get("url", ""),
                    "relevance": "geopolitical"
                })
        logger.info(f"Geopolitical search for '{query}' returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Geopolitical search error: {e}")
        return [{"error": str(e)}]


@mcp.tool()
async def search_client_news(client_name: str, company: str = "", max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Searches for news about a specific client's company or sector holdings.
    Helps prepare meeting briefs and proactive insights.
    """
    if not DDGS:
        return [{"error": "ddgs package not installed. Run: pip install ddgs"}]
    
    query = f"{company} financial news" if company else f"{client_name} investment portfolio news"
    
    try:
        results = []
        with DDGS() as ddgs:
            news_results = ddgs.news(query, max_results=max_results)
            for item in news_results:
                results.append({
                    "title": item.get("title", ""),
                    "body": item.get("body", ""),
                    "source": item.get("source", ""),
                    "date": item.get("date", ""),
                    "url": item.get("url", ""),
                })
        return results
    except Exception as e:
        logger.error(f"Client news search error: {e}")
        return [{"error": str(e)}]


@mcp.tool()
async def fetch_live_market_data(query: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches real-time UK market data using Yahoo Finance (yfinance).
    Returns FTSE 100, FTSE 250, and sector-level signals based on proxy UK stocks.
    """
    if not yf:
        return {"error": "yfinance package not installed. Run: pip install yfinance"}
    
    try:
        market_data = {
            "ftse_100_value": None,
            "ftse_250_value": None,
            "sector_performance": {},
            "headlines": [],
            "source": "Yahoo Finance",
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
        
        # 1. FTSE 100
        ftse_ticker = yf.Ticker("^FTSE")
        ftse_data = ftse_ticker.history(period="1d")
        if not ftse_data.empty:
            market_data["ftse_100_value"] = round(float(ftse_data["Close"].iloc[-1]), 2)
            
        # 2. FTSE 250
        ftse250_ticker = yf.Ticker("^FTMC")
        ftse250_data = ftse250_ticker.history(period="1d")
        if not ftse250_data.empty:
            market_data["ftse_250_value"] = round(float(ftse250_data["Close"].iloc[-1]), 2)
            
        # 3. Sector proxies (UK specific)
        sector_proxies = {
            "Financials": ["HSBA.L", "BARC.L", "LLOY.L"],
            "Energy": ["SHEL.L", "BP.L"],
            "Technology": ["SGE.L", "AUTO.L"],
            "Healthcare": ["AZN.L", "GSK.L"]
        }
        
        for sector, tickers in sector_proxies.items():
            sector_perf = 0.0
            valid_tickers = 0
            for t in tickers:
                tk = yf.Ticker(t)
                hist = tk.history(period="2d")
                if len(hist) >= 2:
                    prev_close = hist["Close"].iloc[-2]
                    curr_close = hist["Close"].iloc[-1]
                    pct_change = (curr_close - prev_close) / prev_close
                    sector_perf += pct_change
                    valid_tickers += 1
            if valid_tickers > 0:
                market_data["sector_performance"][sector] = round(float(sector_perf / valid_tickers), 4)

        return market_data
    except Exception as e:
        logger.error(f"Error fetching live market data: {e}")
        return {"error": str(e)}

@mcp.tool()
async def fetch_comprehensive_market_intel(query: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches a full 360-degree UK market intelligence report in one call.
    Includes indices, sector performance, news, and geopolitical context.
    Parallelizes requests to minimize latency.
    """
    logger.info("Performing comprehensive market intelligence sweep")
    
    # Execute in parallel to save time
    market_data, news, geo = await asyncio.gather(
        fetch_live_market_data(),
        search_market_news("UK financial market news today", max_results=3),
        search_geopolitical_events("geopolitical events UK markets", max_results=3)
    )
    
    return {
        "indices": {
            "ftse_100": market_data.get("ftse_100_value"),
            "ftse_250": market_data.get("ftse_250_value"),
        },
        "sectors": market_data.get("sector_performance", {}),
        "news_headlines": [n.get("title") for n in news if isinstance(n, dict) and "title" in n],
        "geopolitical_context": [g.get("title") for g in geo if isinstance(g, dict) and "title" in g],
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }


# ─── MARKET TOOLS ────────────────────────────────────────────

@mcp.tool()
async def get_market_snapshot(query: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves the latest UK market snapshot from the database."""
    try:
        response = db_manager.client.table("market_snapshots")\
            .select("*")\
            .order("timestamp", desc=True)\
            .limit(1)\
            .execute()
        return response.data[0] if response.data else {"error": "No market data found"}
    except Exception as e:
        logger.error(f"Error fetching market snapshot: {e}")
        return {"error": str(e)}

@mcp.tool()
async def get_sector_performance(query: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves the latest sector-level performance data."""
    snapshot = await get_market_snapshot()
    if "sector_performance" in snapshot:
        return snapshot["sector_performance"]
    return snapshot


# ─── PORTFOLIO TOOLS ─────────────────────────────────────────

@mcp.tool()
async def get_client_portfolio_structure(client_id: str) -> Dict[str, Any]:
    """Retrieves the portfolio structure for a specific client."""
    logger.info(f"TOOL_CALL: get_client_portfolio_structure for {client_id}")
    try:
        response = db_manager.client.table("portfolios")\
            .select("*")\
            .eq("client_id", client_id)\
            .execute()
        result = response.data[0] if response.data else {"error": "Portfolio not found"}
        logger.info(f"TOOL_RESULT: get_client_portfolio_structure success? {'error' not in result}")
        return result
    except Exception as e:
        logger.error(f"Error fetching portfolio for {client_id}: {e}")
        return {"error": str(e)}

@mcp.tool()
async def create_portfolio_snapshot(client_id: str, trigger_event_id: Optional[str] = None) -> Dict[str, Any]:
    """Creates an immutable snapshot of a client's portfolio."""
    try:
        portfolio = await get_client_portfolio_structure(client_id)
        if "error" in portfolio:
            return portfolio
        
        market_snapshot = await get_market_snapshot()
        
        snapshot_data = {
            "portfolio_id": portfolio["id"],
            "holdings_snapshot": portfolio["holdings"],
            "total_value_snapshot": portfolio["total_value_gbp"],
            "market_snapshot_id": market_snapshot.get("id"),
            "trigger_event_id": trigger_event_id
        }
        
        response = db_manager.client.table("portfolio_snapshots").insert(snapshot_data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating portfolio snapshot for {client_id}: {e}")
        return {"error": str(e)}


# ─── TAX TOOLS ───────────────────────────────────────────────

@mcp.tool()
async def get_tax_position(client_id: str) -> Dict[str, Any]:
    """Retrieves the current tax position and profile for a client."""
    try:
        response = db_manager.client.table("clients").select("tax_profile").eq("id", client_id).execute()
        return response.data[0]["tax_profile"] if response.data else {"error": "Client not found"}
    except Exception as e:
        logger.error(f"Error fetching tax position for {client_id}: {e}")
        return {"error": str(e)}


# ─── MEMORY TOOLS ────────────────────────────────────────────

from shared.embeddings import generate_embedding

@mcp.tool()
async def store_memory_item(client_id: str, content: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Stores a behavioural memory item for a client with a semantic vector embedding."""
    try:
        # Generate embedding for the content
        embedding = generate_embedding(content)
        
        data = {
            "client_id": client_id,
            "content": content,
            "embedding": embedding,
            "source_reference": source,
            "metadata": metadata or {}
        }
        response = db_manager.client.table("behavioural_memory").insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error storing memory for {client_id}: {e}")
        return {"error": str(e)}

@mcp.tool()
async def retrieve_relevant_memory(client_id: str, query: str) -> List[Dict[str, Any]]:
    """Retrieves relevant behavioural memories for a client using semantic similarity search."""
    try:
        # 1. Embed the query to find similar past behavior
        query_embedding = generate_embedding(query)
        
        # 2. Call the pgvector match_memory RPC
        params = {
            "query_embedding": query_embedding,
            "match_threshold": 0.5,
            "match_count": 5
        }
        if client_id:
            params["client_id_filter"] = client_id
            
        response = db_manager.client.rpc("match_memory", params).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error retrieving memory for {client_id}: {e}")
        return [{"error": str(e)}]


# ─── EXECUTION TOOLS ─────────────────────────────────────────

@mcp.tool()
async def create_draft_action(risk_event_id: str, client_id: str, action_type: str, draft_content: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a draft action for adviser review."""
    try:
        data = {
            "risk_event_id": risk_event_id,
            "client_id": client_id,
            "action_type": action_type,
            "draft_content": draft_content
        }
        response = db_manager.client.table("draft_actions").insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating draft action: {e}")
        return {"error": str(e)}

@mcp.tool()
async def log_action_decision(entity_id: str, entity_type: str, decision: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Logs an adviser's decision for audit purposes."""
    try:
        data = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "decision": decision,
            "metadata": metadata or {}
        }
        response = db_manager.client.table("action_logs").insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error logging action decision: {e}")
        return {"error": str(e)}


# ─── HELPER FUNCTIONS ────────────────────────────────────────

def _extract_number(text: str) -> Optional[float]:
    """Extract a plausible market index number from text."""
    # Look for patterns like 7,542.30 or 7542.30 or 7,542
    patterns = [
        r'(\d{1,2},\d{3}\.\d+)',  # 7,542.30
        r'(\d{1,2},\d{3})',        # 7,542
        r'(\d{4,5}\.\d+)',         # 7542.30
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                return float(match.replace(",", ""))
            except ValueError:
                continue
    return None


def _estimate_sentiment(news_items) -> float:
    """
    Rough sentiment estimation from news headlines.
    Returns a float between -0.10 and +0.10 representing sector direction.
    """
    positive_words = {"surge", "gain", "rise", "rally", "up", "high", "boost", "growth", "jump", "climb", "recover"}
    negative_words = {"fall", "drop", "decline", "loss", "crash", "down", "low", "plunge", "slump", "tumble", "fear", "risk", "crisis"}
    
    score = 0
    count = 0
    for item in news_items:
        text = (item.get("title", "") + " " + item.get("body", "")).lower()
        for w in positive_words:
            if w in text:
                score += 1
        for w in negative_words:
            if w in text:
                score -= 1
        count += 1
    
    if count == 0:
        return 0.0
    
    # Normalize to -0.10 to +0.10 range
    raw = score / max(count * 3, 1)
    return round(max(-0.10, min(0.10, raw * 0.10)), 4)


if __name__ == "__main__":
    mcp.run()
