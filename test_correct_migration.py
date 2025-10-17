# test_correct_migration.py

"""
Test migration via correct API path
"""

import requests

BASE_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

def test_migration():
    """Test migration endpoints"""
    
    print("TESTING MIGRATION ENDPOINTS")
    print("=" * 50)
    
    # Test 1: Try /migration/run (old path)
    print("\n1. Testing POST /migration/run...")
    try:
        response = requests.post(f"{BASE_URL}/migration/run", timeout=60)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"SUCCESS: {response.json()}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 2: Try /api/v3/migration/run (correct path via router)
    print("\n2. Testing POST /api/v3/migration/run...")
    try:
        response = requests.post(f"{BASE_URL}/api/v3/migration/run", timeout=60)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS!")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"Total tables: {data.get('total_tables')}")
            if data.get('tables_created'):
                print(f"Tables created:")
                for table in data['tables_created']:
                    print(f"  - {table}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_migration()
