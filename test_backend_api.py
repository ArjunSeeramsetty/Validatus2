#!/usr/bin/env python3
"""
Test script to verify backend API is working correctly
"""
import requests
import json
import sys
import uuid

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
            try:
                health_data = response.json()
            except requests.exceptions.JSONDecodeError:
                print(f"   ❌ Invalid JSON response")
                return
            print(f"   ✅ Health check passed: {health_data.get('status', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except requests.Timeout:
        print(f"   ❌ Health check timeout")
    except requests.ConnectionError as e:
        print(f"   ❌ Health check connection error: {e}")
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
        print(f"   Status: {response.status_code}")
        if response.status_code not in [200, 204]:
            print(f"   ❌ OPTIONS request failed with status {response.status_code}")
            return
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
    created_topic_id = None
    try:
        test_topic = {
            "topic": f"API Test Topic {uuid.uuid4()}",
            "description": "Test topic created via API test script",
            "search_queries": ["test", "api"],
            "initial_urls": ["https://example.com/test"],
            "analysis_type": "comprehensive",
            "user_id": f"test_user_api_{uuid.uuid4()}",
            "metadata": {"test": True}
        }
        
        response = requests.post(f"{base_url}/api/v3/topics/create", 
                               json=test_topic, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            topic_response = response.json()
            created_topic_id = topic_response.get('session_id')
            print(f"   ✅ Topic creation successful: {created_topic_id}")
        else:
            print(f"   ❌ Topic creation failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Topic creation error: {e}")
    
    # Cleanup: Delete the test topic
    if created_topic_id:
        print(f"\n5. Cleaning up test topic...")
        try:
            delete_response = requests.delete(f"{base_url}/api/v3/topics/{created_topic_id}", timeout=10)
            print(f"   🧹 Cleanup: Topic deleted (status {delete_response.status_code})")
        except Exception as e:
            print(f"   ⚠️  Cleanup failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Backend API test completed!")

if __name__ == "__main__":
    test_backend_api()
