"""
Topic Management API Endpoints
REST API for topic CRUD operations with Google Cloud Firestore persistence
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging

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
from app.services.topic_service import get_topic_service

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
async def create_topic(
    request: TopicCreateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new topic"""
    try:
        logger.info(f"Creating topic: {request.topic} for user: {user_id}")
        
        # Create topic
        topic = await get_topic_service().create_topic(request)
        
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
        
        topic = await get_topic_service().get_topic(session_id, user_id)
        
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
        
        topic = await get_topic_service().update_topic(session_id, request, user_id)
        
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
        
        success = await get_topic_service().delete_topic(session_id, user_id)
        
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
        
        topics = await get_topic_service().list_topics(
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
        
        results = await get_topic_service().search_topics(request)
        
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
        
        stats = await get_topic_service().get_topic_stats(user_id)
        
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
                await get_topic_service().create_topic(request)
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
