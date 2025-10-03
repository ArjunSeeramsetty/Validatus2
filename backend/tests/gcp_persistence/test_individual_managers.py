"""
Individual GCP Manager Tests
Tests each GCP service manager in isolation
"""
import asyncio
import pytest
from datetime import datetime
from typing import Dict, Any

from app.services.gcp_storage_manager import GCPStorageManager
from app.services.gcp_sql_manager import GCPSQLManager
from app.services.gcp_redis_manager import GCPRedisManager
from app.services.gcp_vector_manager import GCPVectorManager
from app.services.gcp_spanner_manager import GCPSpannerManager
from app.models.topic_models import TopicCreateRequest, AnalysisType, TopicStatus

class TestGCPStorageManager:
    """Test Cloud Storage operations"""
    
    @pytest.fixture
    async def storage_manager(self):
        """Initialize storage manager"""
        manager = GCPStorageManager()
        yield manager
    
    async def test_store_and_retrieve_content(self, storage_manager):
        """Test storing and retrieving scraped content"""
        
        session_id = "test_storage_session"
        test_url = "https://example.com/test-page"
        test_content = "<html><body><h1>Test Page</h1><p>This is test content.</p></body></html>"
        
        # Store content
        gcs_path = await storage_manager.store_scraped_content(
            session_id, test_url, test_content, {"title": "Test Page"}
        )
        
        assert gcs_path.startswith("gs://")
        assert session_id in gcs_path
        
        # Retrieve content
        retrieved_content = await storage_manager.get_scraped_content(gcs_path)
        assert retrieved_content == test_content
    
    async def test_store_embeddings(self, storage_manager):
        """Test storing embeddings data"""
        
        session_id = "test_embeddings_session"
        embeddings_data = {
            "chunk_1": {
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"chunk_index": 1, "word_count": 100}
            },
            "chunk_2": {
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {"chunk_index": 2, "word_count": 150}
            }
        }
        
        gcs_path = await storage_manager.store_embeddings_data(session_id, embeddings_data)
        
        assert gcs_path.startswith("gs://")
        assert "embeddings" in gcs_path
        assert session_id in gcs_path
    
    async def test_store_analysis_report(self, storage_manager):
        """Test storing analysis reports"""
        
        session_id = "test_report_session"
        analysis_id = "test_analysis_123"
        report_content = "<html><body><h1>Analysis Report</h1><p>Test report content</p></body></html>"
        
        gcs_path = await storage_manager.store_analysis_report(
            session_id, analysis_id, report_content, "html"
        )
        
        assert gcs_path.startswith("gs://")
        assert "reports" in gcs_path
        assert session_id in gcs_path
        assert analysis_id in gcs_path

class TestGCPSQLManager:
    """Test Cloud SQL operations"""
    
    @pytest.fixture
    async def sql_manager(self):
        """Initialize SQL manager"""
        manager = GCPSQLManager()
        await manager.initialize()
        yield manager
        await manager.close()
    
    async def test_create_and_retrieve_topic(self, sql_manager):
        """Test creating and retrieving topics"""
        
        request = TopicCreateRequest(
            topic="Test SQL Topic",
            description="Testing SQL operations",
            search_queries=["test query"],
            initial_urls=["https://example.com/test"],
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id="test_user_sql",
            metadata={"test": True}
        )
        
        # Create topic
        topic_response = await sql_manager.create_topic(request)
        
        assert topic_response is not None
        assert topic_response.topic == request.topic
        assert topic_response.user_id == request.user_id
        
        session_id = topic_response.session_id
        
        # Retrieve topic
        retrieved_topic = await sql_manager.get_topic(session_id, request.user_id)
        
        assert retrieved_topic is not None
        assert retrieved_topic.session_id == session_id
        assert retrieved_topic.topic == request.topic
        
        # Cleanup
        async with sql_manager.get_connection() as conn:
            await conn.execute("DELETE FROM topics WHERE session_id = $1", session_id)
    
    async def test_list_topics(self, sql_manager):
        """Test listing topics with pagination"""
        
        user_id = "test_list_user"
        
        # Create multiple topics
        topics_created = []
        for i in range(5):
            request = TopicCreateRequest(
                topic=f"List Test Topic {i}",
                description=f"Description {i}",
                search_queries=[f"query {i}"],
                initial_urls=[],
                analysis_type=AnalysisType.COMPREHENSIVE,
                user_id=user_id,
                metadata={"index": i}
            )
            
            topic = await sql_manager.create_topic(request)
            topics_created.append(topic.session_id)
        
        # Test listing
        topics_list = await sql_manager.list_topics(user_id, page=1, page_size=3)
        
        assert topics_list.total >= 5
        assert len(topics_list.topics) == 3
        assert topics_list.has_next is True
        
        # Cleanup
        async with sql_manager.get_connection() as conn:
            for session_id in topics_created:
                await conn.execute("DELETE FROM topics WHERE session_id = $1", session_id)
    
    async def test_store_and_update_urls(self, sql_manager):
        """Test URL storage and updates"""
        
        session_id = "test_urls_session"
        user_id = "test_urls_user"
        
        # Create topic first
        request = TopicCreateRequest(
            topic="URL Test Topic",
            description="Testing URL operations",
            search_queries=[],
            initial_urls=[],
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id=user_id,
            metadata={}
        )
        
        topic = await sql_manager.create_topic(request)
        
        # Store URLs
        test_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        stored_count = await sql_manager.store_urls(session_id, test_urls, "test")
        assert stored_count == len(test_urls)
        
        # Get URLs for scraping
        urls_to_scrape = await sql_manager.get_urls_for_scraping(session_id, "pending", 10)
        assert len(urls_to_scrape) == len(test_urls)
        
        # Update URL content
        url = test_urls[0]
        content_path = "gs://bucket/test/path"
        metadata = {
            "title": "Test Page",
            "word_count": 500,
            "quality_score": 0.8
        }
        
        success = await sql_manager.update_url_content(session_id, url, content_path, metadata)
        assert success is True
        
        # Cleanup
        async with sql_manager.get_connection() as conn:
            await conn.execute("DELETE FROM topics WHERE session_id = $1", session_id)

