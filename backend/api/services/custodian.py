import yfinance as yf
from typing import Dict, Any, Optional
from backend.shared.database import db_manager
from backend.shared.logging import setup_logger

logger = setup_logger("custodian")

class LiveCustodianClient:
    """
    Simulates a live integration with a custodial platform (e.g., Transact, Interactive Brokers).
    In a real system, this would make an authenticated API call to the custodian's /positions endpoint.
    Here, we read the static base holdings from Supabase and use `yfinance` to simulate live market pricing
    on those assets to generate a real-time portfolio snapshot.
    """
    
    @staticmethod
    def _get_live_price(ticker: str) -> Optional[float]:
        try:
            # First try as a standard ticker
            tk = yf.Ticker(ticker)
            hist = tk.history(period="1d")
            if not hist.empty:
                return float(hist["Close"].iloc[-1])
            
            # If empty, try appending .L for London Stock Exchange
            tk_l = yf.Ticker(f"{ticker}.L")
            hist_l = tk_l.history(period="1d")
            if not hist_l.empty:
                return float(hist_l["Close"].iloc[-1])
                
        except Exception as e:
            logger.debug(f"Failed to fetch live price for {ticker}: {e}")
        return None

    @classmethod
    def get_live_portfolio(cls, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the 'live' portfolio for a client. 
        Updates the values of holdings based on current market data.
        """
        try:
            # 1. Fetch the base structural record from DB
            resp = db_manager.client.table("portfolios").select("*").eq("client_id", client_id).execute()
            if not resp.data:
                return None
                
            base_portfolio = resp.data[0]
            holdings = base_portfolio.get("holdings", [])
            
            total_live_value = 0.0
            live_holdings = []
            
            # 2. Simulate live pricing for each holding
            for holding in holdings:
                ticker = holding.get("ticker")
                quantity = holding.get("quantity", 0)
                base_price = holding.get("price_gbp", 0)
                
                live_price = cls._get_live_price(ticker) if ticker else None
                
                # If we couldn't get a live price, fallback to base price with a simulated tiny drift
                if live_price is None:
                    live_price = base_price
                
                live_value = live_price * quantity
                total_live_value += live_value
                
                live_holdings.append({
                    **holding,
                    "live_price_gbp": live_price,
                    "live_value_gbp": live_value
                })
            
            # 3. Recalculate exposures
            for holding in live_holdings:
                holding["exposure_percentage"] = float(holding["live_value_gbp"] / total_live_value) if total_live_value > 0 else 0

            # 4. Return the live snapshot object (without saving over the base structure)
            return {
                "id": base_portfolio["id"], # Pass original ID for reference
                "client_id": client_id,
                "holdings": live_holdings,
                "total_value_gbp": total_live_value,
                "cash_balance_gbp": base_portfolio.get("cash_balance_gbp", 0),
                "target_risk_score": base_portfolio.get("target_risk_score", 5),
                "current_risk_score": base_portfolio.get("current_risk_score", 5) # In real life, recalculate this based on new exposures
            }
            
        except Exception as e:
            logger.error(f"LiveCustodianClient failed for {client_id}: {e}")
            return None
