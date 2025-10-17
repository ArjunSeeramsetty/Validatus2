# test_api_simple.py

"""
Simple test for data-driven API endpoints
"""

import requests
import json

BASE_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

def test_endpoints():
    """Test data-driven API endpoints"""
    
    print("Testing Data-Driven API Endpoints")
    print("=" * 50)
    
    session_id = "topic-747b5405721c"
    topic = "AI-powered market analysis"
    
    # Test 1: Status endpoint
    print("\n1. Testing status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/data-driven-results/status/{session_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Status = {data.get('status')}")
            print(f"Progress = {data.get('progress_percentage')}%")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 2: Generation trigger
    print("\n2. Testing generation trigger...")
    try:
        response = requests.post(f"{BASE_URL}/api/v3/data-driven-results/generate/{session_id}/{topic}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: {data.get('message')}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 3: Segment results
    print("\n3. Testing segment results...")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/data-driven-results/segment/{session_id}/market")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Loaded segment data")
            print(f"Factors: {len(data.get('factors', {}))}")
        elif response.status_code == 404:
            print("INFO: Results not found (expected)")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    print("\nAPI Test Complete!")

if __name__ == "__main__":
    test_endpoints()
