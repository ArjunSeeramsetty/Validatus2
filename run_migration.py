# run_migration.py

"""
Run database migration via API
"""

import requests
import json

def run_migration():
    """Run database migration"""
    
    print("Running Database Migration")
    print("=" * 50)
    
    url = "https://validatus-backend-ssivkqhvhq-uc.a.run.app/migration/run"
    
    try:
        print("Triggering migration...")
        response = requests.post(url, json={}, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS!")
            print(f"Message: {result.get('message', 'No message')}")
            print(f"Tables Created: {result.get('tables_created', 'Unknown')}")
            print(f"Tables Verified: {result.get('tables_verified', 'Unknown')}")
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    run_migration()