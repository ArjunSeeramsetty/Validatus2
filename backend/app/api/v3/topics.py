"""
Topic Management API Endpoints
REST API for topic CRUD operations with Google Cloud Firestore persistence
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.models.topic_models import (
    TopicConfig,
    TopicCreateRequest,
    TopicUpdateRequest,
    TopicResponse,
    TopicListResponse,
    TopicSearchRequest,
    AnalysisType,
    TopicStatus
)
from app.services.simple_topic_service import get_simple_topic_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v3/topics", tags=["topics"])


# Dependency to get current user ID (placeholder for authentication)
async def get_current_user_id() -> str:
    """
    Get current user ID from authentication
    For now, returns a demo user ID
    In production, this would extract from JWT token or session
    """
    # TODO: Implement proper authentication
    return "demo_user_123"


@router.post("/", response_model=TopicResponse, status_code=201)
@router.post("/create", response_model=TopicResponse, status_code=201)
async def create_topic(
    request: TopicCreateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new topic"""
    try:
        logger.info(f"Creating topic: {request.topic} for user: {user_id}")
        
        # Create topic
        topic_service = get_simple_topic_service()
        topic = await topic_service.create_topic(request)
        
        return topic
        
    except Exception as e:
        logger.error(f"Failed to create topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=TopicResponse)
async def get_topic(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a topic by session ID"""
    try:
        logger.info(f"Getting topic: {session_id} for user: {user_id}")
        
        topic_service = get_simple_topic_service()
        topic = await topic_service.get_topic(session_id, user_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return topic
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get topic {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}", response_model=TopicResponse)
async def update_topic(
    session_id: str,
    request: TopicUpdateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Update an existing topic"""
    try:
        logger.info(f"Updating topic: {session_id} for user: {user_id}")
        
        topic_service = get_simple_topic_service()
        topic = await topic_service.update_topic(session_id, request, user_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return topic
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update topic {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}", status_code=204)
async def delete_topic(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a topic"""
    try:
        logger.info(f"Deleting topic: {session_id} for user: {user_id}")
        
        topic_service = get_simple_topic_service()
        success = await topic_service.delete_topic(session_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete topic {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=TopicListResponse)
async def list_topics(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    user_id: str = Depends(get_current_user_id)
):
    """List topics for the current user with pagination"""
    try:
        logger.info(f"Listing topics for user: {user_id}, page: {page}")
        
        topic_service = get_simple_topic_service()
        topics = await topic_service.list_topics(
            user_id=user_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return topics
        
    except Exception as e:
        logger.error(f"Failed to list topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=TopicListResponse)
async def search_topics(
    request: TopicSearchRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Search topics with filters and text search"""
    try:
        logger.info(f"Searching topics for user: {user_id}")
        
        # Set user_id in request if not provided
        if not request.user_id:
            request.user_id = user_id
        
        topic_service = get_simple_topic_service()
        results = await topic_service.search_topics(request)
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_topic_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get topic statistics for the current user"""
    try:
        logger.info(f"Getting topic stats for user: {user_id}")
        
        topic_service = get_simple_topic_service()
        stats = await topic_service.get_topic_stats(user_id)
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get topic stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis-types/", response_model=List[str])
async def get_analysis_types():
    """Get available analysis types"""
    return [analysis_type.value for analysis_type in AnalysisType]


@router.get("/statuses/", response_model=List[str])
async def get_topic_statuses():
    """Get available topic statuses"""
    return [status.value for status in TopicStatus]


# Migration endpoint to help transition from localStorage
@router.post("/migrate-from-localstorage", response_model=Dict[str, Any])
async def migrate_from_localstorage(
    topics: List[Dict[str, Any]],
    user_id: str = Depends(get_current_user_id)
):
    """Migrate topics from localStorage to Firestore"""
    try:
        logger.info(f"Migrating {len(topics)} topics from localStorage for user: {user_id}")
        
        migrated_count = 0
        errors = []
        
        for topic_data in topics:
            try:
                # Convert localStorage topic to TopicCreateRequest
                request = TopicCreateRequest(
                    topic=topic_data.get("topic", ""),
                    description=topic_data.get("description", ""),
                    search_queries=topic_data.get("search_queries", []),
                    initial_urls=topic_data.get("initial_urls", []),
                    analysis_type=AnalysisType(topic_data.get("analysis_type", "comprehensive")),
                    user_id=user_id,
                    metadata={
                        "migrated_from_localstorage": True,
                        "original_session_id": topic_data.get("session_id"),
                        "original_created_at": topic_data.get("created_at")
                    }
                )
                
                # Create topic
                topic_service = get_simple_topic_service()
                await topic_service.create_topic(request)
                migrated_count += 1
                
            except Exception as e:
                errors.append({
                    "session_id": topic_data.get("session_id"),
                    "error": str(e)
                })
        
        return {
            "migrated_count": migrated_count,
            "total_topics": len(topics),
            "errors": errors,
            "message": f"Successfully migrated {migrated_count} out of {len(topics)} topics"
        }
        
    except Exception as e:
        logger.error(f"Failed to migrate topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}/status", response_model=TopicResponse)
async def update_topic_status(
    session_id: str,
    status: TopicStatus,
    progress_data: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_current_user_id)
):
    """Update topic status (CREATED -> IN_PROGRESS -> COMPLETED)"""
    try:
        logger.info(f"Updating topic status: {session_id} -> {status.value} for user: {user_id}")
        
        topic_service = get_simple_topic_service()
        success = await topic_service.update_topic_status(session_id, status, user_id, progress_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Return updated topic
        updated_topic = await topic_service.get_topic(session_id, user_id)
        return updated_topic
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update topic status {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{status}", response_model=List[TopicResponse])
async def get_topics_by_status(
    status: TopicStatus,
    user_id: str = Depends(get_current_user_id)
):
    """Get topics filtered by specific status"""
    try:
        logger.info(f"Getting topics by status: {status.value} for user: {user_id}")
        
        topic_service = get_simple_topic_service()
        topics = await topic_service.get_topics_by_status(user_id, status)
        
        return topics
        
    except Exception as e:
        logger.error(f"Failed to get topics by status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/start-workflow")
async def start_topic_workflow(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Start the complete topic workflow (URLs -> SCRAPING -> SCORING)"""
    try:
        logger.info(f"Starting workflow for topic: {session_id}")
        
        # Import workflow manager
        from app.services.workflow_manager import get_workflow_manager_instance
        
        workflow_manager = get_workflow_manager_instance()
        
        # Execute the complete workflow
        workflow_results = await workflow_manager.execute_workflow(session_id, user_id)
        
        return {
            "session_id": session_id,
            "status": "workflow_completed",
            "results": workflow_results,
            "message": "Topic workflow completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to start workflow for topic {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/collect-urls")
async def collect_urls_for_topic(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Collect URLs for a topic using web search"""
    try:
        logger.info(f"Collecting URLs for topic: {session_id}")
        
        topic_service = get_simple_topic_service()
        
        # Get topic details
        topic = await topic_service.get_topic(session_id, user_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Update status to IN_PROGRESS
        await topic_service.update_topic_status(
            session_id, 
            TopicStatus.IN_PROGRESS, 
            user_id,
            {"stage": "url_collection", "started_at": datetime.utcnow().isoformat()}
        )
        
        # Import URL orchestrator
        from app.services.gcp_url_orchestrator import GCPURLOrchestrator
        from app.core.gcp_config import get_gcp_settings
        
        settings = get_gcp_settings()
        url_orchestrator = GCPURLOrchestrator(project_id=settings.project_id)
        
        # Collect URLs
        urls_result = await url_orchestrator.collect_urls_for_topic(
            topic.topic,
            topic.search_queries,
            max_urls=50
        )
        
        # Update topic with collected URLs (urls_result is a List[str])
        updated_urls = list(set(topic.initial_urls + urls_result))
        
        # Create update request
        update_request = TopicUpdateRequest(
            initial_urls=updated_urls,
            metadata={
                **topic.metadata,
                "url_collection": {
                    "completed_at": datetime.utcnow().isoformat(),
                    "urls_collected": len(urls_result),
                    "total_urls": len(updated_urls)
                }
            }
        )
        
        # Update topic
        updated_topic = await topic_service.update_topic(session_id, update_request, user_id)
        
        # Update status to COMPLETED
        await topic_service.update_topic_status(
            session_id, 
            TopicStatus.COMPLETED, 
            user_id,
            {
                "stage": "url_collection_completed",
                "urls_collected": len(urls_result),
                "total_urls": len(updated_urls)
            }
        )
        
        return {
            "session_id": session_id,
            "status": "urls_collected",
            "urls_collected": len(urls_result),
            "total_urls": len(updated_urls),
            "new_urls": urls_result,
            "updated_topic": updated_topic,
            "message": f"Successfully collected {len(urls_result)} new URLs"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to collect URLs for topic {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/urls")
async def get_topic_urls(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get URLs for a specific topic"""
    try:
        logger.info(f"Getting URLs for topic: {session_id}")
        
        topic_service = get_simple_topic_service()
        
        # Get topic details
        topic = await topic_service.get_topic(session_id, user_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return {
            "session_id": session_id,
            "topic": topic.topic,
            "urls": topic.initial_urls,
            "url_count": len(topic.initial_urls),
            "last_updated": topic.updated_at,
            "metadata": topic.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get URLs for topic {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
