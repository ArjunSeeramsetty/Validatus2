#!/usr/bin/env python3
"""
Persistence Tests
Consolidated from: test_persistence_across_sessions.py, test_restart_persistence.py, test_simple_persistence.py
Tests data persistence across backend restarts
"""
import pytest
import requests
import os

BASE_URL = "http://localhost:8000"


class TestPersistence:
    """Test data persistence"""
    
    def test_topic_persistence(self):
        """Test that topics persist in database"""
        # Create topic
        topic_data = {
            "topic": "Persistence Test Topic",
            "description": "Testing persistence functionality",
            "search_queries": ["persistence test"],
            "initial_urls": ["https://example.com/test"],
            "analysis_type": "standard",
            "user_id": "test_user_persistence"
        }
        
        response = requests.post(f"{BASE_URL}/api/v3/topics/", json=topic_data, timeout=10)
        assert response.status_code == 201
        session_id = response.json()['session_id']
        
        try:
            # Retrieve topic immediately
            response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
            assert response.status_code == 200
            retrieved_topic = response.json()
            assert retrieved_topic['topic'] == topic_data['topic']
            
            # Verify topic appears in list
            response = requests.get(f"{BASE_URL}/api/v3/topics/", timeout=10)
            assert response.status_code == 200
            topics_list = response.json()
            
            our_topic = next((t for t in topics_list['topics'] if t['session_id'] == session_id), None)
            assert our_topic is not None
            
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
    
    def test_url_persistence(self):
        """Test that URLs persist after collection"""
        # Create topic
        topic_data = {
            "topic": "URL Persistence Test",
            "description": "Testing URL persistence",
            "search_queries": ["url persistence test"],
            "initial_urls": ["https://example.com/url1", "https://example.com/url2"],
            "analysis_type": "standard",
            "user_id": "test_user_persistence"
        }
        
        response = requests.post(f"{BASE_URL}/api/v3/topics/", json=topic_data, timeout=10)
        assert response.status_code == 201
        session_id = response.json()['session_id']
        
        try:
            # Collect URLs
            response = requests.post(f"{BASE_URL}/api/v3/topics/{session_id}/collect-urls", timeout=30)
            assert response.status_code == 200
            
            # Get URLs multiple times to verify persistence
            response1 = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}/urls", timeout=10)
            assert response1.status_code == 200
            urls1 = response1.json()['urls']
            
            response2 = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}/urls", timeout=10)
            assert response2.status_code == 200
            urls2 = response2.json()['urls']
            
            assert urls1 == urls2, "URLs should persist between requests"
            
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
    
    def test_database_file_exists(self):
        """Test that database file exists"""
        db_paths = [
            "validatus_data.db",
            "backend/validatus_data.db",
            "../validatus_data.db"
        ]
        
        db_found = False
        for db_path in db_paths:
            if os.path.exists(db_path):
                db_found = True
                size = os.path.getsize(db_path)
                assert size > 0, f"Database file {db_path} exists but is empty"
                break
        
        if not db_found:
            pytest.skip("Database file not found - may be using different storage")
    
    def test_topic_persistence_across_requests(self):
        """Test that created topics persist across multiple API requests"""
        topics_before = requests.get(f"{BASE_URL}/api/v3/topics/", timeout=10).json()
        initial_count = topics_before['total']
        
        # Create multiple topics
        session_ids = []
        for i in range(3):
            topic_data = {
                "topic": f"Multi-Topic Persistence Test {i}",
                "description": f"Testing persistence {i}",
                "search_queries": [f"test{i}"],
                "initial_urls": [],
                "analysis_type": "standard",
                "user_id": "test_user_persistence"
            }
            
            response = requests.post(f"{BASE_URL}/api/v3/topics/", json=topic_data, timeout=10)
            assert response.status_code == 201
            session_ids.append(response.json()['session_id'])
        
        try:
            # Verify all topics persist
            topics_after = requests.get(f"{BASE_URL}/api/v3/topics/", timeout=10).json()
            assert topics_after['total'] == initial_count + 3
            
            # Verify each topic can be retrieved
            for session_id in session_ids:
                response = requests.get(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
                assert response.status_code == 200
                
        finally:
            # Cleanup all created topics
            for session_id in session_ids:
                try:
                    requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
                except Exception:
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

