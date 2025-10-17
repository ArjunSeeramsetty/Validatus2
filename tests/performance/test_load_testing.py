# tests/performance/test_load_testing.py

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from backend.app.services.analysis_session_manager import AnalysisSessionManager
from backend.app.services.content_quality_analyzer import ContentQualityAnalyzer
from backend.app.services.content_deduplication_service import ContentDeduplicationService
from backend.app.core.performance_optimizer import PerformanceOptimizer
from backend.app.core.error_recovery import ErrorRecoveryManager

class TestLoadTesting:
    """Performance and load testing suite"""
    
    @pytest.fixture
    def analysis_session_manager(self):
        """Create analysis session manager instance"""
        return AnalysisSessionManager()
    
    @pytest.fixture
    def quality_analyzer(self):
        """Create quality analyzer instance"""
        return ContentQualityAnalyzer()
    
    @pytest.fixture
    def deduplication_service(self):
        """Create deduplication service instance"""
        return ContentDeduplicationService()
    
    @pytest.fixture
    def performance_optimizer(self):
        """Create performance optimizer instance"""
        return PerformanceOptimizer()
    
    @pytest.fixture
    def error_recovery_manager(self):
        """Create error recovery manager instance"""
        return ErrorRecoveryManager()
    
    @pytest.fixture
    def sample_documents(self):
        """Generate sample documents for load testing"""
        documents = []
        for i in range(100):
            documents.append({
                "content": f"This is test document {i}. It contains information about artificial intelligence and machine learning. " * 10,
                "url": f"https://example.com/doc-{i}",
                "title": f"Test Document {i}",
                "metadata": {"index": i, "category": "test"}
            })
        return documents
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_sessions_load(self, analysis_session_manager):
        """Test concurrent analysis session creation under load"""
        
        concurrent_sessions = 50
        session_creation_times = []
        
        async def create_session(session_id: int):
            start_time = time.time()
            
            with pytest.mock.patch.object(analysis_session_manager, '_store_session') as mock_store:
                mock_store.return_value = None
                
                session_id_str = await analysis_session_manager.create_analysis_session(
                    topic=f"load_test_topic_{session_id}",
                    user_id=f"load_test_user_{session_id}",
                    analysis_parameters={"test": True}
                )
                
                creation_time = time.time() - start_time
                session_creation_times.append(creation_time)
                
                return session_id_str
        
        # Create sessions concurrently
        tasks = [create_session(i) for i in range(concurrent_sessions)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_sessions = [r for r in results if not isinstance(r, Exception)]
        
        assert len(successful_sessions) == concurrent_sessions
        assert all(0.001 <= t <= 5.0 for t in session_creation_times)  # Reasonable timing
        
        avg_creation_time = statistics.mean(session_creation_times)
        max_creation_time = max(session_creation_times)
        
        print(f"Concurrent Session Creation Results:")
        print(f"  - Successful sessions: {len(successful_sessions)}/{concurrent_sessions}")
        print(f"  - Average creation time: {avg_creation_time:.3f}s")
        print(f"  - Maximum creation time: {max_creation_time:.3f}s")
        print(f"  - Throughput: {concurrent_sessions / sum(session_creation_times):.2f} sessions/s")
        
        # Performance assertions
        assert avg_creation_time < 2.0  # Average should be under 2 seconds
        assert max_creation_time < 5.0  # Maximum should be under 5 seconds
    
    @pytest.mark.asyncio
    async def test_content_quality_analysis_load(self, quality_analyzer, sample_documents):
        """Test content quality analysis under load"""
        
        concurrent_analyses = 20
        analysis_times = []
        
        async def analyze_content(doc_index: int):
            start_time = time.time()
            
            doc = sample_documents[doc_index % len(sample_documents)]
            result = await quality_analyzer.analyze_content_quality(
                content=doc["content"],
                url=doc["url"],
                topic="artificial intelligence"
            )
            
            analysis_time = time.time() - start_time
            analysis_times.append(analysis_time)
            
            return result
        
        # Run analyses concurrently
        tasks = [analyze_content(i) for i in range(concurrent_analyses)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_analyses = [r for r in results if not isinstance(r, Exception)]
        
        assert len(successful_analyses) == concurrent_analyses
        assert all(0.001 <= t <= 10.0 for t in analysis_times)
        
        avg_analysis_time = statistics.mean(analysis_times)
        max_analysis_time = max(analysis_times)
        
        print(f"Content Quality Analysis Load Results:")
        print(f"  - Successful analyses: {len(successful_analyses)}/{concurrent_analyses}")
        print(f"  - Average analysis time: {avg_analysis_time:.3f}s")
        print(f"  - Maximum analysis time: {max_analysis_time:.3f}s")
        print(f"  - Throughput: {concurrent_analyses / sum(analysis_times):.2f} analyses/s")
        
        # Performance assertions
        assert avg_analysis_time < 5.0  # Average should be under 5 seconds
        assert max_analysis_time < 10.0  # Maximum should be under 10 seconds
    
    @pytest.mark.asyncio
    async def test_content_deduplication_load(self, deduplication_service, sample_documents):
        """Test content deduplication under load"""
        
        # Create batches of documents for deduplication
        batch_size = 50
        batch_count = 4
        deduplication_times = []
        
        async def deduplicate_batch(batch_index: int):
            start_time = time.time()
            
            # Create batch with some duplicates
            batch_docs = sample_documents[batch_index * batch_size:(batch_index + 1) * batch_size]
            
            # Add some duplicates
            duplicates = batch_docs[:10]  # First 10 documents as duplicates
            batch_docs.extend(duplicates)
            
            result = await deduplication_service.deduplicate_content_batch(
                documents=batch_docs,
                similarity_threshold=0.85
            )
            
            deduplication_time = time.time() - start_time
            deduplication_times.append(deduplication_time)
            
            return result
        
        # Run deduplication concurrently
        tasks = [deduplicate_batch(i) for i in range(batch_count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_dedups = [r for r in results if not isinstance(r, Exception)]
        
        assert len(successful_dedups) == batch_count
        assert all(0.001 <= t <= 30.0 for t in deduplication_times)
        
        avg_dedup_time = statistics.mean(deduplication_times)
        max_dedup_time = max(deduplication_times)
        
        print(f"Content Deduplication Load Results:")
        print(f"  - Successful batches: {len(successful_dedups)}/{batch_count}")
        print(f"  - Average deduplication time: {avg_dedup_time:.3f}s")
        print(f"  - Maximum deduplication time: {max_dedup_time:.3f}s")
        print(f"  - Throughput: {batch_count / sum(deduplication_times):.2f} batches/s")
        
        # Performance assertions
        assert avg_dedup_time < 20.0  # Average should be under 20 seconds
        assert max_dedup_time < 30.0  # Maximum should be under 30 seconds
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, performance_optimizer, sample_documents):
        """Test memory usage under load"""
        
        initial_memory = performance_optimizer._get_memory_usage()
        memory_measurements = [initial_memory]
        
        # Process documents in batches to monitor memory usage
        batch_size = 20
        batch_count = 5
        
        for batch_idx in range(batch_count):
            batch = sample_documents[batch_idx * batch_size:(batch_idx + 1) * batch_size]
            
            # Simulate processing
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Measure memory
            current_memory = performance_optimizer._get_memory_usage()
            memory_measurements.append(current_memory)
            
            # Trigger garbage collection every other batch
            if batch_idx % 2 == 0:
                import gc
                gc.collect()
        
        final_memory = performance_optimizer._get_memory_usage()
        memory_measurements.append(final_memory)
        
        memory_increase = final_memory - initial_memory
        max_memory = max(memory_measurements)
        
        print(f"Memory Usage Load Test Results:")
        print(f"  - Initial memory: {initial_memory:.2f} MB")
        print(f"  - Final memory: {final_memory:.2f} MB")
        print(f"  - Memory increase: {memory_increase:.2f} MB")
        print(f"  - Peak memory: {max_memory:.2f} MB")
        
        # Memory assertions
        assert memory_increase < 500  # Should not increase by more than 500MB
        assert max_memory < 2000  # Should not exceed 2GB
    
    @pytest.mark.asyncio
    async def test_error_recovery_under_load(self, error_recovery_manager):
        """Test error recovery mechanisms under load"""
        
        # Function that fails randomly
        failure_rate = 0.3  # 30% failure rate
        call_count = 100
        success_count = 0
        recovery_count = 0
        
        async def unreliable_function(value: int):
            import random
            if random.random() < failure_rate:
                raise Exception(f"Simulated failure for value {value}")
            return value * 2
        
        async def fallback_function(value: int):
            return value  # Simple fallback
        
        # Register fallback
        error_recovery_manager.register_fallback_function("unreliable_function", fallback_function)
        
        async def test_with_recovery(value: int):
            nonlocal success_count, recovery_count
            
            result = await error_recovery_manager.execute_with_recovery(
                unreliable_function,
                value,
                recovery_strategy=error_recovery_manager.RecoveryStrategy.FALLBACK,
                fallback_func=fallback_function
            )
            
            if result.success:
                success_count += 1
                if result.fallback_used:
                    recovery_count += 1
            
            return result
        
        # Run tests concurrently
        tasks = [test_with_recovery(i) for i in range(call_count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_rate = success_count / call_count
        recovery_rate = recovery_count / success_count if success_count > 0 else 0
        
        print(f"Error Recovery Load Test Results:")
        print(f"  - Total calls: {call_count}")
        print(f"  - Successful calls: {success_count}")
        print(f"  - Success rate: {success_rate:.1%}")
        print(f"  - Recovery rate: {recovery_rate:.1%}")
        print(f"  - Failed calls: {call_count - success_count}")
        
        # Assertions
        assert success_rate >= 0.95  # Should recover 95% of calls
        assert recovery_rate > 0  # Should use recovery for some calls
    
    @pytest.mark.asyncio
    async def test_sustained_load_performance(self, quality_analyzer, sample_documents):
        """Test sustained load performance over time"""
        
        duration_seconds = 30  # 30 seconds of sustained load
        concurrent_workers = 10
        total_operations = 0
        operation_times = []
        start_time = time.time()
        
        async def sustained_worker():
            nonlocal total_operations
            
            while time.time() - start_time < duration_seconds:
                doc = sample_documents[total_operations % len(sample_documents)]
                op_start = time.time()
                
                try:
                    await quality_analyzer.analyze_content_quality(
                        content=doc["content"],
                        url=doc["url"],
                        topic="sustained load test"
                    )
                    
                    op_time = time.time() - op_start
                    operation_times.append(op_time)
                    total_operations += 1
                    
                except Exception as e:
                    print(f"Operation failed: {e}")
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
        
        # Start workers
        workers = [sustained_worker() for _ in range(concurrent_workers)]
        await asyncio.gather(*workers)
        
        actual_duration = time.time() - start_time
        throughput = total_operations / actual_duration
        avg_operation_time = statistics.mean(operation_times) if operation_times else 0
        
        print(f"Sustained Load Performance Results:")
        print(f"  - Duration: {actual_duration:.1f}s")
        print(f"  - Total operations: {total_operations}")
        print(f"  - Throughput: {throughput:.2f} operations/s")
        print(f"  - Average operation time: {avg_operation_time:.3f}s")
        print(f"  - Concurrent workers: {concurrent_workers}")
        
        # Performance assertions
        assert throughput > 5  # Should maintain at least 5 operations/second
        assert avg_operation_time < 5.0  # Average operation should be under 5 seconds
        assert total_operations > 100  # Should complete at least 100 operations
    
    @pytest.mark.asyncio
    async def test_system_resource_limits(self, performance_optimizer):
        """Test system behavior under resource constraints"""
        
        # Monitor system resources
        initial_cpu = performance_optimizer._get_cpu_usage()
        initial_memory = performance_optimizer._get_memory_usage()
        
        # Simulate high CPU load
        cpu_intensive_tasks = 20
        
        async def cpu_intensive_task():
            # Simulate CPU-intensive work
            result = 0
            for i in range(1000000):
                result += i * i
            return result
        
        # Run CPU-intensive tasks
        tasks = [cpu_intensive_task() for _ in range(cpu_intensive_tasks)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = time.time() - start_time
        
        # Measure resource usage
        peak_cpu = performance_optimizer._get_cpu_usage()
        peak_memory = performance_optimizer._get_memory_usage()
        
        cpu_increase = peak_cpu - initial_cpu
        memory_increase = peak_memory - initial_memory
        
        print(f"Resource Limits Test Results:")
        print(f"  - Initial CPU: {initial_cpu:.1f}%")
        print(f"  - Peak CPU: {peak_cpu:.1f}%")
        print(f"  - CPU increase: {cpu_increase:.1f}%")
        print(f"  - Initial memory: {initial_memory:.2f} MB")
        print(f"  - Peak memory: {peak_memory:.2f} MB")
        print(f"  - Memory increase: {memory_increase:.2f} MB")
        print(f"  - Execution time: {execution_time:.2f}s")
        print(f"  - Successful tasks: {len([r for r in results if not isinstance(r, Exception)])}")
        
        # Resource assertions
        assert execution_time < 60  # Should complete within 60 seconds
        assert memory_increase < 1000  # Should not increase memory by more than 1GB
    
    def test_performance_metrics_accuracy(self, performance_optimizer):
        """Test accuracy of performance metrics collection"""
        
        # Clear existing metrics
        performance_optimizer.reset_metrics()
        
        # Simulate some operations
        for i in range(10):
            start_time = time.time()
            time.sleep(0.01)  # Simulate work
            performance_optimizer._record_metrics_sync(start_time, 100.0, True)
        
        # Get performance summary
        summary = performance_optimizer.get_performance_summary()
        
        assert "performance_summary" in summary
        assert "system_health" in summary
        assert "recommendations" in summary
        
        perf_summary = summary["performance_summary"]
        assert "total_tasks_executed" in perf_summary
        assert perf_summary["total_tasks_executed"] == 10
        assert perf_summary["total_errors"] == 0
        
        print(f"Performance Metrics Accuracy Results:")
        print(f"  - Tasks executed: {perf_summary['total_tasks_executed']}")
        print(f"  - Total errors: {perf_summary['total_errors']}")
        print(f"  - Average execution time: {perf_summary['average_execution_time']:.3f}s")
        print(f"  - Cache hit rate: {perf_summary['average_cache_hit_rate']:.3f}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
