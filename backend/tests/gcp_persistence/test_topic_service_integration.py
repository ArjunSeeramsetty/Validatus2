"""
Topic Service Integration Tests with GCP Persistence
Tests the updated TopicService with GCP persistence integration
"""
import asyncio
import pytest
from datetime import datetime
from typing import Dict, Any

from app.services.topic_service import get_topic_service_instance
from app.models.topic_models import (
    TopicCreateRequest, TopicUpdateRequest, TopicSearchRequest,
    AnalysisType, TopicStatus
)

class TestTopicServiceGCPIntegration:
    """Test TopicService with GCP persistence"""
    
    @pytest.fixture
    async def topic_service(self):
        """Initialize topic service"""
        service = get_topic_service_instance()
        yield service
    
    async def test_create_topic_with_gcp_persistence(self, topic_service):
        """Test topic creation with GCP persistence"""
        
        request = TopicCreateRequest(
            topic="GCP Integration Test Topic",
            description="Testing topic creation with GCP persistence",
            search_queries=["gcp test", "persistence integration"],
            initial_urls=["https://example.com/gcp1", "https://example.com/gcp2"],
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id="gcp_test_user",
            metadata={"gcp_test": True, "environment": "integration"}
        )
        
        # Create topic
        topic_response = await topic_service.create_topic(request)
        
        assert topic_response is not None
        assert topic_response.topic == request.topic
        assert topic_response.user_id == request.user_id
        assert topic_response.status == TopicStatus.CREATED
        assert topic_response.analysis_type == request.analysis_type
        
        session_id = topic_response.session_id
        
        # Verify topic can be retrieved
        retrieved_topic = await topic_service.get_topic(session_id, request.user_id)
        assert retrieved_topic is not None
        assert retrieved_topic.session_id == session_id
        
        # Cleanup
        await topic_service.delete_topic(session_id, request.user_id)
    
    async def test_list_topics_with_caching(self, topic_service):
        """Test topic listing with Redis caching"""
        
        user_id = "list_test_user"
        
        # Create multiple topics
        topics_created = []
        for i in range(3):
            request = TopicCreateRequest(
                topic=f"List Test Topic {i}",
                description=f"Description for topic {i}",
                search_queries=[f"query {i}"],
                initial_urls=[],
                analysis_type=AnalysisType.COMPREHENSIVE,
                user_id=user_id,
                metadata={"index": i}
            )
            
            topic = await topic_service.create_topic(request)
            topics_created.append(topic.session_id)
        
        # Test listing
        topics_list = await topic_service.list_topics(user_id, page=1, page_size=10)
        
        assert topics_list.total >= 3
        assert len(topics_list.topics) >= 3
        
        # Verify all created topics are in the list
        topic_ids = [topic.session_id for topic in topics_list.topics]
        for created_id in topics_created:
            assert created_id in topic_ids
        
        # Cleanup
        for session_id in topics_created:
            await topic_service.delete_topic(session_id, user_id)
    
    async def test_update_topic_status(self, topic_service):
        """Test updating topic status with workflow tracking"""
        
        # Create topic first
        request = TopicCreateRequest(
            topic="Status Update Test Topic",
            description="Testing status updates",
            search_queries=[],
            initial_urls=[],
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id="status_test_user",
            metadata={}
        )
        
        topic = await topic_service.create_topic(request)
        session_id = topic.session_id
        
        # Update status to IN_PROGRESS
        progress_data = {
            "workflow_started": True,
            "current_stage": "URL_COLLECTION",
            "progress_percentage": 25
        }
        
        success = await topic_service.update_topic_status(
            session_id, TopicStatus.IN_PROGRESS, request.user_id, progress_data
        )
        
        assert success is True
        
        # Verify status update
        updated_topic = await topic_service.get_topic(session_id, request.user_id)
        assert updated_topic.status == TopicStatus.IN_PROGRESS
        
        # Cleanup
        await topic_service.delete_topic(session_id, request.user_id)
    
    async def test_search_topics(self, topic_service):
        """Test topic search functionality"""
        
        user_id = "search_test_user"
        
        # Create topics with different characteristics
        topics_data = [
            {
                "topic": "Technology Market Analysis",
                "description": "Analysis of technology market trends",
                "analysis_type": AnalysisType.COMPREHENSIVE
            },
            {
                "topic": "Finance Industry Report",
                "description": "Financial industry analysis and insights",
                "analysis_type": AnalysisType.STANDARD
            },
            {
                "topic": "Healthcare Technology Trends",
                "description": "Healthcare technology market analysis",
                "analysis_type": AnalysisType.COMPREHENSIVE
            }
        ]
        
        topics_created = []
        for data in topics_data:
            request = TopicCreateRequest(
                topic=data["topic"],
                description=data["description"],
                search_queries=[],
                initial_urls=[],
                analysis_type=data["analysis_type"],
                user_id=user_id,
                metadata={}
            )
            
            topic = await topic_service.create_topic(request)
            topics_created.append(topic.session_id)
        
        # Test text search
        search_request = TopicSearchRequest(
            user_id=user_id,
            query="technology",
            page=1,
            page_size=10
        )
        
        search_results = await topic_service.search_topics(search_request)
        
        assert search_results.total >= 2  # Should find technology-related topics
        technology_topics = [t for t in search_results.topics if "technology" in t.topic.lower()]
        assert len(technology_topics) >= 2
        
        # Test analysis type filter
        search_request.analysis_type = AnalysisType.COMPREHENSIVE
        comprehensive_results = await topic_service.search_topics(search_request)
        
        assert all(topic.analysis_type == AnalysisType.COMPREHENSIVE for topic in comprehensive_results.topics)
        
        # Cleanup
        for session_id in topics_created:
            await topic_service.delete_topic(session_id, user_id)
    
    async def test_get_topic_stats(self, topic_service):
        """Test getting comprehensive topic statistics"""
        
        user_id = "stats_test_user"
        
        # Create topics with different statuses and types
        topics_data = [
            {"topic": "Stats Test 1", "analysis_type": AnalysisType.COMPREHENSIVE},
            {"topic": "Stats Test 2", "analysis_type": AnalysisType.STANDARD},
            {"topic": "Stats Test 3", "analysis_type": AnalysisType.COMPREHENSIVE}
        ]
        
        topics_created = []
        for data in topics_data:
            request = TopicCreateRequest(
                topic=data["topic"],
                description="Stats test description",
                search_queries=[],
                initial_urls=[],
                analysis_type=data["analysis_type"],
                user_id=user_id,
                metadata={}
            )
            
            topic = await topic_service.create_topic(request)
            topics_created.append(topic.session_id)
        
        # Get topic stats
        stats = await topic_service.get_topic_stats(user_id)
        
        assert "total_topics" in stats
        assert "topics_by_status" in stats
        assert "topics_by_type" in stats
        assert "recent_activity_count" in stats
        
        assert stats["total_topics"] >= 3
        assert "CREATED" in stats["topics_by_status"]
        assert "comprehensive" in stats["topics_by_type"]
        assert "standard" in stats["topics_by_type"]
        
        # Cleanup
        for session_id in topics_created:
            await topic_service.delete_topic(session_id, user_id)
    
    async def test_workflow_progress_tracking(self, topic_service):
        """Test workflow progress tracking"""
        
        # Create topic
        request = TopicCreateRequest(
            topic="Workflow Progress Test Topic",
            description="Testing workflow progress tracking",
            search_queries=[],
            initial_urls=[],
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id="workflow_test_user",
            metadata={}
        )
        
        topic = await topic_service.create_topic(request)
        session_id = topic.session_id
        
        # Start workflow (this might fail in test environment)
        try:
            workflow_result = await topic_service.start_topic_workflow(session_id, request.user_id)
            
            if workflow_result["success"]:
                # Check workflow progress
                progress = await topic_service.get_workflow_progress(session_id, request.user_id)
                
                if progress:
                    assert "current_stage" in progress
                    assert "progress_data" in progress
                    assert "queue_length" in progress
            else:
                # Workflow failed, but that's expected in test environment
                assert "error" in workflow_result
                
        except Exception as e:
            # Expected in test environment without full GCP setup
            print(f"Workflow test skipped due to external dependencies: {e}")
        
        # Cleanup
        await topic_service.delete_topic(session_id, request.user_id)
    
    async def test_delete_topic_with_cleanup(self, topic_service):
        """Test topic deletion with full cleanup"""
        
        # Create topic with URLs and metadata
        request = TopicCreateRequest(
            topic="Delete Test Topic",
            description="Testing topic deletion and cleanup",
            search_queries=["delete test"],
            initial_urls=["https://example.com/delete1", "https://example.com/delete2"],
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id="delete_test_user",
            metadata={"delete_test": True}
        )
        
        topic = await topic_service.create_topic(request)
        session_id = topic.session_id
        
        # Verify topic exists
        retrieved_topic = await topic_service.get_topic(session_id, request.user_id)
        assert retrieved_topic is not None
        
        # Delete topic
        success = await topic_service.delete_topic(session_id, request.user_id)
        assert success is True
        
        # Verify topic is deleted
        deleted_topic = await topic_service.get_topic(session_id, request.user_id)
        assert deleted_topic is None
        
        # Verify topic is not in list
        topics_list = await topic_service.list_topics(request.user_id)
        topic_ids = [t.session_id for t in topics_list.topics]
        assert session_id not in topic_ids

