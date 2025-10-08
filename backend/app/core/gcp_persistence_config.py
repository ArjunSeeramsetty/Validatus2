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
    cloud_sql_instance: str = Field(default="validatus-sql", env="CLOUD_SQL_INSTANCE")
    cloud_sql_database: str = Field(default="validatus", env="CLOUD_SQL_DATABASE")
    cloud_sql_user: str = Field(default="validatus_app", env="CLOUD_SQL_USER")
    cloud_sql_password: Optional[str] = Field(default=None, env="CLOUD_SQL_PASSWORD")
    cloud_sql_connection_name: Optional[str] = None
    
    # Cloud Storage Configuration
    content_storage_bucket: Optional[str] = Field(default=None, env="CONTENT_STORAGE_BUCKET")
    embeddings_storage_bucket: Optional[str] = Field(default=None, env="EMBEDDINGS_STORAGE_BUCKET")
    reports_storage_bucket: Optional[str] = Field(default=None, env="REPORTS_STORAGE_BUCKET")
    
    # Vertex AI Vector Search Configuration
    vector_search_location: str = Field(default="us-central1", env="VECTOR_SEARCH_LOCATION")
    embedding_model: str = Field(default="text-embedding-004", env="EMBEDDING_MODEL")
    vector_dimensions: int = Field(default=768, env="VECTOR_DIMENSIONS")
    
    # Cloud Spanner Configuration
    spanner_instance_id: str = Field(default="validatus-analytics", env="SPANNER_INSTANCE_ID")
    spanner_database_id: str = Field(default="validatus-analytics", env="SPANNER_DATABASE_ID")
    
    # Memorystore Redis Configuration
    redis_host: Optional[str] = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Google Custom Search Configuration
    google_cse_api_key: str = Field(default="", env="GOOGLE_CSE_API_KEY")
    google_cse_id: str = Field(default="", env="GOOGLE_CSE_ID")
    search_max_results: int = Field(default=20, env="SEARCH_MAX_RESULTS")
    search_site_filters: str = Field(default="", env="SEARCH_SITE_FILTERS")  # CSV of domains
    search_language: str = Field(default="en", env="SEARCH_LANGUAGE")
    search_safe_search: str = Field(default="medium", env="SEARCH_SAFE_SEARCH")
    
    # URL Collection Configuration
    max_urls_per_query: int = Field(default=10, env="MAX_URLS_PER_QUERY")
    url_collection_timeout: int = Field(default=30, env="URL_COLLECTION_TIMEOUT")
    enable_url_deduplication: bool = Field(default=True, env="ENABLE_URL_DEDUPLICATION")
    excluded_domains: str = Field(default="", env="EXCLUDED_DOMAINS")  # CSV of domains to exclude
    
    # Content Processing Configuration
    enable_content_extraction: bool = Field(default=True, env="ENABLE_CONTENT_EXTRACTION")
    content_extraction_timeout: int = Field(default=15, env="CONTENT_EXTRACTION_TIMEOUT")
    max_content_length: int = Field(default=50000, env="MAX_CONTENT_LENGTH")
    
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
    use_iam_auth: bool = Field(default=False, env="USE_IAM_AUTH")
    encryption_key_name: Optional[str] = Field(default=None, env="ENCRYPTION_KEY_NAME")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Build full connection name for Cloud SQL
        if not self.local_development_mode:
            self.cloud_sql_connection_name = f"{self.project_id}:{self.region}:{self.cloud_sql_instance}"
            
            # Build storage bucket names if not provided
            if self.content_storage_bucket in (None, ""):
                self.content_storage_bucket = f"{self.project_id}-validatus-content"
            if self.embeddings_storage_bucket in (None, ""):
                self.embeddings_storage_bucket = f"{self.project_id}-validatus-embeddings"
            if self.reports_storage_bucket in (None, ""):
                self.reports_storage_bucket = f"{self.project_id}-validatus-reports"
    
    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from Google Secret Manager"""
        if self.local_development_mode:
            return os.getenv(secret_name, "")
            
        try:
            from google.api_core import exceptions as gcp_exceptions
            import grpc
            
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except (gcp_exceptions.GoogleAPIError, grpc.RpcError) as e:
            logger.exception(f"Failed to retrieve secret {secret_name} from Secret Manager")
            raise RuntimeError(f"Secret retrieval failed for {secret_name}") from e
        except Exception as e:
            logger.exception(f"Unexpected error retrieving secret {secret_name}")
            raise RuntimeError(f"Unexpected secret retrieval error for {secret_name}") from e
    
    def get_cloud_sql_url(self) -> str:
        """Generate Cloud SQL connection URL"""
        if self.local_development_mode:
            return self.local_postgres_url
        
        password = self.cloud_sql_password or self.get_secret("cloud-sql-password")
        
        if self.use_iam_auth:
            # Use Cloud SQL Proxy with IAM authentication
            return f"postgresql://{self.cloud_sql_user}@/{self.cloud_sql_database}?host=/cloudsql/{self.cloud_sql_connection_name}"
        else:
            # Use password authentication with Cloud SQL Proxy (Unix socket)
            # For Cloud Run with --add-cloudsql-instances, use Unix socket
            return f"postgresql://{self.cloud_sql_user}:{password}@/{self.cloud_sql_database}?host=/cloudsql/{self.cloud_sql_connection_name}"
    
    def get_secure_api_key(self) -> str:
        """Retrieve Google Custom Search API key from environment or Secret Manager"""
        # Check if already loaded from environment variable (Cloud Run --update-secrets)
        if self.google_cse_api_key and len(self.google_cse_api_key.strip()) > 0:
            return self.google_cse_api_key.strip()
        
        # Check raw environment variable (sometimes Pydantic doesn't pick it up immediately)
        env_key = os.getenv("GOOGLE_CSE_API_KEY")
        if env_key and len(env_key.strip()) > 0:
            logger.info("✅ Google CSE API Key loaded from environment variable")
            return env_key.strip()
            
        # For production without env var, try Secret Manager API
        if not self.local_development_mode:
            try:
                logger.info("Attempting to load Google CSE API Key from Secret Manager...")
                return self.get_secret("google-cse-api-key")
            except Exception as e:
                logger.error(f"Failed to retrieve Google CSE API key from Secret Manager: {e}")
                raise RuntimeError(f"Failed to retrieve Google CSE API key: {e}") from e
        
        raise ValueError("Google CSE API key not configured. Set GOOGLE_CSE_API_KEY environment variable or configure Secret Manager.")
    
    def get_secure_cse_id(self) -> str:
        """Retrieve Google Custom Search Engine ID from environment or Secret Manager"""
        # Check if already loaded from environment variable (Cloud Run --update-secrets)
        if self.google_cse_id and len(self.google_cse_id.strip()) > 0:
            return self.google_cse_id.strip()
        
        # Check raw environment variable (sometimes Pydantic doesn't pick it up immediately)
        env_id = os.getenv("GOOGLE_CSE_ID")
        if env_id and len(env_id.strip()) > 0:
            logger.info("✅ Google CSE ID loaded from environment variable")
            return env_id.strip()
            
        # For production without env var, try Secret Manager API
        if not self.local_development_mode:
            try:
                logger.info("Attempting to load Google CSE ID from Secret Manager...")
                return self.get_secret("google-cse-id")
            except Exception as e:
                logger.error(f"Failed to retrieve Google CSE ID from Secret Manager: {e}")
                raise RuntimeError(f"Failed to retrieve Google CSE ID: {e}") from e
        
        raise ValueError("Google CSE ID not configured. Set GOOGLE_CSE_ID environment variable or configure Secret Manager.")
    
    def get_site_filters(self) -> List[str]:
        """Get list of site filters"""
        if not self.search_site_filters:
            return []
        return [domain.strip() for domain in self.search_site_filters.split(",") if domain.strip()]
    
    def get_excluded_domains(self) -> List[str]:
        """Get list of excluded domains"""
        if not self.excluded_domains:
            return []
        return [domain.strip() for domain in self.excluded_domains.split(",") if domain.strip()]
    
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
