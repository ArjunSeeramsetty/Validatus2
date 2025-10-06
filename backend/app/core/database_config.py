"""
Database configuration for Cloud SQL with proper Cloud Run integration
"""
import os
from typing import Optional
import asyncpg
from google.cloud import secretmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "validatus-platform")
        self.region = os.getenv("GCP_REGION", "us-central1")
        self.instance_name = os.getenv("CLOUD_SQL_INSTANCE", "validatus-primary")
        self.database_name = os.getenv("CLOUD_SQL_DATABASE", "validatus")
        self.user = os.getenv("CLOUD_SQL_USER", "validatus_app")
        
    def get_database_url(self) -> str:
        """Get the correct database URL for Cloud Run deployment"""
        
        # Check if running in Cloud Run (has Cloud SQL connection)
        if os.getenv("CLOUD_SQL_CONNECTION_NAME"):
            # Cloud Run with Cloud SQL Proxy
            connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
            password = self._get_db_password()
            
            return f"postgresql://{self.user}:{password}@/{self.database_name}?host=/cloudsql/{connection_name}"
        else:
            # Local development fallback
            password = os.getenv("CLOUD_SQL_PASSWORD", "password")
            return f"postgresql://{self.user}:{password}@localhost:5432/{self.database_name}"
    
    def _get_db_password(self) -> str:
        """Get database password from Secret Manager or environment"""
        password = os.getenv("CLOUD_SQL_PASSWORD")
        if password:
            return password
            
        # Try to get from Secret Manager
        try:
            client = secretmanager.SecretManagerServiceClient()
            secret_name = f"projects/{self.project_id}/secrets/cloud-sql-password/versions/latest"
            response = client.access_secret_version(request={"name": secret_name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Failed to get password from Secret Manager: {e}")
            return "password"  # fallback for development

# Global instance
db_config = DatabaseConfig()
