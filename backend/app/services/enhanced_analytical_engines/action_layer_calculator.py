# backend/app/services/enhanced_analytical_engines/action_layer_calculator.py
import asyncio
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from .pdf_formula_engine import PDFAnalysisResult
from ...core.feature_flags import FeatureFlags
from ...core.gcp_config import GCPSettings
from ...core.error_recovery import with_exponential_backoff

# Optional monitoring import (requires google-cloud-monitoring)
try:
    from ...middleware.monitoring import performance_monitor
    MONITORING_AVAILABLE = True
except ImportError:
    # Create a no-op decorator when monitoring not available
    def performance_monitor(operation_name):
        def decorator(func):
            return func
        return decorator
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)

class ActionPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ActionRecommendation:
    action_id: str
    title: str
    description: str
    priority: ActionPriority
    impact_score: float
    effort_score: float
    timeline: str

@dataclass
class ActionLayerResult:
    layer_id: str
    layer_name: str
    score: float
    confidence: float
    contributing_factors: List[str]
    recommendations: List[ActionRecommendation]
    insights: List[str]

@dataclass
class ActionLayerAnalysis:
    layer_results: Dict[str, ActionLayerResult]
    strategic_priorities: List[ActionRecommendation]
    risk_assessment: Dict[str, float]
    confidence_metrics: Dict[str, float]

