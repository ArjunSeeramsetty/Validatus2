# run_migration.py

"""
Run the database migration via existing endpoint
"""

import requests
import time

BASE_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

def run_migration():
    """Run database migration"""
    
    print("RUNNING DATABASE MIGRATION")
    print("=" * 50)
    
    print("\nCalling POST /migration/run...")
    print("This will create:")
    print("- URL collection tables (2 tables)")
    print("- Results persistence tables (6 tables)")
    print("- All indexes")
    print("\nPlease wait...")
    
    try:
        response = requests.post(f"{BASE_URL}/migration/run", timeout=60)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nSTATUS: {data.get('status')}")
            print(f"MESSAGE: {data.get('message')}")
            print(f"DETAILS: {data.get('details')}")
            
            if data.get('tables_created'):
                print(f"\nTABLES CREATED ({data.get('total_tables', len(data['tables_created']))}):")
                for table in data['tables_created']:
                    print(f"  - {table}")
            
            print("\nMIGRATION SUCCESSFUL!")
            return True
        else:
            print(f"\nERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\nNext step: Verify tables are created")
    else:
        print("\nMigration failed - check logs")
