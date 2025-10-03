#!/usr/bin/env python3
"""
Simple persistence test without manual input
Tests that topics are created and stored in SQLite database
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_simple_persistence():
    """Test basic persistence functionality"""
    
    print("Testing Basic Persistence Functionality")
    print("="*50)
    
    # Step 1: Create a topic
    print("\nStep 1: Creating Topic...")
    topic_data = {
        "topic": "Pergola Market Strategic Analysis",
        "description": "Comprehensive strategic analysis of the pergola market",
        "search_queries": [
            "pergola market size 2025",
            "outdoor living trends"
        ],
        "initial_urls": [
            "https://example.com/pergola-trends-2025"
        ],
        "analysis_type": "comprehensive",
        "user_id": "demo_user_123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v3/topics/", json=topic_data)
    print(f"Create Topic Status: {response.status_code}")
    
    if response.status_code == 201:
        topic = response.json()
        session_id = topic["session_id"]
        print(f"SUCCESS: Topic created: {session_id}")
        print(f"   Topic: {topic['topic']}")
        print(f"   Status: {topic['status']}")
    else:
        print(f"FAILED: Topic creation failed: {response.text}")
        return None
    
    # Step 2: Verify topic can be retrieved
    print(f"\nStep 2: Retrieving Topic...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}")
    print(f"Get Topic Status: {response.status_code}")
    
    if response.status_code == 200:
        retrieved_topic = response.json()
        print(f"SUCCESS: Topic retrieved from database")
        print(f"   Topic: {retrieved_topic['topic']}")
        print(f"   Status: {retrieved_topic['status']}")
    else:
        print(f"FAILED: Topic retrieval failed: {response.text}")
        return session_id
    
    # Step 3: List topics to verify it appears
    print(f"\nStep 3: Listing Topics...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/")
    print(f"List Topics Status: {response.status_code}")
    
    if response.status_code == 200:
        topics_list = response.json()
        print(f"SUCCESS: Found {topics_list['total']} topics in database")
        
        # Find our topic
        our_topic = None
        for topic in topics_list['topics']:
            if topic['session_id'] == session_id:
                our_topic = topic
                break
        
        if our_topic:
            print(f"SUCCESS: Our topic found in list")
            print(f"   Topic: {our_topic['topic']}")
        else:
            print(f"FAILED: Our topic not found in list")
    else:
        print(f"FAILED: Failed to list topics: {response.text}")
    
    # Step 4: Test URL collection
    print(f"\nStep 4: Testing URL Collection...")
    response = requests.post(f"{BASE_URL}/api/v3/topics/{session_id}/collect-urls")
    print(f"Collect URLs Status: {response.status_code}")
    
    if response.status_code == 200:
        collection_result = response.json()
        print(f"SUCCESS: URL collection completed")
        print(f"   URLs collected: {collection_result['urls_collected']}")
        print(f"   Total URLs: {collection_result['total_urls']}")
    else:
        print(f"FAILED: URL collection failed: {response.text}")
    
    # Step 5: Check database file
    print(f"\nStep 5: Checking Database File...")
    db_path = "validatus_data.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"SUCCESS: Database file exists ({size} bytes)")
    else:
        print(f"WARNING: Database file not found at {db_path}")
    
    print(f"\nPersistence Test Results:")
    print(f"   Session ID: {session_id}")
    print(f"   Topic: {topic_data['topic']}")
    print(f"   Database: SQLite")
    print(f"   Status: {'PASSED' if response.status_code == 200 else 'FAILED'}")
    
    return session_id

def show_persistence_instructions():
    """Show instructions for testing backend restart persistence"""
    print(f"\n" + "="*60)
    print("BACKEND RESTART PERSISTENCE TEST INSTRUCTIONS")
    print("="*60)
    print("To test persistence across backend restarts:")
    print("1. Stop the backend server (Ctrl+C)")
    print("2. Start the backend server again")
    print("3. Run this script again to verify the topic still exists")
    print("4. The topic should persist in the SQLite database")
    print("="*60)

if __name__ == "__main__":
    try:
        session_id = test_simple_persistence()
        
        if session_id:
            show_persistence_instructions()
        
        print("\nBasic persistence test completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
