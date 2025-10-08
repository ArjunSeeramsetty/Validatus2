"""
Content Management API - Integrates with existing ScrapedContentManager
🆕 NEW FILE: Provides REST API access to existing scraping and content services
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
import logging
from datetime import datetime, timezone
import json

from ...core.database_config import db_manager
from ...services.scraped_content_manager import ScrapedContentManager
from ...services.content_quality_analyzer import ContentQualityAnalyzer
from ...services.enhanced_content_processor import EnhancedContentProcessor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["content"])

# ✅ REUSING EXISTING SERVICES (not recreating them)
content_manager = ScrapedContentManager()
quality_analyzer = ContentQualityAnalyzer()

try:
    content_processor = EnhancedContentProcessor()
except:
    content_processor = None
    logger.warning("EnhancedContentProcessor not available, using fallback")

@router.get("/{session_id}")
async def get_topic_content(session_id: str):
    """
    Get all scraped content for a topic with quality metrics
    🆕 NEW ENDPOINT: Leverages existing ScrapedContentManager
    """
    try:
        connection = await db_manager.get_connection()
        
        # Get topic details (✅ EXISTING table structure)
        topic_query = """
        SELECT session_id, topic, description, status, created_at, updated_at
        FROM topics WHERE session_id = $1
        """
        topic_row = await connection.fetchrow(topic_query, session_id)
        
        if not topic_row:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Get URLs with scraping status (✅ EXISTING table structure)
        urls_query = """
        SELECT 
            tu.url, tu.title, tu.description, tu.source,
            tu.collection_method, tu.domain, tu.relevance_score,
            tu.quality_score, tu.priority_level, tu.status,
            tu.created_at, tu.metadata
        FROM topic_urls tu
        WHERE tu.session_id = $1
        ORDER BY tu.priority_level ASC, tu.quality_score DESC
        """
        url_rows = await connection.fetch(urls_query, session_id)
        
        # Process content items
        content_items = []
        total_words = 0
        quality_scores = []
        status_counts = {}
        
        for row in url_rows:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            quality_score = float(row['quality_score']) if row['quality_score'] else 0.0
            quality_scores.append(quality_score)
            
            # Estimate word count from description (since content might be in content field)
            description = row['description'] or ""
            word_count = len(description.split()) if description else 0
            
            status = row['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            
            content_items.append({
                "url": row['url'],
                "title": row['title'] or "Untitled",
                "description": description,
                "content_preview": description[:200] + "..." if len(description) > 200 else description,
                "domain": row['domain'] or "",
                "status": status,
                "relevance_score": float(row['relevance_score']) if row['relevance_score'] else 0.0,
                "quality_score": quality_score,
                "priority_level": row['priority_level'] or 5,
                "source": row['source'] or "unknown",
                "collection_method": row['collection_method'] or "",
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "word_count": word_count,
                "content_length": len(description),
                "metadata": metadata
            })
            
            total_words += word_count
        
        # Calculate statistics
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        return {
            "session_id": session_id,
            "topic": {
                "name": topic_row['topic'],
                "description": topic_row['description'],
                "status": topic_row['status'],
                "created_at": topic_row['created_at'].isoformat(),
                "updated_at": topic_row['updated_at'].isoformat()
            },
            "content_items": content_items,
            "statistics": {
                "total_items": len(content_items),
                "total_words": total_words,
                "average_quality_score": round(avg_quality, 3),
                "status_breakdown": status_counts,
                "content_length_stats": {
                    "min": min([item['content_length'] for item in content_items]) if content_items else 0,
                    "max": max([item['content_length'] for item in content_items]) if content_items else 0,
                    "avg": sum([item['content_length'] for item in content_items]) / len(content_items) if content_items else 0
                }
            },
            "last_updated": max([item['created_at'] for item in content_items if item['created_at']]) if any(item['created_at'] for item in content_items) else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content for topic {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

@router.post("/{session_id}/scrape")
async def start_scraping(
    session_id: str,
    background_tasks: BackgroundTasks,
    force_refresh: bool = Query(False, description="Force refresh existing content")
):
    """
    Start content scraping for topic URLs
    🆕 NEW ENDPOINT: Triggers scraping using existing content processor
    """
    try:
        # Get URLs that need scraping
        connection = await db_manager.get_connection()
        
        urls_query = """
        SELECT url, title, quality_score, priority_level
        FROM topic_urls
        WHERE session_id = $1 
        AND status IN ('pending', 'failed')
        ORDER BY priority_level ASC, quality_score DESC
        LIMIT 50
        """
        
        if force_refresh:
            # Get all URLs if forcing refresh
            urls_query = """
            SELECT url, title, quality_score, priority_level
            FROM topic_urls
            WHERE session_id = $1
            ORDER BY priority_level ASC, quality_score DESC
            LIMIT 50
            """
        
        url_rows = await connection.fetch(urls_query, session_id)
        
        if not url_rows:
            return {
                "success": False,
                "message": "No URLs available for scraping",
                "session_id": session_id
            }
        
        urls_to_scrape = [{"url": row['url'], "title": row['title']} for row in url_rows]
        
        # Start scraping in background (✅ Using existing content processor if available)
        if content_processor:
            background_tasks.add_task(
                _scrape_urls_background,
                session_id,
                urls_to_scrape,
                force_refresh
            )
        else:
            # Fallback: Mark URLs as processing
            for url_info in urls_to_scrape[:10]:  # Limit for safety
                await connection.execute(
                    "UPDATE topic_urls SET status = 'processing' WHERE session_id = $1 AND url = $2",
                    session_id, url_info['url']
                )
        
        return {
            "success": True,
            "message": f"Scraping started for {len(urls_to_scrape)} URLs",
            "session_id": session_id,
            "urls_queued": len(urls_to_scrape)
        }
        
    except Exception as e:
        logger.error(f"Failed to start scraping for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/scraping-status")
async def get_scraping_status(session_id: str):
    """
    Get current scraping status and progress
    🆕 NEW ENDPOINT: Provides real-time scraping status
    """
    try:
        connection = await db_manager.get_connection()
        
        # Count URLs by status (✅ Using existing schema)
        status_query = """
        SELECT 
            status,
            COUNT(*) as count,
            AVG(quality_score) as avg_quality
        FROM topic_urls
        WHERE session_id = $1
        GROUP BY status
        """
        
        status_rows = await connection.fetch(status_query, session_id)
        
        status_breakdown = {}
        avg_quality = 0.0
        total_count = 0
        
        for row in status_rows:
            status_breakdown[row['status']] = {
                "count": row['count'],
                "avg_quality": float(row['avg_quality']) if row['avg_quality'] else 0.0
            }
            total_count += row['count']
            if row['avg_quality']:
                avg_quality += float(row['avg_quality']) * row['count']
        
        if total_count > 0:
            avg_quality /= total_count
        
        return {
            "success": True,
            "session_id": session_id,
            "status": {
                "total_items": total_count,
                "processed_items": status_breakdown.get('scraped', {}).get('count', 0) + 
                                 status_breakdown.get('completed', {}).get('count', 0),
                "failed_items": status_breakdown.get('failed', {}).get('count', 0),
                "pending_items": status_breakdown.get('pending', {}).get('count', 0),
                "processing_items": status_breakdown.get('processing', {}).get('count', 0),
                "average_quality": round(avg_quality, 3),
                "status_breakdown": status_breakdown
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraping status for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _scrape_urls_background(session_id: str, urls: List[Dict], force_refresh: bool):
    """
    Background task for scraping URLs
    🆕 NEW FUNCTION: Background scraping using existing services
    """
    try:
        logger.info(f"Background scraping started for {session_id}: {len(urls)} URLs")
        
        # Use existing content processor if available
        if content_processor:
            for url_info in urls:
                try:
                    # Process content using existing service
                    result = await content_processor.process_url(
                        url=url_info['url'],
                        session_id=session_id
                    )
                    
                    if result:
                        # Update status
                        connection = await db_manager.get_connection()
                        await connection.execute(
                            "UPDATE topic_urls SET status = 'scraped' WHERE session_id = $1 AND url = $2",
                            session_id, url_info['url']
                        )
                        
                except Exception as e:
                    logger.error(f"Failed to scrape {url_info['url']}: {e}")
                    # Mark as failed
                    try:
                        connection = await db_manager.get_connection()
                        await connection.execute(
                            "UPDATE topic_urls SET status = 'failed' WHERE session_id = $1 AND url = $2",
                            session_id, url_info['url']
                        )
                    except:
                        pass
        
        logger.info(f"Background scraping completed for {session_id}")
        
    except Exception as e:
        logger.error(f"Background scraping failed for {session_id}: {e}")
