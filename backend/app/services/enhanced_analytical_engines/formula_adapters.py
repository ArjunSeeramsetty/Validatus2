# backend/app/services/enhanced_analytical_engines/formula_adapters.py
import logging
from typing import Dict, List, Any, Optional
import asyncio

from .pdf_formula_engine import PDFFormulaEngine, FactorInput, PDFAnalysisResult
from ..formula_engine import FormulaEngine  # Existing service
from ...core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

class EnhancedFormulaAdapter:
    """
    Adapter that bridges existing FormulaEngine with new PDFFormulaEngine
    Maintains backward compatibility while adding enhanced capabilities
    """
    
    def __init__(self):
        self.existing_engine = FormulaEngine()
        
        # Initialize PDF engine only if enhanced analytics enabled
        if FeatureFlags.PDF_FORMULAS_ENABLED:
            self.pdf_engine = PDFFormulaEngine()
            logger.info("✅ Enhanced Formula Adapter initialized with PDF engine")
        else:
            self.pdf_engine = None
            logger.info("✅ Enhanced Formula Adapter initialized in basic mode")
    
    async def calculate_enhanced_factors(self, 
                                       topic_knowledge: Dict[str, Any], 
                                       analysis_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate factors using both existing and enhanced engines
        
        Args:
            topic_knowledge: Knowledge extracted from topic analysis
            analysis_context: Analysis session context and parameters
            
        Returns:
            Combined results from both engines
        """
        try:
            results = {
                'basic_results': None,
                'enhanced_results': None,
                'combined_insights': [],
                'processing_metadata': {}
            }
            
            # Always run existing engine for backward compatibility
            basic_results = await self._run_existing_engine(topic_knowledge, analysis_context)
            results['basic_results'] = basic_results
            
            # Run enhanced engine if available
            if self.pdf_engine and FeatureFlags.PDF_FORMULAS_ENABLED:
                enhanced_results = await self._run_pdf_engine(topic_knowledge, analysis_context)
                results['enhanced_results'] = enhanced_results
                
                # Combine insights from both engines
                results['combined_insights'] = self._combine_insights(basic_results, enhanced_results)
            
            # Generate processing metadata
            results['processing_metadata'] = {
                'engines_used': ['basic'] + (['pdf'] if results['enhanced_results'] else []),
                'feature_flags': {
                    'pdf_formulas_enabled': FeatureFlags.PDF_FORMULAS_ENABLED,
                    'enhanced_analytics_enabled': FeatureFlags.ENHANCED_ANALYTICS_ENABLED
                }
            }
            
            logger.info("✅ Enhanced factor calculation completed")
            return results
            
        except Exception as e:
            logger.error(f"Enhanced factor calculation failed: {e}")
            # Fallback to basic engine only
            return {
                'basic_results': await self._run_existing_engine(topic_knowledge, analysis_context),
                'enhanced_results': None,
                'combined_insights': [],
                'processing_metadata': {'error': str(e), 'fallback_mode': True}
            }
    
    async def _run_existing_engine(self, topic_knowledge: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the existing formula engine"""
        try:
            # Use existing engine's calculation method
            # Adapt parameters to match existing interface
            layer_scores = context.get('layer_scores', {})
            
            # Call existing engine (adapt as needed based on actual implementation)
            basic_results = await self.existing_engine.calculate_strategic_factors(topic_knowledge, layer_scores)
            
            logger.info("✅ Basic formula engine calculation completed")
            return basic_results
            
        except Exception as e:
            logger.error(f"Basic formula engine calculation failed: {e}")
            return {'error': str(e), 'scores': {}, 'confidence': 0.5}
    
    async def _run_pdf_engine(self, topic_knowledge: Dict[str, Any], context: Dict[str, Any]) -> PDFAnalysisResult:
        """Run the enhanced PDF formula engine"""
        try:
            # Convert topic knowledge to factor inputs
            factor_inputs = self._convert_to_factor_inputs(topic_knowledge, context)
            
            # Run PDF engine
            pdf_results = await self.pdf_engine.calculate_all_factors(factor_inputs)
            
            logger.info("✅ PDF formula engine calculation completed")
            return pdf_results
            
        except Exception as e:
            logger.error(f"PDF formula engine calculation failed: {e}")
            raise
    
    def _convert_to_factor_inputs(self, topic_knowledge: Dict[str, Any], context: Dict[str, Any]) -> List[FactorInput]:
        """Convert topic knowledge to PDF engine factor inputs"""
        factor_inputs = []
        
        # Extract available data for each factor category
        market_data = topic_knowledge.get('market_analysis', {})
        product_data = topic_knowledge.get('product_analysis', {})
        financial_data = topic_knowledge.get('financial_analysis', {})
        strategic_data = topic_knowledge.get('strategic_analysis', {})
        
        # Create factor inputs for F1-F7 (Market factors)
        if market_data:
            for factor_id in ['F1_market_size', 'F2_market_growth', 'F3_market_maturity', 
                             'F4_competitive_intensity', 'F5_barrier_to_entry', 
                             'F6_regulatory_environment', 'F7_economic_sensitivity']:
                factor_input = FactorInput(
                    factor_id=factor_id,
                    raw_data=market_data,
                    context_data=context,
                    quality_score=topic_knowledge.get('content_quality', {}).get('overall_score', 0.7),
                    confidence=context.get('analysis_confidence', 0.7)
                )
                factor_inputs.append(factor_input)
        
        # Create factor inputs for F8-F14 (Product factors)
        if product_data:
            for factor_id in ['F8_product_differentiation', 'F9_innovation_capability', 
                             'F10_quality_reliability', 'F11_scalability_potential',
                             'F12_customer_stickiness', 'F13_pricing_power', 'F14_lifecycle_position']:
                factor_input = FactorInput(
                    factor_id=factor_id,
                    raw_data=product_data,
                    context_data=context,
                    quality_score=topic_knowledge.get('content_quality', {}).get('overall_score', 0.7),
                    confidence=context.get('analysis_confidence', 0.7)
                )
                factor_inputs.append(factor_input)
        
        # Create factor inputs for F15-F21 (Financial factors)
        if financial_data:
            for factor_id in ['F15_revenue_growth', 'F16_profitability_margins', 
                             'F17_cash_flow_generation', 'F18_capital_efficiency',
                             'F19_financial_stability', 'F20_cost_structure', 'F21_working_capital']:
                factor_input = FactorInput(
                    factor_id=factor_id,
                    raw_data=financial_data,
                    context_data=context,
                    quality_score=topic_knowledge.get('content_quality', {}).get('overall_score', 0.7),
                    confidence=context.get('analysis_confidence', 0.7)
                )
                factor_inputs.append(factor_input)
        
        # Create factor inputs for F22-F28 (Strategic factors)
        if strategic_data:
            for factor_id in ['F22_brand_strength', 'F23_management_quality', 
                             'F24_strategic_positioning', 'F25_operational_excellence',
                             'F26_digital_transformation', 'F27_sustainability_esg', 'F28_strategic_flexibility']:
                factor_input = FactorInput(
                    factor_id=factor_id,
                    raw_data=strategic_data,
                    context_data=context,
                    quality_score=topic_knowledge.get('content_quality', {}).get('overall_score', 0.7),
                    confidence=context.get('analysis_confidence', 0.7)
                )
                factor_inputs.append(factor_input)
        
        logger.info(f"✅ Created {len(factor_inputs)} factor inputs for PDF engine")
        return factor_inputs
    
    def _combine_insights(self, basic_results: Dict[str, Any], pdf_results: PDFAnalysisResult) -> List[Dict[str, Any]]:
        """Combine insights from both engines"""
        combined_insights = []
        
        # Compare scores and identify significant differences
        basic_scores = basic_results.get('scores', {})
        
        if hasattr(pdf_results, 'category_scores'):
            pdf_scores = pdf_results.category_scores
            
            for category in ['market', 'product', 'financial', 'strategic']:
                basic_score = basic_scores.get(category, 0.5)
                pdf_score = pdf_scores.get(category, 0.5)
                
                difference = abs(basic_score - pdf_score)
                if difference > 0.1:  # Significant difference
                    insight = {
                        'category': category,
                        'basic_score': basic_score,
                        'enhanced_score': pdf_score,
                        'difference': difference,
                        'recommendation': self._generate_score_difference_insight(category, basic_score, pdf_score)
                    }
                    combined_insights.append(insight)
        
        # Add overall confidence comparison
        basic_confidence = basic_results.get('confidence', 0.5)
        pdf_confidence = pdf_results.confidence_metrics.get('overall_confidence', 0.5) if pdf_results.confidence_metrics else 0.5
        
        combined_insights.append({
            'type': 'confidence_comparison',
            'basic_confidence': basic_confidence,
            'enhanced_confidence': pdf_confidence,
            'improvement': pdf_confidence - basic_confidence
        })
        
        return combined_insights
    
    def _generate_score_difference_insight(self, category: str, basic_score: float, pdf_score: float) -> str:
        """Generate insight text for score differences"""
        if pdf_score > basic_score:
            return f"Enhanced analysis shows {category} performance is {((pdf_score/basic_score - 1) * 100):.1f}% stronger than basic assessment suggests"
        else:
            return f"Enhanced analysis indicates {category} performance is {((1 - pdf_score/basic_score) * 100):.1f}% weaker than basic assessment suggests"

__all__ = ['EnhancedFormulaAdapter']
