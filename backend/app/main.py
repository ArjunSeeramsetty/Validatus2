# backend/app/main.py - STABILIZED VERSION
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from typing import List, Dict, Any, Optional

# Core imports (existing and working)
from .core.gcp_config import get_gcp_settings
from .core.feature_flags import FeatureFlags
from .services.gcp_topic_vector_store_manager import GCPTopicVectorStoreManager
from .services.gcp_url_orchestrator import GCPURLOrchestrator
from .services.enhanced_topic_vector_store_manager import EnhancedTopicVectorStoreManager
from .services.analysis_session_manager import AnalysisSessionManager
from .services.content_quality_analyzer import ContentQualityAnalyzer
from .services.content_deduplication_service import ContentDeduplicationService
from .services.analysis_optimization_service import AnalysisOptimizationService

# Conditional imports with feature flags - NO MORE IMPORT ERRORS!
try:
    if FeatureFlags.ANALYSIS_RESULTS_MANAGER_ENABLED:
        from .services.analysis_results_manager import AnalysisResultsManager
    else:
        AnalysisResultsManager = None
except ImportError:
    AnalysisResultsManager = None
    logging.warning("AnalysisResultsManager not available - using placeholder")

try:
    if FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
        # Import from consolidated enhanced_analytical_engines package
        from .services.enhanced_analytical_engines import (
            PDFFormulaEngine,
            ActionLayerCalculator,
            MonteCarloSimulator,
            EnhancedFormulaAdapter
        )
        from .services.enhanced_analysis_session_manager import EnhancedAnalysisSessionManager
    else:
        PDFFormulaEngine = None
        ActionLayerCalculator = None
        MonteCarloSimulator = None
        EnhancedFormulaAdapter = None
        EnhancedAnalysisSessionManager = None
except ImportError:
    PDFFormulaEngine = None
    ActionLayerCalculator = None
    MonteCarloSimulator = None
    EnhancedFormulaAdapter = None
    EnhancedAnalysisSessionManager = None
    logging.warning("Enhanced analytical engines not available - using basic services")

try:
    if FeatureFlags.RESULTS_API_ENABLED:
        from .api.v3 import results as results_router
    else:
        results_router = None
except ImportError:
    results_router = None
    logging.warning("Results router not available - using placeholder endpoints")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances with safe initialization
