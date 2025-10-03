#!/usr/bin/env python3
"""
Script to clean up test data
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def cleanup_test_data():
    """Clean up test data"""
    
    print("Cleaning up test data...")
    print("="*40)
    
    # Get all topics
    response = requests.get(f"{BASE_URL}/api/v3/topics/")
    if response.status_code == 200:
        topics_list = response.json()
        print(f"Found {topics_list['total']} topics to clean up")
        
        for topic in topics_list['topics']:
            session_id = topic['session_id']
            topic_name = topic['topic']
            
            print(f"Deleting topic: {topic_name} ({session_id})")
            
            # Delete the topic
            delete_response = requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}")
            if delete_response.status_code == 200:
                print(f"  SUCCESS: Deleted {topic_name}")
            else:
                print(f"  FAILED: Could not delete {topic_name}: {delete_response.text}")
    else:
        print(f"Failed to get topics: {response.text}")
    
    # Verify cleanup
    response = requests.get(f"{BASE_URL}/api/v3/topics/")
    if response.status_code == 200:
        topics_list = response.json()
        print(f"\nCleanup complete. Remaining topics: {topics_list['total']}")
    else:
        print(f"Failed to verify cleanup: {response.text}")

if __name__ == "__main__":
    cleanup_test_data()
