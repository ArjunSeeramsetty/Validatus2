"""
Production FastAPI application with GCP persistence integration
Optimized for Cloud Run with essential GCP services
"""
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
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

# Try to import GCP persistence
try:
    from .core.gcp_persistence_config import get_gcp_persistence_settings
    from .services.gcp_persistence_manager import get_gcp_persistence_manager
    GCP_AVAILABLE = True
    logger.info("✅ GCP persistence services imported successfully")
except ImportError as e:
    GCP_AVAILABLE = False
    logger.error(f"❌ Failed to import GCP persistence services: {e}")
    raise RuntimeError("GCP persistence services are required but not available")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with GCP persistence initialization"""
    logger.info("🚀 Starting Validatus Backend with GCP persistence...")
    
    try:
        # Initialize GCP persistence manager
        logger.info("🔧 Initializing GCP persistence manager...")
        persistence_manager = get_gcp_persistence_manager()
        
        # Force initialization - don't allow fallback
        logger.info("⚙️ Configuring GCP persistence settings...")
        await persistence_manager.initialize()
        
        core_services['persistence_manager'] = persistence_manager
        logger.info("✅ GCP persistence manager initialized successfully")
        
    except Exception as e:
        logger.exception("❌ Failed to initialize GCP persistence services")
        logger.error("💥 Application cannot start without GCP persistence")
        raise RuntimeError(f"Failed to initialize GCP persistence: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Validatus Backend...")
    if 'persistence_manager' in core_services:
        try:
            await core_services['persistence_manager'].close()
            logger.info("✅ GCP persistence manager closed")
        except Exception as e:
            logger.exception("❌ Error closing persistence manager")

# Create FastAPI app with proper configuration
app = FastAPI(
    title="Validatus Backend API",
    description="AI-Powered Strategic Analysis Platform with GCP Persistence",
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
    """Enhanced health check for Cloud Run with GCP services status"""
    try:
        if 'persistence_manager' not in core_services:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": "GCP persistence manager not initialized",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Check GCP services health
        gcp_health = await core_services['persistence_manager'].health_check()
        
        return {
            "status": "healthy",
            "service": "validatus-backend",
            "version": "3.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "port": os.getenv("PORT", "8000"),
            "gcp_persistence": gcp_health
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
        "message": "Validatus Backend API with GCP Persistence",
        "version": "3.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "gcp_persistence": "enabled"
    }

# Basic API endpoints for production
@app.get("/api/v3/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "3.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "gcp_persistence": "enabled"
    }

# Topics endpoint with GCP persistence
@app.get("/api/v3/topics")
async def list_topics():
    """List topics endpoint with GCP persistence"""
    try:
        if 'persistence_manager' not in core_services:
            raise HTTPException(status_code=503, detail="GCP persistence manager not initialized")
        
        topics = await core_services['persistence_manager'].list_topics_complete()
        return {
            "topics": topics,
            "message": "Topics retrieved from GCP persistence",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "gcp"
        }
    except Exception as e:
        logger.exception("Failed to list topics")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve topics: {str(e)}")

# Create topic endpoint with GCP persistence
@app.post("/api/v3/topics/create", response_model=TopicResponse)
async def create_topic(topic_data: TopicCreateRequest):
    """Create topic endpoint with GCP persistence"""
    try:
        if 'persistence_manager' not in core_services:
            raise HTTPException(status_code=503, detail="GCP persistence manager not initialized")
        
        # Create topic with GCP persistence
        topic_result = await core_services['persistence_manager'].create_topic_complete(
            title=topic_data.title,
            description=topic_data.description,
            user_id=topic_data.user_id,
            analysis_type=topic_data.analysis_type
        )
        
        return TopicResponse(
            success=True,
            topic_id=topic_result['topic_id'],
            message=f"Topic '{topic_data.title}' created and persisted in GCP database",
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.exception("Failed to create topic")
        raise HTTPException(status_code=500, detail=f"Failed to create topic: {str(e)}")

# URL collection endpoint
@app.post("/api/v3/topics/{topic_id}/collect-urls")
async def collect_urls(topic_id: str, background_tasks: BackgroundTasks):
    """Collect URLs for a topic"""
    try:
        if 'persistence_manager' not in core_services:
            raise HTTPException(status_code=503, detail="GCP persistence manager not initialized")
        
        # Start URL collection workflow
        result = await core_services['persistence_manager'].execute_complete_workflow(
            topic_id=topic_id,
            workflow_type="url_collection"
        )
        
        return {
            "success": True,
            "message": "URL collection workflow started",
            "workflow_id": result.get('workflow_id'),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.exception("Failed to start URL collection")
        raise HTTPException(status_code=500, detail=f"Failed to start URL collection: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "app.main_gcp:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
