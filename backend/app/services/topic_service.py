"""
Topic Service for Validatus Platform
Handles topic CRUD operations with Google Cloud Firestore
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import firestore
from google.cloud.firestore import Query

from app.models.topic_models import (
    TopicConfig, 
    TopicCreateRequest, 
    TopicUpdateRequest, 
    TopicResponse, 
    TopicListResponse,
    TopicSearchRequest,
    TopicStatus,
    AnalysisType
)
from app.core.gcp_config import get_gcp_settings

logger = logging.getLogger(__name__)


class TopicService:
    """Service for managing topics with Firestore persistence"""
    
    def __init__(self):
        self.settings = None
        self.db = None
        self._use_local_fallback = False
        self._local_storage = {}  # In-memory storage for local development
        self._initialize_firestore()
    
    def _initialize_firestore(self):
        """Initialize Firestore client"""
        try:
            # Always use local fallback for development
            # Check if we're in local development mode or if Firestore is not available
            import os
            
            # Force local development mode for now to ensure persistence works
            logger.info(f"TopicService initializing - instance ID: {id(self)}")
            logger.info("Using local in-memory storage for development")
            self.db = None
            self._use_local_fallback = True
            logger.info(f"TopicService initialized - local storage ID: {id(self._local_storage)}")
            return
            
            # Original logic (commented out for now):
            # if os.getenv('LOCAL_DEVELOPMENT_MODE', '').lower() == 'true':
            #     logger.info("Local development mode detected - using in-memory storage")
            #     self.db = None
            #     self._use_local_fallback = True
            #     return
            
            # # Try to get settings for Firestore initialization
            # try:
            #     self.settings = get_gcp_settings()
            # except Exception as e:
            #     logger.warning(f"Failed to load GCP settings: {e}")
            #     logger.info("Using local in-memory storage for development")
            #     self.db = None
            #     self._use_local_fallback = True
            #     return
            
            # # Initialize Firestore client
            # # In GCP, this will use the default service account
            # # For local development, it will use application default credentials
            # self.db = firestore.Client(project=self.settings.project_id)
            # logger.info("Firestore client initialized successfully")
            # self._use_local_fallback = False
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            logger.info("Using local in-memory storage for development")
            self.db = None
            self._use_local_fallback = True
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        import time
        import random
        import string
        
        timestamp = int(time.time() * 1000)
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"topic_{timestamp}_{random_suffix}"
    
    def _topic_config_to_dict(self, topic: TopicConfig) -> Dict[str, Any]:
        """Convert TopicConfig to dictionary for Firestore storage"""
        return {
            "session_id": topic.session_id,
            "topic": topic.topic,
            "description": topic.description,
            "search_queries": topic.search_queries,
            "initial_urls": topic.initial_urls,
            "analysis_type": topic.analysis_type.value,
            "user_id": topic.user_id,
            "created_at": topic.created_at,
            "updated_at": topic.updated_at,
            "status": topic.status.value,
            "metadata": topic.metadata
        }
    
    def _dict_to_topic_config(self, data: Dict[str, Any]) -> TopicConfig:
        """Convert Firestore document to TopicConfig"""
        return TopicConfig(
            session_id=data["session_id"],
            topic=data["topic"],
            description=data["description"],
            search_queries=data.get("search_queries", []),
            initial_urls=data.get("initial_urls", []),
            analysis_type=AnalysisType(data.get("analysis_type", "comprehensive")),
            user_id=data["user_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            status=TopicStatus(data.get("status", "created")),
            metadata=data.get("metadata", {})
        )
    
    async def create_topic(self, request: TopicCreateRequest) -> TopicResponse:
        """Create a new topic"""
        try:
            logger.info(f"Creating topic: {request.topic} - TopicService instance ID: {id(self)}")
            logger.info(f"Using local fallback: {self._use_local_fallback}")
            logger.info(f"Local storage ID: {id(self._local_storage)}")
            
            # Generate unique session ID
            session_id = self._generate_session_id()
            
            # Create topic configuration
            topic = TopicConfig(
                session_id=session_id,
                topic=request.topic,
                description=request.description,
                search_queries=request.search_queries,
                initial_urls=request.initial_urls,
                analysis_type=request.analysis_type,
                user_id=request.user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                status=TopicStatus.CREATED,
                metadata=request.metadata
            )
            
            if self._use_local_fallback:
                # Store in local memory
                self._local_storage[session_id] = self._topic_config_to_dict(topic)
                logger.info(f"Topic created in local storage: {session_id}")
            else:
                # Store in Firestore
                topic_ref = self.db.collection('topics').document(session_id)
                topic_dict = self._topic_config_to_dict(topic)
                topic_ref.set(topic_dict)
                logger.info(f"Topic created in Firestore: {session_id}")
            
            # Return response
            return TopicResponse(
                session_id=topic.session_id,
                topic=topic.topic,
                description=topic.description,
                search_queries=topic.search_queries,
                initial_urls=topic.initial_urls,
                analysis_type=topic.analysis_type,
                user_id=topic.user_id,
                created_at=topic.created_at,
                updated_at=topic.updated_at,
                status=topic.status,
                metadata=topic.metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to create topic: {e}")
            raise Exception(f"Failed to create topic: {str(e)}")
    
    async def get_topic(self, session_id: str, user_id: str) -> Optional[TopicResponse]:
        """Get a topic by session ID"""
        try:
            if self._use_local_fallback:
                # Get from local storage
                if session_id not in self._local_storage:
                    logger.warning(f"Topic not found in local storage: {session_id}")
                    return None
                
                topic_data = self._local_storage[session_id]
                
                # Check user ownership
                if topic_data.get("user_id") != user_id:
                    logger.warning(f"User {user_id} attempted to access topic {session_id} owned by {topic_data.get('user_id')}")
                    return None
                
                topic = self._dict_to_topic_config(topic_data)
                
                return TopicResponse(
                    session_id=topic.session_id,
                    topic=topic.topic,
                    description=topic.description,
                    search_queries=topic.search_queries,
                    initial_urls=topic.initial_urls,
                    analysis_type=topic.analysis_type,
                    user_id=topic.user_id,
                    created_at=topic.created_at,
                    updated_at=topic.updated_at,
                    status=topic.status,
                    metadata=topic.metadata
                )
            else:
                if not self.db:
                    raise Exception("Firestore not initialized")
                
                # Get topic from Firestore
                topic_ref = self.db.collection('topics').document(session_id)
                topic_doc = topic_ref.get()
                
                if not topic_doc.exists:
                    return None
                
                topic_data = topic_doc.to_dict()
                
                # Check user ownership
                if topic_data.get("user_id") != user_id:
                    logger.warning(f"User {user_id} attempted to access topic {session_id} owned by {topic_data.get('user_id')}")
                    return None
                
                topic = self._dict_to_topic_config(topic_data)
                
                return TopicResponse(
                    session_id=topic.session_id,
                    topic=topic.topic,
                    description=topic.description,
                    search_queries=topic.search_queries,
                    initial_urls=topic.initial_urls,
                    analysis_type=topic.analysis_type,
                    user_id=topic.user_id,
                    created_at=topic.created_at,
                    updated_at=topic.updated_at,
                    status=topic.status,
                    metadata=topic.metadata
                )
            
        except Exception as e:
            logger.error(f"Failed to get topic {session_id}: {e}")
            raise Exception(f"Failed to get topic: {str(e)}")
    
    async def update_topic(self, session_id: str, request: TopicUpdateRequest, user_id: str) -> Optional[TopicResponse]:
        """Update an existing topic"""
        try:
            if self._use_local_fallback:
                # Update in local storage
                if session_id not in self._local_storage:
                    logger.warning(f"Topic not found in local storage: {session_id}")
                    return None
                
                topic_data = self._local_storage[session_id]
                
                # Check user ownership
                if topic_data.get("user_id") != user_id:
                    logger.warning(f"User {user_id} attempted to update topic {session_id} owned by {topic_data.get('user_id')}")
                    return None
                
                # Update fields
                if request.topic is not None:
                    topic_data["topic"] = request.topic
                if request.description is not None:
                    topic_data["description"] = request.description
                if request.search_queries is not None:
                    topic_data["search_queries"] = request.search_queries
                if request.initial_urls is not None:
                    topic_data["initial_urls"] = request.initial_urls
                if request.analysis_type is not None:
                    topic_data["analysis_type"] = request.analysis_type.value
                if request.status is not None:
                    topic_data["status"] = request.status.value
                if request.metadata is not None:
                    topic_data["metadata"] = request.metadata
                
                # Update timestamp
                topic_data["updated_at"] = datetime.utcnow()
                
                # Save back to local storage
                self._local_storage[session_id] = topic_data
                
                # Convert to TopicResponse
                topic = self._dict_to_topic_config(topic_data)
                
                return TopicResponse(
                    session_id=topic.session_id,
                    topic=topic.topic,
                    description=topic.description,
                    search_queries=topic.search_queries,
                    initial_urls=topic.initial_urls,
                    analysis_type=topic.analysis_type,
                    user_id=topic.user_id,
                    created_at=topic.created_at,
                    updated_at=topic.updated_at,
                    status=topic.status,
                    metadata=topic.metadata
                )
            else:
                if not self.db:
                    raise Exception("Firestore not initialized")
            
            # Get existing topic
            topic_ref = self.db.collection('topics').document(session_id)
            topic_doc = topic_ref.get()
            
            if not topic_doc.exists:
                return None
            
            topic_data = topic_doc.to_dict()
            
            # Check user ownership
            if topic_data.get("user_id") != user_id:
                logger.warning(f"User {user_id} attempted to update topic {session_id} owned by {topic_data.get('user_id')}")
                return None
            
            # Update fields
            update_data = {"updated_at": datetime.utcnow()}
            
            if request.topic is not None:
                update_data["topic"] = request.topic
            if request.description is not None:
                update_data["description"] = request.description
            if request.search_queries is not None:
                update_data["search_queries"] = request.search_queries
            if request.initial_urls is not None:
                update_data["initial_urls"] = request.initial_urls
            if request.analysis_type is not None:
                update_data["analysis_type"] = request.analysis_type.value
            if request.status is not None:
                update_data["status"] = request.status.value
            if request.metadata is not None:
                update_data["metadata"] = request.metadata
            
            # Update in Firestore
            topic_ref.update(update_data)
            
            # Get updated topic
            updated_topic = await self.get_topic(session_id, user_id)
            
            logger.info(f"Topic updated successfully: {session_id}")
            return updated_topic
            
        except Exception as e:
            logger.error(f"Failed to update topic {session_id}: {e}")
            raise Exception(f"Failed to update topic: {str(e)}")
    
    async def delete_topic(self, session_id: str, user_id: str) -> bool:
        """Delete a topic"""
        try:
            if self._use_local_fallback:
                # Check if topic exists in local storage
                if session_id not in self._local_storage:
                    logger.warning(f"Topic not found in local storage: {session_id}")
                    return False
                
                topic_data = self._local_storage[session_id]
                
                # Check user ownership
                if topic_data.get("user_id") != user_id:
                    logger.warning(f"User {user_id} attempted to delete topic {session_id} owned by {topic_data.get('user_id')}")
                    return False
                
                # Delete from local storage
                del self._local_storage[session_id]
                
                logger.info(f"Topic deleted successfully from local storage: {session_id}")
                return True
            else:
                if not self.db:
                    raise Exception("Firestore not initialized")
                
                # Get topic to check ownership
                topic_ref = self.db.collection('topics').document(session_id)
                topic_doc = topic_ref.get()
                
                if not topic_doc.exists:
                    return False
                
                topic_data = topic_doc.to_dict()
                
                # Check user ownership
                if topic_data.get("user_id") != user_id:
                    logger.warning(f"User {user_id} attempted to delete topic {session_id} owned by {topic_data.get('user_id')}")
                    return False
                
                # Delete from Firestore
                topic_ref.delete()
                
                logger.info(f"Topic deleted successfully from Firestore: {session_id}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to delete topic {session_id}: {e}")
            raise Exception(f"Failed to delete topic: {str(e)}")
    
    async def list_topics(self, user_id: str, page: int = 1, page_size: int = 20, 
                         sort_by: str = "created_at", sort_order: str = "desc") -> TopicListResponse:
        """List topics for a user with pagination"""
        try:
            logger.info(f"Listing topics for user: {user_id} - TopicService instance ID: {id(self)}")
            logger.info(f"Using local fallback: {self._use_local_fallback}")
            logger.info(f"Local storage size: {len(self._local_storage)}")
            logger.info(f"Local storage keys: {list(self._local_storage.keys())}")
            
            if self._use_local_fallback:
                # Get from local storage
                user_topics = []
                for session_id, topic_data in self._local_storage.items():
                    if topic_data.get("user_id") == user_id:
                        topic = self._dict_to_topic_config(topic_data)
                        user_topics.append(TopicResponse(
                            session_id=topic.session_id,
                            topic=topic.topic,
                            description=topic.description,
                            search_queries=topic.search_queries,
                            initial_urls=topic.initial_urls,
                            analysis_type=topic.analysis_type,
                            user_id=topic.user_id,
                            created_at=topic.created_at,
                            updated_at=topic.updated_at,
                            status=topic.status,
                            metadata=topic.metadata
                        ))
                
                # Sort topics
                if sort_by == "created_at":
                    user_topics.sort(key=lambda x: x.created_at, reverse=(sort_order == "desc"))
                elif sort_by == "updated_at":
                    user_topics.sort(key=lambda x: x.updated_at, reverse=(sort_order == "desc"))
                elif sort_by == "topic":
                    user_topics.sort(key=lambda x: x.topic, reverse=(sort_order == "desc"))
                
                # Apply pagination
                total_count = len(user_topics)
                offset = (page - 1) * page_size
                paginated_topics = user_topics[offset:offset + page_size]
                
                return TopicListResponse(
                    topics=paginated_topics,
                    total=total_count,
                    page=page,
                    page_size=page_size,
                    has_next=(offset + page_size) < total_count,
                    has_previous=page > 1
                )
            else:
                if not self.db:
                    raise Exception("Firestore not initialized")
                
                # Calculate offset
                offset = (page - 1) * page_size
                
                # Build query
                query = self.db.collection('topics').where('user_id', '==', user_id)
                
                # Add sorting
                if sort_by == "created_at":
                    if sort_order == "desc":
                        query = query.order_by('created_at', direction=Query.DESCENDING)
                    else:
                        query = query.order_by('created_at', direction=Query.ASCENDING)
                elif sort_by == "updated_at":
                    if sort_order == "desc":
                        query = query.order_by('updated_at', direction=Query.DESCENDING)
                    else:
                        query = query.order_by('updated_at', direction=Query.ASCENDING)
                elif sort_by == "topic":
                    if sort_order == "desc":
                        query = query.order_by('topic', direction=Query.DESCENDING)
                    else:
                        query = query.order_by('topic', direction=Query.ASCENDING)
                
                # Get total count
                total_query = self.db.collection('topics').where('user_id', '==', user_id)
                total_count = len(list(total_query.stream()))
                
                # Apply pagination
                query = query.offset(offset).limit(page_size)
                
                # Execute query
                docs = query.stream()
                
                # Convert to TopicResponse objects
                topics = []
                for doc in docs:
                    topic_data = doc.to_dict()
                    topic = self._dict_to_topic_config(topic_data)
                    topics.append(TopicResponse(
                        session_id=topic.session_id,
                        topic=topic.topic,
                        description=topic.description,
                        search_queries=topic.search_queries,
                        initial_urls=topic.initial_urls,
                        analysis_type=topic.analysis_type,
                        user_id=topic.user_id,
                        created_at=topic.created_at,
                        updated_at=topic.updated_at,
                        status=topic.status,
                        metadata=topic.metadata
                    ))
                
                return TopicListResponse(
                    topics=topics,
                    total=total_count,
                    page=page,
                    page_size=page_size,
                    has_next=(offset + page_size) < total_count,
                    has_previous=page > 1
                )
            
        except Exception as e:
            logger.error(f"Failed to list topics: {e}")
            raise Exception(f"Failed to list topics: {str(e)}")
    
    async def search_topics(self, request: TopicSearchRequest) -> TopicListResponse:
        """Search topics with filters"""
        try:
            if self._use_local_fallback:
                # Search in local storage
                user_topics = []
                for _, topic_data in self._local_storage.items():
                    # Apply filters
                    if request.user_id and topic_data.get("user_id") != request.user_id:
                        continue
                    if request.analysis_type and topic_data.get("analysis_type") != request.analysis_type.value:
                        continue
                    if request.status and topic_data.get("status") != request.status.value:
                        continue
                    
                    # Apply text search
                    if request.query:
                        search_text = f"{topic_data.get('topic', '')} {topic_data.get('description', '')}".lower()
                        if request.query.lower() not in search_text:
                            continue
                    
                    # Convert to TopicResponse
                    topic = self._dict_to_topic_config(topic_data)
                    user_topics.append(TopicResponse(
                        session_id=topic.session_id,
                        topic=topic.topic,
                        description=topic.description,
                        search_queries=topic.search_queries,
                        initial_urls=topic.initial_urls,
                        analysis_type=topic.analysis_type,
                        user_id=topic.user_id,
                        created_at=topic.created_at,
                        updated_at=topic.updated_at,
                        status=topic.status,
                        metadata=topic.metadata
                    ))
                
                # Sort topics
                if request.sort_by == "created_at":
                    user_topics.sort(key=lambda x: x.created_at, reverse=(request.sort_order == "desc"))
                elif request.sort_by == "updated_at":
                    user_topics.sort(key=lambda x: x.updated_at, reverse=(request.sort_order == "desc"))
                elif request.sort_by == "topic":
                    user_topics.sort(key=lambda x: x.topic, reverse=(request.sort_order == "desc"))
                
                # Apply pagination
                total_count = len(user_topics)
                offset = (request.page - 1) * request.page_size
                paginated_topics = user_topics[offset:offset + request.page_size]
                
                return TopicListResponse(
                    topics=paginated_topics,
                    total=total_count,
                    page=request.page,
                    page_size=request.page_size,
                    has_next=(offset + request.page_size) < total_count,
                    has_previous=request.page > 1
                )
            else:
                if not self.db:
                    raise Exception("Firestore not initialized")
            
            # Build base query
            query = self.db.collection('topics')
            
            # Add filters
            if request.user_id:
                query = query.where('user_id', '==', request.user_id)
            if request.analysis_type:
                query = query.where('analysis_type', '==', request.analysis_type.value)
            if request.status:
                query = query.where('status', '==', request.status.value)
            
            # Add text search if provided
            if request.query:
                # For text search, we'll use a simple approach
                # In production, you might want to use Algolia or similar
                docs = query.stream()
                filtered_docs = []
                for doc in docs:
                    topic_data = doc.to_dict()
                    search_text = f"{topic_data.get('topic', '')} {topic_data.get('description', '')}".lower()
                    if request.query.lower() in search_text:
                        filtered_docs.append(doc)
                
                # Apply pagination to filtered results
                total_count = len(filtered_docs)
                offset = (request.page - 1) * request.page_size
                paginated_docs = filtered_docs[offset:offset + request.page_size]
                
                topics = []
                for doc in paginated_docs:
                    topic_data = doc.to_dict()
                    topic = self._dict_to_topic_config(topic_data)
                    topics.append(TopicResponse(
                        session_id=topic.session_id,
                        topic=topic.topic,
                        description=topic.description,
                        search_queries=topic.search_queries,
                        initial_urls=topic.initial_urls,
                        analysis_type=topic.analysis_type,
                        user_id=topic.user_id,
                        created_at=topic.created_at,
                        updated_at=topic.updated_at,
                        status=topic.status,
                        metadata=topic.metadata
                    ))
                
                has_next = (offset + request.page_size) < total_count
                has_previous = request.page > 1
                
                return TopicListResponse(
                    topics=topics,
                    total=total_count,
                    page=request.page,
                    page_size=request.page_size,
                    has_next=has_next,
                    has_previous=has_previous
                )
            else:
                # No text search, use regular query
                # Add sorting
                if request.sort_by == "created_at":
                    if request.sort_order == "desc":
                        query = query.order_by('created_at', direction=Query.DESCENDING)
                    else:
                        query = query.order_by('created_at', direction=Query.ASCENDING)
                elif request.sort_by == "updated_at":
                    if request.sort_order == "desc":
                        query = query.order_by('updated_at', direction=Query.DESCENDING)
                    else:
                        query = query.order_by('updated_at', direction=Query.ASCENDING)
                
                # Get total count
                total_query = self.db.collection('topics')
                if request.user_id:
                    total_query = total_query.where('user_id', '==', request.user_id)
                if request.analysis_type:
                    total_query = total_query.where('analysis_type', '==', request.analysis_type.value)
                if request.status:
                    total_query = total_query.where('status', '==', request.status.value)
                
                total_count = len(list(total_query.stream()))
                
                # Apply pagination
                offset = (request.page - 1) * request.page_size
                query = query.offset(offset).limit(request.page_size)
                
                # Execute query
                docs = query.stream()
                
                # Convert to TopicResponse objects
                topics = []
                for doc in docs:
                    topic_data = doc.to_dict()
                    topic = self._dict_to_topic_config(topic_data)
                    topics.append(TopicResponse(
                        session_id=topic.session_id,
                        topic=topic.topic,
                        description=topic.description,
                        search_queries=topic.search_queries,
                        initial_urls=topic.initial_urls,
                        analysis_type=topic.analysis_type,
                        user_id=topic.user_id,
                        created_at=topic.created_at,
                        updated_at=topic.updated_at,
                        status=topic.status,
                        metadata=topic.metadata
                    ))
                
                has_next = (offset + request.page_size) < total_count
                has_previous = request.page > 1
                
                return TopicListResponse(
                    topics=topics,
                    total=total_count,
                    page=request.page,
                    page_size=request.page_size,
                    has_next=has_next,
                    has_previous=has_previous
                )
                
        except Exception as e:
            logger.error(f"Failed to search topics: {e}")
            raise Exception(f"Failed to search topics: {str(e)}")
    
    async def get_topic_stats(self, user_id: str) -> Dict[str, Any]:
        """Get topic statistics for a user"""
        try:
            if self._use_local_fallback:
                # Get stats from local storage
                user_topics = []
                for _, topic_data in self._local_storage.items():
                    if topic_data.get("user_id") == user_id:
                        user_topics.append(topic_data)
                
                total_topics = len(user_topics)
                topics_by_status = {}
                topics_by_type = {}
                
                for topic_data in user_topics:
                    status = topic_data.get('status', 'unknown')
                    analysis_type = topic_data.get('analysis_type', 'unknown')
                    
                    topics_by_status[status] = topics_by_status.get(status, 0) + 1
                    topics_by_type[analysis_type] = topics_by_type.get(analysis_type, 0) + 1
                
                return {
                    "total_topics": total_topics,
                    "topics_by_status": topics_by_status,
                    "topics_by_type": topics_by_type
                }
            else:
                if not self.db:
                    raise Exception("Firestore not initialized")
            
            # Get all topics for user
            query = self.db.collection('topics').where('user_id', '==', user_id)
            docs = list(query.stream())
            
            total_topics = len(docs)
            topics_by_status = {}
            topics_by_type = {}
            
            for doc in docs:
                topic_data = doc.to_dict()
                status = topic_data.get('status', 'unknown')
                analysis_type = topic_data.get('analysis_type', 'unknown')
                
                topics_by_status[status] = topics_by_status.get(status, 0) + 1
                topics_by_type[analysis_type] = topics_by_type.get(analysis_type, 0) + 1
            
            return {
                "total_topics": total_topics,
                "topics_by_status": topics_by_status,
                "topics_by_type": topics_by_type
            }
            
        except Exception as e:
            logger.error(f"Failed to get topic stats: {e}")
            raise Exception(f"Failed to get topic stats: {str(e)}")
    
    async def update_topic_status(self, session_id: str, status: TopicStatus, user_id: str, 
                                progress_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update topic status with progress tracking"""
        try:
            logger.info(f"Updating topic status: {session_id} -> {status.value} for user: {user_id}")
            
            if self._use_local_fallback:
                if session_id not in self._local_storage:
                    logger.warning(f"Topic {session_id} not found in local storage")
                    return False
                    
                topic_data = self._local_storage[session_id]
                
                # Check user ownership
                if topic_data.get("user_id") != user_id:
                    logger.warning(f"User {user_id} attempted to update status for topic {session_id}")
                    return False
                
                # Update status and metadata
                topic_data["status"] = status.value
                topic_data["updated_at"] = datetime.utcnow()
                
                # Add progress data to metadata
                if progress_data:
                    if "progress" not in topic_data["metadata"]:
                        topic_data["metadata"]["progress"] = {}
                    topic_data["metadata"]["progress"].update(progress_data)
                
                # Add status history
                if "status_history" not in topic_data["metadata"]:
                    topic_data["metadata"]["status_history"] = []
                
                topic_data["metadata"]["status_history"].append({
                    "status": status.value,
                    "timestamp": datetime.utcnow().isoformat(),
                    "progress_data": progress_data
                })
                
                self._local_storage[session_id] = topic_data
                
                logger.info(f"Updated topic status: {session_id} -> {status.value}")
                return True
            else:
                # Firestore implementation
                if not self.db:
                    raise Exception("Firestore not initialized")
                
                topic_ref = self.db.collection('topics').document(session_id)
                topic_doc = topic_ref.get()
                
                if not topic_doc.exists:
                    return False
                
                topic_data = topic_doc.to_dict()
                
                # Check user ownership
                if topic_data.get("user_id") != user_id:
                    return False
                
                # Update data
                update_data = {
                    "status": status.value,
                    "updated_at": datetime.utcnow()
                }
                
                if progress_data:
                    update_data["metadata.progress"] = progress_data
                
                topic_ref.update(update_data)
                
                logger.info(f"Updated topic status in Firestore: {session_id} -> {status.value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update topic status {session_id}: {e}")
            return False

    async def get_topics_by_status(self, user_id: str, status: TopicStatus) -> List[TopicResponse]:
        """Get topics filtered by status"""
        try:
            logger.info(f"Getting topics by status: {status.value} for user: {user_id}")
            
            if self._use_local_fallback:
                user_topics = []
                for _, topic_data in self._local_storage.items():
                    if (topic_data.get("user_id") == user_id and 
                        topic_data.get("status") == status.value):
                        topic = self._dict_to_topic_config(topic_data)
                        user_topics.append(TopicResponse(
                            session_id=topic.session_id,
                            topic=topic.topic,
                            description=topic.description,
                            search_queries=topic.search_queries,
                            initial_urls=topic.initial_urls,
                            analysis_type=topic.analysis_type,
                            user_id=topic.user_id,
                            created_at=topic.created_at,
                            updated_at=topic.updated_at,
                            status=topic.status,
                            metadata=topic.metadata
                        ))
                return user_topics
            else:
                # Firestore implementation
                if not self.db:
                    raise Exception("Firestore not initialized")
                
                query = (self.db.collection('topics')
                        .where('user_id', '==', user_id)
                        .where('status', '==', status.value))
                
                docs = query.stream()
                topics = []
                
                for doc in docs:
                    topic_data = doc.to_dict()
                    topic = self._dict_to_topic_config(topic_data)
                    topics.append(TopicResponse(
                        session_id=topic.session_id,
                        topic=topic.topic,
                        description=topic.description,
                        search_queries=topic.search_queries,
                        initial_urls=topic.initial_urls,
                        analysis_type=topic.analysis_type,
                        user_id=topic.user_id,
                        created_at=topic.created_at,
                        updated_at=topic.updated_at,
                        status=topic.status,
                        metadata=topic.metadata
                    ))
                
                return topics
                
        except Exception as e:
            logger.exception(f"Failed to get topics by status: {e}")
            # Return empty list for any error to maintain API contract
            return []


# Module-level singleton instance (CRITICAL for persistence!)
# This ensures ONE instance per FastAPI process
_topic_service_instance = None

def get_topic_service_instance():
    """Get the singleton TopicService instance"""
    global _topic_service_instance
    if _topic_service_instance is None:
        _topic_service_instance = TopicService()
    return _topic_service_instance

# For backward compatibility
topic_service = get_topic_service_instance()
