# backend/app/main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import List, Dict, Any, Optional

from .core.gcp_config import get_gcp_settings
from .services.gcp_topic_vector_store_manager import GCPTopicVectorStoreManager
from .services.gcp_url_orchestrator import GCPURLOrchestrator
from .services.enhanced_topic_vector_store_manager import EnhancedTopicVectorStoreManager
from .services.analysis_session_manager import AnalysisSessionManager
from .services.content_quality_analyzer import ContentQualityAnalyzer
from .services.content_deduplication_service import ContentDeduplicationService
from .services.analysis_optimization_service import AnalysisOptimizationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
topic_manager = None
enhanced_topic_manager = None
url_orchestrator = None
analysis_session_manager = None
quality_analyzer = None
deduplication_service = None
optimization_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global topic_manager, enhanced_topic_manager, url_orchestrator, analysis_session_manager
    global quality_analyzer, deduplication_service, optimization_service
    
    # Startup
    logger.info("🚀 Starting Validatus Backend with Phase 2 Components...")
    
    try:
        # Initialize GCP settings
        settings = get_gcp_settings()
        logger.info(f"✅ GCP Settings loaded for project: {settings.project_id}")
        
        # Initialize Phase 1 services
        topic_manager = GCPTopicVectorStoreManager(project_id=settings.project_id)
        url_orchestrator = GCPURLOrchestrator(project_id=settings.project_id)
        
        # Initialize Phase 2 services
        enhanced_topic_manager = EnhancedTopicVectorStoreManager()
        analysis_session_manager = AnalysisSessionManager()
        quality_analyzer = ContentQualityAnalyzer()
        deduplication_service = ContentDeduplicationService()
        optimization_service = AnalysisOptimizationService()
        
        logger.info("✅ All Phase 1 and Phase 2 services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Validatus Backend...")

# Create FastAPI app
app = FastAPI(
    title="Validatus API",
    description="AI-powered strategic analysis platform",
    version="3.0.0",
    lifespan=lifespan
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "validatus-backend",
        "version": "3.0.0"
    }

@app.get("/api/v3/topics")
async def get_topics():
    """Get all available topics"""
    try:
        if not topic_manager:
            raise HTTPException(status_code=503, detail="Topic manager not initialized")
        
        topics = await topic_manager.get_available_topics()
        return {"topics": topics}
        
    except Exception as e:
        logger.error(f"Failed to get topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/topics/create")
async def create_topic(topic: str, urls: list[str], search_queries: list[str] = None):
    """Create a new topic vector store"""
    try:
        if not topic_manager:
            raise HTTPException(status_code=503, detail="Topic manager not initialized")
        
        topic_id = await topic_manager.create_topic_store(topic, urls, search_queries)
        
        return {
            "success": True,
            "topic_id": topic_id,
            "message": f"Topic '{topic}' created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create topic '{topic}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/topics/{topic}/collect-urls")
async def collect_urls_for_topic(
    topic: str, 
    search_queries: list[str] = None, 
    max_urls: int = 100
):
    """Collect URLs for a specific topic"""
    try:
        if not url_orchestrator:
            raise HTTPException(status_code=503, detail="URL orchestrator not initialized")
        
        urls = await url_orchestrator.collect_urls_for_topic(topic, search_queries, max_urls)
        
        return {
            "success": True,
            "topic": topic,
            "urls": urls,
            "url_count": len(urls)
        }
        
    except Exception as e:
        logger.error(f"Failed to collect URLs for topic '{topic}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/topics/{topic}/evidence/{layer}")
