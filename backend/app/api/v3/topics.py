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
    request: TopicCreateRequest
):
    """Create a new topic"""
    try:
        logger.info(f"Creating topic: {request.topic} for user: {request.user_id}")
        
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


@router.get("/debug/test-db")
async def test_database_connection():
    """Test database connection"""
    try:
        import asyncpg
        import os
        
        # Get password from environment
        password = os.getenv('CLOUD_SQL_PASSWORD', 'Validatus2024!')
        
        # Test connection string - use validatus_app user
        connection_string = f"postgresql://validatus_app:{password}@/validatusdb?host=/cloudsql/validatus-platform:us-central1:validatus-sql"
        
        conn = await asyncpg.connect(connection_string)
        
        # Test basic query
        version = await conn.fetchval("SELECT version()")
        
        # Check if topics table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'topics'
            )
        """)
        
        await conn.close()
        
        return {
            "status": "success",
            "postgresql_version": version,
            "topics_table_exists": table_exists,
            "connection_string_used": f"postgresql://postgres:***@/validatusdb?host=/cloudsql/validatus-platform:us-central1:validatus-sql"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.post("/debug/create-schema")
async def create_database_schema():
    """Create database schema"""
    try:
        import asyncpg
        import os
        
        # Get password from environment
        password = os.getenv('CLOUD_SQL_PASSWORD', 'Validatus2024!')
        
        # Connection string - try with validatus_app user first
        connection_string = f"postgresql://validatus_app:{password}@/validatusdb?host=/cloudsql/validatus-platform:us-central1:validatus-sql"
        
        conn = await asyncpg.connect(connection_string)
        
        # Read and execute schema
        schema_sql = """
        -- Create topics table
        CREATE TABLE IF NOT EXISTS topics (
            session_id VARCHAR(50) PRIMARY KEY,
            topic VARCHAR(255) NOT NULL,
            description TEXT,
            user_id VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'CREATED',
            analysis_type VARCHAR(50) NOT NULL DEFAULT 'COMPREHENSIVE',
            search_queries TEXT[] DEFAULT '{}',
            initial_urls TEXT[] DEFAULT '{}',
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            CONSTRAINT chk_status CHECK (status IN ('CREATED', 'URL_COLLECTION', 'URL_SCRAPING', 'CONTENT_PROCESSING', 'VECTOR_CREATION', 'ANALYSIS', 'COMPLETED', 'FAILED')),
            CONSTRAINT chk_analysis_type CHECK (analysis_type IN ('STANDARD', 'COMPREHENSIVE'))
        );
        
        -- Create workflow_status table
        CREATE TABLE IF NOT EXISTS workflow_status (
            session_id VARCHAR(50) PRIMARY KEY REFERENCES topics(session_id) ON DELETE CASCADE,
            current_stage VARCHAR(50) NOT NULL,
            stages_completed TEXT[] DEFAULT '{}',
            stage_progress JSONB DEFAULT '{}'::jsonb,
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            
            CONSTRAINT chk_current_stage CHECK (current_stage IN (
                'CREATED', 'URL_COLLECTION', 'URL_SCRAPING', 'CONTENT_PROCESSING', 
                'VECTOR_CREATION', 'ANALYSIS', 'COMPLETED', 'FAILED'
            ))
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics(user_id);
        CREATE INDEX IF NOT EXISTS idx_topics_created_at ON topics(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_topics_status ON topics(status);
        CREATE INDEX IF NOT EXISTS idx_workflow_status_stage ON workflow_status(current_stage);
        CREATE INDEX IF NOT EXISTS idx_workflow_status_updated ON workflow_status(updated_at DESC);
        
        -- Create trigger function for updated_at
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        -- Create triggers
        DROP TRIGGER IF EXISTS update_topics_updated_at ON topics;
        CREATE TRIGGER update_topics_updated_at BEFORE UPDATE ON topics
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_workflow_status_updated_at ON workflow_status;
        CREATE TRIGGER update_workflow_status_updated_at BEFORE UPDATE ON workflow_status
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        await conn.execute(schema_sql)
        
        # Verify tables were created
        topics_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'topics'
            )
        """)
        
        workflow_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'workflow_status'
            )
        """)
        
        await conn.close()
        
        return {
            "status": "success",
            "message": "Database schema created successfully",
            "topics_table_exists": topics_exists,
            "workflow_status_table_exists": workflow_exists
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

@router.get("", response_model=TopicListResponse)
@router.get("/", response_model=TopicListResponse)
async def list_topics(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    user_id: str = Query(..., description="User ID")
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
