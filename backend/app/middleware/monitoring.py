# backend/app/middleware/monitoring.py

import time
import logging
from functools import wraps
from typing import Any, Callable
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import query

logger = logging.getLogger(__name__)

def performance_monitor(func: Callable) -> Callable:
    """Decorator for performance monitoring with GCP Cloud Monitoring"""
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        function_name = f"{func.__module__}.{func.__name__}"
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record success metrics
            await _record_metric(
                metric_type="custom.googleapis.com/validatus/function/execution_time",
                value=execution_time,
                labels={
                    "function_name": function_name,
                    "status": "success"
                }
            )
            
            logger.info(f"✅ {function_name} completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record error metrics
            await _record_metric(
                metric_type="custom.googleapis.com/validatus/function/execution_time",
                value=execution_time,
                labels={
                    "function_name": function_name,
                    "status": "error"
                }
            )
            
            await _record_metric(
                metric_type="custom.googleapis.com/validatus/function/error_count",
                value=1,
                labels={
                    "function_name": function_name,
                    "error_type": type(e).__name__
                }
            )
            
            logger.error(f"❌ {function_name} failed after {execution_time:.2f}s: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        function_name = f"{func.__module__}.{func.__name__}"
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record success metrics (sync version)
            logger.info(f"✅ {function_name} completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {function_name} failed after {execution_time:.2f}s: {e}")
            raise
    
    # Return appropriate wrapper based on function type
    if func.__name__.startswith('_') or func.__name__.endswith('_async'):
        return async_wrapper
    else:
        return sync_wrapper

async def _record_metric(metric_type: str, value: float, labels: dict) -> None:
    """Record custom metric to Cloud Monitoring"""
    try:
        client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/validatus-prod"  # This should come from config
        
        series = monitoring_v3.TimeSeries()
        series.metric.type = metric_type
        
        # Add labels
        for key, val in labels.items():
            series.metric.labels[key] = str(val)
        
        # Set resource
        series.resource.type = "global"
        
        # Set data point
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        
        interval = monitoring_v3.TimeInterval(
            {"end_time": {"seconds": seconds, "nanos": nanos}}
        )
        
        point = monitoring_v3.Point(
            {"interval": interval, "value": {"double_value": value}}
        )
        series.points = [point]
        
        # Write the time series
        client.create_time_series(name=project_name, time_series=[series])
        
    except Exception as e:
        logger.error(f"Failed to record metric {metric_type}: {e}")

# Export for use in other modules
__all__ = ['performance_monitor']