async def get_evidence_by_layer(topic: str, layer: str, k: int = 10):
    """Get evidence chunks for a specific topic and layer"""
    try:
        if not topic_manager:
            raise HTTPException(status_code=503, detail="Topic manager not initialized")
        
        evidence_chunks = await topic_manager.retrieve_by_topic_layer(topic, layer, k)
        
        # Convert EvidenceChunk objects to dictionaries
        evidence_data = []
        for chunk in evidence_chunks:
            evidence_data.append({
                "content": chunk.content,
                "layer": chunk.layer,
                "factor": chunk.factor,
                "segment": chunk.segment,
                "url": chunk.url,
                "title": chunk.title,
                "quality_score": chunk.quality_score,
                "chunk_index": chunk.chunk_index,
                "similarity_score": chunk.similarity_score
            })
        
        return {
            "success": True,
            "topic": topic,
            "layer": layer,
            "evidence_chunks": evidence_data,
            "count": len(evidence_data)
        }
        
    except Exception as e:
        logger.error(f"Failed to get evidence for topic '{topic}', layer '{layer}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase 2 Enhanced API Endpoints

@app.post("/api/v3/enhanced/topics/create")
async def create_enhanced_topic(
    topic: str, 
    urls: List[str], 
    quality_threshold: float = 0.6
):
    """Create an enhanced topic store with quality analysis and classification"""
    try:
        if not enhanced_topic_manager:
            raise HTTPException(status_code=503, detail="Enhanced topic manager not initialized")
        
        topic_id = await enhanced_topic_manager.create_enhanced_topic_store(
            topic, urls, quality_threshold
        )
        
        return {
            "success": True,
            "topic_id": topic_id,
            "message": f"Enhanced topic '{topic}' created successfully",
            "quality_threshold": quality_threshold,
            "url_count": len(urls)
        }
        
    except Exception as e:
        logger.error(f"Failed to create enhanced topic '{topic}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/enhanced/topics/{topic}/knowledge")
async def get_enhanced_topic_knowledge(topic: str):
    """Get comprehensive topic knowledge with enhanced metadata"""
    try:
        if not enhanced_topic_manager:
            raise HTTPException(status_code=503, detail="Enhanced topic manager not initialized")
        
        knowledge = await enhanced_topic_manager.retrieve_topic_knowledge(topic)
        
        return {
            "success": True,
            "topic": topic,
            "knowledge": knowledge
        }
        
    except Exception as e:
        logger.error(f"Failed to get enhanced topic knowledge for '{topic}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v3/enhanced/topics/{topic}/update")
async def update_enhanced_topic(
    topic: str, 
    new_urls: List[str], 
    quality_threshold: float = 0.6
):
    """Update existing topic store with new content"""
    try:
        if not enhanced_topic_manager:
            raise HTTPException(status_code=503, detail="Enhanced topic manager not initialized")
        
        update_result = await enhanced_topic_manager.update_topic_store(
            topic, new_urls, quality_threshold
        )
        
        return {
            "success": True,
            "topic": topic,
            "update_result": update_result
        }
        
    except Exception as e:
        logger.error(f"Failed to update enhanced topic '{topic}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/enhanced/topics/{topic}/performance")
async def analyze_topic_performance(topic: str):
    """Analyze performance metrics for a topic store"""
    try:
        if not enhanced_topic_manager:
            raise HTTPException(status_code=503, detail="Enhanced topic manager not initialized")
        
        performance_analysis = await enhanced_topic_manager.analyze_topic_performance(topic)
        
        return {
            "success": True,
            "topic": topic,
            "performance_analysis": performance_analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze topic performance for '{topic}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Strategic Analysis API Endpoints

@app.post("/api/v3/analysis/sessions/create")
async def create_analysis_session(
    topic: str,
    user_id: str,
    analysis_parameters: Optional[Dict[str, Any]] = None
):
    """Create a new strategic analysis session"""
    try:
        if not analysis_session_manager:
            raise HTTPException(status_code=503, detail="Analysis session manager not initialized")
        
        session_id = await analysis_session_manager.create_analysis_session(
            topic, user_id, analysis_parameters
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "topic": topic,
            "user_id": user_id,
            "message": "Analysis session created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create analysis session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/analysis/sessions/{session_id}/execute")
async def execute_strategic_analysis(
    session_id: str,
    background_tasks: BackgroundTasks
):
    """Execute strategic analysis for a session"""
    try:
        if not analysis_session_manager:
            raise HTTPException(status_code=503, detail="Analysis session manager not initialized")
        
        # Execute analysis in background
        background_tasks.add_task(
            analysis_session_manager.execute_strategic_analysis,
            session_id
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Strategic analysis started in background",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Failed to execute strategic analysis for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/analysis/sessions/{session_id}/status")
async def get_analysis_session_status(session_id: str):
    """Get current status of an analysis session"""
    try:
        if not analysis_session_manager:
            raise HTTPException(status_code=503, detail="Analysis session manager not initialized")
        
        status = await analysis_session_manager.get_session_status(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Failed to get session status for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/analysis/sessions/{session_id}/results")
async def get_analysis_results(session_id: str):
    """Get complete analysis results for a session"""
    try:
        if not analysis_session_manager:
            raise HTTPException(status_code=503, detail="Analysis session manager not initialized")
        
        results = await analysis_session_manager.get_analysis_results(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to get analysis results for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Content Quality and Processing API Endpoints

@app.post("/api/v3/content/analyze-quality")
async def analyze_content_quality(
    content: str,
    url: str,
    topic: str
):
    """Analyze content quality using advanced metrics"""
    try:
        if not quality_analyzer:
            raise HTTPException(status_code=503, detail="Quality analyzer not initialized")
        
        quality_scores = await quality_analyzer.analyze_content_quality(content, url, topic)
        
        return {
            "success": True,
            "url": url,
            "topic": topic,
            "quality_scores": quality_scores
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze content quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/content/deduplicate")
async def deduplicate_content(
    documents: List[Dict[str, Any]],
    similarity_threshold: float = 0.85
):
    """Deduplicate content using advanced similarity metrics"""
    try:
        if not deduplication_service:
            raise HTTPException(status_code=503, detail="Deduplication service not initialized")
        
        deduplicated_docs, stats = await deduplication_service.deduplicate_content_batch(
            documents, similarity_threshold
        )
        
        return {
            "success": True,
            "original_count": len(documents),
            "deduplicated_count": len(deduplicated_docs),
            "duplicates_removed": len(documents) - len(deduplicated_docs),
            "deduplication_stats": stats,
            "documents": deduplicated_docs
        }
        
    except Exception as e:
        logger.error(f"Failed to deduplicate content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/optimization/parallel-processing")
async def optimize_parallel_processing(
    analysis_tasks: List[Dict[str, Any]],
    max_concurrent: int = 10
):
    """Optimize parallel processing for analysis tasks"""
    try:
        if not optimization_service:
            raise HTTPException(status_code=503, detail="Optimization service not initialized")
        
        results = await optimization_service.optimize_parallel_processing(
            analysis_tasks, max_concurrent
        )
        
        return {
            "success": True,
            "original_task_count": len(analysis_tasks),
            "processed_task_count": len(results),
            "optimization_results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to optimize parallel processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
