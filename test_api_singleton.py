#!/usr/bin/env python3
"""
Test script to verify API singleton behavior
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_singleton():
    """Test if API endpoints use the same TopicService instance"""
    print("Testing API singleton behavior...")
    
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
                    print("SUCCESS: Singleton working - Topic found in list")
                    return True
                else:
                    print("FAILED: Singleton issue - Topic not found in list")
                    return False
            else:
                print(f"FAILED: Topic listing failed: {list_response.status_code} - {list_response.text}")
                return False
                
        else:
            print(f"FAILED: Topic creation failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_api_singleton()
    if success:
        print("\nSUCCESS: Singleton pattern is working correctly!")
    else:
        print("\nFAILED: Singleton pattern has issues.")
