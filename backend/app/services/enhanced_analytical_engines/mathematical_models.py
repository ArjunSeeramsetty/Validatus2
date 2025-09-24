# backend/app/services/enhanced_analytical_engines/mathematical_models.py
import math
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class NormalizationMethod(Enum):
    """Normalization methods for factor scores"""
    LOGISTIC = "logistic"
    SIGMOID = "sigmoid"
    MIN_MAX = "min_max"
    Z_SCORE = "z_score"
    ROBUST = "robust"

@dataclass
class RobustnessMultipliers:
    """Robustness multipliers for enhanced factor calculations"""
    s_gen: float = 0.95    # Generalizability strength
    c_stab: float = 0.9    # Confidence stability  
    v_evolve: float = 0.02 # Volatility evolution
    temporal_decay: float = 0.98  # Time-based decay
    market_sensitivity: float = 1.05  # Market condition sensitivity

@dataclass
class FactorWeight:
    """Weight configuration for individual factors"""
    base_weight: float
    market_adjustment: float = 1.0
    sector_adjustment: float = 1.0
    temporal_adjustment: float = 1.0
    confidence_adjustment: float = 1.0
    
    @property
    def effective_weight(self) -> float:
        """Calculate effective weight with all adjustments"""
        return (self.base_weight * 
                self.market_adjustment * 
                self.sector_adjustment * 
                self.temporal_adjustment * 
                self.confidence_adjustment)

