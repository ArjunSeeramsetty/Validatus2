"""
Validatus v2.0 Factor Calculation Engine
Aggregates 210 layer scores into 28 strategic factors
"""
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel

from ..core.aliases_config import aliases_config
from ..services.v2_expert_persona_scorer import LayerScore

logger = logging.getLogger(__name__)

class FactorCalculation(BaseModel):
    """Factor calculation result model"""
    session_id: str
    factor_id: str
    factor_name: str
    calculated_value: float
    confidence_score: float
    input_layer_count: int
    calculation_method: str
    layer_contributions: Dict[str, float]
    validation_metrics: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    created_at: datetime

class V2FactorCalculationEngine:
    """Calculates 28 strategic factors from layer scores"""
    
    def __init__(self):
        self.aliases = aliases_config
        
        # Define default calculation methods
        self.calculation_methods = {
            'weighted_average': self._calculate_weighted_average,
            'harmonic_mean': self._calculate_harmonic_mean,
            'geometric_mean': self._calculate_geometric_mean,
            'min_max_adjusted': self._calculate_min_max_adjusted
        }
    
    async def calculate_all_factors(self, session_id: str, 
                                   layer_scores: List[LayerScore]) -> List[FactorCalculation]:
        """
        Calculate all 28 factors from layer scores
        
        Args:
            session_id: Session identifier
            layer_scores: List of all 210 layer scores
            
        Returns:
            List of 28 FactorCalculation objects
        """
        logger.info(f"🧮 Calculating 28 factors from {len(layer_scores)} layer scores")
        
        # Group layer scores by factor
        layer_scores_by_factor = self._group_scores_by_factor(layer_scores)
        
        # Calculate all factors
        factor_calculations = []
        all_factor_ids = self.aliases.get_all_factor_ids()
        
        for factor_id in all_factor_ids:
            factor_layers = layer_scores_by_factor.get(factor_id, [])
            
            if not factor_layers:
                logger.warning(f"No layer scores found for factor {factor_id}")
                # Create default factor
                factor_calculations.append(self._create_default_factor(session_id, factor_id))
                continue
            
            try:
                calculation = await self._calculate_single_factor(
                    session_id, factor_id, factor_layers
                )
                factor_calculations.append(calculation)
            except Exception as e:
                logger.error(f"Factor calculation failed for {factor_id}: {e}")
                factor_calculations.append(self._create_default_factor(session_id, factor_id))
        
        logger.info(f"✅ Factor calculations completed: {len(factor_calculations)} factors")
        return factor_calculations
    
    async def _calculate_single_factor(self, session_id: str, factor_id: str,
                                     layer_scores: List[LayerScore]) -> FactorCalculation:
        """Calculate single factor from its layer scores"""
        
        factor_name = self.aliases.get_factor_name(factor_id)
        
        # Get layer contributions
        layer_contributions = {}
        total_weight = 0.0
        weighted_sum = 0.0
        confidence_scores = []
        
        # Equal weighting for now (can be enhanced with specific weights later)
        weight_per_layer = 1.0 / len(layer_scores) if layer_scores else 1.0
        
        for layer_score in layer_scores:
            layer_contributions[layer_score.layer_id] = float(layer_score.score)
            weighted_sum += layer_score.score * weight_per_layer
            total_weight += weight_per_layer
            confidence_scores.append(layer_score.confidence)
        
        # Calculate final factor value
        calculated_value = weighted_sum / total_weight if total_weight > 0 else 0.5
        
        # Calculate factor confidence (average of layer confidences)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Validation metrics
        validation_metrics = {
            'input_coverage': len(layer_scores) / len(self.aliases.get_layers_for_factor(factor_id)),
            'confidence_variance': self._calculate_variance(confidence_scores),
            'score_variance': self._calculate_variance([ls.score for ls in layer_scores]),
            'method_validity': 1.0
        }
        
        return FactorCalculation(
            session_id=session_id,
            factor_id=factor_id,
            factor_name=factor_name,
            calculated_value=round(calculated_value, 4),
            confidence_score=round(avg_confidence, 4),
            input_layer_count=len(layer_scores),
            calculation_method='weighted_average',
            layer_contributions=layer_contributions,
            validation_metrics=validation_metrics,
            metadata={
                'segment_id': self.aliases.get_segment_for_factor(factor_id),
                'expected_layers': len(self.aliases.get_layers_for_factor(factor_id))
            },
            created_at=datetime.now(timezone.utc)
        )
    
    def _group_scores_by_factor(self, layer_scores: List[LayerScore]) -> Dict[str, List[LayerScore]]:
        """Group layer scores by their parent factor"""
        grouped = {}
        
        for layer_score in layer_scores:
            factor_id = self.aliases.get_factor_for_layer(layer_score.layer_id)
            if not factor_id:
                logger.warning(f"No factor found for layer {layer_score.layer_id}")
                continue
            
            if factor_id not in grouped:
                grouped[factor_id] = []
            grouped[factor_id].append(layer_score)
        
        return grouped
    
    def _calculate_weighted_average(self, scores: List[float], weights: List[float]) -> float:
        """Calculate weighted average of scores"""
        if not scores or not weights or len(scores) != len(weights):
            return 0.5
        
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        weight_total = sum(weights)
        return weighted_sum / weight_total if weight_total > 0 else 0.5
    
    def _calculate_harmonic_mean(self, scores: List[float], weights: List[float]) -> float:
        """Calculate harmonic mean for scenarios where minimum scores matter more"""
        if not scores:
            return 0.5
        
        # Filter out zeros to avoid division by zero
        valid_scores = [s for s in scores if s > 0]
        if not valid_scores:
            return 0.5
        
        reciprocal_sum = sum(1/s for s in valid_scores)
        return len(valid_scores) / reciprocal_sum
    
    def _calculate_geometric_mean(self, scores: List[float], weights: List[float]) -> float:
        """Calculate geometric mean for multiplicative effects"""
        if not scores:
            return 0.5
        
        # Filter out zeros
        valid_scores = [max(s, 0.01) for s in scores]  # Use 0.01 as minimum
        
        product = 1.0
        for score in valid_scores:
            product *= score
        
        return product ** (1.0 / len(valid_scores))
    
    def _calculate_min_max_adjusted(self, scores: List[float], weights: List[float]) -> float:
        """Calculate score with emphasis on both min and max"""
        if not scores:
            return 0.5
        
        min_score = min(scores)
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        
        # Weighted combination: 30% min, 40% avg, 30% max
        return 0.3 * min_score + 0.4 * avg_score + 0.3 * max_score
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if not values or len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _create_default_factor(self, session_id: str, factor_id: str) -> FactorCalculation:
        """Create default factor calculation when layer scores unavailable"""
        
        factor_name = self.aliases.get_factor_name(factor_id) or f"Factor {factor_id}"
        
        return FactorCalculation(
            session_id=session_id,
            factor_id=factor_id,
            factor_name=factor_name,
            calculated_value=0.5,
            confidence_score=0.3,
            input_layer_count=0,
            calculation_method='default',
            layer_contributions={},
            validation_metrics={'default': True},
            metadata={'warning': 'No layer scores available'},
            created_at=datetime.now(timezone.utc)
        )

# Global engine instance
try:
    v2_factor_engine = V2FactorCalculationEngine()
    logger.info("✅ V2 Factor Calculation Engine initialized")
except Exception as e:
    logger.error(f"Failed to initialize V2 Factor Calculation Engine: {e}")
    v2_factor_engine = None