core_services = {}
enhanced_services = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with gradual service initialization"""
    global core_services, enhanced_services
    
    # Startup
    logger.info("🚀 Starting Validatus Backend with Phased Service Initialization...")
    
    try:
        # Initialize GCP settings
        settings = get_gcp_settings()
        logger.info(f"✅ GCP Settings loaded for project: {settings.project_id}")
        
        # Phase 1: Initialize Core Services (Always Available)
        core_services.update({
            'topic_manager': GCPTopicVectorStoreManager(project_id=settings.project_id),
            'url_orchestrator': GCPURLOrchestrator(project_id=settings.project_id),
            'enhanced_topic_manager': EnhancedTopicVectorStoreManager(),
            'analysis_session_manager': AnalysisSessionManager(),
            'quality_analyzer': ContentQualityAnalyzer(),
            'deduplication_service': ContentDeduplicationService(),
            'optimization_service': AnalysisOptimizationService()
        })
        
        logger.info("✅ Core services initialized successfully")
        
        # Phase 2: Initialize Enhanced Services (Feature Flag Controlled)
        if FeatureFlags.ANALYSIS_RESULTS_MANAGER_ENABLED and AnalysisResultsManager:
            enhanced_services['results_manager'] = AnalysisResultsManager()
            logger.info("✅ Analysis Results Manager initialized")
        
        if FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
            # Initialize Phase B analytical engines
            if PDFFormulaEngine:
                enhanced_services['pdf_formula_engine'] = PDFFormulaEngine()
                logger.info("✅ PDF Formula Engine initialized")
            
            if ActionLayerCalculator:
                enhanced_services['action_layer_calculator'] = ActionLayerCalculator()
                logger.info("✅ Action Layer Calculator initialized")
            
            if MonteCarloSimulator:
                enhanced_services['monte_carlo_simulator'] = MonteCarloSimulator()
                logger.info("✅ Monte Carlo Simulator initialized")
            
            if EnhancedFormulaAdapter:
                enhanced_services['formula_adapter'] = EnhancedFormulaAdapter()
                logger.info("✅ Enhanced Formula Adapter initialized")
            
            if EnhancedAnalysisSessionManager:
                enhanced_services['enhanced_analysis_session_manager'] = EnhancedAnalysisSessionManager()
                logger.info("✅ Enhanced Analysis Session Manager initialized")
        
        logger.info(f"✅ All services initialized - Core: {len(core_services)}, Enhanced: {len(enhanced_services)}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        # Don't raise - allow app to start with basic functionality
        logger.warning("⚠️  Starting with basic functionality only")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Validatus Backend...")

# Create FastAPI app with enhanced error handling
app = FastAPI(
    title="Validatus API",
    description="AI-Powered Strategic Analysis Platform - Phase A Stabilized Integration",
    version="3.0.1-stabilized",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
settings = get_gcp_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conditionally include routers
if FeatureFlags.RESULTS_API_ENABLED and results_router:
    app.include_router(results_router.router)

# Health check with service status
@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    service_status = {
        "core_services": list(core_services.keys()),
        "enhanced_services": list(enhanced_services.keys()),
        "feature_flags": {
            "enhanced_analytics": FeatureFlags.ENHANCED_ANALYTICS_ENABLED,
            "results_manager": FeatureFlags.ANALYSIS_RESULTS_MANAGER_ENABLED,
            "results_api": FeatureFlags.RESULTS_API_ENABLED
        }
    }
    
    return {
        "status": "healthy",
        "service": "validatus-backend",
        "version": "3.0.1-stabilized",
        "services": service_status,
        "message": "Phased service initialization completed"
    }

# Service status endpoint
@app.get("/api/v3/system/status")
async def get_system_status():
    """Get detailed system and service status"""
    return {
        "system_status": "operational",
        "core_services_count": len(core_services),
        "enhanced_services_count": len(enhanced_services),
        "available_services": {
            "core": list(core_services.keys()),
            "enhanced": list(enhanced_services.keys())
        },
        "feature_flags": FeatureFlags.get_all_flags()
    }

# Core API endpoints (always available)
@app.get("/api/v3/topics")
async def get_topics():
    """Get all available topics"""
    try:
        topic_manager = core_services.get('topic_manager')
        if not topic_manager:
            raise HTTPException(status_code=503, detail="Topic manager not available")
        
        topics = await topic_manager.get_available_topics()
        return {"topics": topics}
        
    except Exception as e:
        logger.error(f"Failed to get topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/topics/create")
async def create_topic(topic: str, urls: List[str], search_queries: List[str] = None):
    """Create a new topic vector store"""
    try:
        topic_manager = core_services.get('topic_manager')
        if not topic_manager:
            raise HTTPException(status_code=503, detail="Topic manager not available")
        
        topic_id = await topic_manager.create_topic_store(topic, urls, search_queries)
        
        return {
            "success": True,
            "topic_id": topic_id,
            "message": f"Topic '{topic}' created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create topic '{topic}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced analysis endpoint (feature flag controlled)
@app.post("/api/v3/analysis/sessions/create")
async def create_analysis_session(
    topic: str,
    user_id: str,
    analysis_parameters: Optional[Dict[str, Any]] = None,
    use_enhanced_analytics: bool = False
):
    """Create analysis session with optional enhanced analytics"""
    try:
        # Use enhanced session manager if available and enhanced analytics requested
        if use_enhanced_analytics and FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
            analysis_manager = enhanced_services.get('enhanced_analysis_session_manager')
            if not analysis_manager:
                analysis_manager = core_services.get('analysis_session_manager')
        else:
            analysis_manager = core_services.get('analysis_session_manager')
        
        if not analysis_manager:
            raise HTTPException(status_code=503, detail="Analysis session manager not available")
        
        # Use enhanced analytics if available and requested
        if use_enhanced_analytics and FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
            if analysis_parameters is None:
                analysis_parameters = {}
            analysis_parameters['use_enhanced_analytics'] = True
        
        session_id = await analysis_manager.create_analysis_session(
            topic, user_id, analysis_parameters
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "topic": topic,
            "user_id": user_id,
            "enhanced_analytics": use_enhanced_analytics and FeatureFlags.ENHANCED_ANALYTICS_ENABLED,
            "message": "Analysis session created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create analysis session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase B Enhanced Analysis Endpoint
@app.post("/api/v3/analysis/enhanced")
async def run_enhanced_analysis(
    session_id: str,
    topic: str,
    user_id: str,
    enhanced_options: Optional[Dict[str, Any]] = None
):
    """Run enhanced strategic analysis with Phase B engines"""
    try:
        if not FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
            raise HTTPException(
                status_code=503, 
                detail="Enhanced analytics not enabled. Set ENABLE_ENHANCED_ANALYTICS=true"
            )
        
        enhanced_manager = enhanced_services.get('enhanced_analysis_session_manager')
        if not enhanced_manager:
            raise HTTPException(status_code=503, detail="Enhanced analysis manager not available")
        
        # Run enhanced analysis
        results = await enhanced_manager.execute_enhanced_strategic_analysis(
            session_id, topic, user_id, enhanced_options
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "enhanced_analysis_results": results,
            "phase_b_components": {
                "pdf_formulas_enabled": FeatureFlags.PDF_FORMULAS_ENABLED,
                "action_layers_enabled": FeatureFlags.ACTION_LAYER_CALCULATOR_ENABLED,
                "pattern_recognition_enabled": FeatureFlags.PATTERN_RECOGNITION_ENABLED
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Placeholder endpoints for missing services
@app.get("/api/v3/results/placeholder")
async def placeholder_results_endpoint():
    """Placeholder for results API when not available"""
    return {
        "status": "placeholder",
        "message": "Results API endpoints will be available when AnalysisResultsManager is implemented",
        "feature_flag": "RESULTS_API_ENABLED",
        "currently_enabled": FeatureFlags.RESULTS_API_ENABLED
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)