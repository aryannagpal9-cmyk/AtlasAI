from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from backend.shared.config import settings
from backend.shared.logging import setup_logger

logger = setup_logger("db")

class SupabaseManager:
    def __init__(self):
        url = settings.supabase_url
        key = settings.supabase_service_role_key
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in settings")
        try:
            self.client: Client = create_client(url, key)
            logger.info("Successfully connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise

    def get_all(self, table: str, columns: str = "*") -> List[Dict[str, Any]]:
        try:
            response = self.client.table(table).select(columns).execute()
            return response.data
        except Exception as e:
            logger.error(f"get_all failed for table {table}: {e}")
            return []

    def get_by_id(self, table: str, id: str, columns: str = "*") -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table(table).select(columns).eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"get_by_id failed for table {table}, id {id}: {e}")
            return None

    def insert(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table(table).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"insert failed for table {table}: {e}")
            return None

    def update(self, table: str, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table(table).update(data).eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"update failed for table {table}, id {id}: {e}")
            return None

    def delete(self, table: str, id: str) -> None:
        try:
            self.client.table(table).delete().eq("id", id).execute()
        except Exception as e:
            logger.error(f"delete failed for table {table}, id {id}: {e}")

# Global instance
db_manager = SupabaseManager()
