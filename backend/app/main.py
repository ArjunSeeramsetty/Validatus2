"""
Validatus Backend - Main Application Entry Point
Consolidated FastAPI application with proper database integration
"""
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Import database manager
from .core.database_config import db_manager

# Configure logging FIRST (before any logger usage)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routers
from .api.v3.topics import router as topics_router
from .api.v3.enhanced_topics import router as enhanced_topics_router
from .api.v3.migration_simple import router as migration_router
from .api.v3.schema import router as schema_router

# 🆕 NEW: Content and Scoring APIs (with error handling)
CONTENT_API_AVAILABLE = False
SCORING_API_AVAILABLE = False
V2_SCORING_API_AVAILABLE = False
BOOTSTRAP_API_AVAILABLE = False

try:
    from .api.v3.content import router as content_router
    CONTENT_API_AVAILABLE = True
except Exception as e:
    logger.warning(f"Content API not available: {e}")

try:
    from .api.v3.scoring import router as scoring_router
    SCORING_API_AVAILABLE = True
except Exception as e:
    logger.warning(f"Scoring API not available: {e}")

try:
    from .api.v3.v2_scoring import router as v2_scoring_router
    V2_SCORING_API_AVAILABLE = True
except Exception as e:
    logger.warning(f"V2 Scoring API not available: {e}")

try:
    from .api.v3.bootstrap import router as bootstrap_router
    BOOTSTRAP_API_AVAILABLE = True
except Exception as e:
    logger.warning(f"Bootstrap API not available: {e}")

try:
    from .api.v3.results import router as results_router
    RESULTS_API_AVAILABLE = True
except Exception as e:
    logger.warning(f"Results API not available: {e}")
    RESULTS_API_AVAILABLE = False

try:
    from .api.v3.segment_results import router as segment_results_router
    SEGMENT_RESULTS_API_AVAILABLE = True
except Exception as e:
    logger.warning(f"Segment Results API not available: {e}")
    SEGMENT_RESULTS_API_AVAILABLE = False

try:
    from .api.v3.enhanced_analysis import router as enhanced_analysis_router
    ENHANCED_ANALYSIS_API_AVAILABLE = True
except Exception as e:
    logger.warning(f"Enhanced Analysis API not available: {e}")
    ENHANCED_ANALYSIS_API_AVAILABLE = False

# Data-Driven Results API (Simplified)
try:
    from .api.v3.data_driven_results_simple import router as data_driven_results_router
    DATA_DRIVEN_RESULTS_API_AVAILABLE = True
except Exception as e:
    logger.warning(f"Data-Driven Results API not available: {e}")
    DATA_DRIVEN_RESULTS_API_AVAILABLE = False

# Database Migration API
try:
    from .api.v3.database_migration import router as database_migration_router
    DATABASE_MIGRATION_API_AVAILABLE = True
except Exception as e:
    logger.warning(f"Database Migration API not available: {e}")
    DATABASE_MIGRATION_API_AVAILABLE = False

# Test Router
try:
    from .api.v3.test_router import router as test_router
    TEST_ROUTER_AVAILABLE = True
except Exception as e:
    logger.warning(f"Test Router not available: {e}")
    TEST_ROUTER_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Validatus Backend...")
    
    try:
        # Initialize database connection pool
        await db_manager.create_connection_pool()
        logger.info("✅ Database connection pool initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Continue startup even if database fails (for health checks)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Validatus Backend...")
    await db_manager.close()
    logger.info("✅ Database connections closed")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="Validatus Backend API",
    version="3.1.0",
    description="AI-Powered Strategic Analysis Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://validatus-frontend-ssivkqhvhq-uc.a.run.app",
        "https://validatus-platform.web.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "version": "3.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": {}
    }
    
    # Check database health
    try:
        connection = await db_manager.get_connection()
        await connection.fetchval("SELECT 1")
        health_status["services"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status

# Migration endpoint is now handled by migration_simple.py router
# Removed duplicate endpoint that was causing import errors

# Include API routers
app.include_router(topics_router, prefix="/api/v3/topics", tags=["Topics"])
app.include_router(enhanced_topics_router, prefix="/api/v3/enhanced-topics", tags=["Enhanced Topics"])
app.include_router(migration_router, prefix="/api/v3/migration", tags=["Migration"])
app.include_router(schema_router, prefix="/api/v3/schema", tags=["Schema"])

# 🆕 NEW: Conditionally include Content and Scoring APIs
if CONTENT_API_AVAILABLE:
    app.include_router(content_router, prefix="/api/v3/content", tags=["Content"])
    logger.info("✅ Content API registered")
else:
    logger.warning("⚠️ Content API not registered (dependencies missing)")

if SCORING_API_AVAILABLE:
    app.include_router(scoring_router, prefix="/api/v3/scoring", tags=["Scoring"])
    logger.info("✅ Scoring API registered")
else:
    logger.warning("⚠️ Scoring API not registered (dependencies missing)")

if V2_SCORING_API_AVAILABLE:
    app.include_router(v2_scoring_router, prefix="/api/v3/v2", tags=["V2 Scoring"])
    logger.info("✅ V2 Scoring API registered (5 segments, 28 factors, 210 layers)")
else:
    logger.warning("⚠️ V2 Scoring API not registered (dependencies missing)")

if BOOTSTRAP_API_AVAILABLE:
    app.include_router(bootstrap_router, prefix="/api/v3/bootstrap", tags=["Bootstrap"])
    logger.info("✅ Bootstrap API registered (hierarchy initialization & migrations)")
else:
    logger.warning("⚠️ Bootstrap API not registered (dependencies missing)")

if RESULTS_API_AVAILABLE:
    app.include_router(results_router, tags=["Results Analysis"])
    logger.info("✅ Results Analysis API registered (Market, Consumer, Product, Brand, Experience)")

if SEGMENT_RESULTS_API_AVAILABLE:
    app.include_router(segment_results_router, tags=["Segment Results"])
    logger.info("✅ Segment Results API registered (Enhanced Segment Data)")
else:
    logger.warning("⚠️ Results Analysis API not registered (dependencies missing)")

if ENHANCED_ANALYSIS_API_AVAILABLE:
    app.include_router(enhanced_analysis_router, tags=["Enhanced Analysis"])
    logger.info("✅ Enhanced Analysis API registered (Scoring Breakdown, Recalculation, Weights)")
else:
    logger.warning("⚠️ Enhanced Analysis API not registered (dependencies missing)")

if DATA_DRIVEN_RESULTS_API_AVAILABLE:
    app.include_router(data_driven_results_router, prefix="/api/v3/data-driven-results", tags=["Data-Driven Results"])
    logger.info("✅ Data-Driven Results API registered (100% Real Data, Cloud SQL Persistence)")
else:
    logger.warning("⚠️ Data-Driven Results API not registered (dependencies missing)")

if DATABASE_MIGRATION_API_AVAILABLE:
    app.include_router(database_migration_router, prefix="/api/v3/database", tags=["Database Migration"])
    logger.info("✅ Database Migration API registered")
else:
    logger.warning("⚠️ Database Migration API not registered")

if TEST_ROUTER_AVAILABLE:
    app.include_router(test_router, prefix="/api/v3/test", tags=["Test"])
    logger.info("✅ Test Router registered")
else:
    logger.warning("⚠️ Test Router not registered")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Validatus Backend API",
        "version": "3.1.0",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )