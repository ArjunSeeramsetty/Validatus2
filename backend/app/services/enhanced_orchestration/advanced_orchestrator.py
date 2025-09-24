import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import statistics
from contextlib import asynccontextmanager
import hashlib
import json

from google.cloud import monitoring_v3
from google.cloud import pubsub_v1
from google.cloud import firestore

# Try to import error reporting, fallback if not available
try:
    from google.cloud import error_reporting
except ImportError:
    error_reporting = None

from ..analysis_optimization_service import AnalysisOptimizationService
from ..analysis_session_manager import AnalysisSessionManager
from ...core.gcp_config import GCPSettings
from ...middleware.monitoring import performance_monitor
from ...core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"          # Normal operation
    OPEN = "open"              # Circuit is open, failing fast
    HALF_OPEN = "half_open"    # Testing if service recovered

class OperationPriority(Enum):
    """Operation priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5            # Failures before opening
    recovery_timeout: int = 60           # Seconds before trying half-open
    success_threshold: int = 3           # Successes needed to close from half-open
    timeout_duration: float = 30.0      # Operation timeout in seconds
    expected_exceptions: tuple = (Exception,)  # Exceptions that trigger the breaker

@dataclass
class CircuitBreakerState:
    """Current state of a circuit breaker"""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None
    total_requests: int = 0
    total_failures: int = 0

@dataclass
class OperationMetrics:
    """Metrics for tracking operation performance"""
    operation_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class BulkheadPool:
    """Resource pool for bulkhead isolation"""
    name: str
    max_concurrent: int
    current_count: int = 0
    queue_size: int = 0
    max_queue_size: int = 100
    timeout: float = 30.0

class AdvancedOrchestrator:
    """
    Advanced orchestrator with circuit breaker patterns, bulkhead isolation,
    and enhanced observability for production deployment
    """
    
    def __init__(self, project_id: str = None):
        self.settings = GCPSettings() if not project_id else GCPSettings(project_id=project_id)
        
        # Core services integration
        self.analysis_optimizer = AnalysisOptimizationService()
        self.session_manager = AnalysisSessionManager()
        
        # Circuit breakers by service/operation
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.circuit_configs: Dict[str, CircuitBreakerConfig] = {}
        
        # Bulkhead pools for resource isolation
        self.bulkhead_pools: Dict[str, BulkheadPool] = {
            'analysis_execution': BulkheadPool('analysis_execution', max_concurrent=5, max_queue_size=50),
            'knowledge_loading': BulkheadPool('knowledge_loading', max_concurrent=10, max_queue_size=100),
            'content_processing': BulkheadPool('content_processing', max_concurrent=15, max_queue_size=200),
            'vector_operations': BulkheadPool('vector_operations', max_concurrent=8, max_queue_size=80),
            'ai_model_inference': BulkheadPool('ai_model_inference', max_concurrent=3, max_queue_size=30)
        }
        
        # Operation metrics tracking
        self.operation_metrics: Dict[str, OperationMetrics] = {}
        
        # GCP monitoring clients
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.error_client = error_reporting.Client() if error_reporting else None
        self.publisher = pubsub_v1.PublisherClient()
        self.firestore_client = firestore.Client(project=self.settings.project_id)
        
        # Semaphores for bulkhead pools
        self.pool_semaphores: Dict[str, asyncio.Semaphore] = {
            name: asyncio.Semaphore(pool.max_concurrent)
            for name, pool in self.bulkhead_pools.items()
        }
        
        # Background tasks for maintenance
        self._maintenance_tasks: List[asyncio.Task] = []
        
        logger.info("✅ Advanced Orchestrator initialized with circuit breaker patterns")
    
    async def initialize(self):
        """Initialize the orchestrator and start background tasks"""
        try:
            # Setup default circuit breaker configurations
            await self._setup_default_circuit_configs()
            
            # Start background maintenance tasks
            await self._start_maintenance_tasks()
            
            logger.info("Advanced Orchestrator fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Advanced Orchestrator: {e}")
            if self.error_client:
                self.error_client.report_exception()
            raise
    
    async def _setup_default_circuit_configs(self):
        """Setup default circuit breaker configurations for different operations"""
        
        # Analysis operations - more tolerant due to complexity
        self.circuit_configs['analysis_execution'] = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=120,
            success_threshold=2,
            timeout_duration=300.0,  # 5 minutes for complex analysis
            expected_exceptions=(Exception,)
        )
        
        # Knowledge loading - medium tolerance
        self.circuit_configs['knowledge_loading'] = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            success_threshold=3,
            timeout_duration=60.0,
            expected_exceptions=(Exception,)
        )
        
        # Content processing - high tolerance due to external dependencies
        self.circuit_configs['content_processing'] = CircuitBreakerConfig(
            failure_threshold=8,
            recovery_timeout=45,
            success_threshold=4,
            timeout_duration=45.0,
            expected_exceptions=(Exception,)
        )
        
        # Vector operations - low tolerance, should be reliable
        self.circuit_configs['vector_operations'] = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            success_threshold=2,
            timeout_duration=30.0,
            expected_exceptions=(Exception,)
        )
        
        # AI model inference - medium tolerance, can have timeouts
        self.circuit_configs['ai_model_inference'] = CircuitBreakerConfig(
            failure_threshold=4,
            recovery_timeout=90,
            success_threshold=3,
            timeout_duration=120.0,
            expected_exceptions=(Exception,)
        )
    
    async def _start_maintenance_tasks(self):
        """Start background maintenance tasks"""
        
        # Circuit breaker state monitoring
        circuit_monitor_task = asyncio.create_task(
            self._circuit_breaker_monitor_loop()
        )
        self._maintenance_tasks.append(circuit_monitor_task)
        
        # Metrics collection and reporting
        metrics_task = asyncio.create_task(
            self._metrics_collection_loop()
        )
        self._maintenance_tasks.append(metrics_task)
        
        # Pool health monitoring
        pool_monitor_task = asyncio.create_task(
            self._pool_health_monitor_loop()
        )
        self._maintenance_tasks.append(pool_monitor_task)
        
        logger.info("Started background maintenance tasks")
    
    @asynccontextmanager
    async def bulkhead_protection(self, pool_name: str, operation_name: str, priority: OperationPriority = OperationPriority.MEDIUM):
        """
        Bulkhead pattern implementation with priority queuing
        """
        if pool_name not in self.bulkhead_pools:
            raise ValueError(f"Unknown bulkhead pool: {pool_name}")
        
        pool = self.bulkhead_pools[pool_name]
        semaphore = self.pool_semaphores[pool_name]
        
        # Check if pool is at capacity
        if pool.queue_size >= pool.max_queue_size:
            raise RuntimeError(f"Bulkhead pool {pool_name} queue is full")
        
        pool.queue_size += 1
        start_time = time.time()
        
        try:
            # Acquire semaphore with timeout based on priority
            timeout = pool.timeout * (4 - priority.value)  # Higher priority = longer timeout
            
            async with asyncio.timeout(timeout):
                async with semaphore:
                    pool.current_count += 1
                    pool.queue_size -= 1
                    
                    wait_time = time.time() - start_time
                    
                    # Record pool utilization metrics
                    await self._record_pool_metrics(pool_name, wait_time)
                    
                    logger.debug(f"Acquired {pool_name} resource for {operation_name} after {wait_time:.2f}s")
                    
                    try:
                        yield
                    finally:
                        pool.current_count -= 1
                        
        except asyncio.TimeoutError:
            pool.queue_size -= 1
            logger.error(f"Timeout waiting for {pool_name} resource for {operation_name}")
            raise
        except Exception as e:
            pool.queue_size -= 1
            logger.error(f"Error in bulkhead protection for {pool_name}: {e}")
            raise
    
    async def execute_with_circuit_breaker(self, 
                                         operation_name: str, 
                                         operation_func: Callable,
                                         *args, 
                                         pool_name: str = None,
                                         priority: OperationPriority = OperationPriority.MEDIUM,
                                         **kwargs) -> Any:
        """
        Execute operation with circuit breaker protection and optional bulkhead isolation
        """
        # Get or create circuit breaker state
        if operation_name not in self.circuit_breakers:
            self.circuit_breakers[operation_name] = CircuitBreakerState()
        
        circuit = self.circuit_breakers[operation_name]
        config = self.circuit_configs.get(operation_name, CircuitBreakerConfig())
        
        # Check circuit state
        current_time = datetime.now(timezone.utc)
        
        if circuit.state == CircuitState.OPEN:
            if current_time < circuit.next_attempt_time:
                raise RuntimeError(f"Circuit breaker OPEN for {operation_name}. Next attempt at {circuit.next_attempt_time}")
            else:
                # Move to half-open state
                circuit.state = CircuitState.HALF_OPEN
                circuit.success_count = 0
                logger.info(f"Circuit breaker for {operation_name} moved to HALF_OPEN")
        
        elif circuit.state == CircuitState.HALF_OPEN:
            if circuit.success_count >= config.success_threshold:
                # Close the circuit
                circuit.state = CircuitState.CLOSED
                circuit.failure_count = 0
                circuit.success_count = 0
                logger.info(f"Circuit breaker for {operation_name} CLOSED after recovery")
        
        # Initialize or get operation metrics
        if operation_name not in self.operation_metrics:
            self.operation_metrics[operation_name] = OperationMetrics(operation_name)
        
        metrics = self.operation_metrics[operation_name]
        
        # Execute operation with optional bulkhead protection
        start_time = time.time()
        
        try:
            if pool_name:
                async with self.bulkhead_protection(pool_name, operation_name, priority):
                    result = await asyncio.wait_for(
                        operation_func(*args, **kwargs),
                        timeout=config.timeout_duration
                    )
            else:
                result = await asyncio.wait_for(
                    operation_func(*args, **kwargs),
                    timeout=config.timeout_duration
                )
            
            # Operation succeeded
            response_time = time.time() - start_time
            
            await self._record_success(operation_name, circuit, metrics, response_time)
            
            return result
            
        except config.expected_exceptions as e:
            response_time = time.time() - start_time
            
            await self._record_failure(operation_name, circuit, config, metrics, response_time, str(e))
            
            raise
    
    async def _record_success(self, operation_name: str, circuit: CircuitBreakerState, 
                            metrics: OperationMetrics, response_time: float):
        """Record successful operation execution"""
        
        # Update circuit breaker
        circuit.total_requests += 1
        
        if circuit.state == CircuitState.HALF_OPEN:
            circuit.success_count += 1
        elif circuit.state == CircuitState.CLOSED:
            circuit.failure_count = max(0, circuit.failure_count - 1)  # Gradually reduce failure count
        
        # Update metrics
        metrics.total_requests += 1
        metrics.successful_requests += 1
        metrics.response_times.append(response_time)
        
        # Keep only last 1000 response times for percentile calculations
        if len(metrics.response_times) > 1000:
            metrics.response_times = metrics.response_times[-1000:]
        
        # Calculate updated statistics
        metrics.avg_response_time = statistics.mean(metrics.response_times)
        if len(metrics.response_times) >= 20:  # Need minimum samples for percentiles
            sorted_times = sorted(metrics.response_times)
            metrics.p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
            metrics.p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
        
        metrics.last_updated = datetime.now(timezone.utc)
        
        # Record metrics to GCP Monitoring
        await self._record_gcp_metrics(operation_name, 'success', response_time)
        
        logger.debug(f"✅ {operation_name} succeeded in {response_time:.3f}s")
    
    async def _record_failure(self, operation_name: str, circuit: CircuitBreakerState, 
                            config: CircuitBreakerConfig, metrics: OperationMetrics, 
                            response_time: float, error_message: str):
        """Record failed operation execution"""
        
        # Update circuit breaker
        circuit.total_requests += 1
        circuit.total_failures += 1
        circuit.failure_count += 1
        circuit.last_failure_time = datetime.now(timezone.utc)
        
        # Check if circuit should open
        if (circuit.state == CircuitState.CLOSED and 
            circuit.failure_count >= config.failure_threshold):
            
            circuit.state = CircuitState.OPEN
            circuit.next_attempt_time = datetime.now(timezone.utc) + timedelta(seconds=config.recovery_timeout)
            
            logger.error(f"🔴 Circuit breaker OPENED for {operation_name} after {circuit.failure_count} failures")
            
            # Publish circuit breaker event
            await self._publish_circuit_breaker_event(operation_name, 'OPENED', circuit)
        
        elif circuit.state == CircuitState.HALF_OPEN:
            # Return to open state
            circuit.state = CircuitState.OPEN
            circuit.next_attempt_time = datetime.now(timezone.utc) + timedelta(seconds=config.recovery_timeout)
            
            logger.error(f"🔴 Circuit breaker returned to OPEN for {operation_name}")
        
        # Update metrics
        metrics.total_requests += 1
        metrics.failed_requests += 1
        metrics.response_times.append(response_time)
        
        if len(metrics.response_times) > 1000:
            metrics.response_times = metrics.response_times[-1000:]
        
        # Recalculate statistics
        metrics.avg_response_time = statistics.mean(metrics.response_times)
        metrics.last_updated = datetime.now(timezone.utc)
        
        # Record metrics and error to GCP
        await self._record_gcp_metrics(operation_name, 'failure', response_time)
        
        # Report error to Error Reporting
        if self.error_client:
            self.error_client.report(f"Operation {operation_name} failed: {error_message}")
        
        logger.error(f"❌ {operation_name} failed in {response_time:.3f}s: {error_message}")
    
    async def _record_gcp_metrics(self, operation_name: str, result: str, response_time: float):
        """Record custom metrics to GCP Monitoring"""
        try:
            project_name = f"projects/{self.settings.project_id}"
            
            # Response time metric
            response_time_series = monitoring_v3.TimeSeries()
            response_time_series.metric.type = "custom.googleapis.com/validatus/operation_response_time"
            response_time_series.resource.type = "global"
            response_time_series.metric.labels['operation'] = operation_name
            response_time_series.metric.labels['result'] = result
            
            now = time.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)
            interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": seconds, "nanos": nanos}}
            )
            
            point = monitoring_v3.Point({
                "interval": interval,
                "value": {"double_value": response_time}
            })
            response_time_series.points = [point]
            
            # Counter metric
            counter_series = monitoring_v3.TimeSeries()
            counter_series.metric.type = "custom.googleapis.com/validatus/operation_count"
            counter_series.resource.type = "global"
            counter_series.metric.labels['operation'] = operation_name
            counter_series.metric.labels['result'] = result
            
            counter_point = monitoring_v3.Point({
                "interval": interval,
                "value": {"int64_value": 1}
            })
            counter_series.points = [counter_point]
            
            # Send metrics
            self.monitoring_client.create_time_series(
                name=project_name, 
                time_series=[response_time_series, counter_series]
            )
            
        except Exception as e:
            logger.error(f"Failed to record GCP metrics: {e}")
    
    async def _record_pool_metrics(self, pool_name: str, wait_time: float):
        """Record bulkhead pool utilization metrics"""
        try:
            pool = self.bulkhead_pools[pool_name]
            
            project_name = f"projects/{self.settings.project_id}"
            
            # Pool utilization metric
            utilization_series = monitoring_v3.TimeSeries()
            utilization_series.metric.type = "custom.googleapis.com/validatus/pool_utilization"
            utilization_series.resource.type = "global"
            utilization_series.metric.labels['pool'] = pool_name
            
            now = time.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)
            interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": seconds, "nanos": nanos}}
            )
            
            utilization = (pool.current_count / pool.max_concurrent) * 100
            
            point = monitoring_v3.Point({
                "interval": interval,
                "value": {"double_value": utilization}
            })
            utilization_series.points = [point]
            
            # Wait time metric
            wait_time_series = monitoring_v3.TimeSeries()
            wait_time_series.metric.type = "custom.googleapis.com/validatus/pool_wait_time"
            wait_time_series.resource.type = "global"
            wait_time_series.metric.labels['pool'] = pool_name
            
            wait_point = monitoring_v3.Point({
                "interval": interval,
                "value": {"double_value": wait_time}
            })
            wait_time_series.points = [wait_point]
            
            # Send metrics
            self.monitoring_client.create_time_series(
                name=project_name, 
                time_series=[utilization_series, wait_time_series]
            )
            
        except Exception as e:
            logger.error(f"Failed to record pool metrics: {e}")
    
    async def _publish_circuit_breaker_event(self, operation_name: str, event_type: str, circuit: CircuitBreakerState):
        """Publish circuit breaker state change events"""
        try:
            topic_path = self.publisher.topic_path(
                self.settings.project_id, 
                f"validatus-circuit-breaker-events"
            )
            
            event_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'operation_name': operation_name,
                'event_type': event_type,
                'circuit_state': circuit.state.value,
                'failure_count': circuit.failure_count,
                'total_requests': circuit.total_requests,
                'total_failures': circuit.total_failures
            }
            
            message_data = json.dumps(event_data).encode('utf-8')
            
            # Publish the message
            future = self.publisher.publish(topic_path, message_data)
            await asyncio.get_event_loop().run_in_executor(None, future.result)
            
            logger.info(f"Published circuit breaker event: {operation_name} {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to publish circuit breaker event: {e}")
    
    async def _circuit_breaker_monitor_loop(self):
        """Background task to monitor circuit breaker states"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                current_time = datetime.now(timezone.utc)
                
                for operation_name, circuit in self.circuit_breakers.items():
                    # Check if open circuits should move to half-open
                    if (circuit.state == CircuitState.OPEN and 
                        circuit.next_attempt_time and
                        current_time >= circuit.next_attempt_time):
                        
                        circuit.state = CircuitState.HALF_OPEN
                        circuit.success_count = 0
                        
                        logger.info(f"Circuit breaker for {operation_name} moved to HALF_OPEN for testing")
                        
                        await self._publish_circuit_breaker_event(operation_name, 'HALF_OPEN', circuit)
                
                # Store circuit breaker states in Firestore for persistence
                await self._persist_circuit_states()
                
            except Exception as e:
                logger.error(f"Error in circuit breaker monitor loop: {e}")
    
    async def _metrics_collection_loop(self):
        """Background task to collect and report metrics"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect metrics every minute
                
                # Generate aggregated metrics report
                metrics_summary = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'operations': {},
                    'circuit_breakers': {},
                    'bulkhead_pools': {}
                }
                
                # Operation metrics
                for operation_name, metrics in self.operation_metrics.items():
                    success_rate = (metrics.successful_requests / max(1, metrics.total_requests)) * 100
                    
                    metrics_summary['operations'][operation_name] = {
                        'total_requests': metrics.total_requests,
                        'success_rate': success_rate,
                        'avg_response_time': metrics.avg_response_time,
                        'p95_response_time': metrics.p95_response_time,
                        'p99_response_time': metrics.p99_response_time
                    }
                
                # Circuit breaker states
                for operation_name, circuit in self.circuit_breakers.items():
                    failure_rate = (circuit.total_failures / max(1, circuit.total_requests)) * 100
                    
                    metrics_summary['circuit_breakers'][operation_name] = {
                        'state': circuit.state.value,
                        'failure_count': circuit.failure_count,
                        'total_failures': circuit.total_failures,
                        'total_requests': circuit.total_requests,
                        'failure_rate': failure_rate
                    }
                
                # Bulkhead pool states
                for pool_name, pool in self.bulkhead_pools.items():
                    utilization = (pool.current_count / pool.max_concurrent) * 100
                    
                    metrics_summary['bulkhead_pools'][pool_name] = {
                        'current_count': pool.current_count,
                        'max_concurrent': pool.max_concurrent,
                        'queue_size': pool.queue_size,
                        'utilization': utilization
                    }
                
                # Store metrics summary in Firestore
                doc_ref = self.firestore_client.collection('orchestrator_metrics').document(
                    f"summary_{int(time.time())}"
                )
                await asyncio.get_event_loop().run_in_executor(
                    None, doc_ref.set, metrics_summary
                )
                
                logger.debug("Collected and stored orchestrator metrics")
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
    
    async def _pool_health_monitor_loop(self):
        """Background task to monitor bulkhead pool health"""
        while True:
            try:
                await asyncio.sleep(45)  # Check every 45 seconds
                
                for pool_name, pool in self.bulkhead_pools.items():
                    utilization = (pool.current_count / pool.max_concurrent) * 100
                    queue_utilization = (pool.queue_size / pool.max_queue_size) * 100
                    
                    # Alert on high utilization
                    if utilization > 80:
                        logger.warning(f"High utilization in {pool_name}: {utilization:.1f}%")
                    
                    if queue_utilization > 70:
                        logger.warning(f"High queue utilization in {pool_name}: {queue_utilization:.1f}%")
                        
                        # Consider dynamic scaling or load shedding
                        if queue_utilization > 90:
                            logger.error(f"Critical queue utilization in {pool_name}: {queue_utilization:.1f}%")
                
            except Exception as e:
                logger.error(f"Error in pool health monitor loop: {e}")
    
    async def _persist_circuit_states(self):
        """Persist circuit breaker states to Firestore"""
        try:
            for operation_name, circuit in self.circuit_breakers.items():
                doc_ref = self.firestore_client.collection('circuit_breaker_states').document(operation_name)
                
                state_data = {
                    'operation_name': operation_name,
                    'state': circuit.state.value,
                    'failure_count': circuit.failure_count,
                    'success_count': circuit.success_count,
                    'total_requests': circuit.total_requests,
                    'total_failures': circuit.total_failures,
                    'last_failure_time': circuit.last_failure_time.isoformat() if circuit.last_failure_time else None,
                    'next_attempt_time': circuit.next_attempt_time.isoformat() if circuit.next_attempt_time else None,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                
                await asyncio.get_event_loop().run_in_executor(
                    None, doc_ref.set, state_data, {'merge': True}
                )
                
        except Exception as e:
            logger.error(f"Failed to persist circuit states: {e}")
    
    # Enhanced analysis operations with circuit breaker protection
    async def execute_strategic_analysis_protected(self, 
                                                 session_id: str, 
                                                 topic: str, 
                                                 user_id: str,
                                                 priority: OperationPriority = OperationPriority.HIGH) -> Dict[str, Any]:
        """Execute strategic analysis with full orchestration protection"""
        
        return await self.execute_with_circuit_breaker(
            operation_name='analysis_execution',
            operation_func=self.session_manager.execute_strategic_analysis,
            session_id=session_id,
            topic=topic,
            user_id=user_id,
            pool_name='analysis_execution',
            priority=priority
        )
    
    async def load_topic_knowledge_protected(self, 
                                           topic: str,
                                           priority: OperationPriority = OperationPriority.MEDIUM) -> Dict[str, Any]:
        """Load topic knowledge with orchestration protection"""
        
        return await self.execute_with_circuit_breaker(
            operation_name='knowledge_loading',
            operation_func=self.session_manager._load_topic_knowledge,
            topic=topic,
            pool_name='knowledge_loading',
            priority=priority
        )
    
    async def get_orchestrator_health(self) -> Dict[str, Any]:
        """Get comprehensive health status of the orchestrator"""
        
        health_status = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'overall_status': 'healthy',
            'circuit_breakers': {},
            'bulkhead_pools': {},
            'operation_metrics': {},
            'maintenance_tasks': len(self._maintenance_tasks),
            'active_maintenance_tasks': len([t for t in self._maintenance_tasks if not t.done()])
        }
        
        # Circuit breaker health
        open_circuits = 0
        for operation_name, circuit in self.circuit_breakers.items():
            health_status['circuit_breakers'][operation_name] = {
                'state': circuit.state.value,
                'failure_count': circuit.failure_count,
                'total_requests': circuit.total_requests,
                'health': 'unhealthy' if circuit.state == CircuitState.OPEN else 'healthy'
            }
            
            if circuit.state == CircuitState.OPEN:
                open_circuits += 1
        
        # Bulkhead pool health
        stressed_pools = 0
        for pool_name, pool in self.bulkhead_pools.items():
            utilization = (pool.current_count / pool.max_concurrent) * 100
            queue_utilization = (pool.queue_size / pool.max_queue_size) * 100
            
            pool_health = 'healthy'
            if utilization > 80 or queue_utilization > 70:
                pool_health = 'stressed'
                stressed_pools += 1
            elif utilization > 95 or queue_utilization > 90:
                pool_health = 'critical'
                stressed_pools += 1
            
            health_status['bulkhead_pools'][pool_name] = {
                'utilization': utilization,
                'queue_utilization': queue_utilization,
                'current_count': pool.current_count,
                'max_concurrent': pool.max_concurrent,
                'health': pool_health
            }
        
        # Operation metrics summary
        for operation_name, metrics in self.operation_metrics.items():
            if metrics.total_requests > 0:
                success_rate = (metrics.successful_requests / metrics.total_requests) * 100
                health_status['operation_metrics'][operation_name] = {
                    'success_rate': success_rate,
                    'avg_response_time': metrics.avg_response_time,
                    'total_requests': metrics.total_requests,
                    'health': 'healthy' if success_rate > 95 else 'degraded' if success_rate > 80 else 'unhealthy'
                }
        
        # Determine overall status
        if open_circuits > 0 or stressed_pools > 0:
            health_status['overall_status'] = 'degraded'
        
        if open_circuits > 2 or stressed_pools > 3:
            health_status['overall_status'] = 'unhealthy'
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        logger.info("Shutting down Advanced Orchestrator...")
        
        # Cancel maintenance tasks
        for task in self._maintenance_tasks:
            task.cancel()
        
        await asyncio.gather(*self._maintenance_tasks, return_exceptions=True)
        
        # Final metrics persistence
        await self._persist_circuit_states()
        
        logger.info("Advanced Orchestrator shutdown completed")

__all__ = [
    'AdvancedOrchestrator', 'CircuitBreakerConfig', 'OperationPriority',
    'CircuitState', 'BulkheadPool', 'OperationMetrics'
]
