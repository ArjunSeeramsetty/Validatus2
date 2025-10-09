"""
Content Management API - Simple scraping without heavy dependencies
🆕 NEW FILE: Provides REST API access to content scraping
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timezone
import json
import asyncio
import hashlib
from urllib.parse import urlparse

from ...core.database_config import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["content"])

# Simple scraping implementation without heavy dependencies
async def simple_scrape_url(url: str, session) -> Optional[Dict[str, Any]]:
    """Simple URL scraper using aiohttp and basic text extraction"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        async with session.get(url, headers=headers, timeout=30) as response:
            if response.status != 200:
                return None
            
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return None
            
            html_content = await response.text()
            
            # Basic HTML parsing
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string.strip() if soup.title.string else ""
            elif soup.h1:
                title = soup.h1.get_text().strip()
            
            # Extract main content
            content = soup.get_text(separator=' ', strip=True)
            word_count = len(content.split())
            
            # Calculate simple quality score
            quality_score = 0.0
            if word_count > 500:
                quality_score += 0.3
            elif word_count > 200:
                quality_score += 0.2
            elif word_count > 50:
                quality_score += 0.1
            
            if title and len(title) > 10:
                quality_score += 0.2
            
            domain = urlparse(url).netloc.lower()
            if any(domain.endswith(tld) for tld in ['.edu', '.org', '.gov']):
                quality_score += 0.2
            
            if word_count > 100:
                quality_score += 0.2
            
            quality_score = min(quality_score, 1.0)
            
            return {
                "url": url,
                "title": title[:500] if title else "Untitled",
                "content": content[:50000],  # Limit content size
                "word_count": word_count,
                "quality_score": quality_score,
                "domain": domain,
                "scraped_at": datetime.now(timezone.utc),
                "status": "processed"
            }
            
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None


async def _scrape_urls_background(session_id: str, urls: List[Dict[str, Any]], force_refresh: bool):
    """Background task to scrape URLs"""
    try:
        import aiohttp
        
        logger.info(f"Starting background scraping for {session_id} with {len(urls)} URLs")
        
        # Get existing scraped URLs if not forcing refresh
        existing_urls = set()
        if not force_refresh:
            connection = await db_manager.get_connection()
            existing_query = "SELECT url FROM scraped_content WHERE session_id = $1 AND processing_status = 'processed'"
            existing_rows = await connection.fetch(existing_query, session_id)
            existing_urls = {row['url'] for row in existing_rows}
            logger.info(f"Found {len(existing_urls)} already scraped URLs")
        
        # Filter URLs to scrape
        urls_to_scrape = [u for u in urls if u['url'] not in existing_urls]
        logger.info(f"Will scrape {len(urls_to_scrape)} new URLs")
        
        if not urls_to_scrape:
            logger.info("No new URLs to scrape")
            return
        
        # Scrape ALL URLs (no limit)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            # Process all URLs to scrape, not just the first 20
            logger.info(f"Creating scraping tasks for {len(urls_to_scrape)} URLs")
            for url_data in urls_to_scrape:
                tasks.append(simple_scrape_url(url_data['url'], session))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Save results to database using a single connection for the entire batch
            successful = 0
            failed = 0
            
            # Get a single connection for all saves to avoid pool exhaustion
            connection = await db_manager.get_connection()
            
            for i, result in enumerate(results):
                url = urls_to_scrape[i]['url']
                
                try:
                    if isinstance(result, Exception) or result is None:
                        # Save failed scrape
                        await connection.execute(
                            """
                            INSERT INTO scraped_content (session_id, url, title, content, scraped_at, processing_status, metadata)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ON CONFLICT (session_id, url) DO UPDATE SET
                                processing_status = EXCLUDED.processing_status,
                                metadata = EXCLUDED.metadata,
                                scraped_at = EXCLUDED.scraped_at
                            """,
                            session_id,
                            url,
                            "Failed to scrape",
                            "",
                            datetime.now(timezone.utc),
                            "failed",
                            json.dumps({"error": str(result) if isinstance(result, Exception) else "Unknown error"})
                        )
                        failed += 1
                    else:
                        # Save successful scrape
                        await connection.execute(
                            """
                            INSERT INTO scraped_content (session_id, url, title, content, scraped_at, processing_status, metadata)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ON CONFLICT (session_id, url) DO UPDATE SET
                                title = EXCLUDED.title,
                                content = EXCLUDED.content,
                                scraped_at = EXCLUDED.scraped_at,
                                processing_status = EXCLUDED.processing_status,
                                metadata = EXCLUDED.metadata
                            """,
                            session_id,
                            result['url'],
                            result['title'],
                            result['content'],
                            result['scraped_at'],
                            result['status'],
                            json.dumps({
                                "quality_score": result['quality_score'],
                                "word_count": result['word_count'],
                                "domain": result['domain']
                            })
                        )
                        successful += 1
                        
                    # Small delay between saves to avoid overwhelming the connection
                    await asyncio.sleep(0.05)
                    
                except Exception as e:
                    logger.error(f"Error saving scrape result for {url}: {e}")
                    failed += 1
            
            logger.info(f"Scraping completed: {successful} successful, {failed} failed")
            
    except Exception as e:
        logger.error(f"Background scraping failed for {session_id}: {e}")


