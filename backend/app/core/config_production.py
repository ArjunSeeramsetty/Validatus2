"""
Production configuration for Validatus with database connectivity
"""
import os
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "Validatus Backend API"
    version: str = "3.1.0"
    environment: str = "production"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # GCP
    gcp_project_id: str = "validatus-platform"
    gcp_region: str = "us-central1"
    
    # Database - Must be provided via environment variables:
    # DATABASE_URL, CLOUD_SQL_CONNECTION_NAME, CLOUD_SQL_DATABASE, CLOUD_SQL_USER
    database_url: Optional[str] = None
    cloud_sql_connection_name: Optional[str] = None
    cloud_sql_database: Optional[str] = None
    cloud_sql_user: Optional[str] = None
    
    @field_validator('database_url', 'cloud_sql_connection_name', 'cloud_sql_database', 'cloud_sql_user')
    @classmethod
    def validate_db_config(cls, v, info):
        if not v and cls.environment == "production":
            raise ValueError(f"{info.field_name} must be provided in production environment")
        return v
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # Features
    local_development_mode: bool = False
    enable_caching: bool = True
    enable_monitoring: bool = True
    
    # CORS
    allowed_origins: list = [
        "https://validatus-frontend-ssivkqhvhq-uc.a.run.app",
        "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
