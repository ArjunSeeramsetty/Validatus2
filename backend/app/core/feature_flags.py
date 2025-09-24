# backend/app/core/feature_flags.py
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FeatureFlags:
    """Centralized feature flag management for gradual integration"""
    
    # Core service feature flags
    ENHANCED_ANALYTICS_ENABLED = os.getenv('ENABLE_ENHANCED_ANALYTICS', 'false').lower() == 'true'
    ANALYSIS_RESULTS_MANAGER_ENABLED = os.getenv('ENABLE_RESULTS_MANAGER', 'true').lower() == 'true'
    RESULTS_API_ENABLED = os.getenv('ENABLE_RESULTS_API', 'true').lower() == 'true'
    
    # Phase B feature flags (for future use)
    PDF_FORMULAS_ENABLED = os.getenv('ENABLE_PDF_FORMULAS', 'false').lower() == 'true'
    ACTION_LAYER_CALCULATOR_ENABLED = os.getenv('ENABLE_ACTION_LAYER', 'false').lower() == 'true'
    PATTERN_RECOGNITION_ENABLED = os.getenv('ENABLE_PATTERN_RECOGNITION', 'false').lower() == 'true'
    
    # Phase C feature flags (for future use)
    BAYESIAN_PIPELINE_ENABLED = os.getenv('ENABLE_BAYESIAN_PIPELINE', 'false').lower() == 'true'
    ADVANCED_RAG_ENABLED = os.getenv('ENABLE_ADVANCED_RAG', 'false').lower() == 'true'
    HYBRID_VECTOR_STORE_ENABLED = os.getenv('ENABLE_HYBRID_VECTOR_STORE', 'false').lower() == 'true'
    
    # Phase D feature flags (for future use)
    ENHANCED_FRONTEND_ENABLED = os.getenv('ENABLE_ENHANCED_FRONTEND', 'false').lower() == 'true'
    REAL_TIME_UPDATES_ENABLED = os.getenv('ENABLE_REAL_TIME_UPDATES', 'false').lower() == 'true'
    ADVANCED_VISUALIZATIONS_ENABLED = os.getenv('ENABLE_ADVANCED_VIZ', 'false').lower() == 'true'
    
    # Phase E feature flags (for future use)
    CIRCUIT_BREAKERS_ENABLED = os.getenv('ENABLE_CIRCUIT_BREAKERS', 'false').lower() == 'true'
    MULTI_LEVEL_CACHING_ENABLED = os.getenv('ENABLE_MULTI_LEVEL_CACHE', 'false').lower() == 'true'
    ADVANCED_MONITORING_ENABLED = os.getenv('ENABLE_ADVANCED_MONITORING', 'false').lower() == 'true'
    
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
            
            # Phase B flags
            'pdf_formulas': cls.PDF_FORMULAS_ENABLED,
            'action_layer_calculator': cls.ACTION_LAYER_CALCULATOR_ENABLED,
            'pattern_recognition': cls.PATTERN_RECOGNITION_ENABLED,
            
            # Phase C flags
            'bayesian_pipeline': cls.BAYESIAN_PIPELINE_ENABLED,
            'advanced_rag': cls.ADVANCED_RAG_ENABLED,
            'hybrid_vector_store': cls.HYBRID_VECTOR_STORE_ENABLED,
            
            # Phase D flags
            'enhanced_frontend': cls.ENHANCED_FRONTEND_ENABLED,
            'real_time_updates': cls.REAL_TIME_UPDATES_ENABLED,
            'advanced_visualizations': cls.ADVANCED_VISUALIZATIONS_ENABLED,
            
            # Phase E flags
            'circuit_breakers': cls.CIRCUIT_BREAKERS_ENABLED,
            'multi_level_caching': cls.MULTI_LEVEL_CACHING_ENABLED,
            'advanced_monitoring': cls.ADVANCED_MONITORING_ENABLED,
            
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
                cls.ADVANCED_RAG_ENABLED,
                cls.HYBRID_VECTOR_STORE_ENABLED
            ]),
            'phase_d': any([
                cls.ENHANCED_FRONTEND_ENABLED,
                cls.REAL_TIME_UPDATES_ENABLED,
                cls.ADVANCED_VISUALIZATIONS_ENABLED
            ]),
            'phase_e': any([
                cls.CIRCUIT_BREAKERS_ENABLED,
                cls.MULTI_LEVEL_CACHING_ENABLED,
                cls.ADVANCED_MONITORING_ENABLED
            ])
        }
        return phase_mappings.get(phase.lower(), False)
    
    @classmethod
    def log_current_configuration(cls):
        """Log current feature flag configuration"""
        enabled_flags = [name for name, value in cls.get_all_flags().items() if value]
        logger.info(f"Feature flags enabled: {enabled_flags}")
        
        for phase in ['phase_b', 'phase_c', 'phase_d', 'phase_e']:
            if cls.is_phase_enabled(phase):
                logger.info(f"Integration {phase.upper()} is enabled")

# Initialize logging on import
FeatureFlags.log_current_configuration()

__all__ = ['FeatureFlags']
