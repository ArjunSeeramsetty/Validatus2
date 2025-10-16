#!/usr/bin/env python3
"""
Web Search and URL Collection Integration Tests
Consolidated from: test_websearch_functionality.py
Tests all requirements for the URLs tab implementation
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"


class TestWebSearchFunctionality:
    """Test web search and URL collection functionality"""
    
    @pytest.fixture
    def test_topic(self):
        """Create a test topic for websearch tests"""
        topic_data = {
            "topic": "AI Market Trends 2025",
            "description": "Comprehensive analysis of artificial intelligence market trends",
            "search_queries": [
                "AI market size forecast 2025",
                "artificial intelligence industry trends",
                "machine learning market growth"
            ],
            "initial_urls": [
                "https://example.com/ai-trends-2025",
                "https://research.com/ai-market-analysis"
            ],
            "analysis_type": "comprehensive",
            "user_id": "demo_user_123",
            "metadata": {"test_case": "websearch_functionality"}
        }
        
        response = requests.post(f"{BASE_URL}/api/v3/topics/", json=topic_data, timeout=10)
        assert response.status_code == 201
        session_id = response.json()["session_id"]
        
        yield session_id
        
        # Cleanup
        try:
            requests.delete(f"{BASE_URL}/api/v3/topics/{session_id}", timeout=10)
        except Exception:
            pass
    
    def test_initial_urls(self, test_topic):
        """Test getting initial URLs"""
        response = requests.get(f"{BASE_URL}/api/v3/topics/{test_topic}/urls", timeout=10)
        assert response.status_code == 200
        urls_data = response.json()
        assert urls_data['url_count'] >= 2  # At least initial URLs
        assert isinstance(urls_data['urls'], list)
    
    def test_url_collection(self, test_topic):
        """Test collecting additional URLs"""
        response = requests.post(f"{BASE_URL}/api/v3/topics/{test_topic}/collect-urls", timeout=30)
        assert response.status_code == 200
        collection_result = response.json()
        assert 'urls_collected' in collection_result
        assert 'total_urls' in collection_result
        assert 'status' in collection_result
        assert collection_result['status'] in ['success', 'completed', 'in_progress']
    
    def test_multiple_collections(self, test_topic):
        """Test multiple URL collections for the same topic"""
        # First collection
        response1 = requests.post(f"{BASE_URL}/api/v3/topics/{test_topic}/collect-urls", timeout=30)
        assert response1.status_code == 200
        result1 = response1.json()
        total1 = result1['total_urls']
        
        # Second collection
        response2 = requests.post(f"{BASE_URL}/api/v3/topics/{test_topic}/collect-urls", timeout=30)
        assert response2.status_code == 200
        result2 = response2.json()
        total2 = result2['total_urls']
        
        # Total should be greater or equal (no duplicates)
        assert total2 >= total1
    
    def test_url_persistence(self, test_topic):
        """Test that collected URLs persist"""
        # Collect URLs
        requests.post(f"{BASE_URL}/api/v3/topics/{test_topic}/collect-urls", timeout=30)
        
        # Get URLs
        response1 = requests.get(f"{BASE_URL}/api/v3/topics/{test_topic}/urls", timeout=10)
        urls1 = response1.json()['urls']
        
        # Get URLs again
        response2 = requests.get(f"{BASE_URL}/api/v3/topics/{test_topic}/urls", timeout=10)
        urls2 = response2.json()['urls']
        
        # Should be the same
        assert urls1 == urls2
    
    def test_error_handling(self):
        """Test error scenarios"""
        fake_session_id = "non_existent_topic_123"
        
        # Test with non-existent topic
        response = requests.get(f"{BASE_URL}/api/v3/topics/{fake_session_id}/urls", timeout=10)
        assert response.status_code == 404
        
        # Test URL collection for non-existent topic
        response = requests.post(f"{BASE_URL}/api/v3/topics/{fake_session_id}/collect-urls", timeout=10)
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