class MathematicalModels:
    """Advanced mathematical models for factor calculations"""
    
    def __init__(self):
        self.robustness = RobustnessMultipliers()
        
        # Factor weights (F1-F28) with mathematical precision
        self.factor_weights = self._initialize_factor_weights()
        
    def _initialize_factor_weights(self) -> Dict[str, FactorWeight]:
        """Initialize mathematically calibrated factor weights"""
        return {
            # Market Factors (F1-F7) - Total weight: 1.0
            'F1_market_size': FactorWeight(0.18),
            'F2_market_growth': FactorWeight(0.16),
            'F3_market_maturity': FactorWeight(0.14),
            'F4_competitive_intensity': FactorWeight(0.15),
            'F5_barrier_to_entry': FactorWeight(0.13),
            'F6_regulatory_environment': FactorWeight(0.12),
            'F7_economic_sensitivity': FactorWeight(0.12),
            
            # Product Factors (F8-F14) - Total weight: 1.0  
            'F8_product_differentiation': FactorWeight(0.17),
            'F9_innovation_capability': FactorWeight(0.16),
            'F10_quality_reliability': FactorWeight(0.15),
            'F11_scalability_potential': FactorWeight(0.14),
            'F12_customer_stickiness': FactorWeight(0.13),
            'F13_pricing_power': FactorWeight(0.13),
            'F14_lifecycle_position': FactorWeight(0.12),
            
            # Financial Factors (F15-F21) - Total weight: 1.0
            'F15_revenue_growth': FactorWeight(0.18),
            'F16_profitability_margins': FactorWeight(0.17),
            'F17_cash_flow_generation': FactorWeight(0.16),
            'F18_capital_efficiency': FactorWeight(0.15),
            'F19_financial_stability': FactorWeight(0.14),
            'F20_cost_structure': FactorWeight(0.11),
            'F21_working_capital': FactorWeight(0.09),
            
            # Strategic Factors (F22-F28) - Total weight: 1.0
            'F22_brand_strength': FactorWeight(0.16),
            'F23_management_quality': FactorWeight(0.15),
            'F24_strategic_positioning': FactorWeight(0.15),
            'F25_operational_excellence': FactorWeight(0.14),
            'F26_digital_transformation': FactorWeight(0.14),
            'F27_sustainability_esg': FactorWeight(0.13),
            'F28_strategic_flexibility': FactorWeight(0.13)
        }
    
    def logistic_normalize(self, raw_score: float, sensitivity: float = 5.0) -> float:
        """
        Enhanced logistic normalization: 1 / (1 + e^(-sensitivity * (raw_score - 0.5)))
        
        Args:
            raw_score: Raw factor score (typically 0-1 range)
            sensitivity: Sensitivity parameter (default 5.0 for McKinsey precision)
        
        Returns:
            Normalized score between 0 and 1
        """
        try:
            # Clamp input to prevent overflow
            clamped_score = max(-10, min(10, raw_score))
            
            # Apply logistic function
            normalized = 1.0 / (1.0 + math.exp(-sensitivity * (clamped_score - 0.5)))
            
            # Apply robustness multiplier
            robust_normalized = normalized * self.robustness.s_gen
            
            return max(0.0, min(1.0, robust_normalized))
            
        except (OverflowError, ValueError) as e:
            logger.warning(f"Logistic normalization error for score {raw_score}: {e}")
            return 0.5  # Return neutral score on error
    
    def sigmoid_normalize(self, raw_score: float, steepness: float = 2.0) -> float:
        """Alternative sigmoid normalization for specific factors"""
        try:
            return 1.0 / (1.0 + math.exp(-steepness * raw_score))
        except (OverflowError, ValueError):
            return 0.5
    
    def robust_normalize(self, scores: List[float]) -> List[float]:
        """Robust normalization using percentile-based scaling"""
        if not scores:
            return []
        
        # Calculate robust statistics
        scores_array = np.array(scores)
        q25, q75 = np.percentile(scores_array, [25, 75])
        iqr = q75 - q25
        
        if iqr == 0:
            return [0.5] * len(scores)
        
        # Robust scaling
        normalized = []
        for score in scores:
            robust_score = (score - q25) / iqr
            # Clamp to [0, 1] and apply logistic smoothing
            clamped = max(0, min(1, robust_score))
            normalized.append(self.logistic_normalize(clamped))
        
        return normalized
    
    def apply_temporal_decay(self, score: float, days_old: int) -> float:
        """Apply temporal decay to factor scores"""
        decay_factor = self.robustness.temporal_decay ** (days_old / 30.0)  # Monthly decay
        return score * decay_factor
    
    def calculate_confidence_interval(self, score: float, sample_size: int, confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for factor scores"""
        # Standard error estimation
        std_error = math.sqrt((score * (1 - score)) / sample_size) if sample_size > 0 else 0.1
        
        # Z-score for confidence level
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z_score = z_scores.get(confidence_level, 1.96)
        
        # Calculate interval
        margin_error = z_score * std_error
        lower_bound = max(0.0, score - margin_error)
        upper_bound = min(1.0, score + margin_error)
        
        return (lower_bound, upper_bound)
    
    def calculate_composite_score(self, factor_scores: Dict[str, float], category: str) -> float:
        """Calculate weighted composite score for factor category"""
        total_score = 0.0
        total_weight = 0.0
        
        # Get category factors
        category_factors = self._get_category_factors(category)
        
        for factor_id in category_factors:
            if factor_id in factor_scores and factor_id in self.factor_weights:
                score = factor_scores[factor_id]
                weight = self.factor_weights[factor_id].effective_weight
                
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _get_category_factors(self, category: str) -> List[str]:
        """Get factor IDs for a specific category"""
        category_mappings = {
            'market': [f'F{i}_' for i in range(1, 8)],
            'product': [f'F{i}_' for i in range(8, 15)],
            'financial': [f'F{i}_' for i in range(15, 22)],
            'strategic': [f'F{i}_' for i in range(22, 29)]
        }
        
        factor_prefixes = category_mappings.get(category.lower(), [])
        return [factor_id for factor_id in self.factor_weights.keys() 
                if any(factor_id.startswith(prefix) for prefix in factor_prefixes)]

__all__ = ['MathematicalModels', 'NormalizationMethod', 'RobustnessMultipliers', 'FactorWeight']