class TestGCPRedisManager:
    """Test Redis operations"""
    
    @pytest.fixture
    async def redis_manager(self):
        """Initialize Redis manager"""
        manager = GCPRedisManager()
        await manager.initialize()
        yield manager
        await manager.close()
    
    async def test_session_caching(self, redis_manager):
        """Test session data caching"""
        
        session_id = "test_redis_session"
        session_data = {
            "session_id": session_id,
            "user_id": "test_redis_user",
            "topic": "Redis Test Topic",
            "status": "CREATED",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Cache session data
        await redis_manager.cache_session_data(session_id, session_data, ttl=3600)
        
        # Retrieve session data
        retrieved_data = await redis_manager.get_session_data(session_id)
        assert retrieved_data is not None
        assert retrieved_data["user_id"] == session_data["user_id"]
        
        # Extend TTL
        await redis_manager.extend_session_ttl(session_id, 7200)
    
    async def test_workflow_progress(self, redis_manager):
        """Test workflow progress tracking"""
        
        session_id = "test_workflow_session"
        progress_data = {
            "stage": "URL_COLLECTION",
            "percentage": 50,
            "message": "Collecting URLs from search",
            "urls_found": 25
        }
        
        # Cache workflow progress
        await redis_manager.cache_workflow_progress(session_id, "URL_COLLECTION", progress_data)
        
        # Retrieve workflow progress
        progress = await redis_manager.get_workflow_progress(session_id)
        assert progress is not None
        assert progress["current_stage"] == "URL_COLLECTION"
        assert "progress_data" in progress
    
    async def test_url_queue_operations(self, redis_manager):
        """Test URL queue operations"""
        
        session_id = "test_queue_session"
        test_urls = [
            "https://example.com/queue1",
            "https://example.com/queue2",
            "https://example.com/queue3"
        ]
        
        # Queue URLs
        await redis_manager.queue_urls_for_processing(session_id, test_urls)
        
        # Check queue length
        queue_length = await redis_manager.get_queue_length(session_id)
        assert queue_length == len(test_urls)
        
        # Process URLs
        processed_urls = []
        while True:
            url = await redis_manager.get_next_url_to_process(session_id)
            if not url:
                break
            processed_urls.append(url)
        
        assert len(processed_urls) == len(test_urls)
        assert set(processed_urls) == set(test_urls)
    
    async def test_user_activity_tracking(self, redis_manager):
        """Test user activity tracking"""
        
        user_id = "test_activity_user"
        
        # Track activities
        activities = [
            {"type": "topic_created", "data": {"topic": "Activity Test Topic"}},
            {"type": "workflow_started", "data": {"session_id": "test_123"}},
            {"type": "analysis_completed", "data": {"confidence": 0.92}}
        ]
        
        for activity in activities:
            await redis_manager.track_user_activity(
                user_id, activity["type"], activity["data"]
            )
        
        # Get recent activities
        recent_activities = await redis_manager.get_recent_user_activity(user_id, hours=1)
        
        assert len(recent_activities) >= len(activities)
        
        # Verify activity types
        activity_types = [activity["type"] for activity in recent_activities]
        for activity in activities:
            assert activity["type"] in activity_types
    
    async def test_rate_limiting(self, redis_manager):
        """Test rate limiting functionality"""
        
        user_id = "test_rate_limit_user"
        action = "test_action"
        
        # Test rate limiting (5 requests per hour)
        for i in range(3):
            allowed = await redis_manager.check_rate_limit(user_id, action, limit=5, window_seconds=3600)
            assert allowed is True
        
        # Should still be within limit
        allowed = await redis_manager.check_rate_limit(user_id, action, limit=5, window_seconds=3600)
        assert allowed is True
    
    async def test_health_check(self, redis_manager):
        """Test Redis health check"""
        
        health_status = await redis_manager.health_check()
        
        assert "status" in health_status
        assert "response_time_ms" in health_status
        assert health_status["status"] in ["healthy", "unhealthy"]

class TestGCPVectorManager:
    """Test Vertex AI Vector Search operations"""
    
    @pytest.fixture
    async def vector_manager(self):
        """Initialize vector manager"""
        manager = GCPVectorManager()
        await manager.initialize()
        yield manager
        await manager.close()
    
    async def test_create_vector_index(self, vector_manager):
        """Test creating vector index"""
        
        session_id = "test_vector_session"
        
        # Create vector index
        result = await vector_manager.create_topic_vector_index(session_id)
        
        assert result["status"] in ["completed", "failed"]
        assert "embedding_count" in result
        
        if result["status"] == "completed":
            assert result["embedding_count"] >= 0
            assert "index_id" in result
    
    async def test_similarity_search(self, vector_manager):
        """Test similarity search"""
        
        session_id = "test_search_session"
        query = "test search query"
        
        # Perform similarity search
        results = await vector_manager.similarity_search(session_id, query, top_k=5)
        
        assert isinstance(results, list)
        # Results might be empty in test environment
    
    async def test_health_check(self, vector_manager):
        """Test vector manager health check"""
        
        health_status = await vector_manager.health_check()
        
        assert "status" in health_status
        assert "vector_search_location" in health_status
        assert "embedding_model" in health_status

class TestGCPSpannerManager:
    """Test Cloud Spanner operations"""
    
    @pytest.fixture
    async def spanner_manager(self):
        """Initialize Spanner manager"""
        manager = GCPSpannerManager()
        await manager.initialize()
        yield manager
        await manager.close()
    
    async def test_store_analysis_results(self, spanner_manager):
        """Test storing analysis results"""
        
        session_id = "test_spanner_session"
        analysis_result = {
            "analysis_id": "test_analysis_123",
            "overall_score": 0.85,
            "confidence_score": 0.92,
            "factor_scores": {
                "market_potential": 0.88,
                "competitive_advantage": 0.82
            },
            "processing_time_ms": 12000
        }
        
        # Store analysis results
        success = await spanner_manager.store_analysis_results(session_id, analysis_result)
        assert success is True
    
    async def test_get_user_analytics(self, spanner_manager):
        """Test getting user analytics"""
        
        user_id = "test_analytics_user"
        
        # Get user analytics
        analytics = await spanner_manager.get_user_analytics(user_id, days=30)
        
        assert "user_id" in analytics
        assert "period_days" in analytics
        assert "topics_created" in analytics
    
    async def test_get_market_intelligence(self, spanner_manager):
        """Test getting market intelligence"""
        
        market_segment = "Technology"
        
        # Get market intelligence
        intelligence = await spanner_manager.get_market_intelligence(market_segment, 90)
        
        assert "market_segment" in intelligence
        assert "time_period_days" in intelligence
        assert "total_analyses" in intelligence
    
    async def test_get_cross_topic_insights(self, spanner_manager):
        """Test getting cross-topic insights"""
        
        user_id = "test_insights_user"
        
        # Get cross-topic insights
        insights = await spanner_manager.get_cross_topic_insights(user_id, ["pattern_recognition"])
        
        assert isinstance(insights, list)
        # Insights might be empty in test environment
    
    async def test_health_check(self, spanner_manager):
        """Test Spanner health check"""
        
        health_status = await spanner_manager.health_check()
        
        assert "status" in health_status
        assert "spanner_instance" in health_status
        assert "spanner_database" in health_status

if __name__ == "__main__":
    # Run individual manager tests
    asyncio.run(test_integration_end_to_end())
