#!/usr/bin/env python3
"""
Test script to verify backend API is working correctly
"""
import requests
import json
import sys

def test_backend_api():
    """Test the backend API endpoints"""
    
    base_url = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
    
    print("🧪 Testing Backend API...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health check passed: {health_data.get('status', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Topics list
    print("\n2. Testing topics list endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v3/topics", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            topics_data = response.json()
            topics = topics_data.get('topics', [])
            print(f"   ✅ Topics list successful: Found {len(topics)} topics")
            for i, topic in enumerate(topics[:3]):  # Show first 3 topics
                print(f"      {i+1}. {topic.get('topic', 'Unknown')} (ID: {topic.get('session_id', 'Unknown')})")
        else:
            print(f"   ❌ Topics list failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Topics list error: {e}")
    
    # Test 3: CORS headers
    print("\n3. Testing CORS headers...")
    try:
        response = requests.options(f"{base_url}/api/v3/topics", timeout=10)
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        print(f"   CORS Headers: {json.dumps(cors_headers, indent=2)}")
        if cors_headers['Access-Control-Allow-Origin']:
            print("   ✅ CORS headers present")
        else:
            print("   ❌ CORS headers missing")
    except Exception as e:
        print(f"   ❌ CORS test error: {e}")
    
    # Test 4: Create topic test
    print("\n4. Testing topic creation...")
    try:
        test_topic = {
            "topic": "API Test Topic",
            "description": "Test topic created via API test script",
            "search_queries": ["test", "api"],
            "initial_urls": ["https://example.com/test"],
            "analysis_type": "comprehensive",
            "user_id": "test_user_api",
            "metadata": {"test": True}
        }
        
        response = requests.post(f"{base_url}/api/v3/topics/create", 
                               json=test_topic, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            topic_response = response.json()
            print(f"   ✅ Topic creation successful: {topic_response.get('session_id', 'Unknown')}")
        else:
            print(f"   ❌ Topic creation failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Topic creation error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Backend API test completed!")

if __name__ == "__main__":
    test_backend_api()
