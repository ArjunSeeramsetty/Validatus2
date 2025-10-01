#!/usr/bin/env python3
"""
Test script to verify TopicService local fallback
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.topic_service import TopicService
from app.models.topic_models import TopicCreateRequest

async def test_topic_service():
    """Test TopicService with local fallback"""
    print("Testing TopicService initialization...")
    
    # Set local development mode
    os.environ['LOCAL_DEVELOPMENT_MODE'] = 'true'
    
    try:
        # Create TopicService instance
        topic_service = TopicService()
        
        print(f"Using local fallback: {topic_service._use_local_fallback}")
        print(f"Firestore client: {topic_service.db}")
        
        if topic_service._use_local_fallback:
            print("SUCCESS: TopicService is using local fallback")
        else:
            print("WARNING: TopicService is not using local fallback")
        
        # Test topic creation
        print("\nTesting topic creation...")
        request = TopicCreateRequest(
            topic="Test Topic",
            description="Test Description",
            search_queries=["test query"],
            initial_urls=["https://example.com"],
            analysis_type="comprehensive",
            user_id="test_user_123"
        )
        
        topic = await topic_service.create_topic(request)
        print(f"Topic created: {topic.session_id}")
        
        # Test topic retrieval
        print("\nTesting topic retrieval...")
        retrieved_topic = await topic_service.get_topic(topic.session_id, "test_user_123")
        
        if retrieved_topic:
            print(f"SUCCESS: Topic retrieved: {retrieved_topic.topic}")
        else:
            print("FAILED: Topic not found")
        
        # Test topic listing
        print("\nTesting topic listing...")
        topic_list = await topic_service.list_topics("test_user_123")
        print(f"Topics found: {len(topic_list.topics)}")
        
        # Test topic deletion
        print("\nTesting topic deletion...")
        deleted = await topic_service.delete_topic(topic.session_id, "test_user_123")
        
        if deleted:
            print("SUCCESS: Topic deleted")
        else:
            print("FAILED: Topic not deleted")
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_topic_service())
