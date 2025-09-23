# backend/app/core/gcp_config.py

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings

class GCPSettings(BaseSettings):
    """Google Cloud Platform configuration settings"""
    
    # Project configuration
    project_id: str = Field(default="validatus-prod", env="GCP_PROJECT_ID")
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
    cloud_sql_user: str = Field(default="validatus_user", env="CLOUD_SQL_USER")
    cloud_sql_password: str = Field(default="validatus_password", env="CLOUD_SQL_PASSWORD")
    
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
        default=["https://validatus-frontend.app", "http://localhost:3000"],
        env="ALLOWED_ORIGINS"
    )
    
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
