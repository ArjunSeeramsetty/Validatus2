#!/usr/bin/env python3
"""
End-to-End Topic Integration Tests
Consolidated from: test_topic_integration.py, test_topic_integration_simple.py
Tests complete topic workflow from frontend to backend
"""
import pytest
import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


class TestTopicIntegration:
    """Test end-to-end topic integration"""
    
    def test_api_endpoints(self):
        """Test various API endpoints"""
        endpoints = [
            "/health",
            "/api/v3/topics/analysis-types/",
            "/api/v3/topics/statuses/",
            "/api/v3/topics/stats/overview"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
    
    def test_frontend_connectivity(self):
        """Test frontend connectivity"""
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend not running")
    
    def test_complete_topic_workflow(self):
        """Test complete topic workflow"""
        # Create topic
        topic_data = {
            "topic": "E2E Integration Test Topic",
            "description": "Testing complete integration",
            "search_queries": ["integration testing", "topic management"],
            "initial_urls": ["https://example.com/test1"],
            "analysis_type": "comprehensive",
            "user_id": "test_user_123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v3/topics/",
            json=topic_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 201
        session_id = response.json()['session_id']
        
        try:
            # Retrieve topic
            response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
            assert response.status_code == 200
            topic = response.json()
            assert topic['topic'] == topic_data['topic']
            
            # Update topic
            update_data = {
                "topic": "Updated E2E Test Topic",
                "description": "Updated description",
                "status": "in_progress"
            }
            response = requests.put(
                f"{BASE_URL}/api/v3/topics/{session_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            assert response.status_code == 200
            updated_topic = response.json()
            assert updated_topic['topic'] == update_data['topic']
            
            # Delete topic
            response = requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
            assert response.status_code in [200, 204]
            
            # Verify deletion
            response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
            assert response.status_code == 404
            
        except AssertionError:
            # Cleanup on failure
            try:
                requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
            except Exception:
                pass
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

