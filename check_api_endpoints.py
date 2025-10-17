# check_api_endpoints.py

"""
Check what API endpoints are available
"""

import requests
import json

BASE_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

def check_endpoints():
    """Check available API endpoints"""
    
    print("Checking Available API Endpoints")
    print("=" * 50)
    
    # Test root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: {data}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test health endpoint
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: {data}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test existing results endpoint
    print("\n3. Testing existing results endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/results/market/topic-747b5405721c")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Existing results endpoint works")
            print(f"Keys: {list(data.keys())}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test OpenAPI schema
    print("\n4. Testing OpenAPI schema...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            paths = data.get('paths', {})
            print(f"SUCCESS: Found {len(paths)} API paths")
            
            # Look for data-driven endpoints
            data_driven_paths = [path for path in paths.keys() if 'data-driven' in path]
            if data_driven_paths:
                print(f"Data-driven endpoints found: {data_driven_paths}")
            else:
                print("No data-driven endpoints found in schema")
                
            # Show some example paths
            example_paths = list(paths.keys())[:5]
            print(f"Example paths: {example_paths}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    print("\nAPI Check Complete!")

if __name__ == "__main__":
    check_endpoints()
