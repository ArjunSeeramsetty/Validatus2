#!/usr/bin/env python3
"""
Test script to debug TopicService singleton behavior
"""
import sys
import os
import requests

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

BASE_URL = "http://localhost:8000"

def test_singleton_behavior():
    """Test if TopicService singleton is working correctly"""
    print("Testing TopicService singleton behavior...")
    
    # Test 1: Create a topic
    topic_data = {
        "topic": "Singleton Test Topic",
        "description": "Testing singleton behavior",
        "search_queries": ["singleton test"],
        "initial_urls": ["https://example.com/singleton"],
        "analysis_type": "comprehensive",
        "user_id": "singleton_user_123"
    }
    
    try:
        # Create topic
        response = requests.post(
            f"{BASE_URL}/api/v3/topics/",
            json=topic_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            topic = response.json()
            session_id = topic['session_id']
            print(f"SUCCESS: Topic created: {session_id}")
            
            # Test 2: List topics immediately
            list_response = requests.get(
                f"{BASE_URL}/api/v3/topics/?user_id=singleton_user_123",
                timeout=10
            )
            
            if list_response.status_code == 200:
                topics_list = list_response.json()
                print(f"SUCCESS: Listed {len(topics_list['topics'])} topics")
                
                if len(topics_list['topics']) > 0:
                    print("✅ Singleton working: Topic found in list")
                else:
                    print("❌ Singleton issue: Topic not found in list")
            else:
                print(f"FAILED: Topic listing failed: {list_response.status_code} - {list_response.text}")
            
            # Test 3: Try to retrieve the topic
            get_response = requests.get(
                f"{BASE_URL}/api/v3/topics/{session_id}?user_id=singleton_user_123",
                timeout=10
            )
            
            if get_response.status_code == 200:
                retrieved_topic = get_response.json()
                print(f"SUCCESS: Topic retrieved: {retrieved_topic['topic']}")
                print("✅ Singleton working: Topic retrieved successfully")
            else:
                print(f"FAILED: Topic retrieval failed: {get_response.status_code} - {get_response.text}")
                print("❌ Singleton issue: Topic not retrievable")
                
        else:
            print(f"FAILED: Topic creation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

def test_direct_topic_service():
    """Test TopicService directly to compare behavior"""
    print("\nTesting TopicService directly...")
    
    try:
        from app.services.topic_service import topic_service_instance
        from app.models.topic_models import TopicCreateRequest
        
        print(f"TopicService instance: {topic_service_instance}")
        print(f"Using local fallback: {topic_service_instance._use_local_fallback}")
        print(f"Local storage size: {len(topic_service_instance._local_storage)}")
        
        # Create a topic directly
        request = TopicCreateRequest(
            topic="Direct Test Topic",
            description="Testing direct TopicService",
            search_queries=["direct test"],
            initial_urls=["https://example.com/direct"],
            analysis_type="comprehensive",
            user_id="direct_user_123"
        )
        
        import asyncio
        topic = asyncio.run(topic_service_instance.create_topic(request))
        print(f"SUCCESS: Direct topic created: {topic.session_id}")
        
        # Check local storage
        print(f"Local storage size after creation: {len(topic_service_instance._local_storage)}")
        
        # Try to retrieve it
        retrieved = asyncio.run(topic_service_instance.get_topic(topic.session_id, "direct_user_123"))
        if retrieved:
            print(f"SUCCESS: Direct topic retrieved: {retrieved.topic}")
            print("✅ Direct TopicService working correctly")
        else:
            print("❌ Direct TopicService issue: Topic not retrievable")
            
    except Exception as e:
        print(f"ERROR in direct test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_singleton_behavior()
    test_direct_topic_service()
