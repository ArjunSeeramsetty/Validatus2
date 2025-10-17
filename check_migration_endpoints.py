# check_migration_endpoints.py

"""
Check available migration endpoints
"""

import requests
import json

def check_migration_endpoints():
    """Check what migration endpoints are available"""
    
    print("Checking Migration Endpoints")
    print("=" * 50)
    
    try:
        # Get OpenAPI schema
        response = requests.get("https://validatus-backend-ssivkqhvhq-uc.a.run.app/openapi.json")
        
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get('paths', {})
            
            # Find migration endpoints
            migration_paths = [path for path in paths.keys() if 'migration' in path]
            
            print(f"Found {len(migration_paths)} migration endpoints:")
            for path in migration_paths:
                methods = list(paths[path].keys())
                print(f"  {path} - {methods}")
            
            # Also check for any endpoints with 'run' in them
            run_paths = [path for path in paths.keys() if 'run' in path]
            print(f"\nFound {len(run_paths)} endpoints with 'run':")
            for path in run_paths:
                methods = list(paths[path].keys())
                print(f"  {path} - {methods}")
                
        else:
            print(f"ERROR: Failed to get schema - {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_migration_endpoints()