@router.get("/{session_id}")
async def get_topic_content(session_id: str):
    """
    Get all scraped content for a topic with quality metrics
    """
    try:
        connection = await db_manager.get_connection()
        
        # Get topic details
        topic_query = """
        SELECT session_id, topic, description, status, created_at, updated_at
        FROM topics WHERE session_id = $1
        """
        topic_row = await connection.fetchrow(topic_query, session_id)
        
        if not topic_row:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Get scraped content with enhanced details
        content_query = """
        SELECT 
            url, title, content, scraped_at, processing_status, metadata,
            LENGTH(TRIM(COALESCE(content, ''))) as content_length,
            ARRAY_LENGTH(STRING_TO_ARRAY(TRIM(COALESCE(content, ' ')), ' '), 1) as word_count
        FROM scraped_content 
        WHERE session_id = $1
        ORDER BY scraped_at DESC
        """
        content_rows = await connection.fetch(content_query, session_id)
        
        content_items = []
        total_words = 0
        quality_scores = []
        
        for row in content_rows:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            quality_score = metadata.get('quality_score', 0.0)
            quality_scores.append(quality_score)
            
            content_items.append({
                "url": row['url'],
                "title": row['title'] or "Untitled",
                "content_preview": (row['content'] or "")[:200] + "..." if row['content'] and len(row['content']) > 200 else (row['content'] or ""),
                "scraped_at": row['scraped_at'].isoformat() if row['scraped_at'] else None,
                "status": row['processing_status'] or "unknown",
                "content_length": row['content_length'] or 0,
                "word_count": row['word_count'] or 0,
                "quality_score": quality_score,
                "domain": urlparse(row['url']).netloc,
                "metadata": metadata
            })
            
            total_words += (row['word_count'] or 0)
        
        # Calculate statistics
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        status_counts = {}
        for item in content_items:
            status = item['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
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
            "last_updated": max([item['scraped_at'] for item in content_items if item['scraped_at']]) if any(item['scraped_at'] for item in content_items) else None
        }
        
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
    """
    try:
        # Get URLs that need scraping
        connection = await db_manager.get_connection()
        
        urls_query = """
        SELECT url, title, quality_score, priority_level
        FROM topic_urls
        WHERE session_id = $1 
        ORDER BY priority_level ASC, quality_score DESC
        """
        url_rows = await connection.fetch(urls_query, session_id)
        
        if not url_rows:
            raise HTTPException(status_code=404, detail="No URLs found for scraping")
        
        urls_to_scrape = []
        for row in url_rows:
            urls_to_scrape.append({
                "url": row['url'],
                "title": row['title'],
                "quality_score": float(row['quality_score']) if row['quality_score'] else 0.0,
                "priority_level": row['priority_level']
            })
        
        # Start scraping in background
        background_tasks.add_task(
            _scrape_urls_background,
            session_id, urls_to_scrape, force_refresh
        )
        
        logger.info(f"Queued {len(urls_to_scrape)} URLs for scraping for session {session_id}")
        
        return {
            "success": True,
            "message": "Content scraping started in background",
            "session_id": session_id,
            "urls_queued": len(urls_to_scrape)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start scraping for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scraping: {str(e)}")


@router.get("/{session_id}/scraping-status")
async def get_scraping_status(session_id: str):
    """
    Get scraping status and progress for a topic
    """
    try:
        connection = await db_manager.get_connection()
        
        # Get total URLs for the topic
        total_urls_query = "SELECT COUNT(*) FROM topic_urls WHERE session_id = $1"
        total_urls = await connection.fetchval(total_urls_query, session_id)
        
        # Get counts from scraped_content table
        status_counts_query = """
        SELECT processing_status, COUNT(*) 
        FROM scraped_content 
        WHERE session_id = $1 
        GROUP BY processing_status
        """
        status_rows = await connection.fetch(status_counts_query, session_id)
        
        status_breakdown = {row['processing_status']: row['count'] for row in status_rows}
        
        processed_items = status_breakdown.get('processed', 0)
        failed_items = status_breakdown.get('failed', 0)
        total_scraped = sum(status_breakdown.values())
        pending_items = max(0, total_urls - total_scraped)
        
        # Get average quality score
        avg_quality_query = """
        SELECT AVG(CAST(metadata->>'quality_score' AS FLOAT)) 
        FROM scraped_content 
        WHERE session_id = $1 AND processing_status = 'processed'
        AND metadata->>'quality_score' IS NOT NULL
        """
        average_quality = await connection.fetchval(avg_quality_query, session_id)
        
        # Get last updated timestamp
        last_updated_query = """
        SELECT MAX(scraped_at) FROM scraped_content WHERE session_id = $1
        """
        last_updated = await connection.fetchval(last_updated_query, session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "status": {
                "total_urls_in_topic": total_urls,
                "processed_items": processed_items,
                "failed_items": failed_items,
                "pending_items": pending_items,
                "processing_items": status_breakdown.get('processing', 0),
                "average_quality": round(average_quality or 0.0, 3),
                "last_updated": last_updated.isoformat() if last_updated else None,
                "status_breakdown": status_breakdown
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraping status for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scraping status: {str(e)}")