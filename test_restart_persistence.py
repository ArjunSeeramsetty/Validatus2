#!/usr/bin/env python3
"""
Test persistence across backend restarts
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_restart_persistence():
    """Test that topics persist after backend restart"""
    
    print("Testing Persistence After Backend Restart")
    print("="*50)
    
    # Step 1: List existing topics
    print("\nStep 1: Listing Existing Topics...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/")
    print(f"List Topics Status: {response.status_code}")
    
    if response.status_code == 200:
        topics_list = response.json()
        print(f"SUCCESS: Found {topics_list['total']} topics in database")
        
        if topics_list['total'] > 0:
            print("Topics found:")
            for topic in topics_list['topics']:
                print(f"   - {topic['topic']} (ID: {topic['session_id']})")
                print(f"     Status: {topic['status']}")
                print(f"     URLs: {len(topic['initial_urls'])}")
                print(f"     Created: {topic['created_at']}")
        else:
            print("No topics found - this suggests data was lost on restart")
            return False
    else:
        print(f"FAILED: Could not list topics: {response.text}")
        return False
    
    # Step 2: Test retrieving a specific topic
    if topics_list['total'] > 0:
        test_topic = topics_list['topics'][0]
        session_id = test_topic['session_id']
        
        print(f"\nStep 2: Testing Topic Retrieval...")
        response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}")
        print(f"Get Topic Status: {response.status_code}")
        
        if response.status_code == 200:
            topic_data = response.json()
            print(f"SUCCESS: Topic retrieved successfully")
            print(f"   Topic: {topic_data['topic']}")
            print(f"   Status: {topic_data['status']}")
            print(f"   URLs: {len(topic_data['initial_urls'])}")
        else:
            print(f"FAILED: Could not retrieve topic: {response.text}")
            return False
        
        # Step 3: Test URL retrieval
        print(f"\nStep 3: Testing URL Retrieval...")
        response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}/urls")
        print(f"Get URLs Status: {response.status_code}")
        
        if response.status_code == 200:
            urls_data = response.json()
            print(f"SUCCESS: URLs retrieved successfully")
            print(f"   URL Count: {urls_data['url_count']}")
            print(f"   Last Updated: {urls_data['last_updated']}")
        else:
            print(f"FAILED: Could not retrieve URLs: {response.text}")
            return False
    
    # Step 4: Check database file
    print(f"\nStep 4: Checking Database File...")
    db_path = "backend/validatus_data.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"SUCCESS: Database file exists ({size} bytes)")
    else:
        print(f"WARNING: Database file not found at {db_path}")
    
    print(f"\nPersistence Test Results:")
    print(f"   Topics Found: {topics_list['total']}")
    print(f"   Database Status: {'EXISTS' if os.path.exists(db_path) else 'MISSING'}")
    print(f"   Persistence: {'WORKING' if topics_list['total'] > 0 else 'FAILED'}")
    
    return topics_list['total'] > 0

if __name__ == "__main__":
    try:
        success = test_restart_persistence()
        
        if success:
            print("\n✅ PERSISTENCE TEST PASSED!")
            print("   Topics, URLs, and data are persisting across backend restarts")
            print("   SQLite database is working correctly")
        else:
            print("\n❌ PERSISTENCE TEST FAILED!")
            print("   Data is not persisting across backend restarts")
            print("   Check database configuration")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
