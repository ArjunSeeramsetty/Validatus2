"""
Unit tests for Phase E Advanced Orchestrator component.

Tests circuit breaker patterns, bulkhead isolation, and orchestration logic.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from app.services.enhanced_orchestration.advanced_orchestrator import (
    AdvancedOrchestrator,
    CircuitState,
    OperationPriority,
    CircuitBreakerConfig,
    CircuitBreakerState,
    OperationMetrics,
    BulkheadPool
)


@pytest.mark.unit
@pytest.mark.phase_e
class TestAdvancedOrchestrator:
    """Test suite for Advanced Orchestrator."""

    @pytest.fixture
    async def orchestrator(self, mock_gcp_settings, mock_feature_flags, mock_gcp_clients):
        """Create a test orchestrator instance."""
        with patch('app.services.enhanced_orchestration.advanced_orchestrator.GCPSettings') as mock_settings:
            mock_settings.return_value = mock_gcp_settings
            
            orchestrator = AdvancedOrchestrator(project_id="test-project")
            
            # Mock the GCP clients
            orchestrator.monitoring_client = mock_gcp_clients['monitoring_v3'].MetricServiceClient()
            orchestrator.error_client = mock_gcp_clients['error_reporting'].Client() if mock_gcp_clients['error_reporting'] else None
            orchestrator.publisher = mock_gcp_clients['pubsub_v1'].PublisherClient()
            orchestrator.firestore_client = mock_gcp_clients['firestore'].Client()
            
            # Mock the analysis services
            orchestrator.analysis_optimizer = Mock()
            orchestrator.session_manager = Mock()
            
            await orchestrator.initialize()
            return orchestrator

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_gcp_settings, mock_feature_flags):
        """Test orchestrator initialization."""
        with patch('app.services.enhanced_orchestration.advanced_orchestrator.GCPSettings') as mock_settings:
            mock_settings.return_value = mock_gcp_settings
            
            orchestrator = AdvancedOrchestrator(project_id="test-project")
            
            assert orchestrator.project_id == "test-project"
            assert len(orchestrator.circuit_breakers) == 0
            assert len(orchestrator.bulkhead_pools) == 5
            assert len(orchestrator.operation_metrics) == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_config_setup(self, orchestrator):
        """Test circuit breaker configuration setup."""
        await orchestrator._setup_default_circuit_configs()
        
        assert 'analysis_execution' in orchestrator.circuit_configs
        assert 'knowledge_loading' in orchestrator.circuit_configs
        assert 'content_processing' in orchestrator.circuit_configs
        assert 'vector_operations' in orchestrator.circuit_configs
        assert 'ai_model_inference' in orchestrator.circuit_configs
        
        # Check specific configurations
        analysis_config = orchestrator.circuit_configs['analysis_execution']
        assert analysis_config.failure_threshold == 3
        assert analysis_config.recovery_timeout == 120
        assert analysis_config.timeout_duration == 300.0

    @pytest.mark.asyncio
    async def test_circuit_breaker_states(self, orchestrator):
        """Test circuit breaker state transitions."""
        # Test initial state
        circuit = CircuitBreakerState()
        assert circuit.state == CircuitState.CLOSED
        assert circuit.failure_count == 0
        assert circuit.success_count == 0

        # Test state transitions
        circuit.state = CircuitState.OPEN
        circuit.next_attempt_time = datetime.now(timezone.utc) + timedelta(seconds=60)
        
        assert circuit.state == CircuitState.OPEN
        assert circuit.next_attempt_time is not None

    @pytest.mark.asyncio
    async def test_bulkhead_pool_creation(self, orchestrator):
        """Test bulkhead pool creation and configuration."""
        pools = orchestrator.bulkhead_pools
        
        assert 'analysis_execution' in pools
        assert 'knowledge_loading' in pools
        assert 'content_processing' in pools
        assert 'vector_operations' in pools
        assert 'ai_model_inference' in pools
        
        # Check specific pool configurations
        analysis_pool = pools['analysis_execution']
        assert analysis_pool.max_concurrent == 5
        assert analysis_pool.max_queue_size == 50
        assert analysis_pool.timeout == 30.0

    @pytest.mark.asyncio
    async def test_bulkhead_protection(self, orchestrator):
        """Test bulkhead protection mechanism."""
        pool_name = 'analysis_execution'
        operation_name = 'test_operation'
        
        # Mock the semaphore
        orchestrator.pool_semaphores[pool_name] = AsyncMock()
        orchestrator.pool_semaphores[pool_name].acquire = AsyncMock()
        orchestrator.pool_semaphores[pool_name].release = AsyncMock()
        
        async with orchestrator.bulkhead_protection(pool_name, operation_name):
            # Simulate some work
            await asyncio.sleep(0.01)
        
        # Verify semaphore was acquired and released
        orchestrator.pool_semaphores[pool_name].acquire.assert_called_once()
        orchestrator.pool_semaphores[pool_name].release.assert_called_once()

    @pytest.mark.asyncio
    async def test_circuit_breaker_execution_success(self, orchestrator):
        """Test successful operation execution with circuit breaker."""
        operation_name = 'test_operation'
        operation_func = AsyncMock(return_value="success")
        
        result = await orchestrator.execute_with_circuit_breaker(
            operation_name=operation_name,
            operation_func=operation_func,
            pool_name='analysis_execution',
            priority=OperationPriority.HIGH
        )
        
        assert result == "success"
        assert operation_name in orchestrator.circuit_breakers
        assert operation_name in orchestrator.operation_metrics
        
        # Check circuit breaker state
        circuit = orchestrator.circuit_breakers[operation_name]
        assert circuit.state == CircuitState.CLOSED
        assert circuit.total_requests == 1
        assert circuit.total_failures == 0
        
        # Check metrics
        metrics = orchestrator.operation_metrics[operation_name]
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_execution_failure(self, orchestrator):
        """Test failed operation execution with circuit breaker."""
        operation_name = 'test_operation'
        operation_func = AsyncMock(side_effect=Exception("Test error"))
        
        with pytest.raises(Exception, match="Test error"):
            await orchestrator.execute_with_circuit_breaker(
                operation_name=operation_name,
                operation_func=operation_func,
                pool_name='analysis_execution',
                priority=OperationPriority.HIGH
            )
        
        # Check circuit breaker state
        circuit = orchestrator.circuit_breakers[operation_name]
        assert circuit.total_requests == 1
        assert circuit.total_failures == 1
        assert circuit.failure_count == 1
        
        # Check metrics
        metrics = orchestrator.operation_metrics[operation_name]
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_opening(self, orchestrator):
        """Test circuit breaker opening after threshold failures."""
        operation_name = 'test_operation'
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=60)
        orchestrator.circuit_configs[operation_name] = config
        
        operation_func = AsyncMock(side_effect=Exception("Test error"))
        
        # Execute operations to trigger circuit breaker opening
        for _ in range(3):  # Exceed failure threshold
            with pytest.raises(Exception):
                await orchestrator.execute_with_circuit_breaker(
                    operation_name=operation_name,
                    operation_func=operation_func
                )
        
        # Check circuit breaker is open
        circuit = orchestrator.circuit_breakers[operation_name]
        assert circuit.state == CircuitState.OPEN
        assert circuit.failure_count >= config.failure_threshold

    @pytest.mark.asyncio
    async def test_operation_metrics_tracking(self, orchestrator):
        """Test operation metrics tracking."""
        operation_name = 'test_operation'
        operation_func = AsyncMock(return_value="success")
        
        # Execute multiple operations
        for _ in range(5):
            await orchestrator.execute_with_circuit_breaker(
                operation_name=operation_name,
                operation_func=operation_func
            )
        
        metrics = orchestrator.operation_metrics[operation_name]
        assert metrics.total_requests == 5
        assert metrics.successful_requests == 5
        assert metrics.failed_requests == 0
        assert len(metrics.response_times) == 5
        assert metrics.avg_response_time > 0

    @pytest.mark.asyncio
    async def test_priority_based_timeout(self, orchestrator):
        """Test priority-based timeout calculation."""
        pool = orchestrator.bulkhead_pools['analysis_execution']
        
        # Test different priority timeouts
        critical_timeout = pool.timeout * (4 - OperationPriority.CRITICAL.value)
        high_timeout = pool.timeout * (4 - OperationPriority.HIGH.value)
        medium_timeout = pool.timeout * (4 - OperationPriority.MEDIUM.value)
        low_timeout = pool.timeout * (4 - OperationPriority.LOW.value)
        
        assert critical_timeout > high_timeout > medium_timeout > low_timeout
        assert critical_timeout == pool.timeout * 3  # 4 - 1 = 3
        assert low_timeout == pool.timeout * 1      # 4 - 4 = 1

    @pytest.mark.asyncio
    async def test_orchestrator_health_status(self, orchestrator):
        """Test orchestrator health status reporting."""
        # Add some test data
        orchestrator.circuit_breakers['test_op'] = CircuitBreakerState(
            state=CircuitState.CLOSED,
            total_requests=10,
            total_failures=1
        )
        
        orchestrator.operation_metrics['test_op'] = OperationMetrics(
            operation_name='test_op',
            total_requests=10,
            successful_requests=9,
            failed_requests=1,
            avg_response_time=0.5
        )
        
        health_status = await orchestrator.get_orchestrator_health()
        
        assert 'timestamp' in health_status
        assert 'overall_status' in health_status
        assert 'circuit_breakers' in health_status
        assert 'bulkhead_pools' in health_status
        assert 'operation_metrics' in health_status
        
        assert health_status['overall_status'] in ['healthy', 'degraded', 'unhealthy']
        assert 'test_op' in health_status['circuit_breakers']
        assert 'test_op' in health_status['operation_metrics']

    @pytest.mark.asyncio
    async def test_enhanced_analysis_operations(self, orchestrator):
        """Test enhanced analysis operations with protection."""
        # Mock the session manager methods
        orchestrator.session_manager.execute_strategic_analysis = AsyncMock(
            return_value={"status": "completed", "score": 0.85}
        )
        orchestrator.session_manager._load_topic_knowledge = AsyncMock(
            return_value={"knowledge": "loaded", "documents": 100}
        )
        
        # Test strategic analysis with protection
        result = await orchestrator.execute_strategic_analysis_protected(
            session_id="test_session",
            topic="test_topic",
            user_id="test_user",
            priority=OperationPriority.HIGH
        )
        
        assert result["status"] == "completed"
        assert result["score"] == 0.85
        
        # Test knowledge loading with protection
        knowledge_result = await orchestrator.load_topic_knowledge_protected(
            topic="test_topic",
            priority=OperationPriority.MEDIUM
        )
        
        assert knowledge_result["knowledge"] == "loaded"
        assert knowledge_result["documents"] == 100

    @pytest.mark.asyncio
    async def test_maintenance_tasks_startup(self, orchestrator):
        """Test maintenance tasks startup."""
        assert len(orchestrator._maintenance_tasks) == 3
        
        # Check that tasks are created
        task_names = [task.get_name() for task in orchestrator._maintenance_tasks]
        assert any('circuit_breaker_monitor' in name for name in task_names)
        assert any('metrics_collection' in name for name in task_names)
        assert any('pool_health_monitor' in name for name in task_names)

    @pytest.mark.asyncio
    async def test_orchestrator_shutdown(self, orchestrator):
        """Test orchestrator graceful shutdown."""
        # Verify tasks are running
        assert len(orchestrator._maintenance_tasks) > 0
        
        # Shutdown orchestrator
        await orchestrator.shutdown()
        
        # Check that tasks are cancelled
        for task in orchestrator._maintenance_tasks:
            assert task.done() or task.cancelled()


@pytest.mark.unit
@pytest.mark.phase_e
class TestCircuitBreakerConfig:
    """Test suite for Circuit Breaker Configuration."""

    def test_default_config(self):
        """Test default circuit breaker configuration."""
        config = CircuitBreakerConfig()
        
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60
        assert config.success_threshold == 3
        assert config.timeout_duration == 30.0
        assert config.expected_exceptions == (Exception,)

    def test_custom_config(self):
        """Test custom circuit breaker configuration."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=120,
            success_threshold=2,
            timeout_duration=60.0,
            expected_exceptions=(ValueError, RuntimeError)
        )
        
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 120
        assert config.success_threshold == 2
        assert config.timeout_duration == 60.0
        assert config.expected_exceptions == (ValueError, RuntimeError)


