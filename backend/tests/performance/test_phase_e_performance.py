"""
Performance tests for Phase E components.

Tests advanced orchestration, multi-level caching, and system performance under load.
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, AsyncMock, patch
import json
from datetime import datetime, timezone

from app.services.enhanced_orchestration.advanced_orchestrator import AdvancedOrchestrator
from app.services.enhanced_orchestration.multi_level_cache_manager import MultiLevelCacheManager


@pytest.mark.performance
@pytest.mark.phase_e
class TestPhaseEPerformance:
    """Performance test suite for Phase E components."""

    @pytest.fixture
    async def performance_orchestrator(self, mock_gcp_settings, mock_feature_flags, mock_gcp_clients):
        """Create a performance test orchestrator instance."""
        with patch('app.services.enhanced_orchestration.advanced_orchestrator.GCPSettings') as mock_settings:
            mock_settings.return_value = mock_gcp_settings
            
            orchestrator = AdvancedOrchestrator(project_id="performance-test")
            
            # Mock the GCP clients for performance testing
            orchestrator.monitoring_client = mock_gcp_clients['monitoring_v3'].MetricServiceClient()
            orchestrator.error_client = mock_gcp_clients['error_reporting'].Client() if mock_gcp_clients['error_reporting'] else None
            orchestrator.publisher = mock_gcp_clients['pubsub_v1'].PublisherClient()
            orchestrator.firestore_client = mock_gcp_clients['firestore'].Client()
            
            # Mock analysis services with realistic delays
            orchestrator.analysis_optimizer = Mock()
            orchestrator.session_manager = Mock()
            
            await orchestrator.initialize()
            return orchestrator

    @pytest.fixture
    async def performance_cache_manager(self, mock_gcp_settings, mock_feature_flags):
        """Create a performance test cache manager instance."""
        with patch('app.services.enhanced_orchestration.multi_level_cache_manager.GCPSettings') as mock_settings:
            mock_settings.return_value = mock_gcp_settings
            
            cache_manager = MultiLevelCacheManager(
                project_id="performance-test",
                cache_config={
                    "l1_max_size": 1000,
                    "l1_ttl": 300,
                    "l2_ttl": 600,
                    "l3_ttl": 1800,
                    "l4_ttl": 3600
                }
            )
            
            # Mock external dependencies
            cache_manager._redis_client = AsyncMock()
            cache_manager._memcached_client = AsyncMock()
            cache_manager._firestore_client = Mock()
            cache_manager._storage_client = Mock()
            
            await cache_manager.initialize()
            return cache_manager

    @pytest.mark.asyncio
    async def test_orchestrator_concurrent_operations(self, performance_orchestrator):
        """Test orchestrator performance under concurrent operations."""
        operation_count = 100
        concurrent_limit = 20
        
        async def mock_operation(operation_id):
            """Mock operation with realistic delay."""
            await asyncio.sleep(0.01)  # 10ms operation
            return f"result_{operation_id}"
        
        # Test concurrent operations
        start_time = time.time()
        
        tasks = []
        for i in range(operation_count):
            task = performance_orchestrator.execute_with_circuit_breaker(
                operation_name=f"test_operation_{i}",
                operation_func=lambda op_id=i: mock_operation(op_id),
                pool_name='analysis_execution',
                priority=1  # HIGH priority
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert len(results) == operation_count
        assert total_time < 10.0  # Should complete within 10 seconds
        
        # Check that bulkhead protection worked
        assert len(performance_orchestrator.bulkhead_pools['analysis_execution'].current_count) <= 5
        
        # Calculate performance metrics
        operations_per_second = operation_count / total_time
        avg_response_time = total_time / operation_count
        
        print(f"Concurrent Operations Performance:")
        print(f"  Total Operations: {operation_count}")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Operations/sec: {operations_per_second:.2f}")
        print(f"  Avg Response Time: {avg_response_time:.3f}s")
        
        assert operations_per_second > 10  # Should handle at least 10 ops/sec
        assert avg_response_time < 0.1  # Avg response time under 100ms

    @pytest.mark.asyncio
    async def test_cache_performance_under_load(self, performance_cache_manager):
        """Test cache performance under high load."""
        operation_count = 1000
        cache_keys = [f"test_key_{i}" for i in range(operation_count)]
        cache_values = [{"data": f"value_{i}", "timestamp": datetime.now(timezone.utc).isoformat()} 
                       for i in range(operation_count)]
        
        # Test cache set performance
        start_time = time.time()
        
        set_tasks = []
        for i in range(operation_count):
            task = performance_cache_manager.set(cache_keys[i], cache_values[i])
            set_tasks.append(task)
        
        await asyncio.gather(*set_tasks)
        
        set_time = time.time() - start_time
        
        # Test cache get performance
        start_time = time.time()
        
        get_tasks = []
        for i in range(operation_count):
            task = performance_cache_manager.get(cache_keys[i])
            get_tasks.append(task)
        
        get_results = await asyncio.gather(*get_tasks)
        
        get_time = time.time() - start_time
        
        # Performance assertions
        assert len(get_results) == operation_count
        assert set_time < 5.0  # Set operations should complete within 5 seconds
        assert get_time < 2.0  # Get operations should complete within 2 seconds
        
        # Calculate performance metrics
        set_ops_per_second = operation_count / set_time
        get_ops_per_second = operation_count / get_time
        
        print(f"Cache Performance:")
        print(f"  Set Operations: {operation_count} in {set_time:.2f}s ({set_ops_per_second:.2f} ops/sec)")
        print(f"  Get Operations: {operation_count} in {get_time:.2f}s ({get_ops_per_second:.2f} ops/sec)")
        
        assert set_ops_per_second > 100  # Should handle at least 100 sets/sec
        assert get_ops_per_second > 200  # Should handle at least 200 gets/sec

    @pytest.mark.asyncio
    async def test_circuit_breaker_performance(self, performance_orchestrator):
        """Test circuit breaker performance under failure conditions."""
        operation_count = 50
        failure_rate = 0.3  # 30% failure rate
        
        async def mock_failing_operation(operation_id):
            """Mock operation that fails randomly."""
            if operation_id % 10 < (failure_rate * 10):
                raise Exception(f"Simulated failure for operation {operation_id}")
            await asyncio.sleep(0.01)
            return f"success_{operation_id}"
        
        start_time = time.time()
        
        tasks = []
        for i in range(operation_count):
            task = performance_orchestrator.execute_with_circuit_breaker(
                operation_name="failing_operation",
                operation_func=lambda op_id=i: mock_failing_operation(op_id),
                pool_name='analysis_execution'
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        actual_failure_rate = len(failed_results) / len(results)
        
        print(f"Circuit Breaker Performance:")
        print(f"  Total Operations: {operation_count}")
        print(f"  Successful: {len(successful_results)}")
        print(f"  Failed: {len(failed_results)}")
        print(f"  Actual Failure Rate: {actual_failure_rate:.2%}")
        print(f"  Total Time: {total_time:.2f}s")
        
        # Performance assertions
        assert total_time < 5.0  # Should complete within 5 seconds
        assert actual_failure_rate <= 0.5  # Should not exceed 50% failure rate
        
        # Check circuit breaker state
        circuit = performance_orchestrator.circuit_breakers.get("failing_operation")
        if circuit:
            assert circuit.total_requests == operation_count
            assert circuit.total_failures == len(failed_results)

    @pytest.mark.asyncio
    async def test_bulkhead_isolation_performance(self, performance_orchestrator):
        """Test bulkhead isolation performance with different pool loads."""
        pool_operations = {
            'analysis_execution': 30,
            'knowledge_loading': 20,
            'content_processing': 25,
            'vector_operations': 15,
            'ai_model_inference': 10
        }
        
        async def mock_operation_with_delay(operation_id, delay=0.05):
            """Mock operation with configurable delay."""
            await asyncio.sleep(delay)
            return f"result_{operation_id}"
        
        start_time = time.time()
        
        all_tasks = []
        for pool_name, operation_count in pool_operations.items():
            for i in range(operation_count):
                task = performance_orchestrator.execute_with_circuit_breaker(
                    operation_name=f"{pool_name}_operation_{i}",
                    operation_func=lambda op_id=i, pool=pool_name: mock_operation_with_delay(op_id),
                    pool_name=pool_name,
                    priority=1
                )
                all_tasks.append(task)
        
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check that pools maintained isolation
        pool_stats = {}
        for pool_name in pool_operations.keys():
            pool = performance_orchestrator.bulkhead_pools[pool_name]
            pool_stats[pool_name] = {
                'max_concurrent': pool.max_concurrent,
                'current_count': pool.current_count,
                'queue_size': pool.queue_size
            }
        
        print(f"Bulkhead Isolation Performance:")
        print(f"  Total Operations: {sum(pool_operations.values())}")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Pool Statistics:")
        for pool_name, stats in pool_stats.items():
            print(f"    {pool_name}: {stats['current_count']}/{stats['max_concurrent']} concurrent, {stats['queue_size']} queued")
        
        # Performance assertions
        assert total_time < 10.0  # Should complete within 10 seconds
        assert len(results) == sum(pool_operations.values())
        
        # Verify no pool exceeded its limits
        for pool_name, stats in pool_stats.items():
            assert stats['current_count'] <= stats['max_concurrent']

    @pytest.mark.asyncio
    async def test_cache_hit_ratio_optimization(self, performance_cache_manager):
        """Test cache hit ratio optimization over time."""
        # Warm up cache with initial data
        warmup_keys = [f"warmup_key_{i}" for i in range(100)]
        warmup_values = [{"data": f"warmup_value_{i}"} for i in range(100)]
        
        for key, value in zip(warmup_keys, warmup_values):
            await performance_cache_manager.set(key, value)
        
        # Test repeated access patterns
        access_patterns = [
            ("hot_keys", warmup_keys[:20], 50),  # 20 hot keys accessed 50 times each
            ("warm_keys", warmup_keys[20:50], 20),  # 30 warm keys accessed 20 times each
            ("cold_keys", warmup_keys[50:], 5),  # 50 cold keys accessed 5 times each
        ]
        
        total_operations = 0
        start_time = time.time()
        
        for pattern_name, keys, access_count in access_patterns:
            for _ in range(access_count):
                tasks = []
                for key in keys:
                    task = performance_cache_manager.get(key)
                    tasks.append(task)
                await asyncio.gather(*tasks)
                total_operations += len(keys)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Get final cache statistics
        stats = performance_cache_manager.get_cache_stats()
        
        print(f"Cache Hit Ratio Optimization:")
        print(f"  Total Operations: {total_operations}")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Overall Hit Rate: {stats.hit_rate:.2%}")
        print(f"  L1 Hit Rate: {stats.l1_hit_rate:.2%}")
        print(f"  Total Requests: {stats.total_requests}")
        print(f"  Total Hits: {stats.total_hits}")
        print(f"  Total Misses: {stats.total_misses}")
        
        # Performance assertions
        assert stats.hit_rate > 0.8  # Should achieve >80% hit rate
        assert stats.l1_hit_rate > 0.7  # L1 should have >70% hit rate
        assert total_time < 5.0  # Should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, performance_cache_manager):
        """Test memory usage under high load."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        large_data_size = 1000
        large_keys = [f"large_key_{i}" for i in range(large_data_size)]
        large_values = [
            {
                "data": f"large_value_{i}",
                "payload": "x" * 1000,  # 1KB payload per item
                "metadata": {"index": i, "timestamp": datetime.now(timezone.utc).isoformat()}
            }
            for i in range(large_data_size)
        ]
        
        # Load large dataset into cache
        start_time = time.time()
        
        for key, value in zip(large_keys, large_values):
            await performance_cache_manager.set(key, value)
        
        load_time = time.time() - start_time
        
        # Get memory usage after loading
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory Usage Under Load:")
        print(f"  Initial Memory: {initial_memory:.2f} MB")
        print(f"  Final Memory: {final_memory:.2f} MB")
        print(f"  Memory Increase: {memory_increase:.2f} MB")
        print(f"  Load Time: {load_time:.2f}s")
        print(f"  Data Items: {large_data_size}")
        print(f"  Memory per Item: {memory_increase/large_data_size:.3f} MB")
        
        # Performance assertions
        assert memory_increase < 100  # Should not use more than 100MB for 1000 items
        assert load_time < 10.0  # Should load within 10 seconds
        assert memory_increase / large_data_size < 0.1  # Less than 100KB per item

    @pytest.mark.asyncio
    async def test_response_time_distribution(self, performance_orchestrator):
        """Test response time distribution under normal load."""
        operation_count = 200
        response_times = []
        
        async def mock_operation_with_variable_delay(operation_id):
            """Mock operation with variable delay."""
            # Simulate realistic operation delay (10-50ms)
            delay = 0.01 + (operation_id % 40) * 0.001  # 10-50ms
            await asyncio.sleep(delay)
            return f"result_{operation_id}"
        
        start_time = time.time()
        
        tasks = []
        for i in range(operation_count):
            task = performance_orchestrator.execute_with_circuit_breaker(
                operation_name=f"timing_operation_{i}",
                operation_func=lambda op_id=i: mock_operation_with_variable_delay(op_id),
                pool_name='analysis_execution'
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate response time statistics
        avg_response_time = total_time / operation_count
        
        print(f"Response Time Distribution:")
        print(f"  Total Operations: {operation_count}")
        print(f"  Total Time: {total_time:.3f}s")
        print(f"  Average Response Time: {avg_response_time:.3f}s")
        print(f"  Operations per Second: {operation_count/total_time:.2f}")
        
        # Performance assertions
        assert avg_response_time < 0.1  # Average response time under 100ms
        assert operation_count / total_time > 50  # Should handle >50 ops/sec

    @pytest.mark.asyncio
    async def test_system_stability_under_sustained_load(self, performance_orchestrator, performance_cache_manager):
        """Test system stability under sustained load."""
        duration_seconds = 30
        operations_per_second = 10
        
        async def sustained_load_test():
            """Run sustained load test."""
            start_time = time.time()
            operation_count = 0
            
            while time.time() - start_time < duration_seconds:
                # Mix of operations
                if operation_count % 3 == 0:
                    # Cache operations
                    await performance_cache_manager.set(f"sustained_key_{operation_count}", {"data": f"value_{operation_count}"})
                elif operation_count % 3 == 1:
                    # Orchestrator operations
                    await performance_orchestrator.execute_with_circuit_breaker(
                        operation_name=f"sustained_op_{operation_count}",
                        operation_func=lambda op_id=operation_count: asyncio.sleep(0.01),
                        pool_name='analysis_execution'
                    )
                else:
                    # Cache reads
                    await performance_cache_manager.get(f"sustained_key_{operation_count % 100}")
                
                operation_count += 1
                
                # Maintain target rate
                await asyncio.sleep(1.0 / operations_per_second)
            
            return operation_count
        
        start_time = time.time()
        total_operations = await sustained_load_test()
        end_time = time.time()
        
        actual_duration = end_time - start_time
        actual_ops_per_second = total_operations / actual_duration
        
        # Get final system health
        orchestrator_health = await performance_orchestrator.get_orchestrator_health()
        cache_stats = performance_cache_manager.get_cache_stats()
        
        print(f"Sustained Load Test Results:")
        print(f"  Target Duration: {duration_seconds}s")
        print(f"  Actual Duration: {actual_duration:.2f}s")
        print(f"  Total Operations: {total_operations}")
        print(f"  Target Ops/sec: {operations_per_second}")
        print(f"  Actual Ops/sec: {actual_ops_per_second:.2f}")
        print(f"  Orchestrator Status: {orchestrator_health['overall_status']}")
        print(f"  Cache Hit Rate: {cache_stats.hit_rate:.2%}")
        
        # Performance assertions
        assert actual_duration >= duration_seconds * 0.9  # Within 90% of target duration
        assert actual_ops_per_second >= operations_per_second * 0.8  # Within 80% of target rate
        assert orchestrator_health['overall_status'] in ['healthy', 'degraded']  # System should remain stable
        assert cache_stats.hit_rate > 0  # Cache should be working