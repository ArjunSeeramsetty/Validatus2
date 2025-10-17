# test_data_driven_api.py

"""
Test the data-driven API endpoints
"""

import requests
import json
import time

BASE_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

def test_data_driven_endpoints():
    """Test all data-driven API endpoints"""
    
    print("Testing Data-Driven API Endpoints")
    print("=" * 50)
    
    # Test session ID (use existing session)
    session_id = "topic-747b5405721c"
    topic = "AI-powered market analysis"
    
    # Test 1: Check generation status
    print("1. Testing status endpoint for session", session_id)
    try:
        response = requests.get(f"{BASE_URL}/api/v3/data-driven-results/status/{session_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Status: {status_data.get('status', 'unknown')}")
            print(f"Progress: {status_data.get('progress_percentage', 0)}%")
            print(f"Current Stage: {status_data.get('current_stage', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Trigger results generation
    print(f"\n2️⃣ Testing generation trigger for session {session_id}")
    try:
        response = requests.post(f"{BASE_URL}/api/v3/data-driven-results/generate/{session_id}/{topic}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            gen_data = response.json()
            print(f"✅ Generation: {gen_data.get('status', 'unknown')}")
            print(f"Message: {gen_data.get('message', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Check status again (should be processing)
    print(f"\n3️⃣ Checking status after generation trigger")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/data-driven-results/status/{session_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Status: {status_data.get('status', 'unknown')}")
            print(f"Progress: {status_data.get('progress_percentage', 0)}%")
            print(f"Current Stage: {status_data.get('current_stage', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Try to get segment results (should show processing or error)
    print(f"\n4️⃣ Testing segment results for market segment")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/data-driven-results/segment/{session_id}/market")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            segment_data = response.json()
            print(f"✅ Segment data loaded")
            print(f"Factors: {len(segment_data.get('factors', {}))}")
            print(f"Patterns: {len(segment_data.get('patterns', []))}")
            print(f"Scenarios: {len(segment_data.get('scenarios', []))}")
        elif response.status_code == 404:
            print("ℹ️ Results not found (expected if not generated yet)")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 5: Test complete results endpoint
    print(f"\n5️⃣ Testing complete results endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/data-driven-results/complete/{session_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            complete_data = response.json()
            print(f"✅ Complete results loaded")
            print(f"Segments: {list(complete_data.get('segments', {}).keys())}")
        elif response.status_code == 404:
            print("ℹ️ Complete results not found (expected if not generated yet)")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print(f"\n🎯 Data-Driven API Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_data_driven_endpoints()