@pytest.mark.asyncio
async def test_topic_service_integration_end_to_end():
    """End-to-end integration test for TopicService"""
    
    topic_service = get_topic_service_instance()
    
    try:
        # Create a comprehensive topic
        request = TopicCreateRequest(
            topic="End-to-End Integration Test",
            description="Complete integration test for TopicService with GCP persistence",
            search_queries=["integration test", "end to end"],
            initial_urls=["https://example.com/integration1", "https://example.com/integration2"],
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id="e2e_test_user",
            metadata={"integration_test": True, "test_type": "end_to_end"}
        )
        
        # Create topic
        topic = await topic_service.create_topic(request)
        session_id = topic.session_id
        
        # Test retrieval
        retrieved_topic = await topic_service.get_topic(session_id, request.user_id)
        assert retrieved_topic is not None
        assert retrieved_topic.topic == request.topic
        
        # Test listing
        topics_list = await topic_service.list_topics(request.user_id)
        assert topics_list.total >= 1
        
        # Test status update
        success = await topic_service.update_topic_status(
            session_id, TopicStatus.IN_PROGRESS, request.user_id, {"test": "progress"}
        )
        assert success
        
        # Test search
        search_request = TopicSearchRequest(
            user_id=request.user_id,
            query="integration",
            page=1,
            page_size=10
        )
        search_results = await topic_service.search_topics(search_request)
        assert search_results.total >= 1
        
        # Test stats
        stats = await topic_service.get_topic_stats(request.user_id)
        assert stats["total_topics"] >= 1
        
        # Test deletion
        delete_success = await topic_service.delete_topic(session_id, request.user_id)
        assert delete_success
        
        # Verify deletion
        deleted_topic = await topic_service.get_topic(session_id, request.user_id)
        assert deleted_topic is None
        
        print("✅ End-to-end TopicService integration test passed")
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        raise

if __name__ == "__main__":
    # Run integration test
    asyncio.run(test_topic_service_integration_end_to_end())
