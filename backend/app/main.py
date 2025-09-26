# backend/app/main.py - STABILIZED VERSION
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import warnings
from typing import List, Dict, Any, Optional

# Suppress GRPC ALTS warnings and Vertex AI deprecation logs
os.environ["GRPC_ALTS_SKIP_HANDSHAKE"] = "true"
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GCLOUD_PROJECT"] = "validatus-platform"
warnings.filterwarnings("ignore", category=UserWarning, module="vertexai_model_garden")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google.cloud")
warnings.filterwarnings("ignore", category=FutureWarning, module="google.cloud")
warnings.filterwarnings("ignore", message=".*ALTS creds ignored.*")
warnings.filterwarnings("ignore", message=".*deprecated.*")

# Suppress specific GRPC logs
import logging
logging.getLogger("grpc").setLevel(logging.ERROR)
logging.getLogger("google.auth").setLevel(logging.ERROR)
logging.getLogger("google.cloud").setLevel(logging.ERROR)

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

# Deferred imports - only load when needed
def get_analysis_results_manager():
    """Lazy load AnalysisResultsManager only when needed"""
    if FeatureFlags.ANALYSIS_RESULTS_MANAGER_ENABLED:
        try:
            from .services.analysis_results_manager import AnalysisResultsManager
            return AnalysisResultsManager()
        except ImportError:
            logging.warning("AnalysisResultsManager not available - using placeholder")
            return None
    return None

def get_enhanced_analytics_services():
    """Lazy load enhanced analytics services only when needed"""
    if FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
        try:
            from .services.enhanced_analytical_engines import (
                PDFFormulaEngine,
                ActionLayerCalculator,
                MonteCarloSimulator,
                EnhancedFormulaAdapter
            )
            from .services.enhanced_analysis_session_manager import EnhancedAnalysisSessionManager
            return {
                'formula_engine': PDFFormulaEngine(),
                'action_calculator': ActionLayerCalculator(),
                'monte_carlo_simulator': MonteCarloSimulator(),
                'formula_adapter': EnhancedFormulaAdapter(),
                'session_manager': EnhancedAnalysisSessionManager()
            }
        except ImportError:
            logging.warning("Enhanced analytical engines not available - using basic services")
            return None
    return None

def get_phase_c_services():
    """Lazy load Phase C services only when needed"""
    if FeatureFlags.is_phase_enabled('phase_c'):
        try:
            from .services.enhanced_content_processor import EnhancedContentProcessor
            from .services.enhanced_data_pipeline import BayesianDataBlender, EventShockModeler
            from .services.enhanced_knowledge import HybridVectorStoreManager
            from .services.phase_integrated_analysis_session_manager import PhaseIntegratedAnalysisSessionManager
            return {
                'content_processor': EnhancedContentProcessor(),
                'data_blender': BayesianDataBlender(),
                'event_modeler': EventShockModeler(),
                'vector_store': HybridVectorStoreManager(),
                'session_manager': PhaseIntegratedAnalysisSessionManager()
            }
        except ImportError:
            logging.warning("Phase C enhanced services not available - using basic services")
            return None
    return None

def get_phase_e_services():
    """Lazy load Phase E services only when needed"""
    if FeatureFlags.is_phase_e_enabled():
        try:
            from .services.enhanced_analysis_optimization_service import EnhancedAnalysisOptimizationService
            from .services.enhanced_orchestration import AdvancedOrchestrator, MultiLevelCacheManager
            return {
                'optimization_service': EnhancedAnalysisOptimizationService(),
                'orchestrator': AdvancedOrchestrator(),
                'cache_manager': MultiLevelCacheManager()
            }
        except ImportError:
            logging.warning("Phase E orchestration services not available - using basic services")
            return None
    return None

try:
    if FeatureFlags.RESULTS_API_ENABLED:
        from .api.v3 import results as results_router
    else:
        results_router = None
except ImportError:
    results_router = None
    logging.warning("Results router not available - using placeholder endpoints")

# Live Search API
try:
    from .api.v3 import search as search_router
