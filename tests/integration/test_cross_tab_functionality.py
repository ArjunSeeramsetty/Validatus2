#!/usr/bin/env python3
"""
Cross-Tab Functionality Integration Tests
Consolidated from: test_cross_tab_functionality.py
Tests topic creation in Topics tab and usage in URLs tab
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"


class TestCrossTabFunctionality:
    """Test cross-tab functionality between Topics and URLs tabs"""
    
    def test_topic_creation_and_url_collection(self):
        """Test creating topic in Topics tab and using it in URLs tab"""
        # Create topic (Topics tab)
        topic_data = {
            "topic": "Cross-Tab Test Topic",
            "description": "Testing topic creation in Topics tab and usage in URLs tab",
            "search_queries": ["cross-tab functionality test", "topic persistence test"],
            "initial_urls": [],
            "analysis_type": "standard",
            "user_id": "demo_user_123"
        }
        
        response = requests.post(f"{BASE_URL}/api/v3/topics/", json=topic_data, timeout=10)
        assert response.status_code == 201
        session_id = response.json()["session_id"]
        
        try:
            # List topics (URLs tab)
            response = requests.get(f"{BASE_URL}/api/v3/topics/", timeout=10)
            assert response.status_code == 200
            topics_list = response.json()
            
            # Find our created topic
            our_topic = next((t for t in topics_list['topics'] if t['session_id'] == session_id), None)
            assert our_topic is not None
            assert our_topic['topic'] == topic_data['topic']
            
            # Get topic URLs (URLs tab functionality)
            response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}/urls", timeout=10)
            assert response.status_code == 200
            urls_data = response.json()
            assert 'url_count' in urls_data
            assert 'urls' in urls_data
            
            # Collect URLs (URLs tab functionality)
            response = requests.post(f"{BASE_URL}/api/v3/topics/{session_id}/collect-urls", timeout=30)
            assert response.status_code == 200
            collection_result = response.json()
            assert 'urls_collected' in collection_result
            assert 'total_urls' in collection_result
            
            # Verify updated URLs
            response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}/urls", timeout=10)
            assert response.status_code == 200
            updated_urls = response.json()
            assert 'last_updated' in updated_urls
            
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

