#!/usr/bin/env python3
"""
Test Topic Creation Endpoint
============================

Simple test script to verify the topic creation endpoint is working
before testing from the frontend.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_topic_creation_endpoints():
    """Test various topic creation endpoints"""
    
    print("Testing Topic Creation Endpoints")
    print("=" * 40)
    
    # Test data
    topic_data = {
        "topic": "Test Pergola Analysis",
        "description": "Test topic for frontend validation",
        "search_queries": [
            "pergola market analysis",
            "outdoor living trends",
            "bioclimatic pergola market"
        ],
        "initial_urls": [
            "https://www.verifiedmarketresearch.com/product/pergolas-market/",
            "https://www.fortunebusinessinsights.com/bioclimatic-pergola-market-112455"
        ],
        "analysis_type": "pergola",
        "user_id": "test_user_frontend"
    }
    
    # Test different endpoints
    endpoints_to_test = [
        {
            "name": "Analysis Sessions Create",
            "url": "/api/v3/analysis/sessions/create",
            "method": "POST"
        },
        {
            "name": "Migrated Topics",
            "url": "/api/v3/migrated/topics",
            "method": "POST"
        },
        {
            "name": "Topics Create",
            "url": "/api/v3/topics/create",
            "method": "POST"
        }
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'POST':
                response = requests.post(
                    f"{BASE_URL}{endpoint['url']}",
                    json=topic_data,
                    timeout=30
                )
            else:
                response = requests.get(
                    f"{BASE_URL}{endpoint['url']}",
                    timeout=30
                )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("SUCCESS: Endpoint is working")
                if 'session_id' in result:
                    print(f"Session ID: {result['session_id']}")
                if 'topic_id' in result:
                    print(f"Topic ID: {result['topic_id']}")
                if 'success' in result:
                    print(f"Success: {result['success']}")
            else:
                print(f"ERROR: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Response: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"REQUEST ERROR: {e}")
        except Exception as e:
            print(f"UNEXPECTED ERROR: {e}")
    
    # Test if server is running
    print(f"\n{'='*40}")
    print("Testing Server Health")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("SUCCESS: Server is running and healthy")
            health_data = response.json()
            print(f"Service: {health_data.get('service', 'Unknown')}")
            print(f"Version: {health_data.get('version', 'Unknown')}")
        else:
            print(f"ERROR: Health check failed - {response.status_code}")
    except Exception as e:
        print(f"ERROR: Cannot connect to server - {e}")

if __name__ == "__main__":
    test_topic_creation_endpoints()
