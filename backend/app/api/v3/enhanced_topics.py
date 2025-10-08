"""
Enhanced Topics API with Google Custom Search URL Collection Integration
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field

from ...services.integrated_topic_service import get_integrated_topic_service
from ...models.topic_models import TopicCreateRequest, TopicResponse, AnalysisType

router = APIRouter(tags=["enhanced-topics"])

class EnhancedTopicCreateRequest(TopicCreateRequest):
    """Enhanced topic creation request with URL collection options"""
    enable_url_collection: bool = Field(default=True, description="Enable automatic URL collection")
    max_urls_per_query: int = Field(default=10, description="Maximum URLs to collect per search query")
    include_initial_urls: bool = Field(default=True, description="Include provided initial URLs")

class TopicWithURLsResponse(TopicResponse):
    """Topic response with URL collection data"""
    url_collection: dict = Field(default={}, description="URL collection status and results")
    next_steps: dict = Field(default={}, description="Next processing steps")
    collected_urls: Optional[dict] = Field(default=None, description="Collected URLs data")

@router.post("/create", response_model=TopicWithURLsResponse, status_code=201)
async def create_topic_with_url_collection(
    request: EnhancedTopicCreateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create topic with integrated Google Custom Search URL collection
    This is the main endpoint that integrates all functionality
    """
    try:
        service = await get_integrated_topic_service()
        
        # Convert to base request for compatibility
        base_request = TopicCreateRequest(
            topic=request.topic,
            description=request.description,
            search_queries=request.search_queries if request.enable_url_collection else [],
            initial_urls=request.initial_urls if request.include_initial_urls else [],
            analysis_type=request.analysis_type,
            user_id=request.user_id,
            metadata=request.metadata or {}
        )
        
        # Create topic with URL collection
        result = await service.create_topic_with_url_collection(base_request)
        
        # Start Stage 1 processing in background if URLs were collected
        if result.get("url_collection", {}).get("urls_collected", 0) > 0:
            background_tasks.add_task(
                start_stage_1_background_processing,
                service,
                result["session_id"]
            )
        
        return TopicWithURLsResponse(**result)
        
    except Exception as e:
        import logging
        logging.error(f"Failed to create topic with URL collection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create topic with URL collection")

async def start_stage_1_background_processing(service, session_id: str):
    """Background task to start Stage 1 processing"""
    try:
        await service.start_stage_1_processing(session_id)
    except Exception as e:
        # Log error but don't fail the main request
        import logging
        logging.error(f"Background Stage 1 processing failed for {session_id}: {e}")

@router.get("/{session_id}", response_model=TopicWithURLsResponse)
async def get_topic_with_urls(
    session_id: str,
    user_id: str = Query(default=None, description="User ID for authorization")
):
    """Get topic with collected URLs and processing status"""
    try:
        service = await get_integrated_topic_service()
        result = await service.get_topic_with_urls(session_id, user_id=user_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return TopicWithURLsResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Failed to get topic: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get topic")

@router.get("", response_model=dict)
async def list_topics_with_url_stats(
    user_id: str = Query(..., description="User ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Page size")
):
    """List topics with URL collection statistics"""
    try:
        service = await get_integrated_topic_service()
        result = await service.list_topics_with_url_stats(user_id, page, page_size)
        return result
        
    except Exception as e:
        import logging
        logging.error(f"Failed to list topics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list topics")

@router.post("/{session_id}/collect-urls")
async def collect_urls_for_existing_topic(
    session_id: str,
    search_queries: List[str] = Query(..., description="Search queries"),
    max_urls_per_query: int = Query(default=10, description="Max URLs per query"),
    force_refresh: bool = Query(default=False, description="Force refresh existing collection")
):
    """Collect URLs for an existing topic"""
    try:
        service = await get_integrated_topic_service()
        
        if not service.url_collection_service:
            await service.initialize()
        
        from ...services.enhanced_url_collection_service import URLCollectionRequest
        
        collection_request = URLCollectionRequest(
            session_id=session_id,
            search_queries=search_queries,
            max_urls_per_query=max_urls_per_query,
            force_refresh=force_refresh
        )
        
        result = await service.url_collection_service.collect_urls_for_topic(collection_request)
        
        return {
            "session_id": session_id,
            "collection_status": result.collection_status,
            "urls_discovered": result.urls_discovered,
            "urls_stored": result.urls_stored,
            "queries_processed": result.queries_processed,
            "campaign_id": result.campaign_id,
            "error": result.error_message
        }
        
    except Exception as e:
        import logging
        logging.error(f"Failed to collect URLs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to collect URLs")

@router.get("/{session_id}/urls")
async def get_collected_urls(session_id: str):
    """Get all collected URLs for a topic"""
    try:
        # Query database directly for URLs
        from ...core.database_config import db_manager
        
        connection = await db_manager.get_connection()
        
        query = """
        SELECT url, title, description, source, collection_method, 
               domain, relevance_score, quality_score, priority_level,
               status, metadata, created_at
        FROM topic_urls
        WHERE session_id = $1
        ORDER BY priority_level ASC, quality_score DESC, created_at DESC
        """
        
        rows = await connection.fetch(query, session_id)
        
        urls = []
        for row in rows:
            urls.append({
                "url": row['url'],
                "title": row['title'] or "",
                "description": row['description'] or "",
                "source": row['source'],
                "collection_method": row['collection_method'] or "unknown",
                "domain": row['domain'] or "",
                "relevance_score": float(row['relevance_score']) if row['relevance_score'] else 0.0,
                "quality_score": float(row['quality_score']) if row['quality_score'] else 0.0,
                "priority_level": row['priority_level'] or 5,
                "status": row['status'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })
        
        return {
            "session_id": session_id,
            "url_count": len(urls),
            "urls": urls
        }
        
    except Exception as e:
        import logging
        logging.exception(f"Failed to get collected URLs for session {session_id}")
        raise HTTPException(status_code=500, detail="Failed to get collected URLs")

@router.post("/{session_id}/start-stage-1")
async def start_stage_1_processing(session_id: str):
    """Start Stage 1 processing (content extraction and vectorization)"""
    try:
        service = await get_integrated_topic_service()
        result = await service.start_stage_1_processing(session_id)
        return result
        
    except Exception as e:
        import logging
        logging.error(f"Failed to start Stage 1 processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start Stage 1 processing")

# Legacy endpoints for backward compatibility
@router.post("/create-simple", response_model=TopicResponse, status_code=201)
async def create_simple_topic(request: TopicCreateRequest):
    """Create topic without URL collection (legacy endpoint)"""
    try:
        service = await get_integrated_topic_service()
        result = await service.create_topic(request)
        return TopicResponse(**result)
        
    except Exception as e:
        import logging
        logging.error(f"Failed to create topic: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create topic")
