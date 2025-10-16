#!/usr/bin/env python3
"""
API CRUD Tests for Topic Management
Consolidated from: test_backend_api.py
"""
import pytest
import requests
import uuid
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
PROD_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"


class TestTopicCRUD:
    """Test CRUD operations for topics"""
    
    @pytest.fixture
    def base_url(self, pytestconfig):
        """Get base URL based on environment"""
        env = pytestconfig.getoption("--env", default="local")
        return PROD_URL if env == "prod" else BASE_URL
    
    def test_health_endpoint(self, base_url):
        """Test health check endpoint"""
        response = requests.get(f"{base_url}/health", timeout=10)
        assert response.status_code == 200
        health_data = response.json()
        assert health_data.get('status') in ['healthy', 'ok']
    
    def test_list_topics(self, base_url):
        """Test topics list endpoint"""
        response = requests.get(f"{base_url}/api/v3/topics", timeout=10)
        assert response.status_code == 200
        topics_data = response.json()
        assert 'topics' in topics_data
        assert isinstance(topics_data['topics'], list)
    
    def test_cors_headers(self, base_url):
        """Test CORS headers"""
        response = requests.options(f"{base_url}/api/v3/topics", timeout=10)
        assert response.status_code in [200, 204]
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_create_and_delete_topic(self, base_url):
        """Test topic creation and deletion"""
        test_topic = {
            "topic": f"API Test Topic {uuid.uuid4()}",
            "description": "Test topic created via API test script",
            "search_queries": ["test", "api"],
            "initial_urls": ["https://example.com/test"],
            "analysis_type": "comprehensive",
            "user_id": f"test_user_api_{uuid.uuid4()}",
            "metadata": {"test": True}
        }
        
        # Create topic
        response = requests.post(
            f"{base_url}/api/v3/topics/create",
            json=test_topic,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        assert response.status_code == 201
        topic_response = response.json()
        created_topic_id = topic_response.get('session_id')
        assert created_topic_id is not None
        
        # Cleanup: Delete the test topic
        delete_response = requests.delete(
            f"{base_url}/api/v3/topics/{created_topic_id}",
            timeout=10
        )
        assert delete_response.status_code in [200, 204]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