@pytest.mark.unit
@pytest.mark.phase_e
class TestBulkheadPool:
    """Test suite for Bulkhead Pool."""

    def test_pool_creation(self):
        """Test bulkhead pool creation."""
        pool = BulkheadPool(
            name="test_pool",
            max_concurrent=10,
            max_queue_size=100,
            timeout=45.0
        )
        
        assert pool.name == "test_pool"
        assert pool.max_concurrent == 10
        assert pool.max_queue_size == 100
        assert pool.timeout == 45.0
        assert pool.current_count == 0
        assert pool.queue_size == 0

    def test_pool_defaults(self):
        """Test bulkhead pool default values."""
        pool = BulkheadPool(name="test_pool", max_concurrent=5)
        
        assert pool.max_queue_size == 100
        assert pool.timeout == 30.0
        assert pool.current_count == 0
        assert pool.queue_size == 0


@pytest.mark.unit
@pytest.mark.phase_e
class TestOperationMetrics:
    """Test suite for Operation Metrics."""

    def test_metrics_creation(self):
        """Test operation metrics creation."""
        metrics = OperationMetrics(operation_name="test_operation")
        
        assert metrics.operation_name == "test_operation"
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.avg_response_time == 0.0
        assert metrics.p95_response_time == 0.0
        assert metrics.p99_response_time == 0.0
        assert len(metrics.response_times) == 0
        assert isinstance(metrics.last_updated, datetime)

    def test_metrics_update(self):
        """Test operation metrics update."""
        metrics = OperationMetrics(operation_name="test_operation")
        
        # Add some response times
        metrics.response_times = [0.1, 0.2, 0.3, 0.4, 0.5]
        metrics.total_requests = 5
        metrics.successful_requests = 4
        metrics.failed_requests = 1
        
        # Update average response time
        metrics.avg_response_time = sum(metrics.response_times) / len(metrics.response_times)
        
        assert metrics.avg_response_time == 0.3
        assert metrics.total_requests == 5
        assert metrics.successful_requests == 4
        assert metrics.failed_requests == 1
