# test_data_bridge.py

"""
Test data bridge with real session
"""

import requests
import json

def test_data_bridge():
    """Test data-driven endpoints with real session"""
    
    session_id = "topic-747b5405721c"
    base_url = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
    
    print("=" * 60)
    print("TESTING DATA BRIDGE WITH REAL SESSION")
    print("=" * 60)
    
    # Test 1: Status endpoint
    print("\n[1] Testing status endpoint...")
    try:
        r = requests.get(f"{base_url}/api/v3/data-driven-results/status/{session_id}")
        print(f"Status Code: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"Results Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"Progress: {data.get('progress_percentage')}%")
            print(f"Completed Segments: {data.get('completed_segments', 0)}/{data.get('total_segments', 5)}")
        else:
            print(f"Error: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Market segment
    print("\n[2] Testing market segment...")
    try:
        r = requests.get(f"{base_url}/api/v3/data-driven-results/segment/{session_id}/market")
        print(f"Status Code: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"Segment: {data.get('segment')}")
            print(f"Source: {data.get('source')}")
            print(f"Factors: {len(data.get('factors', {}))} found")
            print(f"Patterns: {len(data.get('patterns', []))} found")
            print(f"Scenarios: {len(data.get('scenarios', []))} found")
            print(f"Personas: {len(data.get('personas', []))} found")
            
            rich_content = data.get('rich_content', {})
            print(f"Opportunities: {len(rich_content.get('opportunities', []))} found")
            print(f"Has Market Share: {'market_share' in rich_content}")
            
            # Sample a few factors
            factors = data.get('factors', {})
            if factors:
                print(f"\nSample Factors:")
                for i, (key, value) in enumerate(list(factors.items())[:3]):
                    print(f"  - {key}: {value}")
                    
        else:
            print(f"Error: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Consumer segment
    print("\n[3] Testing consumer segment...")
    try:
        r = requests.get(f"{base_url}/api/v3/data-driven-results/segment/{session_id}/consumer")
        print(f"Status Code: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"Segment: {data.get('segment')}")
            print(f"Factors: {len(data.get('factors', {}))} found")
            print(f"Patterns: {len(data.get('patterns', []))} found")
        else:
            print(f"Error: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_data_bridge()
