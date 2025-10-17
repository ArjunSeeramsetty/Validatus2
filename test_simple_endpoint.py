# test_simple_endpoint.py

"""
Test the simple test endpoint
"""

import requests

BASE_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

def test_simple():
    """Test simple endpoint"""
    
    print("Testing Simple Data-Driven Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v3/data-driven-results/test")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: {data}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_simple()
