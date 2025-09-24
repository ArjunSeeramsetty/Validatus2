"""
Pytest configuration and shared fixtures for Validatus testing suite.
"""

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Generator
import os
import sys
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test configuration
TEST_CONFIG = {
    "project_id": "validatus-test",
    "environment": "test",
    "gcp_enabled": False,  # Disable GCP services for testing
    "redis_enabled": False,
    "memcached_enabled": False,
    "firestore_enabled": False,
    "monitoring_enabled": False
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_gcp_settings():
    """Mock GCP settings for testing."""
    mock_settings = Mock()
    mock_settings.project_id = TEST_CONFIG["project_id"]
    mock_settings.environment = TEST_CONFIG["environment"]
    mock_settings.local_development_mode = True
    mock_settings.region = "us-central1"
    mock_settings.allowed_origins = ["http://localhost:3000", "http://localhost:8080"]
    return mock_settings

@pytest.fixture
def mock_feature_flags():
    """Mock feature flags for testing."""
    with patch('app.core.feature_flags.FeatureFlags') as mock_flags:
        mock_flags.ADVANCED_ORCHESTRATION_ENABLED = True
        mock_flags.CIRCUIT_BREAKER_ENABLED = True
        mock_flags.MULTI_LEVEL_CACHE_ENABLED = True
        mock_flags.REDIS_CACHE_ENABLED = False
        mock_flags.COMPREHENSIVE_MONITORING_ENABLED = True
        mock_flags.is_phase_e_enabled.return_value = True
        mock_flags.get_all_flags.return_value = {
            "advanced_orchestration": True,
            "circuit_breaker": True,
            "multi_level_cache": True,
            "redis_cache": False,
            "comprehensive_monitoring": True
        }
        yield mock_flags

@pytest.fixture
def mock_gcp_clients():
    """Mock GCP clients for testing."""
    with patch.multiple(
        'google.cloud',
        monitoring_v3=Mock(),
        pubsub_v1=Mock(),
        firestore=Mock(),
        storage=Mock(),
        error_reporting=Mock()
    ) as mock_clients:
        yield mock_clients

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch('redis.asyncio.Redis') as mock_redis:
        mock_redis_instance = AsyncMock()
        mock_redis_instance.ping = AsyncMock(return_value=True)
        mock_redis_instance.get = AsyncMock(return_value=None)
        mock_redis_instance.setex = AsyncMock(return_value=True)
        mock_redis_instance.delete = AsyncMock(return_value=1)
        mock_redis_instance.flushdb = AsyncMock(return_value=True)
        mock_redis_instance.dbsize = AsyncMock(return_value=0)
        mock_redis_instance.scan_iter = AsyncMock(return_value=iter([]))
        mock_redis.return_value = mock_redis_instance
        yield mock_redis_instance

@pytest.fixture
def sample_analysis_config():
    """Sample analysis configuration for testing."""
    return {
        "topic": "test_topic",
        "user_id": "test_user_123",
        "analysis_type": "strategic",
        "parameters": {
            "depth": "comprehensive",
            "include_predictions": True,
            "use_enhanced_analytics": True
        },
        "session_metadata": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0"
        }
    }

@pytest.fixture
def sample_factor_results():
    """Sample factor analysis results for testing."""
    return {
        "F1_market_size": {
            "formula_name": "market_size_analysis",
            "raw_score": 0.75,
            "normalized_score": 0.82,
            "confidence": 0.88,
            "calculation_steps": [
                {"step": "market_research", "value": 0.75},
                {"step": "normalization", "value": 0.82}
            ],
            "metadata": {
                "weight": 0.15,
                "description": "Total Addressable Market analysis",
                "calculation_timestamp": datetime.now(timezone.utc).isoformat()
            }
        },
        "F2_market_growth": {
            "formula_name": "growth_rate_analysis",
            "raw_score": 0.68,
            "normalized_score": 0.71,
            "confidence": 0.85,
            "calculation_steps": [
                {"step": "growth_calculation", "value": 0.68},
                {"step": "normalization", "value": 0.71}
            ],
            "metadata": {
                "weight": 0.12,
                "description": "Market growth rate analysis",
                "calculation_timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    }

@pytest.fixture
def sample_cache_data():
    """Sample cache data for testing."""
    return {
        "analysis_results": {
            "session_id": "test_session_123",
            "topic": "test_topic",
            "results": {"status": "completed", "score": 0.85},
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "knowledge_base": {
            "topic": "test_topic",
            "documents": ["doc1", "doc2", "doc3"],
            "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "metadata": {"source": "test", "last_updated": datetime.now(timezone.utc).isoformat()}
        }
    }

@pytest.fixture
def mock_async_context_manager():
    """Mock async context manager for testing."""
    class MockAsyncContextManager:
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
    
    return MockAsyncContextManager()

@pytest.fixture
def performance_test_config():
    """Configuration for performance testing."""
    return {
        "concurrent_requests": 100,
        "duration_seconds": 60,
        "ramp_up_seconds": 10,
        "target_response_time_ms": 1000,
        "error_rate_threshold": 0.05,
        "cache_hit_ratio_threshold": 0.8
    }

@pytest.fixture
def load_test_scenarios():
    """Load test scenarios for different phases."""
    return {
        "phase_b_analysis": {
            "endpoint": "/api/v3/analysis/enhanced",
            "payload": {
                "session_id": "load_test_session",
                "topic": "load_test_topic",
                "user_id": "load_test_user",
                "enhanced_options": {"use_all_engines": True}
            },
            "expected_response_time_ms": 5000,
            "concurrent_users": 50
        },
        "phase_c_comprehensive": {
            "endpoint": "/api/v3/analysis/comprehensive",
            "payload": {
                "session_id": "load_test_session",
                "topic": "load_test_topic",
                "user_id": "load_test_user",
                "analysis_options": {"include_bayesian": True}
            },
            "expected_response_time_ms": 10000,
            "concurrent_users": 25
        },
        "phase_e_orchestration": {
            "endpoint": "/api/v3/orchestration/health",
            "payload": {},
            "expected_response_time_ms": 500,
            "concurrent_users": 100
        }
    }

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "phase_a: mark test as Phase A (Stabilization) test"
    )
    config.addinivalue_line(
        "markers", "phase_b: mark test as Phase B (Enhanced Analytics) test"
    )
    config.addinivalue_line(
        "markers", "phase_c: mark test as Phase C (Data Pipeline) test"
    )
    config.addinivalue_line(
        "markers", "phase_d: mark test as Phase D (Frontend Enhancement) test"
    )
    config.addinivalue_line(
        "markers", "phase_e: mark test as Phase E (Advanced Orchestration) test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "gcp: mark test as requiring GCP services"
    )
