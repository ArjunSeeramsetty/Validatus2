"""
Topics API v3 - Fixed with proper database integration
"""
import uuid
import hashlib
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...core.database_config import db_manager

router = APIRouter()

class TopicCreateRequest(BaseModel):
    topic: str
    description: Optional[str] = ""
    search_queries: List[str] = []
    initial_urls: List[str] = []
    analysis_type: str = "comprehensive"
    user_id: str = "default_user"

class TopicResponse(BaseModel):
    session_id: str
    topic: str
    description: str
    user_id: str
    status: str
    analysis_type: str
    created_at: datetime
    url_count: int = 0

@router.get("", response_model=List[TopicResponse])
async def list_topics(
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all topics with URL counts"""
    try:
        connection = await db_manager.get_connection()
        
        # Build query based on user_id filter
        if user_id:
            query = """
            SELECT t.session_id, t.topic, t.description, t.user_id, t.status, 
                   t.analysis_type, t.created_at, COUNT(tu.id) as url_count
            FROM topics t
            LEFT JOIN topic_urls tu ON t.session_id = tu.session_id
            WHERE t.user_id = $1
            GROUP BY t.session_id, t.topic, t.description, t.user_id, t.status, t.analysis_type, t.created_at
            ORDER BY t.created_at DESC
            LIMIT $2 OFFSET $3
            """
            params = [user_id, limit, offset]
        else:
            query = """
            SELECT t.session_id, t.topic, t.description, t.user_id, t.status, 
                   t.analysis_type, t.created_at, COUNT(tu.id) as url_count
            FROM topics t
            LEFT JOIN topic_urls tu ON t.session_id = tu.session_id
            GROUP BY t.session_id, t.topic, t.description, t.user_id, t.status, t.analysis_type, t.created_at
            ORDER BY t.created_at DESC
            LIMIT $1 OFFSET $2
            """
            params = [limit, offset]
        
        rows = await connection.fetch(query, *params)
        
        topics = []
        for row in rows:
            topics.append(TopicResponse(
                session_id=row['session_id'],
                topic=row['topic'],
                description=row['description'] or "",
                user_id=row['user_id'],
                status=row['status'],
                analysis_type=row['analysis_type'],
                created_at=row['created_at'],
                url_count=row['url_count']
            ))
        
        return topics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/create", response_model=TopicResponse)
async def create_topic(request: TopicCreateRequest):
    """Create a new topic"""
    try:
        connection = await db_manager.get_connection()
        
        # Generate session ID
        session_id = f"topic-{uuid.uuid4().hex[:12]}"
        
        async with connection.transaction():
            # Insert topic
            topic_query = """
            INSERT INTO topics (session_id, topic, description, user_id, analysis_type, status, search_queries, initial_urls)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING session_id, topic, description, user_id, analysis_type, status, created_at
            """
            
            topic_row = await connection.fetchrow(
                topic_query,
                session_id,
                request.topic,
                request.description,
                request.user_id,
                request.analysis_type,
                "CREATED",
                request.search_queries,
                request.initial_urls
            )
            
            # Insert initial URLs if provided
            url_count = 0
            if request.initial_urls:
                for url in request.initial_urls:
                    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
                    
                    url_query = """
                    INSERT INTO topic_urls (session_id, url, url_hash, source, status)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (session_id, url_hash) DO NOTHING
                    """
                    
                    await connection.execute(url_query, session_id, url, url_hash, "initial", "pending")
                
                url_count = len(request.initial_urls)
            
            # Create workflow status
            workflow_query = """
            INSERT INTO workflow_status (session_id, stage, status)
            VALUES ($1, $2, $3)
            """
            
            await connection.execute(workflow_query, session_id, "CREATED", "completed")
        
        return TopicResponse(
            session_id=topic_row['session_id'],
            topic=topic_row['topic'],
            description=topic_row['description'],
            user_id=topic_row['user_id'],
            status=topic_row['status'],
            analysis_type=topic_row['analysis_type'],
            created_at=topic_row['created_at'],
            url_count=url_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic creation failed: {str(e)}")

@router.get("/{session_id}", response_model=TopicResponse)
async def get_topic(session_id: str):
    """Get a specific topic by session_id"""
    try:
        connection = await db_manager.get_connection()
        
        query = """
        SELECT t.session_id, t.topic, t.description, t.user_id, t.status, 
               t.analysis_type, t.created_at, COUNT(tu.id) as url_count
        FROM topics t
        LEFT JOIN topic_urls tu ON t.session_id = tu.session_id
        WHERE t.session_id = $1
        GROUP BY t.session_id, t.topic, t.description, t.user_id, t.status, t.analysis_type, t.created_at
        """
        
        row = await connection.fetchrow(query, session_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return TopicResponse(
            session_id=row['session_id'],
            topic=row['topic'],
            description=row['description'] or "",
            user_id=row['user_id'],
            status=row['status'],
            analysis_type=row['analysis_type'],
            created_at=row['created_at'],
            url_count=row['url_count']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{session_id}")
async def delete_topic(session_id: str):
    """Delete a topic and all associated data"""
    try:
        connection = await db_manager.get_connection()
        
        async with connection.transaction():
            # Check if topic exists
            check_query = "SELECT session_id FROM topics WHERE session_id = $1"
            exists = await connection.fetchval(check_query, session_id)
            
            if not exists:
                raise HTTPException(status_code=404, detail="Topic not found")
            
            # Delete topic (cascades to related tables)
            delete_query = "DELETE FROM topics WHERE session_id = $1"
            await connection.execute(delete_query, session_id)
        
        return {"message": "Topic deleted successfully", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")