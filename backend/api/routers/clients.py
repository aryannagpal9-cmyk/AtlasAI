from fastapi import APIRouter, HTTPException
from backend.shared.database import db_manager
from backend.shared.logging import setup_logger

logger = setup_logger("api.clients")
router = APIRouter()

@router.get("/clients")
async def list_clients():
    """List all clients (Optimized summary view)."""
    try:
        # Optimization: Exclude heavy JSON profiles and metadata from list view
        summary_cols = "id, first_name, last_name, email, vulnerability_score, vulnerability_category"
        resp = db_manager.client.table("clients").select(summary_cols).order("last_name").execute()
        return {"clients": resp.data or []}
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients/{client_id}/portfolio")
async def get_client_portfolio(client_id: str):
    """Returns portfolio structure for a specific client."""
    try:
        resp = db_manager.client.table("portfolios")\
            .select("*").eq("client_id", client_id).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return resp.data[0]
    except Exception as e:
        logger.error(f"Error fetching portfolio for {client_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients/{client_id}/memory")
async def get_client_memory(client_id: str):
    """Returns behavioural memory entries for a specific client."""
    try:
        resp = db_manager.client.table("behavioural_memory")\
            .select("*").eq("client_id", client_id)\
            .order("created_at", desc=True).limit(10).execute()
        return resp.data
    except Exception as e:
        logger.error(f"Error fetching memory for {client_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
