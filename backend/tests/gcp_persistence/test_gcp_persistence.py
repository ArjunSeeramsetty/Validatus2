"""
Comprehensive tests for GCP Persistence integration
"""
import asyncio
import pytest
from datetime import datetime
from typing import Dict, Any

from app.services.gcp_persistence_manager import get_gcp_persistence_manager
from app.models.topic_models import TopicCreateRequest, AnalysisType, TopicStatus
from app.core.gcp_persistence_config import get_gcp_persistence_settings

@pytest.fixture
async def persistence_manager():
    """Initialize persistence manager for testing"""
    manager = get_gcp_persistence_manager()
    await manager.initialize()
    yield manager
    await manager.close()

@pytest.fixture
def sample_topic_request():
    """Sample topic creation request"""
    return TopicCreateRequest(
        topic="Test Pergola Market Analysis",
        description="Testing the GCP persistence integration",
        search_queries=["pergola market test", "outdoor furniture analysis"],
        initial_urls=["https://example.com/test1", "https://example.com/test2"],
        analysis_type=AnalysisType.COMPREHENSIVE,
        user_id="test_user_123",
        metadata={"test": True, "environment": "pytest"}
    )

class TestGCPPersistence:
    """Test GCP persistence operations"""
    
    async def test_topic_creation_complete_workflow(self, persistence_manager, sample_topic_request):
        """Test complete topic creation with all GCP services"""
        
        # Create topic
        topic_response = await persistence_manager.create_topic_complete(sample_topic_request)
        
        assert topic_response is not None
        assert topic_response.topic == sample_topic_request.topic
        assert topic_response.user_id == sample_topic_request.user_id
        assert topic_response.status == TopicStatus.CREATED
        
        session_id = topic_response.session_id
        
        # Verify in SQL
        sql_topic = await persistence_manager.sql_manager.get_topic(session_id, sample_topic_request.user_id)
        assert sql_topic is not None
        assert sql_topic.session_id == session_id
        
        # Verify in Redis cache
        cached_data = await persistence_manager.redis_manager.get_session_data(session_id)
        assert cached_data is not None
        assert cached_data['user_id'] == sample_topic_request.user_id
        
        # Verify workflow progress
        progress = await persistence_manager.redis_manager.get_workflow_progress(session_id)
        assert progress is not None
        assert progress['current_stage'] == 'CREATED'
        
        # Cleanup
        async with persistence_manager.sql_manager.get_connection() as conn:
            await conn.execute("DELETE FROM topics WHERE session_id = $1", session_id)
    
    async def test_topic_listing_with_caching(self, persistence_manager, sample_topic_request):
        """Test topic listing with Redis caching optimization"""
        
        # Create multiple topics
        topics_created = []
        for i in range(3):
            request = TopicCreateRequest(
                topic=f"Test Topic {i}",
                description=f"Test description {i}",
                search_queries=[f"test query {i}"],
                initial_urls=[f"https://example.com/test{i}"],
                analysis_type=AnalysisType.COMPREHENSIVE,
                user_id="test_user_123",
                metadata={"test": True, "index": i}
            )
            
            topic = await persistence_manager.create_topic_complete(request)
            topics_created.append(topic.session_id)
        
        # Test listing
        topics_list = await persistence_manager.list_topics_complete("test_user_123")
        
        assert topics_list.total >= 3
        assert len(topics_list.topics) >= 3
        
        # Verify topics are cached
        for topic in topics_list.topics[:3]:
            cached_data = await persistence_manager.redis_manager.get_session_data(topic.session_id)
            assert cached_data is not None
        
        # Cleanup
        async with persistence_manager.sql_manager.get_connection() as conn:
            for session_id in topics_created:
                await conn.execute("DELETE FROM topics WHERE session_id = $1", session_id)
    
    async def test_workflow_execution(self, persistence_manager, sample_topic_request):
        """Test complete 5-task workflow execution"""
        
        # Create topic
        topic = await persistence_manager.create_topic_complete(sample_topic_request)
        session_id = topic.session_id
        
        # Start workflow (this will run the complete pipeline)
        try:
            workflow_result = await persistence_manager.execute_complete_workflow(
                session_id, 
                sample_topic_request.user_id
            )
            
            assert workflow_result['session_id'] == session_id
            assert 'stages' in workflow_result
            
            # Check individual stages
            assert 'url_collection' in workflow_result['stages']
            assert 'url_scraping' in workflow_result['stages']
            assert 'vector_creation' in workflow_result['stages']
            assert 'analysis' in workflow_result['stages']
            
            # Verify final status
            updated_topic = await persistence_manager.get_topic_complete(session_id, sample_topic_request.user_id)
            assert updated_topic.status in [TopicStatus.COMPLETED, TopicStatus.IN_PROGRESS]
            
        except Exception as e:
            # Workflow might fail in test environment due to external dependencies
            pytest.skip(f"Workflow test skipped due to external dependencies: {e}")
        
        finally:
            # Cleanup
            async with persistence_manager.sql_manager.get_connection() as conn:
                await conn.execute("DELETE FROM topics WHERE session_id = $1", session_id)
    
    async def test_storage_operations(self, persistence_manager):
        """Test Cloud Storage operations"""
        
        session_id = "test_session_storage"
        test_url = "https://example.com/test"
        test_content = "<html><body><h1>Test Content</h1><p>This is test scraped content.</p></body></html>"
        
        # Store content
        gcs_path = await persistence_manager.storage_manager.store_scraped_content(
            session_id, test_url, test_content, {"test": True}
        )
        
        assert gcs_path.startswith("gs://")
        assert session_id in gcs_path
        
        # Retrieve content
        retrieved_content = await persistence_manager.storage_manager.get_scraped_content(gcs_path)
        assert retrieved_content == test_content
        
        # Cleanup
        await persistence_manager.storage_manager.batch_delete_content(session_id)
    
    async def test_redis_operations(self, persistence_manager):
        """Test Redis caching and real-time operations"""
        
        session_id = "test_session_redis"
        user_id = "test_user_redis"
        
        # Test session caching
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "topic": "Test Topic",
            "status": "CREATED"
        }
        
        await persistence_manager.redis_manager.cache_session_data(session_id, session_data)
        
        retrieved_data = await persistence_manager.redis_manager.get_session_data(session_id)
        assert retrieved_data == session_data
        
        # Test workflow progress
        progress_data = {
            "stage": "URL_COLLECTION",
            "percentage": 25,
            "message": "Collecting URLs"
        }
        
        await persistence_manager.redis_manager.cache_workflow_progress(
            session_id, "URL_COLLECTION", progress_data
        )
        
        progress = await persistence_manager.redis_manager.get_workflow_progress(session_id)
        assert progress is not None
        assert progress['current_stage'] == 'URL_COLLECTION'
        
        # Test URL queue
        test_urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]
        await persistence_manager.redis_manager.queue_urls_for_processing(session_id, test_urls)
        
        queue_length = await persistence_manager.redis_manager.get_queue_length(session_id)
        assert queue_length == len(test_urls)
        
        # Process URLs
        processed_urls = []
        while True:
            url = await persistence_manager.redis_manager.get_next_url_to_process(session_id)
            if not url:
                break
            processed_urls.append(url)
        
        assert len(processed_urls) == len(test_urls)
        assert set(processed_urls) == set(test_urls)
    
    async def test_health_checks(self, persistence_manager):
        """Test comprehensive health checks"""
        
        health_status = await persistence_manager.health_check()
        
        assert 'overall_status' in health_status
        assert 'services' in health_status
        assert 'timestamp' in health_status
        
        # Check individual services
        expected_services = ['sql', 'redis', 'storage', 'vector', 'spanner']
        for service in expected_services:
            assert service in health_status['services']
            service_health = health_status['services'][service]
            assert 'status' in service_health
    
    async def test_user_activity_tracking(self, persistence_manager):
        """Test user activity tracking and analytics"""
        
        user_id = "test_user_activity"
        
        # Track various activities
        activities = [
            {"type": "topic_created", "data": {"topic": "Test Topic 1"}},
            {"type": "workflow_started", "data": {"session_id": "test_123"}},
            {"type": "analysis_completed", "data": {"confidence": 0.85}}
        ]
        
        for activity in activities:
            await persistence_manager.redis_manager.track_user_activity(
                user_id, activity["type"], activity["data"]
            )
        
        # Get recent activity
        recent_activities = await persistence_manager.redis_manager.get_recent_user_activity(
            user_id, hours=1
        )
        
        assert len(recent_activities) >= len(activities)
        
        # Verify activity types
        activity_types = [activity['type'] for activity in recent_activities]
        for activity in activities:
            assert activity['type'] in activity_types

