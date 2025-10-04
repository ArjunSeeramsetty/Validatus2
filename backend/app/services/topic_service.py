"""
Updated Topic Service with GCP Persistence Integration
Now uses the unified GCP persistence manager for all operations
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

# Custom exceptions
class TopicServiceError(Exception):
    """Base exception for topic service errors"""
    pass

class RateLimitExceededError(TopicServiceError):
    """Exception raised when rate limit is exceeded"""
    pass

from .gcp_persistence_manager import get_gcp_persistence_manager
from ..models.topic_models import (
    TopicCreateRequest, TopicResponse, TopicUpdateRequest,
    TopicListResponse, TopicSearchRequest, TopicStatus, AnalysisType
)

logger = logging.getLogger(__name__)

class TopicService:
    """Enhanced Topic Service with full GCP persistence"""
    
    def __init__(self):
        self.persistence_manager = get_gcp_persistence_manager()
        logger.info("TopicService initialized with GCP persistence")
    
    async def create_topic(self, request: TopicCreateRequest) -> TopicResponse:
        """Create topic with complete GCP persistence"""
        try:
            logger.info(f"Creating topic: {request.topic} for user: {request.user_id}")
            
            # Use the unified persistence manager
            topic_response = await self.persistence_manager.create_topic_complete(request)
            
            logger.info(f"✅ Topic created successfully: {topic_response.session_id}")
            return topic_response
            
        except Exception as e:
            logger.exception("Failed to create topic")
            raise Exception(f"Failed to create topic: {str(e)}") from e
    
    async def get_topic(self, session_id: str, user_id: str) -> Optional[TopicResponse]:
        """Get topic with caching optimization"""
        try:
            topic = await self.persistence_manager.get_topic_complete(session_id, user_id)
            
            if topic:
                logger.debug(f"Retrieved topic: {session_id}")
            else:
                logger.warning(f"Topic not found: {session_id} for user: {user_id}")
            
            return topic
            
        except Exception as e:
            logger.error(f"Failed to get topic {session_id}: {e}")
            return None
    
    async def list_topics(self, user_id: str, page: int = 1, page_size: int = 20,
                         sort_by: str = "created_at", sort_order: str = "desc") -> TopicListResponse:
        """List topics with enhanced performance"""
        try:
            logger.info(f"Listing topics for user: {user_id}, page: {page}")
            
            topics_response = await self.persistence_manager.list_topics_complete(
                user_id=user_id,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            logger.info(f"Listed {len(topics_response.topics)} topics for user: {user_id}")
            return topics_response
            
        except Exception as e:
            logger.error(f"Failed to list topics for user {user_id}: {e}")
            return TopicListResponse(
                topics=[], total=0, page=page, page_size=page_size, 
                has_next=False, has_previous=False
            )
    
    async def update_topic_status(self, session_id: str, status: TopicStatus, 
                                user_id: str, progress_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update topic status with workflow tracking"""
        try:
            logger.info(f"Updating topic status: {session_id} -> {status.value}")
            
            # Update in SQL
            success = await self.persistence_manager.sql_manager.update_topic_status(
                session_id, status, user_id, progress_data
            )
            
            if success:
                # Update cache
                cached_data = await self.persistence_manager.redis_manager.get_session_data(session_id)
                if cached_data:
                    cached_data['status'] = status.value
                    await self.persistence_manager.redis_manager.cache_session_data(
                        session_id, cached_data, ttl=86400
                    )
                
                # Update workflow progress
                if progress_data:
                    await self.persistence_manager.redis_manager.cache_workflow_progress(
                        session_id, status.value, progress_data
                    )
                
                # Track activity
                await self.persistence_manager.redis_manager.track_user_activity(
                    user_id,
                    "status_updated",
                    {
                        "session_id": session_id,
                        "new_status": status.value,
                        "progress_data": progress_data
                    }
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update topic status {session_id}: {e}")
            return False
    
    async def start_topic_workflow(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Start the complete 5-task workflow"""
        try:
            logger.info(f"Starting workflow for topic: {session_id}")
            
            # Check rate limiting
            rate_limit_ok = await self.persistence_manager.redis_manager.check_rate_limit(
                user_id, "workflow_start", limit=5, window_seconds=3600  # 5 workflows per hour
            )
            
            if not rate_limit_ok:
                raise RateLimitExceededError("Rate limit exceeded. Please wait before starting another workflow.")
            
            # Execute complete workflow
            workflow_result = await self.persistence_manager.execute_complete_workflow(session_id, user_id)
            
            return {
                "success": True,
                "session_id": session_id,
                "workflow_result": workflow_result,
                "message": "Workflow started successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to start workflow for {session_id}: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "message": "Failed to start workflow"
            }
    
    async def get_workflow_progress(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get real-time workflow progress"""
        try:
            progress = await self.persistence_manager.redis_manager.get_workflow_progress(session_id)
            
            if progress:
                # Verify user ownership
                topic = await self.get_topic(session_id, user_id)
                if not topic:
                    return None
                
                # Add queue information
                queue_length = await self.persistence_manager.redis_manager.get_queue_length(session_id)
                progress['queue_length'] = queue_length
                
                return progress
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get workflow progress for {session_id}: {e}")
            return None
    
    async def get_topic_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive topic statistics"""
        try:
            # Get basic stats using server-side aggregation instead of fetching all topics
            # This prevents memory issues with large topic lists
            stats_response = await self.persistence_manager.sql_manager._get_topic_stats_aggregated(user_id)
            
            total_topics = stats_response["total_topics"]
            topics_by_status = stats_response["topics_by_status"]
            topics_by_type = stats_response["topics_by_type"]
            
            # Get recent activity from Redis
            recent_activity = await self.persistence_manager.redis_manager.get_recent_user_activity(
                user_id, hours=24
            )
            
            return {
                "total_topics": total_topics,
                "topics_by_status": topics_by_status,
                "topics_by_type": topics_by_type,
                "recent_activity_count": len(recent_activity),
                "recent_activities": recent_activity[:10]  # Last 10 activities
            }
            
        except Exception as e:
            logger.error(f"Failed to get topic stats for user {user_id}: {e}")
            return {
                "total_topics": 0,
                "topics_by_status": {},
                "topics_by_type": {},
                "recent_activity_count": 0
            }
    
    # Additional helper methods
    async def delete_topic(self, session_id: str, user_id: str) -> bool:
        """Delete topic and all associated data"""
        try:
            logger.info(f"Deleting topic: {session_id}")
            
            # Verify ownership
            topic = await self.get_topic(session_id, user_id)
            if not topic:
                return False
            
            # Delete from all GCP services
            async with self.persistence_manager.sql_manager.get_connection() as conn:
                async with conn.transaction():
                    # Delete from SQL (cascading deletes will handle related tables)
                    result = await conn.execute(
                        "DELETE FROM topics WHERE session_id = $1 AND user_id = $2",
                        session_id, user_id
                    )
                    
                    if result.split()[-1] != '1':
                        return False
            
            # Delete from Cloud Storage
            await self.persistence_manager.storage_manager.batch_delete_content(session_id)
            
            # Delete from Redis cache
            await self.persistence_manager.redis_manager.client.delete(f"session:{session_id}")
            await self.persistence_manager.redis_manager.client.delete(f"workflow:{session_id}")
            
            # Track deletion activity
            await self.persistence_manager.redis_manager.track_user_activity(
                user_id,
                "topic_deleted",
                {"session_id": session_id, "topic": topic.topic}
            )
            
            logger.info(f"✅ Topic deleted successfully: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete topic {session_id}: {e}")
            return False
    
    async def search_topics(self, request: TopicSearchRequest) -> TopicListResponse:
        """Search topics with advanced filtering"""
        try:
            # For now, delegate to list_topics with basic filtering
            # In production, you could implement full-text search using SQL or Elasticsearch
            
            # Apply basic filters through SQL
            topics_response = await self.list_topics(
                user_id=request.user_id,
                page=request.page,
                page_size=request.page_size,
                sort_by=request.sort_by,
                sort_order=request.sort_order
            )
            
            # Apply additional filtering if needed
            if request.query or request.analysis_type or request.status:
                filtered_topics = []
                
                for topic in topics_response.topics:
                    # Text search
                    if request.query:
                        search_text = f"{topic.topic} {topic.description}".lower()
                        if request.query.lower() not in search_text:
                            continue
                    
                    # Type filter
                    if request.analysis_type and topic.analysis_type != request.analysis_type:
                        continue
                    
                    # Status filter  
                    if request.status and topic.status != request.status:
                        continue
                    
                    filtered_topics.append(topic)
                
                topics_response.topics = filtered_topics
                topics_response.total = len(filtered_topics)
            
            return topics_response
            
        except Exception as e:
            logger.error(f"Failed to search topics: {e}")
            return TopicListResponse(
                topics=[], total=0, page=request.page, page_size=request.page_size,
                has_next=False, has_previous=False
            )
    
    async def update_topic(self, session_id: str, request: TopicUpdateRequest, user_id: str) -> Optional[TopicResponse]:
        """Update topic with GCP persistence"""
        try:
            logger.info(f"Updating topic: {session_id}")
            
            # Get existing topic
            existing_topic = await self.get_topic(session_id, user_id)
            if not existing_topic:
                return None
            
            # Update in SQL
            async with self.persistence_manager.sql_manager.get_connection() as conn:
                query = """
                    UPDATE topics 
                    SET topic = COALESCE($1, topic),
                        description = COALESCE($2, description),
                        search_queries = COALESCE($3, search_queries),
                        initial_urls = COALESCE($4, initial_urls),
                        metadata = metadata || $5::jsonb,
                        updated_at = NOW()
                    WHERE session_id = $6 AND user_id = $7
                    RETURNING *
                """
                
                result = await conn.fetchrow(
                    query,
                    request.topic,
                    request.description,
                    request.search_queries,
                    request.initial_urls,
                    request.metadata or {},
                    session_id,
                    user_id
                )
                
                if not result:
                    return None
            
            # Update cache
            updated_topic = TopicResponse(
                session_id=result['session_id'],
                topic=result['topic'],
                description=result['description'],
                search_queries=result['search_queries'] or [],
                initial_urls=result['initial_urls'] or [],
                analysis_type=AnalysisType(result['analysis_type']),
                user_id=result['user_id'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                status=TopicStatus(result['status']),
                metadata=result['metadata'] or {}
            )
            
            # Update cache
            session_cache_data = {
                "session_id": session_id,
                "topic": updated_topic.topic,
                "user_id": user_id,
                "status": updated_topic.status.value,
                "created_at": updated_topic.created_at.isoformat(),
                "updated_at": updated_topic.updated_at.isoformat(),
                "analysis_type": updated_topic.analysis_type.value
            }
            
            await self.persistence_manager.redis_manager.cache_session_data(
                session_id, session_cache_data, ttl=86400
            )
            
            # Track activity
            await self.persistence_manager.redis_manager.track_user_activity(
                user_id,
                "topic_updated",
                {"session_id": session_id, "changes": request.dict(exclude_unset=True)}
            )
            
            logger.info(f"✅ Topic updated successfully: {session_id}")
            return updated_topic
            
        except Exception as e:
            logger.error(f"Failed to update topic {session_id}: {e}")
            return None

# Global singleton instance
_topic_service_instance = None

def get_topic_service_instance() -> TopicService:
    """Get the singleton TopicService instance"""
    global _topic_service_instance
    if _topic_service_instance is None:
        _topic_service_instance = TopicService()
    return _topic_service_instance
