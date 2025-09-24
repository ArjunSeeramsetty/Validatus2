# backend/app/services/enhanced_analysis_session_manager.py
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from .analysis_session_manager import AnalysisSessionManager  # Existing service
from .enhanced_analytical_engines.pdf_formula_engine import PDFFormulaEngine, FactorInput
from .enhanced_analytical_engines.action_layer_calculator import ActionLayerCalculator
from .enhanced_analytical_engines.formula_adapters import EnhancedFormulaAdapter
from ..core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

class EnhancedAnalysisSessionManager(AnalysisSessionManager):
    """
    Enhanced Analysis Session Manager that extends existing functionality
    with Phase B analytical engines while maintaining backward compatibility
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize Phase B engines conditionally
        if FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
            self.formula_adapter = EnhancedFormulaAdapter()
            
            if FeatureFlags.ACTION_LAYER_CALCULATOR_ENABLED:
                self.action_calculator = ActionLayerCalculator()
            else:
                self.action_calculator = None
            
            logger.info("✅ Enhanced Analysis Session Manager initialized with Phase B engines")
        else:
            self.formula_adapter = None
            self.action_calculator = None
            logger.info("✅ Enhanced Analysis Session Manager initialized in basic mode")
    
    async def execute_enhanced_strategic_analysis(self, 
                                                session_id: str, 
                                                topic: str, 
                                                user_id: str,
                                                enhanced_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute strategic analysis with enhanced capabilities
        
        Args:
            session_id: Analysis session identifier
            topic: Analysis topic
            user_id: User identifier  
            enhanced_options: Options for enhanced analysis
            
        Returns:
            Comprehensive analysis results combining basic and enhanced engines
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"Starting enhanced strategic analysis for session {session_id}")
        
        try:
            # First run existing analysis pipeline
            basic_results = await super().execute_strategic_analysis(session_id, topic, user_id)
            
            analysis_results = {
                'session_id': session_id,
                'topic': topic,
                'user_id': user_id,
                'basic_analysis': basic_results,
                'enhanced_analysis': {},
                'combined_insights': [],
                'processing_metadata': {}
            }
            
            # If enhanced analytics enabled, run Phase B engines
            if self.formula_adapter and FeatureFlags.ENHANCED_ANALYTICS_ENABLED:
                enhanced_results = await self._run_enhanced_analysis(
                    session_id, basic_results, enhanced_options or {}
                )
                analysis_results['enhanced_analysis'] = enhanced_results
                
                # Generate combined insights
                analysis_results['combined_insights'] = await self._generate_combined_insights(
                    basic_results, enhanced_results
                )
            
            # Calculate processing metadata
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            analysis_results['processing_metadata'] = {
                'total_processing_time': processing_time,
                'enhanced_engines_used': FeatureFlags.ENHANCED_ANALYTICS_ENABLED,
                'engines_enabled': {
                    'pdf_formulas': FeatureFlags.PDF_FORMULAS_ENABLED,
                    'action_layers': FeatureFlags.ACTION_LAYER_CALCULATOR_ENABLED,
                    'pattern_recognition': FeatureFlags.PATTERN_RECOGNITION_ENABLED
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Enhanced strategic analysis completed in {processing_time:.2f}s")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Enhanced strategic analysis failed for session {session_id}: {e}")
            # Fallback to basic analysis only
            return {
                'session_id': session_id,
                'basic_analysis': await super().execute_strategic_analysis(session_id, topic, user_id),
                'enhanced_analysis': {},
                'error': str(e),
                'fallback_mode': True
            }
    
    async def _run_enhanced_analysis(self, 
                                   session_id: str, 
                                   basic_results: Dict[str, Any],
                                   enhanced_options: Dict[str, Any]) -> Dict[str, Any]:
        """Run enhanced analysis engines"""
        
        enhanced_results = {}
        
        # Extract topic knowledge from basic results
        topic_knowledge = basic_results.get('topic_knowledge', {})
        analysis_context = basic_results.get('analysis_context', {})
        
        # Run enhanced formula analysis
        if self.formula_adapter:
            try:
                formula_results = await self.formula_adapter.calculate_enhanced_factors(
                    topic_knowledge, analysis_context
                )
                enhanced_results['formula_analysis'] = formula_results
                
                # Run action layer analysis if PDF results available
                if (self.action_calculator and 
                    formula_results.get('enhanced_results') and
                    FeatureFlags.ACTION_LAYER_CALCULATOR_ENABLED):
                    
                    pdf_results = formula_results['enhanced_results']
                    action_results = await self.action_calculator.calculate_all_action_layers(pdf_results)
                    enhanced_results['action_analysis'] = action_results
                    
            except Exception as e:
                logger.error(f"Enhanced formula analysis failed: {e}")
                enhanced_results['formula_analysis'] = {'error': str(e)}
        
        # Add pattern recognition analysis (placeholder for future implementation)
        if FeatureFlags.PATTERN_RECOGNITION_ENABLED:
            enhanced_results['pattern_analysis'] = {
                'status': 'planned',
                'message': 'Pattern recognition analysis will be implemented in next phase'
            }
        
        return enhanced_results
    
    async def _generate_combined_insights(self, 
                                        basic_results: Dict[str, Any], 
                                        enhanced_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights combining basic and enhanced analysis results"""
        
        combined_insights = []
        
        # Compare basic vs enhanced formula results
        if 'formula_analysis' in enhanced_results:
            formula_analysis = enhanced_results['formula_analysis']
            
            if 'combined_insights' in formula_analysis:
                # Add formula-level insights
                for insight in formula_analysis['combined_insights']:
                    combined_insights.append({
                        'source': 'formula_comparison',
                        'type': 'score_enhancement',
                        **insight
                    })
        
        # Add action layer insights
        if 'action_analysis' in enhanced_results:
            action_analysis = enhanced_results['action_analysis']
            
            # Extract top strategic priorities
            if hasattr(action_analysis, 'strategic_priorities'):
                top_priorities = action_analysis.strategic_priorities[:3]
                combined_insights.append({
                    'source': 'action_layer_analysis',
                    'type': 'strategic_priorities',
                    'priorities': [
                        {
                            'title': priority.title,
                            'priority': priority.priority.value,
                            'impact_score': priority.impact_score,
                            'roi_estimate': priority.roi_estimate
                        }
                        for priority in top_priorities
                    ]
                })
            
            # Add risk assessment insights
            if hasattr(action_analysis, 'risk_assessment'):
                risk_info = action_analysis.risk_assessment
                combined_insights.append({
                    'source': 'risk_assessment',
                    'type': 'risk_analysis',
                    'overall_risk': risk_info.get('overall_risk', 0.5),
                    'risk_level': risk_info.get('risk_level', 'Medium'),
                    'key_risks': [
                        f"{risk_type}: {score:.2f}" 
                        for risk_type, score in risk_info.items() 
                        if risk_type.endswith('_risk') and risk_type != 'overall_risk'
                    ]
                })
        
        # Add enhancement summary
        combined_insights.append({
            'source': 'enhancement_summary',
            'type': 'analysis_enhancement',
            'message': f"Enhanced analysis added {len(enhanced_results)} additional analytical layers",
            'enhanced_components': list(enhanced_results.keys())
        })
        
        return combined_insights

    # Override parent method to use enhanced version when available
    async def execute_strategic_analysis(self, session_id: str, topic: str, user_id: str) -> Dict[str, Any]:
        """Execute strategic analysis with enhanced capabilities when available"""
        
        if FeatureFlags.ENHANCED_ANALYTICS_ENABLED and self.formula_adapter:
            return await self.execute_enhanced_strategic_analysis(session_id, topic, user_id)
        else:
            # Fallback to parent implementation
            return await super().execute_strategic_analysis(session_id, topic, user_id)

__all__ = ['EnhancedAnalysisSessionManager']
