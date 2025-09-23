# backend/app/core/performance_optimizer.py

import asyncio
import logging
import time
import psutil
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from functools import wraps
import gc
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    throughput: float
    error_count: int
    cache_hit_rate: float
    timestamp: str

@dataclass
class OptimizationConfig:
    """Performance optimization configuration"""
    max_memory_mb: int = 1024
    max_cpu_percent: float = 80.0
    cache_size: int = 1000
    batch_size: int = 100
    max_concurrent_tasks: int = 10
    enable_gc: bool = True
    gc_threshold: float = 0.8

class PerformanceOptimizer:
    """Advanced performance optimization utilities"""
    
    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        self.metrics_history: List[PerformanceMetrics] = []
        self.cache: Dict[str, Any] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_tasks)
        
        # Performance monitoring
        self._start_time = time.time()
        self._task_count = 0
        self._error_count = 0
        
    def optimize_function(self, 
                         cache_key: Optional[str] = None,
                         batch_processing: bool = False,
                         memory_monitoring: bool = True):
        """Decorator for function performance optimization"""
        
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_optimized_function(
                    func, args, kwargs, cache_key, batch_processing, memory_monitoring
                )
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._execute_sync_optimized_function(
                    func, args, kwargs, cache_key, batch_processing, memory_monitoring
                )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    async def _execute_optimized_function(self, 
                                        func: Callable,
                                        args: tuple,
                                        kwargs: dict,
                                        cache_key: Optional[str],
                                        batch_processing: bool,
                                        memory_monitoring: bool):
        """Execute async function with optimization"""
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            # Check cache first
            if cache_key and cache_key in self.cache:
                self.cache_hits += 1
                logger.debug(f"Cache hit for key: {cache_key}")
                return self.cache[cache_key]
            
            self.cache_misses += 1
            
            # Monitor memory before execution
            if memory_monitoring:
                await self._monitor_memory_usage()
            
            # Execute function
            if batch_processing and len(args) > 0 and isinstance(args[0], list):
                result = await self._execute_batch_processing(func, args, kwargs)
            else:
                result = await func(*args, **kwargs)
            
            # Cache result if cache key provided
            if cache_key:
                self._update_cache(cache_key, result)
            
            # Record metrics
            await self._record_metrics(start_time, start_memory, success=True)
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Function execution failed: {e}")
            await self._record_metrics(start_time, start_memory, success=False)
            raise
    
    def _execute_sync_optimized_function(self, 
                                       func: Callable,
                                       args: tuple,
                                       kwargs: dict,
                                       cache_key: Optional[str],
                                       batch_processing: bool,
                                       memory_monitoring: bool):
        """Execute sync function with optimization"""
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            # Check cache first
            if cache_key and cache_key in self.cache:
                self.cache_hits += 1
                logger.debug(f"Cache hit for key: {cache_key}")
                return self.cache[cache_key]
            
            self.cache_misses += 1
            
            # Monitor memory before execution
            if memory_monitoring:
                self._monitor_memory_usage_sync()
            
            # Execute function
            if batch_processing and len(args) > 0 and isinstance(args[0], list):
                result = self._execute_batch_processing_sync(func, args, kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache result if cache key provided
            if cache_key:
                self._update_cache(cache_key, result)
            
            # Record metrics
            self._record_metrics_sync(start_time, start_memory, success=True)
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Function execution failed: {e}")
            self._record_metrics_sync(start_time, start_memory, success=False)
            raise
    
    async def _execute_batch_processing(self, func: Callable, args: tuple, kwargs: dict):
        """Execute function with batch processing optimization"""
        
        data_list = args[0]
        batch_size = self.config.batch_size
        
        results = []
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            batch_args = (batch,) + args[1:]
            
            # Execute batch
            batch_result = await func(*batch_args, **kwargs)
            results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
            
            # Monitor memory between batches
            await self._monitor_memory_usage()
            
            # Optional: Add small delay to prevent overwhelming
            if i + batch_size < len(data_list):
                await asyncio.sleep(0.01)
        
        return results
    
    def _execute_batch_processing_sync(self, func: Callable, args: tuple, kwargs: dict):
        """Execute sync function with batch processing optimization"""
        
        data_list = args[0]
        batch_size = self.config.batch_size
        
        results = []
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            batch_args = (batch,) + args[1:]
            
            # Execute batch
            batch_result = func(*batch_args, **kwargs)
            results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
            
            # Monitor memory between batches
            self._monitor_memory_usage_sync()
            
            # Optional: Add small delay to prevent overwhelming
            if i + batch_size < len(data_list):
                time.sleep(0.01)
        
        return results
    
    async def _monitor_memory_usage(self):
        """Monitor memory usage and trigger garbage collection if needed"""
        
        current_memory = self._get_memory_usage()
        
        if current_memory > self.config.max_memory_mb:
            logger.warning(f"Memory usage ({current_memory:.2f} MB) exceeds threshold ({self.config.max_memory_mb} MB)")
            
            if self.config.enable_gc:
                gc.collect()
                logger.info("Garbage collection triggered")
        
        # Check cache size and cleanup if needed
        if len(self.cache) > self.config.cache_size:
            await self._cleanup_cache()
    
    def _monitor_memory_usage_sync(self):
        """Monitor memory usage synchronously"""
        
        current_memory = self._get_memory_usage()
        
        if current_memory > self.config.max_memory_mb:
            logger.warning(f"Memory usage ({current_memory:.2f} MB) exceeds threshold ({self.config.max_memory_mb} MB)")
            
            if self.config.enable_gc:
                gc.collect()
                logger.info("Garbage collection triggered")
        
        # Check cache size and cleanup if needed
        if len(self.cache) > self.config.cache_size:
            self._cleanup_cache_sync()
    
    async def _cleanup_cache(self):
        """Clean up cache by removing least recently used items"""
        
        # Simple cleanup: remove oldest 25% of cache
        items_to_remove = len(self.cache) // 4
        cache_items = list(self.cache.items())
        
        for i in range(items_to_remove):
            key, _ = cache_items[i]
            del self.cache[key]
        
        logger.info(f"Cache cleanup: removed {items_to_remove} items")
    
    def _cleanup_cache_sync(self):
        """Clean up cache synchronously"""
        
        # Simple cleanup: remove oldest 25% of cache
        items_to_remove = len(self.cache) // 4
        cache_items = list(self.cache.items())
        
        for i in range(items_to_remove):
            key, _ = cache_items[i]
            del self.cache[key]
        
        logger.info(f"Cache cleanup: removed {items_to_remove} items")
    
    def _update_cache(self, key: str, value: Any):
        """Update cache with new value"""
        
        self.cache[key] = value
        
        # Maintain cache size limit
        if len(self.cache) > self.config.cache_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    async def _record_metrics(self, start_time: float, start_memory: float, success: bool):
        """Record performance metrics"""
        
        execution_time = time.time() - start_time
        end_memory = self._get_memory_usage()
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # Calculate throughput
        self._task_count += 1
        total_time = time.time() - self._start_time
        throughput = self._task_count / total_time if total_time > 0 else 0
        
        # Calculate cache hit rate
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / total_cache_requests if total_cache_requests > 0 else 0
        
        metrics = PerformanceMetrics(
            execution_time=execution_time,
            memory_usage=end_memory,
            cpu_usage=cpu_usage,
            throughput=throughput,
            error_count=self._error_count,
            cache_hit_rate=cache_hit_rate,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.metrics_history.append(metrics)
        
        # Keep only last 100 metrics
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        logger.debug(f"Performance metrics recorded: {execution_time:.3f}s, {end_memory:.2f}MB, {cpu_usage:.1f}% CPU")
    
    def _record_metrics_sync(self, start_time: float, start_memory: float, success: bool):
        """Record performance metrics synchronously"""
        
        execution_time = time.time() - start_time
        end_memory = self._get_memory_usage()
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # Calculate throughput
        self._task_count += 1
        total_time = time.time() - self._start_time
        throughput = self._task_count / total_time if total_time > 0 else 0
        
        # Calculate cache hit rate
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / total_cache_requests if total_cache_requests > 0 else 0
        
        metrics = PerformanceMetrics(
            execution_time=execution_time,
            memory_usage=end_memory,
            cpu_usage=cpu_usage,
            throughput=throughput,
            error_count=self._error_count,
            cache_hit_rate=cache_hit_rate,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.metrics_history.append(metrics)
        
        # Keep only last 100 metrics
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        logger.debug(f"Performance metrics recorded: {execution_time:.3f}s, {end_memory:.2f}MB, {cpu_usage:.1f}% CPU")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 executions
        
        avg_execution_time = sum(m.execution_time for m in recent_metrics) / len(recent_metrics)
        avg_memory_usage = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_cpu_usage = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_throughput = sum(m.throughput for m in recent_metrics) / len(recent_metrics)
        avg_cache_hit_rate = sum(m.cache_hit_rate for m in recent_metrics) / len(recent_metrics)
        
        return {
            "performance_summary": {
                "average_execution_time": round(avg_execution_time, 3),
                "average_memory_usage_mb": round(avg_memory_usage, 2),
                "average_cpu_usage_percent": round(avg_cpu_usage, 1),
                "average_throughput": round(avg_throughput, 2),
                "average_cache_hit_rate": round(avg_cache_hit_rate, 3),
                "total_tasks_executed": self._task_count,
                "total_errors": self._error_count,
                "cache_size": len(self.cache),
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses
            },
            "system_health": {
                "memory_usage_mb": self._get_memory_usage(),
                "cpu_usage_percent": psutil.cpu_percent(interval=1),
                "uptime_seconds": time.time() - self._start_time
            },
            "recommendations": self._generate_recommendations(recent_metrics)
        }
    
    def _generate_recommendations(self, metrics: List[PerformanceMetrics]) -> List[str]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        if metrics:
            avg_memory = sum(m.memory_usage for m in metrics) / len(metrics)
            avg_cpu = sum(m.cpu_usage for m in metrics) / len(metrics)
            avg_cache_hit = sum(m.cache_hit_rate for m in metrics) / len(metrics)
            
            if avg_memory > self.config.max_memory_mb * 0.8:
                recommendations.append("Consider reducing batch size or implementing more aggressive memory management")
            
            if avg_cpu > self.config.max_cpu_percent:
                recommendations.append("CPU usage is high - consider reducing concurrency or optimizing algorithms")
            
            if avg_cache_hit < 0.3:
                recommendations.append("Low cache hit rate - consider improving cache key strategy or increasing cache size")
            
            if self._error_count > len(metrics) * 0.1:
                recommendations.append("High error rate detected - review error handling and input validation")
        
        if not recommendations:
            recommendations.append("Performance metrics look good - no immediate optimizations needed")
        
        return recommendations
    
    def clear_cache(self):
        """Clear all cached data"""
        
        cache_size = len(self.cache)
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info(f"Cache cleared: {cache_size} items removed")
    
    def reset_metrics(self):
        """Reset performance metrics"""
        
        self.metrics_history.clear()
        self._start_time = time.time()
        self._task_count = 0
        self._error_count = 0
        
        logger.info("Performance metrics reset")

# Global instance for easy access
performance_optimizer = PerformanceOptimizer()

# Decorator for easy use
def optimize_performance(cache_key: Optional[str] = None, 
                        batch_processing: bool = False,
                        memory_monitoring: bool = True):
    """Convenience decorator for performance optimization"""
    return performance_optimizer.optimize_function(
        cache_key=cache_key,
        batch_processing=batch_processing,
        memory_monitoring=memory_monitoring
    )

# Export the classes and functions
__all__ = [
    'PerformanceOptimizer', 
    'PerformanceMetrics', 
    'OptimizationConfig',
    'performance_optimizer',
    'optimize_performance'
]
