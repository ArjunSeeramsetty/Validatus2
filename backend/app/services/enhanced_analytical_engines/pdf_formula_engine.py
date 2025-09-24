# backend/app/services/enhanced_analytical_engines/pdf_formula_engine.py
import asyncio
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import math

from .mathematical_models import MathematicalModels, FactorWeight
from ..content_quality_analyzer import ContentQualityAnalyzer
from ...core.feature_flags import FeatureFlags
from ...core.gcp_config import GCPSettings
from ...middleware.monitoring import performance_monitor
from ...core.error_recovery import with_exponential_backoff
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class FactorInput:
    """Input data for individual factor calculation"""
    factor_id: str
    raw_data: Dict[str, Any]
    context_data: Dict[str, Any]
    quality_score: float = 0.0
    confidence: float = 0.5
    timestamp: Optional[str] = None

@dataclass
class FactorResult:
    """Result of individual factor calculation"""
    factor_id: str
    factor_name: str
    raw_score: float
    normalized_score: float
    confidence: float
    weight: float
    calculation_steps: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    @property
    def weighted_score(self) -> float:
        """Calculate weighted score"""
        return self.normalized_score * self.weight

@dataclass 
class PDFAnalysisResult:
    """Complete PDF formula analysis result"""
    factor_results: Dict[str, FactorResult]
    category_scores: Dict[str, float]
    overall_score: float
    confidence_metrics: Dict[str, float]
    processing_metadata: Dict[str, Any]

