# backend/app/core/error_recovery.py

import asyncio
import logging
import time
import traceback
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecoveryStrategy(Enum):
    """Error recovery strategies"""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FAIL_FAST = "fail_fast"

@dataclass
class ErrorContext:
    """Context information for error recovery"""
    error_type: str
    error_message: str
    function_name: str
    timestamp: str
    severity: ErrorSeverity
    retry_count: int = 0
    max_retries: int = 3
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    context_data: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""

@dataclass
class RecoveryResult:
    """Result of error recovery attempt"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    recovery_strategy_used: Optional[RecoveryStrategy] = None
    retry_count: int = 0
    execution_time: float = 0.0
    fallback_used: bool = False

@dataclass
class CircuitBreakerState:
    """Circuit breaker state management"""
    failure_count: int = 0
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    last_failure_time: Optional[float] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

class ErrorRecoveryManager:
    """Advanced error recovery and management system"""
    
    def __init__(self):
        self.error_history: List[ErrorContext] = []
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.fallback_functions: Dict[str, Callable] = {}
        self.error_patterns: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default recovery strategies
        self._initialize_default_strategies()
        
    def _initialize_default_strategies(self):
        """Initialize default recovery strategies"""
        
        self.recovery_strategies = {
            "retry": self._retry_strategy,
            "fallback": self._fallback_strategy,
            "circuit_breaker": self._circuit_breaker_strategy,
            "graceful_degradation": self._graceful_degradation_strategy,
            "fail_fast": self._fail_fast_strategy
        }
    
    async def execute_with_recovery(self, 
                                  func: Callable,
                                  *args,
                                  error_context: Optional[Dict[str, Any]] = None,
                                  recovery_strategy: RecoveryStrategy = RecoveryStrategy.RETRY,
                                  max_retries: int = 3,
                                  fallback_func: Optional[Callable] = None,
                                  circuit_breaker_key: Optional[str] = None,
                                  **kwargs) -> RecoveryResult:
        """Execute function with comprehensive error recovery"""
        
        start_time = time.time()
        error_context = error_context or {}
        
        try:
            # Check circuit breaker if specified
            if circuit_breaker_key and not self._is_circuit_breaker_open(circuit_breaker_key):
                return await self._execute_with_circuit_breaker(
                    func, args, kwargs, circuit_breaker_key, error_context
                )
            
            # Execute function directly
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Record successful execution
            execution_time = time.time() - start_time
            
            return RecoveryResult(
                success=True,
                result=result,
                recovery_strategy_used=None,
                retry_count=0,
                execution_time=execution_time,
                fallback_used=False
            )
            
        except Exception as e:
            # Create error context
            error_ctx = ErrorContext(
                error_type=type(e).__name__,
                error_message=str(e),
                function_name=func.__name__,
                timestamp=datetime.now(timezone.utc).isoformat(),
                severity=self._determine_severity(e),
                max_retries=max_retries,
                recovery_strategy=recovery_strategy,
                context_data=error_context,
                stack_trace=traceback.format_exc()
            )
            
            # Record error
            self.error_history.append(error_ctx)
            
            # Apply recovery strategy
            recovery_result = await self._apply_recovery_strategy(
                error_ctx, func, args, kwargs, fallback_func, circuit_breaker_key
            )
            
            recovery_result.execution_time = time.time() - start_time
            
            return recovery_result
    
    async def _execute_with_circuit_breaker(self, 
                                          func: Callable,
                                          args: tuple,
                                          kwargs: dict,
                                          circuit_breaker_key: str,
                                          error_context: Dict[str, Any]) -> RecoveryResult:
        """Execute function with circuit breaker protection"""
        
        circuit_breaker = self.circuit_breakers.get(circuit_breaker_key)
        
        if not circuit_breaker:
            circuit_breaker = CircuitBreakerState()
            self.circuit_breakers[circuit_breaker_key] = circuit_breaker
        
        # Check if circuit breaker is open
        if circuit_breaker.state == "OPEN":
            if time.time() - circuit_breaker.last_failure_time > circuit_breaker.recovery_timeout:
                circuit_breaker.state = "HALF_OPEN"
                logger.info(f"Circuit breaker {circuit_breaker_key} moved to HALF_OPEN state")
            else:
                return RecoveryResult(
                    success=False,
                    error=f"Circuit breaker {circuit_breaker_key} is OPEN",
                    recovery_strategy_used=RecoveryStrategy.CIRCUIT_BREAKER
                )
        
        try:
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset circuit breaker
            if circuit_breaker.state == "HALF_OPEN":
                circuit_breaker.state = "CLOSED"
                circuit_breaker.failure_count = 0
                logger.info(f"Circuit breaker {circuit_breaker_key} moved to CLOSED state")
            
            return RecoveryResult(
                success=True,
                result=result,
                recovery_strategy_used=RecoveryStrategy.CIRCUIT_BREAKER
            )
            
        except Exception as e:
            # Failure - update circuit breaker
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = time.time()
            
            if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
                circuit_breaker.state = "OPEN"
                logger.warning(f"Circuit breaker {circuit_breaker_key} moved to OPEN state")
            
            raise e
    
    async def _apply_recovery_strategy(self, 
                                     error_context: ErrorContext,
                                     func: Callable,
                                     args: tuple,
                                     kwargs: dict,
                                     fallback_func: Optional[Callable],
                                     circuit_breaker_key: Optional[str]) -> RecoveryResult:
        """Apply the specified recovery strategy"""
        
        strategy_func = self.recovery_strategies.get(error_context.recovery_strategy.value)
        
        if not strategy_func:
            logger.error(f"Unknown recovery strategy: {error_context.recovery_strategy}")
            return RecoveryResult(
                success=False,
                error=f"Unknown recovery strategy: {error_context.recovery_strategy}",
                recovery_strategy_used=error_context.recovery_strategy
            )
        
        return await strategy_func(error_context, func, args, kwargs, fallback_func, circuit_breaker_key)
    
    async def _retry_strategy(self, 
                            error_context: ErrorContext,
                            func: Callable,
                            args: tuple,
                            kwargs: dict,
                            fallback_func: Optional[Callable],
                            circuit_breaker_key: Optional[str]) -> RecoveryResult:
        """Retry strategy with exponential backoff"""
        
        for attempt in range(error_context.max_retries):
            try:
                # Exponential backoff
                if attempt > 0:
                    delay = min(2 ** attempt, 60)  # Max 60 seconds
                    await asyncio.sleep(delay)
                
                # Update retry count
                error_context.retry_count = attempt + 1
                
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                logger.info(f"Function {func.__name__} succeeded on retry {attempt + 1}")
                
                return RecoveryResult(
                    success=True,
                    result=result,
                    recovery_strategy_used=RecoveryStrategy.RETRY,
                    retry_count=attempt + 1
                )
                
            except Exception as e:
                logger.warning(f"Retry {attempt + 1} failed for {func.__name__}: {e}")
                
                if attempt == error_context.max_retries - 1:
                    # Final attempt failed
                    if fallback_func:
                        return await self._fallback_strategy(
                            error_context, func, args, kwargs, fallback_func, circuit_breaker_key
                        )
                    else:
                        return RecoveryResult(
                            success=False,
                            error=str(e),
                            recovery_strategy_used=RecoveryStrategy.RETRY,
                            retry_count=attempt + 1
                        )
        
        return RecoveryResult(
            success=False,
            error="Max retries exceeded",
            recovery_strategy_used=RecoveryStrategy.RETRY,
            retry_count=error_context.max_retries
        )
    
    async def _fallback_strategy(self, 
                               error_context: ErrorContext,
                               func: Callable,
                               args: tuple,
                               kwargs: dict,
                               fallback_func: Optional[Callable],
                               circuit_breaker_key: Optional[str]) -> RecoveryResult:
        """Fallback strategy - execute alternative function"""
        
        if not fallback_func:
            return RecoveryResult(
                success=False,
                error="No fallback function provided",
                recovery_strategy_used=RecoveryStrategy.FALLBACK
            )
        
        try:
            logger.info(f"Executing fallback function for {func.__name__}")
            
            # Execute fallback function
            if asyncio.iscoroutinefunction(fallback_func):
                result = await fallback_func(*args, **kwargs)
            else:
                result = fallback_func(*args, **kwargs)
            
            return RecoveryResult(
                success=True,
                result=result,
                recovery_strategy_used=RecoveryStrategy.FALLBACK,
                fallback_used=True
            )
            
        except Exception as e:
            logger.error(f"Fallback function failed: {e}")
            return RecoveryResult(
                success=False,
                error=f"Fallback function failed: {str(e)}",
                recovery_strategy_used=RecoveryStrategy.FALLBACK,
                fallback_used=True
            )
    
    async def _circuit_breaker_strategy(self, 
                                      error_context: ErrorContext,
                                      func: Callable,
                                      args: tuple,
                                      kwargs: dict,
                                      fallback_func: Optional[Callable],
                                      circuit_breaker_key: Optional[str]) -> RecoveryResult:
        """Circuit breaker strategy"""
        
        if not circuit_breaker_key:
            return RecoveryResult(
                success=False,
                error="Circuit breaker key required",
                recovery_strategy_used=RecoveryStrategy.CIRCUIT_BREAKER
            )
        
        # Update circuit breaker state
        circuit_breaker = self.circuit_breakers.get(circuit_breaker_key)
        if not circuit_breaker:
            circuit_breaker = CircuitBreakerState()
            self.circuit_breakers[circuit_breaker_key] = circuit_breaker
        
        circuit_breaker.failure_count += 1
        circuit_breaker.last_failure_time = time.time()
        
        if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
            circuit_breaker.state = "OPEN"
            logger.warning(f"Circuit breaker {circuit_breaker_key} opened")
        
        # Try fallback if available
        if fallback_func:
            return await self._fallback_strategy(
                error_context, func, args, kwargs, fallback_func, circuit_breaker_key
            )
        
        return RecoveryResult(
            success=False,
            error=f"Circuit breaker opened for {circuit_breaker_key}",
            recovery_strategy_used=RecoveryStrategy.CIRCUIT_BREAKER
        )
    
    async def _graceful_degradation_strategy(self, 
                                           error_context: ErrorContext,
                                           func: Callable,
                                           args: tuple,
                                           kwargs: dict,
                                           fallback_func: Optional[Callable],
                                           circuit_breaker_key: Optional[str]) -> RecoveryResult:
        """Graceful degradation strategy - return partial results"""
        
        try:
            # Try to get partial results or default values
            if hasattr(func, '__name__'):
                if 'analysis' in func.__name__.lower():
                    # Return empty analysis results
                    result = {
                        "status": "degraded",
                        "message": "Analysis completed with reduced functionality",
                        "results": [],
                        "error": str(error_context.error_message)
                    }
                elif 'search' in func.__name__.lower():
                    # Return empty search results
                    result = {
                        "status": "degraded",
                        "message": "Search completed with reduced functionality",
                        "results": [],
                        "total": 0
                    }
                else:
                    # Generic degraded response
                    result = {
                        "status": "degraded",
                        "message": "Function completed with reduced functionality",
                        "error": str(error_context.error_message)
                    }
            else:
                result = {
                    "status": "degraded",
                    "message": "Operation completed with reduced functionality"
                }
            
            logger.info(f"Graceful degradation applied for {func.__name__}")
            
            return RecoveryResult(
                success=True,
                result=result,
                recovery_strategy_used=RecoveryStrategy.GRACEFUL_DEGRADATION
            )
            
        except Exception as e:
            logger.error(f"Graceful degradation failed: {e}")
            return RecoveryResult(
                success=False,
                error=f"Graceful degradation failed: {str(e)}",
                recovery_strategy_used=RecoveryStrategy.GRACEFUL_DEGRADATION
            )
    
    async def _fail_fast_strategy(self, 
                                error_context: ErrorContext,
                                func: Callable,
                                args: tuple,
                                kwargs: dict,
                                fallback_func: Optional[Callable],
                                circuit_breaker_key: Optional[str]) -> RecoveryResult:
        """Fail fast strategy - immediately return error"""
        
        logger.error(f"Fail fast strategy applied for {func.__name__}: {error_context.error_message}")
        
        return RecoveryResult(
            success=False,
            error=error_context.error_message,
            recovery_strategy_used=RecoveryStrategy.FAIL_FAST
        )
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on error type"""
        
        error_type = type(error).__name__.lower()
        
        if 'critical' in error_type or 'fatal' in error_type:
            return ErrorSeverity.CRITICAL
        elif 'timeout' in error_type or 'connection' in error_type:
            return ErrorSeverity.HIGH
        elif 'validation' in error_type or 'argument' in error_type:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _is_circuit_breaker_open(self, circuit_breaker_key: str) -> bool:
        """Check if circuit breaker is open"""
        
        circuit_breaker = self.circuit_breakers.get(circuit_breaker_key)
        
        if not circuit_breaker:
            return False
        
        if circuit_breaker.state == "OPEN":
            # Check if recovery timeout has passed
            if time.time() - circuit_breaker.last_failure_time > circuit_breaker.recovery_timeout:
                circuit_breaker.state = "HALF_OPEN"
                return False
            return True
        
        return False
    
    def register_fallback_function(self, function_name: str, fallback_func: Callable):
        """Register a fallback function for a specific function"""
        
        self.fallback_functions[function_name] = fallback_func
        logger.info(f"Registered fallback function for {function_name}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        
        if not self.error_history:
            return {"error": "No error history available"}
        
        # Group errors by type
        error_types = {}
        error_severities = {}
        function_errors = {}
        
        for error in self.error_history:
            # Count by error type
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            
            # Count by severity
            error_severities[error.severity.value] = error_severities.get(error.severity.value, 0) + 1
            
            # Count by function
            function_errors[error.function_name] = function_errors.get(error.function_name, 0) + 1
        
        # Calculate recovery success rate
        recovery_successes = sum(1 for error in self.error_history if error.retry_count > 0 and error.retry_count < error.max_retries)
        total_retries = sum(1 for error in self.error_history if error.retry_count > 0)
        recovery_success_rate = recovery_successes / total_retries if total_retries > 0 else 0
        
        return {
            "error_statistics": {
                "total_errors": len(self.error_history),
                "error_types": error_types,
                "error_severities": error_severities,
                "function_errors": function_errors,
                "recovery_success_rate": round(recovery_success_rate, 3)
            },
            "circuit_breakers": {
                key: {
                    "state": breaker.state,
                    "failure_count": breaker.failure_count,
                    "failure_threshold": breaker.failure_threshold
                }
                for key, breaker in self.circuit_breakers.items()
            },
            "registered_fallbacks": list(self.fallback_functions.keys()),
            "recommendations": self._generate_error_recommendations()
        }
    
    def _generate_error_recommendations(self) -> List[str]:
        """Generate recommendations based on error patterns"""
        
        recommendations = []
        
        if not self.error_history:
            return ["No errors recorded - system is stable"]
        
        # Analyze recent errors (last 24 hours)
        recent_errors = [
            error for error in self.error_history
            if (datetime.now(timezone.utc) - datetime.fromisoformat(error.timestamp)).total_seconds() < 86400
        ]
        
        if len(recent_errors) > 10:
            recommendations.append("High error frequency detected - review system stability")
        
        # Check for specific error patterns
        timeout_errors = sum(1 for error in recent_errors if 'timeout' in error.error_type.lower())
        if timeout_errors > len(recent_errors) * 0.3:
            recommendations.append("High timeout error rate - consider increasing timeout values or optimizing performance")
        
        connection_errors = sum(1 for error in recent_errors if 'connection' in error.error_type.lower())
        if connection_errors > len(recent_errors) * 0.2:
            recommendations.append("Connection errors detected - review network configuration and retry policies")
        
        # Check circuit breaker states
        open_breakers = sum(1 for breaker in self.circuit_breakers.values() if breaker.state == "OPEN")
        if open_breakers > 0:
            recommendations.append(f"{open_breakers} circuit breaker(s) are open - review dependent services")
        
        if not recommendations:
            recommendations.append("Error patterns look normal - no immediate action required")
        
        return recommendations
    
    def clear_error_history(self):
        """Clear error history"""
        
        history_size = len(self.error_history)
        self.error_history.clear()
        logger.info(f"Error history cleared: {history_size} errors removed")
    
    def reset_circuit_breakers(self):
        """Reset all circuit breakers"""
        
        for key, breaker in self.circuit_breakers.items():
            breaker.state = "CLOSED"
            breaker.failure_count = 0
            breaker.last_failure_time = None
        
        logger.info("All circuit breakers reset")

# Global instance for easy access
error_recovery_manager = ErrorRecoveryManager()

# Decorator for easy use
def with_error_recovery(recovery_strategy: RecoveryStrategy = RecoveryStrategy.RETRY,
                       max_retries: int = 3,
                       fallback_func: Optional[Callable] = None,
                       circuit_breaker_key: Optional[str] = None):
    """Convenience decorator for error recovery"""
    
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await error_recovery_manager.execute_with_recovery(
                func, *args,
                recovery_strategy=recovery_strategy,
                max_retries=max_retries,
                fallback_func=fallback_func,
                circuit_breaker_key=circuit_breaker_key,
                **kwargs
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to run the async recovery in an event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    error_recovery_manager.execute_with_recovery(
                        func, *args,
                        recovery_strategy=recovery_strategy,
                        max_retries=max_retries,
                        fallback_func=fallback_func,
                        circuit_breaker_key=circuit_breaker_key,
                        **kwargs
                    )
                )
                return result
            finally:
                loop.close()
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Export the classes and functions
__all__ = [
    'ErrorRecoveryManager',
    'ErrorContext',
    'RecoveryResult',
    'CircuitBreakerState',
    'ErrorSeverity',
    'RecoveryStrategy',
    'error_recovery_manager',
    'with_error_recovery'
]
