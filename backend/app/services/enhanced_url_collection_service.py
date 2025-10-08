"""
Enhanced URL Collection Service with Google Custom Search and Database Persistence
Integrates with existing repository architecture and database schema
"""
import asyncio
import json
import hashlib
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

from .google_custom_search_service import get_google_search_service, SearchResult
from .gcp_sql_manager import GCPSQLManager
from ..core.gcp_persistence_config import get_gcp_persistence_settings
from .strategic_query_generator import get_query_generator
from .url_quality_validator import get_url_validator

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
        self.query_generator = get_query_generator()
        self.url_validator = get_url_validator()
        
    async def initialize(self):
        """Initialize all services"""
        await self.db_manager.initialize()
        self.search_service = await get_google_search_service()
        logger.info("✅ Enhanced URL Collection Service initialized with strategic query generation and quality validation")
    
    async def collect_urls_for_topic(self, request: URLCollectionRequest) -> URLCollectionResult:
        """
        Main URL collection method - integrates with existing repository flow
        
        ENHANCED FEATURES:
        1. Strategic Query Generation: Combines user queries with Segment+Factor+Layer queries
        2. URL Quality Validation: Filters and scores URLs for strategic analysis usefulness
        3. Multi-layer Deduplication: Ensures only unique, high-quality URLs
        4. Database Persistence: Stores in Cloud SQL PostgreSQL
        """
        if not self.search_service:
            await self.initialize()
        
        logger.info(f"🔍 Starting enhanced URL collection for session {request.session_id}")
        
        try:
            # Check if collection already exists and is fresh
            if not request.force_refresh:
                existing_campaign = await self._get_existing_campaign(request.session_id)
                if existing_campaign:
                    logger.info(f"Using existing URL collection for session {request.session_id}")
                    return existing_campaign
            
            # STEP 1: Get topic information for query generation
            topic_info = await self._get_topic_info(request.session_id)
            topic_name = topic_info.get('topic', 'Unknown Topic')
            topic_description = topic_info.get('description', '')
            
            # STEP 2: Generate comprehensive search queries (User + Segment + Factor + Layer)
            # Uses topic name AND description for enhanced relevance
            all_search_queries = self.query_generator.generate_queries(
                topic=topic_name,
                description=topic_description,  # Include description for context
                user_queries=request.search_queries,
                include_segments=True,
                include_factors=True,
                include_layers=True,
                max_queries=50  # Limit total queries for API quota
            )
            
            logger.info(f"🎯 Using topic: '{topic_name}' with description: '{topic_description[:50]}...' for enhanced query relevance")
            
            logger.info(f"📝 Generated {len(all_search_queries)} search queries (User: {len(request.search_queries or [])}, Strategic: {len(all_search_queries) - len(request.search_queries or [])})")
            
            # Create new collection campaign
            campaign_id = await self._create_collection_campaign(request)
            
            # STEP 3: Execute URL collection using Google Custom Search
            search_results = await self.search_service.search_urls_for_topic(
                search_queries=all_search_queries,  # Use enhanced queries
                session_id=request.session_id,
                max_results_per_query=request.max_urls_per_query
            )
            
            # STEP 4: Merge with initial URLs and apply quality validation
            all_urls = self._merge_with_initial_urls(
                search_results["urls"], 
                request.initial_urls,
                topic=topic_name  # Pass topic for quality validation
            )
            
            # STEP 5: Store validated, high-quality URLs in Cloud SQL database
            stored_count = await self._store_collected_urls(
                session_id=request.session_id,
                campaign_id=campaign_id,
                urls=all_urls,  # Only high-quality URLs that passed validation
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
                campaign_id=-1,  # Indicates no campaign was created
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
    
    async def _get_topic_info(self, session_id: str) -> Dict[str, Any]:
        """Retrieve topic information from database for query generation"""
        async with self.db_manager.pool.acquire() as connection:
            query = """
            SELECT session_id, topic, description, analysis_type
            FROM topics
            WHERE session_id = $1
            """
            
            row = await connection.fetchrow(query, session_id)
            if row:
                return {
                    "session_id": row['session_id'],
                    "topic": row['topic'],
                    "description": row['description'] or "",
                    "analysis_type": row['analysis_type'] or "comprehensive"
                }
            
            # Fallback if topic not found
            return {"session_id": session_id, "topic": session_id, "description": "", "analysis_type": "comprehensive"}
    
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
        initial_urls: Optional[List[str]],
        topic: str = ""
    ) -> List[Dict[str, Any]]:
        """
        DEDUPLICATION STEP 3: Merge collected URLs with existing initial URLs
        + QUALITY VALIDATION: Filter and score URLs for strategic analysis usefulness
        
        - Combines Google Custom Search results with manually provided initial URLs
        - Uses URL hash to ensure no duplicates between search results and initial URLs
        - Validates each URL for quality and relevance to strategic analysis
        - Prioritizes high-quality URLs based on domain authority and content indicators
        - Filters out low-quality URLs (blogs, paywalls, dynamic pages, etc.)
        """
        merged_urls = []
        seen_urls = set()
        rejected_count = 0
        
        # Add search results first (they have richer metadata)
        for result in search_results:
            url_hash = self._generate_url_hash(result.url)
            if url_hash not in seen_urls:
                # QUALITY VALIDATION: Validate and score URL
                validation_result = self.url_validator.validate_and_score(
                    url=result.url,
                    title=result.title,
                    snippet=result.snippet,
                    topic=topic,
                    relevance_score=result.relevance_score
                )
                
                # Only include URLs that pass quality validation
                if validation_result["is_valid"]:
                    merged_urls.append({
                        "url": result.url,
                        "title": result.title,
                        "description": result.snippet,
                        "source": "google_custom_search",
                        "collection_method": "search_api",
                        "domain": result.domain,
                        "relevance_score": result.relevance_score,
                        "quality_score": validation_result["quality_score"],
                        "priority_level": validation_result["priority_level"],
                        "search_query": result.search_query,
                        "metadata": {
                            **result.metadata,
                            "validation": validation_result["scoring_breakdown"],
                            "confidence": validation_result["confidence"]
                        }
                    })
                    seen_urls.add(url_hash)
                else:
                    rejected_count += 1
                    logger.debug(f"❌ URL rejected: {result.url} - {validation_result['rejection_reason']}")
        
        # Add initial URLs if not already present in search results
        if initial_urls:
            for url in initial_urls:
                url_hash = self._generate_url_hash(url)
                if url_hash not in seen_urls:  # DEDUPLICATION: Skip if already in search results
                    # Manual URLs are assumed to be high quality (user-vetted)
                    parsed_url = urllib.parse.urlparse(url)
                    merged_urls.append({
                        "url": url,
                        "title": "",
                        "description": "",
                        "source": "manual",
                        "collection_method": "manual",
                        "domain": parsed_url.netloc,
                        "relevance_score": 0.8,  # Higher for manual URLs
                        "quality_score": 0.75,  # Higher assumed quality
                        "priority_level": 2,  # Higher priority for manual (user-selected)
                        "search_query": "",
                        "metadata": {"source": "initial_urls", "user_provided": True}
                    })
                    seen_urls.add(url_hash)
        
        if rejected_count > 0:
            logger.info(f"🔍 Quality Filter: Rejected {rejected_count} low-quality URLs, kept {len(merged_urls)} high-quality URLs")
        
        return merged_urls
    
    async def _store_collected_urls(
        self, 
        session_id: str, 
        campaign_id: int, 
        urls: List[Dict[str, Any]], 
        search_metadata: Dict[str, Any]
    ) -> int:
        """
        ═══════════════════════════════════════════════════════════════════════════
        PERSISTENCE: Store collected URLs in Cloud SQL PostgreSQL Database
        ═══════════════════════════════════════════════════════════════════════════
        
        DATABASE TABLE: topic_urls
        LOCATION: Cloud SQL PostgreSQL instance 'validatus-sql'
        DATABASE: validatus
        
        DEDUPLICATION STEP 4 (FINAL): Database-level deduplication
        - Uses PostgreSQL UNIQUE constraint on (session_id, url_hash)
        - ON CONFLICT DO NOTHING ensures no duplicates are inserted
        - Prevents duplicate URLs across multiple collection campaigns
        - url_hash is generated from normalized URL (domain + path + query)
        
        STORED DATA PER URL:
        - url: The full URL
        - url_hash: Unique hash for deduplication
        - source: 'google_custom_search' or 'manual'
        - collection_method: 'search_api' or 'manual'
        - title: Page title from search results
        - description: Snippet/description from search
        - domain: Extracted domain name
        - relevance_score: Calculated relevance (0-1)
        - quality_score: Quality assessment (0-1)
        - priority_level: Processing priority (1-10)
        - status: 'pending' (for later content scraping)
        - metadata: JSON with search metadata
        
        RETURNS: Number of new URLs actually inserted (excludes duplicates)
        ═══════════════════════════════════════════════════════════════════════════
        """
        stored_count = 0
        
        async with self.db_manager.pool.acquire() as connection:
            async with connection.transaction():
                for url_data in urls:
                    try:
                        url_hash = self._generate_url_hash(url_data["url"])
                        
                        # INSERT with ON CONFLICT DO NOTHING for database-level deduplication
                        insert_sql = """
                        INSERT INTO topic_urls (
                            session_id, url, url_hash, source, collection_method,
                            title, description, domain, relevance_score, quality_score,
                            priority_level, status, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        ON CONFLICT (session_id, url_hash) DO NOTHING
                        """
                        
                        result = await connection.execute(
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
                        
                        # Only increment if a row was actually inserted (not a duplicate)
                        if result == "INSERT 0 1":
                            stored_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error storing URL {url_data['url']}: {e}")
                        continue
        
        logger.info(f"✅ Stored {stored_count} new unique URLs for session {session_id} in Cloud SQL database")
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
                "completion_time": datetime.now(timezone.utc).isoformat(),
                "search_stats": metadata.get("query_stats", {}),
                "total_api_calls": metadata.get("total_api_calls", 0)
            }
            
            await connection.execute(
                update_sql,
                "completed",
                100.0,
                urls_discovered,
                urls_stored,
                datetime.now(timezone.utc),
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
                "failed_at": datetime.now(timezone.utc).isoformat()
            }
            
            await connection.execute(
                update_sql,
                "failed",
                datetime.now(timezone.utc),
                json.dumps(error_metadata),
                campaign_id
            )
    
    def _generate_url_hash(self, url: str) -> str:
        """Generate hash for URL deduplication"""
        parsed = urllib.parse.urlparse(url.lower())
        # Include query params for accurate deduplication
        normalized = f"{parsed.netloc}{parsed.path}{parsed.query}"
        return hashlib.sha256(normalized.encode()).hexdigest()
    
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
_initialization_lock = asyncio.Lock()

async def get_url_collection_service() -> EnhancedURLCollectionService:
    """Get or create global URL collection service instance"""
    global _url_collection_service
    if _url_collection_service is None:
        async with _initialization_lock:
            # Double-check after acquiring lock
            if _url_collection_service is None:
                _url_collection_service = EnhancedURLCollectionService()
                await _url_collection_service.initialize()
    return _url_collection_service
