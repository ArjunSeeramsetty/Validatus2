"""
End-to-end integration tests for complete analysis workflows.

Tests the complete analysis pipeline from request to response across all phases.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from app.services.enhanced_analysis_optimization_service import EnhancedAnalysisOptimizationService
from app.services.enhanced_orchestration.advanced_orchestrator import AdvancedOrchestrator
from app.services.enhanced_orchestration.multi_level_cache_manager import MultiLevelCacheManager


@pytest.mark.integration
class TestEndToEndAnalysis:
    """Test suite for end-to-end analysis workflows."""

    @pytest.fixture
    async def integrated_system(self, mock_gcp_settings, mock_feature_flags, mock_gcp_clients):
        """Create an integrated system with all components."""
        with patch.multiple(
            'app.services.enhanced_orchestration.advanced_orchestrator',
            GCPSettings=mock_gcp_settings
        ), patch.multiple(
            'app.services.enhanced_orchestration.multi_level_cache_manager',
            GCPSettings=mock_gcp_settings
        ):
            # Initialize components
            orchestrator = AdvancedOrchestrator(project_id="integration-test")
            cache_manager = MultiLevelCacheManager(project_id="integration-test")
            
            # Mock GCP clients
            orchestrator.monitoring_client = mock_gcp_clients['monitoring_v3'].MetricServiceClient()
            orchestrator.error_client = mock_gcp_clients['error_reporting'].Client() if mock_gcp_clients['error_reporting'] else None
            orchestrator.publisher = mock_gcp_clients['pubsub_v1'].PublisherClient()
            orchestrator.firestore_client = mock_gcp_clients['firestore'].Client()
            
            cache_manager._redis_client = AsyncMock()
            cache_manager._memcached_client = AsyncMock()
            cache_manager._firestore_client = Mock()
            cache_manager._storage_client = Mock()
            
            # Initialize components
            await orchestrator.initialize()
            await cache_manager.initialize()
            
            # Create integrated optimization service
            optimization_service = EnhancedAnalysisOptimizationService(
                orchestrator=orchestrator,
                cache_manager=cache_manager
            )
            
            return {
                'orchestrator': orchestrator,
                'cache_manager': cache_manager,
                'optimization_service': optimization_service
            }

    @pytest.mark.asyncio
    async def test_complete_strategic_analysis_workflow(self, integrated_system):
        """Test complete strategic analysis workflow."""
        system = integrated_system
        
        # Mock the analysis session manager
        mock_session_manager = Mock()
        mock_session_manager.execute_strategic_analysis = AsyncMock(return_value={
            "status": "completed",
            "session_id": "test_session_123",
            "topic": "test_topic",
            "analysis_results": {
                "factor_scores": {
                    "F1_market_size": 0.85,
                    "F2_market_growth": 0.78,
                    "F3_market_maturity": 0.72
                },
                "action_recommendations": [
                    {"layer": "L01", "recommendation": "Expand market presence", "priority": "high"},
                    {"layer": "L02", "recommendation": "Optimize pricing strategy", "priority": "medium"}
                ],
                "confidence_score": 0.82,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
        })
        
        system['orchestrator'].session_manager = mock_session_manager
        
        # Execute complete analysis
        result = await system['optimization_service'].execute_comprehensive_analysis(
            session_id="test_session_123",
            topic="test_topic",
            user_id="test_user",
            analysis_options={
                "include_phase_c": True,
                "include_phase_e": True,
                "use_caching": True,
                "use_circuit_breaker": True
            }
        )
        
        # Verify result structure
        assert result is not None
        assert 'session_id' in result
        assert 'topic' in result
        assert 'analysis_results' in result
        assert 'performance_metrics' in result
        assert 'cache_metrics' in result
        assert 'orchestration_metrics' in result
        
        # Verify analysis results
        analysis_results = result['analysis_results']
        assert analysis_results['status'] == 'completed'
        assert 'factor_scores' in analysis_results
        assert 'action_recommendations' in analysis_results
        assert 'confidence_score' in analysis_results
        
        # Verify performance metrics
        performance_metrics = result['performance_metrics']
        assert 'total_analysis_time' in performance_metrics
        assert 'cache_hit_rate' in performance_metrics
        assert 'circuit_breaker_operations' in performance_metrics
        
        # Verify cache was used
        cache_stats = system['cache_manager'].get_cache_stats()
        assert cache_stats.total_requests > 0

    @pytest.mark.asyncio
    async def test_multi_phase_analysis_integration(self, integrated_system):
        """Test integration across multiple phases (B, C, E)."""
        system = integrated_system
        
        # Mock Phase B components
        mock_pdf_engine = Mock()
        mock_pdf_engine.calculate_factors = AsyncMock(return_value={
            "F1_market_size": {"score": 0.85, "confidence": 0.88},
            "F2_market_growth": {"score": 0.78, "confidence": 0.82}
        })
        
        mock_action_calculator = Mock()
        mock_action_calculator.calculate_action_layers = AsyncMock(return_value={
            "L01_strategic_positioning": {"score": 0.80, "recommendations": ["Expand market"]},
            "L02_risk_assessment": {"score": 0.75, "recommendations": ["Mitigate risks"]}
        })
        
        # Mock Phase C components
        mock_bayesian_blender = Mock()
        mock_bayesian_blender.blend_data_sources = AsyncMock(return_value={
            "blended_value": 0.82,
            "confidence_score": 0.85,
            "contributing_sources": ["client", "benchmark", "industry"]
        })
        
        # Integrate components
        system['optimization_service'].pdf_engine = mock_pdf_engine
        system['optimization_service'].action_calculator = mock_action_calculator
        system['optimization_service'].bayesian_blender = mock_bayesian_blender
        
        # Execute multi-phase analysis
        result = await system['optimization_service'].execute_multi_phase_analysis(
            session_id="multi_phase_session",
            topic="multi_phase_topic",
            user_id="test_user",
            phases=["phase_b", "phase_c", "phase_e"]
        )
        
        # Verify multi-phase result
        assert result is not None
        assert 'phase_b_results' in result
        assert 'phase_c_results' in result
        assert 'phase_e_results' in result
        assert 'integration_metrics' in result
        
        # Verify Phase B results
        phase_b_results = result['phase_b_results']
        assert 'factor_analysis' in phase_b_results
        assert 'action_layers' in phase_b_results
        
        # Verify Phase C results
        phase_c_results = result['phase_c_results']
        assert 'bayesian_blending' in phase_c_results
        assert 'data_pipeline_metrics' in phase_c_results
        
        # Verify Phase E results
        phase_e_results = result['phase_e_results']
        assert 'orchestration_health' in phase_e_results
        assert 'cache_performance' in phase_e_results
        assert 'circuit_breaker_status' in phase_e_results

    @pytest.mark.asyncio
    async def test_error_recovery_and_fallback(self, integrated_system):
        """Test error recovery and fallback mechanisms."""
        system = integrated_system
        
        # Mock failing component
        mock_failing_service = Mock()
        mock_failing_service.analyze = AsyncMock(side_effect=Exception("Service unavailable"))
        
        system['optimization_service'].failing_service = mock_failing_service
        
        # Execute analysis with error handling
        result = await system['optimization_service'].execute_analysis_with_fallback(
            session_id="error_recovery_session",
            topic="error_recovery_topic",
            user_id="test_user",
            primary_service="failing_service",
            fallback_service="mock_session_manager"
        )
        
        # Verify fallback was used
        assert result is not None
        assert 'fallback_used' in result
        assert result['fallback_used'] is True
        
        # Verify circuit breaker state
        circuit_health = await system['orchestrator'].get_orchestrator_health()
        assert circuit_health['overall_status'] in ['healthy', 'degraded']

    @pytest.mark.asyncio
    async def test_cache_integration_across_phases(self, integrated_system):
        """Test cache integration across different phases."""
        system = integrated_system
        
        # Simulate cache usage across phases
        cache_keys = [
            "phase_b_factor_analysis_test_topic",
            "phase_c_bayesian_blend_test_topic",
            "phase_e_orchestration_health"
        ]
        
        cache_values = [
            {"phase": "B", "data": "factor_analysis_results"},
            {"phase": "C", "data": "bayesian_blend_results"},
            {"phase": "E", "data": "orchestration_health_results"}
        ]
        
        # Set cache values
        for key, value in zip(cache_keys, cache_values):
            await system['cache_manager'].set(key, value)
        
        # Retrieve from cache
        retrieved_values = []
        for key in cache_keys:
            value = await system['cache_manager'].get(key)
            retrieved_values.append(value)
        
        # Verify cache integration
        assert len(retrieved_values) == len(cache_values)
        assert all(value is not None for value in retrieved_values)
        
        # Verify cache statistics
        cache_stats = system['cache_manager'].get_cache_stats()
        assert cache_stats.total_requests >= len(cache_keys)
        assert cache_stats.total_hits >= len(cache_keys)

    @pytest.mark.asyncio
    async def test_concurrent_analysis_requests(self, integrated_system):
        """Test handling of concurrent analysis requests."""
        system = integrated_system
        
        # Mock session manager for concurrent requests
        mock_session_manager = Mock()
        mock_session_manager.execute_strategic_analysis = AsyncMock(return_value={
            "status": "completed",
            "session_id": "concurrent_session",
            "topic": "concurrent_topic",
            "analysis_results": {"score": 0.85}
        })
        
        system['orchestrator'].session_manager = mock_session_manager
        
        # Create concurrent requests
        concurrent_requests = 10
        tasks = []
        
        for i in range(concurrent_requests):
            task = system['optimization_service'].execute_comprehensive_analysis(
                session_id=f"concurrent_session_{i}",
                topic=f"concurrent_topic_{i}",
                user_id="test_user",
                analysis_options={"use_circuit_breaker": True}
            )
            tasks.append(task)
        
        # Execute concurrent requests
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all requests completed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == concurrent_requests
        
        # Verify bulkhead isolation worked
        orchestrator_health = await system['orchestrator'].get_orchestrator_health()
        assert orchestrator_health['overall_status'] in ['healthy', 'degraded']

    @pytest.mark.asyncio
    async def test_data_flow_across_phases(self, integrated_system):
        """Test data flow across different phases."""
        system = integrated_system
        
        # Simulate data flow: Phase B -> Phase C -> Phase E
        phase_b_data = {
            "factor_scores": {"F1": 0.85, "F2": 0.78},
            "action_recommendations": [{"layer": "L01", "priority": "high"}]
        }
        
        # Phase B to Phase C data flow
        phase_c_input = {
            "factor_data": phase_b_data,
            "additional_sources": [
                {"source": "benchmark", "data": {"F1": 0.82}},
                {"source": "industry", "data": {"F1": 0.88}}
            ]
        }
        
        # Mock Phase C processing
        mock_bayesian_result = {
            "blended_factor_scores": {"F1": 0.85, "F2": 0.78},
            "confidence_scores": {"F1": 0.87, "F2": 0.80}
        }
        
        # Phase C to Phase E data flow
        phase_e_input = {
            "enhanced_data": mock_bayesian_result,
            "orchestration_options": {
                "use_circuit_breaker": True,
                "use_caching": True,
                "priority": "high"
            }
        }
        
        # Execute data flow
        result = await system['optimization_service'].execute_data_flow_analysis(
            session_id="data_flow_session",
            topic="data_flow_topic",
            user_id="test_user",
            phase_b_data=phase_b_data,
            phase_c_input=phase_c_input,
            phase_e_input=phase_e_input
        )
        
        # Verify data flow result
        assert result is not None
        assert 'phase_b_output' in result
        assert 'phase_c_output' in result
        assert 'phase_e_output' in result
        assert 'data_flow_metrics' in result
        
        # Verify data integrity across phases
        assert result['phase_b_output']['factor_scores']['F1'] == 0.85
        assert 'blended_factor_scores' in result['phase_c_output']
        assert 'orchestration_health' in result['phase_e_output']

    @pytest.mark.asyncio
    async def test_system_health_monitoring_integration(self, integrated_system):
        """Test integrated system health monitoring."""
        system = integrated_system
        
        # Get comprehensive system health
        system_health = await system['optimization_service'].get_comprehensive_system_health()
        
        # Verify system health structure
        assert 'timestamp' in system_health
        assert 'overall_status' in system_health
        assert 'component_health' in system_health
        assert 'performance_metrics' in system_health
        assert 'cache_health' in system_health
        assert 'orchestration_health' in system_health
        
        # Verify component health
        component_health = system_health['component_health']
        assert 'orchestrator' in component_health
        assert 'cache_manager' in component_health
        assert 'optimization_service' in component_health
        
        # Verify performance metrics
        performance_metrics = system_health['performance_metrics']
        assert 'avg_response_time' in performance_metrics
        assert 'throughput' in performance_metrics
        assert 'error_rate' in performance_metrics
        assert 'resource_utilization' in performance_metrics
        
        # Verify cache health
        cache_health = system_health['cache_health']
        assert 'overall_status' in cache_health
        assert 'hit_rate' in cache_health
        assert 'memory_usage' in cache_health
        
        # Verify orchestration health
        orchestration_health = system_health['orchestration_health']
        assert 'overall_status' in orchestration_health
        assert 'circuit_breaker_status' in orchestration_health
        assert 'bulkhead_pool_status' in orchestration_health

    @pytest.mark.asyncio
    async def test_graceful_degradation_scenarios(self, integrated_system, monkeypatch):
        """Test graceful degradation under various failure scenarios."""
        system = integrated_system
        
        # Scenario 1: Cache unavailable
        with patch.object(system['cache_manager'], 'get', side_effect=Exception("Cache unavailable")):
            result = await system['optimization_service'].execute_analysis_with_graceful_degradation(
                session_id="cache_failure_session",
                topic="cache_failure_topic",
                user_id="test_user",
                fallback_to_direct=True
            )
            
            assert result is not None
            assert 'degradation_applied' in result
            assert result['degradation_applied'] is True
        
        # Scenario 2: Circuit breaker open
        circuit = system['orchestrator'].circuit_breakers.get("analysis_execution")
        if circuit:
            # Use monkeypatch to safely set circuit breaker state
            monkeypatch.setattr(circuit, 'state', "OPEN")
            
            result = await system['optimization_service'].execute_analysis_with_graceful_degradation(
                session_id="circuit_open_session",
                topic="circuit_open_topic",
                user_id="test_user",
                fallback_to_direct=True
            )
            
            assert result is not None
            assert 'circuit_breaker_bypassed' in result
        
        # Scenario 3: High load conditions
        # Simulate high load by submitting tasks to fill bulkhead pools
        high_load_tasks = []
        for pool_name, pool in system['orchestrator'].bulkhead_pools.items():
            # Submit tasks to fill pool to near capacity
            for i in range(pool.max_concurrent - 1):
                async def mock_long_operation():
                    await asyncio.sleep(60)  # Long-running task
                    return "long_result"
                
                task = system['orchestrator'].execute_with_circuit_breaker(
                    operation_name=f'load_test_{pool_name}_{i}',
                    operation_func=mock_long_operation,
                    pool_name=pool_name
                )
                high_load_tasks.append(task)
        
        # Wait a moment for tasks to start and fill pools
        await asyncio.sleep(0.1)
        
        result = await system['optimization_service'].execute_analysis_with_graceful_degradation(
            session_id="high_load_session",
            topic="high_load_topic",
            user_id="test_user",
            reduce_priority_on_load=True
        )
        
        assert result is not None
        assert 'priority_adjusted' in result
        
        # Clean up high load tasks
        for task in high_load_tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*high_load_tasks, return_exceptions=True)
