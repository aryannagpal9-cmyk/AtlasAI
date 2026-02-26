import asyncio
from datetime import datetime
from backend.shared.database import db_manager
from backend.shared.logging import setup_logger
from backend.mcp_server.main import fetch_live_market_data, search_market_news

logger = setup_logger("sentinel")

async def run_sentinel():
    """
    Market Sentinel: Every 5 minutes, detect abnormal UK market movements.
    Uses DuckDuckGo web search to fetch real market data.
    """
    logger.info("Starting sentinel check")
    
    try:
        # 1. Fetch real market data via DuckDuckGo web search
        current_data = await fetch_live_market_data()
        
        if "error" in current_data:
            logger.error(f"Failed to fetch live market data: {current_data['error']}")
            return
        
        ftse_100 = current_data.get("ftse_100_value")
        ftse_250 = current_data.get("ftse_250_value")
        sectors = current_data.get("sector_performance", {})
        headlines = current_data.get("headlines", [])
        
        logger.info(f"Fetched market data: FTSE100={ftse_100}, FTSE250={ftse_250}, Sectors={sectors}")
        
        # 2. Also fetch market news for context
        news_results = await search_market_news("FTSE 100 UK market today", max_results=3)
        news_headlines = [n.get("title", "") for n in news_results if not n.get("error")]
        
        # 3. Compare with previous snapshot
        prev_resp = db_manager.client.table("market_snapshots")\
            .select("*")\
            .order("timestamp", desc=True)\
            .limit(1)\
            .execute()
        
        if prev_resp.data and ftse_100:
            prev = prev_resp.data[0]
            prev_ftse = float(prev.get("ftse_100_value", 0))
            
            if prev_ftse > 0:
                delta = (ftse_100 - prev_ftse) / prev_ftse
                
                # Threshold: > 2% intraday movement
                if abs(delta) > 0.02:
                    logger.warning(f"Abnormal market movement detected: {delta*100:.2f}%")
                    logger.warning(f"Headlines: {news_headlines}")
                    # Trigger immediate heartbeat
                    from backend.reasoning.heartbeat import run_heartbeat
                    await run_heartbeat()
        
        # 4. Store new snapshot with real data
        snapshot_data = {
            "ftse_100_value": ftse_100 or 0,
            "ftse_250_value": ftse_250 or 0,
            "sector_performance": sectors,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        db_manager.insert("market_snapshots", snapshot_data)
        logger.info(f"Stored market snapshot: FTSE100={ftse_100}, sectors={len(sectors)}")
        
        logger.info("Sentinel check completed")
        
    except Exception as e:
        logger.error(f"Error in sentinel check: {e}")

if __name__ == "__main__":
    asyncio.run(run_sentinel())
