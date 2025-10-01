#!/usr/bin/env python3
"""
Test script to check backend logs and TopicService behavior
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_topic_creation_with_debug():
    """Test topic creation and check what's happening"""
    print("Testing topic creation with debug info...")
    
    # Create a topic
    topic_data = {
        "topic": "Debug Test Topic 2",
        "description": "This is a debug test topic 2",
        "search_queries": ["debug test 2"],
        "initial_urls": ["https://example.com/debug2"],
        "analysis_type": "comprehensive",
        "user_id": "debug_user_456"
    }
    
    try:
        # Create topic
        print("Creating topic...")
        response = requests.post(
            f"{BASE_URL}/api/v3/topics/",
            json=topic_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 201:
            topic = response.json()
            session_id = topic['session_id']
            print(f"SUCCESS: Topic created: {session_id}")
            print(f"Topic details: {json.dumps(topic, indent=2)}")
            
            # Try to retrieve it immediately
            print(f"Attempting to retrieve topic: {session_id}")
            get_response = requests.get(
                f"{BASE_URL}/api/v3/topics/{session_id}?user_id=debug_user_456",
                timeout=15
            )
            
            print(f"Retrieval response status: {get_response.status_code}")
            print(f"Retrieval response: {get_response.text}")
            
        else:
            print(f"FAILED: Topic creation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_topic_creation_with_debug()
