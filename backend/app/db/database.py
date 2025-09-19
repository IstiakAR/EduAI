"""
Database connection and configuration for Supabase.
This project uses Supabase as the primary database - no local PostgreSQL needed.
"""
import asyncio
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from app.core.config import get_settings

settings = get_settings()


class DatabaseManager:
    """Supabase database manager."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        self.service_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    async def health_check(self) -> bool:
        """Check if Supabase connection is healthy."""
        try:
            # Simple query to test connection
            response = await asyncio.to_thread(
                lambda: self.supabase.table("users").select("id").limit(1).execute()
            )
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False
    
    def get_client(self, use_service_key: bool = False) -> Client:
        """Get Supabase client."""
        return self.service_client if use_service_key else self.supabase
    
    async def create_tables_if_not_exist(self):
        """Create tables if they don't exist using SQL."""
        # This would typically be done through Supabase dashboard or migrations
        # For now, we'll handle this through the init_db.py script
        pass


# Global database manager instance
db_manager = DatabaseManager()


def get_supabase() -> Client:
    """Dependency to get Supabase client."""
    return db_manager.supabase


def get_service_supabase() -> Client:
    """Dependency to get Supabase service client (with elevated permissions)."""
    return db_manager.service_client