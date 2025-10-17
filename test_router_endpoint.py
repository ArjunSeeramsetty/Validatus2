# test_router_endpoint.py

"""
Test the router endpoint
"""

import requests

BASE_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

def test_router():
    """Test router endpoint"""
    
    print("Testing Router Endpoint")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v3/test/hello")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: {data}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_router()
