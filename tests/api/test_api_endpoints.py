# tests/api/test_api_endpoints.py

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from backend.app.main import app
from backend.app.models.analysis_models import AnalysisSession, LayerScore, FactorCalculation

class TestAPIEndpoints:
    """Comprehensive API endpoint testing suite"""
    
    @pytest.fixture
    def client(self):
        """Create FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_urls(self):
        """Sample URLs for testing"""
        return [
            "https://example.com/article1",
            "https://example.com/article2",
            "https://example.com/article3"
        ]
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing"""
        return [
            {
                "content": "This is a test document about artificial intelligence.",
                "url": "https://example.com/doc1",
                "title": "AI Test Document"
            },
            {
                "content": "Another test document about machine learning algorithms.",
                "url": "https://example.com/doc2", 
                "title": "ML Test Document"
            }
        ]
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    # Phase 1 API Tests
    
    def test_list_topics_endpoint(self, client):
        """Test list topics endpoint"""
        with patch('backend.app.main.topic_manager') as mock_manager:
            mock_manager.get_all_topics = AsyncMock(return_value=["ai", "ml", "data-science"])
            
            response = client.get("/api/v3/topics")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "topics" in data
            assert len(data["topics"]) == 3
    
    def test_create_topic_endpoint(self, client, sample_urls):
        """Test create topic endpoint"""
        with patch('backend.app.main.topic_manager') as mock_manager:
            mock_manager.create_topic_store = AsyncMock(return_value="topic_123")
            
            response = client.post("/api/v3/topics/create", json={
                "topic": "artificial intelligence",
                "urls": sample_urls
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["topic_id"] == "topic_123"
            assert data["url_count"] == len(sample_urls)
    
    def test_collect_urls_endpoint(self, client):
        """Test collect URLs endpoint"""
        with patch('backend.app.main.url_orchestrator') as mock_orchestrator:
            mock_orchestrator.collect_urls = AsyncMock(return_value={
                "urls": ["https://example.com/url1", "https://example.com/url2"],
                "total_collected": 2
            })
            
            response = client.post("/api/v3/topics/ai/collect-urls", json={
                "search_query": "artificial intelligence",
                "max_urls": 10
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total_collected"] == 2
            assert len(data["urls"]) == 2
    
    def test_get_evidence_endpoint(self, client):
        """Test get evidence endpoint"""
        with patch('backend.app.main.topic_manager') as mock_manager:
            mock_manager.retrieve_evidence = AsyncMock(return_value={
                "evidence": ["evidence1", "evidence2"],
                "layer": "consumer",
                "total_count": 2
            })
            
            response = client.get("/api/v3/topics/ai/evidence/consumer")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["layer"] == "consumer"
            assert len(data["evidence"]) == 2
    
    # Phase 2 Enhanced API Tests
    
    def test_create_enhanced_topic_endpoint(self, client, sample_urls):
        """Test create enhanced topic endpoint"""
        with patch('backend.app.main.enhanced_topic_manager') as mock_manager:
            mock_manager.create_enhanced_topic_store = AsyncMock(return_value="enhanced_topic_123")
            
            response = client.post("/api/v3/enhanced/topics/create", json={
                "topic": "artificial intelligence",
                "urls": sample_urls,
                "quality_threshold": 0.7
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["topic_id"] == "enhanced_topic_123"
            assert data["quality_threshold"] == 0.7
    
    def test_get_enhanced_topic_knowledge_endpoint(self, client):
        """Test get enhanced topic knowledge endpoint"""
        with patch('backend.app.main.enhanced_topic_manager') as mock_manager:
            mock_manager.retrieve_topic_knowledge = AsyncMock(return_value={
                "topic": "ai",
                "knowledge_base": "enhanced_knowledge",
                "metadata": {"quality_score": 0.85}
            })
            
            response = client.get("/api/v3/enhanced/topics/ai/knowledge")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["topic"] == "ai"
            assert "knowledge" in data
    
    def test_update_enhanced_topic_endpoint(self, client, sample_urls):
        """Test update enhanced topic endpoint"""
        with patch('backend.app.main.enhanced_topic_manager') as mock_manager:
            mock_manager.update_topic_store = AsyncMock(return_value={
                "updated_documents": 5,
                "quality_improvement": 0.1
            })
            
            response = client.put("/api/v3/enhanced/topics/ai/update", json={
                "new_urls": sample_urls,
                "quality_threshold": 0.8
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["topic"] == "ai"
            assert "update_result" in data
    
    def test_analyze_topic_performance_endpoint(self, client):
        """Test analyze topic performance endpoint"""
        with patch('backend.app.main.enhanced_topic_manager') as mock_manager:
            mock_manager.analyze_topic_performance = AsyncMock(return_value={
                "performance_metrics": {"throughput": 100, "accuracy": 0.95},
                "recommendations": ["optimize cache", "increase batch size"]
            })
            
            response = client.get("/api/v3/enhanced/topics/ai/performance")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["topic"] == "ai"
            assert "performance_analysis" in data
    
    # Strategic Analysis API Tests
    
    def test_create_analysis_session_endpoint(self, client):
        """Test create analysis session endpoint"""
        with patch('backend.app.main.analysis_session_manager') as mock_manager:
            mock_manager.create_analysis_session = AsyncMock(return_value="session_123")
            
            response = client.post("/api/v3/analysis/sessions/create", json={
                "topic": "artificial intelligence",
                "user_id": "user_123",
                "analysis_parameters": {"quality_threshold": 0.7}
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "session_123"
            assert data["topic"] == "artificial intelligence"
    
    def test_execute_strategic_analysis_endpoint(self, client):
        """Test execute strategic analysis endpoint"""
        with patch('backend.app.main.analysis_session_manager') as mock_manager:
            mock_manager.execute_strategic_analysis = AsyncMock(return_value={
                "status": "processing",
                "estimated_completion": "2024-01-01T12:00:00Z"
            })
            
            response = client.post("/api/v3/analysis/sessions/session_123/execute")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "session_123"
            assert data["status"] == "processing"
    
    def test_get_analysis_session_status_endpoint(self, client):
        """Test get analysis session status endpoint"""
        with patch('backend.app.main.analysis_session_manager') as mock_manager:
            mock_manager.get_session_status = AsyncMock(return_value={
                "status": "completed",
                "progress_percentage": 100.0,
                "current_stage": "finalization"
            })
            
            response = client.get("/api/v3/analysis/sessions/session_123/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "session_123"
            assert data["status"]["status"] == "completed"
    
    def test_get_analysis_results_endpoint(self, client):
        """Test get analysis results endpoint"""
        with patch('backend.app.main.analysis_session_manager') as mock_manager:
            mock_manager.get_analysis_results = AsyncMock(return_value={
                "session_id": "session_123",
                "analysis_results": {
                    "layer_scores": [{"layer": "consumer", "score": 0.85}],
                    "factor_calculations": [{"factor": "market_attractiveness", "value": 0.78}],
                    "segment_scores": [{"segment": "growth", "score": 0.82}]
                }
            })
            
            response = client.get("/api/v3/analysis/sessions/session_123/results")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "session_123"
            assert "results" in data
    
    # Content Processing API Tests
    
    def test_analyze_content_quality_endpoint(self, client):
        """Test analyze content quality endpoint"""
        with patch('backend.app.main.quality_analyzer') as mock_analyzer:
            mock_analyzer.analyze_content_quality = AsyncMock(return_value={
                "overall_score": 0.85,
                "topic_relevance": 0.9,
                "readability": 0.8,
                "domain_authority": 0.85
            })
            
            response = client.post("/api/v3/content/analyze-quality", json={
                "content": "This is a test article about AI.",
                "url": "https://example.com/test",
                "topic": "artificial intelligence"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["url"] == "https://example.com/test"
            assert "quality_scores" in data
            assert data["quality_scores"]["overall_score"] == 0.85
    
    def test_deduplicate_content_endpoint(self, client, sample_documents):
        """Test deduplicate content endpoint"""
        with patch('backend.app.main.deduplication_service') as mock_service:
            mock_service.deduplicate_content_batch = AsyncMock(return_value=(
                sample_documents[:1],  # Return only first document
                {"duplicates_removed": 1, "similarity_threshold": 0.85}
            ))
            
            response = client.post("/api/v3/content/deduplicate", json={
                "documents": sample_documents,
                "similarity_threshold": 0.85
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["original_count"] == len(sample_documents)
            assert data["deduplicated_count"] == 1
            assert data["duplicates_removed"] == 1
    
    def test_optimize_parallel_processing_endpoint(self, client):
        """Test optimize parallel processing endpoint"""
        with patch('backend.app.main.optimization_service') as mock_service:
            mock_service.optimize_parallel_processing = AsyncMock(return_value=[
                {"task_id": "task_1", "result": "success"},
                {"task_id": "task_2", "result": "success"}
            ])
            
            analysis_tasks = [
                {"id": "task_1", "type": "layer_scoring"},
                {"id": "task_2", "type": "factor_calculation"}
            ]
            
            response = client.post("/api/v3/optimization/parallel-processing", json={
                "analysis_tasks": analysis_tasks,
                "max_concurrent": 5
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["original_task_count"] == 2
            assert data["processed_task_count"] == 2
    
    # Error Handling Tests
    
    def test_missing_service_error(self, client):
        """Test error handling when services are not initialized"""
        with patch('backend.app.main.enhanced_topic_manager', None):
            response = client.post("/api/v3/enhanced/topics/create", json={
                "topic": "test",
                "urls": ["https://example.com"]
            })
            
            assert response.status_code == 503
            data = response.json()
            assert "not initialized" in data["detail"]
    
    def test_invalid_request_data(self, client):
        """Test error handling for invalid request data"""
        response = client.post("/api/v3/topics/create", json={
            "topic": "",  # Empty topic
            "urls": []    # Empty URLs
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_nonexistent_session_error(self, client):
        """Test error handling for nonexistent session"""
        with patch('backend.app.main.analysis_session_manager') as mock_manager:
            mock_manager.get_session_status = AsyncMock(side_effect=Exception("Session not found"))
            
            response = client.get("/api/v3/analysis/sessions/nonexistent_session/status")
            
            assert response.status_code == 500
            data = response.json()
            assert "Session not found" in data["detail"]
    
    # Authentication and Authorization Tests (if implemented)
    
    def test_endpoint_without_auth(self, client):
        """Test that endpoints work without authentication (for now)"""
        response = client.get("/api/v3/topics")
        assert response.status_code == 200  # Should work without auth
    
    # Performance Tests
    
    def test_endpoint_response_time(self, client):
        """Test that endpoints respond within acceptable time"""
        import time
        
        with patch('backend.app.main.topic_manager') as mock_manager:
            mock_manager.get_all_topics = AsyncMock(return_value=["ai", "ml"])
            
            start_time = time.time()
            response = client.get("/api/v3/topics")
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0  # Should respond within 1 second
    
    # Input Validation Tests
    
    def test_url_validation(self, client):
        """Test URL validation in endpoints"""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Unsupported protocol
            "javascript:alert('xss')"  # Potential XSS
        ]
        
        response = client.post("/api/v3/topics/create", json={
            "topic": "test",
            "urls": invalid_urls
        })
        
        # Should either accept and filter or reject with validation error
        assert response.status_code in [200, 422]
    
    def test_topic_name_validation(self, client):
        """Test topic name validation"""
        invalid_topics = [
            "",  # Empty
            "a" * 1000,  # Too long
            "<script>alert('xss')</script>",  # XSS attempt
            "../../etc/passwd"  # Path traversal attempt
        ]
        
        for invalid_topic in invalid_topics:
            response = client.post("/api/v3/topics/create", json={
                "topic": invalid_topic,
                "urls": ["https://example.com"]
            })
            
            # Should reject invalid topics
            assert response.status_code in [422, 400]
    
    # Concurrent Request Tests
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch('backend.app.main.topic_manager') as mock_manager:
                mock_manager.get_all_topics = AsyncMock(return_value=["ai", "ml"])
                response = client.get("/api/v3/topics")
                results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
