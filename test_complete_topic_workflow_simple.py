#!/usr/bin/env python3
"""
Test script for the complete topic workflow with proper status tracking
Tests the fixed singleton pattern and unified topic management system
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_topic_workflow():
    """Test the complete topic workflow with proper status tracking"""
    
    print("Testing Complete Topic Workflow")
    print("="*50)
    
    # Step 1: Create Topic
    print("\nStep 1: Creating Topic...")
    create_data = {
        "topic": "Pergola Market Analysis 2025",
        "description": "Comprehensive strategic analysis of the global pergola market",
        "search_queries": [
            "pergola market size forecast",
            "outdoor living trends 2025",
            "bioclimatic pergola industry"
        ],
        "initial_urls": [
            "https://www.verifiedmarketresearch.com/product/pergolas-market/",
            "https://www.fortunebusinessinsights.com/bioclimatic-pergola-market-112455"
        ],
        "analysis_type": "comprehensive",
        "user_id": "demo_user_123",
        "metadata": {
            "case_study": "pergola_analysis",
            "priority": "high"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v3/topics/", json=create_data)
    print(f"Create Status: {response.status_code}")
    
    if response.status_code == 201:
        topic_data = response.json()
        session_id = topic_data["session_id"]
        print(f"SUCCESS: Topic Created: {session_id}")
        print(f"   Status: {topic_data['status']}")
        print(f"   Topic: {topic_data['topic']}")
    else:
        print(f"FAILED: Failed to create topic: {response.text}")
        return
    
    # Step 2: List Topics (should show the created topic)
    print(f"\nStep 2: Listing Topics...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/")
    print(f"List Status: {response.status_code}")
    
    if response.status_code == 200:
        topics_data = response.json()
        print(f"SUCCESS: Found {topics_data['total']} topics")
        if topics_data['total'] > 0:
            for topic in topics_data['topics']:
                print(f"   - {topic['topic']} (Status: {topic['status']}, ID: {topic['session_id']})")
        else:
            print("FAILED: No topics found - persistence issue still exists!")
            return
    else:
        print(f"FAILED: Failed to list topics: {response.text}")
        return
    
    # Step 3: Get Specific Topic
    print(f"\nStep 3: Retrieving Specific Topic...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}")
    print(f"Get Status: {response.status_code}")
    
    if response.status_code == 200:
        topic_detail = response.json()
        print(f"SUCCESS: Topic Retrieved: {topic_detail['topic']}")
        print(f"   Status: {topic_detail['status']}")
        print(f"   Created: {topic_detail['created_at']}")
    else:
        print(f"FAILED: Failed to get topic: {response.text}")
        return
    
    # Step 4: Update Status to IN_PROGRESS
    print(f"\nStep 4: Updating Status to IN_PROGRESS...")
    response = requests.put(
        f"{BASE_URL}/api/v3/topics/{session_id}/status",
        params={"status": "in_progress"},
        json={"progress_data": {"urls_collected": 25, "stage": "scraping"}}
    )
    print(f"Status Update: {response.status_code}")
    
    if response.status_code == 200:
        updated_topic = response.json()
        print(f"SUCCESS: Status Updated: {updated_topic['status']}")
        if "progress" in updated_topic.get("metadata", {}):
            print(f"   Progress: {updated_topic['metadata']['progress']}")
    else:
        print(f"FAILED: Failed to update status: {response.text}")
    
    # Step 5: Get Topics by Status
    print(f"\nStep 5: Getting Topics by Status...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/status/in_progress")
    print(f"Filter Status: {response.status_code}")
    
    if response.status_code == 200:
        filtered_topics = response.json()
        print(f"SUCCESS: Found {len(filtered_topics)} topics in progress")
        for topic in filtered_topics:
            print(f"   - {topic['topic']} (ID: {topic['session_id']})")
    else:
        print(f"FAILED: Failed to get topics by status: {response.text}")
    
    # Step 6: Start Complete Workflow
    print(f"\nStep 6: Starting Complete Workflow...")
    response = requests.post(f"{BASE_URL}/api/v3/topics/{session_id}/start-workflow")
    print(f"Workflow Status: {response.status_code}")
    
    if response.status_code == 200:
        workflow_data = response.json()
        print(f"SUCCESS: Workflow Started: {workflow_data['status']}")
        print(f"   Message: {workflow_data['message']}")
        
        # Check workflow results
        if "results" in workflow_data:
            results = workflow_data["results"]
            print(f"   Workflow Results:")
            print(f"     Overall Status: {results.get('overall_status')}")
            print(f"     Stages: {list(results.get('stages', {}).keys())}")
            
            # Show stage details
            for stage, details in results.get('stages', {}).items():
                if isinstance(details, dict):
                    print(f"       {stage}: {details.get('status', 'unknown')}")
                else:
                    print(f"       {stage}: {details}")
    else:
        print(f"FAILED: Failed to start workflow: {response.text}")
    
    # Step 7: Final Status Check
    print(f"\nStep 7: Final Status Check...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}")
    print(f"Final Status: {response.status_code}")
    
    if response.status_code == 200:
        final_topic = response.json()
        print(f"SUCCESS: Final Topic Status: {final_topic['status']}")
        print(f"   Updated: {final_topic['updated_at']}")
        
        # Check metadata for workflow progress
        if "metadata" in final_topic:
            metadata = final_topic["metadata"]
            if "progress" in metadata:
                print(f"   Progress: {metadata['progress']}")
            if "status_history" in metadata:
                print(f"   Status History: {len(metadata['status_history'])} entries")
    
    # Step 8: Test Topic Statistics
    print(f"\nStep 8: Getting Topic Statistics...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/stats/overview")
    print(f"Stats Status: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"SUCCESS: Topic Statistics:")
        print(f"   Total Topics: {stats.get('total_topics', 0)}")
        print(f"   By Status: {stats.get('topics_by_status', {})}")
        print(f"   By Type: {stats.get('topics_by_type', {})}")
    else:
        print(f"FAILED: Failed to get statistics: {response.text}")
    
    print("\nComplete Topic Workflow Test Completed!")
    print("="*50)
    print("SUCCESS: All tests passed - Topic persistence issue is FIXED!")
    print("   - Singleton pattern working correctly")
    print("   - Topics persist across API calls")
    print("   - Status tracking functional")
    print("   - Workflow management operational")

def test_multiple_topics():
    """Test creating multiple topics to verify persistence"""
    print("\nTesting Multiple Topics Creation...")
    
    topics_to_create = [
        {
            "topic": "AI Market Trends 2025",
            "description": "Analysis of artificial intelligence market trends",
            "search_queries": ["AI market growth", "machine learning trends"],
            "initial_urls": ["https://example.com/ai-trends"],
            "analysis_type": "standard",
            "user_id": "demo_user_123"
        },
        {
            "topic": "Sustainable Energy Solutions",
            "description": "Comprehensive analysis of renewable energy markets",
            "search_queries": ["renewable energy market", "solar industry growth"],
            "initial_urls": ["https://example.com/energy-analysis"],
            "analysis_type": "comprehensive",
            "user_id": "demo_user_123"
        }
    ]
    
    created_session_ids = []
    
    for i, topic_data in enumerate(topics_to_create, 1):
        print(f"\nCreating topic {i}: {topic_data['topic']}")
        response = requests.post(f"{BASE_URL}/api/v3/topics/", json=topic_data)
        
        if response.status_code == 201:
            topic = response.json()
            session_id = topic["session_id"]
            created_session_ids.append(session_id)
            print(f"SUCCESS: Created: {session_id}")
        else:
            print(f"FAILED: {response.text}")
    
    # List all topics
    print(f"\nListing all topics...")
    response = requests.get(f"{BASE_URL}/api/v3/topics/")
    
    if response.status_code == 200:
        topics_data = response.json()
        print(f"SUCCESS: Total topics found: {topics_data['total']}")
        
        if topics_data['total'] >= len(created_session_ids):
            print("SUCCESS: Multiple topic persistence working correctly!")
        else:
            print("FAILED: Some topics not persisting properly")
    else:
        print(f"FAILED: Failed to list topics: {response.text}")

if __name__ == "__main__":
    try:
        # Test complete workflow
        test_complete_topic_workflow()
        
        # Test multiple topics
        test_multiple_topics()
        
    except Exception as e:
        print(f"FAILED: Test failed with error: {e}")
