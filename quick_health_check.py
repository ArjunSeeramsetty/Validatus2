# quick_health_check.py

"""
Quick health check with longer timeout
"""

import requests

BASE_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

print("Quick Health Check")
print("=" * 50)

# Test root endpoint
print("\n1. Testing root endpoint...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test health endpoint
print("\n2. Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Backend: {data.get('status')}")
        print(f"   Database: {data.get('services', {}).get('database', {}).get('status')}")
except Exception as e:
    print(f"   Error: {e}")

# Test existing results
print("\n3. Testing existing results API...")
try:
    response = requests.get(f"{BASE_URL}/api/v3/results/market/topic-747b5405721c", timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Data keys: {list(data.keys())}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 50)
