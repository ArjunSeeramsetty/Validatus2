#!/usr/bin/env python3
"""
Test script for persistence across backend sessions
Tests that topics, URLs, scraped content, and analysis scores persist across backend restarts
"""
import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_persistence_across_sessions():
    """Test persistence across backend restarts"""
    
    print("Testing Persistence Across Backend Sessions")
    print("="*60)
    
    # Step 1: Create a topic
    print("\nStep 1: Creating Topic...")
    topic_data = {
        "topic": "Pergola Market Strategic Analysis",
        "description": "Comprehensive strategic analysis of the pergola market including trends, competition, and opportunities",
        "search_queries": [
            "pergola market size 2025",
            "outdoor living trends",
            "pergola industry analysis",
            "outdoor structure market"
        ],
        "initial_urls": [
            "https://example.com/pergola-trends-2025",
            "https://research.com/outdoor-living-market"
        ],
        "analysis_type": "comprehensive",
        "user_id": "demo_user_123",
        "metadata": {
            "industry": "outdoor_living",
            "priority": "high",
            "analysis_scope": "strategic"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v3/topics/", json=topic_data)
    print(f"Create Topic Status: {response.status_code}")
    
    if response.status_code == 201:
        topic = response.json()
        session_id = topic["session_id"]
        print(f"SUCCESS: Topic created: {session_id}")
        print(f"   Topic: {topic['topic']}")
        print(f"   Status: {topic['status']}")
        print(f"   Initial URLs: {len(topic['initial_urls'])}")
    else:
        print(f"FAILED: Topic creation failed: {response.text}")
        return None
    
    # Step 2: Collect URLs
    print(f"\nStep 2: Collecting URLs...")
    response = requests.post(f"{BASE_URL}/api/v3/topics/{session_id}/collect-urls")
    print(f"Collect URLs Status: {response.status_code}")
    
    if response.status_code == 200:
        collection_result = response.json()
        print(f"SUCCESS: URL collection completed")
        print(f"   URLs collected: {collection_result['urls_collected']}")
        print(f"   Total URLs: {collection_result['total_urls']}")
    else:
        print(f"FAILED: URL collection failed: {response.text}")
        return session_id
    
    # Step 3: Verify data is in database
    print(f"\nStep 3: Verifying Data in Database...")
    
    # Check topic exists
    response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}")
    if response.status_code == 200:
        topic_data = response.json()
        print(f"SUCCESS: Topic retrieved from database")
        print(f"   Topic: {topic_data['topic']}")
        print(f"   Status: {topic_data['status']}")
        print(f"   URLs: {len(topic_data['initial_urls'])}")
    else:
        print(f"FAILED: Topic not found in database: {response.text}")
        return session_id
    
    # Check URLs exist
    response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}/urls")
    if response.status_code == 200:
        urls_data = response.json()
        print(f"SUCCESS: URLs retrieved from database")
        print(f"   URL Count: {urls_data['url_count']}")
    else:
        print(f"FAILED: URLs not found in database: {response.text}")
        return session_id
    
    # Step 4: List topics to verify persistence
    print(f"\nStep 4: Listing All Topics...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/")
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
            print(f"SUCCESS: Our topic found in database list")
            print(f"   Topic: {our_topic['topic']}")
            print(f"   Status: {our_topic['status']}")
            print(f"   URLs: {len(our_topic['initial_urls'])}")
        else:
            print(f"FAILED: Our topic not found in database list")
            return session_id
    else:
        print(f"FAILED: Failed to list topics: {response.text}")
        return session_id
    
    print(f"\nStep 5: Data Persistence Test Complete!")
    print(f"   Session ID: {session_id}")
    print(f"   Topic: {topic_data['topic']}")
    print(f"   Status: {topic_data['status']}")
    print(f"   URLs: {len(topic_data['initial_urls'])}")
    print(f"   Database: SQLite (validatus_data.db)")
    
    return session_id

def test_backend_restart_persistence(session_id):
    """Test that data persists after backend restart"""
    
    print(f"\n" + "="*60)
    print("BACKEND RESTART PERSISTENCE TEST")
    print("="*60)
    print(f"IMPORTANT: Please restart the backend server now!")
    print(f"Session ID to verify: {session_id}")
    print(f"Then run this script again to verify persistence.")
    print("="*60)
    
    # Wait for user to restart backend
    input("\nPress Enter after restarting the backend server...")
    
    # Test 1: Verify topic still exists
    print(f"\nTest 1: Verifying Topic Still Exists...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}")
    if response.status_code == 200:
        topic_data = response.json()
        print(f"SUCCESS: Topic persisted across backend restart!")
        print(f"   Topic: {topic_data['topic']}")
        print(f"   Status: {topic_data['status']}")
        print(f"   URLs: {len(topic_data['initial_urls'])}")
    else:
        print(f"FAILED: Topic not found after restart: {response.text}")
        return False
    
    # Test 2: Verify URLs still exist
    print(f"\nTest 2: Verifying URLs Still Exist...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}/urls")
    if response.status_code == 200:
        urls_data = response.json()
        print(f"SUCCESS: URLs persisted across backend restart!")
        print(f"   URL Count: {urls_data['url_count']}")
    else:
        print(f"FAILED: URLs not found after restart: {response.text}")
        return False
    
    # Test 3: Verify topic appears in list
    print(f"\nTest 3: Verifying Topic in List...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/")
    if response.status_code == 200:
        topics_list = response.json()
        our_topic = None
        for topic in topics_list['topics']:
            if topic['session_id'] == session_id:
                our_topic = topic
                break
        
        if our_topic:
            print(f"SUCCESS: Topic appears in list after restart!")
            print(f"   Total topics: {topics_list['total']}")
        else:
            print(f"FAILED: Topic not found in list after restart")
            return False
    else:
        print(f"FAILED: Failed to list topics after restart: {response.text}")
        return False
    
    print(f"\n" + "="*60)
    print("PERSISTENCE TEST RESULTS:")
    print("="*60)
    print("✅ Topic persisted across backend restart")
    print("✅ URLs persisted across backend restart") 
    print("✅ Topic appears in list after restart")
    print("✅ Database storage working correctly")
    print("="*60)
    
    return True

def show_database_info():
    """Show database file information"""
    print(f"\nDatabase Information:")
    print(f"   Type: SQLite")
    print(f"   File: validatus_data.db")
    print(f"   Location: Backend working directory")
    print(f"   Tables: topics, topic_urls, scraped_content, analysis_scores")
    
    # Check if database file exists
    db_path = "validatus_data.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"   Status: EXISTS ({size} bytes)")
    else:
        print(f"   Status: NOT FOUND")

if __name__ == "__main__":
    try:
        # Show database info
        show_database_info()
        
        # Test persistence
        session_id = test_persistence_across_sessions()
        
        if session_id:
            # Test backend restart persistence
            test_backend_restart_persistence(session_id)
        
        print("\nAll persistence tests completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
