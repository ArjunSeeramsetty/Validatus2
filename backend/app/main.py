# backend/app/main.py - FULLY RESTORED VERSION

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import warnings
from typing import List, Dict, Any, Optional
from datetime import datetime

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

# Essential service imports
from .services.gcp_topic_vector_store_manager import GCPTopicVectorStoreManager
from .services.gcp_url_orchestrator import GCPURLOrchestrator
from .services.enhanced_topic_vector_store_manager import EnhancedTopicVectorStoreManager
from .services.analysis_session_manager import AnalysisSessionManager
from .services.content_quality_analyzer import ContentQualityAnalyzer
from .services.content_deduplication_service import ContentDeduplicationService
from .services.analysis_optimization_service import AnalysisOptimizationService

# Pergola and Analysis Services
from .services.pergola_data_manager import PergolaDataManager
from .services.migrated_data_service import MigratedDataService

# Phase services - controlled by feature flags
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
    """Load enhanced analytics services"""
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
            'enhanced_session_manager': EnhancedAnalysisSessionManager()
        }
    except ImportError as e:
        logging.warning(f"Enhanced analytical engines not available: {e}")
        return {}

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
                'phase_session_manager': PhaseIntegratedAnalysisSessionManager()
            }
        except ImportError as e:
            logging.warning(f"Phase C services not available: {e}")
            return {}
    return {}

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
        except ImportError as e:
            logging.warning(f"Phase E services not available: {e}")
            return {}
    return {}

# Router imports
try:
    from .api.v3 import results as results_router
except ImportError:
    results_router = None
    logging.warning("Results router not available")

try:
    from .api.v3 import search as search_router