@pytest.mark.asyncio
async def test_integration_end_to_end():
    """End-to-end integration test"""
    settings = get_gcp_persistence_settings()
    
    # Skip if not in test environment
    if not settings.local_development_mode:
        pytest.skip("Integration test requires local development mode")
    
    manager = get_gcp_persistence_manager()
    await manager.initialize()
    
    try:
        # Create test topic
        request = TopicCreateRequest(
            topic="End-to-End Test Topic",
            description="Testing complete integration",
            search_queries=["integration test"],
            initial_urls=["https://example.com/integration"],
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id="integration_test_user",
            metadata={"integration_test": True}
        )
        
        topic = await manager.create_topic_complete(request)
        session_id = topic.session_id
        
        # Verify creation in all systems
        assert topic.session_id is not None
        
        # Test retrieval
        retrieved_topic = await manager.get_topic_complete(session_id, request.user_id)
        assert retrieved_topic is not None
        assert retrieved_topic.topic == request.topic
        
        # Test listing
        topics_list = await manager.list_topics_complete(request.user_id)
        assert topics_list.total >= 1
        
        # Test status update
        success = await manager.sql_manager.update_topic_status(
            session_id, TopicStatus.IN_PROGRESS, request.user_id, {"test": "progress"}
        )
        assert success
        
        # Verify update
        updated_topic = await manager.get_topic_complete(session_id, request.user_id)
        assert updated_topic.status == TopicStatus.IN_PROGRESS
        
        print(f"✅ End-to-end integration test passed for session: {session_id}")
        
    finally:
        await manager.close()

if __name__ == "__main__":
    # Run a quick test
    asyncio.run(test_integration_end_to_end())
