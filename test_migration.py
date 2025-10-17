# test_migration.py

"""
Test database migration endpoints
"""

import requests
import json

BASE_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

def test_migration():
    """Test database migration"""
    
    print("DATABASE MIGRATION TEST")
    print("=" * 50)
    
    # Test 1: Verify tables (before migration)
    print("\n1. Checking current table status...")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/database/verify-tables")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"All tables exist: {data.get('all_tables_exist')}")
            if data.get('tables'):
                for table_name, table_info in data['tables'].items():
                    status = "EXISTS" if table_info.get('exists') else "MISSING"
                    count = table_info.get('row_count', 0)
                    print(f"  - {table_name}: {status} ({count} rows)")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 2: Run migration
    print("\n2. Running database migration...")
    try:
        response = requests.post(f"{BASE_URL}/api/v3/database/run-results-persistence-migration")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"Tables created: {data.get('tables_created')}")
            print(f"Tables existed: {data.get('tables_existed')}")
            print(f"Indexes created: {data.get('indexes_created')}")
            if data.get('errors'):
                print(f"Errors: {data.get('errors')}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 3: Verify tables (after migration)
    print("\n3. Verifying tables after migration...")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/database/verify-tables")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"All tables exist: {data.get('all_tables_exist')}")
            if data.get('tables'):
                for table_name, table_info in data['tables'].items():
                    status = "EXISTS" if table_info.get('exists') else "MISSING"
                    count = table_info.get('row_count', 0)
                    print(f"  - {table_name}: {status} ({count} rows)")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    print("\nMigration test complete!")

if __name__ == "__main__":
    test_migration()
