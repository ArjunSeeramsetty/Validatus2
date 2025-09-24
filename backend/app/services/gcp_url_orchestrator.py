# backend/app/services/gcp_url_orchestrator.py

import asyncio
import aiohttp
import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

# Google Cloud imports
from google.cloud import tasks_v2
from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud import functions_v1
from google.cloud import monitoring_v3

# Internal imports
from ..core.gcp_config import GCPSettings
from ..middleware.monitoring import performance_monitor

logger = logging.getLogger(__name__)

@dataclass
class GCPScrapingTask:
    """GCP Cloud Tasks compatible scraping task"""
    task_id: str
    topic: str
    urls: List[str]
    created_at: str
    status: str
    result_gcs_path: Optional[str] = None

class ScrapedContentProcessor:
    """Content processing for scraped data"""
    
    def extract_main_content(self, html_content: str) -> str:
        """Extract main content from HTML"""
        # Simplified content extraction
        # In production, use libraries like BeautifulSoup or newspaper3k
        import re
        
        # Remove script and style elements
        content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def extract_title(self, html_content: str) -> str:
        """Extract title from HTML"""
        import re
        
        # Look for title tag
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            return re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        
        # Look for h1 tag as fallback
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            return re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        
        return ""

class ResearchAgent:
    """Research agent for URL discovery"""
    
    async def search_and_extract(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search and extract URLs (placeholder implementation)"""
        # This would integrate with search APIs like Google Search, Bing, etc.
        # For now, return mock data
        return {
            "results": [
                {
                    "url": f"https://example.com/article-{i}",
                    "title": f"Sample Article {i} about {query}",
                    "snippet": f"This is a sample article about {query} with relevant content."
                }
                for i in range(max_results)
            ]
        }

class GCPURLOrchestrator:
    """GCP-integrated URL orchestrator with enterprise scalability"""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.settings = GCPSettings()
        
        # Check if running in local development mode
        # Only use local dev mode if explicitly set, not just because service account key is missing
        self.local_dev_mode = self.settings.local_development_mode
        
        if self.local_dev_mode:
            logger.info("Running GCPURLOrchestrator in local development mode")
            self._init_local_dev_mode()
        else:
            # Configuration
            self.bucket_name = f"{project_id}-validatus-scraping"
            self.task_queue_name = "url-scraping-queue"
            self.pubsub_topic = "url-scraping-results"
            
            # Initialize GCP clients
            self._init_gcp_clients()
        
        # Rate limiting
        self.max_concurrent_requests = 50  # Increased for GCP
        self.request_delay = 0.1  # Reduced with Cloud Tasks
        
        # Content quality thresholds
        self.min_word_count = 100
        self.min_quality_score = 0.3
        
        if not self.local_dev_mode:
            # Ensure infrastructure
            self._ensure_gcp_infrastructure()
    
    def _init_local_dev_mode(self):
        """Initialize for local development mode"""
        logger.info("Initializing local development mode - using mock implementations")
        
        # Mock clients for local development
        self.storage_client = None
        self.tasks_client = None
        self.publisher = None
        self.monitoring_client = None
        
        # Configuration (not used in local mode)
        self.bucket_name = "local-validatus-scraping"
        self.task_queue_name = "local-url-scraping-queue"
        self.pubsub_topic = "local-url-scraping-results"
        
        logger.info("Local development mode initialized successfully")
    
    def _init_gcp_clients(self):
        """Initialize GCP service clients"""
        # Cloud Tasks client for job queuing
        self.tasks_client = tasks_v2.CloudTasksClient()
        self.queue_path = self.tasks_client.queue_path(
            self.project_id, self.region, self.task_queue_name
        )
        
        # Pub/Sub client for event messaging
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.topic_path = self.publisher.topic_path(self.project_id, self.pubsub_topic)
        
        # Storage client
        self.storage_client = storage.Client(project=self.project_id)
        
        # Monitoring client
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        
        # Research agent with GCP enhancements
        self.research_agent = ResearchAgent()
        self.content_processor = ScrapedContentProcessor()
        
        logger.info("✅ GCP URL Orchestrator clients initialized")
    
    def _ensure_gcp_infrastructure(self):
        """Ensure required GCP infrastructure"""
        try:
            # Create storage bucket
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket = self.storage_client.create_bucket(
                    self.bucket_name, location=self.region
                )
                logger.info(f"Created scraping bucket: {self.bucket_name}")
            
            # Create Pub/Sub topic
            try:
                self.publisher.create_topic(request={"name": self.topic_path})
                logger.info(f"Created Pub/Sub topic: {self.pubsub_topic}")
            except Exception:
                # Topic might already exist
                pass
            
            logger.info("✅ GCP URL orchestrator infrastructure verified")
            
        except Exception as e:
            logger.error(f"Failed to ensure GCP infrastructure: {e}")
            raise
    
    @performance_monitor
    async def collect_urls_for_topic(self, topic: str, search_queries: List[str] = None, 
                                   max_urls: int = 100) -> List[str]:
        """Collect URLs using GCP-enhanced research capabilities"""
        logger.info(f"Collecting URLs for topic: '{topic}' with max {max_urls} URLs")
        
        # Generate search queries if not provided
        if not search_queries:
            search_queries = self._generate_search_queries(topic)
        
        # Create Cloud Task for URL collection
        task_id = f"collect_{topic}_{datetime.now().timestamp()}"
        
        try:
            # Use enhanced research agent with parallel processing
            all_urls = set()
            
            # Process queries in parallel using asyncio
            tasks = [
                self._search_single_query(query, max_urls // len(search_queries))
                for query in search_queries[:10]  # Limit to 10 queries
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_urls.update(result)
                elif isinstance(result, Exception):
                    logger.error(f"Search query failed: {result}")
            
            # Limit and deduplicate
            url_list = list(all_urls)[:max_urls]
            
            # Store results in GCS for audit
            await self._store_collected_urls(task_id, topic, url_list, search_queries)
            
            # Publish success event
            await self._publish_collection_event(task_id, topic, len(url_list))
            
            logger.info(f"✅ Collected {len(url_list)} URLs for topic '{topic}'")
            return url_list
            
        except Exception as e:
            logger.error(f"Failed to collect URLs for topic '{topic}': {e}")
            # Publish failure event
            await self._publish_collection_event(task_id, topic, 0, error=str(e))
            return []
    
    async def _search_single_query(self, query: str, max_results: int) -> List[str]:
        """Search single query with error handling"""
        try:
            search_results = await self.research_agent.search_and_extract(
                query, max_results=max_results
            )
            
            urls = []
            for result in search_results.get("results", []):
                url = result.get("url")
                if url and self._is_valid_url(url):
                    urls.append(url)
            
            return urls
            
        except Exception as e:
            logger.error(f"Search query '{query}' failed: {e}")
            return []
    
    @performance_monitor
    async def batch_scrape_urls(self, urls: List[str], topic: str) -> Dict[str, Any]:
        """Batch scrape URLs using Cloud Tasks for scalability"""
        task_id = f"scrape_{topic}_{datetime.now().timestamp()}"
        
        logger.info(f"Starting GCP batch scraping for {len(urls)} URLs, topic: '{topic}'")
        
        try:
            # Create scraping task
            scraping_task = GCPScrapingTask(
                task_id=task_id,
                topic=topic,
                urls=urls,
                created_at=datetime.now(timezone.utc).isoformat(),
                status="processing"
            )
            
            # For large URL sets, use Cloud Tasks
            if len(urls) > 20:
                return await self._batch_scrape_with_cloud_tasks(scraping_task)
            else:
                return await self._batch_scrape_direct(scraping_task)
                
        except Exception as e:
            logger.error(f"Batch scraping failed for topic '{topic}': {e}")
            return {
                "success": False,
                "documents": [],
                "error": str(e),
                "task_id": task_id
            }
    
    async def _batch_scrape_with_cloud_tasks(self, task: GCPScrapingTask) -> Dict[str, Any]:
        """Use Cloud Tasks for large-scale scraping"""
        try:
            # Split URLs into smaller batches
            batch_size = 10
            url_batches = [
                task.urls[i:i + batch_size] 
                for i in range(0, len(task.urls), batch_size)
            ]
            
            # Create Cloud Tasks for each batch
            task_names = []
            for i, batch_urls in enumerate(url_batches):
                batch_task = {
                    "http_request": {
                        "http_method": tasks_v2.HttpMethod.POST,
                        "url": f"https://{self.region}-{self.project_id}.cloudfunctions.net/scrape-urls",
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({
                            "urls": batch_urls,
                            "topic": task.topic,
                            "batch_id": f"{task.task_id}_batch_{i}",
                            "result_bucket": self.bucket_name
                        }).encode()
                    }
                }
                
                # Create the task
                cloud_task = self.tasks_client.create_task(
                    parent=self.queue_path,
                    task={"http_request": batch_task["http_request"]}
                )
                task_names.append(cloud_task.name)
            
            # Wait for tasks to complete (simplified - in production, use Pub/Sub)
            await asyncio.sleep(30)  # Estimated processing time
            
            # Collect results from GCS
            results = await self._collect_scraping_results(task.task_id)
            
            return {
                "success": True,
                "documents": results.get("documents", []),
                "total_urls": len(task.urls),
                "successful_scrapes": results.get("successful_scrapes", 0),
                "task_id": task.task_id,
                "cloud_tasks": task_names
            }
            
        except Exception as e:
            logger.error(f"Cloud Tasks scraping failed: {e}")
            raise
    
    async def _batch_scrape_direct(self, task: GCPScrapingTask) -> Dict[str, Any]:
        """Direct scraping for smaller URL sets"""
        try:
            # Validate URLs first
            validation_results = await self._validate_urls_parallel(task.urls)
            
            # Filter accessible URLs
            accessible_urls = [
                result["url"] for result in validation_results 
                if result["is_accessible"] and result.get("is_html", False)
            ]
            
            if not accessible_urls:
                return {
                    "success": False,
                    "documents": [],
                    "error": "No accessible URLs found"
                }
            
            # Scrape content with increased concurrency
            scraping_results = await self._scrape_urls_parallel(accessible_urls, task.topic)
            
            # Filter high-quality results
            quality_documents = self._filter_quality_documents(scraping_results)
            
            # Store results in GCS
            gcs_path = await self._store_scraping_results(task.task_id, {
                "task": task,
                "documents": quality_documents,
                "stats": {
                    "total_urls": len(task.urls),
                    "accessible_urls": len(accessible_urls),
                    "successful_scrapes": len([r for r in scraping_results if r["success"]]),
                    "quality_documents": len(quality_documents)
                }
            })
            
            # Publish completion event
            await self._publish_scraping_event(task.task_id, task.topic, len(quality_documents))
            
            return {
                "success": len(quality_documents) > 0,
                "documents": quality_documents,
                "total_urls": len(task.urls),
                "accessible_urls": len(accessible_urls),
                "successful_scrapes": len([r for r in scraping_results if r["success"]]),
                "quality_documents": len(quality_documents),
                "gcs_result_path": gcs_path
            }
            
        except Exception as e:
            logger.error(f"Direct scraping failed: {e}")
            raise
    
    async def _validate_urls_parallel(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Validate URLs in parallel with GCP monitoring"""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=self.max_concurrent_requests)
        ) as session:
            
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            tasks = [self._validate_single_url(session, semaphore, url) for url in urls]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and format results
            validation_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    validation_results.append({
                        "url": urls[i],
                        "is_accessible": False,
                        "error": str(result)
                    })
                else:
                    validation_results.append(result)
            
            return validation_results
    
    async def _validate_single_url(self, session: aiohttp.ClientSession, 
                                 semaphore: asyncio.Semaphore, url: str) -> Dict[str, Any]:
        """Validate single URL with detailed response"""
        async with semaphore:
            try:
                async with session.head(url, allow_redirects=True) as response:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    return {
                        "url": url,
                        "is_accessible": response.status == 200,
                        "is_html": 'text/html' in content_type,
                        "status_code": response.status,
                        "content_type": content_type
                    }
                    
            except Exception as e:
                return {
                    "url": url,
                    "is_accessible": False,
                    "is_html": False,
                    "error": str(e)
                }
    
    async def _scrape_urls_parallel(self, urls: List[str], topic: str) -> List[Dict[str, Any]]:
        """Scrape URLs in parallel with monitoring"""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            connector=aiohttp.TCPConnector(limit=self.max_concurrent_requests)
        ) as session:
            
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            tasks = [
                self._scrape_single_url_enhanced(session, semaphore, url, topic) 
                for url in urls
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            scraping_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    scraping_results.append({
                        "url": urls[i],
                        "success": False,
                        "error": str(result)
                    })
                else:
                    scraping_results.append(result)
            
            return scraping_results
    
    async def _scrape_single_url_enhanced(self, session: aiohttp.ClientSession,
                                        semaphore: asyncio.Semaphore, url: str, 
                                        topic: str) -> Dict[str, Any]:
        """Enhanced single URL scraping with GCP monitoring"""
        async with semaphore:
            try:
                # Record scraping metrics
                start_time = datetime.now()
                
                async with session.get(url) as response:
                    if response.status != 200:
                        return {
                            "url": url,
                            "success": False,
                            "error": f"HTTP {response.status}"
                        }
                    
                    html_content = await response.text()
                    
                    # Extract content
                    processed_content = self.content_processor.extract_main_content(html_content)
                    
                    if not processed_content or len(processed_content.strip()) < self.min_word_count:
                        return {
                            "url": url,
                            "success": False,
                            "error": "Insufficient content extracted"
                        }
                    
                    # Extract title
                    title = (self.content_processor.extract_title(html_content) or 
                           f"Document from {url}")
                    
                    # Calculate quality and relevance
                    quality_score = await self._calculate_content_quality(processed_content, topic)
                    
                    # Content classification
                    layer, factor, segment = self._classify_content_enhanced(processed_content, topic)
                    
                    # Processing time
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    # Record metrics to Cloud Monitoring
                    await self._record_scraping_metrics(url, processing_time, quality_score)
                    
                    return {
                        "url": url,
                        "title": title,
                        "content": processed_content,
                        "quality_score": quality_score,
                        "content_quality_score": quality_score,  # Compatibility
                        "layer": layer,
                        "factor": factor,
                        "segment": segment,
                        "word_count": len(processed_content.split()),
                        "extracted_at": datetime.now(timezone.utc).isoformat(),
                        "processing_time_seconds": processing_time,
                        "success": True
                    }
                    
            except Exception as e:
                logger.error(f"Failed to scrape URL {url}: {e}")
                return {
                    "url": url,
                    "success": False,
                    "error": str(e)
                }
    
    def _filter_quality_documents(self, scraping_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter documents based on quality criteria"""
        quality_documents = []
        
        for result in scraping_results:
            if (result.get("success", False) and 
                result.get("quality_score", 0) >= self.min_quality_score and
                result.get("word_count", 0) >= self.min_word_count):
                quality_documents.append(result)
        
        return quality_documents
    
    async def _calculate_content_quality(self, content: str, topic: str) -> float:
        """Enhanced content quality calculation"""
        try:
            # Keyword relevance
            topic_words = set(topic.lower().split())
            content_words = set(content.lower().split())
            keyword_overlap = len(topic_words.intersection(content_words))
            relevance_score = min(1.0, (keyword_overlap / len(topic_words)) * 2) if topic_words else 0
            
            # Content structure analysis
            word_count = len(content.split())
            sentence_count = len([s for s in content.split('.') if s.strip()])
            paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
            
            # Quality metrics
            length_score = min(1.0, word_count / 800)  # Optimal ~800 words
            structure_score = min(1.0, sentence_count / 25)  # ~25 sentences
            organization_score = min(1.0, paragraph_count / 8)  # ~8 paragraphs
            
            # Combined score with weights
            final_score = (
                relevance_score * 0.4 +
                length_score * 0.3 +
                structure_score * 0.2 +
                organization_score * 0.1
            )
            
            return round(final_score, 3)
            
        except Exception as e:
            logger.error(f"Failed to calculate content quality: {e}")
            return 0.5  # Default neutral score
    
    def _classify_content_enhanced(self, content: str, topic: str) -> tuple:
        """Enhanced content classification"""
        # Simplified classification - in production, use ML models
        content_lower = content.lower()
        
        # Layer classification
        if any(word in content_lower for word in ['market', 'industry', 'business']):
            layer = "market"
        elif any(word in content_lower for word in ['consumer', 'customer', 'user']):
            layer = "consumer"
        elif any(word in content_lower for word in ['technology', 'tech', 'innovation']):
            layer = "technology"
        else:
            layer = "general"
        
        # Factor classification
        if any(word in content_lower for word in ['growth', 'expansion', 'increase']):
            factor = "growth"
        elif any(word in content_lower for word in ['competition', 'competitive', 'rival']):
            factor = "competition"
        elif any(word in content_lower for word in ['trend', 'forecast', 'prediction']):
            factor = "trends"
        else:
            factor = "general"
        
        # Segment classification
        if any(word in content_lower for word in ['enterprise', 'b2b', 'business']):
            segment = "enterprise"
        elif any(word in content_lower for word in ['consumer', 'retail', 'b2c']):
            segment = "consumer"
        else:
            segment = "general"
        
        return layer, factor, segment
    
    async def _record_scraping_metrics(self, url: str, processing_time: float, quality_score: float):
        """Record scraping metrics to Cloud Monitoring"""
        # Implementation would record custom metrics
        logger.debug(f"Recorded metrics for {url}: {processing_time}s, quality: {quality_score}")
    
    # Additional helper methods with GCP integration
    async def _store_collected_urls(self, task_id: str, topic: str, urls: List[str], 
                                  queries: List[str]):
        """Store collected URLs in GCS"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob_path = f"collections/{task_id}/urls.json"
            blob = bucket.blob(blob_path)
            
            data = {
                "task_id": task_id,
                "topic": topic,
                "urls": urls,
                "search_queries": queries,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "url_count": len(urls)
            }
            
            blob.upload_from_string(
                json.dumps(data, indent=2),
                content_type='application/json'
            )
            
            logger.info(f"✅ Stored collected URLs in GCS: gs://{self.bucket_name}/{blob_path}")
            
        except Exception as e:
            logger.error(f"Failed to store collected URLs: {e}")
    
    async def _store_scraping_results(self, task_id: str, results: Dict[str, Any]) -> str:
        """Store scraping results in GCS"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob_path = f"scraping/{task_id}/results.json"
            blob = bucket.blob(blob_path)
            
            blob.upload_from_string(
                json.dumps(results, indent=2, default=str),
                content_type='application/json'
            )
            
            gcs_path = f"gs://{self.bucket_name}/{blob_path}"
            logger.info(f"✅ Stored scraping results in GCS: {gcs_path}")
            return gcs_path
            
        except Exception as e:
            logger.error(f"Failed to store scraping results: {e}")
            return ""
    
    async def _collect_scraping_results(self, task_id: str) -> Dict[str, Any]:
        """Collect scraping results from GCS"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob_path = f"scraping/{task_id}/results.json"
            blob = bucket.blob(blob_path)
            
            if blob.exists():
                content = blob.download_as_text()
                return json.loads(content)
            else:
                return {"documents": [], "successful_scrapes": 0}
                
        except Exception as e:
            logger.error(f"Failed to collect scraping results: {e}")
            return {"documents": [], "successful_scrapes": 0}
    
    async def _publish_collection_event(self, task_id: str, topic: str, url_count: int, 
                                      error: str = None):
        """Publish URL collection event to Pub/Sub"""
        try:
            event_data = {
                "task_id": task_id,
                "topic": topic,
                "url_count": url_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "error" if error else "success"
            }
            
            if error:
                event_data["error"] = error
            
            # Publish to Pub/Sub
            future = self.publisher.publish(
                self.topic_path,
                json.dumps(event_data).encode("utf-8")
            )
            
            future.result()  # Wait for publish to complete
            logger.info(f"✅ Published collection event for task {task_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish collection event: {e}")
    
    async def _publish_scraping_event(self, task_id: str, topic: str, document_count: int):
        """Publish scraping completion event"""
        try:
            event_data = {
                "task_id": task_id,
                "topic": topic,
                "document_count": document_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "completed"
            }
            
            future = self.publisher.publish(
                self.topic_path,
                json.dumps(event_data).encode("utf-8")
            )
            
            future.result()
            logger.info(f"✅ Published scraping event for task {task_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish scraping event: {e}")
    
    # Helper methods
    def _generate_search_queries(self, topic: str) -> List[str]:
        """Generate comprehensive search queries"""
        base_queries = [
            f"{topic} market analysis 2024 2025",
            f"{topic} industry trends report",
            f"{topic} consumer behavior research",
            f"{topic} competitive landscape analysis",
            f"{topic} market research insights",
            f"{topic} business intelligence report",
            f"{topic} strategic market analysis",
            f"{topic} market opportunities forecast"
        ]
        
        # Add topic-specific variations
        topic_words = topic.lower().split()
        for word in topic_words:
            base_queries.extend([
                f"{word} market size analysis",
                f"{word} industry forecast 2025",
                f"{word} competitive intelligence"
            ])
        
        return base_queries[:12]  # Limit to 12 queries
    
    def _is_valid_url(self, url: str) -> bool:
        """Enhanced URL validation"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except:
            return False

# Export for use in other modules
__all__ = ['GCPURLOrchestrator', 'GCPScrapingTask', 'ScrapedContentProcessor', 'ResearchAgent']
