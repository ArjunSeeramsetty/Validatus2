# backend/app/services/service_factory.py
import logging
from typing import Dict, Any, Optional, Type, List
from dataclasses import dataclass
from ..core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfiguration:
    """Configuration for service initialization"""
    service_class: Type
    dependencies: List[str]
    feature_flag: Optional[str] = None
    initialization_priority: int = 1
    fallback_service: Optional[Type] = None

class ServiceFactory:
    """Factory for creating and managing services with feature flag control"""
    
    def __init__(self):
        self.core_services: Dict[str, Any] = {}
        self.enhanced_services: Dict[str, Any] = {}
        self.service_configurations = self._initialize_service_configurations()
        
    def _initialize_service_configurations(self) -> Dict[str, ServiceConfiguration]:
        """Define service configurations with dependencies and feature flags"""
        from .gcp_topic_vector_store_manager import GCPTopicVectorStoreManager
        from .analysis_session_manager import AnalysisSessionManager
        from .content_quality_analyzer import ContentQualityAnalyzer
        from .analysis_results_manager import AnalysisResultsManager
        
        configurations = {
            # Core services (always available)
            'topic_manager': ServiceConfiguration(
                service_class=GCPTopicVectorStoreManager,
                dependencies=[],
                initialization_priority=1
            ),
            'analysis_session_manager': ServiceConfiguration(
                service_class=AnalysisSessionManager,
                dependencies=['topic_manager'],
                initialization_priority=2
            ),
            'quality_analyzer': ServiceConfiguration(
                service_class=ContentQualityAnalyzer,
                dependencies=[],
                initialization_priority=1
            ),
            
            # Enhanced services (feature flag controlled)
            'results_manager': ServiceConfiguration(
                service_class=AnalysisResultsManager,
                dependencies=[],
                feature_flag='ANALYSIS_RESULTS_MANAGER_ENABLED',
                initialization_priority=3
            )
        }
        
        # Add Phase B services (when available)
        if FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
            try:
                from .enhanced_analytical_engines.pdf_formula_engine import PDFFormulaEngine
                configurations['pdf_formula_engine'] = ServiceConfiguration(
                    service_class=PDFFormulaEngine,
                    dependencies=[],
                    feature_flag='PDF_FORMULAS_ENABLED',
                    initialization_priority=4
                )
            except ImportError:
                logger.debug("PDF Formula Engine not available")
        
        return configurations
    
    async def create_core_services(self, gcp_settings) -> Dict[str, Any]:
        """Create core services that are always available"""
        from .gcp_topic_vector_store_manager import GCPTopicVectorStoreManager
        from .gcp_url_orchestrator import GCPURLOrchestrator
        from .enhanced_topic_vector_store_manager import EnhancedTopicVectorStoreManager
        from .analysis_session_manager import AnalysisSessionManager
        from .content_quality_analyzer import ContentQualityAnalyzer
        from .content_deduplication_service import ContentDeduplicationService
        from .analysis_optimization_service import AnalysisOptimizationService
        
        services = {}
        
        try:
            # Initialize with dependency order
            services['topic_manager'] = GCPTopicVectorStoreManager(
                project_id=gcp_settings.project_id
            )
            services['url_orchestrator'] = GCPURLOrchestrator(
                project_id=gcp_settings.project_id
            )
            services['enhanced_topic_manager'] = EnhancedTopicVectorStoreManager()
            services['analysis_session_manager'] = AnalysisSessionManager()
            services['quality_analyzer'] = ContentQualityAnalyzer()
            services['deduplication_service'] = ContentDeduplicationService()
            services['optimization_service'] = AnalysisOptimizationService()
            
            logger.info(f"✅ Created {len(services)} core services")
            
        except Exception as e:
            logger.error(f"Failed to create core services: {e}")
            raise
        
        return services
    
    async def create_enhanced_services(self) -> Dict[str, Any]:
        """Create enhanced services based on feature flags"""
        services = {}
        
        # Results Manager
        if FeatureFlags.ANALYSIS_RESULTS_MANAGER_ENABLED:
            try:
                from .analysis_results_manager import AnalysisResultsManager
                services['results_manager'] = AnalysisResultsManager()
                logger.info("✅ Analysis Results Manager created")
            except Exception as e:
                logger.error(f"Failed to create Results Manager: {e}")
        
        # Phase B Enhanced Analytics
        if FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
            services.update(await self._create_phase_b_services())
        
        # Phase C Data Pipeline
        if FeatureFlags.is_phase_enabled('phase_c'):
            services.update(await self._create_phase_c_services())
        
        logger.info(f"✅ Created {len(services)} enhanced services")
        return services
    
    async def _create_phase_b_services(self) -> Dict[str, Any]:
        """Create Phase B analytical engine services"""
        services = {}
        
        if FeatureFlags.PDF_FORMULAS_ENABLED:
            try:
                from .enhanced_analytical_engines.pdf_formula_engine import PDFFormulaEngine
                services['pdf_formula_engine'] = PDFFormulaEngine()
                logger.info("✅ PDF Formula Engine created")
            except ImportError:
                logger.warning("PDF Formula Engine not available")
        
        if FeatureFlags.ACTION_LAYER_CALCULATOR_ENABLED:
            try:
                from .enhanced_analytical_engines.action_layer_calculator import ActionLayerCalculator
                services['action_layer_calculator'] = ActionLayerCalculator()
                logger.info("✅ Action Layer Calculator created")
            except ImportError:
                logger.warning("Action Layer Calculator not available")
        
        if FeatureFlags.PATTERN_RECOGNITION_ENABLED:
            try:
                from .enhanced_analytical_engines.pattern_library_monte_carlo import PatternLibraryMonteCarloEngine
                services['pattern_engine'] = PatternLibraryMonteCarloEngine()
                logger.info("✅ Pattern Recognition Engine created")
            except ImportError:
                logger.warning("Pattern Recognition Engine not available")
        
        return services
    
    async def _create_phase_c_services(self) -> Dict[str, Any]:
        """Create Phase C data pipeline services"""
        services = {}
        
        # Placeholder for Phase C services
        logger.info("Phase C services will be implemented in Phase C")
        
        return services
    
    def get_service(self, service_name: str, service_type: str = 'core') -> Optional[Any]:
        """Get a service instance by name"""
        if service_type == 'core':
            return self.core_services.get(service_name)
        elif service_type == 'enhanced':
            return self.enhanced_services.get(service_name)
        else:
            # Search both
            return (self.core_services.get(service_name) or 
                   self.enhanced_services.get(service_name))
    
    def list_available_services(self) -> Dict[str, List[str]]:
        """List all available services"""
        return {
            'core_services': list(self.core_services.keys()),
            'enhanced_services': list(self.enhanced_services.keys())
        }

__all__ = ['ServiceFactory', 'ServiceConfiguration']
