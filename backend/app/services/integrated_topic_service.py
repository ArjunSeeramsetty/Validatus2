"""
Integrated Topic Service with Google Custom Search URL Collection
This integrates the existing topic management with the new URL collection capabilities
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .simple_topic_service import SimpleTopicService
from .enhanced_url_collection_service import get_url_collection_service, URLCollectionRequest
from ..models.topic_models import TopicCreateRequest

import logging
logger = logging.getLogger(__name__)

class IntegratedTopicService(SimpleTopicService):
    """
    Extended topic service that includes Google Custom Search URL collection
    Inherits from existing SimpleTopicService to maintain compatibility
    """
    
    def __init__(self):
        super().__init__()
        self.url_collection_service = None
    
    async def initialize(self):
        """Initialize parent service and URL collection"""
        await super().initialize()
        self.url_collection_service = await get_url_collection_service()
        
    async def create_topic_with_url_collection(self, request: TopicCreateRequest) -> Dict[str, Any]:
        """
        Create topic and automatically start URL collection
        This is the main integration point for the enhanced workflow
        """
        if not self.url_collection_service:
            await self.initialize()
        
        logger.info(f"Creating topic with integrated URL collection: {request.topic}")
        
        try:
            # Step 1: Create the topic using existing service
            topic_result = await self.create_topic(request)
            session_id = topic_result["session_id"]
            
            logger.info(f"Topic created with session ID: {session_id}")
            
            # Step 2: Start URL collection if search queries are provided
            url_collection_result = None
            if request.search_queries and len(request.search_queries) > 0:
                logger.info(f"Starting URL collection for {len(request.search_queries)} queries")
                
                collection_request = URLCollectionRequest(
                    session_id=session_id,
                    search_queries=request.search_queries,
                    initial_urls=request.initial_urls,
                    max_urls_per_query=10,  # Configurable
                    metadata={
                        "topic": request.topic,
                        "description": request.description,
                        "analysis_type": request.analysis_type,
                        "user_id": request.user_id
                    }
                )
                
                # Start URL collection asynchronously
                url_collection_result = await self.url_collection_service.collect_urls_for_topic(
                    collection_request
                )
                
                logger.info(f"URL collection completed: {url_collection_result.urls_stored} URLs collected")
                
                # Update topic with URL collection results
                await self._update_topic_with_url_collection(session_id, url_collection_result)
            
            # Step 3: Prepare integrated response
            response = {
                **topic_result,
                "url_collection": {
                    "status": url_collection_result.collection_status if url_collection_result else "skipped",
                    "urls_collected": url_collection_result.urls_stored if url_collection_result else 0,
                    "queries_processed": url_collection_result.queries_processed if url_collection_result else 0,
                    "campaign_id": url_collection_result.campaign_id if url_collection_result else None,
                    "error": url_collection_result.error_message if url_collection_result else None
                },
                "next_steps": {
                    "stage_1_ready": url_collection_result.collection_status == "completed" if url_collection_result else False,
                    "content_extraction": "pending" if url_collection_result and url_collection_result.urls_stored > 0 else "not_applicable",
                    "vectorization": "pending" if url_collection_result and url_collection_result.urls_stored > 0 else "not_applicable"
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error in integrated topic creation: {e}")
            # Return basic topic creation result even if URL collection fails
            return {
                **await self.create_topic(request),
                "url_collection": {
                    "status": "failed",
                    "error": str(e)
                }
            }
    
    async def _update_topic_with_url_collection(self, session_id: str, url_collection_result):
        """Update topic metadata with URL collection results"""
        try:
            # Get current topic
            topic = await self.get_topic(session_id, "demo_user_123")  # TODO: Get actual user_id
            if not topic:
                return
            
            # Update metadata
            current_metadata = topic.get("metadata", {})
            current_metadata["url_collection"] = {
                "completed_at": datetime.utcnow().isoformat(),
                "urls_collected": url_collection_result.urls_stored,
                "campaign_id": url_collection_result.campaign_id,
                "status": url_collection_result.collection_status
            }
            
            # Update in database
            if hasattr(self.db_manager, 'pool'):
                async with self.db_manager.pool.acquire() as connection:
                    await connection.execute(
                        "UPDATE topics SET metadata = $1, updated_at = NOW() WHERE session_id = $2",
                        current_metadata,
                        session_id
                    )
        except Exception as e:
            logger.error(f"Failed to update topic with URL collection results: {e}")
    
    async def get_topic_with_urls(self, session_id: str) -> Dict[str, Any]:
        """
        Get topic with collected URLs
        Enhanced version of get_topic that includes URL collection data
        """
        # Get basic topic data
        topic_data = await self.get_topic(session_id, "demo_user_123")  # TODO: Get actual user_id
        if not topic_data:
            return None
        
        # Get collected URLs
        try:
            if self.url_collection_service:
                urls_data = await self.url_collection_service.get_collected_urls(session_id)
                topic_data["collected_urls"] = urls_data
        except Exception as e:
            logger.error(f"Failed to get URLs for topic {session_id}: {e}")
            topic_data["collected_urls"] = {"error": str(e)}
        
        return topic_data
    
    async def list_topics_with_url_stats(self, user_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        List topics with URL collection statistics
        Enhanced version that includes URL collection status
        """
        # Get basic topics list
        topics_result = await self.list_topics(user_id, page=page, page_size=page_size)
        
        # Enhance each topic with URL stats
        if topics_result and "topics" in topics_result:
            enhanced_topics = []
            
            for topic in topics_result["topics"]:
                enhanced_topic = dict(topic)
                
                try:
                    # Get URL count for this topic
                    if hasattr(self.db_manager, 'pool'):
                        async with self.db_manager.pool.acquire() as connection:
                            url_count = await connection.fetchval(
                                "SELECT COUNT(*) FROM topic_urls WHERE session_id = $1",
                                topic["session_id"]
                            )
                            
                            campaign_info = await connection.fetchrow(
                                """SELECT status, urls_discovered, urls_processed, completed_at 
                                   FROM url_collection_campaigns 
                                   WHERE session_id = $1 
                                   ORDER BY created_at DESC LIMIT 1""",
                                topic["session_id"]
                            )
                            
                            enhanced_topic["url_stats"] = {
                                "total_urls": url_count or 0,
                                "campaign_status": campaign_info["status"] if campaign_info else "none",
                                "urls_discovered": campaign_info["urls_discovered"] if campaign_info else 0,
                                "urls_processed": campaign_info["urls_processed"] if campaign_info else 0,
                                "collection_completed": campaign_info["completed_at"] is not None if campaign_info else False
                            }
                except Exception as e:
                    enhanced_topic["url_stats"] = {"error": str(e)}
                
                enhanced_topics.append(enhanced_topic)
            
            topics_result["topics"] = enhanced_topics
        
        return topics_result
    
    async def start_stage_1_processing(self, session_id: str) -> Dict[str, Any]:
        """
        Start Stage 1 processing (content extraction and vectorization)
        This would integrate with existing repository stage processing
        """
        logger.info(f"Starting Stage 1 processing for session {session_id}")
        
        # Get collected URLs
        urls_data = await self.url_collection_service.get_collected_urls(session_id)
        
        if not urls_data["urls"]:
            return {
                "status": "failed",
                "error": "No URLs available for processing"
            }
        
        # Here you would integrate with existing repository's content extraction
        # and vectorization services. For now, return a placeholder response.
        
        return {
            "status": "started",
            "session_id": session_id,
            "urls_to_process": len(urls_data["urls"]),
            "message": f"Started processing {len(urls_data['urls'])} URLs for content extraction and vectorization"
        }

# Global service instance
_integrated_topic_service: Optional[IntegratedTopicService] = None

async def get_integrated_topic_service() -> IntegratedTopicService:
    """Get or create global integrated topic service instance"""
    global _integrated_topic_service
    if _integrated_topic_service is None:
        _integrated_topic_service = IntegratedTopicService()
        await _integrated_topic_service.initialize()
    return _integrated_topic_service
