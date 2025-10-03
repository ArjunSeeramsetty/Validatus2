"""
Configuration and fixtures for GCP Persistence tests
"""
import pytest
import asyncio
import os
from typing import Dict, Any

# Set test environment variables
os.environ["LOCAL_DEVELOPMENT_MODE"] = "true"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["CONTENT_STORAGE_BUCKET"] = "test-content-bucket"
os.environ["EMBEDDINGS_STORAGE_BUCKET"] = "test-embeddings-bucket"
os.environ["REPORTS_STORAGE_BUCKET"] = "test-reports-bucket"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["LOCAL_POSTGRES_URL"] = "postgresql://postgres:password@localhost:5432/validatus_test"
os.environ["LOCAL_REDIS_URL"] = "redis://localhost:6379/1"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_settings():
    """Test configuration settings"""
    return {
        "project_id": "test-project",
        "region": "us-central1",
        "local_development_mode": True,
        "content_storage_bucket": "test-content-bucket",
        "embeddings_storage_bucket": "test-embeddings-bucket",
        "reports_storage_bucket": "test-reports-bucket",
        "redis_host": "localhost",
        "redis_port": 6379,
        "local_postgres_url": "postgresql://postgres:password@localhost:5432/validatus_test",
        "local_redis_url": "redis://localhost:6379/1"
    }

@pytest.fixture
async def mock_gcp_services():
    """Mock GCP services for testing"""
    return {
        "storage": True,
        "sql": True,
        "redis": True,
        "vector": True,
        "spanner": True
    }

@pytest.fixture
def sample_topic_data():
    """Sample topic data for testing"""
    return {
        "topic": "Test Market Analysis",
        "description": "Testing GCP persistence integration",
        "search_queries": ["market analysis", "industry trends"],
        "initial_urls": ["https://example.com/page1", "https://example.com/page2"],
        "user_id": "test_user_123",
        "metadata": {"test": True, "environment": "pytest"}
    }

@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing"""
    return {
        "session_id": "test_workflow_session",
        "user_id": "test_user_workflow",
        "stages": {
            "url_collection": {"status": "completed", "urls_collected": 25},
            "url_scraping": {"status": "completed", "documents_processed": 20},
            "vector_creation": {"status": "completed", "embeddings_created": 150},
            "analysis": {"status": "completed", "confidence_score": 0.85}
        },
        "overall_status": "completed"
    }

@pytest.fixture
def sample_analysis_results():
    """Sample analysis results for testing"""
    return {
        "analysis_id": "test_analysis_123",
        "overall_score": 0.82,
        "confidence_score": 0.88,
        "factor_scores": {
            "market_potential": 0.85,
            "competitive_advantage": 0.79,
            "growth_opportunity": 0.83
        },
        "processing_time_ms": 15000,
        "data_points_analyzed": 250
    }

# Test markers
pytest.mark.gcp_persistence = pytest.mark.gcp_persistence
pytest.mark.storage = pytest.mark.storage
pytest.mark.sql = pytest.mark.sql
pytest.mark.redis = pytest.mark.redis
pytest.mark.vector = pytest.mark.vector
pytest.mark.spanner = pytest.mark.spanner
pytest.mark.integration = pytest.mark.integration
