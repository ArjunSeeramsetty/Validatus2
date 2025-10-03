"""
Google Cloud SQL Manager
Handles all PostgreSQL database operations for structured data
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
import asyncpg
from asyncpg import Pool, Connection
from contextlib import asynccontextmanager

from ..core.gcp_persistence_config import get_gcp_persistence_settings
from ..models.topic_models import (
    TopicCreateRequest, TopicResponse, TopicUpdateRequest, 
    TopicStatus, AnalysisType, TopicListResponse
)

logger = logging.getLogger(__name__)

class GCPSQLManager:
    """Manages Google Cloud SQL PostgreSQL operations"""
    
    def __init__(self):
        self.settings = get_gcp_persistence_settings()
        self.pool: Optional[Pool] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize connection pool"""
        if self._initialized:
            return
        
        try:
            connection_url = self.settings.get_cloud_sql_url()
            
            self.pool = await asyncpg.create_pool(
                connection_url,
                min_size=5,
                max_size=self.settings.connection_pool_size,
                command_timeout=self.settings.query_timeout_seconds,
                server_settings={
                    'application_name': 'validatus-app',
                    'timezone': 'UTC'
                }
            )
            
            self._initialized = True
            logger.info("Cloud SQL connection pool initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Cloud SQL pool: {e}")
            raise
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self._initialized = False
            logger.info("Cloud SQL connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self) -> Connection:
        """Get database connection from pool"""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def create_topic(self, request: TopicCreateRequest) -> TopicResponse:
        """Create a new topic in Cloud SQL"""
        try:
            async with self.get_connection() as conn:
                # Generate session ID
                session_id = self._generate_session_id()
                
                # Insert topic
                query = """
                    INSERT INTO topics (
                        session_id, topic, description, user_id, status, 
                        analysis_type, search_queries, initial_urls, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING session_id, created_at, updated_at
                """
                
                result = await conn.fetchrow(
                    query,
                    session_id,
                    request.topic,
                    request.description,
                    request.user_id,
                    TopicStatus.CREATED.value,
                    request.analysis_type.value,
                    request.search_queries,
                    request.initial_urls,
                    request.metadata
                )
                
                # Initialize workflow status
                await self._create_workflow_status(conn, session_id)
                
                # Store initial URLs if provided
                if request.initial_urls:
                    await self._store_initial_urls(conn, session_id, request.initial_urls)
                
                logger.info(f"Created topic {session_id} in Cloud SQL")
                
                return TopicResponse(
                    session_id=result['session_id'],
                    topic=request.topic,
                    description=request.description,
                    search_queries=request.search_queries,
                    initial_urls=request.initial_urls,
                    analysis_type=request.analysis_type,
                    user_id=request.user_id,
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    status=TopicStatus.CREATED,
                    metadata=request.metadata
                )
                
        except Exception as e:
            logger.error(f"Failed to create topic in Cloud SQL: {e}")
            raise
    
    async def get_topic(self, session_id: str, user_id: str) -> Optional[TopicResponse]:
        """Retrieve topic by session ID"""
        try:
            async with self.get_connection() as conn:
                query = """
                    SELECT session_id, topic, description, user_id, status, 
                           analysis_type, search_queries, initial_urls, metadata,
                           created_at, updated_at
                    FROM topics 
                    WHERE session_id = $1 AND user_id = $2
                """
                
                result = await conn.fetchrow(query, session_id, user_id)
                
                if not result:
                    return None
                
                return TopicResponse(
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
                
        except Exception as e:
            logger.error(f"Failed to get topic {session_id}: {e}")
            return None
    
    async def list_topics(self, user_id: str, page: int = 1, page_size: int = 20,
                         sort_by: str = "created_at", sort_order: str = "desc") -> TopicListResponse:
        """List topics for a user with pagination"""
        try:
            async with self.get_connection() as conn:
                # Build sort clause
                sort_clause = f"ORDER BY {sort_by} {'DESC' if sort_order == 'desc' else 'ASC'}"
                offset = (page - 1) * page_size
                
                # Get total count
                count_query = "SELECT COUNT(*) FROM topics WHERE user_id = $1"
                total_count = await conn.fetchval(count_query, user_id)
                
                # Get paginated results
                query = f"""
                    SELECT session_id, topic, description, user_id, status, 
                           analysis_type, search_queries, initial_urls, metadata,
                           created_at, updated_at
                    FROM topics 
                    WHERE user_id = $1
                    {sort_clause}
                    LIMIT $2 OFFSET $3
                """
                
                results = await conn.fetch(query, user_id, page_size, offset)
                
                topics = []
                for result in results:
                    topics.append(TopicResponse(
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
            logger.error(f"Failed to list topics for user {user_id}: {e}")
            return TopicListResponse(topics=[], total=0, page=page, page_size=page_size, has_next=False, has_previous=False)
    
    async def update_topic_status(self, session_id: str, status: TopicStatus, 
                                user_id: str, metadata_update: Optional[Dict] = None) -> bool:
        """Update topic status"""
        try:
            async with self.get_connection() as conn:
                async with conn.transaction():
                    # Update topic status
                    if metadata_update:
                        query = """
                            UPDATE topics 
                            SET status = $1, metadata = metadata || $2::jsonb
                            WHERE session_id = $3 AND user_id = $4
                        """
                        result = await conn.execute(query, status.value, metadata_update, session_id, user_id)
                    else:
                        query = """
                            UPDATE topics 
                            SET status = $1
                            WHERE session_id = $2 AND user_id = $3
                        """
                        result = await conn.execute(query, status.value, session_id, user_id)
                    
                    # Update workflow status if needed
                    if status in [TopicStatus.IN_PROGRESS, TopicStatus.COMPLETED, TopicStatus.FAILED]:
                        await self._update_workflow_status(conn, session_id, status.value, metadata_update)
                    
                    success = result.split()[-1] == '1'  # Check if one row was updated
                    
                    if success:
                        logger.info(f"Updated topic {session_id} status to {status.value}")
                    
                    return success
                    
        except Exception as e:
            logger.error(f"Failed to update topic status {session_id}: {e}")
            return False
    
    async def store_urls(self, session_id: str, urls: List[str], source: str = "search") -> int:
        """Store URLs for a topic session"""
        try:
            async with self.get_connection() as conn:
                stored_count = 0
                
                for url in urls:
                    # Use INSERT ... ON CONFLICT to handle duplicates
                    query = """
                        INSERT INTO topic_urls (session_id, url, source)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (session_id, url) DO NOTHING
                    """
                    
                    result = await conn.execute(query, session_id, url, source)
                    if result.split()[-1] == '1':  # Check if row was inserted
                        stored_count += 1
                
                logger.info(f"Stored {stored_count} new URLs for session {session_id}")
                return stored_count
                
        except Exception as e:
            logger.error(f"Failed to store URLs for session {session_id}: {e}")
            return 0
    
    async def update_url_content(self, session_id: str, url: str, 
                               content_path: str, metadata: Dict[str, Any]) -> bool:
        """Update URL with scraped content information"""
        try:
            async with self.get_connection() as conn:
                query = """
                    UPDATE topic_urls 
                    SET status = 'scraped',
                        content_storage_path = $1,
                        content_hash = $2,
                        title = $3,
                        word_count = $4,
                        quality_score = $5,
                        processing_metadata = $6,
                        scraped_at = NOW()
                    WHERE session_id = $7 AND url = $8
                """
                
                result = await conn.execute(
                    query,
                    content_path,
                    metadata.get('content_hash'),
                    metadata.get('title'),
                    metadata.get('word_count'),
                    metadata.get('quality_score'),
                    metadata,
                    session_id,
                    url
                )
                
                success = result.split()[-1] == '1'
                if success:
                    logger.debug(f"Updated URL content info for {url}")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to update URL content for {url}: {e}")
            return False
    
    async def get_urls_for_scraping(self, session_id: str, status: str = "pending", 
                                   limit: int = 50) -> List[Dict[str, Any]]:
        """Get URLs ready for scraping"""
        try:
            async with self.get_connection() as conn:
                query = """
                    SELECT id, url, source, created_at
                    FROM topic_urls 
                    WHERE session_id = $1 AND status = $2
                    ORDER BY created_at ASC
                    LIMIT $3
                """
                
                results = await conn.fetch(query, session_id, status, limit)
                
                return [dict(result) for result in results]
                
        except Exception as e:
            logger.error(f"Failed to get URLs for scraping {session_id}: {e}")
            return []
    
    # Helper methods
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import time
        import random
        import string
        
        timestamp = int(time.time() * 1000)
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"topic_{timestamp}_{random_suffix}"
    
    async def _create_workflow_status(self, conn: Connection, session_id: str):
        """Create initial workflow status"""
        query = """
            INSERT INTO workflow_status (session_id, current_stage, stages_completed)
            VALUES ($1, 'CREATED', ARRAY['CREATED'])
        """
        await conn.execute(query, session_id)
    
    async def _update_workflow_status(self, conn: Connection, session_id: str, 
                                    stage: str, progress_data: Optional[Dict] = None):
        """Update workflow status"""
        query = """
            UPDATE workflow_status 
            SET current_stage = $1,
                stages_completed = array_append(stages_completed, $1),
                stage_progress = COALESCE(stage_progress, '{}'::jsonb) || $2::jsonb
            WHERE session_id = $3
        """
        await conn.execute(query, stage, progress_data or {}, session_id)
    
    async def _store_initial_urls(self, conn: Connection, session_id: str, urls: List[str]):
        """Store initial URLs provided during topic creation"""
        for url in urls:
            query = """
                INSERT INTO topic_urls (session_id, url, source)
                VALUES ($1, $2, 'initial')
                ON CONFLICT (session_id, url) DO NOTHING
            """
            await conn.execute(query, session_id, url)
