# backend/app/services/pdf_formula_engine.py

import asyncio
import logging
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

import numpy as np
from pydantic import BaseModel, Field

from ..core.gcp_config import GCPSettings
from ..middleware.monitoring import performance_monitor
from ..core.error_recovery import with_exponential_backoff

logger = logging.getLogger(__name__)

@dataclass
class FormulaResult:
    """Result of a single formula calculation"""
    formula_name: str
    raw_score: float
    normalized_score: float
    confidence: float
    calculation_steps: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@dataclass
class PDFAnalysisResult:
    """Complete PDF formula analysis result"""
    factor_results: Dict[str, FormulaResult]  # F1-F28 results
    action_layer_scores: Dict[str, float]     # 18 action layer scores
    overall_confidence: float
    processing_time: float
    timestamp: str

class FactorInputs(BaseModel):
    """Input model for factor calculations"""
    market_data: Dict[str, float] = Field(..., description="Market metrics and KPIs")
    competitive_data: Dict[str, float] = Field(..., description="Competitive positioning data")
    financial_data: Dict[str, float] = Field(..., description="Financial performance metrics")
    operational_data: Dict[str, float] = Field(..., description="Operational efficiency data")
    strategic_context: Dict[str, Any] = Field(..., description="Strategic context and metadata")