class PDFFormulaEngine:
    """
    PDF Formula Engine implementing F1-F28 factor calculations with mathematical precision
    Integrates with existing Validatus services while adding sophisticated analytics
    """
    
    def __init__(self):
        # Initialize GCP settings for enhanced integration
        self.settings = GCPSettings()
        
        self.math_models = MathematicalModels()
        self.quality_analyzer = ContentQualityAnalyzer()
        
        # F1-F28 Factor calculation definitions
        self.factor_calculators = self._initialize_factor_calculators()
        
        logger.info(f"✅ PDF Formula Engine initialized with F1-F28 calculations for project {self.settings.project_id}")
    
    def _initialize_factor_calculators(self) -> Dict[str, callable]:
        """Initialize all F1-F28 factor calculation methods"""
        return {
            # Market Factors (F1-F7)
            'F1_market_size': self._calculate_f1_market_size,
            'F2_market_growth': self._calculate_f2_market_growth,
            'F3_market_maturity': self._calculate_f3_market_maturity,
            'F4_competitive_intensity': self._calculate_f4_competitive_intensity,
            'F5_barrier_to_entry': self._calculate_f5_barrier_to_entry,
            'F6_regulatory_environment': self._calculate_f6_regulatory_environment,
            'F7_economic_sensitivity': self._calculate_f7_economic_sensitivity,
            
            # Product Factors (F8-F14)
            'F8_product_differentiation': self._calculate_f8_product_differentiation,
            'F9_innovation_capability': self._calculate_f9_innovation_capability,
            'F10_quality_reliability': self._calculate_f10_quality_reliability,
            'F11_scalability_potential': self._calculate_f11_scalability_potential,
            'F12_customer_stickiness': self._calculate_f12_customer_stickiness,
            'F13_pricing_power': self._calculate_f13_pricing_power,
            'F14_lifecycle_position': self._calculate_f14_lifecycle_position,
            
            # Financial Factors (F15-F21)
            'F15_revenue_growth': self._calculate_f15_revenue_growth,
            'F16_profitability_margins': self._calculate_f16_profitability_margins,
            'F17_cash_flow_generation': self._calculate_f17_cash_flow_generation,
            'F18_capital_efficiency': self._calculate_f18_capital_efficiency,
            'F19_financial_stability': self._calculate_f19_financial_stability,
            'F20_cost_structure': self._calculate_f20_cost_structure,
            'F21_working_capital': self._calculate_f21_working_capital,
            
            # Strategic Factors (F22-F28)
            'F22_brand_strength': self._calculate_f22_brand_strength,
            'F23_management_quality': self._calculate_f23_management_quality,
            'F24_strategic_positioning': self._calculate_f24_strategic_positioning,
            'F25_operational_excellence': self._calculate_f25_operational_excellence,
            'F26_digital_transformation': self._calculate_f26_digital_transformation,
            'F27_sustainability_esg': self._calculate_f27_sustainability_esg,
            'F28_strategic_flexibility': self._calculate_f28_strategic_flexibility
        }
    
    @performance_monitor
    @with_exponential_backoff(max_retries=3)
    async def calculate_all_factors(self, factor_inputs: List[FactorInput]) -> PDFAnalysisResult:
        """Calculate all F1-F28 factors with enhanced mathematical precision"""
        start_time = datetime.now(timezone.utc)
        logger.info(f"Starting PDF factor calculation for {len(factor_inputs)} inputs")
        
        try:
            # Group inputs by factor for parallel processing
            factor_input_map = {}
            for input_data in factor_inputs:
                if input_data.factor_id not in factor_input_map:
                    factor_input_map[input_data.factor_id] = []
                factor_input_map[input_data.factor_id].append(input_data)
            
            # Calculate factors in parallel
            calculation_tasks = []
            for factor_id, inputs in factor_input_map.items():
                if factor_id in self.factor_calculators:
                    task = self._calculate_single_factor(factor_id, inputs)
                    calculation_tasks.append(task)
            
            factor_results = await asyncio.gather(*calculation_tasks, return_exceptions=True)
            
            # Process results
            final_factor_results = {}
            for i, result in enumerate(factor_results):
                factor_id = list(factor_input_map.keys())[i]
                if isinstance(result, Exception):
                    logger.error(f"Factor {factor_id} calculation failed: {result}")
                    # Create fallback result
                    final_factor_results[factor_id] = self._create_fallback_result(factor_id)
                else:
                    final_factor_results[factor_id] = result
            
            # Calculate category scores
            category_scores = self._calculate_category_scores(final_factor_results)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(final_factor_results, category_scores)
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(final_factor_results)
            
            # Processing metadata
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            processing_metadata = {
                'processing_time': processing_time,
                'factors_calculated': len(final_factor_results),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'engine_version': '1.0.0',
                'mathematical_model': 'logistic_normalization_v1'
            }
            
            result = PDFAnalysisResult(
                factor_results=final_factor_results,
                category_scores=category_scores,
                overall_score=overall_score,
                confidence_metrics=confidence_metrics,
                processing_metadata=processing_metadata
            )
            
            logger.info(f"✅ PDF analysis completed in {processing_time:.2f}s - Overall score: {overall_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"PDF factor calculation failed: {e}")
            raise
    
    async def _calculate_single_factor(self, factor_id: str, inputs: List[FactorInput]) -> FactorResult:
        """Calculate a single factor with enhanced precision"""
        try:
            calculator = self.factor_calculators[factor_id]
            
            # Execute factor calculation
            raw_score, calculation_steps = await calculator(inputs)
            
            # Apply mathematical normalization
            normalized_score = self.math_models.logistic_normalize(raw_score)
            
            # Calculate confidence
            confidence = self._calculate_factor_confidence(inputs, calculation_steps)
            
            # Get factor weight
            weight = self.math_models.factor_weights[factor_id].effective_weight
            
            # Create result
            return FactorResult(
                factor_id=factor_id,
                factor_name=self._get_factor_name(factor_id),
                raw_score=raw_score,
                normalized_score=normalized_score,
                confidence=confidence,
                weight=weight,
                calculation_steps=calculation_steps,
                metadata={
                    'input_count': len(inputs),
                    'calculation_method': 'logistic_normalized',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Single factor calculation failed for {factor_id}: {e}")
            raise
    
    # Individual Factor Calculations (F1-F28)
    
    async def _calculate_f1_market_size(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        """F1: Market Size - Total Addressable Market analysis"""
        calculation_steps = []
        
        # Extract market size data
        tam_values = []
        sam_values = []
        som_values = []
        
        for input_data in inputs:
            raw_data = input_data.raw_data
            tam = raw_data.get('total_addressable_market', 0)
            sam = raw_data.get('serviceable_addressable_market', 0)
            som = raw_data.get('serviceable_obtainable_market', 0)
            
            if tam > 0:
                tam_values.append(tam)
            if sam > 0:
                sam_values.append(sam)
            if som > 0:
                som_values.append(som)
        
        calculation_steps.append({
            'step': 'data_extraction',
            'tam_count': len(tam_values),
            'sam_count': len(sam_values),
            'som_count': len(som_values)
        })
        
        # Calculate market size score using logarithmic scaling
        if tam_values:
            avg_tam = sum(tam_values) / len(tam_values)
            # Log scale normalization (assume $1T = 1.0 score)
            tam_score = min(1.0, math.log10(avg_tam) / 12.0) if avg_tam > 0 else 0.0
        else:
            tam_score = 0.0
        
        # Adjust for market penetration potential
        market_penetration = 0.5  # Default assumption
        for input_data in inputs:
            penetration = input_data.raw_data.get('market_penetration', 0.5)
            market_penetration = max(market_penetration, penetration)
        
        # Market growth multiplier
        growth_multiplier = 1.0
        for input_data in inputs:
            growth_rate = input_data.raw_data.get('market_growth_rate', 0.1)
            growth_mult = 1.0 + min(0.5, growth_rate / 20.0)  # Cap at 2.5% = 1.5x
            growth_multiplier = max(growth_multiplier, growth_mult)
        
        # Final score calculation
        raw_score = tam_score * (1.0 - market_penetration) * growth_multiplier
        
        calculation_steps.append({
            'step': 'score_calculation',
            'tam_score': tam_score,
            'market_penetration': market_penetration,
            'growth_multiplier': growth_multiplier,
            'raw_score': raw_score
        })
        
        return min(1.0, raw_score), calculation_steps
    
    async def _calculate_f2_market_growth(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        """F2: Market Growth Rate analysis"""
        calculation_steps = []
        
        growth_rates = []
        sustainability_scores = []
        
        for input_data in inputs:
            raw_data = input_data.raw_data
            growth_rate = raw_data.get('market_growth_rate', 0.1)
            sustainability = raw_data.get('growth_sustainability', 0.5)
            
            if growth_rate is not None:
                growth_rates.append(growth_rate)
            if sustainability is not None:
                sustainability_scores.append(sustainability)
        
        calculation_steps.append({
            'step': 'data_extraction',
            'growth_rates': growth_rates,
            'sustainability_scores': sustainability_scores
        })
        
        if not growth_rates:
            return 0.5, calculation_steps
        
        # Average growth rate
        avg_growth = sum(growth_rates) / len(growth_rates)
        avg_sustainability = sum(sustainability_scores) / len(sustainability_scores) if sustainability_scores else 0.5
        
        # Sigmoid transformation (10% = 0.5, 30% = ~0.9)
        normalized_growth = 1.0 / (1.0 + math.exp(-0.2 * (avg_growth * 100 - 10)))
        
        # Apply sustainability factor
        raw_score = normalized_growth * avg_sustainability
        
        calculation_steps.append({
            'step': 'score_calculation',
            'avg_growth': avg_growth,
            'avg_sustainability': avg_sustainability,
            'normalized_growth': normalized_growth,
            'raw_score': raw_score
        })
        
        return raw_score, calculation_steps
    
    async def _calculate_f3_market_maturity(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        """F3: Market Maturity Stage analysis"""
        calculation_steps = []
        
        maturity_scores = []
        
        for input_data in inputs:
            raw_data = input_data.raw_data
            maturity_stage = raw_data.get('market_maturity_stage', 2.0)  # Default to growth stage
            
            # Convert maturity stage to score (0-4 scale: embryonic, growth, mature, decline)
            stage_scores = [0.2, 0.8, 0.6, 0.3]  # Growth stage is most attractive
            index = max(0, min(len(stage_scores) - 1, int(maturity_stage)))
            maturity_scores.append(stage_scores[index])
        
        calculation_steps.append({
            'step': 'maturity_analysis',
            'maturity_scores': maturity_scores,
            'avg_maturity': sum(maturity_scores) / len(maturity_scores) if maturity_scores else 0.5
        })
        
        raw_score = sum(maturity_scores) / len(maturity_scores) if maturity_scores else 0.5
        
        return raw_score, calculation_steps
    
    # Simplified implementations for remaining factors (F4-F28) for brevity
    async def _calculate_f4_competitive_intensity(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        """F4: Competitive Intensity analysis"""
        calculation_steps = []
        competitive_factors = []
        
        for input_data in inputs:
            raw_data = input_data.raw_data
            market_concentration = raw_data.get('market_concentration', 0.5)
            competitor_count = raw_data.get('competitor_count', 10)
            price_competition = raw_data.get('price_competition_level', 0.5)
            
            concentration_score = 1.0 - market_concentration
            competitor_score = max(0.2, 1.0 - (competitor_count / 100))
            price_score = 1.0 - price_competition
            
            competitive_score = (concentration_score + competitor_score + price_score) / 3.0
            competitive_factors.append(competitive_score)
        
        calculation_steps.append({'step': 'competitive_analysis', 'competitive_scores': competitive_factors})
        raw_score = sum(competitive_factors) / len(competitive_factors) if competitive_factors else 0.5
        
        return raw_score, calculation_steps
    
    async def _calculate_f5_barrier_to_entry(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        """F5: Barriers to Entry analysis"""
        calculation_steps = []
        barrier_scores = []
        
        for input_data in inputs:
            raw_data = input_data.raw_data
            capital_requirements = raw_data.get('capital_requirements', 0.5)
            regulatory_barriers = raw_data.get('regulatory_barriers', 0.5)
            technology_barriers = raw_data.get('technology_barriers', 0.5)
            brand_barriers = raw_data.get('brand_barriers', 0.5)
            
            barrier_score = (capital_requirements + regulatory_barriers + technology_barriers + brand_barriers) / 4.0
            barrier_scores.append(barrier_score)
        
        calculation_steps.append({'step': 'barrier_analysis', 'barrier_scores': barrier_scores})
        raw_score = sum(barrier_scores) / len(barrier_scores) if barrier_scores else 0.5
        
        return raw_score, calculation_steps
    
    async def _calculate_f6_regulatory_environment(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        """F6: Regulatory Environment analysis"""
        calculation_steps = []
        regulatory_scores = []
        
        for input_data in inputs:
            raw_data = input_data.raw_data
            regulatory_clarity = raw_data.get('regulatory_clarity', 0.5)
            regulatory_stability = raw_data.get('regulatory_stability', 0.5)
            compliance_cost = raw_data.get('compliance_cost', 0.5)
            
            compliance_score = 1.0 - compliance_cost
            regulatory_score = (regulatory_clarity + regulatory_stability + compliance_score) / 3.0
            regulatory_scores.append(regulatory_score)
        
        calculation_steps.append({'step': 'regulatory_analysis', 'regulatory_scores': regulatory_scores})
        raw_score = sum(regulatory_scores) / len(regulatory_scores) if regulatory_scores else 0.5
        
        return raw_score, calculation_steps
    
    async def _calculate_f7_economic_sensitivity(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        """F7: Economic Sensitivity analysis"""
        calculation_steps = []
        sensitivity_scores = []
        
        for input_data in inputs:
            raw_data = input_data.raw_data
            recession_resilience = raw_data.get('recession_resilience', 0.5)
            income_elasticity = raw_data.get('income_elasticity', 0.5)
            cyclical_dependency = raw_data.get('cyclical_dependency', 0.5)
            
            income_score = 1.0 - income_elasticity
            cyclical_score = 1.0 - cyclical_dependency
            
            sensitivity_score = (recession_resilience + income_score + cyclical_score) / 3.0
            sensitivity_scores.append(sensitivity_score)
        
        calculation_steps.append({'step': 'sensitivity_analysis', 'sensitivity_scores': sensitivity_scores})
        raw_score = sum(sensitivity_scores) / len(sensitivity_scores) if sensitivity_scores else 0.5
        
        return raw_score, calculation_steps
    
    # Product Factors (F8-F14) - Simplified implementations
    async def _calculate_f8_product_differentiation(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        differentiation_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            differentiation = raw_data.get('product_differentiation', 0.5)
            differentiation_scores.append(differentiation)
        
        raw_score = sum(differentiation_scores) / len(differentiation_scores) if differentiation_scores else 0.5
        calculation_steps.append({'step': 'differentiation_analysis', 'scores': differentiation_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f9_innovation_capability(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        innovation_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            innovation = raw_data.get('innovation_capability', 0.5)
            innovation_scores.append(innovation)
        
        raw_score = sum(innovation_scores) / len(innovation_scores) if innovation_scores else 0.5
        calculation_steps.append({'step': 'innovation_analysis', 'scores': innovation_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f10_quality_reliability(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        quality_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            quality = raw_data.get('quality_reliability', 0.5)
            quality_scores.append(quality)
        
        raw_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
        calculation_steps.append({'step': 'quality_analysis', 'scores': quality_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f11_scalability_potential(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        scalability_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            scalability = raw_data.get('scalability_potential', 0.5)
            scalability_scores.append(scalability)
        
        raw_score = sum(scalability_scores) / len(scalability_scores) if scalability_scores else 0.5
        calculation_steps.append({'step': 'scalability_analysis', 'scores': scalability_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f12_customer_stickiness(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        stickiness_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            stickiness = raw_data.get('customer_stickiness', 0.5)
            stickiness_scores.append(stickiness)
        
        raw_score = sum(stickiness_scores) / len(stickiness_scores) if stickiness_scores else 0.5
        calculation_steps.append({'step': 'stickiness_analysis', 'scores': stickiness_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f13_pricing_power(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        pricing_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            pricing_power = raw_data.get('pricing_power', 0.5)
            pricing_scores.append(pricing_power)
        
        raw_score = sum(pricing_scores) / len(pricing_scores) if pricing_scores else 0.5
        calculation_steps.append({'step': 'pricing_analysis', 'scores': pricing_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f14_lifecycle_position(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        lifecycle_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            lifecycle_position = raw_data.get('lifecycle_position', 0.5)
            lifecycle_scores.append(lifecycle_position)
        
        raw_score = sum(lifecycle_scores) / len(lifecycle_scores) if lifecycle_scores else 0.5
        calculation_steps.append({'step': 'lifecycle_analysis', 'scores': lifecycle_scores})
        return raw_score, calculation_steps
    
    # Financial Factors (F15-F21) - Simplified implementations
    async def _calculate_f15_revenue_growth(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        growth_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            revenue_growth = raw_data.get('revenue_growth_rate', 0.1)
            normalized_growth = min(1.0, max(0.0, revenue_growth / 0.5))
            growth_scores.append(normalized_growth)
        
        raw_score = sum(growth_scores) / len(growth_scores) if growth_scores else 0.5
        calculation_steps.append({'step': 'growth_analysis', 'scores': growth_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f16_profitability_margins(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        margin_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            profit_margin = raw_data.get('profit_margin', 0.1)
            normalized_margin = min(1.0, max(0.0, profit_margin / 0.2))
            margin_scores.append(normalized_margin)
        
        raw_score = sum(margin_scores) / len(margin_scores) if margin_scores else 0.5
        calculation_steps.append({'step': 'margin_analysis', 'scores': margin_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f17_cash_flow_generation(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        cashflow_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            cashflow = raw_data.get('cash_flow_quality', 0.5)
            cashflow_scores.append(cashflow)
        
        raw_score = sum(cashflow_scores) / len(cashflow_scores) if cashflow_scores else 0.5
        calculation_steps.append({'step': 'cashflow_analysis', 'scores': cashflow_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f18_capital_efficiency(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        efficiency_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            efficiency = raw_data.get('capital_efficiency', 0.5)
            efficiency_scores.append(efficiency)
        
        raw_score = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0.5
        calculation_steps.append({'step': 'efficiency_analysis', 'scores': efficiency_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f19_financial_stability(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        stability_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            stability = raw_data.get('financial_stability', 0.5)
            stability_scores.append(stability)
        
        raw_score = sum(stability_scores) / len(stability_scores) if stability_scores else 0.5
        calculation_steps.append({'step': 'stability_analysis', 'scores': stability_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f20_cost_structure(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        cost_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            cost_efficiency = raw_data.get('cost_efficiency', 0.5)
            cost_scores.append(cost_efficiency)
        
        raw_score = sum(cost_scores) / len(cost_scores) if cost_scores else 0.5
        calculation_steps.append({'step': 'cost_analysis', 'scores': cost_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f21_working_capital(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        working_capital_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            working_capital = raw_data.get('working_capital_efficiency', 0.5)
            working_capital_scores.append(working_capital)
        
        raw_score = sum(working_capital_scores) / len(working_capital_scores) if working_capital_scores else 0.5
        calculation_steps.append({'step': 'working_capital_analysis', 'scores': working_capital_scores})
        return raw_score, calculation_steps
    
    # Strategic Factors (F22-F28) - Detailed implementation for key factors
    async def _calculate_f22_brand_strength(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        """F22: Brand Strength analysis"""
        calculation_steps = []
        
        brand_metrics = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            
            # Brand strength indicators
            brand_recognition = raw_data.get('brand_recognition', 0.5)
            customer_loyalty = raw_data.get('customer_loyalty', 0.5)
            brand_equity = raw_data.get('brand_equity_value', 0.5)
            market_share = raw_data.get('market_share', 0.1)
            
            brand_score = (
                brand_recognition * 0.3 +
                customer_loyalty * 0.3 + 
                brand_equity * 0.2 +
                min(1.0, market_share * 5) * 0.2  # Scale market share
            )
            
            brand_metrics.append(brand_score)
        
        calculation_steps.append({
            'step': 'brand_metrics_calculation',
            'metrics_count': len(brand_metrics)
        })
        
        if not brand_metrics:
            return 0.5, calculation_steps
        
        avg_brand_score = sum(brand_metrics) / len(brand_metrics)
        
        calculation_steps.append({
            'step': 'final_calculation',
            'avg_brand_score': avg_brand_score
        })
        
        return avg_brand_score, calculation_steps
    
    # Simplified implementations for remaining strategic factors
    async def _calculate_f23_management_quality(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        management_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            management_quality = raw_data.get('management_quality', 0.5)
            management_scores.append(management_quality)
        
        raw_score = sum(management_scores) / len(management_scores) if management_scores else 0.5
        calculation_steps.append({'step': 'management_analysis', 'scores': management_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f24_strategic_positioning(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        positioning_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            strategic_position = raw_data.get('strategic_positioning', 0.5)
            positioning_scores.append(strategic_position)
        
        raw_score = sum(positioning_scores) / len(positioning_scores) if positioning_scores else 0.5
        calculation_steps.append({'step': 'positioning_analysis', 'scores': positioning_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f25_operational_excellence(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        operational_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            operational_excellence = raw_data.get('operational_excellence', 0.5)
            operational_scores.append(operational_excellence)
        
        raw_score = sum(operational_scores) / len(operational_scores) if operational_scores else 0.5
        calculation_steps.append({'step': 'operational_analysis', 'scores': operational_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f26_digital_transformation(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        digital_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            digital_maturity = raw_data.get('digital_maturity', 0.5)
            digital_scores.append(digital_maturity)
        
        raw_score = sum(digital_scores) / len(digital_scores) if digital_scores else 0.5
        calculation_steps.append({'step': 'digital_analysis', 'scores': digital_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f27_sustainability_esg(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        esg_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            esg_score = raw_data.get('esg_score', 0.5)
            esg_scores.append(esg_score)
        
        raw_score = sum(esg_scores) / len(esg_scores) if esg_scores else 0.5
        calculation_steps.append({'step': 'esg_analysis', 'scores': esg_scores})
        return raw_score, calculation_steps
    
    async def _calculate_f28_strategic_flexibility(self, inputs: List[FactorInput]) -> Tuple[float, List[Dict[str, Any]]]:
        calculation_steps = []
        flexibility_scores = []
        for input_data in inputs:
            raw_data = input_data.raw_data
            strategic_flexibility = raw_data.get('strategic_flexibility', 0.5)
            flexibility_scores.append(strategic_flexibility)
        
        raw_score = sum(flexibility_scores) / len(flexibility_scores) if flexibility_scores else 0.5
        calculation_steps.append({'step': 'flexibility_analysis', 'scores': flexibility_scores})
        return raw_score, calculation_steps
    
    # Helper methods
    
    def _calculate_factor_confidence(self, inputs: List[FactorInput], calculation_steps: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for factor result"""
        if not inputs:
            return 0.1
        
        # Base confidence from input quality
        input_confidences = [inp.confidence for inp in inputs]
        avg_input_confidence = sum(input_confidences) / len(input_confidences)
        
        # Adjust based on data completeness
        data_completeness = len([inp for inp in inputs if inp.raw_data]) / len(inputs)
        
        # Adjust based on calculation complexity
        calculation_complexity = len(calculation_steps)
        complexity_bonus = min(0.1, calculation_complexity * 0.02)
        
        final_confidence = (avg_input_confidence * 0.7 + 
                           data_completeness * 0.2 + 
                           complexity_bonus)
        
        return max(0.1, min(1.0, final_confidence))
    
    def _calculate_category_scores(self, factor_results: Dict[str, FactorResult]) -> Dict[str, float]:
        """Calculate weighted category scores"""
        categories = {
            'market': self.math_models._get_category_factors('market'),
            'product': self.math_models._get_category_factors('product'),
            'financial': self.math_models._get_category_factors('financial'),
            'strategic': self.math_models._get_category_factors('strategic')
        }
        
        category_scores = {}
        for category, factor_ids in categories.items():
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for factor_id in factor_ids:
                if factor_id in factor_results:
                    result = factor_results[factor_id]
                    total_weighted_score += result.weighted_score
                    total_weight += result.weight
            
            category_scores[category] = (total_weighted_score / total_weight) if total_weight > 0 else 0.5
        
        return category_scores
    
    def _calculate_overall_score(self, factor_results: Dict[str, FactorResult], category_scores: Dict[str, float]) -> float:
        """Calculate overall weighted score"""
        # Category weights for overall score
        category_weights = {
            'market': 0.25,
            'product': 0.25, 
            'financial': 0.25,
            'strategic': 0.25
        }
        
        overall_score = sum(category_scores[cat] * weight 
                           for cat, weight in category_weights.items() 
                           if cat in category_scores)
        
        return overall_score
    
    def _calculate_confidence_metrics(self, factor_results: Dict[str, FactorResult]) -> Dict[str, float]:
        """Calculate comprehensive confidence metrics"""
        if not factor_results:
            return {'overall_confidence': 0.1}
        
        confidences = [result.confidence for result in factor_results.values()]
        
        return {
            'overall_confidence': sum(confidences) / len(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'confidence_std': np.std(confidences) if len(confidences) > 1 else 0.0
        }
    
    def _get_factor_name(self, factor_id: str) -> str:
        """Get human-readable factor name"""
        factor_names = {
            'F1_market_size': 'Total Addressable Market Size',
            'F2_market_growth': 'Market Growth Rate',
            'F3_market_maturity': 'Market Maturity Stage',
            'F4_competitive_intensity': 'Competitive Intensity',
            'F5_barrier_to_entry': 'Barriers to Entry',
            'F6_regulatory_environment': 'Regulatory Environment',
            'F7_economic_sensitivity': 'Economic Sensitivity',
            'F8_product_differentiation': 'Product Differentiation',
            'F9_innovation_capability': 'Innovation Capability',
            'F10_quality_reliability': 'Quality & Reliability',
            'F11_scalability_potential': 'Scalability Potential',
            'F12_customer_stickiness': 'Customer Stickiness',
            'F13_pricing_power': 'Pricing Power',
            'F14_lifecycle_position': 'Product Lifecycle Position',
            'F15_revenue_growth': 'Revenue Growth',
            'F16_profitability_margins': 'Profitability Margins',
            'F17_cash_flow_generation': 'Cash Flow Generation',
            'F18_capital_efficiency': 'Capital Efficiency',
            'F19_financial_stability': 'Financial Stability',
            'F20_cost_structure': 'Cost Structure Optimization',
            'F21_working_capital': 'Working Capital Management',
            'F22_brand_strength': 'Brand Strength',
            'F23_management_quality': 'Management Quality',
            'F24_strategic_positioning': 'Strategic Positioning',
            'F25_operational_excellence': 'Operational Excellence',
            'F26_digital_transformation': 'Digital Transformation',
            'F27_sustainability_esg': 'Sustainability & ESG',
            'F28_strategic_flexibility': 'Strategic Flexibility'
        }
        return factor_names.get(factor_id, factor_id)
    
    def _create_fallback_result(self, factor_id: str) -> FactorResult:
        """Create fallback result for failed calculations"""
        return FactorResult(
            factor_id=factor_id,
            factor_name=self._get_factor_name(factor_id),
            raw_score=0.5,
            normalized_score=0.5,
            confidence=0.1,
            weight=self.math_models.factor_weights[factor_id].effective_weight,
            calculation_steps=[{'error': 'Calculation failed - using fallback'}],
            metadata={'status': 'fallback', 'timestamp': datetime.now(timezone.utc).isoformat()}
        )

__all__ = ['PDFFormulaEngine', 'FactorInput', 'FactorResult', 'PDFAnalysisResult']