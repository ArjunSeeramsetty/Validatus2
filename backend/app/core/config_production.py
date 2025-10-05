"""
Production configuration for Validatus with database connectivity
"""
import os
from typing import Optional
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
    
    # Database
    database_url: Optional[str] = "postgresql+asyncpg://validatus_app:Validatus2024!@/validatusdb?host=/cloudsql/validatus-platform:us-central1:validatus-sql"
    cloud_sql_connection_name: str = "validatus-platform:us-central1:validatus-sql"
    cloud_sql_database: str = "validatusdb"
    cloud_sql_user: str = "validatus_app"
    
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