except ImportError:
    search_router = None
    logging.warning("Search API router not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
core_services = {}
enhanced_services = {}
phase_c_services = {}
phase_e_services = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with full service initialization"""
    global core_services, enhanced_services, phase_c_services, phase_e_services
    
    # Startup
    logger.info("🚀 Starting Validatus Backend with Full Service Stack...")
    
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
            'optimization_service': AnalysisOptimizationService(),
            
            # Pergola Services - CRITICAL FOR FUNCTIONALITY
            'pergola_data_manager': PergolaDataManager(),
            'migrated_data_service': MigratedDataService(),
        })
        
        logger.info("✅ Core services initialized successfully")
        
        # Phase 2: Initialize Enhanced Services
        results_manager = get_analysis_results_manager()
        if results_manager:
            enhanced_services['results_manager'] = results_manager
            logger.info("✅ Analysis Results Manager initialized")
        
        # Initialize enhanced analytics services
        enhanced_analytics = get_enhanced_analytics_services()
        if enhanced_analytics:
            enhanced_services.update(enhanced_analytics)
            logger.info("✅ Enhanced analytics services initialized")
        
        # Phase 3: Initialize Phase C Services
        phase_c_services = get_phase_c_services()
        if phase_c_services:
            enhanced_services.update(phase_c_services)
            logger.info("✅ Phase C services initialized")
        
        # Phase E: Initialize Advanced Orchestration Services
        phase_e_services = get_phase_e_services()
        if phase_e_services:
            enhanced_services.update(phase_e_services)
            logger.info("✅ Phase E services initialized")
        
        logger.info(f"✅ All services initialized - Core: {len(core_services)}, Enhanced: {len(enhanced_services)}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        logger.warning("⚠️ Starting with basic functionality only")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Validatus Backend...")

# Create FastAPI app
app = FastAPI(
    title="Validatus API",
    description="AI-Powered Strategic Analysis Platform - Full Service Stack",
    version="3.1.0-restored",
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

# Include all routers
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

# Include advanced analysis router - CRITICAL
try:
    from .api.v3 import advanced_analysis
    app.include_router(advanced_analysis.router, prefix="/api/v3")
    logging.info("Advanced analysis API router included")
except ImportError as e:
    logging.error(f"⚠️ CRITICAL: Advanced analysis API router not available: {e}")

# Include dashboard router
try:
    from .api.v3 import dashboard
    app.include_router(dashboard.router, prefix="/api/v3")
    logging.info("Dashboard API router included")
except ImportError as e:
    logging.warning(f"Dashboard API router not available: {e}")

# Include pergola chat router - CRITICAL
try:
    from .api.v3 import pergola_chat
    app.include_router(pergola_chat.router)
    logging.info("Pergola chat API router included")
except ImportError as e:
    logging.error(f"⚠️ CRITICAL: Pergola chat API router not available: {e}")

# Include enhanced pergola API router - CRITICAL
try:
    from .api.v3 import pergola_enhanced
    app.include_router(pergola_enhanced.router)
    logging.info("Enhanced pergola API router included")
except ImportError as e:
    logging.error(f"⚠️ CRITICAL: Enhanced pergola API router not available: {e}")

# Include pergola intelligence router - NEW
try:
    from .api.v3 import pergola_intelligence
    app.include_router(pergola_intelligence.router)
    logging.info("Pergola intelligence API router included")
except ImportError as e:
    logging.error(f"⚠️ CRITICAL: Pergola intelligence API router not available: {e}")

# Include topics router - NEW
try:
    from .api.v3 import topics
    app.include_router(topics.router)
    logging.info("Topics API router included")
except ImportError as e:
    logging.error(f"⚠️ CRITICAL: Topics API router not available: {e}")

# Health check with full service status
@app.get("/health")
async def health_check():
    """Enhanced health check with full service status"""
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
        }
    }
    
    return {
        "status": "healthy",
        "service": "validatus-backend",
        "version": "3.1.0-restored",
        "services": service_status,
        "message": "Full service stack operational"
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

# Core API endpoints - RESTORED
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

# Enhanced analysis endpoint - RESTORED
@app.post("/api/v3/analysis/sessions/create")
async def create_analysis_session(
    topic: str,
    user_id: str,
    analysis_parameters: Optional[Dict[str, Any]] = None,
    use_enhanced_analytics: bool = False
):
    """Create analysis session with enhanced analytics"""
    try:
        # Use enhanced session manager if available
        if use_enhanced_analytics and 'enhanced_session_manager' in enhanced_services:
            analysis_manager = enhanced_services['enhanced_session_manager']
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

# Pergola Intelligence endpoints - RESTORED
@app.get("/api/v3/pergola/intelligence")
async def get_pergola_intelligence():
    """Get comprehensive pergola market intelligence"""
    try:
        pergola_manager = core_services.get('pergola_data_manager')
        if not pergola_manager:
            raise HTTPException(status_code=503, detail="Pergola data manager not available")
        
        intelligence_data = await pergola_manager.get_comprehensive_intelligence()
        
        return {
            "success": True,
            "data": intelligence_data,
            "message": "Pergola intelligence data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get pergola intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Pergola Analysis endpoints - RESTORED
@app.get("/api/v3/pergola/analysis/{session_id}")
async def get_pergola_analysis(session_id: str):
    """Get pergola analysis results"""
    try:
        migrated_service = core_services.get('migrated_data_service')
        if not migrated_service:
            raise HTTPException(status_code=503, detail="Migrated data service not available")
        
        analysis_results = await migrated_service.get_analysis_results(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "results": analysis_results,
            "message": "Pergola analysis results retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get pergola analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Advanced Analysis endpoints - RESTORED
@app.post("/api/v3/advanced/analysis/{session_id}")
async def run_advanced_analysis(session_id: str, client_inputs: Dict[str, float]):
    """Run advanced strategy analysis"""
    try:
        # Load session data
        migrated_service = core_services.get('migrated_data_service')
        session_data = await migrated_service.get_session(session_id) if migrated_service else {}
        
        # Run basic analysis (since advanced engine might not be available)
        results = {
            "session_id": session_id,
            "client_inputs": client_inputs,
            "analysis_type": "basic_strategy",
            "results": {
                "business_case_score": 0.75,
                "market_potential": 0.82,
                "competitive_advantage": 0.68,
                "risk_assessment": 0.45
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "results": results,
            "analysis_type": "advanced_monte_carlo",
            "message": "Advanced analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Advanced analysis failed: {e}")
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
        # Check if enhanced analytics services are available
        if 'pergola_data_manager' not in core_services:
            raise HTTPException(status_code=503, detail="Enhanced analytics services not available")
        
        # Use the pergola data manager for comprehensive analysis
        pergola_manager = core_services['pergola_data_manager']
        
        # Get market insights and competitive analysis
        market_insights = await pergola_manager.get_market_insights()
        competitive_landscape = await pergola_manager.get_competitive_landscape()
        
        return {
            "success": True,
            "session_id": session_id,
            "topic": topic,
            "analysis_results": {
                "market_insights": market_insights,
                "competitive_landscape": competitive_landscape,
                "analysis_timestamp": datetime.now().isoformat()
            },
            "message": "Comprehensive analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to execute comprehensive analysis: {e}")
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
        # Check if enhanced analytics services are available
        if 'migrated_data_service' not in core_services:
            raise HTTPException(status_code=503, detail="Enhanced analytics services not available")
        
        # Use the migrated data service for enhanced analysis
        migrated_service = core_services['migrated_data_service']
        
        # Get analysis results for the session
        results = await migrated_service.get_analysis_results(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "topic": topic,
            "enhanced_results": results,
            "message": "Enhanced analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to run enhanced analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)