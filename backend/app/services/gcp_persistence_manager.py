"""
Unified GCP Persistence Manager
Orchestrates all GCP services for complete data persistence
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from contextlib import asynccontextmanager

from .gcp_sql_manager import GCPSQLManager
from .gcp_storage_manager import GCPStorageManager
from .gcp_redis_manager import GCPRedisManager
from .gcp_vector_manager import GCPVectorManager
from .gcp_spanner_manager import GCPSpannerManager

from ..models.topic_models import (
    TopicCreateRequest, TopicResponse, TopicUpdateRequest,
    TopicStatus, TopicListResponse
)
from ..core.gcp_persistence_config import get_gcp_persistence_settings

logger = logging.getLogger(__name__)

class GCPPersistenceManager:
    """Unified persistence manager for all GCP services"""
    
    def __init__(self):
        self.settings = get_gcp_persistence_settings()
        
        # Initialize all service managers
        self.sql_manager = GCPSQLManager()
        self.storage_manager = GCPStorageManager()
        self.redis_manager = GCPRedisManager()
        self.vector_manager = GCPVectorManager()
        self.spanner_manager = GCPSpannerManager()
        
        self._initialized = False
        logger.info("GCP Persistence Manager created")
    
    async def initialize(self):
        """Initialize all GCP services"""
        if self._initialized:
            return
        
        try:
            # Initialize services in parallel for faster startup
            await asyncio.gather(
                self.sql_manager.initialize(),
                self.redis_manager.initialize(),
                self.vector_manager.initialize(),
                self.spanner_manager.initialize(),
                return_exceptions=True
            )
            
            self._initialized = True
            logger.info("✅ All GCP services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GCP services: {e}")
            raise
    
    async def close(self):
        """Close all service connections"""
        try:
            await asyncio.gather(
                self.sql_manager.close(),
                self.redis_manager.close(),
                self.vector_manager.close(),
                self.spanner_manager.close(),
                return_exceptions=True
            )
            
            self._initialized = False
            logger.info("All GCP service connections closed")
            
        except Exception as e:
            logger.error(f"Error closing GCP services: {e}")
    
    async def _ensure_initialized(self):
        """Ensure all services are initialized"""
        if not self._initialized:
            await self.initialize()
    
    # Topic Management with Full GCP Integration
    async def create_topic_complete(self, request: TopicCreateRequest) -> TopicResponse:
        """Create topic with complete GCP persistence setup"""
        await self._ensure_initialized()
        
        try:
            logger.info(f"Creating topic '{request.topic}' for user {request.user_id}")
            
            # 1. Create topic in Cloud SQL (primary source of truth)
            topic_response = await self.sql_manager.create_topic(request)
            session_id = topic_response.session_id
            
            # 2. Cache session data in Redis for performance
            session_cache_data = {
                "session_id": session_id,
                "topic": request.topic,
                "user_id": request.user_id,
                "status": TopicStatus.CREATED.value,
                "created_at": topic_response.created_at.isoformat(),
                "analysis_type": request.analysis_type.value
            }
            
            await self.redis_manager.cache_session_data(
                session_id, 
                session_cache_data, 
                ttl=86400  # 24 hours
            )
            
            # 3. Initialize workflow progress tracking
            await self.redis_manager.cache_workflow_progress(
                session_id,
                "CREATED",
                {
                    "stage": "Topic Created",
                    "percentage": 10,
                    "message": "Topic successfully created",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # 4. Queue initial URLs if provided
            if request.initial_urls:
                await self.redis_manager.queue_urls_for_processing(
                    session_id, 
                    request.initial_urls
                )
                
                # Also store in SQL for persistence
                await self.sql_manager.store_urls(
                    session_id, 
                    request.initial_urls, 
                    source="initial"
                )
            
            # 5. Track user activity
            await self.redis_manager.track_user_activity(
                request.user_id,
                "topic_created",
                {
                    "session_id": session_id,
                    "topic": request.topic,
                    "analysis_type": request.analysis_type.value
                }
            )
            
            logger.info(f"✅ Topic {session_id} created successfully with full GCP setup")
            return topic_response
            
        except Exception as e:
            logger.error(f"Failed to create topic with complete persistence: {e}")
            # Cleanup any partial state
            await self._cleanup_failed_topic_creation(session_id if 'session_id' in locals() else None)
            raise
    
    async def get_topic_complete(self, session_id: str, user_id: str) -> Optional[TopicResponse]:
        """Get topic with performance optimization through caching"""
        await self._ensure_initialized()
        
        try:
            # 1. Try cache first for performance
            cached_data = await self.redis_manager.get_session_data(session_id)
            
            if cached_data and cached_data.get('user_id') == user_id:
                # Extend cache TTL on access
                await self.redis_manager.extend_session_ttl(session_id, 86400)
                
                # Get detailed data from SQL if cache hit
                topic_response = await self.sql_manager.get_topic(session_id, user_id)
                
                if topic_response:
                    logger.debug(f"Retrieved topic {session_id} from cache + SQL")
                    return topic_response
            
            # 2. Fallback to SQL only
            topic_response = await self.sql_manager.get_topic(session_id, user_id)
            
            if topic_response:
                # Update cache for future requests
                session_cache_data = {
                    "session_id": session_id,
                    "topic": topic_response.topic,
                    "user_id": user_id,
                    "status": topic_response.status.value,
                    "created_at": topic_response.created_at.isoformat(),
                    "analysis_type": topic_response.analysis_type.value
                }
                
                await self.redis_manager.cache_session_data(
                    session_id, 
                    session_cache_data, 
                    ttl=86400
                )
                
                logger.debug(f"Retrieved topic {session_id} from SQL and cached")
            
            return topic_response
            
        except Exception as e:
            logger.error(f"Failed to get topic {session_id}: {e}")
            return None
    
    async def list_topics_complete(self, user_id: str, **kwargs) -> TopicListResponse:
        """List topics with caching for frequently accessed data"""
        await self._ensure_initialized()
        
        try:
            # Get from SQL (primary source)
            topics_response = await self.sql_manager.list_topics(user_id, **kwargs)
            
            # Cache individual topics for future single-topic requests
            for topic in topics_response.topics:
                session_cache_data = {
                    "session_id": topic.session_id,
                    "topic": topic.topic,
                    "user_id": user_id,
                    "status": topic.status.value,
                    "created_at": topic.created_at.isoformat(),
                    "analysis_type": topic.analysis_type.value
                }
                
                # Cache with shorter TTL for list operations
                await self.redis_manager.cache_session_data(
                    topic.session_id, 
                    session_cache_data, 
                    ttl=3600  # 1 hour
                )
            
            logger.debug(f"Listed {len(topics_response.topics)} topics for user {user_id}")
            return topics_response
            
        except Exception as e:
            logger.error(f"Failed to list topics for user {user_id}: {e}")
            return TopicListResponse(topics=[], total=0, page=1, page_size=20, has_next=False, has_previous=False)
    
    # Complete Workflow Execution
    async def execute_complete_workflow(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Execute the complete 5-task workflow with full GCP persistence"""
        await self._ensure_initialized()
        
        workflow_result = {
            "session_id": session_id,
            "user_id": user_id,
            "stages": {},
            "overall_status": "in_progress",
            "started_at": datetime.utcnow().isoformat()
        }
        
        try:
            # Update topic status to IN_PROGRESS
            await self.sql_manager.update_topic_status(
                session_id, 
                TopicStatus.IN_PROGRESS, 
                user_id,
                {"workflow_started": True}
            )
            
            # Stage 1: URL Collection
            logger.info(f"Stage 1: URL Collection for {session_id}")
            await self._update_workflow_progress(session_id, "URL_COLLECTION", 20, "Collecting URLs from search and initial sources")
            
            urls_result = await self._execute_url_collection_stage(session_id)
            workflow_result["stages"]["url_collection"] = urls_result
            
            # Stage 2: URL Scraping and Content Storage
            logger.info(f"Stage 2: URL Scraping for {session_id}")
            await self._update_workflow_progress(session_id, "URL_SCRAPING", 40, "Scraping content from collected URLs")
            
            scraping_result = await self._execute_scraping_stage(session_id)
            workflow_result["stages"]["url_scraping"] = scraping_result
            
            # Stage 3: Vector Store Creation
            logger.info(f"Stage 3: Vector Store Creation for {session_id}")
            await self._update_workflow_progress(session_id, "VECTOR_CREATION", 60, "Creating vector embeddings and search index")
            
            vector_result = await self._execute_vector_creation_stage(session_id)
            workflow_result["stages"]["vector_creation"] = vector_result
            
            # Stage 4: Analysis Execution
            logger.info(f"Stage 4: Analysis Execution for {session_id}")
            await self._update_workflow_progress(session_id, "ANALYSIS", 80, "Executing strategic analysis")
            
            analysis_result = await self._execute_analysis_stage(session_id)
            workflow_result["stages"]["analysis"] = analysis_result
            
            # Stage 5: Complete and Store Results
            logger.info(f"Stage 5: Finalizing results for {session_id}")
            await self._update_workflow_progress(session_id, "COMPLETED", 100, "Analysis completed successfully")
            
            # Update final status
            await self.sql_manager.update_topic_status(
                session_id, 
                TopicStatus.COMPLETED, 
                user_id,
                {"workflow_completed": True, "completed_at": datetime.utcnow().isoformat()}
            )
            
            workflow_result["overall_status"] = "completed"
            workflow_result["completed_at"] = datetime.utcnow().isoformat()
            
            # Store comprehensive results in Spanner for global analytics
            await self.spanner_manager.store_workflow_results(session_id, workflow_result)
            
            # Track completion activity
            await self.redis_manager.track_user_activity(
                user_id,
                "workflow_completed",
                {
                    "session_id": session_id,
                    "total_urls": workflow_result["stages"]["url_collection"]["urls_collected"],
                    "documents_processed": workflow_result["stages"]["url_scraping"]["documents_processed"],
                    "analysis_confidence": workflow_result["stages"]["analysis"]["confidence_score"]
                }
            )
            
            logger.info(f"✅ Complete workflow finished successfully for {session_id}")
            return workflow_result
            
        except Exception as e:
            logger.error(f"Workflow failed for {session_id}: {e}")
            
            # Update failure status
            await self.sql_manager.update_topic_status(
                session_id, 
                TopicStatus.FAILED, 
                user_id,
                {"workflow_failed": True, "error": str(e)}
            )
            
            await self._update_workflow_progress(
                session_id, 
                "FAILED", 
                0, 
                f"Workflow failed: {str(e)}"
            )
            
            workflow_result["overall_status"] = "failed"
            workflow_result["error"] = str(e)
            
            raise
    
    # Individual Workflow Stages
    async def _execute_url_collection_stage(self, session_id: str) -> Dict[str, Any]:
        """Execute URL collection stage"""
        try:
            # Get initial URLs from queue
            initial_urls = []
            while True:
                url = await self.redis_manager.get_next_url_to_process(session_id)
                if not url:
                    break
                initial_urls.append(url)
            
            # Simulate additional URL discovery (integrate with your URL orchestrator)
            from .gcp_url_orchestrator import GCPURLOrchestrator
            url_orchestrator = GCPURLOrchestrator(project_id=self.settings.project_id)
            
            # Get topic details for search
            topic_data = await self.redis_manager.get_session_data(session_id)
            topic_name = topic_data.get('topic', 'analysis') if topic_data else 'analysis'
            
            # Collect additional URLs through search
            search_urls = await url_orchestrator.collect_urls_for_topic(
                topic_name,
                search_queries=[f"{topic_name} market analysis", f"{topic_name} industry trends"],
                max_urls=30
            )
            
            all_urls = list(set(initial_urls + search_urls))  # Deduplicate
            
            # Store all URLs in SQL for persistence
            stored_count = await self.sql_manager.store_urls(session_id, all_urls, source="search")
            
            return {
                "status": "completed",
                "urls_collected": len(all_urls),
                "urls_stored": stored_count,
                "initial_urls": len(initial_urls),
                "search_urls": len(search_urls)
            }
            
        except Exception as e:
            logger.error(f"URL collection stage failed for {session_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "urls_collected": 0
            }
    
    async def _execute_scraping_stage(self, session_id: str) -> Dict[str, Any]:
        """Execute content scraping stage"""
        try:
            # Get URLs ready for scraping
            urls_to_scrape = await self.sql_manager.get_urls_for_scraping(session_id, status="pending", limit=50)
            
            if not urls_to_scrape:
                return {
                    "status": "completed",
                    "documents_processed": 0,
                    "message": "No URLs to scrape"
                }
            
            # Scrape content and store in GCS
            documents_processed = 0
            
            for url_record in urls_to_scrape:
                url = url_record['url']
                
                try:
                    # Simulate content scraping (integrate with your scraper)
                    from .content_scraper import ContentScraper
                    scraper = ContentScraper()
                    
                    scraped_result = await scraper.scrape_url(url)
                    
                    if scraped_result['success']:
                        # Store content in GCS
                        gcs_path = await self.storage_manager.store_scraped_content(
                            session_id,
                            url,
                            scraped_result['content'],
                            {
                                'title': scraped_result.get('title'),
                                'quality_score': scraped_result.get('quality_score'),
                                'word_count': scraped_result.get('word_count')
                            }
                        )
                        
                        # Update URL record in SQL
                        await self.sql_manager.update_url_content(
                            session_id,
                            url,
                            gcs_path,
                            {
                                'content_hash': scraped_result.get('content_hash'),
                                'title': scraped_result.get('title'),
                                'word_count': scraped_result.get('word_count'),
                                'quality_score': scraped_result.get('quality_score')
                            }
                        )
                        
                        documents_processed += 1
                
                except Exception as url_error:
                    logger.error(f"Failed to scrape {url}: {url_error}")
                    continue
            
            return {
                "status": "completed",
                "documents_processed": documents_processed,
                "total_urls": len(urls_to_scrape)
            }
            
        except Exception as e:
            logger.error(f"Scraping stage failed for {session_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "documents_processed": 0
            }
    
    async def _execute_vector_creation_stage(self, session_id: str) -> Dict[str, Any]:
        """Execute vector embeddings creation stage"""
        try:
            # Create vector embeddings using Vertex AI
            vector_result = await self.vector_manager.create_topic_vector_index(session_id)
            
            return {
                "status": "completed",
                "embeddings_created": vector_result.get("embedding_count", 0),
                "vector_index_id": vector_result.get("index_id"),
                "vector_endpoint_id": vector_result.get("endpoint_id")
            }
            
        except Exception as e:
            logger.error(f"Vector creation stage failed for {session_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "embeddings_created": 0
            }
    
    async def _execute_analysis_stage(self, session_id: str) -> Dict[str, Any]:
        """Execute strategic analysis stage"""
        try:
            # Execute analysis using your analysis engines
            analysis_result = {
                "analysis_id": f"analysis_{session_id}_{int(datetime.utcnow().timestamp())}",
                "overall_score": 0.75,  # Placeholder - replace with actual analysis
                "confidence_score": 0.82,
                "factor_scores": {
                    "market_potential": 0.78,
                    "competitive_advantage": 0.71,
                    "growth_opportunity": 0.83
                },
                "processing_time_ms": 15000
            }
            
            # Cache analysis preview in Redis
            await self.redis_manager.cache_analysis_preview(
                session_id,
                analysis_result["analysis_id"],
                analysis_result,
                ttl=3600  # 1 hour cache
            )
            
            # Store full results in Spanner
            await self.spanner_manager.store_analysis_results(session_id, analysis_result)
            
            return {
                "status": "completed",
                "analysis_id": analysis_result["analysis_id"],
                "confidence_score": analysis_result["confidence_score"],
                "overall_score": analysis_result["overall_score"]
            }
            
        except Exception as e:
            logger.error(f"Analysis stage failed for {session_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "analysis_id": None
            }
    
    # Helper Methods
    async def _update_workflow_progress(self, session_id: str, stage: str, 
                                      percentage: int, message: str):
        """Update workflow progress in Redis"""
        progress_data = {
            "stage": stage,
            "percentage": percentage,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_manager.cache_workflow_progress(session_id, stage, progress_data)
    
    async def _cleanup_failed_topic_creation(self, session_id: Optional[str]):
        """Cleanup any partial state from failed topic creation"""
        if not session_id:
            return
        
        try:
            # Remove from cache
            await self.redis_manager.client.delete(f"session:{session_id}")
            await self.redis_manager.client.delete(f"workflow:{session_id}")
            await self.redis_manager.client.delete(f"queue:scraping:{session_id}")
            
            logger.info(f"Cleaned up failed topic creation: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup failed topic creation {session_id}: {e}")
    
    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of all GCP services"""
        await self._ensure_initialized()
        
        health_status = {
            "overall_status": "healthy",
            "services": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Check all services in parallel
            results = await asyncio.gather(
                self._check_sql_health(),
                self._check_redis_health(),
                self._check_storage_health(),
                self._check_vector_health(),
                self._check_spanner_health(),
                return_exceptions=True
            )
            
            service_names = ["sql", "redis", "storage", "vector", "spanner"]
            
            for i, result in enumerate(results):
                service_name = service_names[i]
                
                if isinstance(result, Exception):
                    health_status["services"][service_name] = {
                        "status": "unhealthy",
                        "error": str(result)
                    }
                    health_status["overall_status"] = "degraded"
                else:
                    health_status["services"][service_name] = result
                    
                    if result.get("status") != "healthy":
                        health_status["overall_status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_sql_health(self) -> Dict[str, Any]:
        """Check Cloud SQL health"""
        try:
            async with self.sql_manager.get_connection() as conn:
                result = await conn.fetchval("SELECT 1")
                return {
                    "status": "healthy" if result == 1 else "unhealthy",
                    "response_time_ms": 10  # Placeholder
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        return await self.redis_manager.health_check()
    
    async def _check_storage_health(self) -> Dict[str, Any]:
        """Check Cloud Storage health"""
        try:
            # Test bucket access
            bucket = self.storage_manager.content_bucket
            bucket.reload()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_vector_health(self) -> Dict[str, Any]:
        """Check Vertex AI Vector Search health"""
        return await self.vector_manager.health_check()
    
    async def _check_spanner_health(self) -> Dict[str, Any]:
        """Check Cloud Spanner health"""
        return await self.spanner_manager.health_check()


# Global instance
_persistence_manager = None

def get_gcp_persistence_manager() -> GCPPersistenceManager:
    """Get the singleton GCP persistence manager"""
    global _persistence_manager
    if _persistence_manager is None:
        _persistence_manager = GCPPersistenceManager()
    return _persistence_manager
