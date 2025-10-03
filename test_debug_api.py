#!/usr/bin/env python3
"""
Debug script to test API TopicService state
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_topic_creation_and_debug():
    """Test topic creation and check API state"""
    print("Testing topic creation and API state...")
    
    # Create a topic
    topic_data = {
        "topic": "Debug API Test",
        "description": "Testing API state",
        "search_queries": ["debug api"],
        "initial_urls": ["https://example.com/debug-api"],
        "analysis_type": "comprehensive",
        "user_id": "debug_api_user_123"
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
            
            # Try to list topics
            list_response = requests.get(
                f"{BASE_URL}/api/v3/topics/?user_id=debug_api_user_123",
                timeout=10
            )
            
            print(f"List response status: {list_response.status_code}")
            print(f"List response: {list_response.text}")
            
            # Try to get the specific topic
            get_response = requests.get(
                f"{BASE_URL}/api/v3/topics/{session_id}?user_id=debug_api_user_123",
                timeout=10
            )
            
            print(f"Get response status: {get_response.status_code}")
            print(f"Get response: {get_response.text}")
            
        else:
            print(f"FAILED: Topic creation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_topic_creation_and_debug()
