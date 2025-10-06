"""
Enhanced URL Collection Service with Google Custom Search and Database Persistence
Integrates with existing repository architecture and database schema
"""
import asyncio
import json
import hashlib
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from .google_custom_search_service import get_google_search_service, SearchResult
from .gcp_sql_manager import GCPSQLManager
from ..core.gcp_persistence_config import get_gcp_persistence_settings

import logging
logger = logging.getLogger(__name__)

@dataclass
class URLCollectionRequest:
    """Request for URL collection"""
    session_id: str
    search_queries: List[str]
    initial_urls: Optional[List[str]] = None
    max_urls_per_query: Optional[int] = None
    force_refresh: bool = False
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class URLCollectionResult:
    """Result of URL collection operation"""
    session_id: str
    campaign_id: int
    urls_discovered: int
    urls_stored: int
    queries_processed: int
    collection_status: str
    error_message: Optional[str] = None
    collection_metadata: Optional[Dict[str, Any]] = None

class EnhancedURLCollectionService:
    """
    Enhanced URL Collection Service that integrates:
    1. Google Custom Search API
    2. Database persistence (Cloud SQL)
    3. Existing repository patterns
    """
    
    def __init__(self):
        self.settings = get_gcp_persistence_settings()
        self.db_manager = GCPSQLManager()
        self.search_service = None
        
    async def initialize(self):
        """Initialize all services"""
        await self.db_manager.initialize()
        self.search_service = await get_google_search_service()
        logger.info("Enhanced URL Collection Service initialized")
    
    async def collect_urls_for_topic(self, request: URLCollectionRequest) -> URLCollectionResult:
        """
        Main URL collection method - integrates with existing repository flow
        """
        if not self.search_service:
            await self.initialize()
        
        logger.info(f"Starting URL collection for session {request.session_id}")
        
        try:
            # Check if collection already exists and is fresh
            if not request.force_refresh:
                existing_campaign = await self._get_existing_campaign(request.session_id)
                if existing_campaign:
                    logger.info(f"Using existing URL collection for session {request.session_id}")
                    return existing_campaign
            
            # Create new collection campaign
            campaign_id = await self._create_collection_campaign(request)
            
            # Execute URL collection using Google Custom Search
            search_results = await self.search_service.search_urls_for_topic(
                search_queries=request.search_queries,
                session_id=request.session_id,
                max_results_per_query=request.max_urls_per_query
            )
            
            # Merge with initial URLs if provided
            all_urls = self._merge_with_initial_urls(search_results["urls"], request.initial_urls)
            
            # Store URLs in database
            stored_count = await self._store_collected_urls(
                session_id=request.session_id,
                campaign_id=campaign_id,
                urls=all_urls,
                search_metadata=search_results
            )
            
            # Update campaign status
            await self._update_campaign_completion(
                campaign_id=campaign_id,
                urls_discovered=len(all_urls),
                urls_stored=stored_count,
                metadata=search_results
            )
            
            result = URLCollectionResult(
                session_id=request.session_id,
                campaign_id=campaign_id,
                urls_discovered=len(all_urls),
                urls_stored=stored_count,
                queries_processed=len(request.search_queries),
                collection_status="completed",
                collection_metadata=search_results
            )
            
            logger.info(f"URL collection completed for session {request.session_id}: {stored_count} URLs stored")
            return result
            
        except Exception as e:
            logger.error(f"URL collection failed for session {request.session_id}: {e}")
            
            # Try to update campaign with error status
            if 'campaign_id' in locals():
                await self._update_campaign_failure(campaign_id, str(e))
            
            return URLCollectionResult(
                session_id=request.session_id,
                campaign_id=0,
                urls_discovered=0,
                urls_stored=0,
                queries_processed=0,
                collection_status="failed",
                error_message=str(e)
            )
    
    async def _get_existing_campaign(self, session_id: str) -> Optional[URLCollectionResult]:
        """Check for existing fresh URL collection"""
        async with self.db_manager.pool.acquire() as connection:
            # Check for recent campaign (within last 24 hours)
            query = """
            SELECT id, urls_discovered, urls_processed, created_at, status, configuration
            FROM url_collection_campaigns 
            WHERE session_id = $1 AND status = 'completed' 
            AND created_at > NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC LIMIT 1
            """
            
            row = await connection.fetchrow(query, session_id)
            if row:
                return URLCollectionResult(
                    session_id=session_id,
                    campaign_id=row['id'],
                    urls_discovered=row['urls_discovered'] or 0,
                    urls_stored=row['urls_processed'] or 0,
                    queries_processed=1,  # Approximation
                    collection_status="completed",
                    collection_metadata=json.loads(row['configuration']) if row['configuration'] else {}
                )
        
        return None
    
    async def _create_collection_campaign(self, request: URLCollectionRequest) -> int:
        """Create a new collection campaign record"""
        async with self.db_manager.pool.acquire() as connection:
            async with connection.transaction():
                insert_sql = """
                INSERT INTO url_collection_campaigns (
                    session_id, campaign_name, collection_strategy, 
                    search_queries, max_urls, status, configuration
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """
                
                campaign_name = f"google_custom_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                configuration = {
                    "service": "google_custom_search",
                    "max_urls_per_query": request.max_urls_per_query or self.settings.max_urls_per_query,
                    "initial_urls_count": len(request.initial_urls) if request.initial_urls else 0,
                    "force_refresh": request.force_refresh,
                    "request_metadata": request.metadata or {}
                }
                
                row = await connection.fetchrow(
                    insert_sql,
                    request.session_id,
                    campaign_name,
                    "google_custom_search",
                    request.search_queries,
                    request.max_urls_per_query or self.settings.max_urls_per_query,
                    "running",
                    json.dumps(configuration)
                )
                
                return row['id']
    
    def _merge_with_initial_urls(
        self, 
        search_results: List[SearchResult], 
        initial_urls: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Merge search results with initial URLs"""
        merged_urls = []
        seen_urls = set()
        
        # Add search results first
        for result in search_results:
            url_hash = self._generate_url_hash(result.url)
            if url_hash not in seen_urls:
                merged_urls.append({
                    "url": result.url,
                    "title": result.title,
                    "description": result.snippet,
                    "source": "google_custom_search",
                    "collection_method": "search_api",
                    "domain": result.domain,
                    "relevance_score": result.relevance_score,
                    "quality_score": 0.6,  # Default for search results
                    "priority_level": 5,
                    "search_query": result.search_query,
                    "metadata": result.metadata
                })
                seen_urls.add(url_hash)
        
        # Add initial URLs if not already present
        if initial_urls:
            for url in initial_urls:
                url_hash = self._generate_url_hash(url)
                if url_hash not in seen_urls:
                    parsed_url = urllib.parse.urlparse(url)
                    merged_urls.append({
                        "url": url,
                        "title": "",
                        "description": "",
                        "source": "manual",
                        "collection_method": "manual",
                        "domain": parsed_url.netloc,
                        "relevance_score": 0.8,  # Higher for manual URLs
                        "quality_score": 0.7,
                        "priority_level": 3,  # Higher priority for manual
                        "search_query": "",
                        "metadata": {"source": "initial_urls"}
                    })
                    seen_urls.add(url_hash)
        
        return merged_urls
    
    async def _store_collected_urls(
        self, 
        session_id: str, 
        campaign_id: int, 
        urls: List[Dict[str, Any]], 
        search_metadata: Dict[str, Any]
    ) -> int:
        """Store collected URLs in the database"""
        stored_count = 0
        
        async with self.db_manager.pool.acquire() as connection:
            async with connection.transaction():
                for url_data in urls:
                    try:
                        url_hash = self._generate_url_hash(url_data["url"])
                        
                        insert_sql = """
                        INSERT INTO topic_urls (
                            session_id, url, url_hash, source, collection_method,
                            title, description, domain, relevance_score, quality_score,
                            priority_level, status, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        ON CONFLICT (session_id, url_hash) DO NOTHING
                        """
                        
                        await connection.execute(
                            insert_sql,
                            session_id,
                            url_data["url"],
                            url_hash,
                            url_data["source"],
                            url_data["collection_method"],
                            url_data["title"],
                            url_data["description"],
                            url_data["domain"],
                            url_data["relevance_score"],
                            url_data["quality_score"],
                            url_data["priority_level"],
                            "pending",
                            json.dumps(url_data["metadata"])
                        )
                        
                        stored_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error storing URL {url_data['url']}: {e}")
                        continue
        
        logger.info(f"Stored {stored_count} URLs for session {session_id}")
        return stored_count
    
    async def _update_campaign_completion(
        self, 
        campaign_id: int, 
        urls_discovered: int, 
        urls_stored: int, 
        metadata: Dict[str, Any]
    ):
        """Update campaign with completion status"""
        async with self.db_manager.pool.acquire() as connection:
            update_sql = """
            UPDATE url_collection_campaigns 
            SET status = $1, progress_percentage = $2, urls_discovered = $3, 
                urls_processed = $4, completed_at = $5, configuration = configuration || $6
            WHERE id = $7
            """
            
            completion_metadata = {
                "completion_time": datetime.utcnow().isoformat(),
                "search_stats": metadata.get("query_stats", {}),
                "total_api_calls": metadata.get("total_api_calls", 0)
            }
            
            await connection.execute(
                update_sql,
                "completed",
                100.0,
                urls_discovered,
                urls_stored,
                datetime.utcnow(),
                json.dumps(completion_metadata),
                campaign_id
            )
    
    async def _update_campaign_failure(self, campaign_id: int, error_message: str):
        """Update campaign with failure status"""
        async with self.db_manager.pool.acquire() as connection:
            update_sql = """
            UPDATE url_collection_campaigns 
            SET status = $1, completed_at = $2, configuration = configuration || $3
            WHERE id = $4
            """
            
            error_metadata = {
                "error": error_message,
                "failed_at": datetime.utcnow().isoformat()
            }
            
            await connection.execute(
                update_sql,
                "failed",
                datetime.utcnow(),
                json.dumps(error_metadata),
                campaign_id
            )
    
    def _generate_url_hash(self, url: str) -> str:
        """Generate hash for URL deduplication"""
        parsed = urllib.parse.urlparse(url.lower())
        normalized = f"{parsed.netloc}{parsed.path}"
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    async def get_collected_urls(self, session_id: str) -> Dict[str, Any]:
        """Get collected URLs for a session"""
        async with self.db_manager.pool.acquire() as connection:
            # Get URLs
            urls_query = """
            SELECT id, url, title, description, source, collection_method,
                   domain, relevance_score, quality_score, priority_level,
                   status, created_at, metadata
            FROM topic_urls 
            WHERE session_id = $1
            ORDER BY priority_level ASC, relevance_score DESC, created_at DESC
            """
            
            url_rows = await connection.fetch(urls_query, session_id)
            
            urls = []
            for row in url_rows:
                urls.append({
                    "id": row['id'],
                    "url": row['url'],
                    "title": row['title'],
                    "description": row['description'],
                    "source": row['source'],
                    "collection_method": row['collection_method'],
                    "domain": row['domain'],
                    "relevance_score": float(row['relevance_score']) if row['relevance_score'] else 0.0,
                    "quality_score": float(row['quality_score']) if row['quality_score'] else 0.0,
                    "priority_level": row['priority_level'],
                    "status": row['status'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                    "metadata": json.loads(row['metadata']) if row['metadata'] else {}
                })
            
            # Get campaign info
            campaign_query = """
            SELECT campaign_name, collection_strategy, status, 
                   urls_discovered, urls_processed, created_at, completed_at
            FROM url_collection_campaigns 
            WHERE session_id = $1
            ORDER BY created_at DESC LIMIT 1
            """
            
            campaign_row = await connection.fetchrow(campaign_query, session_id)
            
            campaign_info = None
            if campaign_row:
                campaign_info = {
                    "campaign_name": campaign_row['campaign_name'],
                    "collection_strategy": campaign_row['collection_strategy'],
                    "status": campaign_row['status'],
                    "urls_discovered": campaign_row['urls_discovered'],
                    "urls_processed": campaign_row['urls_processed'],
                    "created_at": campaign_row['created_at'].isoformat() if campaign_row['created_at'] else None,
                    "completed_at": campaign_row['completed_at'].isoformat() if campaign_row['completed_at'] else None
                }
            
            return {
                "session_id": session_id,
                "urls": urls,
                "url_count": len(urls),
                "campaign": campaign_info
            }

# Global service instance
_url_collection_service: Optional[EnhancedURLCollectionService] = None

async def get_url_collection_service() -> EnhancedURLCollectionService:
    """Get or create global URL collection service instance"""
    global _url_collection_service
    if _url_collection_service is None:
        _url_collection_service = EnhancedURLCollectionService()
        await _url_collection_service.initialize()
    return _url_collection_service