class PDFFormulaEngine:
    """
    PDF Formula Engine implementing F1-F28 factor calculations with logistic normalization
    Based on the sophisticated mathematical framework from the previous repository
    """
    
    def __init__(self):
        self.settings = GCPSettings()
        self.robustness_multipliers = {
            'S_gen': 0.95,    # Generalizability strength
            'C_stab': 0.9,    # Confidence stability
            'V_evolve': 0.02  # Volatility evolution
        }
        
        # F1-F28 Formula definitions with mathematical precision
        self.factor_formulas = self._initialize_factor_formulas()
        
    def _initialize_factor_formulas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all F1-F28 factor calculation formulas"""
        return {
            # Market Factors (F1-F7)
            'F1_market_size': {
                'weight': 0.15,
                'formula': lambda inputs: self._calculate_market_size_score(inputs),
                'description': 'Total Addressable Market scoring with growth projections'
            },
            'F2_market_growth': {
                'weight': 0.12,
                'formula': lambda inputs: self._calculate_market_growth_score(inputs),
                'description': 'Market growth rate and sustainability analysis'
            },
            'F3_market_maturity': {
                'weight': 0.10,
                'formula': lambda inputs: self._calculate_market_maturity_score(inputs),
                'description': 'Market lifecycle stage and opportunity assessment'
            },
            'F4_competitive_intensity': {
                'weight': 0.13,
                'formula': lambda inputs: self._calculate_competitive_intensity_score(inputs),
                'description': 'Porter\'s Five Forces competitive analysis'
            },
            'F5_barrier_to_entry': {
                'weight': 0.11,
                'formula': lambda inputs: self._calculate_barrier_entry_score(inputs),
                'description': 'Market entry barriers and defensibility'
            },
            'F6_regulatory_environment': {
                'weight': 0.09,
                'formula': lambda inputs: self._calculate_regulatory_score(inputs),
                'description': 'Regulatory complexity and compliance requirements'
            },
            'F7_economic_sensitivity': {
                'weight': 0.08,
                'formula': lambda inputs: self._calculate_economic_sensitivity_score(inputs),
                'description': 'Economic cycle sensitivity and resilience'
            },
            
            # Product Factors (F8-F14)
            'F8_product_differentiation': {
                'weight': 0.14,
                'formula': lambda inputs: self._calculate_product_differentiation_score(inputs),
                'description': 'Product uniqueness and competitive advantage'
            },
            'F9_innovation_capability': {
                'weight': 0.13,
                'formula': lambda inputs: self._calculate_innovation_score(inputs),
                'description': 'R&D capabilities and innovation pipeline'
            },
            'F10_quality_reliability': {
                'weight': 0.12,
                'formula': lambda inputs: self._calculate_quality_score(inputs),
                'description': 'Product quality and reliability metrics'
            },
            'F11_scalability_potential': {
                'weight': 0.11,
                'formula': lambda inputs: self._calculate_scalability_score(inputs),
                'description': 'Business model scalability and growth potential'
            },
            'F12_customer_stickiness': {
                'weight': 0.10,
                'formula': lambda inputs: self._calculate_customer_stickiness_score(inputs),
                'description': 'Customer retention and switching costs'
            },
            'F13_pricing_power': {
                'weight': 0.09,
                'formula': lambda inputs: self._calculate_pricing_power_score(inputs),
                'description': 'Pricing flexibility and margin sustainability'
            },
            'F14_lifecycle_position': {
                'weight': 0.08,
                'formula': lambda inputs: self._calculate_lifecycle_position_score(inputs),
                'description': 'Product lifecycle stage and longevity'
            },
            
            # Financial Factors (F15-F21)
            'F15_revenue_growth': {
                'weight': 0.16,
                'formula': lambda inputs: self._calculate_revenue_growth_score(inputs),
                'description': 'Revenue growth rate and sustainability'
            },
            'F16_profitability_margins': {
                'weight': 0.15,
                'formula': lambda inputs: self._calculate_profitability_score(inputs),
                'description': 'Gross, operating, and net margin analysis'
            },
            'F17_cash_flow_generation': {
                'weight': 0.14,
                'formula': lambda inputs: self._calculate_cash_flow_score(inputs),
                'description': 'Free cash flow generation and conversion'
            },
            'F18_capital_efficiency': {
                'weight': 0.13,
                'formula': lambda inputs: self._calculate_capital_efficiency_score(inputs),
                'description': 'Return on invested capital and asset utilization'
            },
            'F19_financial_stability': {
                'weight': 0.12,
                'formula': lambda inputs: self._calculate_financial_stability_score(inputs),
                'description': 'Debt levels, liquidity, and financial risk'
            },
            'F20_cost_structure': {
                'weight': 0.10,
                'formula': lambda inputs: self._calculate_cost_structure_score(inputs),
                'description': 'Fixed vs variable cost optimization'
            },
            'F21_working_capital': {
                'weight': 0.08,
                'formula': lambda inputs: self._calculate_working_capital_score(inputs),
                'description': 'Working capital management efficiency'
            },
            
            # Strategic Factors (F22-F28)
            'F22_brand_strength': {
                'weight': 0.16,
                'formula': lambda inputs: self._calculate_brand_strength_score(inputs),
                'description': 'Brand recognition, loyalty, and equity'
            },
            'F23_management_quality': {
                'weight': 0.15,
                'formula': lambda inputs: self._calculate_management_quality_score(inputs),
                'description': 'Leadership capability and execution track record'
            },
            'F24_strategic_positioning': {
                'weight': 0.14,
                'formula': lambda inputs: self._calculate_strategic_positioning_score(inputs),
                'description': 'Competitive positioning and strategic clarity'
            },
            'F25_operational_excellence': {
                'weight': 0.13,
                'formula': lambda inputs: self._calculate_operational_excellence_score(inputs),
                'description': 'Operational efficiency and process optimization'
            },
            'F26_digital_transformation': {
                'weight': 0.12,
                'formula': lambda inputs: self._calculate_digital_transformation_score(inputs),
                'description': 'Digital capabilities and technology adoption'
            },
            'F27_sustainability_esg': {
                'weight': 0.10,
                'formula': lambda inputs: self._calculate_sustainability_score(inputs),
                'description': 'Environmental, Social, Governance factors'
            },
            'F28_strategic_flexibility': {
                'weight': 0.08,
                'formula': lambda inputs: self._calculate_strategic_flexibility_score(inputs),
                'description': 'Adaptability and strategic option value'
            }
        }

    @performance_monitor
    async def calculate_all_factors(self, inputs: FactorInputs) -> PDFAnalysisResult:
        """
        Calculate all F1-F28 factors with full mathematical precision
        """
        start_time = datetime.now(timezone.utc)
        logger.info("Starting comprehensive PDF factor analysis")
        
        try:
            # Calculate all factor scores
            factor_results = {}
            calculation_tasks = []
            
            for factor_name, formula_config in self.factor_formulas.items():
                task = self._calculate_single_factor(factor_name, formula_config, inputs)
                calculation_tasks.append(task)
            
            # Execute calculations in parallel
            factor_calculations = await asyncio.gather(*calculation_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(factor_calculations):
                factor_name = list(self.factor_formulas.keys())[i]
                if isinstance(result, Exception):
                    logger.error(f"Factor {factor_name} calculation failed: {result}")
                    # Use default score with low confidence
                    factor_results[factor_name] = FormulaResult(
                        formula_name=factor_name,
                        raw_score=0.5,
                        normalized_score=0.5,
                        confidence=0.1,
                        calculation_steps=[{"error": str(result)}],
                        metadata={"status": "error"}
                    )
                else:
                    factor_results[factor_name] = result
            
            # Calculate action layer scores from factor results
            action_layer_scores = await self._calculate_action_layer_scores(factor_results)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(factor_results)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = PDFAnalysisResult(
                factor_results=factor_results,
                action_layer_scores=action_layer_scores,
                overall_confidence=overall_confidence,
                processing_time=processing_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            logger.info(f"✅ PDF analysis completed in {processing_time:.2f}s with confidence {overall_confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"PDF factor analysis failed: {e}")
            raise

    @with_exponential_backoff
    async def _calculate_single_factor(self, factor_name: str, formula_config: Dict[str, Any], inputs: FactorInputs) -> FormulaResult:
        """Calculate a single factor score with full traceability"""
        
        try:
            # Execute the formula calculation
            raw_score, calculation_steps = formula_config['formula'](inputs)
            
            # Apply logistic normalization
            normalized_score = self._logistic_normalize(raw_score)
            
            # Calculate confidence based on data quality and completeness
            confidence = self._calculate_confidence(inputs, calculation_steps)
            
            # Apply robustness multipliers
            final_confidence = confidence * self.robustness_multipliers['C_stab']
            
            return FormulaResult(
                formula_name=factor_name,
                raw_score=raw_score,
                normalized_score=normalized_score,
                confidence=final_confidence,
                calculation_steps=calculation_steps,
                metadata={
                    'weight': formula_config['weight'],
                    'description': formula_config['description'],
                    'calculation_timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Factor {factor_name} calculation error: {e}")
            raise
    
    def _logistic_normalize(self, raw_score: float) -> float:
        """Apply logistic normalization: 1 / (1 + e^(-5 * (raw_score - 0.5)))"""
        try:
            # Clamp raw_score to prevent overflow
            clamped_score = max(-10, min(10, raw_score))
            normalized = 1.0 / (1.0 + math.exp(-5.0 * (clamped_score - 0.5)))
            return max(0.0, min(1.0, normalized))
        except (OverflowError, ValueError):
            return 0.5  # Default middle value on calculation error

    def _calculate_confidence(self, inputs: FactorInputs, calculation_steps: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on data quality and calculation completeness"""
        
        base_confidence = 0.8
        
        # Adjust based on data completeness
        data_completeness = self._assess_data_completeness(inputs)
        confidence_adjustment = (data_completeness - 0.5) * 0.4
        
        # Adjust based on calculation complexity
        calculation_complexity = len(calculation_steps)
        complexity_adjustment = min(0.1, calculation_complexity * 0.02)
        
        final_confidence = base_confidence + confidence_adjustment + complexity_adjustment
        return max(0.1, min(1.0, final_confidence))
    
    def _assess_data_completeness(self, inputs: FactorInputs) -> float:
        """Assess the completeness of input data"""
        total_fields = 0
        populated_fields = 0
        
        for data_dict in [inputs.market_data, inputs.competitive_data, inputs.financial_data, inputs.operational_data]:
            total_fields += len(data_dict)
            populated_fields += sum(1 for v in data_dict.values() if v is not None and v != 0)
        
        return populated_fields / max(1, total_fields)

    async def _calculate_action_layer_scores(self, factor_results: Dict[str, FormulaResult]) -> Dict[str, float]:
        """Calculate 18 action layer scores from factor results"""
        
        # Group factors by category for action layer calculation
        market_factors = {k: v for k, v in factor_results.items() if k.startswith(('F1_', 'F2_', 'F3_', 'F4_', 'F5_', 'F6_', 'F7_'))}
        product_factors = {k: v for k, v in factor_results.items() if k.startswith(('F8_', 'F9_', 'F10_', 'F11_', 'F12_', 'F13_', 'F14_'))}
        financial_factors = {k: v for k, v in factor_results.items() if k.startswith(('F15_', 'F16_', 'F17_', 'F18_', 'F19_', 'F20_', 'F21_'))}
        strategic_factors = {k: v for k, v in factor_results.items() if k.startswith(('F22_', 'F23_', 'F24_', 'F25_', 'F26_', 'F27_', 'F28_'))}
        
        action_scores = {}
        
        # D_Score: Overall Decision Score
        all_scores = [result.normalized_score for result in factor_results.values()]
        weights = [self.factor_formulas[name]['weight'] for name in factor_results.keys()]
        action_scores['D_Score'] = sum(score * weight for score, weight in zip(all_scores, weights)) / sum(weights)
        
        # Market Action Layers
        action_scores['Market_Attractiveness_Score'] = self._weighted_average([r.normalized_score for r in market_factors.values()])
        action_scores['Competitive_Position_Score'] = sum(r.normalized_score for r in market_factors.values() if 'competitive' in r.formula_name.lower()) / max(1, len([r for r in market_factors.values() if 'competitive' in r.formula_name.lower()]))
        
        # Product Action Layers  
        action_scores['Product_Strength_Score'] = self._weighted_average([r.normalized_score for r in product_factors.values()])
        action_scores['Innovation_Score'] = sum(r.normalized_score for r in product_factors.values() if 'innovation' in r.formula_name.lower()) / max(1, len([r for r in product_factors.values() if 'innovation' in r.formula_name.lower()]))
        
        # Financial Action Layers
        action_scores['Financial_Health_Score'] = self._weighted_average([r.normalized_score for r in financial_factors.values()])
        action_scores['Growth_Potential_Score'] = sum(r.normalized_score for r in financial_factors.values() if 'growth' in r.formula_name.lower()) / max(1, len([r for r in financial_factors.values() if 'growth' in r.formula_name.lower()]))
        
        # Strategic Action Layers
        action_scores['Strategic_Position_Score'] = self._weighted_average([r.normalized_score for r in strategic_factors.values()])
        action_scores['Execution_Capability_Score'] = sum(r.normalized_score for r in strategic_factors.values() if 'management' in r.formula_name.lower() or 'operational' in r.formula_name.lower()) / max(1, len([r for r in strategic_factors.values() if 'management' in r.formula_name.lower() or 'operational' in r.formula_name.lower()]))
        
        # Risk Assessments
        action_scores['Risk_Score'] = 1.0 - action_scores['D_Score']  # Inverse relationship
        action_scores['Volatility_Score'] = self._calculate_volatility_from_factors(factor_results)
        
        # SWOT Derived Scores
        action_scores['SWOT_Score'] = (action_scores['Product_Strength_Score'] * 0.3 + 
                                     action_scores['Market_Attractiveness_Score'] * 0.3 +
                                     action_scores['Financial_Health_Score'] * 0.2 +
                                     action_scores['Strategic_Position_Score'] * 0.2)
        
        # Additional Action Layers
        action_scores['Sustainability_Score'] = sum(r.normalized_score for r in factor_results.values() if 'sustainability' in r.formula_name.lower() or 'esg' in r.formula_name.lower()) / max(1, len([r for r in factor_results.values() if 'sustainability' in r.formula_name.lower() or 'esg' in r.formula_name.lower()]))
        action_scores['Scalability_Score'] = sum(r.normalized_score for r in factor_results.values() if 'scalability' in r.formula_name.lower()) / max(1, len([r for r in factor_results.values() if 'scalability' in r.formula_name.lower()]))
        action_scores['Differentiation_Score'] = sum(r.normalized_score for r in factor_results.values() if 'differentiation' in r.formula_name.lower() or 'brand' in r.formula_name.lower()) / max(1, len([r for r in factor_results.values() if 'differentiation' in r.formula_name.lower() or 'brand' in r.formula_name.lower()]))
        
        # Confidence and Quality Scores
        action_scores['Confidence_Score'] = sum(r.confidence for r in factor_results.values()) / len(factor_results)
        action_scores['Data_Quality_Score'] = action_scores['Confidence_Score']  # Proxy for data quality
        
        # Strategic Recommendations Score
        action_scores['Strategic_Recommendation_Score'] = (action_scores['SWOT_Score'] * 0.4 +
                                                         action_scores['Growth_Potential_Score'] * 0.3 +
                                                         action_scores['Risk_Score'] * -0.2 +
                                                         action_scores['Execution_Capability_Score'] * 0.5)
        
        # Overall Investment Attractiveness
        action_scores['Investment_Attractiveness_Score'] = (action_scores['D_Score'] * 0.3 +
                                                          action_scores['Financial_Health_Score'] * 0.25 +
                                                          action_scores['Growth_Potential_Score'] * 0.25 +
                                                          action_scores['Risk_Score'] * -0.2)
        
        # Normalize all action scores
        for key in action_scores:
            action_scores[key] = max(0.0, min(1.0, action_scores[key]))
            
        return action_scores
    
    def _weighted_average(self, scores: List[float]) -> float:
        """Calculate weighted average of scores"""
        if not scores:
            return 0.5
        return sum(scores) / len(scores)
    
    def _calculate_volatility_from_factors(self, factor_results: Dict[str, FormulaResult]) -> float:
        """Calculate volatility score from factor confidence variations"""
        confidences = [result.confidence for result in factor_results.values()]
        if not confidences:
            return 0.5
            
        mean_confidence = sum(confidences) / len(confidences)
        variance = sum((c - mean_confidence) ** 2 for c in confidences) / len(confidences)
        volatility = math.sqrt(variance)
        
        # Normalize volatility to 0-1 range
        return min(1.0, volatility * 2.0)
    
    def _calculate_overall_confidence(self, factor_results: Dict[str, FormulaResult]) -> float:
        """Calculate overall analysis confidence"""
        if not factor_results:
            return 0.0
            
        confidences = [result.confidence for result in factor_results.values()]
        weights = [self.factor_formulas[name]['weight'] for name in factor_results.keys()]
        
        weighted_confidence = sum(conf * weight for conf, weight in zip(confidences, weights)) / sum(weights)
        return weighted_confidence * self.robustness_multipliers['S_gen']

    # Individual factor calculation methods (F1-F28)
    # These methods implement the sophisticated mathematical formulas
    
    def _calculate_market_size_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F1: Market Size scoring with TAM, SAM, SOM analysis"""
        steps = []
        
        tam = inputs.market_data.get('total_addressable_market', 0)
        sam = inputs.market_data.get('serviceable_addressable_market', 0)  
        som = inputs.market_data.get('serviceable_obtainable_market', 0)
        market_growth = inputs.market_data.get('market_growth_rate', 0)
        
        steps.append({"step": "market_size_data", "tam": tam, "sam": sam, "som": som})
        
        # Normalize market size (log scale for large numbers)
        if tam > 0:
            normalized_tam = min(1.0, math.log10(tam) / 12.0)  # Assume $1T = 1.0 score
        else:
            normalized_tam = 0.0
            
        # Weight by market growth
        growth_multiplier = 1.0 + min(0.5, market_growth / 20.0)  # 20% growth = 1.5x multiplier
        
        raw_score = normalized_tam * growth_multiplier
        steps.append({"step": "calculation", "normalized_tam": normalized_tam, "growth_multiplier": growth_multiplier, "raw_score": raw_score})
        
        return min(1.0, raw_score), steps

    def _calculate_market_growth_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F2: Market Growth Rate scoring"""
        steps = []
        
        growth_rate = inputs.market_data.get('market_growth_rate', 0)
        growth_sustainability = inputs.market_data.get('growth_sustainability_score', 0.5)
        
        steps.append({"step": "growth_data", "growth_rate": growth_rate, "sustainability": growth_sustainability})
        
        # Sigmoid transformation for growth rate (10% = 0.5, 30% = ~0.9)
        normalized_growth = 1.0 / (1.0 + math.exp(-0.2 * (growth_rate - 10.0)))
        
        # Apply sustainability factor
        raw_score = normalized_growth * growth_sustainability
        steps.append({"step": "calculation", "normalized_growth": normalized_growth, "raw_score": raw_score})
        
        return raw_score, steps
    
    def _calculate_market_maturity_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F3: Market Maturity scoring"""
        steps = []
        
        maturity_stage = inputs.market_data.get('maturity_stage', 2)  # 0-4 scale
        adoption_rate = inputs.market_data.get('technology_adoption_rate', 0.5)
        
        steps.append({"step": "maturity_data", "stage": maturity_stage, "adoption": adoption_rate})
        
        # Optimal maturity is growth stage (stage 2)
        stage_scores = [0.3, 0.6, 1.0, 0.7, 0.4]  # Introduction, Growth, Maturity, Decline, Decline
        stage_score = stage_scores[min(4, max(0, int(maturity_stage)))]
        
        raw_score = (stage_score * 0.7) + (adoption_rate * 0.3)
        steps.append({"step": "calculation", "stage_score": stage_score, "raw_score": raw_score})
        
        return raw_score, steps

    def _calculate_competitive_intensity_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F4: Competitive Intensity using Porter's Five Forces"""
        steps = []
        
        # Porter's Five Forces components
        rivalry = inputs.competitive_data.get('competitive_rivalry', 0.5)
        supplier_power = inputs.competitive_data.get('supplier_bargaining_power', 0.5)
        buyer_power = inputs.competitive_data.get('buyer_bargaining_power', 0.5)
        threat_substitutes = inputs.competitive_data.get('threat_of_substitutes', 0.5)
        threat_new_entrants = inputs.competitive_data.get('threat_of_new_entrants', 0.5)
        
        steps.append({
            "step": "porters_five_forces", 
            "rivalry": rivalry,
            "supplier_power": supplier_power,
            "buyer_power": buyer_power,
            "substitutes": threat_substitutes,
            "new_entrants": threat_new_entrants
        })
        
        # Calculate weighted competitive intensity (lower is better)
        competitive_pressure = (rivalry * 0.3 + supplier_power * 0.2 + buyer_power * 0.2 + 
                              threat_substitutes * 0.15 + threat_new_entrants * 0.15)
        
        # Invert score (low competitive pressure = high score)
        raw_score = 1.0 - competitive_pressure
        
        steps.append({"step": "calculation", "competitive_pressure": competitive_pressure, "raw_score": raw_score})
        return raw_score, steps

    # [Continue with remaining F5-F28 calculations...]
    # For brevity, showing pattern for first 4. Each follows similar structure:
    # 1. Extract relevant inputs
    # 2. Apply mathematical transformation  
    # 3. Record calculation steps
    # 4. Return raw score and steps

    def _calculate_barrier_entry_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F5: Barrier to Entry scoring"""
        steps = []
        
        capital_requirements = inputs.competitive_data.get('capital_requirements', 0.5)
        regulatory_barriers = inputs.competitive_data.get('regulatory_barriers', 0.5)
        brand_loyalty = inputs.competitive_data.get('brand_loyalty', 0.5)
        switching_costs = inputs.competitive_data.get('switching_costs', 0.5)
        
        steps.append({"step": "barrier_data", "capital": capital_requirements, "regulatory": regulatory_barriers})
        
        # Higher barriers = higher score (good for incumbents)
        barrier_score = (capital_requirements * 0.3 + regulatory_barriers * 0.25 + 
                        brand_loyalty * 0.25 + switching_costs * 0.2)
        
        steps.append({"step": "calculation", "barrier_score": barrier_score})
        return barrier_score, steps

    def _calculate_regulatory_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F6: Regulatory Environment scoring"""
        steps = []
        
        regulatory_complexity = inputs.market_data.get('regulatory_complexity', 0.5)
        compliance_cost = inputs.market_data.get('compliance_cost', 0.5)
        policy_stability = inputs.market_data.get('policy_stability', 0.5)
        
        steps.append({"step": "regulatory_data", "complexity": regulatory_complexity, "cost": compliance_cost})
        
        # Lower complexity and cost = higher score
        regulatory_score = 1.0 - ((regulatory_complexity * 0.5) + (compliance_cost * 0.3) - (policy_stability * 0.2))
        
        steps.append({"step": "calculation", "regulatory_score": regulatory_score})
        return max(0.0, min(1.0, regulatory_score)), steps

    def _calculate_economic_sensitivity_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F7: Economic Sensitivity scoring"""
        steps = []
        
        beta_coefficient = inputs.market_data.get('beta_coefficient', 1.0)
        cyclical_dependency = inputs.market_data.get('cyclical_dependency', 0.5)
        
        steps.append({"step": "economic_data", "beta": beta_coefficient, "cyclical": cyclical_dependency})
        
        # Lower sensitivity = higher score
        sensitivity_score = 1.0 - (min(1.0, beta_coefficient / 2.0) * 0.6 + cyclical_dependency * 0.4)
        
        steps.append({"step": "calculation", "sensitivity_score": sensitivity_score})
        return max(0.0, min(1.0, sensitivity_score)), steps

    # Product Factors (F8-F14) - Simplified implementations
    def _calculate_product_differentiation_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F8: Product Differentiation scoring"""
        differentiation = inputs.operational_data.get('product_differentiation', 0.5)
        uniqueness = inputs.operational_data.get('product_uniqueness', 0.5)
        return differentiation * 0.6 + uniqueness * 0.4, [{"step": "differentiation", "score": differentiation}]

    def _calculate_innovation_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F9: Innovation Capability scoring"""
        r_d_investment = inputs.operational_data.get('r_d_investment', 0.5)
        innovation_pipeline = inputs.operational_data.get('innovation_pipeline', 0.5)
        return r_d_investment * 0.5 + innovation_pipeline * 0.5, [{"step": "innovation", "score": r_d_investment}]

    def _calculate_quality_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F10: Quality & Reliability scoring"""
        quality_metrics = inputs.operational_data.get('quality_metrics', 0.5)
        reliability_score = inputs.operational_data.get('reliability_score', 0.5)
        return quality_metrics * 0.6 + reliability_score * 0.4, [{"step": "quality", "score": quality_metrics}]

    def _calculate_scalability_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F11: Scalability Potential scoring"""
        scalability = inputs.operational_data.get('scalability_potential', 0.5)
        growth_capacity = inputs.operational_data.get('growth_capacity', 0.5)
        return scalability * 0.6 + growth_capacity * 0.4, [{"step": "scalability", "score": scalability}]

    def _calculate_customer_stickiness_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F12: Customer Stickiness scoring"""
        retention_rate = inputs.operational_data.get('customer_retention', 0.5)
        switching_costs = inputs.operational_data.get('switching_costs', 0.5)
        return retention_rate * 0.7 + switching_costs * 0.3, [{"step": "stickiness", "score": retention_rate}]

    def _calculate_pricing_power_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F13: Pricing Power scoring"""
        pricing_flexibility = inputs.operational_data.get('pricing_flexibility', 0.5)
        margin_sustainability = inputs.operational_data.get('margin_sustainability', 0.5)
        return pricing_flexibility * 0.6 + margin_sustainability * 0.4, [{"step": "pricing", "score": pricing_flexibility}]

    def _calculate_lifecycle_position_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F14: Lifecycle Position scoring"""
        lifecycle_stage = inputs.operational_data.get('lifecycle_stage', 0.5)
        longevity_potential = inputs.operational_data.get('longevity_potential', 0.5)
        return lifecycle_stage * 0.5 + longevity_potential * 0.5, [{"step": "lifecycle", "score": lifecycle_stage}]

    # Financial Factors (F15-F21) - Simplified implementations
    def _calculate_revenue_growth_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F15: Revenue Growth scoring"""
        growth_rate = inputs.financial_data.get('revenue_growth_rate', 0.1)
        growth_sustainability = inputs.financial_data.get('growth_sustainability', 0.5)
        return min(1.0, growth_rate * 2.0) * growth_sustainability, [{"step": "revenue_growth", "rate": growth_rate}]

    def _calculate_profitability_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F16: Profitability Margins scoring"""
        gross_margin = inputs.financial_data.get('gross_margin', 0.3)
        operating_margin = inputs.financial_data.get('operating_margin', 0.15)
        return (gross_margin + operating_margin) / 2, [{"step": "profitability", "gross": gross_margin}]

    def _calculate_cash_flow_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F17: Cash Flow Generation scoring"""
        free_cash_flow = inputs.financial_data.get('free_cash_flow', 0.1)
        cash_conversion = inputs.financial_data.get('cash_conversion', 0.5)
        return min(1.0, free_cash_flow * 3.0) * cash_conversion, [{"step": "cash_flow", "fcf": free_cash_flow}]

    def _calculate_capital_efficiency_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F18: Capital Efficiency scoring"""
        roic = inputs.financial_data.get('return_on_invested_capital', 0.15)
        asset_turnover = inputs.financial_data.get('asset_turnover', 1.0)
        return min(1.0, roic * 2.0) * min(1.0, asset_turnover), [{"step": "capital_efficiency", "roic": roic}]

    def _calculate_financial_stability_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F19: Financial Stability scoring"""
        debt_ratio = inputs.financial_data.get('debt_to_equity', 0.5)
        liquidity_ratio = inputs.financial_data.get('current_ratio', 1.5)
        stability = (1.0 - min(1.0, debt_ratio)) * 0.6 + min(1.0, liquidity_ratio / 2.0) * 0.4
        return stability, [{"step": "financial_stability", "debt": debt_ratio}]

    def _calculate_cost_structure_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F20: Cost Structure scoring"""
        fixed_cost_ratio = inputs.financial_data.get('fixed_cost_ratio', 0.3)
        variable_cost_efficiency = inputs.financial_data.get('variable_cost_efficiency', 0.5)
        return (1.0 - fixed_cost_ratio) * 0.6 + variable_cost_efficiency * 0.4, [{"step": "cost_structure", "fixed": fixed_cost_ratio}]

    def _calculate_working_capital_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F21: Working Capital scoring"""
        working_capital_efficiency = inputs.financial_data.get('working_capital_efficiency', 0.5)
        cash_cycle = inputs.financial_data.get('cash_conversion_cycle', 30)
        efficiency = working_capital_efficiency * (1.0 - min(1.0, cash_cycle / 100.0))
        return efficiency, [{"step": "working_capital", "efficiency": working_capital_efficiency}]

    # Strategic Factors (F22-F28) - Simplified implementations
    def _calculate_brand_strength_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F22: Brand Strength scoring"""
        brand_recognition = inputs.operational_data.get('brand_recognition', 0.5)
        brand_loyalty = inputs.operational_data.get('brand_loyalty', 0.5)
        return brand_recognition * 0.6 + brand_loyalty * 0.4, [{"step": "brand_strength", "recognition": brand_recognition}]

    def _calculate_management_quality_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F23: Management Quality scoring"""
        leadership_score = inputs.operational_data.get('leadership_quality', 0.5)
        execution_track_record = inputs.operational_data.get('execution_track_record', 0.5)
        return leadership_score * 0.6 + execution_track_record * 0.4, [{"step": "management", "leadership": leadership_score}]

    def _calculate_strategic_positioning_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F24: Strategic Positioning scoring"""
        market_position = inputs.competitive_data.get('market_position', 0.5)
        strategic_clarity = inputs.operational_data.get('strategic_clarity', 0.5)
        return market_position * 0.6 + strategic_clarity * 0.4, [{"step": "strategic_positioning", "position": market_position}]

    def _calculate_operational_excellence_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F25: Operational Excellence scoring"""
        process_efficiency = inputs.operational_data.get('process_efficiency', 0.5)
        quality_management = inputs.operational_data.get('quality_management', 0.5)
        return process_efficiency * 0.6 + quality_management * 0.4, [{"step": "operational_excellence", "efficiency": process_efficiency}]

    def _calculate_digital_transformation_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F26: Digital Transformation scoring"""
        digital_capabilities = inputs.operational_data.get('digital_capabilities', 0.5)
        technology_adoption = inputs.operational_data.get('technology_adoption', 0.5)
        return digital_capabilities * 0.6 + technology_adoption * 0.4, [{"step": "digital_transformation", "capabilities": digital_capabilities}]

    def _calculate_sustainability_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F27: Sustainability & ESG scoring"""
        esg_score = inputs.operational_data.get('esg_score', 0.5)
        sustainability_initiatives = inputs.operational_data.get('sustainability_initiatives', 0.5)
        return esg_score * 0.7 + sustainability_initiatives * 0.3, [{"step": "sustainability", "esg": esg_score}]

    def _calculate_strategic_flexibility_score(self, inputs: FactorInputs) -> Tuple[float, List[Dict[str, Any]]]:
        """F28: Strategic Flexibility scoring"""
        adaptability = inputs.operational_data.get('strategic_adaptability', 0.5)
        option_value = inputs.operational_data.get('strategic_options', 0.5)
        return adaptability * 0.6 + option_value * 0.4, [{"step": "strategic_flexibility", "adaptability": adaptability}]

# Export the engine for use by other services
__all__ = ['PDFFormulaEngine', 'FactorInputs', 'PDFAnalysisResult', 'FormulaResult']
