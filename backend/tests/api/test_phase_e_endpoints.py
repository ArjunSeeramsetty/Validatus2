"""
API tests for Phase E endpoints.

Tests advanced orchestration, multi-level caching, and enhanced optimization endpoints.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app


@pytest.mark.api
@pytest.mark.phase_e
class TestPhaseEEndpoints:
    """Test suite for Phase E API endpoints."""

    @pytest.fixture
    def client(self, mock_feature_flags, mock_gcp_clients):
        """Create a test client with mocked dependencies."""
        with patch('app.main.FeatureFlags') as mock_flags:
            mock_flags.ADVANCED_ORCHESTRATION_ENABLED = True
            mock_flags.CIRCUIT_BREAKER_ENABLED = True
            mock_flags.MULTI_LEVEL_CACHE_ENABLED = True
            mock_flags.REDIS_CACHE_ENABLED = False
            mock_flags.COMPREHENSIVE_MONITORING_ENABLED = True
            mock_flags.is_phase_e_enabled.return_value = True
            
            return TestClient(app)

    @pytest.mark.asyncio
    async def test_orchestration_health_endpoint(self, client):
        """Test orchestration health endpoint."""
        response = client.get("/api/v3/orchestration/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'timestamp' in data
        assert 'overall_status' in data
        assert 'circuit_breakers' in data
        assert 'bulkhead_pools' in data
        assert 'operation_metrics' in data
        
        # Check status values
        assert data['overall_status'] in ['healthy', 'degraded', 'unhealthy']
        
        # Check circuit breaker status
        assert isinstance(data['circuit_breakers'], dict)
        
        # Check bulkhead pool status
        assert isinstance(data['bulkhead_pools'], dict)
        expected_pools = [
            'analysis_execution', 'knowledge_loading', 'content_processing',
            'vector_operations', 'ai_model_inference'
        ]
        for pool in expected_pools:
            assert pool in data['bulkhead_pools']

    @pytest.mark.asyncio
    async def test_cache_performance_endpoint(self, client):
        """Test cache performance endpoint."""
        response = client.get("/api/v3/cache/performance")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'timestamp' in data
        assert 'overall_performance' in data
        assert 'cache_levels' in data
        assert 'hit_rates' in data
        assert 'performance_metrics' in data
        
        # Check cache levels
        cache_levels = data['cache_levels']
        assert 'l1' in cache_levels
        assert 'l2' in cache_levels
        assert 'l3' in cache_levels
        assert 'l4' in cache_levels
        
        # Check hit rates
        hit_rates = data['hit_rates']
        assert 'overall_hit_rate' in hit_rates
        assert 'l1_hit_rate' in hit_rates
        assert 'l2_hit_rate' in hit_rates
        assert 'l3_hit_rate' in hit_rates
        assert 'l4_hit_rate' in hit_rates
        
        # Validate hit rate values
        assert 0 <= hit_rates['overall_hit_rate'] <= 1
        assert 0 <= hit_rates['l1_hit_rate'] <= 1
        assert 0 <= hit_rates['l2_hit_rate'] <= 1
        assert 0 <= hit_rates['l3_hit_rate'] <= 1
        assert 0 <= hit_rates['l4_hit_rate'] <= 1

    @pytest.mark.asyncio
    async def test_cache_invalidation_endpoint(self, client):
        """Test cache invalidation endpoint."""
        # Test single key invalidation
        payload = {
            "invalidation_type": "key",
            "key": "test_key"
        }
        
        response = client.post("/api/v3/cache/invalidate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'timestamp' in data
        assert 'invalidation_result' in data
        assert 'keys_invalidated' in data
        assert 'pattern_matched' in data
        
        # Test pattern-based invalidation
        pattern_payload = {
            "invalidation_type": "pattern",
            "pattern": "test_*",
            "cache_levels": ["l1", "l2"]
        }
        
        response = client.post("/api/v3/cache/invalidate", json=pattern_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'invalidation_result' in data
        assert 'pattern_matched' in data
        assert 'cache_levels_processed' in data

    @pytest.mark.asyncio
    async def test_enhanced_optimization_metrics_endpoint(self, client):
        """Test enhanced optimization metrics endpoint."""
        response = client.get("/api/v3/optimization/enhanced-metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'timestamp' in data
        assert 'optimization_status' in data
        assert 'performance_metrics' in data
        assert 'circuit_breaker_metrics' in data
        assert 'cache_optimization' in data
        assert 'system_health' in data
        
        # Check optimization status
        optimization_status = data['optimization_status']
        assert 'overall_status' in optimization_status
        assert 'active_optimizations' in optimization_status
        assert 'performance_score' in optimization_status
        
        # Check performance metrics
        performance_metrics = data['performance_metrics']
        assert 'avg_response_time' in performance_metrics
        assert 'throughput' in performance_metrics
        assert 'error_rate' in performance_metrics
        assert 'resource_utilization' in performance_metrics
        
        # Check circuit breaker metrics
        circuit_breaker_metrics = data['circuit_breaker_metrics']
        assert 'total_circuits' in circuit_breaker_metrics
        assert 'open_circuits' in circuit_breaker_metrics
        assert 'half_open_circuits' in circuit_breaker_metrics
        assert 'closed_circuits' in circuit_breaker_metrics

    @pytest.mark.asyncio
    async def test_cache_invalidation_validation(self, client):
        """Test cache invalidation endpoint validation."""
        # Test invalid payload
        invalid_payload = {
            "invalidation_type": "invalid_type"
        }
        
        response = client.post("/api/v3/cache/invalidate", json=invalid_payload)
        
        assert response.status_code == 422  # Validation error
        
        # Test missing required fields
        missing_fields_payload = {
            "invalidation_type": "key"
            # Missing 'key' field
        }
        
        response = client.post("/api/v3/cache/invalidate", json=missing_fields_payload)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_orchestration_health_with_circuit_breakers(self, client):
        """Test orchestration health with circuit breaker states."""
        response = client.get("/api/v3/orchestration/health")
        
        assert response.status_code == 200
        data = response.json()
        
        circuit_breakers = data['circuit_breakers']
        
        # Check that circuit breaker information is present
        for circuit_name, circuit_info in circuit_breakers.items():
            assert 'state' in circuit_info
            assert 'total_requests' in circuit_info
            assert 'total_failures' in circuit_info
            assert 'failure_rate' in circuit_info
            assert 'last_state_change' in circuit_info
            
            # Validate state values
            assert circuit_info['state'] in ['CLOSED', 'OPEN', 'HALF_OPEN']
            assert circuit_info['total_requests'] >= 0
            assert circuit_info['total_failures'] >= 0
            assert 0 <= circuit_info['failure_rate'] <= 1

    @pytest.mark.asyncio
    async def test_bulkhead_pool_status(self, client):
        """Test bulkhead pool status in orchestration health."""
        response = client.get("/api/v3/orchestration/health")
        
        assert response.status_code == 200
        data = response.json()
        
        bulkhead_pools = data['bulkhead_pools']
        
        expected_pools = [
            'analysis_execution', 'knowledge_loading', 'content_processing',
            'vector_operations', 'ai_model_inference'
        ]
        
        for pool_name in expected_pools:
            assert pool_name in bulkhead_pools
            
            pool_info = bulkhead_pools[pool_name]
            assert 'max_concurrent' in pool_info
            assert 'current_count' in pool_info
            assert 'queue_size' in pool_info
            assert 'utilization_rate' in pool_info
            assert 'status' in pool_info
            
            # Validate values
            assert pool_info['max_concurrent'] > 0
            assert pool_info['current_count'] >= 0
            assert pool_info['queue_size'] >= 0
            assert 0 <= pool_info['utilization_rate'] <= 1
            assert pool_info['status'] in ['healthy', 'degraded', 'overloaded']

    @pytest.mark.asyncio
    async def test_operation_metrics_in_health(self, client):
        """Test operation metrics in orchestration health."""
        response = client.get("/api/v3/orchestration/health")
        
        assert response.status_code == 200
        data = response.json()
        
        operation_metrics = data['operation_metrics']
        
        # Check that operation metrics are present
        for operation_name, metrics in operation_metrics.items():
            assert 'total_requests' in metrics
            assert 'successful_requests' in metrics
            assert 'failed_requests' in metrics
            assert 'avg_response_time' in metrics
            assert 'p95_response_time' in metrics
            assert 'p99_response_time' in metrics
            assert 'error_rate' in metrics
            assert 'last_updated' in metrics
            
            # Validate metrics values
            assert metrics['total_requests'] >= 0
            assert metrics['successful_requests'] >= 0
            assert metrics['failed_requests'] >= 0
            assert metrics['avg_response_time'] >= 0
            assert metrics['p95_response_time'] >= 0
            assert metrics['p99_response_time'] >= 0
            assert 0 <= metrics['error_rate'] <= 1

    @pytest.mark.asyncio
    async def test_cache_performance_detailed_metrics(self, client):
        """Test detailed cache performance metrics."""
        response = client.get("/api/v3/cache/performance")
        
        assert response.status_code == 200
        data = response.json()
        
        performance_metrics = data['performance_metrics']
        
        assert 'total_requests' in performance_metrics
        assert 'total_hits' in performance_metrics
        assert 'total_misses' in performance_metrics
        assert 'avg_response_time' in performance_metrics
        assert 'memory_usage' in performance_metrics
        assert 'storage_usage' in performance_metrics
        
        # Validate performance values
        assert performance_metrics['total_requests'] >= 0
        assert performance_metrics['total_hits'] >= 0
        assert performance_metrics['total_misses'] >= 0
        assert performance_metrics['avg_response_time'] >= 0
        assert performance_metrics['memory_usage'] >= 0
        assert performance_metrics['storage_usage'] >= 0

    @pytest.mark.asyncio
    async def test_enhanced_optimization_system_health(self, client):
        """Test system health in enhanced optimization metrics."""
        response = client.get("/api/v3/optimization/enhanced-metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        system_health = data['system_health']
        
        assert 'overall_health' in system_health
        assert 'component_status' in system_health
        assert 'resource_utilization' in system_health
        assert 'alert_count' in system_health
        
        # Check component status
        component_status = system_health['component_status']
        assert 'orchestrator' in component_status
        assert 'cache_manager' in component_status
        assert 'circuit_breakers' in component_status
        assert 'bulkhead_pools' in component_status
        
        # Validate health values
        assert system_health['overall_health'] in ['healthy', 'degraded', 'unhealthy']
        assert system_health['alert_count'] >= 0
        
        for component, status in component_status.items():
            assert status in ['healthy', 'degraded', 'unhealthy', 'unknown']

    @pytest.mark.asyncio
    async def test_endpoint_error_handling(self, client):
        """Test error handling in Phase E endpoints."""
        # Test with invalid query parameters
        response = client.get("/api/v3/orchestration/health?invalid_param=test")
        
        # Should still return 200 (invalid params ignored)
        assert response.status_code == 200
        
        # Test cache invalidation with invalid JSON
        response = client.post("/api/v3/cache/invalidate", json={"invalid": "data"})
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_endpoint_response_times(self, client):
        """Test that Phase E endpoints respond within acceptable time limits."""
        import time
        
        # Test orchestration health response time
        start_time = time.time()
        response = client.get("/api/v3/orchestration/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds
        
        # Test cache performance response time
        start_time = time.time()
        response = client.get("/api/v3/cache/performance")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds
        
        # Test enhanced optimization metrics response time
        start_time = time.time()
        response = client.get("/api/v3/optimization/enhanced-metrics")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 3.0  # Should respond within 3 seconds

    @pytest.mark.asyncio
    async def test_concurrent_endpoint_access(self, client):
        """Test concurrent access to Phase E endpoints."""
        import asyncio
        import concurrent.futures
        
        async def make_request(endpoint):
            response = client.get(endpoint)
            return response.status_code
        
        # Test concurrent requests to different endpoints
        endpoints = [
            "/api/v3/orchestration/health",
            "/api/v3/cache/performance",
            "/api/v3/optimization/enhanced-metrics"
        ]
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(client.get, endpoint) for endpoint in endpoints]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
