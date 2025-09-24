# backend/app/services/action_layer_calculator.py

import asyncio
import logging
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field

from .pdf_formula_engine import PDFAnalysisResult, FormulaResult
from ..core.gcp_config import GCPSettings
from ..middleware.monitoring import performance_monitor
from ..core.error_recovery import with_exponential_backoff

logger = logging.getLogger(__name__)

class ActionLayerCategory(Enum):
    """Categories for 18 Action Layer assessments"""
    STRATEGIC = "strategic"
    FINANCIAL = "financial" 
    OPERATIONAL = "operational"
    MARKET = "market"
    RISK = "risk"

@dataclass
class ActionLayerResult:
    """Result of a single action layer calculation"""
    layer_name: str
    category: ActionLayerCategory
    score: float
    confidence: float
    contributing_factors: List[str]
    calculation_method: str
    insights: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]

@dataclass
class ActionLayerAnalysis:
    """Complete 18-layer action analysis result"""
    layer_results: Dict[str, ActionLayerResult]
    category_scores: Dict[str, float]
    overall_action_score: float
    strategic_recommendations: List[str]
    risk_assessment: Dict[str, float]
    processing_time: float
    timestamp: str

class ActionLayerCalculator:
    """
    18-Formula Action Layer Calculator implementing strategic assessments
    Based on sophisticated action layer framework from previous repository
    """
    
    def __init__(self):
        self.settings = GCPSettings()
        self.action_layer_definitions = self._initialize_action_layers()
        
    def _initialize_action_layers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all 18 action layer calculation definitions"""
        return {
            # Strategic Action Layers (6 layers)
            'D_Score': {
                'category': ActionLayerCategory.STRATEGIC,
                'weight': 0.20,
                'description': 'Overall Decision Score - Comprehensive strategic assessment',
                'method': 'weighted_composite',
                'required_factors': ['market_factors', 'product_factors', 'financial_factors', 'strategic_factors']
            },
            'Strategic_Position_Score': {
                'category': ActionLayerCategory.STRATEGIC,
                'weight': 0.15,
                'description': 'Strategic positioning strength and competitive advantage',
                'method': 'strategic_positioning_analysis',
                'required_factors': ['F22_brand_strength', 'F24_strategic_positioning', 'F8_product_differentiation']
            },
            'SWOT_Score': {
                'category': ActionLayerCategory.STRATEGIC,
                'weight': 0.12,
                'description': 'SWOT analysis comprehensive score',
                'method': 'swot_composite',
                'required_factors': ['strengths', 'weaknesses', 'opportunities', 'threats']
            },
            'Strategic_Flexibility_Score': {
                'category': ActionLayerCategory.STRATEGIC,
                'weight': 0.10,
                'description': 'Adaptability and strategic option value',
                'method': 'flexibility_analysis',
                'required_factors': ['F28_strategic_flexibility', 'F26_digital_transformation']
            },
            'Competitive_Advantage_Score': {
                'category': ActionLayerCategory.STRATEGIC,
                'weight': 0.13,
                'description': 'Sustainable competitive advantage assessment',
                'method': 'competitive_advantage_analysis',
                'required_factors': ['F4_competitive_intensity', 'F5_barrier_to_entry', 'F8_product_differentiation']
            },
            'Innovation_Leadership_Score': {
                'category': ActionLayerCategory.STRATEGIC,
                'weight': 0.11,
                'description': 'Innovation capability and leadership position',
                'method': 'innovation_leadership_analysis',
                'required_factors': ['F9_innovation_capability', 'F26_digital_transformation']
            },
            
            # Financial Action Layers (4 layers)
            'Financial_Health_Score': {
                'category': ActionLayerCategory.FINANCIAL,
                'weight': 0.18,
                'description': 'Overall financial health and stability',
                'method': 'financial_health_composite',
                'required_factors': ['F15_revenue_growth', 'F16_profitability_margins', 'F17_cash_flow_generation', 'F19_financial_stability']
            },
            'Growth_Potential_Score': {
                'category': ActionLayerCategory.FINANCIAL,
                'weight': 0.16,
                'description': 'Revenue and profit growth sustainability',
                'method': 'growth_potential_analysis',
                'required_factors': ['F15_revenue_growth', 'F2_market_growth', 'F11_scalability_potential']
            },
            'Profitability_Score': {
                'category': ActionLayerCategory.FINANCIAL,
                'weight': 0.15,
                'description': 'Margin sustainability and profitability trends',
                'method': 'profitability_analysis',
                'required_factors': ['F16_profitability_margins', 'F13_pricing_power', 'F20_cost_structure']
            },
            'Capital_Efficiency_Score': {
                'category': ActionLayerCategory.FINANCIAL,
                'weight': 0.13,
                'description': 'Capital allocation and return efficiency',
                'method': 'capital_efficiency_analysis',
                'required_factors': ['F18_capital_efficiency', 'F21_working_capital']
            },
            
            # Market Action Layers (3 layers)
            'Market_Attractiveness_Score': {
                'category': ActionLayerCategory.MARKET,
                'weight': 0.17,
                'description': 'Overall market opportunity and attractiveness',
                'method': 'market_attractiveness_analysis',
                'required_factors': ['F1_market_size', 'F2_market_growth', 'F3_market_maturity']
            },
            'Customer_Value_Score': {
                'category': ActionLayerCategory.MARKET,
                'weight': 0.14,
                'description': 'Customer satisfaction and value proposition strength',
                'method': 'customer_value_analysis',
                'required_factors': ['F12_customer_stickiness', 'F10_quality_reliability', 'F22_brand_strength']
            },
            'Market_Share_Potential_Score': {
                'category': ActionLayerCategory.MARKET,
                'weight': 0.12,
                'description': 'Market share capture and expansion potential',
                'method': 'market_share_analysis',
                'required_factors': ['F4_competitive_intensity', 'F5_barrier_to_entry', 'F1_market_size']
            },
            
            # Operational Action Layers (3 layers)
            'Operational_Excellence_Score': {
                'category': ActionLayerCategory.OPERATIONAL,
                'weight': 0.15,
                'description': 'Operational efficiency and process optimization',
                'method': 'operational_excellence_analysis',
                'required_factors': ['F25_operational_excellence', 'F20_cost_structure', 'F18_capital_efficiency']
            },
            'Execution_Capability_Score': {
                'category': ActionLayerCategory.OPERATIONAL,
                'weight': 0.13,
                'description': 'Management execution and delivery capability',
                'method': 'execution_capability_analysis',
                'required_factors': ['F23_management_quality', 'F25_operational_excellence']
            },
            'Scalability_Score': {
                'category': ActionLayerCategory.OPERATIONAL,
                'weight': 0.11,
                'description': 'Business model scalability and growth capacity',
                'method': 'scalability_analysis',
                'required_factors': ['F11_scalability_potential', 'F26_digital_transformation', 'F20_cost_structure']
            },
            
            # Risk Action Layers (2 layers)
            'Risk_Score': {
                'category': ActionLayerCategory.RISK,
                'weight': 0.16,
                'description': 'Comprehensive risk assessment (inverse of opportunity)',
                'method': 'comprehensive_risk_analysis',
                'required_factors': ['F19_financial_stability', 'F6_regulatory_environment', 'F7_economic_sensitivity']
            },
            'Sustainability_Risk_Score': {
                'category': ActionLayerCategory.RISK,
                'weight': 0.12,
                'description': 'ESG and sustainability risk assessment',
                'method': 'sustainability_risk_analysis',
                'required_factors': ['F27_sustainability_esg', 'F6_regulatory_environment']
            }
        }

    @performance_monitor
    async def calculate_all_action_layers(self, pdf_results: PDFAnalysisResult) -> ActionLayerAnalysis:
        """
        Calculate all 18 action layer scores from PDF factor results
        """
        start_time = datetime.now(timezone.utc)
        logger.info("Starting comprehensive action layer analysis")
        
        try:
            # Calculate individual action layers
            layer_results = {}
            calculation_tasks = []
            
            for layer_name, layer_config in self.action_layer_definitions.items():
                task = self._calculate_single_action_layer(layer_name, layer_config, pdf_results)
                calculation_tasks.append(task)
            
            # Execute calculations in parallel
            layer_calculations = await asyncio.gather(*calculation_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(layer_calculations):
                layer_name = list(self.action_layer_definitions.keys())[i]
                if isinstance(result, Exception):
                    logger.error(f"Action layer {layer_name} calculation failed: {result}")
                    # Use default result with low confidence
                    layer_results[layer_name] = ActionLayerResult(
                        layer_name=layer_name,
                        category=self.action_layer_definitions[layer_name]['category'],
                        score=0.5,
                        confidence=0.1,
                        contributing_factors=[],
                        calculation_method="error_fallback",
                        insights=["Calculation failed - using default score"],
                        recommendations=["Review input data quality"],
                        metadata={"error": str(result)}
                    )
                else:
                    layer_results[layer_name] = result
            
            # Calculate category scores
            category_scores = self._calculate_category_scores(layer_results)
            
            # Calculate overall action score
            overall_action_score = self._calculate_overall_action_score(layer_results)
            
            # Generate strategic recommendations
            strategic_recommendations = self._generate_strategic_recommendations(layer_results)
            
            # Assess comprehensive risk
            risk_assessment = self._assess_comprehensive_risk(layer_results)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = ActionLayerAnalysis(
                layer_results=layer_results,
                category_scores=category_scores,
                overall_action_score=overall_action_score,
                strategic_recommendations=strategic_recommendations,
                risk_assessment=risk_assessment,
                processing_time=processing_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            logger.info(f"✅ Action layer analysis completed in {processing_time:.2f}s with overall score {overall_action_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Action layer analysis failed: {e}")
            raise

    @with_exponential_backoff
    async def _calculate_single_action_layer(self, layer_name: str, layer_config: Dict[str, Any], pdf_results: PDFAnalysisResult) -> ActionLayerResult:
        """Calculate a single action layer score with full analysis"""
        
        try:
            method = layer_config['method']
            required_factors = layer_config['required_factors']
            
            # Extract relevant factor scores
            relevant_factors = self._extract_relevant_factors(required_factors, pdf_results)
            
            # Calculate score using specified method
            if method == 'weighted_composite':
                score, insights, recommendations = await self._calculate_weighted_composite(relevant_factors)
            elif method == 'strategic_positioning_analysis':
                score, insights, recommendations = await self._calculate_strategic_positioning(relevant_factors)
            elif method == 'swot_composite':
                score, insights, recommendations = await self._calculate_swot_composite(relevant_factors)
            elif method == 'financial_health_composite':
                score, insights, recommendations = await self._calculate_financial_health(relevant_factors)
            elif method == 'growth_potential_analysis':
                score, insights, recommendations = await self._calculate_growth_potential(relevant_factors)
            elif method == 'market_attractiveness_analysis':
                score, insights, recommendations = await self._calculate_market_attractiveness(relevant_factors)
            elif method == 'comprehensive_risk_analysis':
                score, insights, recommendations = await self._calculate_comprehensive_risk(relevant_factors)
            else:
                # Default calculation method
                score, insights, recommendations = await self._calculate_default_composite(relevant_factors)
            
            # Calculate confidence based on factor quality
            confidence = self._calculate_action_layer_confidence(relevant_factors)
            
            # Extract contributing factor names
            contributing_factors = list(relevant_factors.keys())
            
            return ActionLayerResult(
                layer_name=layer_name,
                category=layer_config['category'],
                score=max(0.0, min(1.0, score)),
                confidence=confidence,
                contributing_factors=contributing_factors,
                calculation_method=method,
                insights=insights,
                recommendations=recommendations,
                metadata={
                    'weight': layer_config['weight'],
                    'description': layer_config['description'],
                    'calculation_timestamp': datetime.now(timezone.utc).isoformat(),
                    'factor_count': len(relevant_factors)
                }
            )
            
        except Exception as e:
            logger.error(f"Action layer {layer_name} calculation error: {e}")
            raise

    def _extract_relevant_factors(self, required_factors: List[str], pdf_results: PDFAnalysisResult) -> Dict[str, FormulaResult]:
        """Extract relevant factor results for action layer calculation"""
        relevant_factors = {}
        
        for factor_requirement in required_factors:
            # Handle different factor requirement patterns
            if factor_requirement.startswith('F') and '_' in factor_requirement:
                # Direct factor reference (e.g., 'F1_market_size')
                if factor_requirement in pdf_results.factor_results:
                    relevant_factors[factor_requirement] = pdf_results.factor_results[factor_requirement]
            elif factor_requirement.endswith('_factors'):
                # Category reference (e.g., 'market_factors')
                category_prefix = factor_requirement.replace('_factors', '')
                
                # Category prefix mapping
                category_prefix_map = {
                    'market': ('F1_', 'F2_', 'F3_', 'F4_', 'F5_', 'F6_', 'F7_'),
                    'product': ('F8_', 'F9_', 'F10_', 'F11_', 'F12_', 'F13_', 'F14_'),
                    'financial': ('F15_', 'F16_', 'F17_', 'F18_', 'F19_', 'F20_', 'F21_'),
                    'strategic': ('F22_', 'F23_', 'F24_', 'F25_', 'F26_', 'F27_', 'F28_')
                }
                
                prefix_tuple = category_prefix_map.get(category_prefix, ())
                category_factors = {k: v for k, v in pdf_results.factor_results.items() if k.startswith(prefix_tuple)}
                relevant_factors.update(category_factors)
            elif factor_requirement in ['strengths', 'weaknesses', 'opportunities', 'threats']:
                # SWOT component - derive from existing action layer scores
                if hasattr(pdf_results, 'action_layer_scores') and pdf_results.action_layer_scores:
                    # Create synthetic factor result for SWOT components
                    swot_score = self._derive_swot_component_score(factor_requirement, pdf_results.action_layer_scores)
                    relevant_factors[factor_requirement] = FormulaResult(
                        formula_name=factor_requirement,
                        raw_score=swot_score,
                        normalized_score=swot_score,
                        confidence=0.8,
                        calculation_steps=[{"method": "swot_derivation"}],
                        metadata={"type": "swot_component"}
                    )
                    
        return relevant_factors

    async def _calculate_weighted_composite(self, factors: Dict[str, FormulaResult]) -> Tuple[float, List[str], List[str]]:
        """Calculate weighted composite score (used for D_Score)"""
        if not factors:
            return 0.5, ["No factors available"], ["Improve data collection"]
        
        # Calculate weighted average
        total_score = 0.0
        total_weight = 0.0
        
        for factor_result in factors.values():
            weight = factor_result.confidence  # Use confidence as weight
            total_score += factor_result.normalized_score * weight
            total_weight += weight
        
        final_score = total_score / max(total_weight, 0.01)
        
        # Generate insights
        insights = []
        top_factors = sorted(factors.items(), key=lambda x: x[1].normalized_score, reverse=True)[:3]
        insights.append(f"Top performing factors: {', '.join([f[0] for f in top_factors])}")
        
        weak_factors = [f for f in factors.items() if f[1].normalized_score < 0.4]
        if weak_factors:
            insights.append(f"Areas needing attention: {', '.join([f[0] for f in weak_factors])}")
        
        # Generate recommendations
        recommendations = []
        if final_score > 0.7:
            recommendations.append("Strong overall performance - focus on maintaining competitive advantage")
        elif final_score > 0.5:
            recommendations.append("Moderate performance - identify key improvement areas")
        else:
            recommendations.append("Performance concerns - comprehensive improvement strategy needed")
            
        return final_score, insights, recommendations

    async def _calculate_strategic_positioning(self, factors: Dict[str, FormulaResult]) -> Tuple[float, List[str], List[str]]:
        """Calculate strategic positioning strength"""
        brand_strength = factors.get('F22_brand_strength', FormulaResult('F22_brand_strength', 0.5, 0.5, 0.5, [], {})).normalized_score
        strategic_pos = factors.get('F24_strategic_positioning', FormulaResult('F24_strategic_positioning', 0.5, 0.5, 0.5, [], {})).normalized_score
        differentiation = factors.get('F8_product_differentiation', FormulaResult('F8_product_differentiation', 0.5, 0.5, 0.5, [], {})).normalized_score
        
        # Strategic positioning composite
        score = (brand_strength * 0.4 + strategic_pos * 0.35 + differentiation * 0.25)
        
        insights = [
            f"Brand strength: {brand_strength:.2f}",
            f"Strategic positioning: {strategic_pos:.2f}",
            f"Product differentiation: {differentiation:.2f}"
        ]
        
        recommendations = []
        if brand_strength < 0.5:
            recommendations.append("Invest in brand building and market presence")
        if differentiation < 0.5:
            recommendations.append("Enhance product differentiation strategy")
        if strategic_pos < 0.5:
            recommendations.append("Clarify and strengthen strategic positioning")
            
        return score, insights, recommendations

    async def _calculate_swot_composite(self, factors: Dict[str, FormulaResult]) -> Tuple[float, List[str], List[str]]:
        """Calculate SWOT composite score"""
        strengths = factors.get('strengths', FormulaResult('strengths', 0.5, 0.5, 0.5, [], {})).normalized_score
        weaknesses = factors.get('weaknesses', FormulaResult('weaknesses', 0.5, 0.5, 0.5, [], {})).normalized_score
        opportunities = factors.get('opportunities', FormulaResult('opportunities', 0.5, 0.5, 0.5, [], {})).normalized_score
        threats = factors.get('threats', FormulaResult('threats', 0.5, 0.5, 0.5, [], {})).normalized_score
        
        # SWOT composite: (Strengths + Opportunities) - (Weaknesses + Threats)
        swot_score = ((strengths + opportunities) - (weaknesses + threats)) / 2.0
        normalized_score = max(0.0, min(1.0, (swot_score + 1.0) / 2.0))  # Normalize to 0-1
        
        insights = [
            f"Strengths score: {strengths:.2f}",
            f"Opportunities score: {opportunities:.2f}",
            f"Weaknesses score: {weaknesses:.2f}",
            f"Threats score: {threats:.2f}"
        ]
        
        recommendations = []
        if strengths > opportunities:
            recommendations.append("Leverage strengths to capitalize on market opportunities")
        if weaknesses > 0.6:
            recommendations.append("Address key weaknesses that limit performance")
        if threats > 0.6:
            recommendations.append("Develop mitigation strategies for identified threats")
            
        return normalized_score, insights, recommendations

    async def _calculate_financial_health(self, factors: Dict[str, FormulaResult]) -> Tuple[float, List[str], List[str]]:
        """Calculate financial health composite score"""
        revenue_growth = factors.get('F15_revenue_growth', FormulaResult('F15_revenue_growth', 0.5, 0.5, 0.5, [], {})).normalized_score
        profitability = factors.get('F16_profitability_margins', FormulaResult('F16_profitability_margins', 0.5, 0.5, 0.5, [], {})).normalized_score
        cash_flow = factors.get('F17_cash_flow_generation', FormulaResult('F17_cash_flow_generation', 0.5, 0.5, 0.5, [], {})).normalized_score
        stability = factors.get('F19_financial_stability', FormulaResult('F19_financial_stability', 0.5, 0.5, 0.5, [], {})).normalized_score
        
        # Financial health composite
        score = (revenue_growth * 0.3 + profitability * 0.3 + cash_flow * 0.2 + stability * 0.2)
        
        insights = [
            f"Revenue growth: {revenue_growth:.2f}",
            f"Profitability: {profitability:.2f}",
            f"Cash flow: {cash_flow:.2f}",
            f"Financial stability: {stability:.2f}"
        ]
        
        recommendations = []
        if revenue_growth < 0.5:
            recommendations.append("Focus on revenue growth acceleration strategies")
        if profitability < 0.5:
            recommendations.append("Improve margin management and cost optimization")
        if cash_flow < 0.5:
            recommendations.append("Enhance cash flow generation and working capital management")
        if stability < 0.5:
            recommendations.append("Strengthen financial stability and risk management")
            
        return score, insights, recommendations

    async def _calculate_growth_potential(self, factors: Dict[str, FormulaResult]) -> Tuple[float, List[str], List[str]]:
        """Calculate growth potential analysis"""
        revenue_growth = factors.get('F15_revenue_growth', FormulaResult('F15_revenue_growth', 0.5, 0.5, 0.5, [], {})).normalized_score
        market_growth = factors.get('F2_market_growth', FormulaResult('F2_market_growth', 0.5, 0.5, 0.5, [], {})).normalized_score
        scalability = factors.get('F11_scalability_potential', FormulaResult('F11_scalability_potential', 0.5, 0.5, 0.5, [], {})).normalized_score
        
        # Growth potential composite
        score = (revenue_growth * 0.4 + market_growth * 0.35 + scalability * 0.25)
        
        insights = [
            f"Revenue growth potential: {revenue_growth:.2f}",
            f"Market growth opportunity: {market_growth:.2f}",
            f"Scalability capacity: {scalability:.2f}"
        ]
        
        recommendations = []
        if revenue_growth > 0.7 and market_growth > 0.7:
            recommendations.append("Strong growth environment - accelerate expansion plans")
        elif scalability < 0.5:
            recommendations.append("Improve scalability infrastructure and capabilities")
        else:
            recommendations.append("Optimize growth strategy based on market conditions")
            
        return score, insights, recommendations

    async def _calculate_market_attractiveness(self, factors: Dict[str, FormulaResult]) -> Tuple[float, List[str], List[str]]:
        """Calculate market attractiveness analysis"""
        market_size = factors.get('F1_market_size', FormulaResult('F1_market_size', 0.5, 0.5, 0.5, [], {})).normalized_score
        market_growth = factors.get('F2_market_growth', FormulaResult('F2_market_growth', 0.5, 0.5, 0.5, [], {})).normalized_score
        market_maturity = factors.get('F3_market_maturity', FormulaResult('F3_market_maturity', 0.5, 0.5, 0.5, [], {})).normalized_score
        
        # Market attractiveness composite
        score = (market_size * 0.4 + market_growth * 0.4 + market_maturity * 0.2)
        
        insights = [
            f"Market size opportunity: {market_size:.2f}",
            f"Market growth rate: {market_growth:.2f}",
            f"Market maturity stage: {market_maturity:.2f}"
        ]
        
        recommendations = []
        if market_size > 0.7 and market_growth > 0.7:
            recommendations.append("Highly attractive market - prioritize market entry and expansion")
        elif market_maturity > 0.8:
            recommendations.append("Mature market - focus on differentiation and efficiency")
        else:
            recommendations.append("Emerging market - develop early mover advantage")
            
        return score, insights, recommendations

    async def _calculate_comprehensive_risk(self, factors: Dict[str, FormulaResult]) -> Tuple[float, List[str], List[str]]:
        """Calculate comprehensive risk assessment"""
        financial_stability = factors.get('F19_financial_stability', FormulaResult('F19_financial_stability', 0.5, 0.5, 0.5, [], {})).normalized_score
        regulatory = factors.get('F6_regulatory_environment', FormulaResult('F6_regulatory_environment', 0.5, 0.5, 0.5, [], {})).normalized_score
        economic_sensitivity = factors.get('F7_economic_sensitivity', FormulaResult('F7_economic_sensitivity', 0.5, 0.5, 0.5, [], {})).normalized_score
        
        # Risk score (higher = more risky, so invert stability scores)
        risk_score = (1.0 - financial_stability) * 0.4 + (1.0 - regulatory) * 0.3 + economic_sensitivity * 0.3
        
        insights = [
            f"Financial risk level: {1.0 - financial_stability:.2f}",
            f"Regulatory risk level: {1.0 - regulatory:.2f}",
            f"Economic sensitivity: {economic_sensitivity:.2f}"
        ]
        
        recommendations = []
        if financial_stability < 0.5:
            recommendations.append("Strengthen financial position and reduce debt levels")
        if regulatory < 0.5:
            recommendations.append("Enhance regulatory compliance and monitoring")
        if economic_sensitivity > 0.7:
            recommendations.append("Diversify revenue streams to reduce economic sensitivity")
            
        return risk_score, insights, recommendations

    async def _calculate_default_composite(self, factors: Dict[str, FormulaResult]) -> Tuple[float, List[str], List[str]]:
        """Default composite calculation method"""
        if not factors:
            return 0.5, ["No factors available"], ["Improve data collection"]
        
        scores = [f.normalized_score for f in factors.values()]
        score = sum(scores) / len(scores)
        
        insights = [f"Average score across {len(factors)} factors: {score:.2f}"]
        recommendations = ["Review individual factor performance for targeted improvements"]
        
        return score, insights, recommendations

    def _derive_swot_component_score(self, component: str, action_scores: Dict[str, float]) -> float:
        """Derive SWOT component scores from existing action layer scores"""
        if component == 'strengths':
            return (action_scores.get('Product_Strength_Score', 0.5) * 0.4 + 
                   action_scores.get('Strategic_Position_Score', 0.5) * 0.35 +
                   action_scores.get('Financial_Health_Score', 0.5) * 0.25)
        elif component == 'weaknesses':
            return 1.0 - ((action_scores.get('Operational_Excellence_Score', 0.5) * 0.5 + 
                          action_scores.get('Execution_Capability_Score', 0.5) * 0.5))
        elif component == 'opportunities':
            return (action_scores.get('Market_Attractiveness_Score', 0.5) * 0.6 + 
                   action_scores.get('Growth_Potential_Score', 0.5) * 0.4)
        elif component == 'threats':
            return action_scores.get('Risk_Score', 0.5)
        return 0.5

    def _calculate_category_scores(self, layer_results: Dict[str, ActionLayerResult]) -> Dict[str, float]:
        """Calculate average scores by action layer category"""
        category_scores = {}
        category_counts = {}
        
        for result in layer_results.values():
            category_name = result.category.value
            if category_name not in category_scores:
                category_scores[category_name] = 0.0
                category_counts[category_name] = 0
                
            category_scores[category_name] += result.score
            category_counts[category_name] += 1
        
        # Calculate averages
        for category in category_scores:
            category_scores[category] /= category_counts[category]
            
        return category_scores

    def _calculate_overall_action_score(self, layer_results: Dict[str, ActionLayerResult]) -> float:
        """Calculate overall weighted action score"""
        total_score = 0.0
        total_weight = 0.0
        
        for layer_name, result in layer_results.items():
            weight = self.action_layer_definitions[layer_name]['weight']
            total_score += result.score * weight
            total_weight += weight
            
        return total_score / max(total_weight, 0.01)

    def _calculate_action_layer_confidence(self, factors: Dict[str, FormulaResult]) -> float:
        """Calculate confidence for action layer result"""
        if not factors:
            return 0.1
            
        confidences = [f.confidence for f in factors.values()]
        return sum(confidences) / len(confidences)

    def _generate_strategic_recommendations(self, layer_results: Dict[str, ActionLayerResult]) -> List[str]:
        """Generate strategic recommendations based on action layer results"""
        recommendations = []
        
        # Analyze top and bottom performing layers
        sorted_layers = sorted(layer_results.items(), key=lambda x: x[1].score)
        bottom_layers = sorted_layers[:3]
        top_layers = sorted_layers[-3:]
        
        # Add category-specific recommendations
        for layer_name, result in bottom_layers:
            if result.score < 0.4:
                recommendations.extend(result.recommendations[:2])  # Top 2 recommendations
        
        # Add strategic focus recommendations
        if any(result.score > 0.8 for result in layer_results.values()):
            recommendations.append("Maintain and protect areas of excellence as competitive advantages")
            
        return recommendations[:10]  # Limit to top 10 recommendations

    def _assess_comprehensive_risk(self, layer_results: Dict[str, ActionLayerResult]) -> Dict[str, float]:
        """Assess comprehensive risk across all dimensions"""
        risk_assessment = {}
        
        # Extract risk-related scores
        financial_risk = 1.0 - layer_results.get('Financial_Health_Score', ActionLayerResult(
            layer_name="Financial_Health_Score", 
            category=ActionLayerCategory.FINANCIAL, 
            score=0.5, 
            confidence=0.5, 
            recommendations=[], 
            description='', 
            influences=[], 
            links=[], 
            metadata={}
        )).score
        market_risk = 1.0 - layer_results.get('Market_Attractiveness_Score', ActionLayerResult(
            layer_name="Market_Attractiveness_Score", 
            category=ActionLayerCategory.MARKET, 
            score=0.5, 
            confidence=0.5, 
            recommendations=[], 
            description='', 
            influences=[], 
            links=[], 
            metadata={}
        )).score
        operational_risk = 1.0 - layer_results.get('Operational_Excellence_Score', ActionLayerResult(
            layer_name="Operational_Excellence_Score", 
            category=ActionLayerCategory.OPERATIONAL, 
            score=0.5, 
            confidence=0.5, 
            recommendations=[], 
            description='', 
            influences=[], 
            links=[], 
            metadata={}
        )).score
        strategic_risk = 1.0 - layer_results.get('Strategic_Position_Score', ActionLayerResult(
            layer_name="Strategic_Position_Score", 
            category=ActionLayerCategory.STRATEGIC, 
            score=0.5, 
            confidence=0.5, 
            recommendations=[], 
            description='', 
            influences=[], 
            links=[], 
            metadata={}
        )).score
        
        risk_assessment['financial_risk'] = financial_risk
        risk_assessment['market_risk'] = market_risk
        risk_assessment['operational_risk'] = operational_risk
        risk_assessment['strategic_risk'] = strategic_risk
        risk_assessment['overall_risk'] = (financial_risk + market_risk + operational_risk + strategic_risk) / 4.0
        
        return risk_assessment

# Export the calculator for use by other services
__all__ = ['ActionLayerCalculator', 'ActionLayerAnalysis', 'ActionLayerResult', 'ActionLayerCategory']
