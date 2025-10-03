"""
GCP Persistence Configuration
Manages all GCP service configurations and connection settings
"""
import os
from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from google.cloud import secretmanager
import logging

logger = logging.getLogger(__name__)

class GCPPersistenceSettings(BaseSettings):
    """GCP Persistence configuration settings"""
    
    # Project Configuration
    project_id: str = Field(default="validatus-platform", env="GCP_PROJECT_ID")
    region: str = Field(default="us-central1", env="GCP_REGION")
    zone: str = Field(default="us-central1-a", env="GCP_ZONE")
    
    # Cloud SQL Configuration
    cloud_sql_instance: str = Field(default="validatus-primary", env="CLOUD_SQL_INSTANCE")
    cloud_sql_database: str = Field(default="validatus", env="CLOUD_SQL_DATABASE")
    cloud_sql_user: str = Field(default="validatus_app", env="CLOUD_SQL_USER")
    cloud_sql_password: Optional[str] = Field(default=None, env="CLOUD_SQL_PASSWORD")
    cloud_sql_connection_name: Optional[str] = None
    
    # Cloud Storage Configuration
    content_storage_bucket: str = Field(env="CONTENT_STORAGE_BUCKET")
    embeddings_storage_bucket: str = Field(env="EMBEDDINGS_STORAGE_BUCKET")
    reports_storage_bucket: str = Field(env="REPORTS_STORAGE_BUCKET")
    
    # Vertex AI Vector Search Configuration
    vector_search_location: str = Field(default="us-central1", env="VECTOR_SEARCH_LOCATION")
    embedding_model: str = Field(default="text-embedding-004", env="EMBEDDING_MODEL")
    vector_dimensions: int = Field(default=768, env="VECTOR_DIMENSIONS")
    
    # Cloud Spanner Configuration
    spanner_instance_id: str = Field(default="validatus-analytics", env="SPANNER_INSTANCE_ID")
    spanner_database_id: str = Field(default="validatus-analytics", env="SPANNER_DATABASE_ID")
    
    # Memorystore Redis Configuration
    redis_host: str = Field(env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Local Development Configuration
    local_development_mode: bool = Field(default=False, env="LOCAL_DEVELOPMENT_MODE")
    local_postgres_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/validatus",
        env="LOCAL_POSTGRES_URL"
    )
    local_redis_url: str = Field(default="redis://localhost:6379/0", env="LOCAL_REDIS_URL")
    
    # Performance Settings
    max_concurrent_operations: int = Field(default=50, env="MAX_CONCURRENT_OPERATIONS")
    connection_pool_size: int = Field(default=20, env="CONNECTION_POOL_SIZE")
    query_timeout_seconds: int = Field(default=30, env="QUERY_TIMEOUT_SECONDS")
    
    # Security Settings
    use_iam_auth: bool = Field(default=True, env="USE_IAM_AUTH")
    encryption_key_name: Optional[str] = Field(default=None, env="ENCRYPTION_KEY_NAME")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Build full connection name for Cloud SQL
        if not self.local_development_mode:
            self.cloud_sql_connection_name = f"{self.project_id}:{self.region}:{self.cloud_sql_instance}"
            
            # Build storage bucket names if not provided
            if not hasattr(self, 'content_storage_bucket') or not self.content_storage_bucket:
                self.content_storage_bucket = f"{self.project_id}-validatus-content"
            if not hasattr(self, 'embeddings_storage_bucket') or not self.embeddings_storage_bucket:
                self.embeddings_storage_bucket = f"{self.project_id}-validatus-embeddings"
            if not hasattr(self, 'reports_storage_bucket') or not self.reports_storage_bucket:
                self.reports_storage_bucket = f"{self.project_id}-validatus-reports"
    
    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from Google Secret Manager"""
        if self.local_development_mode:
            return os.getenv(secret_name, "")
            
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            return ""
    
    def get_cloud_sql_url(self) -> str:
        """Generate Cloud SQL connection URL"""
        if self.local_development_mode:
            return self.local_postgres_url
        
        password = self.cloud_sql_password or self.get_secret("cloud-sql-password")
        
        if self.use_iam_auth:
            # Use Cloud SQL Proxy with IAM authentication
            return f"postgresql+asyncpg://{self.cloud_sql_user}@/{self.cloud_sql_database}?host=/cloudsql/{self.cloud_sql_connection_name}"
        else:
            # Use password authentication
            return f"postgresql+asyncpg://{self.cloud_sql_user}:{password}@/{self.cloud_sql_database}?host=/cloudsql/{self.cloud_sql_connection_name}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Global settings instance
_gcp_settings = None

def get_gcp_persistence_settings() -> GCPPersistenceSettings:
    """Get GCP persistence configuration settings singleton"""
    global _gcp_settings
    if _gcp_settings is None:
        _gcp_settings = GCPPersistenceSettings()
    return _gcp_settings
