#!/usr/bin/env python3
"""
Test script for topic integration
Tests the complete topic workflow from frontend to backend
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_topic_creation():
    """Test topic creation via API"""
    print("Testing Topic Creation...")
    
    topic_data = {
        "topic": "Integration Test Topic",
        "description": "This is a test topic created during integration testing",
        "search_queries": [
            "integration testing",
            "topic management",
            "API testing"
        ],
        "initial_urls": [
            "https://example.com/test1",
            "https://example.com/test2"
        ],
        "analysis_type": "comprehensive",
        "user_id": "test_user_123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v3/topics/",
            json=topic_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            topic = response.json()
            print(f"SUCCESS: Topic created successfully: {topic['session_id']}")
            return topic['session_id']
        else:
            print(f"FAILED: Topic creation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"ERROR: Topic creation error: {e}")
        return None

def test_topic_retrieval(session_id):
    """Test topic retrieval via API"""
    if not session_id:
        print("⏭️ Skipping topic retrieval test - no session ID")
        return
        
    print("🧪 Testing Topic Retrieval...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v3/topics/{session_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            topic = response.json()
            print(f"✅ Topic retrieved successfully: {topic['topic']}")
            return topic
        else:
            print(f"❌ Topic retrieval failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Topic retrieval error: {e}")
        return None

def test_topic_update(session_id):
    """Test topic update via API"""
    if not session_id:
        print("⏭️ Skipping topic update test - no session ID")
        return
        
    print("🧪 Testing Topic Update...")
    
    update_data = {
        "topic": "Updated Integration Test Topic",
        "description": "This topic has been updated during integration testing",
        "status": "in_progress"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/v3/topics/{session_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            topic = response.json()
            print(f"✅ Topic updated successfully: {topic['topic']}")
            return topic
        else:
            print(f"❌ Topic update failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Topic update error: {e}")
        return None

def test_topic_deletion(session_id):
    """Test topic deletion via API"""
    if not session_id:
        print("⏭️ Skipping topic deletion test - no session ID")
        return
        
    print("🧪 Testing Topic Deletion...")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/api/v3/topics/{session_id}",
            timeout=10
        )
        
        if response.status_code == 204:
            print("✅ Topic deleted successfully")
            return True
        else:
            print(f"❌ Topic deletion failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Topic deletion error: {e}")
        return False

def test_api_endpoints():
    """Test various API endpoints"""
    print("🧪 Testing API Endpoints...")
    
    endpoints = [
        "/health",
        "/api/v3/topics/analysis-types/",
        "/api/v3/topics/statuses/",
        "/api/v3/topics/stats/overview"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"⚠️ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def test_frontend_connectivity():
    """Test frontend connectivity"""
    print("🧪 Testing Frontend Connectivity...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"⚠️ Frontend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connectivity error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Topic Integration Tests")
    print("=" * 50)
    
    # Test API endpoints
    test_api_endpoints()
    print()
    
    # Test frontend connectivity
    frontend_ok = test_frontend_connectivity()
    print()
    
    # Test topic workflow
    session_id = test_topic_creation()
    print()
    
    topic = test_topic_retrieval(session_id)
    print()
    
    updated_topic = test_topic_update(session_id)
    print()
    
    deletion_success = test_topic_deletion(session_id)
    print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Frontend Accessible: {'✅' if frontend_ok else '❌'}")
    print(f"Topic Creation: {'✅' if session_id else '❌'}")
    print(f"Topic Retrieval: {'✅' if topic else '❌'}")
    print(f"Topic Update: {'✅' if updated_topic else '❌'}")
    print(f"Topic Deletion: {'✅' if deletion_success else '❌'}")
    
    if all([session_id, topic, updated_topic, deletion_success]):
        print("\n🎉 All tests passed! Topic integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