class ActionLayerCalculator:
    """18-Layer Action Calculator for strategic assessments"""
    
    def __init__(self):
        # Initialize GCP settings for enhanced integration
        self.settings = GCPSettings()
        
        self.action_layers = {
            'L01_overall_attractiveness': {'name': 'Overall Strategic Attractiveness', 'weight': 0.15},
            'L02_competitive_position': {'name': 'Competitive Position Strength', 'weight': 0.13},
            'L03_market_opportunity': {'name': 'Market Opportunity Assessment', 'weight': 0.14},
            'L04_innovation_potential': {'name': 'Innovation & Growth Potential', 'weight': 0.12},
            'L05_financial_health': {'name': 'Financial Health & Stability', 'weight': 0.13},
            'L06_execution_capability': {'name': 'Execution Capability', 'weight': 0.11},
            'L07_market_risk': {'name': 'Market Risk Assessment', 'weight': 0.08},
            'L08_operational_risk': {'name': 'Operational Risk Assessment', 'weight': 0.07},
            'L09_financial_risk': {'name': 'Financial Risk Assessment', 'weight': 0.08},
            'L10_strategic_risk': {'name': 'Strategic Risk Assessment', 'weight': 0.07},
            'L11_customer_value': {'name': 'Customer Value Creation', 'weight': 0.10},
            'L12_shareholder_value': {'name': 'Shareholder Value Creation', 'weight': 0.09},
            'L13_stakeholder_value': {'name': 'Stakeholder Value Creation', 'weight': 0.08},
            'L14_ecosystem_value': {'name': 'Ecosystem Value Creation', 'weight': 0.07},
            'L15_implementation_readiness': {'name': 'Implementation Readiness', 'weight': 0.09},
            'L16_resource_availability': {'name': 'Resource Availability', 'weight': 0.08},
            'L17_change_management': {'name': 'Change Management Capability', 'weight': 0.07},
            'L18_success_probability': {'name': 'Success Probability Assessment', 'weight': 0.08}
        }
        logger.info(f"✅ Action Layer Calculator initialized with 18 strategic assessments for project {self.settings.project_id}")
    
    @performance_monitor
    @with_exponential_backoff(max_retries=3)
    async def calculate_all_action_layers(self, pdf_results: PDFAnalysisResult) -> ActionLayerAnalysis:
        """Calculate all 18 action layers from PDF factor results"""
        start_time = datetime.now(timezone.utc)
        logger.info("Starting 18-layer action analysis")
        
        try:
            layer_results = {}
            
            # Calculate each layer based on PDF results
            for layer_id, layer_config in self.action_layers.items():
                layer_score = self._calculate_layer_score(layer_id, pdf_results)
                confidence = self._calculate_confidence(layer_score)
                contributing_factors = self._get_contributing_factors(layer_id, pdf_results)
                recommendations = self._generate_recommendations(layer_id, layer_score)
                insights = self._generate_insights(layer_id, layer_score)
                
                layer_results[layer_id] = ActionLayerResult(
                    layer_id=layer_id,
                    layer_name=layer_config['name'],
                    score=layer_score,
                    confidence=confidence,
                    contributing_factors=contributing_factors,
                    recommendations=recommendations,
                    insights=insights
                )
            
            # Generate strategic priorities
            strategic_priorities = self._generate_strategic_priorities(layer_results)
            
            # Calculate risk assessment
            risk_assessment = self._calculate_risk_assessment(layer_results)
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(layer_results)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = ActionLayerAnalysis(
                layer_results=layer_results,
                strategic_priorities=strategic_priorities,
                risk_assessment=risk_assessment,
                confidence_metrics=confidence_metrics
            )
            
            logger.info(f"✅ 18-layer action analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Action layer calculation failed: {e}")
            raise
    
    def _calculate_layer_score(self, layer_id: str, pdf_results: PDFAnalysisResult) -> float:
        """Calculate score for a specific layer"""
        if layer_id.startswith('L0'):
            # Strategic layers use category scores
            if layer_id in ['L01_overall_attractiveness', 'L18_success_probability']:
                return pdf_results.overall_score
            elif layer_id in ['L02_competitive_position', 'L03_market_opportunity']:
                return pdf_results.category_scores.get('market', 0.5)
            elif layer_id in ['L04_innovation_potential', 'L05_financial_health']:
                return pdf_results.category_scores.get('product', 0.5)
            else:
                return pdf_results.category_scores.get('strategic', 0.5)
        elif layer_id.startswith('L07') or layer_id.startswith('L08') or layer_id.startswith('L09') or layer_id.startswith('L10'):
            # Risk layers - invert scores
            return 1.0 - pdf_results.overall_score
        else:
            # Value creation and implementation layers
            return pdf_results.overall_score * 0.8
    
    def _calculate_confidence(self, score: float) -> float:
        """Calculate confidence based on score"""
        return min(1.0, max(0.1, score + 0.2))
    
    def _get_contributing_factors(self, layer_id: str, pdf_results: PDFAnalysisResult) -> List[str]:
        """Get contributing factors for a layer"""
        return list(pdf_results.factor_results.keys())[:3]  # Simplified
    
    def _generate_recommendations(self, layer_id: str, score: float) -> List[ActionRecommendation]:
        """Generate recommendations for a layer"""
        if score < 0.3:
            priority = ActionPriority.CRITICAL
        elif score < 0.5:
            priority = ActionPriority.HIGH
        elif score < 0.7:
            priority = ActionPriority.MEDIUM
        else:
            priority = ActionPriority.LOW
        
        return [ActionRecommendation(
            action_id=f"{layer_id}_001",
            title=f"Improve {self.action_layers[layer_id]['name']}",
            description=f"Score of {score:.2f} requires attention",
            priority=priority,
            impact_score=score,
            effort_score=0.6,
            timeline="3-6 months"
        )]
    
    def _generate_insights(self, layer_id: str, score: float) -> List[str]:
        """Generate insights for a layer"""
        layer_name = self.action_layers[layer_id]['name']
        if score < 0.4:
            return [f"{layer_name} shows critical weakness (score: {score:.2f})"]
        elif score < 0.6:
            return [f"{layer_name} indicates moderate performance (score: {score:.2f})"]
        else:
            return [f"{layer_name} demonstrates strong performance (score: {score:.2f})"]
    
    def _generate_strategic_priorities(self, layer_results: Dict[str, ActionLayerResult]) -> List[ActionRecommendation]:
        """Generate strategic priorities"""
        all_recommendations = []
        for layer_result in layer_results.values():
            all_recommendations.extend(layer_result.recommendations)
        
        # Sort by priority
        priority_order = {ActionPriority.CRITICAL: 0, ActionPriority.HIGH: 1, ActionPriority.MEDIUM: 2, ActionPriority.LOW: 3}
        all_recommendations.sort(key=lambda x: (priority_order[x.priority], -x.impact_score))
        
        return all_recommendations[:10]
    
    def _calculate_risk_assessment(self, layer_results: Dict[str, ActionLayerResult]) -> Dict[str, float]:
        """Calculate risk assessment"""
        risk_layers = ['L07_market_risk', 'L08_operational_risk', 'L09_financial_risk', 'L10_strategic_risk']
        risk_scores = []
        
        for risk_layer in risk_layers:
            if risk_layer in layer_results:
                risk_scores.append(layer_results[risk_layer].score)
        
        overall_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.5
        
        return {
            'overall_risk': overall_risk,
            'market_risk': layer_results.get('L07_market_risk', ActionLayerResult('', '', 0.5, 0.5, [], [], [])).score,
            'operational_risk': layer_results.get('L08_operational_risk', ActionLayerResult('', '', 0.5, 0.5, [], [], [])).score,
            'financial_risk': layer_results.get('L09_financial_risk', ActionLayerResult('', '', 0.5, 0.5, [], [], [])).score,
            'strategic_risk': layer_results.get('L10_strategic_risk', ActionLayerResult('', '', 0.5, 0.5, [], [], [])).score
        }
    
    def _calculate_confidence_metrics(self, layer_results: Dict[str, ActionLayerResult]) -> Dict[str, float]:
        """Calculate confidence metrics"""
        if not layer_results:
            return {'overall_confidence': 0.1}
        
        confidences = [result.confidence for result in layer_results.values()]
        
        return {
            'overall_confidence': sum(confidences) / len(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences)
        }

__all__ = ['ActionLayerCalculator', 'ActionLayerResult', 'ActionLayerAnalysis', 'ActionRecommendation', 'ActionPriority']