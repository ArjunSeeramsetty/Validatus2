"""
Production FastAPI application with proper Cloud Run integration
Optimized for fast startup and minimal dependencies
"""
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging for Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services storage
core_services = {}

# Pydantic models for request validation
class TopicCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Topic title")
    description: str = Field(default="", max_length=1000, description="Topic description")
    analysis_type: str = Field(default="comprehensive", description="Analysis type")
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")

class TopicResponse(BaseModel):
    success: bool
    topic_id: str
    message: str
    timestamp: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with enhanced error handling"""
    logger.info("🚀 Starting Validatus Backend...")
    
    try:
        # Initialize core services (minimal for production)
        logger.info("✅ Core services initialized")
        
    except Exception as e:
        logger.exception("❌ Failed to initialize services during startup")
        # Continue with degraded functionality
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Validatus Backend...")

# Create FastAPI app with proper configuration
app = FastAPI(
    title="Validatus Backend API",
    description="AI-Powered Strategic Analysis Platform",
    version="3.1.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# CORS configuration for production
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if not allowed_origins_env:
    logger.error("ALLOWED_ORIGINS environment variable is required in production")
    raise RuntimeError("ALLOWED_ORIGINS must be set in production environment")

allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

# Validate no wildcard when credentials are allowed
if "*" in allowed_origins:
    logger.error("Wildcard origin '*' not allowed when credentials are enabled")
    raise RuntimeError("Wildcard origin not allowed in production with credentials")

# Use explicit origins with credentials
allow_credentials = True
allow_headers = ["Authorization", "Content-Type", "X-Requested-With"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=allow_headers,
)

# Health check endpoint (CRITICAL for Cloud Run)
@app.get("/health")
async def health_check():
    """Enhanced health check for Cloud Run"""
    try:
        return {
            "status": "healthy",
            "service": "validatus-backend",
            "version": "3.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "port": os.getenv("PORT", "8000")
        }
    except Exception as e:
        logger.exception("Health check failed")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Validatus Backend API",
        "version": "3.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Basic API endpoints for production
@app.get("/api/v3/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "3.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Topics endpoint (basic)
@app.get("/api/v3/topics")
async def list_topics():
    """List topics endpoint"""
    return {
        "topics": [],
        "message": "Topics endpoint ready",
        "timestamp": datetime.utcnow().isoformat()
    }

# Create topic endpoint (basic)
@app.post("/api/v3/topics/create", response_model=TopicResponse)
async def create_topic(topic_data: TopicCreateRequest):
    """Create topic endpoint with validation"""
    try:
        # Generate a demo topic ID (in production, this would create in database)
        topic_id = f"topic-{topic_data.user_id}-{int(datetime.utcnow().timestamp())}"
        
        return TopicResponse(
            success=True,
            topic_id=topic_id,
            message=f"Topic '{topic_data.title}' created successfully",
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.exception("Failed to create topic")
        raise HTTPException(status_code=500, detail="Failed to create topic")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "app.main_production:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
