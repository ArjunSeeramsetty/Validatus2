# backend/app/services/analysis_optimization_service.py

import asyncio
import logging
import time
import gc
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import numpy as np
import psutil

from google.cloud import monitoring_v3

from ..models.analysis_models import OptimizationMetrics
from ..middleware.monitoring import performance_monitor

logger = logging.getLogger(__name__)

@dataclass
class TaskGroup:
    """Task group for optimization"""
    group_name: str
    tasks: List[Dict[str, Any]]
    complexity: str
    estimated_duration: float
    resource_requirements: Dict[str, float]

@dataclass
class OptimizationConfig:
    """Configuration for optimization parameters"""
    max_concurrent_tasks: int = 10
    memory_threshold_mb: int = 1024
    cache_enabled: bool = True
    error_recovery_enabled: bool = True
    max_retries: int = 3
    batch_size: int = 1000

class AnalysisOptimizationService:
    """Advanced optimization for large-scale strategic analysis"""
    
    def __init__(self):
        self.config = OptimizationConfig()
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        # Performance tracking
        self.performance_cache = {}
        self.task_completion_times = {}
        self.memory_usage_history = []
        
        # Cache management
        self.memory_cache = {}
        self.distributed_cache = {}
        self.cache_hit_count = 0
        self.cache_miss_count = 0
        
    @performance_monitor
    async def optimize_parallel_processing(self, 
                                         analysis_tasks: List[Dict[str, Any]],
                                         max_concurrent: int = None) -> List[Dict[str, Any]]:
        """Optimize parallel processing for large-scale analysis"""
        
        max_concurrent = max_concurrent or self.config.max_concurrent_tasks
        logger.info(f"Optimizing parallel processing for {len(analysis_tasks)} tasks with max_concurrent={max_concurrent}")
        
        start_time = time.time()
        
        try:
            # Group tasks by complexity and resource requirements
            task_groups = self._group_tasks_by_complexity(analysis_tasks)
            
            results = []
            
            for group_name, tasks in task_groups.items():
                logger.info(f"Processing {len(tasks)} tasks in group '{group_name}'")
                
                # Adjust concurrency based on task complexity
                group_concurrency = self._calculate_optimal_concurrency(group_name, len(tasks), max_concurrent)
                
                # Process tasks with optimized concurrency
                semaphore = asyncio.Semaphore(group_concurrency)
                group_tasks = [
                    self._process_task_with_optimization(task, semaphore)
                    for task in tasks
                ]
                
                group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
                
                # Handle any exceptions and retry failed tasks
                processed_results = await self._handle_task_exceptions(group_results, tasks)
                results.extend(processed_results)
            
            # Calculate optimization metrics
            total_time = time.time() - start_time
            metrics = await self._calculate_optimization_metrics(results, total_time)
            
            logger.info(f"✅ Completed parallel processing optimization in {total_time:.2f}s")
            logger.info(f"Metrics - Throughput: {metrics.throughput:.2f} tasks/s, Cache hit rate: {metrics.cache_hit_rate:.1%}")
            
            return results
            
        except Exception as e:
            logger.error(f"Parallel processing optimization failed: {e}")
            return []

    @performance_monitor
    async def optimize_memory_usage(self, 
                                  large_dataset: List[Dict[str, Any]],
                                  chunk_size: int = None) -> List[Dict[str, Any]]:
        """Optimize memory usage for large dataset processing"""
        
        chunk_size = chunk_size or self.config.batch_size
        logger.info(f"Optimizing memory usage for dataset of {len(large_dataset)} items with chunk_size={chunk_size}")
        
        results = []
        memory_usage = []
        
        try:
            # Process in optimized chunks
            for i in range(0, len(large_dataset), chunk_size):
                chunk = large_dataset[i:i + chunk_size]
                
                # Monitor memory usage
                pre_memory = self._get_memory_usage()
                
                # Process chunk with memory optimization
                chunk_results = await self._process_chunk_optimized(chunk)
                results.extend(chunk_results)
                
                # Track memory usage
                post_memory = self._get_memory_usage()
                memory_usage.append(post_memory - pre_memory)
                
                # Trigger garbage collection if needed
                if post_memory > self.config.memory_threshold_mb:
                    gc.collect()
                    logger.info("Triggered garbage collection for memory optimization")
                
                # Update memory history
                self.memory_usage_history.append(post_memory)
                
                # Log progress
                if (i // chunk_size) % 10 == 0:
                    logger.info(f"Processed {i + len(chunk)}/{len(large_dataset)} items")
            
            avg_memory_per_chunk = np.mean(memory_usage) if memory_usage else 0
            logger.info(f"✅ Memory optimization completed. Avg memory per chunk: {avg_memory_per_chunk:.2f} MB")
            
            return results
            
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
            return []

    @performance_monitor
    async def implement_advanced_caching(self, 
                                       cache_keys: List[str],
                                       analysis_functions: List[callable]) -> Dict[str, Any]:
        """Implement multi-level caching for analysis optimization"""
        
        logger.info(f"Implementing advanced caching for {len(cache_keys)} items")
        
        # Level 1: Memory cache
        memory_results = {}
        
        # Level 2: Distributed cache (simulated)
        distributed_results = {}
        
        # Level 3: Persistent cache (simulated)
        persistent_results = {}
        
        cache_stats = {
            'memory_hits': 0,
            'distributed_hits': 0,
            'persistent_hits': 0,
            'cache_misses': 0
        }
        
        try:
            for i, cache_key in enumerate(cache_keys):
                analysis_func = analysis_functions[i % len(analysis_functions)]
                
                # Check memory cache first
                if cache_key in self.memory_cache:
                    memory_results[cache_key] = self.memory_cache[cache_key]
                    cache_stats['memory_hits'] += 1
                    continue
                
                # Check distributed cache
                distributed_result = await self._get_distributed_cache(cache_key)
                if distributed_result is not None:
                    distributed_results[cache_key] = distributed_result
                    # Also store in memory cache for future requests
                    self.memory_cache[cache_key] = distributed_result
                    cache_stats['distributed_hits'] += 1
                    continue
                
                # Check persistent cache
                persistent_result = await self._get_persistent_cache(cache_key)
                if persistent_result is not None:
                    persistent_results[cache_key] = persistent_result
                    # Store in both memory and distributed caches
                    self.memory_cache[cache_key] = persistent_result
                    await self._set_distributed_cache(cache_key, persistent_result)
                    cache_stats['persistent_hits'] += 1
                    continue
                
                # Cache miss - compute and store at all levels
                try:
                    computed_result = await analysis_func(cache_key)
                    
                    # Store at all cache levels
                    self.memory_cache[cache_key] = computed_result
                    await self._set_distributed_cache(cache_key, computed_result)
                    await self._set_persistent_cache(cache_key, computed_result)
                    
                    persistent_results[cache_key] = computed_result
                    cache_stats['cache_misses'] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to compute result for cache key {cache_key}: {e}")
                    continue
            
            # Calculate cache efficiency
            total_requests = len(cache_keys)
            cache_hit_rate = (cache_stats['memory_hits'] + cache_stats['distributed_hits'] + cache_stats['persistent_hits']) / total_requests
            
            logger.info(f"✅ Advanced caching completed. Hit rate: {cache_hit_rate:.1%}")
            logger.info(f"Cache breakdown - Memory: {cache_stats['memory_hits']}, Distributed: {cache_stats['distributed_hits']}, Persistent: {cache_stats['persistent_hits']}, Misses: {cache_stats['cache_misses']}")
            
            # Combine all results
            all_results = {**memory_results, **distributed_results, **persistent_results}
            all_results['cache_stats'] = cache_stats
            
            return all_results
            
        except Exception as e:
            logger.error(f"Advanced caching failed: {e}")
            return {'cache_stats': cache_stats, 'error': str(e)}

    @performance_monitor
    async def implement_error_recovery(self, 
                                     failed_tasks: List[Dict[str, Any]],
                                     max_retries: int = None) -> Dict[str, Any]:
        """Implement intelligent error recovery with exponential backoff"""
        
        max_retries = max_retries or self.config.max_retries
        logger.info(f"Implementing error recovery for {len(failed_tasks)} failed tasks with max_retries={max_retries}")
        
        recovered_results = []
        permanent_failures = []
        
        try:
            for task in failed_tasks:
                task_id = task.get('id', 'unknown')
                retry_count = task.get('retry_count', 0)
                
                if retry_count >= max_retries:
                    permanent_failures.append(task)
                    logger.warning(f"Task {task_id} permanently failed after {max_retries} retries")
                    continue
                
                try:
                    # Implement exponential backoff
                    backoff_delay = 2 ** retry_count
                    await asyncio.sleep(backoff_delay)
                    
                    # Retry with error recovery optimizations
                    recovered_result = await self._retry_with_recovery(task)
                    recovered_results.append(recovered_result)
                    
                    logger.info(f"Successfully recovered task {task_id} on retry {retry_count + 1}")
                    
                except Exception as e:
                    # Increment retry count and try again
                    task['retry_count'] = retry_count + 1
                    task['last_error'] = str(e)
                    
                    logger.error(f"Retry {retry_count + 1} failed for task {task_id}: {e}")
                    
                    # Add back to failed tasks for next iteration
                    if task['retry_count'] < max_retries:
                        failed_tasks.append(task)
            
            recovery_rate = len(recovered_results) / len(failed_tasks) if failed_tasks else 1.0
            
            logger.info(f"✅ Error recovery completed. Recovered: {len(recovered_results)}, Permanent failures: {len(permanent_failures)}")
            
            return {
                'recovered_results': recovered_results,
                'permanent_failures': permanent_failures,
                'recovery_rate': recovery_rate
            }
            
        except Exception as e:
            logger.error(f"Error recovery failed: {e}")
            return {
                'recovered_results': [],
                'permanent_failures': failed_tasks,
                'recovery_rate': 0.0,
                'error': str(e)
            }

    @performance_monitor
    async def optimize_resource_utilization(self, 
                                          current_workload: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize resource utilization based on current system state"""
        
        logger.info(f"Optimizing resource utilization for {len(current_workload)} tasks")
        
        try:
            # Get current system metrics
            system_metrics = self._get_system_metrics()
            
            # Analyze workload characteristics
            workload_analysis = self._analyze_workload_characteristics(current_workload)
            
            # Calculate optimal resource allocation
            resource_allocation = self._calculate_optimal_resource_allocation(
                system_metrics, workload_analysis
            )
            
            # Apply optimizations
            optimization_results = await self._apply_resource_optimizations(
                current_workload, resource_allocation
            )
            
            logger.info(f"✅ Resource utilization optimization completed")
            
            return {
                'system_metrics': system_metrics,
                'workload_analysis': workload_analysis,
                'resource_allocation': resource_allocation,
                'optimization_results': optimization_results
            }
            
        except Exception as e:
            logger.error(f"Resource utilization optimization failed: {e}")
            return {'error': str(e)}

    def _group_tasks_by_complexity(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group tasks by computational complexity"""
        
        groups = {
            'light': [],      # Simple calculations, fast operations
            'medium': [],     # Moderate AI inference, database queries
            'heavy': [],      # Large language model operations, complex analysis
            'io_bound': []    # Network requests, file operations
        }
        
        for task in tasks:
            complexity = task.get('complexity', 'medium')
            if complexity in groups:
                groups[complexity].append(task)
            else:
                groups['medium'].append(task)  # Default to medium
        
        return {k: v for k, v in groups.items() if v}  # Remove empty groups

    def _calculate_optimal_concurrency(self, group_name: str, task_count: int, max_concurrent: int) -> int:
        """Calculate optimal concurrency based on task type and system resources"""
        
        base_concurrency = {
            'light': min(20, task_count),
            'medium': min(10, task_count), 
            'heavy': min(5, task_count),
            'io_bound': min(50, task_count)
        }
        
        calculated_concurrency = base_concurrency.get(group_name, 10)
        
        # Adjust based on available system resources
        memory_usage = self._get_memory_usage()
        if memory_usage > self.config.memory_threshold_mb * 0.8:
            calculated_concurrency = max(1, calculated_concurrency // 2)
        
        return min(calculated_concurrency, max_concurrent)

    async def _process_task_with_optimization(self, task: Dict[str, Any], semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Process individual task with optimization techniques"""
        
        async with semaphore:
            task_id = task.get('id', 'unknown')
            
            try:
                # Apply performance optimizations based on task type
                optimized_task = await self._apply_task_optimizations(task)
                
                # Execute the task
                result = await self._execute_optimized_task(optimized_task)
                
                # Track completion time
                self.task_completion_times[task_id] = time.time()
                
                return {
                    'task_id': task_id,
                    'result': result,
                    'status': 'success',
                    'optimization_applied': True
                }
                
            except Exception as e:
                logger.error(f"Task {task_id} failed during optimized processing: {e}")
                return {
                    'task_id': task_id,
                    'error': str(e),
                    'status': 'error',
                    'optimization_applied': False
                }

    async def _process_chunk_optimized(self, chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a chunk of data with memory optimization"""
        
        results = []
        
        try:
            # Process chunk with memory-efficient techniques
            for item in chunk:
                # Simulate processing
                processed_item = await self._process_single_item(item)
                results.append(processed_item)
            
            # Clear temporary variables
            del chunk
            
            return results
            
        except Exception as e:
            logger.error(f"Chunk processing failed: {e}")
            return []

    async def _process_single_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single item with optimization"""
        
        # Simulate processing based on item type
        item_type = item.get('type', 'unknown')
        
        if item_type == 'layer_scoring':
            return await self._optimized_layer_scoring(item)
        elif item_type == 'factor_calculation':
            return await self._optimized_factor_calculation(item)
        elif item_type == 'segment_analysis':
            return await self._optimized_segment_analysis(item)
        else:
            return await self._generic_item_processing(item)

    async def _optimized_layer_scoring(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Optimized layer scoring processing"""
        # Simulate optimized processing
        await asyncio.sleep(0.1)  # Simulate processing time
        return {'processed': True, 'type': 'layer_scoring', 'score': 0.8}

    async def _optimized_factor_calculation(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Optimized factor calculation processing"""
        # Simulate optimized processing
        await asyncio.sleep(0.05)  # Simulate processing time
        return {'processed': True, 'type': 'factor_calculation', 'value': 0.75}

    async def _optimized_segment_analysis(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Optimized segment analysis processing"""
        # Simulate optimized processing
        await asyncio.sleep(0.08)  # Simulate processing time
        return {'processed': True, 'type': 'segment_analysis', 'attractiveness': 0.7}

    async def _generic_item_processing(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Generic item processing"""
        # Simulate generic processing
        await asyncio.sleep(0.02)  # Simulate processing time
        return {'processed': True, 'type': 'generic', 'result': 'success'}

    async def _apply_task_optimizations(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations to a task"""
        
        optimized_task = task.copy()
        
        # Add optimization metadata
        optimized_task['optimization_applied'] = True
        optimized_task['optimization_timestamp'] = time.time()
        
        # Apply specific optimizations based on task type
        task_type = task.get('type', 'unknown')
        
        if task_type in ['layer_scoring', 'factor_calculation']:
            # Add caching optimization
            optimized_task['cache_enabled'] = True
            optimized_task['batch_processing'] = True
        
        elif task_type == 'segment_analysis':
            # Add parallel processing optimization
            optimized_task['parallel_processing'] = True
            optimized_task['chunk_size'] = 100
        
        return optimized_task

    async def _execute_optimized_task(self, task: Dict[str, Any]) -> Any:
        """Execute a single optimized task"""
        
        task_type = task.get('type', 'unknown')
        
        # Simulate task execution with optimizations
        if task.get('cache_enabled'):
            # Check cache first
            cache_key = f"{task_type}_{task.get('id', 'unknown')}"
            if cache_key in self.memory_cache:
                return self.memory_cache[cache_key]
        
        # Execute task (simulated)
        await asyncio.sleep(0.1)  # Simulate processing time
        
        result = {'task_type': task_type, 'executed': True}
        
        # Cache result if enabled
        if task.get('cache_enabled'):
            cache_key = f"{task_type}_{task.get('id', 'unknown')}"
            self.memory_cache[cache_key] = result
        
        return result

    async def _handle_task_exceptions(self, 
                                    group_results: List[Any], 
                                    original_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Handle exceptions from task execution"""
        
        processed_results = []
        
        for i, result in enumerate(group_results):
            if isinstance(result, Exception):
                # Create error result
                error_result = {
                    'task_id': original_tasks[i].get('id', 'unknown'),
                    'error': str(result),
                    'status': 'error',
                    'exception_type': type(result).__name__
                }
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results

    async def _retry_with_recovery(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Retry a task with recovery optimizations"""
        
        # Apply recovery optimizations
        recovery_task = task.copy()
        recovery_task['recovery_mode'] = True
        recovery_task['timeout'] = 30  # Add timeout
        
        # Execute with recovery
        try:
            result = await self._execute_optimized_task(recovery_task)
            return {
                'task_id': task.get('id', 'unknown'),
                'result': result,
                'status': 'recovered',
                'recovery_applied': True
            }
        except Exception as e:
            raise e

    async def _get_distributed_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from distributed cache"""
        # Simulate distributed cache
        return self.distributed_cache.get(cache_key)

    async def _set_distributed_cache(self, cache_key: str, value: Any):
        """Set value in distributed cache"""
        # Simulate distributed cache
        self.distributed_cache[cache_key] = value

    async def _get_persistent_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from persistent cache"""
        # Simulate persistent cache (would be database/disk)
        return None  # Simplified implementation

    async def _set_persistent_cache(self, cache_key: str, value: Any):
        """Set value in persistent cache"""
        # Simulate persistent cache (would be database/disk)
        pass  # Simplified implementation

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory_percent,
                'disk_usage': disk_percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'disk_usage': 0.0,
                'memory_available_mb': 0.0,
                'timestamp': time.time()
            }

    def _analyze_workload_characteristics(self, workload: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze characteristics of the current workload"""
        
        if not workload:
            return {'total_tasks': 0}
        
        # Analyze task types
        task_types = {}
        for task in workload:
            task_type = task.get('type', 'unknown')
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        # Analyze complexity distribution
        complexity_dist = {}
        for task in workload:
            complexity = task.get('complexity', 'medium')
            complexity_dist[complexity] = complexity_dist.get(complexity, 0) + 1
        
        return {
            'total_tasks': len(workload),
            'task_types': task_types,
            'complexity_distribution': complexity_dist,
            'average_task_size': sum(len(str(task)) for task in workload) / len(workload)
        }

    def _calculate_optimal_resource_allocation(self, 
                                             system_metrics: Dict[str, Any],
                                             workload_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal resource allocation"""
        
        cpu_usage = system_metrics.get('cpu_usage', 0)
        memory_usage = system_metrics.get('memory_usage', 0)
        total_tasks = workload_analysis.get('total_tasks', 0)
        
        # Calculate optimal concurrency based on system state
        optimal_concurrency = self.config.max_concurrent_tasks
        
        if cpu_usage > 80:
            optimal_concurrency = max(1, optimal_concurrency // 2)
        
        if memory_usage > 80:
            optimal_concurrency = max(1, optimal_concurrency // 2)
        
        # Adjust based on workload characteristics
        if total_tasks > 1000:
            optimal_concurrency = min(optimal_concurrency, 15)
        
        return {
            'optimal_concurrency': optimal_concurrency,
            'memory_allocation_mb': self.config.memory_threshold_mb,
            'batch_size': self.config.batch_size,
            'cache_enabled': self.config.cache_enabled
        }

    async def _apply_resource_optimizations(self, 
                                          workload: List[Dict[str, Any]],
                                          resource_allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply resource optimizations to workload"""
        
        try:
            # Apply concurrency optimizations
            optimal_concurrency = resource_allocation.get('optimal_concurrency', 10)
            
            # Group tasks for optimal processing
            task_groups = self._group_tasks_by_complexity(workload)
            
            optimization_results = {
                'concurrency_optimization': optimal_concurrency,
                'task_grouping': {name: len(tasks) for name, tasks in task_groups.items()},
                'memory_optimization': resource_allocation.get('memory_allocation_mb', 1024),
                'cache_optimization': resource_allocation.get('cache_enabled', True)
            }
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Resource optimization application failed: {e}")
            return {'error': str(e)}

    async def _calculate_optimization_metrics(self, 
                                            results: List[Dict[str, Any]], 
                                            total_time: float) -> OptimizationMetrics:
        """Calculate comprehensive optimization metrics"""
        
        successful_results = [r for r in results if r.get('status') == 'success']
        
        # Calculate cache hit rate
        total_cache_requests = self.cache_hit_count + self.cache_miss_count
        cache_hit_rate = self.cache_hit_count / total_cache_requests if total_cache_requests > 0 else 0.0
        
        # Calculate throughput
        throughput = len(results) / total_time if total_time > 0 else 0.0
        
        # Calculate error rate
        error_rate = 1.0 - (len(successful_results) / len(results)) if results else 0.0
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(successful_results)
        
        # Calculate parallel efficiency
        parallel_efficiency = self._calculate_parallel_efficiency(results, total_time)
        
        # Calculate resource utilization
        resource_utilization = {
            'cpu_utilization': self._get_system_metrics().get('cpu_usage', 0),
            'memory_utilization': self._get_memory_usage(),
            'cache_utilization': len(self.memory_cache)
        }
        
        return OptimizationMetrics(
            processing_time=total_time,
            memory_usage=self._get_memory_usage(),
            cache_hit_rate=cache_hit_rate,
            error_rate=error_rate,
            throughput=throughput,
            quality_score=quality_score,
            parallel_efficiency=parallel_efficiency,
            resource_utilization=resource_utilization
        )

    def _calculate_quality_score(self, successful_results: List[Dict[str, Any]]) -> float:
        """Calculate quality score based on successful results"""
        
        if not successful_results:
            return 0.0
        
        # Simple quality scoring based on result completeness
        quality_scores = []
        for result in successful_results:
            # Check if result has expected fields
            completeness = 0.0
            if 'result' in result:
                completeness += 0.5
            if 'optimization_applied' in result:
                completeness += 0.3
            if 'status' in result:
                completeness += 0.2
            
            quality_scores.append(completeness)
        
        return sum(quality_scores) / len(quality_scores)

    def _calculate_parallel_efficiency(self, results: List[Dict[str, Any]], total_time: float) -> float:
        """Calculate parallel processing efficiency"""
        
        if not results or total_time == 0:
            return 0.0
        
        # Estimate sequential processing time
        avg_task_time = 0.1  # Estimated average task time
        sequential_time = len(results) * avg_task_time
        
        # Calculate efficiency
        efficiency = min(1.0, sequential_time / total_time)
        
        return efficiency

    def get_cache_hit_rate(self) -> float:
        """Get current cache hit rate"""
        total_requests = self.cache_hit_count + self.cache_miss_count
        return self.cache_hit_count / total_requests if total_requests > 0 else 0.0

# Export the class
__all__ = ['AnalysisOptimizationService', 'OptimizationConfig', 'TaskGroup']
