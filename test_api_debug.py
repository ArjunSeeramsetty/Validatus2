#!/usr/bin/env python3
"""
Debug script to test API endpoints directly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_topic_creation_and_retrieval():
    """Test topic creation and immediate retrieval"""
    print("Testing topic creation and retrieval...")
    
    # Create a topic
    topic_data = {
        "topic": "Debug Test Topic",
        "description": "This is a debug test topic",
        "search_queries": ["debug test"],
        "initial_urls": ["https://example.com/debug"],
        "analysis_type": "comprehensive",
        "user_id": "debug_user_123"
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
            
            # Immediately try to retrieve it
            print(f"Attempting to retrieve topic: {session_id}")
            get_response = requests.get(
                f"{BASE_URL}/api/v3/topics/{session_id}?user_id=debug_user_123",
                timeout=10
            )
            
            if get_response.status_code == 200:
                retrieved_topic = get_response.json()
                print(f"SUCCESS: Topic retrieved: {retrieved_topic['topic']}")
            else:
                print(f"FAILED: Topic retrieval failed: {get_response.status_code} - {get_response.text}")
            
            # Try to list topics
            print("Attempting to list topics...")
            list_response = requests.get(
                f"{BASE_URL}/api/v3/topics/?user_id=debug_user_123",
                timeout=10
            )
            
            if list_response.status_code == 200:
                topics_list = list_response.json()
                print(f"SUCCESS: Listed {len(topics_list['topics'])} topics")
            else:
                print(f"FAILED: Topic listing failed: {list_response.status_code} - {list_response.text}")
                
        else:
            print(f"FAILED: Topic creation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_topic_creation_and_retrieval()