except ImportError:
    search_router = None
    logging.warning("Search API router not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances with safe initialization
core_services = {}
enhanced_services = {}
phase_c_services = {}
phase_e_services = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with gradual service initialization"""
    global core_services, enhanced_services, phase_c_services, phase_e_services
    
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
        results_manager = get_analysis_results_manager()
        if results_manager:
            enhanced_services['results_manager'] = results_manager
            logger.info("✅ Analysis Results Manager initialized")
        
        # Initialize enhanced analytics services lazily
        enhanced_analytics = get_enhanced_analytics_services()
        if enhanced_analytics:
            enhanced_services.update(enhanced_analytics)
            logger.info("✅ Enhanced analytics services initialized")

        # Phase 3: Initialize Phase C Services (Feature Flag Controlled)
        phase_c_services = get_phase_c_services()
        if phase_c_services:
            enhanced_services.update(phase_c_services)
            logger.info("✅ Phase C services initialized")
        
        # Phase E: Initialize Advanced Orchestration & Observability Services
        phase_e_services = get_phase_e_services()
        if phase_e_services:
            enhanced_services.update(phase_e_services)
            logger.info("✅ Phase E services initialized")
            if AdvancedOrchestrator and FeatureFlags.ADVANCED_ORCHESTRATION_ENABLED:
                if not phase_e_services.get('enhanced_optimization_service') or not phase_e_services['enhanced_optimization_service'].orchestrator:
                    phase_e_services['standalone_orchestrator'] = AdvancedOrchestrator(project_id=settings.project_id)
                    await phase_e_services['standalone_orchestrator'].initialize()
                    logger.info("✅ Standalone Advanced Orchestrator initialized")
            
            # Initialize standalone Multi-Level Cache Manager if needed
            if MultiLevelCacheManager and FeatureFlags.MULTI_LEVEL_CACHE_ENABLED:
                if not phase_e_services.get('enhanced_optimization_service') or not phase_e_services['enhanced_optimization_service'].cache_manager:
                    phase_e_services['standalone_cache_manager'] = MultiLevelCacheManager(project_id=settings.project_id)
                    await phase_e_services['standalone_cache_manager'].initialize()
                    logger.info("✅ Standalone Multi-Level Cache Manager initialized")
        
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

# Include migrated data router
try:
    from .api.v3 import migrated
    app.include_router(migrated.router, prefix="/api/v3")
    logging.info("Migrated data API router included")
except ImportError as e:
    logging.warning(f"Migrated data API router not available: {e}")

# Include sequential analysis router
try:
    from .api.v3 import sequential_analysis
    app.include_router(sequential_analysis.router, prefix="/api/v3")
    logging.info("Sequential analysis API router included")
except ImportError as e:
    logging.warning(f"Sequential analysis API router not available: {e}")

# Include live search router
if search_router:
    app.include_router(search_router.router, prefix="/api/v3")
    logging.info("Live search API router included")

# Include advanced analysis router
try:
    from .api.v3 import advanced_analysis
    app.include_router(advanced_analysis.router, prefix="/api/v3")
    logging.info("Advanced analysis API router included")
except ImportError as e:
    logging.warning(f"Advanced analysis API router not available: {e}")

# Health check with service status
@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    service_status = {
        "core_services": list(core_services.keys()),
        "enhanced_services": list(enhanced_services.keys()),
        "phase_c_services": list(phase_c_services.keys()),
        "phase_e_services": list(phase_e_services.keys()),
        "feature_flags": {
            "enhanced_analytics": FeatureFlags.ENHANCED_ANALYTICS_ENABLED,
            "results_manager": FeatureFlags.ANALYSIS_RESULTS_MANAGER_ENABLED,
            "results_api": FeatureFlags.RESULTS_API_ENABLED,
            "phase_c_enabled": FeatureFlags.is_phase_enabled('phase_c'),
            "phase_e_enabled": FeatureFlags.is_phase_e_enabled(),
            "bayesian_pipeline": FeatureFlags.BAYESIAN_PIPELINE_ENABLED,
            "event_shock_modeling": FeatureFlags.EVENT_SHOCK_MODELING_ENABLED,
            "enhanced_content_processing": FeatureFlags.ENHANCED_CONTENT_PROCESSING_ENABLED,
            "hybrid_vector_store": FeatureFlags.HYBRID_VECTOR_STORE_ENABLED,
            "advanced_orchestration": FeatureFlags.ADVANCED_ORCHESTRATION_ENABLED,
            "circuit_breaker": FeatureFlags.CIRCUIT_BREAKER_ENABLED,
            "multi_level_cache": FeatureFlags.MULTI_LEVEL_CACHE_ENABLED,
            "comprehensive_monitoring": FeatureFlags.COMPREHENSIVE_MONITORING_ENABLED
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
        "feature_flags": FeatureFlags.get_all_flags(),
        "enabled_phases": list(FeatureFlags.get_enabled_phases())
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

    # Phase C comprehensive analysis endpoint
    @app.post("/api/v3/analysis/comprehensive")
    async def execute_comprehensive_analysis(
        session_id: str,
        topic: str,
        user_id: str,
        analysis_options: Optional[Dict[str, Any]] = None
    ):
        """Execute comprehensive analysis with Phase C enhancements"""
        try:
            # Check if Phase C is enabled
            if not FeatureFlags.is_phase_enabled('phase_c'):
                raise HTTPException(
                    status_code=503, 
                    detail="Phase C comprehensive analysis not enabled"
                )
            
            # Get Phase C session manager
            phase_c_manager = phase_c_services.get('phase_integrated_session_manager')
            if not phase_c_manager:
                raise HTTPException(
                    status_code=503, 
                    detail="Phase C session manager not available"
                )
            
            # Execute comprehensive analysis
            results = await phase_c_manager.execute_comprehensive_analysis(
                session_id, topic, user_id, analysis_options
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "analysis_type": "comprehensive_phase_c",
                "results": results,
                "phases_enabled": results.get('session_metadata', {}).get('phases_enabled', {}),
                "message": "Comprehensive analysis completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
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

# Phase E Enhanced Orchestration Endpoints
@app.get("/api/v3/orchestration/health")
async def get_orchestration_health():
    """Get orchestrator health status"""
    try:
        if not FeatureFlags.is_phase_e_enabled():
            raise HTTPException(
                status_code=503, 
                detail="Phase E orchestration not enabled"
            )
        
        # Get orchestrator from enhanced optimization service or standalone
        orchestrator = None
        if phase_e_services.get('enhanced_optimization_service'):
            orchestrator = phase_e_services['enhanced_optimization_service'].orchestrator
        elif phase_e_services.get('standalone_orchestrator'):
            orchestrator = phase_e_services['standalone_orchestrator']
        
        if not orchestrator:
            raise HTTPException(
                status_code=503, 
                detail="Orchestrator not available"
            )
        
        health_status = await orchestrator.get_orchestrator_health()
        
        return {
            "success": True,
            "orchestrator_health": health_status,
            "timestamp": health_status.get('timestamp')
        }
        
    except Exception as e:
        logger.error(f"Failed to get orchestration health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/cache/performance")
async def get_cache_performance():
    """Get cache performance analysis"""
    try:
        if not FeatureFlags.MULTI_LEVEL_CACHE_ENABLED:
            raise HTTPException(
                status_code=503, 
                detail="Multi-level cache not enabled"
            )
        
        # Get cache manager from enhanced optimization service or standalone
        cache_manager = None
        if phase_e_services.get('enhanced_optimization_service'):
            cache_manager = phase_e_services['enhanced_optimization_service'].cache_manager
        elif phase_e_services.get('standalone_cache_manager'):
            cache_manager = phase_e_services['standalone_cache_manager']
        
        if not cache_manager:
            raise HTTPException(
                status_code=503, 
                detail="Cache manager not available"
            )
        
        performance_analysis = await cache_manager.get_cache_stats()
        
        return {
            "success": True,
            "cache_performance": performance_analysis,
            "timestamp": performance_analysis.get('timestamp')
        }
        
    except Exception as e:
        logger.error(f"Failed to get cache performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/cache/invalidate")
async def invalidate_cache(pattern: str = None):
    """Invalidate cache entries by pattern"""
    try:
        if not FeatureFlags.MULTI_LEVEL_CACHE_ENABLED:
            raise HTTPException(
                status_code=503, 
                detail="Multi-level cache not enabled"
            )
        
        # Get cache manager from enhanced optimization service or standalone
        cache_manager = None
        if phase_e_services.get('enhanced_optimization_service'):
            cache_manager = phase_e_services['enhanced_optimization_service'].cache_manager
        elif phase_e_services.get('standalone_cache_manager'):
            cache_manager = phase_e_services['standalone_cache_manager']
        
        if not cache_manager:
            raise HTTPException(
                status_code=503, 
                detail="Cache manager not available"
            )
        
        invalidated_count = await cache_manager.invalidate_by_pattern(pattern or "*")
        
        return {
            "success": True,
            "invalidated_count": invalidated_count,
            "pattern": pattern or "*",
            "message": f"Invalidated {invalidated_count} cache entries"
        }
        
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/optimization/enhanced-metrics")
async def get_enhanced_optimization_metrics():
    """Get enhanced optimization metrics including Phase E components"""
    try:
        if not FeatureFlags.is_phase_e_enabled():
            raise HTTPException(
                status_code=503, 
                detail="Phase E enhanced optimization not enabled"
            )
        
        enhanced_optimization_service = phase_e_services.get('enhanced_optimization_service')
        if not enhanced_optimization_service:
            raise HTTPException(
                status_code=503, 
                detail="Enhanced optimization service not available"
            )
        
        metrics = await enhanced_optimization_service.get_enhanced_optimization_metrics()
        
        return {
            "success": True,
            "enhanced_metrics": metrics,
            "timestamp": metrics.get('timestamp')
        }
        
    except Exception as e:
        logger.error(f"Failed to get enhanced optimization metrics: {e}")
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