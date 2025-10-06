"""
Simple Topic Service for immediate database storage
Uses GCP Cloud SQL in production, SQLite for local development
"""
import logging
import os
from typing import List, Optional
from datetime import datetime
import uuid

from .database_manager import DatabaseManager
from .gcp_sql_manager import GCPSQLManager
from ..models.topic_models import (
    TopicCreateRequest, TopicResponse, TopicUpdateRequest,
    TopicListResponse, TopicStatus, AnalysisType
)

logger = logging.getLogger(__name__)

class SimpleTopicService:
    """Simple Topic Service with configurable database storage"""
    
    def __init__(self):
        # Use GCP Cloud SQL in production, SQLite for local development
        # Be explicit about environment to avoid accidental GCP usage in development
        use_gcp = os.getenv("ENVIRONMENT") == "production" and os.getenv("LOCAL_DEVELOPMENT_MODE", "false") != "true"
        if use_gcp:
            self.db_manager = GCPSQLManager()
            logger.info("SimpleTopicService initialized with GCP Cloud SQL")
        else:
            self.db_manager = DatabaseManager()
            logger.info("SimpleTopicService initialized with SQLite database")
    
    async def create_topic(self, request: TopicCreateRequest) -> TopicResponse:
        """Create topic and store in database"""
        try:
            logger.info(f"Creating topic: {request.topic} for user: {request.user_id}")
            
            # Generate unique session ID using UUID to prevent collisions
            session_id = f"topic_{request.user_id}_{uuid.uuid4().hex}"
            
            # Prepare topic data
            topic_data = {
                'session_id': session_id,
                'topic': request.topic,
                'description': request.description,
                'search_queries': request.search_queries,
                'initial_urls': request.initial_urls,
                'analysis_type': request.analysis_type,
                'user_id': request.user_id,
                'status': TopicStatus.CREATED.value,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'metadata': {}
            }
            
            # Store in database - handle both sync and async database managers
            if hasattr(self.db_manager, 'initialize'):
                # GCP SQL Manager (async) - initialize first, then create topic
                await self.db_manager.initialize()
                result = await self.db_manager.create_topic(request)
                logger.info(f"✅ Topic created successfully via GCP SQL: {session_id}")
                return result
            else:
                # SQLite Manager (sync) - convert request to dict format
                success = self.db_manager.create_topic(topic_data)
                if success:
                    logger.info(f"✅ Topic created successfully via SQLite: {session_id}")
                    return TopicResponse(
                        session_id=session_id,
                        topic=request.topic,
                        description=request.description,
                        search_queries=request.search_queries,
                        initial_urls=request.initial_urls,
                        analysis_type=request.analysis_type,
                        user_id=request.user_id,
                        created_at=datetime.fromisoformat(topic_data['created_at']),
                        updated_at=datetime.fromisoformat(topic_data['updated_at']),
                        status=TopicStatus.CREATED,
                        metadata={}
                    )
                else:
                    raise Exception("Failed to store topic in SQLite database")
                
        except Exception as e:
            logger.exception("Failed to create topic")
            raise Exception(f"Failed to create topic: {str(e)}") from e
    
    async def get_topic(self, session_id: str, user_id: str) -> Optional[TopicResponse]:
        """Get topic by session ID"""
        try:
            # Handle both sync and async database managers
            if hasattr(self.db_manager, 'initialize'):
                # GCP SQL Manager (async)
                await self.db_manager.initialize()
                topic_data = await self.db_manager.get_topic(session_id)
            else:
                # SQLite Manager (sync)
                topic_data = self.db_manager.get_topic(session_id)
            
            if not topic_data:
                return None
            
            # Verify user owns this topic
            if topic_data['user_id'] != user_id:
                logger.warning(f"User {user_id} attempted to access topic {session_id} owned by {topic_data['user_id']}")
                return None
            
            # Convert database data to response
            return TopicResponse(
                session_id=session_id,
                topic=topic_data['topic'],
                description=topic_data['description'],
                search_queries=topic_data.get('search_queries', []),
                initial_urls=topic_data.get('initial_urls', []),
                analysis_type=topic_data['analysis_type'],
                user_id=topic_data['user_id'],
                created_at=datetime.fromisoformat(topic_data['created_at']),
                updated_at=datetime.fromisoformat(topic_data['updated_at']),
                status=topic_data['status'],
                metadata=topic_data.get('metadata', {})
            )
            
        except Exception as e:
            logger.exception(f"Failed to get topic: {session_id}")
            raise Exception(f"Failed to get topic: {str(e)}") from e
    
    async def list_topics(self, user_id: str, limit: int = 50, offset: int = 0, page: int = None, page_size: int = None, sort_by: str = None, sort_order: str = None) -> TopicListResponse:
        """List topics for a user"""
        try:
            # Use page_size if provided, otherwise use limit
            actual_limit = page_size if page_size is not None else limit
            
            # Validate offset alignment with page size
            if offset % actual_limit != 0 and actual_limit > 0:
                logger.warning(f"Offset {offset} not aligned with page_size {actual_limit}")
            
            # Handle both sync and async database managers
            if hasattr(self.db_manager, 'initialize'):
                # GCP SQL Manager (async) - returns TopicListResponse
                await self.db_manager.initialize()
                result = await self.db_manager.list_topics(user_id, page=offset // actual_limit + 1 if actual_limit > 0 else 1, page_size=actual_limit)
                return result
            else:
                # SQLite Manager (sync) - returns tuple
                topics_data, total_count = self.db_manager.list_topics(user_id, actual_limit, offset)
                
                # Convert to TopicResponse objects
                topics = []
                for topic_data in topics_data:
                    topic = TopicResponse(
                        session_id=topic_data['session_id'],
                        topic=topic_data['topic'],
                        description=topic_data['description'],
                        search_queries=topic_data.get('search_queries', []),
                        initial_urls=topic_data.get('initial_urls', []),
                        analysis_type=topic_data['analysis_type'],
                        user_id=topic_data['user_id'],
                        created_at=datetime.fromisoformat(topic_data['created_at']),
                        updated_at=datetime.fromisoformat(topic_data['updated_at']),
                        status=topic_data['status'],
                        metadata=topic_data.get('metadata', {})
                    )
                    topics.append(topic)
                
                return TopicListResponse(
                    topics=topics,
                    total=total_count,
                    page=offset // actual_limit + 1 if actual_limit > 0 else 1,
                    page_size=actual_limit,
                    has_next=len(topics) == actual_limit,
                    has_previous=offset > 0
                )
            
        except Exception as e:
            logger.exception("Failed to list topics")
            raise Exception(f"Failed to list topics: {str(e)}") from e
    
    async def update_topic(self, session_id: str, request: TopicUpdateRequest, user_id: str) -> TopicResponse:
        """Update topic"""
        try:
            # Get existing topic
            existing_topic = await self.get_topic(session_id, user_id)
            if not existing_topic:
                raise Exception("Topic not found")
            
            # Prepare update data
            update_data = {
                'session_id': session_id,
                'topic': request.topic if request.topic is not None else existing_topic.topic,
                'description': request.description if request.description is not None else existing_topic.description,
                'analysis_type': request.analysis_type if request.analysis_type is not None else existing_topic.analysis_type,
                'status': request.status if request.status is not None else existing_topic.status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Update in database
            success = self.db_manager.update_topic(update_data)
            
            if success:
                return TopicResponse(
                    session_id=session_id,
                    topic=update_data['topic'],
                    description=update_data['description'],
                    search_queries=existing_topic.search_queries,
                    initial_urls=existing_topic.initial_urls,
                    analysis_type=update_data['analysis_type'],
                    user_id=user_id,
                    created_at=existing_topic.created_at,
                    updated_at=datetime.fromisoformat(update_data['updated_at']),
                    status=update_data['status'],
                    metadata=existing_topic.metadata
                )
            else:
                raise Exception("Failed to update topic in database")
                
        except Exception as e:
            logger.exception(f"Failed to update topic: {session_id}")
            raise Exception(f"Failed to update topic: {str(e)}") from e
    
    async def delete_topic(self, session_id: str, user_id: str) -> bool:
        """Delete topic"""
        try:
            # Verify user owns this topic before deleting
            topic_data = self.db_manager.get_topic(session_id)
            if not topic_data:
                return False
            if topic_data['user_id'] != user_id:
                logger.warning(f"User {user_id} attempted to delete topic {session_id} owned by {topic_data['user_id']}")
                return False
            
            success = self.db_manager.delete_topic(session_id)
            logger.info(f"Topic deletion {'successful' if success else 'failed'}: {session_id}")
            return success
            
        except Exception as e:
            logger.exception(f"Failed to delete topic: {session_id}")
            raise Exception(f"Failed to delete topic: {str(e)}") from e

# Singleton instance
_topic_service_instance = None

def get_simple_topic_service() -> SimpleTopicService:
    """Get singleton instance of SimpleTopicService"""
    global _topic_service_instance
    if _topic_service_instance is None:
        _topic_service_instance = SimpleTopicService()
    return _topic_service_instance
