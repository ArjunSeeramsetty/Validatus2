# backend/app/core/gcp_config.py

import os
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class GCPSettings(BaseSettings):
    """Google Cloud Platform configuration settings"""
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields for local development
    
    # Project configuration
    project_id: str = Field(default="validatus-platform", env="GCP_PROJECT_ID")
    region: str = Field(default="us-central1", env="GCP_REGION")
    zone: str = Field(default="us-central1-a", env="GCP_ZONE")
    
    # Service configuration
    service_account_key_path: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Storage configuration
    storage_bucket_prefix: str = Field(default="validatus", env="GCP_STORAGE_PREFIX")
    
    # AI Platform configuration
    vertex_ai_location: str = Field(default="us-central1", env="VERTEX_AI_LOCATION")
    embedding_model: str = Field(default="text-embedding-004", env="VERTEX_EMBEDDING_MODEL")
    
    # Cloud SQL configuration
    cloud_sql_instance: str = Field(default="validatus-db", env="CLOUD_SQL_INSTANCE")
    cloud_sql_database: str = Field(default="validatus", env="CLOUD_SQL_DATABASE")
    cloud_sql_user: Optional[str] = Field(default=None, env="CLOUD_SQL_USER")
    cloud_sql_password: Optional[str] = Field(default=None, env="CLOUD_SQL_PASSWORD")
    environment: str = Field(default="development", env="ENVIRONMENT")
    local_development_mode: bool = Field(default=False, env="LOCAL_DEVELOPMENT_MODE")
    
    # Cloud Tasks configuration
    task_queue_location: str = Field(default="us-central1", env="CLOUD_TASKS_LOCATION")
    scraping_queue_name: str = Field(default="url-scraping-queue", env="SCRAPING_QUEUE_NAME")
    
    # Pub/Sub configuration
    pubsub_topic_prefix: str = Field(default="validatus", env="PUBSUB_TOPIC_PREFIX")
    
    # Monitoring configuration
    enable_monitoring: bool = Field(default=True, env="ENABLE_GCP_MONITORING")
    monitoring_interval: int = Field(default=60, env="MONITORING_INTERVAL_SECONDS")
    
    # Security configuration
    enable_vpc_native: bool = Field(default=True, env="ENABLE_VPC_NATIVE")
    allowed_origins: List[str] = Field(
        default=[
            "https://validatus-frontend-ssivkqhvhq-uc.a.run.app",
            "https://validatus-frontend.app", 
            "http://localhost:3000",
            "http://localhost:8000"
        ],
        env="ALLOWED_ORIGINS"
    )
    
    @field_validator('cloud_sql_user')
    @classmethod
    def validate_cloud_sql_user(cls, v, info):
        if v is None and not info.data.get('local_development_mode', True):
            raise ValueError("CLOUD_SQL_USER is required for non-development environments")
        elif v is None:
            return "validatus_user"  # Development default
        return v
    
    @field_validator('cloud_sql_password')
    @classmethod
    def validate_cloud_sql_password(cls, v, info):
        if v is None and not info.data.get('local_development_mode', True):
            raise ValueError("CLOUD_SQL_PASSWORD is required for non-development environments")
        elif v is None:
            return "validatus_password"  # Development default
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

def get_gcp_settings() -> GCPSettings:
    """Get GCP configuration settings"""
    return GCPSettings()

# Cloud SQL connection helper
def get_cloud_sql_connection_string() -> str:
    """Generate Cloud SQL connection string"""
    settings = get_gcp_settings()
    return f"postgresql://{settings.cloud_sql_user}:{settings.cloud_sql_password}@/{settings.cloud_sql_database}?host=/cloudsql/{settings.cloud_sql_instance}"

# Export settings
__all__ = ['GCPSettings', 'get_gcp_settings', 'get_cloud_sql_connection_string']
