#!/usr/bin/env python3
"""
Phase B Integration Test Script

This script tests the Phase B enhanced analytical engines integration
into the Validatus platform.
"""

import sys
import os
import asyncio
import logging
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.feature_flags import FeatureFlags
from app.services.enhanced_analytical_engines import (
    PDFFormulaEngine, 
    ActionLayerCalculator,
    MonteCarloSimulator,
    EnhancedFormulaAdapter,
    MathematicalModels
)

logger = logging.getLogger(__name__)

class PhaseBIntegrationTester:
    """Test Phase B integration components"""
    
    def __init__(self):
        self.test_results = []
        self.feature_flags_status = {}
        
    def test_feature_flags(self) -> bool:
        """Test Phase B feature flags configuration"""
        logger.info("🧪 Testing Phase B feature flags...")
        
        try:
            self.feature_flags_status = {
                'enhanced_analytics': FeatureFlags.ENHANCED_ANALYTICS_ENABLED,
                'pdf_formulas': FeatureFlags.PDF_FORMULAS_ENABLED,
                'action_layers': FeatureFlags.ACTION_LAYER_CALCULATOR_ENABLED,
                'pattern_recognition': FeatureFlags.PATTERN_RECOGNITION_ENABLED,
                'phase_b_enabled': FeatureFlags.is_phase_enabled('phase_b')
            }
            
            logger.info(f"✅ Feature flags status: {self.feature_flags_status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Feature flags test failed: {e}")
            return False
    
    async def test_mathematical_models(self) -> bool:
        """Test mathematical models foundation"""
        logger.info("🧪 Testing Mathematical Models...")
        
        try:
            math_models = MathematicalModels()
            
            # Test logistic normalization
            test_score = 0.7
            normalized = math_models.logistic_normalize(test_score)
            
            # Test factor weights
            factor_weights = math_models.factor_weights
            f1_weight = factor_weights['F1_market_size'].effective_weight
            
            # Test category factors
            market_factors = math_models._get_category_factors('market')
            
            logger.info(f"✅ Mathematical models working:")
            logger.info(f"  - Logistic normalization: {test_score} -> {normalized:.3f}")
            logger.info(f"  - F1 weight: {f1_weight:.3f}")
            logger.info(f"  - Market factors: {len(market_factors)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Mathematical models test failed: {e}")
            return False
    
    async def test_pdf_formula_engine(self) -> bool:
        """Test PDF Formula Engine"""
        logger.info("🧪 Testing PDF Formula Engine...")
        
        try:
            pdf_engine = PDFFormulaEngine()
            
            # Create test factor inputs
            from app.services.enhanced_analytical_engines import FactorInput
            
            test_inputs = [
                FactorInput(
                    factor_id='F1_market_size',
                    raw_data={'total_addressable_market': 1000000000, 'market_penetration': 0.3},
                    context_data={'analysis_confidence': 0.8},
                    quality_score=0.8,
                    confidence=0.8
                ),
                FactorInput(
                    factor_id='F2_market_growth',
                    raw_data={'market_growth_rate': 0.15, 'growth_sustainability': 0.7},
                    context_data={'analysis_confidence': 0.8},
                    quality_score=0.8,
                    confidence=0.8
                )
            ]
            
            # Run factor calculation
            results = await pdf_engine.calculate_all_factors(test_inputs)
            
            logger.info(f"✅ PDF Formula Engine working:")
            logger.info(f"  - Factors calculated: {len(results.factor_results)}")
            logger.info(f"  - Overall score: {results.overall_score:.3f}")
            logger.info(f"  - Category scores: {results.category_scores}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ PDF Formula Engine test failed: {e}")
            return False
    
    async def test_action_layer_calculator(self) -> bool:
        """Test Action Layer Calculator"""
        logger.info("🧪 Testing Action Layer Calculator...")
        
        try:
            action_calculator = ActionLayerCalculator()
            
            # Create mock PDF results for testing
            from app.services.enhanced_analytical_engines import PDFAnalysisResult, FactorResult
            
            mock_factor_results = {}
            for i in range(1, 29):
                factor_id = f'F{i}_test_factor'
                mock_factor_results[factor_id] = FactorResult(
                    factor_id=factor_id,
                    factor_name=f'Test Factor {i}',
                    raw_score=0.6,
                    normalized_score=0.6,
                    confidence=0.8,
                    weight=0.04,
                    calculation_steps=[],
                    metadata={}
                )
            
            mock_pdf_results = PDFAnalysisResult(
                factor_results=mock_factor_results,
                category_scores={'market': 0.6, 'product': 0.6, 'financial': 0.6, 'strategic': 0.6},
                overall_score=0.6,
                confidence_metrics={'overall_confidence': 0.8},
                processing_metadata={}
            )
            
            # Run action layer analysis
            action_results = await action_calculator.calculate_all_action_layers(mock_pdf_results)
            
            logger.info(f"✅ Action Layer Calculator working:")
            logger.info(f"  - Layers calculated: {len(action_results.layer_results)}")
            logger.info(f"  - Strategic priorities: {len(action_results.strategic_priorities)}")
            logger.info(f"  - Risk assessment: {action_results.risk_assessment}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Action Layer Calculator test failed: {e}")
            return False
    
    async def test_monte_carlo_simulator(self) -> bool:
        """Test Monte Carlo Simulator"""
        logger.info("🧪 Testing Monte Carlo Simulator...")
        
        try:
            simulator = MonteCarloSimulator()
            
            # Test simulation parameters
            pattern_data = {
                'expected_score': 0.7,
                'pattern_multiplier': 1.0,
                'industry_factor': 1.0,
                'time_decay_factor': 1.0
            }
            
            uncertainties = {
                'market_conditions': {'distribution': 'normal', 'mean': 0.0, 'std': 0.1},
                'competitive_dynamics': {'distribution': 'normal', 'mean': 0.0, 'std': 0.05},
                'financial_performance': {'distribution': 'normal', 'mean': 0.0, 'std': 0.08},
                'execution_risk': {'distribution': 'normal', 'mean': 0.0, 'std': 0.06}
            }
            
            # Run simulation
            simulation_result = await simulator.run_pattern_simulation(pattern_data, uncertainties)
            
            logger.info(f"✅ Monte Carlo Simulator working:")
            logger.info(f"  - Mean: {simulation_result.mean:.3f}")
            logger.info(f"  - Std Dev: {simulation_result.std_dev:.3f}")
            logger.info(f"  - 95% CI: {simulation_result.confidence_intervals[0.95]}")
            logger.info(f"  - Success probability: {simulation_result.risk_metrics['success_probability']:.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Monte Carlo Simulator test failed: {e}")
            return False
    
    async def test_enhanced_formula_adapter(self) -> bool:
        """Test Enhanced Formula Adapter"""
        logger.info("🧪 Testing Enhanced Formula Adapter...")
        
        try:
            adapter = EnhancedFormulaAdapter()
            
            # Test topic knowledge
            topic_knowledge = {
                'market_analysis': {
                    'total_addressable_market': 1000000000,
                    'market_growth_rate': 0.15,
                    'market_maturity_stage': 2.0
                },
                'product_analysis': {
                    'product_differentiation': 0.7,
                    'innovation_capability': 0.6,
                    'quality_reliability': 0.8
                },
                'content_quality': {'overall_score': 0.8}
            }
            
            analysis_context = {
                'analysis_confidence': 0.8,
                'layer_scores': {'market': 0.6, 'product': 0.7}
            }
            
            # Run enhanced factor calculation
            results = await adapter.calculate_enhanced_factors(topic_knowledge, analysis_context)
            
            logger.info(f"✅ Enhanced Formula Adapter working:")
            logger.info(f"  - Engines used: {results['processing_metadata']['engines_used']}")
            logger.info(f"  - Enhanced results available: {results['enhanced_results'] is not None}")
            logger.info(f"  - Combined insights: {len(results['combined_insights'])}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Enhanced Formula Adapter test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase B integration tests"""
        logger.info("🚀 Starting Phase B Integration Tests...")
        
        test_results = {
            'feature_flags': False,
            'mathematical_models': False,
            'pdf_formula_engine': False,
            'action_layer_calculator': False,
            'monte_carlo_simulator': False,
            'enhanced_formula_adapter': False
        }
        
        # Test feature flags first
        test_results['feature_flags'] = self.test_feature_flags()
        
        # Test individual components
        test_results['mathematical_models'] = await self.test_mathematical_models()
        test_results['pdf_formula_engine'] = await self.test_pdf_formula_engine()
        test_results['action_layer_calculator'] = await self.test_action_layer_calculator()
        test_results['monte_carlo_simulator'] = await self.test_monte_carlo_simulator()
        test_results['enhanced_formula_adapter'] = await self.test_enhanced_formula_adapter()
        
        # Calculate success rate
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"📊 Phase B Integration Test Results:")
        logger.info(f"  - Tests passed: {passed_tests}/{total_tests}")
        logger.info(f"  - Success rate: {success_rate:.1f}%")
        logger.info(f"  - Feature flags: {self.feature_flags_status}")
        
        return {
            'test_results': test_results,
            'feature_flags_status': self.feature_flags_status,
            'success_rate': success_rate,
            'passed_tests': passed_tests,
            'total_tests': total_tests
        }

async def main():
    """Main test function"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    tester = PhaseBIntegrationTester()
    results = await tester.run_all_tests()
    
    if results['success_rate'] == 100.0:
        logger.info("🎉 All Phase B integration tests passed!")
        return 0
    else:
        logger.warning(f"⚠️  Phase B integration tests completed with {results['success_rate']:.1f}% success rate")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
