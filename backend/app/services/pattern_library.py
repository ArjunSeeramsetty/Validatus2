"""
Strategic patterns library for simulation enhancement
"""

from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class StrategyPatternLibrary:
    """Library of strategic patterns that modify simulations"""
    
    def __init__(self):
        self.patterns = {
            'seasonal_install_compression': {
                'factors': ['F1', 'F3', 'F4'],  # Market growth, tech adoption, regulatory
                'preconditions': ['installer_capacity_visible', 'seasonal_market'],
                'mc_levers': ['conversion', 'lead_time', 'cac'],
                'effect_priors': {
                    'lead_time': ('normal', -0.30, 0.08),
                    'conversion': ('triangular', 0.03, 0.06, 0.12)
                },
                'correlation': {'lead_time': {'conversion': -0.6}},
                'confidence': 0.72,
                'transferability': 0.85,
                'description': 'Seasonal compression in installation capacity affects lead times and conversion rates'
            },
            'tariff_shock_pattern': {
                'factors': ['F4', 'F5'],  # Regulatory, economic
                'preconditions': ['international_supply_chain'],
                'mc_levers': ['cogs', 'margin'],
                'effect_priors': {
                    'cogs': ('normal', 0.25, 0.15),
                    'margin': ('normal', -0.20, 0.10)
                },
                'correlation': {'cogs': {'margin': -0.7}},
                'confidence': 0.68,
                'transferability': 0.60,
                'description': 'Tariff shocks impact supply chain costs and margins'
            },
            'technology_adoption_s_curve': {
                'factors': ['F3', 'F1'],  # Tech adoption, market growth
                'preconditions': ['new_technology', 'market_education_required'],
                'mc_levers': ['adoption_rate', 'conversion'],
                'effect_priors': {
                    'adoption_rate': ('beta', 2, 5),  # Slow initial, then acceleration
                    'conversion': ('normal', 0.05, 0.02)
                },
                'correlation': {'adoption_rate': {'conversion': 0.4}},
                'confidence': 0.75,
                'transferability': 0.70,
                'description': 'S-curve adoption pattern for new technologies'
            },
            'competitive_response_pattern': {
                'factors': ['F2', 'F4'],  # Competition, regulatory
                'preconditions': ['established_competitors', 'price_sensitive_market'],
                'mc_levers': ['margin', 'conversion', 'cac'],
                'effect_priors': {
                    'margin': ('normal', -0.15, 0.08),
                    'conversion': ('normal', -0.10, 0.05),
                    'cac': ('normal', 0.20, 0.10)
                },
                'correlation': {'margin': {'conversion': 0.5, 'cac': -0.3}},
                'confidence': 0.65,
                'transferability': 0.80,
                'description': 'Competitive response to market entry affects pricing and acquisition costs'
            },
            'regulatory_uncertainty_pattern': {
                'factors': ['F4', 'F5'],  # Regulatory, economic
                'preconditions': ['pending_regulations', 'industry_oversight'],
                'mc_levers': ['adoption_rate', 'margin', 'conversion'],
                'effect_priors': {
                    'adoption_rate': ('triangular', -0.20, -0.05, 0.10),
                    'margin': ('normal', -0.10, 0.15),
                    'conversion': ('normal', -0.15, 0.08)
                },
                'correlation': {'adoption_rate': {'conversion': 0.6}},
                'confidence': 0.60,
                'transferability': 0.55,
                'description': 'Regulatory uncertainty creates market hesitation and adoption delays'
            },
            'economic_cycle_pattern': {
                'factors': ['F5', 'F1'],  # Economic, market growth
                'preconditions': ['cyclical_industry', 'discretionary_spending'],
                'mc_levers': ['adoption_rate', 'conversion', 'margin'],
                'effect_priors': {
                    'adoption_rate': ('normal', 0.20, 0.12),
                    'conversion': ('normal', 0.15, 0.08),
                    'margin': ('normal', 0.10, 0.06)
                },
                'correlation': {'adoption_rate': {'conversion': 0.7}, 'conversion': {'margin': 0.4}},
                'confidence': 0.70,
                'transferability': 0.75,
                'description': 'Economic upswing drives increased adoption and conversion rates'
            }
        }
    
    def get_applicable_patterns(self, factors: List[str], 
                               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get patterns applicable to current analysis"""
        applicable = []
        
        for pattern_id, pattern_config in self.patterns.items():
            # Check factor overlap
            factor_overlap = len(set(factors) & set(pattern_config['factors']))
            
            # Check preconditions
            preconditions_met = all(
                context.get(precond, False) 
                for precond in pattern_config['preconditions']
            )
            
            if factor_overlap > 0 and preconditions_met:
                activation_weight = (
                    (factor_overlap / len(pattern_config['factors'])) * 
                    pattern_config['confidence'] * 
                    pattern_config['transferability']
                )
                
                applicable.append({
                    'pattern_id': pattern_id,
                    'config': pattern_config,
                    'activation_weight': activation_weight,
                    'factor_overlap': factor_overlap,
                    'preconditions_met': preconditions_met
                })
        
        # Sort by activation weight
        applicable.sort(key=lambda x: x['activation_weight'], reverse=True)
        
        return applicable
    
    def apply_pattern_effects(self, pattern_id: str, base_values: Dict[str, float], 
                            context: Dict[str, Any]) -> Dict[str, float]:
        """Apply pattern effects to base simulation values"""
        if pattern_id not in self.patterns:
            logger.warning(f"Pattern {pattern_id} not found")
            return base_values
        
        pattern_config = self.patterns[pattern_id]
        modified_values = base_values.copy()
        
        # Apply effect priors
        for lever, (dist_type, *params) in pattern_config['effect_priors'].items():
            if lever in modified_values:
                effect = self._sample_effect(dist_type, params)
                modified_values[lever] = modified_values[lever] * (1 + effect)
        
        # Apply correlations
        for lever, correlations in pattern_config['correlation'].items():
            if lever in modified_values:
                for correlated_lever, correlation in correlations.items():
                    if correlated_lever in modified_values:
                        # Apply correlation effect
                        correlation_effect = correlation * 0.1 * modified_values[lever]
                        modified_values[correlated_lever] += correlation_effect
        
        return modified_values
    
    def _sample_effect(self, dist_type: str, params: Tuple) -> float:
        """Sample effect value from distribution"""
        import numpy as np
        
        if dist_type == 'normal':
            return np.random.normal(params[0], params[1])
        elif dist_type == 'triangular':
            return np.random.triangular(params[0], params[1], params[2])
        elif dist_type == 'beta':
            return np.random.beta(params[0], params[1]) - 0.5  # Center around 0
        else:
            return 0.0
    
    def get_pattern_summary(self, pattern_id: str) -> Dict[str, Any]:
        """Get summary information for a pattern"""
        if pattern_id not in self.patterns:
            return {}
        
        pattern = self.patterns[pattern_id]
        return {
            'id': pattern_id,
            'description': pattern['description'],
            'confidence': pattern['confidence'],
            'transferability': pattern['transferability'],
            'factors': pattern['factors'],
            'preconditions': pattern['preconditions'],
            'mc_levers': pattern['mc_levers']
        }
    
    def get_all_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get all available patterns"""
        return {
            pattern_id: self.get_pattern_summary(pattern_id)
            for pattern_id in self.patterns.keys()
        }
    
    def validate_pattern_context(self, context: Dict[str, Any]) -> Dict[str, bool]:
        """Validate which preconditions are met in the given context"""
        all_preconditions = set()
        for pattern in self.patterns.values():
            all_preconditions.update(pattern['preconditions'])
        
        return {
            precond: context.get(precond, False)
            for precond in all_preconditions
        }
    
    def suggest_context_improvements(self, context: Dict[str, Any]) -> List[str]:
        """Suggest context improvements to activate more patterns"""
        suggestions = []
        
        # Check for missing common preconditions
        common_preconditions = [
            'installer_capacity_visible',
            'seasonal_market',
            'international_supply_chain',
            'new_technology',
            'market_education_required',
            'established_competitors',
            'price_sensitive_market',
            'pending_regulations',
            'industry_oversight',
            'cyclical_industry',
            'discretionary_spending'
        ]
        
        for precond in common_preconditions:
            if not context.get(precond, False):
                suggestions.append(f"Consider adding '{precond}' to context for more pattern activation")
        
        return suggestions
