"""
Workflow Manager for coordinating the 5 core tasks:
1. Topic Creation
2. Web Search  
3. Save URLs
4. Scrape URL Contents
5. Vector DB Creation
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from ..models.topic_models import TopicStatus
from .topic_service import get_topic_service_instance

logger = logging.getLogger(__name__)

class WorkflowStage(str, Enum):
    """Workflow stage enumeration"""
    TOPIC_CREATED = "topic_created"
    URL_COLLECTION = "url_collection" 
    URL_SCRAPING = "url_scraping"
    CONTENT_PROCESSING = "content_processing"
    VECTOR_STORE_CREATION = "vector_store_creation"
    ANALYSIS_READY = "analysis_ready"

class TopicWorkflowManager:
    """Manages the complete topic workflow"""
    
    def __init__(self):
        self.topic_service = get_topic_service_instance()
        self.url_orchestrator = None
        self.vector_store_manager = None
    
    async def execute_workflow(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Execute the complete 5-task workflow"""
        try:
            logger.info(f"Starting workflow execution for topic: {session_id}")
            
            # Get topic details
            topic = await self.topic_service.get_topic(session_id, user_id)
            if not topic:
                raise Exception("Topic not found")
            
            workflow_results = {
                "session_id": session_id,
                "topic_name": topic.topic,
                "user_id": user_id,
                "stages": {},
                "overall_status": "in_progress"
            }
            
            # Stage 1: Topic already created
            await self._update_workflow_progress(session_id, user_id, WorkflowStage.TOPIC_CREATED, {
                "stage": "Topic Creation",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            })
            workflow_results["stages"]["topic_creation"] = "completed"
            
            # Stage 2: Web Search & URL Collection
            await self._update_workflow_progress(session_id, user_id, WorkflowStage.URL_COLLECTION, {
                "stage": "URL Collection",
                "status": "in_progress",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            urls_result = await self._collect_urls(topic)
            workflow_results["stages"]["url_collection"] = {
                "status": "completed",
                "urls_found": len(urls_result.get("urls", [])),
                "urls": urls_result.get("urls", [])
            }
            
            # Stage 3: URL Scraping
            await self._update_workflow_progress(session_id, user_id, WorkflowStage.URL_SCRAPING, {
                "stage": "URL Scraping", 
                "status": "in_progress",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            scraping_result = await self._scrape_urls(urls_result.get("urls", []), topic.topic)
            workflow_results["stages"]["url_scraping"] = {
                "status": "completed",
                "documents_scraped": len(scraping_result.get("documents", [])),
                "quality_documents": len([d for d in scraping_result.get("documents", []) if d.get("quality_score", 0) > 0.3])
            }
            
            # Stage 4: Vector Store Creation
            await self._update_workflow_progress(session_id, user_id, WorkflowStage.VECTOR_STORE_CREATION, {
                "stage": "Vector Store Creation",
                "status": "in_progress", 
                "timestamp": datetime.utcnow().isoformat()
            })
            
            vector_result = await self._create_vector_store(session_id, topic.topic, scraping_result.get("documents", []))
            workflow_results["stages"]["vector_store"] = {
                "status": "completed",
                "chunks_created": vector_result.get("chunk_count", 0),
                "vector_store_id": vector_result.get("vector_store_id")
            }
            
            # Final Stage: Mark as Analysis Ready
            await self.topic_service.update_topic_status(
                session_id, 
                TopicStatus.COMPLETED, 
                user_id,
                {
                    "workflow": "completed",
                    "completed_at": datetime.utcnow().isoformat(),
                    "stages_completed": list(workflow_results["stages"].keys())
                }
            )
            
            workflow_results["overall_status"] = "completed"
            
            logger.info(f"Workflow completed successfully for topic: {session_id}")
            return workflow_results
            
        except Exception as e:
            logger.error(f"Workflow failed for topic {session_id}: {e}")
            
            # Mark as failed
            await self.topic_service.update_topic_status(
                session_id,
                TopicStatus.CREATED,  # Reset to created status
                user_id,
                {
                    "workflow": "failed",
                    "error": str(e),
                    "failed_at": datetime.utcnow().isoformat()
                }
            )
            
            raise Exception(f"Workflow failed: {str(e)}")
    
    async def _update_workflow_progress(self, session_id: str, user_id: str, 
                                      stage: WorkflowStage, progress_data: Dict[str, Any]):
        """Update workflow progress"""
        await self.topic_service.update_topic_status(
            session_id,
            TopicStatus.IN_PROGRESS,
            user_id,
            {
                "current_stage": stage.value,
                "stage_data": progress_data
            }
        )
    
    async def _collect_urls(self, topic) -> Dict[str, Any]:
        """Task 2: Web Search & URL Collection"""
        try:
            # For now, return mock URLs based on the topic's search queries
            # In production, this would integrate with your URL collection service
            mock_urls = [
                f"https://example.com/{topic.topic.replace(' ', '-').lower()}-analysis",
                f"https://research.com/{topic.topic.replace(' ', '-').lower()}-market-report",
                f"https://industry.com/{topic.topic.replace(' ', '-').lower()}-trends"
            ]
            
            # Add initial URLs from topic
            all_urls = topic.initial_urls + mock_urls
            
            return {
                "success": True,
                "urls": all_urls,
                "total_found": len(all_urls)
            }
            
        except Exception as e:
            logger.error(f"URL collection failed: {e}")
            return {
                "success": False,
                "urls": [],
                "error": str(e)
            }
    
    async def _scrape_urls(self, urls: List[str], topic_name: str) -> Dict[str, Any]:
        """Task 4: Scrape URL Contents"""
        try:
            # For now, return mock documents
            # In production, this would integrate with your scraping service
            mock_documents = []
            for i, url in enumerate(urls[:5]):  # Limit to 5 URLs for demo
                mock_documents.append({
                    "url": url,
                    "title": f"{topic_name} - Document {i+1}",
                    "content": f"This is mock content for {topic_name} from {url}. It contains relevant information about the topic and would be scraped in a real implementation.",
                    "quality_score": 0.7 + (i * 0.05),  # Varying quality scores
                    "metadata": {
                        "source": url,
                        "scraped_at": datetime.utcnow().isoformat(),
                        "word_count": 150 + (i * 20)
                    }
                })
            
            return {
                "success": True,
                "documents": mock_documents,
                "total_scraped": len(mock_documents)
            }
            
        except Exception as e:
            logger.error(f"URL scraping failed: {e}")
            return {
                "success": False,
                "documents": [],
                "error": str(e)
            }
    
    async def _create_vector_store(self, session_id: str, topic_name: str, 
                                 documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Task 5: Vector DB Creation"""
        try:
            # For now, return mock vector store creation
            # In production, this would integrate with your vector store service
            mock_vector_store_id = f"vector_store_{session_id}"
            
            return {
                "success": True,
                "vector_store_id": mock_vector_store_id,
                "chunk_count": len(documents) * 2  # Approximate chunks
            }
            
        except Exception as e:
            logger.error(f"Vector store creation failed: {e}")
            return {
                "success": False,
                "vector_store_id": None,
                "error": str(e)
            }

# Singleton instance
_workflow_manager_instance = None

def get_workflow_manager_instance():
    """Get the singleton WorkflowManager instance"""
    global _workflow_manager_instance
    if _workflow_manager_instance is None:
        _workflow_manager_instance = TopicWorkflowManager()
    return _workflow_manager_instance
