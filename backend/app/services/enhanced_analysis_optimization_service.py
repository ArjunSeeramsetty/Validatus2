import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from .analysis_optimization_service import AnalysisOptimizationService
from .enhanced_orchestration.advanced_orchestrator import AdvancedOrchestrator, OperationPriority
from .enhanced_orchestration.multi_level_cache_manager import MultiLevelCacheManager, CacheStrategy
from ..core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

class EnhancedAnalysisOptimizationService(AnalysisOptimizationService):
    """
    Enhanced Analysis Optimization Service integrating Phase E capabilities
    Extends existing service with circuit breakers and multi-level caching
    """
    
    def __init__(self):
        super().__init__()  # Initialize parent AnalysisOptimizationService
        
        # Initialize Phase E components only if enabled
        self.orchestrator: Optional[AdvancedOrchestrator] = None
        self.cache_manager: Optional[MultiLevelCacheManager] = None
        
        if FeatureFlags.ADVANCED_ORCHESTRATION_ENABLED:
            self.orchestrator = AdvancedOrchestrator(project_id=self.project_id)
        
        if FeatureFlags.MULTI_LEVEL_CACHE_ENABLED:
            self.cache_manager = MultiLevelCacheManager(project_id=self.project_id)
        
        logger.info("✅ Enhanced Analysis Optimization Service initialized")
    
    async def initialize_enhanced_components(self):
        """Initialize enhanced components"""
        tasks = []
        
        if self.orchestrator:
            tasks.append(self.orchestrator.initialize())
        
        if self.cache_manager:
            tasks.append(self.cache_manager.initialize())
        
        if tasks:
            await asyncio.gather(*tasks)
            logger.info("Enhanced optimization components initialized")
    
    async def optimize_strategic_analysis_enhanced(self, 
                                                 session_id: str, 
                                                 analysis_config: Dict[str, Any],
                                                 priority: OperationPriority = OperationPriority.HIGH) -> Dict[str, Any]:
        """
        Enhanced strategic analysis optimization with circuit breaker protection
        """
        try:
            # Check cache first if enabled
            cache_key = f"analysis_optimization:{session_id}"
            
            if self.cache_manager:
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for analysis optimization: {session_id}")
                    return cached_result
            
            # Execute with circuit breaker protection if available
            if self.orchestrator and FeatureFlags.CIRCUIT_BREAKER_ENABLED:
                result = await self.orchestrator.execute_with_circuit_breaker(
                    operation_name='strategic_analysis_optimization',
                    operation_func=super().optimize_strategic_analysis,
                    session_id=session_id,
                    analysis_config=analysis_config,
                    pool_name='analysis_execution',
                    priority=priority
                )
            else:
                # Fallback to parent method
                result = await super().optimize_strategic_analysis(session_id, analysis_config)
            
            # Cache the result if enabled
            if self.cache_manager and result.get('success', False):
                await self.cache_manager.set(
                    cache_key, 
                    result, 
                    ttl_seconds=1800,  # 30 minutes
                    strategy=CacheStrategy.WRITE_THROUGH
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced analysis optimization failed: {e}")
            
            # Fallback to base implementation
            return await super().optimize_strategic_analysis(session_id, analysis_config)
    
    async def optimize_parallel_processing_enhanced(self, 
                                                  tasks: List[Dict[str, Any]],
                                                  priority: OperationPriority = OperationPriority.MEDIUM) -> Dict[str, Any]:
        """Enhanced parallel processing with bulkhead isolation"""
        
        try:
            if self.orchestrator and FeatureFlags.CIRCUIT_BREAKER_ENABLED:
                return await self.orchestrator.execute_with_circuit_breaker(
                    operation_name='parallel_processing_optimization',
                    operation_func=super().optimize_parallel_processing,
                    tasks=tasks,
                    pool_name='content_processing',
                    priority=priority
                )
            else:
                return await super().optimize_parallel_processing(tasks)
                
        except Exception as e:
            logger.error(f"Enhanced parallel processing failed: {e}")
            return await super().optimize_parallel_processing(tasks)
    
    async def optimize_knowledge_loading_enhanced(self, 
                                                topic: str,
                                                priority: OperationPriority = OperationPriority.MEDIUM) -> Dict[str, Any]:
        """Enhanced knowledge loading with caching and circuit breaker protection"""
        
        try:
            # Check cache first
            cache_key = f"knowledge_loading:{topic}"
            
            if self.cache_manager:
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for knowledge loading: {topic}")
                    return cached_result
            
            # Execute with circuit breaker protection
            if self.orchestrator and FeatureFlags.CIRCUIT_BREAKER_ENABLED:
                result = await self.orchestrator.execute_with_circuit_breaker(
                    operation_name='knowledge_loading_optimization',
                    operation_func=super().optimize_knowledge_loading,
                    topic=topic,
                    pool_name='knowledge_loading',
                    priority=priority
                )
            else:
                result = await super().optimize_knowledge_loading(topic)
            
            # Cache the result if successful
            if self.cache_manager and result.get('success', False):
                await self.cache_manager.set(
                    cache_key,
                    result,
                    ttl_seconds=3600,  # 1 hour for knowledge data
                    strategy=CacheStrategy.WRITE_THROUGH
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced knowledge loading failed: {e}")
            return await super().optimize_knowledge_loading(topic)
    
    async def optimize_vector_operations_enhanced(self, 
                                                vector_operations: List[Dict[str, Any]],
                                                priority: OperationPriority = OperationPriority.MEDIUM) -> Dict[str, Any]:
        """Enhanced vector operations with circuit breaker protection"""
        
        try:
            if self.orchestrator and FeatureFlags.CIRCUIT_BREAKER_ENABLED:
                return await self.orchestrator.execute_with_circuit_breaker(
                    operation_name='vector_operations_optimization',
                    operation_func=super().optimize_vector_operations,
                    vector_operations=vector_operations,
                    pool_name='vector_operations',
                    priority=priority
                )
            else:
                return await super().optimize_vector_operations(vector_operations)
                
        except Exception as e:
            logger.error(f"Enhanced vector operations failed: {e}")
            return await super().optimize_vector_operations(vector_operations)
    
    async def get_enhanced_optimization_metrics(self) -> Dict[str, Any]:
        """Get comprehensive optimization metrics including Phase E components"""
        
        # Get base metrics
        base_metrics = await super().get_optimization_metrics()
        
        enhanced_metrics = {
            **base_metrics,
            'enhancement_enabled': FeatureFlags.is_phase_e_enabled(),
            'phase_e_components': {
                'orchestrator': self.orchestrator is not None,
                'cache_manager': self.cache_manager is not None
            }
        }
        
        # Add orchestrator metrics if available
        if self.orchestrator:
            try:
                orchestrator_health = await self.orchestrator.get_orchestrator_health()
                enhanced_metrics['orchestrator'] = orchestrator_health
            except Exception as e:
                enhanced_metrics['orchestrator'] = {'error': str(e)}
        
        # Add cache metrics if available
        if self.cache_manager:
            try:
                cache_stats = await self.cache_manager.get_cache_stats()
                enhanced_metrics['cache'] = cache_stats
            except Exception as e:
                enhanced_metrics['cache'] = {'error': str(e)}
        
        return enhanced_metrics
    
    async def get_cache_performance_analysis(self) -> Dict[str, Any]:
        """Get detailed cache performance analysis"""
        
        if not self.cache_manager:
            return {'error': 'Cache manager not available'}
        
        try:
            cache_stats = await self.cache_manager.get_cache_stats()
            
            # Calculate performance insights
            analysis = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'cache_stats': cache_stats,
                'performance_insights': {},
                'recommendations': []
            }
            
            overall_hit_ratio = cache_stats.get('overall', {}).get('overall_hit_ratio', 0)
            
            # Performance insights
            if overall_hit_ratio > 0.8:
                analysis['performance_insights']['cache_efficiency'] = 'excellent'
            elif overall_hit_ratio > 0.6:
                analysis['performance_insights']['cache_efficiency'] = 'good'
            elif overall_hit_ratio > 0.4:
                analysis['performance_insights']['cache_efficiency'] = 'fair'
            else:
                analysis['performance_insights']['cache_efficiency'] = 'poor'
            
            # Recommendations
            if overall_hit_ratio < 0.5:
                analysis['recommendations'].append('Consider increasing cache TTL for frequently accessed data')
                analysis['recommendations'].append('Review cache key strategies for better hit rates')
            
            # Level-specific analysis
            levels = cache_stats.get('levels', {})
            for level_name, level_stats in levels.items():
                if level_stats.get('hit_ratio', 0) < 0.3:
                    analysis['recommendations'].append(f'Low hit ratio in {level_name} cache - consider configuration review')
            
            return analysis
            
        except Exception as e:
            return {'error': f'Failed to analyze cache performance: {e}'}
    
    async def invalidate_optimization_cache(self, pattern: str = None) -> Dict[str, Any]:
        """Invalidate optimization-related cache entries"""
        
        if not self.cache_manager:
            return {'error': 'Cache manager not available'}
        
        try:
            if pattern:
                invalidated_count = await self.cache_manager.invalidate_by_pattern(pattern)
            else:
                # Invalidate common optimization patterns
                patterns = [
                    'analysis_optimization:*',
                    'knowledge_loading:*',
                    'vector_operations:*',
                    'parallel_processing:*'
                ]
                
                total_invalidated = 0
                for p in patterns:
                    count = await self.cache_manager.invalidate_by_pattern(p)
                    total_invalidated += count
                
                invalidated_count = total_invalidated
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'invalidated_count': invalidated_count,
                'pattern': pattern or 'optimization_related',
                'success': True
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e),
                'success': False
            }
    
    async def get_orchestrator_health_summary(self) -> Dict[str, Any]:
        """Get orchestrator health summary for monitoring"""
        
        if not self.orchestrator:
            return {'error': 'Orchestrator not available'}
        
        try:
            health = await self.orchestrator.get_orchestrator_health()
            
            # Create summary
            summary = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'overall_status': health.get('overall_status', 'unknown'),
                'open_circuits': 0,
                'stressed_pools': 0,
                'total_operations': 0,
                'avg_success_rate': 0.0,
                'circuit_breaker_summary': {},
                'bulkhead_pool_summary': {}
            }
            
            # Analyze circuit breakers
            circuit_breakers = health.get('circuit_breakers', {})
            for op_name, cb_data in circuit_breakers.items():
                if cb_data.get('state') == 'open':
                    summary['open_circuits'] += 1
                
                summary['circuit_breaker_summary'][op_name] = {
                    'state': cb_data.get('state'),
                    'health': cb_data.get('health')
                }
            
            # Analyze bulkhead pools
            bulkhead_pools = health.get('bulkhead_pools', {})
            for pool_name, pool_data in bulkhead_pools.items():
                utilization = pool_data.get('utilization', 0)
                if utilization > 80:
                    summary['stressed_pools'] += 1
                
                summary['bulkhead_pool_summary'][pool_name] = {
                    'utilization': utilization,
                    'health': pool_data.get('health')
                }
            
            # Analyze operation metrics
            operation_metrics = health.get('operation_metrics', {})
            total_requests = 0
            total_successful = 0
            
            for op_name, metrics in operation_metrics.items():
                requests = metrics.get('total_requests', 0)
                success_rate = metrics.get('success_rate', 0)
                
                total_requests += requests
                total_successful += (requests * success_rate / 100)
            
            if total_requests > 0:
                summary['total_operations'] = total_requests
                summary['avg_success_rate'] = (total_successful / total_requests) * 100
            
            return summary
            
        except Exception as e:
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e),
                'success': False
            }
    
    async def shutdown_enhanced_components(self):
        """Shutdown enhanced components gracefully"""
        tasks = []
        
        if self.orchestrator:
            tasks.append(self.orchestrator.shutdown())
        
        if self.cache_manager:
            tasks.append(self.cache_manager.shutdown())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("Enhanced optimization components shut down")

__all__ = ['EnhancedAnalysisOptimizationService']
