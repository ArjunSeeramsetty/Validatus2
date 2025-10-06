"""
Unified Database Configuration for Validatus2
Handles Cloud SQL connections with proper Cloud Run integration
"""
import os
import asyncio
import asyncpg
import logging
from typing import Optional
from google.cloud import secretmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "validatus-platform")
        self.region = os.getenv("GCP_REGION", "us-central1")
        self.connection = None
        self.pool = None
        
    def get_connection_config(self) -> dict:
        """Get database connection configuration"""
        
        # Check if running in Cloud Run
        if os.getenv("CLOUD_SQL_CONNECTION_NAME"):
            # Cloud Run deployment with Cloud SQL
            connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
            database = os.getenv("CLOUD_SQL_DATABASE", "validatus")
            user = os.getenv("CLOUD_SQL_USER", "validatus_app")
            
            # Try to get password from environment or Secret Manager
            password = self._get_database_password()
            
            return {
                "database": database,
                "user": user,
                "password": password,
                "host": f"/cloudsql/{connection_name}",
                "port": None  # Unix socket doesn't use port
            }
        else:
            # Local development
            return {
                "database": os.getenv("DB_NAME", "validatus"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", "password"),
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432"))
            }
    
    def _get_database_password(self) -> str:
        """Get database password from environment or Secret Manager"""
        # First try environment variable
        password = os.getenv("CLOUD_SQL_PASSWORD")
        if password:
            return password
        
        # Try Secret Manager
        try:
            client = secretmanager.SecretManagerServiceClient()
            secret_name = f"projects/{self.project_id}/secrets/cloud-sql-password/versions/latest"
            response = client.access_secret_version(request={"name": secret_name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.warning(f"Could not retrieve password from Secret Manager: {e}")
            # Fallback for development
            return os.getenv("DB_PASSWORD", "password")
    
    async def get_connection(self):
        """Get database connection"""
        if self.connection and not self.connection.is_closed():
            return self.connection
        
        config = self.get_connection_config()
        
        try:
            self.connection = await asyncpg.connect(**config)
            logger.info("Database connection established successfully")
            return self.connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def create_connection_pool(self, min_size=5, max_size=20):
        """Create connection pool for better performance"""
        if self.pool:
            return self.pool
        
        config = self.get_connection_config()
        
        try:
            self.pool = await asyncpg.create_pool(
                min_size=min_size,
                max_size=max_size,
                **config
            )
            logger.info("Database connection pool created successfully")
            return self.pool
        except Exception as e:
            logger.error(f"Connection pool creation failed: {e}")
            raise
    
    async def close(self):
        """Close connections"""
        if self.connection and not self.connection.is_closed():
            await self.connection.close()
        if self.pool:
            await self.pool.close()

# Global instance
db_manager = DatabaseManager()