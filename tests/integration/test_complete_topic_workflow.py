#!/usr/bin/env python3
"""
Complete Topic Workflow Integration Tests
Consolidated from: test_complete_topic_workflow_simple.py
Tests the end-to-end topic workflow with proper status tracking
"""
import pytest
import requests
import time
from typing import Optional

BASE_URL = "http://localhost:8000"


class TestCompleteTopicWorkflow:
    """Test complete topic workflow from creation to analysis"""
    
    @pytest.fixture
    def created_topic_id(self) -> Optional[str]:
        """Fixture to create a topic and clean it up after tests"""
        session_id = None
        yield session_id
        # Cleanup after test
        if session_id:
            try:
                requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
            except Exception:
                pass
    
    def test_topic_creation(self):
        """Test creating a topic"""
        create_data = {
            "topic": "Pergola Market Analysis 2025",
            "description": "Comprehensive strategic analysis of the global pergola market",
            "search_queries": [
                "pergola market size forecast",
                "outdoor living trends 2025",
                "bioclimatic pergola industry"
            ],
            "initial_urls": [
                "https://www.example.com/pergola-market",
                "https://www.example.com/bioclimatic-pergola"
            ],
            "analysis_type": "comprehensive",
            "user_id": "demo_user_123",
            "metadata": {
                "case_study": "pergola_analysis",
                "priority": "high"
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/v3/topics/", json=create_data, timeout=10)
        assert response.status_code == 201
        
        topic_data = response.json()
        assert 'session_id' in topic_data
        assert topic_data['topic'] == create_data['topic']
        assert 'status' in topic_data
        
        return topic_data['session_id']
    
    def test_topic_lifecycle(self):
        """Test complete topic lifecycle"""
        # 1. Create Topic
        create_data = {
            "topic": "Test Topic Lifecycle",
            "description": "Testing complete lifecycle",
            "search_queries": ["test"],
            "initial_urls": [],
            "analysis_type": "standard",
            "user_id": "test_user_123"
        }
        
        response = requests.post(f"{BASE_URL}/api/v3/topics/", json=create_data, timeout=10)
        assert response.status_code == 201
        session_id = response.json()['session_id']
        
        try:
            # 2. List Topics
            response = requests.get(f"{BASE_URL}/api/v3/topics/", timeout=10)
            assert response.status_code == 200
            topics_data = response.json()
            assert topics_data['total'] > 0
            
            # 3. Get Specific Topic
            response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
            assert response.status_code == 200
            topic_detail = response.json()
            assert topic_detail['session_id'] == session_id
            
            # 4. Update Status
            response = requests.put(
                f"{BASE_URL}/api/v3/topics/{session_id}/status",
                params={"status": "in_progress"},
                json={"progress_data": {"stage": "scraping"}},
                timeout=10
            )
            assert response.status_code == 200
            
            # 5. Get Topics by Status
            response = requests.get(f"{BASE_URL}/api/v3/topics/status/in_progress", timeout=10)
            assert response.status_code == 200
            filtered_topics = response.json()
            assert isinstance(filtered_topics, list)
            
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

