# backend/app/core/feature_flags.py
import os
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class FeatureFlags:
    """Centralized feature flag management for gradual integration"""
    
    # Core service feature flags - ENABLED FOR RESTORED FUNCTIONALITY
    ENHANCED_ANALYTICS_ENABLED = os.getenv('ENABLE_ENHANCED_ANALYTICS', 'true').lower() == 'true'
    ANALYSIS_RESULTS_MANAGER_ENABLED = os.getenv('ENABLE_RESULTS_MANAGER', 'true').lower() == 'true'
    RESULTS_API_ENABLED = os.getenv('ENABLE_RESULTS_API', 'true').lower() == 'true'
    
    # Pergola Feature Flags - ENABLED
    PERGOLA_INTELLIGENCE_ENABLED = os.getenv('ENABLE_PERGOLA_INTELLIGENCE', 'true').lower() == 'true'
    PERGOLA_ANALYSIS_ENABLED = os.getenv('ENABLE_PERGOLA_ANALYSIS', 'true').lower() == 'true'
    PERGOLA_CHAT_ENABLED = os.getenv('ENABLE_PERGOLA_CHAT', 'true').lower() == 'true'
    
    # Advanced Analysis Feature Flags - ENABLED
    ADVANCED_ANALYSIS_ENABLED = os.getenv('ENABLE_ADVANCED_ANALYSIS', 'true').lower() == 'true'
    MONTE_CARLO_SIMULATION_ENABLED = os.getenv('ENABLE_MONTE_CARLO', 'true').lower() == 'true'
    PATTERN_RECOGNITION_ENABLED = os.getenv('ENABLE_PATTERN_RECOGNITION', 'true').lower() == 'true'
    
    # Phase B feature flags (for future use)
    PDF_FORMULAS_ENABLED = os.getenv('ENABLE_PDF_FORMULAS', 'false').lower() == 'true'
    ACTION_LAYER_CALCULATOR_ENABLED = os.getenv('ENABLE_ACTION_LAYER', 'false').lower() == 'true'
    PATTERN_RECOGNITION_ENABLED = os.getenv('ENABLE_PATTERN_RECOGNITION', 'false').lower() == 'true'
    
    # Phase C feature flags - Data Pipeline Enhancement
    BAYESIAN_PIPELINE_ENABLED = os.getenv('ENABLE_BAYESIAN_PIPELINE', 'false').lower() == 'true'
    EVENT_SHOCK_MODELING_ENABLED = os.getenv('ENABLE_EVENT_SHOCK_MODELING', 'false').lower() == 'true'
    ENHANCED_CONTENT_PROCESSING_ENABLED = os.getenv('ENABLE_ENHANCED_CONTENT_PROCESSING', 'false').lower() == 'true'
    HYBRID_VECTOR_STORE_ENABLED = os.getenv('ENABLE_HYBRID_VECTOR_STORE', 'false').lower() == 'true'
    ADVANCED_RAG_ENABLED = os.getenv('ENABLE_ADVANCED_RAG', 'false').lower() == 'true'
    
    # Phase D feature flags (for future use)
    ENHANCED_FRONTEND_ENABLED = os.getenv('ENABLE_ENHANCED_FRONTEND', 'false').lower() == 'true'
    REAL_TIME_UPDATES_ENABLED = os.getenv('ENABLE_REAL_TIME_UPDATES', 'false').lower() == 'true'
    ADVANCED_VISUALIZATIONS_ENABLED = os.getenv('ENABLE_ADVANCED_VIZ', 'false').lower() == 'true'
    
    # Phase E feature flags - Advanced Orchestration & Observability
    ADVANCED_ORCHESTRATION_ENABLED = os.getenv('ENABLE_ADVANCED_ORCHESTRATION', 'false').lower() == 'true'
    CIRCUIT_BREAKER_ENABLED = os.getenv('ENABLE_CIRCUIT_BREAKER', 'false').lower() == 'true'
    MULTI_LEVEL_CACHE_ENABLED = os.getenv('ENABLE_MULTI_LEVEL_CACHE', 'false').lower() == 'true'
    REDIS_CACHE_ENABLED = os.getenv('ENABLE_REDIS_CACHE', 'false').lower() == 'true'
    EVENT_DRIVEN_PUBLISHER_ENABLED = os.getenv('ENABLE_EVENT_DRIVEN_PUBLISHER', 'false').lower() == 'true'
    COMPREHENSIVE_MONITORING_ENABLED = os.getenv('ENABLE_COMPREHENSIVE_MONITORING', 'true').lower() == 'true'
    
    # Advanced observability
    PERFORMANCE_PROFILING_ENABLED = os.getenv('ENABLE_PERFORMANCE_PROFILING', 'false').lower() == 'true'
    DISTRIBUTED_TRACING_ENABLED = os.getenv('ENABLE_DISTRIBUTED_TRACING', 'false').lower() == 'true'
    CUSTOM_METRICS_ENABLED = os.getenv('ENABLE_CUSTOM_METRICS', 'true').lower() == 'true'
    ERROR_TRACKING_ENHANCED = os.getenv('ENABLE_ENHANCED_ERROR_TRACKING', 'true').lower() == 'true'
    
    # Production hardening
    RATE_LIMITING_ENABLED = os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
    REQUEST_VALIDATION_STRICT = os.getenv('ENABLE_STRICT_VALIDATION', 'false').lower() == 'true'
    SECURITY_HEADERS_ENABLED = os.getenv('ENABLE_SECURITY_HEADERS', 'true').lower() == 'true'
    AUDIT_LOGGING_ENABLED = os.getenv('ENABLE_AUDIT_LOGGING', 'true').lower() == 'true'
    
    # Development and testing flags
    DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    MOCK_SERVICES_ENABLED = os.getenv('ENABLE_MOCK_SERVICES', 'false').lower() == 'true'
    
    @classmethod
    def get_all_flags(cls) -> Dict[str, bool]:
        """Get all feature flags as a dictionary"""
        return {
            # Core flags
            'enhanced_analytics': cls.ENHANCED_ANALYTICS_ENABLED,
            'results_manager': cls.ANALYSIS_RESULTS_MANAGER_ENABLED,
            'results_api': cls.RESULTS_API_ENABLED,
            
            # Pergola flags
            'pergola_intelligence': cls.PERGOLA_INTELLIGENCE_ENABLED,
            'pergola_analysis': cls.PERGOLA_ANALYSIS_ENABLED,
            'pergola_chat': cls.PERGOLA_CHAT_ENABLED,
            
            # Advanced analysis flags
            'advanced_analysis': cls.ADVANCED_ANALYSIS_ENABLED,
            'monte_carlo_simulation': cls.MONTE_CARLO_SIMULATION_ENABLED,
            
            # Phase B flags
            'pdf_formulas': cls.PDF_FORMULAS_ENABLED,
            'action_layer_calculator': cls.ACTION_LAYER_CALCULATOR_ENABLED,
            'pattern_recognition': cls.PATTERN_RECOGNITION_ENABLED,
            
            # Phase C flags
            'bayesian_pipeline': cls.BAYESIAN_PIPELINE_ENABLED,
            'event_shock_modeling': cls.EVENT_SHOCK_MODELING_ENABLED,
            'enhanced_content_processing': cls.ENHANCED_CONTENT_PROCESSING_ENABLED,
            'advanced_rag': cls.ADVANCED_RAG_ENABLED,
            'hybrid_vector_store': cls.HYBRID_VECTOR_STORE_ENABLED,
            
            # Phase D flags
            'enhanced_frontend': cls.ENHANCED_FRONTEND_ENABLED,
            'real_time_updates': cls.REAL_TIME_UPDATES_ENABLED,
            'advanced_visualizations': cls.ADVANCED_VISUALIZATIONS_ENABLED,
            
            # Phase E flags
            'advanced_orchestration': cls.ADVANCED_ORCHESTRATION_ENABLED,
            'circuit_breaker': cls.CIRCUIT_BREAKER_ENABLED,
            'multi_level_cache': cls.MULTI_LEVEL_CACHE_ENABLED,
            'redis_cache': cls.REDIS_CACHE_ENABLED,
            'event_driven_publisher': cls.EVENT_DRIVEN_PUBLISHER_ENABLED,
            'comprehensive_monitoring': cls.COMPREHENSIVE_MONITORING_ENABLED,
            
            # Observability flags
            'performance_profiling': cls.PERFORMANCE_PROFILING_ENABLED,
            'distributed_tracing': cls.DISTRIBUTED_TRACING_ENABLED,
            'custom_metrics': cls.CUSTOM_METRICS_ENABLED,
            'error_tracking_enhanced': cls.ERROR_TRACKING_ENHANCED,
            
            # Production hardening flags
            'rate_limiting': cls.RATE_LIMITING_ENABLED,
            'request_validation_strict': cls.REQUEST_VALIDATION_STRICT,
            'security_headers': cls.SECURITY_HEADERS_ENABLED,
            'audit_logging': cls.AUDIT_LOGGING_ENABLED,
            
            # Development flags
            'debug_mode': cls.DEBUG_MODE_ENABLED,
            'mock_services': cls.MOCK_SERVICES_ENABLED
        }
    
    @classmethod
    def is_phase_enabled(cls, phase: str) -> bool:
        """Check if a specific integration phase is enabled"""
        phase_mappings = {
            'phase_a': True,  # Always enabled (stabilization)
            'phase_b': any([
                cls.PDF_FORMULAS_ENABLED,
                cls.ACTION_LAYER_CALCULATOR_ENABLED,
                cls.PATTERN_RECOGNITION_ENABLED
            ]),
            'phase_c': any([
                cls.BAYESIAN_PIPELINE_ENABLED,
                cls.EVENT_SHOCK_MODELING_ENABLED,
                cls.ENHANCED_CONTENT_PROCESSING_ENABLED,
                cls.ADVANCED_RAG_ENABLED,
                cls.HYBRID_VECTOR_STORE_ENABLED
            ]),
            'phase_d': any([
                cls.ENHANCED_FRONTEND_ENABLED,
                cls.REAL_TIME_UPDATES_ENABLED,
                cls.ADVANCED_VISUALIZATIONS_ENABLED
            ]),
            'phase_e': any([
                cls.ADVANCED_ORCHESTRATION_ENABLED,
                cls.CIRCUIT_BREAKER_ENABLED,
                cls.MULTI_LEVEL_CACHE_ENABLED,
                cls.EVENT_DRIVEN_PUBLISHER_ENABLED,
                cls.COMPREHENSIVE_MONITORING_ENABLED
            ])
        }
        return phase_mappings.get(phase.lower(), False)
    
    @classmethod
    def is_phase_e_enabled(cls) -> bool:
        """Check if any Phase E features are enabled"""
        return any([
            cls.ADVANCED_ORCHESTRATION_ENABLED,
            cls.CIRCUIT_BREAKER_ENABLED,
            cls.MULTI_LEVEL_CACHE_ENABLED,
            cls.EVENT_DRIVEN_PUBLISHER_ENABLED,
            cls.COMPREHENSIVE_MONITORING_ENABLED
        ])
    
    @classmethod
    def get_enabled_phases(cls) -> set:
        """Get list of enabled phases"""
        phases = set()
        
        if cls.ENHANCED_ANALYTICS_ENABLED:
            phases.add('phase_b')
        
        if any([cls.BAYESIAN_PIPELINE_ENABLED, cls.EVENT_SHOCK_MODELING_ENABLED, 
                cls.ENHANCED_CONTENT_PROCESSING_ENABLED, cls.HYBRID_VECTOR_STORE_ENABLED]):
            phases.add('phase_c')
        
        if any([cls.ENHANCED_FRONTEND_ENABLED, cls.REAL_TIME_UPDATES_ENABLED, 
                cls.ADVANCED_VISUALIZATIONS_ENABLED]):
            phases.add('phase_d')
        
        if cls.is_phase_e_enabled():
            phases.add('phase_e')
        
        return phases
    
    @classmethod
    def validate_feature_dependencies(cls) -> Dict[str, List[str]]:
        """Validate feature flag dependencies"""
        warnings = []
        
        # Multi-level cache requires Redis for L2
        if cls.MULTI_LEVEL_CACHE_ENABLED and not cls.REDIS_CACHE_ENABLED:
            warnings.append("Multi-level cache enabled but Redis cache disabled - L2 cache will be skipped")
        
        # Circuit breaker requires advanced orchestration
        if cls.CIRCUIT_BREAKER_ENABLED and not cls.ADVANCED_ORCHESTRATION_ENABLED:
            warnings.append("Circuit breaker enabled but advanced orchestration disabled")
        
        # Enhanced monitoring works best with all observability features
        if cls.COMPREHENSIVE_MONITORING_ENABLED:
            if not cls.CUSTOM_METRICS_ENABLED:
                warnings.append("Comprehensive monitoring enabled but custom metrics disabled")
            if not cls.ERROR_TRACKING_ENHANCED:
                warnings.append("Comprehensive monitoring enabled but enhanced error tracking disabled")
        
        return {'warnings': warnings}
    
    @classmethod
    def log_current_configuration(cls):
        """Log current feature flag configuration"""
        enabled_flags = [name for name, value in cls.get_all_flags().items() if value]
        logger.info(f"Feature flags enabled: {enabled_flags}")
        
        for phase in ['phase_b', 'phase_c', 'phase_d', 'phase_e']:
            if cls.is_phase_enabled(phase):
                logger.info(f"Integration {phase.upper()} is enabled")
        
        # Log dependency warnings
        validation_result = cls.validate_feature_dependencies()
        for warning in validation_result.get('warnings', []):
            logger.warning(f"Feature flag dependency warning: {warning}")

# Initialize logging on import
FeatureFlags.log_current_configuration()

__all__ = ['FeatureFlags']
