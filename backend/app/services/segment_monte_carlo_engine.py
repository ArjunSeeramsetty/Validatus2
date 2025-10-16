"""
Segment-Specific Monte Carlo Engine
Generates Monte Carlo scenarios with segment-specific counts and KPI distributions
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class MonteCarloScenario:
    """Monte Carlo scenario result for a specific pattern"""
    scenario_id: str
    pattern_id: str
    pattern_name: str
    segment: str
    strategic_response: str
    kpi_results: Dict[str, Any]
    probability_success: float
    confidence_interval: Tuple[float, float]
    iterations_run: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert tuple to list for JSON
        data['confidence_interval'] = list(data['confidence_interval'])
        return data


class SegmentMonteCarloEngine:
    """Monte Carlo engine that generates segment-specific scenarios"""
    
    def __init__(self):
        self.iterations = 1000
        self.required_scenarios = {
            'market': 4,
            'consumer': 4,
            'brand': 4,
            'product': 3,
            'experience': 2
        }
        logger.info("SegmentMonteCarloEngine initialized with segment-specific scenario counts")
    
    async def generate_segment_scenarios(self, 
                                       segment: str, 
                                       matched_patterns: List[Dict],
                                       factor_scores: Dict[str, float]) -> List[MonteCarloScenario]:
        """Generate Monte Carlo scenarios for a specific segment"""
        
        required_count = self.required_scenarios.get(segment.lower(), 4)
        scenarios = []
        
        logger.info(f"Generating {required_count} Monte Carlo scenarios for {segment} segment")
        
        # Use top patterns based on required scenario count
        top_patterns = sorted(
            matched_patterns, 
            key=lambda x: x.get('confidence_adjusted', x.get('confidence', 0)), 
            reverse=True
        )[:required_count]
        
        # If we don't have enough patterns, generate default ones
        if len(top_patterns) < required_count:
            logger.warning(f"Only {len(top_patterns)} patterns available, generating {required_count - len(top_patterns)} default patterns")
            top_patterns.extend(self._generate_default_patterns(segment, required_count - len(top_patterns)))
        
        # Generate Monte Carlo scenario for each pattern
        for i, pattern in enumerate(top_patterns):
            scenario = await self._run_monte_carlo_for_pattern(
                segment, pattern, factor_scores, scenario_index=i+1
            )
            scenarios.append(scenario)
        
        logger.info(f"Successfully generated {len(scenarios)} scenarios for {segment}")
        return scenarios
    
    async def _run_monte_carlo_for_pattern(self,
                                         segment: str,
                                         pattern: Dict,
                                         factor_scores: Dict[str, float],
                                         scenario_index: int) -> MonteCarloScenario:
        """Run Monte Carlo simulation for a single pattern"""
        
        kpi_anchors = pattern.get('kpi_anchors', {})
        
        if not kpi_anchors:
            # Generate default KPI anchors based on segment and pattern type
            kpi_anchors = self._generate_default_kpi_anchors(segment, pattern)
        
        kpi_results = {}
        
        for kpi_name, kpi_config in kpi_anchors.items():
            distribution = kpi_config.get('distribution', 'normal')
            params = kpi_config.get('params', [0, 1])
            bounds = kpi_config.get('bounds', [None, None])
            
            # Run simulation
            samples = self._generate_samples(distribution, params, self.iterations)
            
            # Apply bounds
            if bounds[0] is not None:
                samples = np.maximum(samples, bounds[0])
            if bounds[1] is not None:
                samples = np.minimum(samples, bounds[1])
            
            # Calculate statistics
            kpi_results[kpi_name] = {
                'mean': float(np.mean(samples)),
                'median': float(np.median(samples)),
                'std': float(np.std(samples)),
                'min': float(np.min(samples)),
                'max': float(np.max(samples)),
                'confidence_interval_95': [
                    float(np.percentile(samples, 2.5)),
                    float(np.percentile(samples, 97.5))
                ],
                'confidence_interval_68': [
                    float(np.percentile(samples, 16)),
                    float(np.percentile(samples, 84))
                ],
                'probability_positive': float(np.mean(samples > 0)),
                'probability_target': float(np.mean(samples > params[0])) if len(params) > 0 else 0.5
            }
        
        # Calculate overall success probability
        success_prob = np.mean([
            kpi_results[kpi]['probability_positive'] 
            for kpi in kpi_results.keys()
        ]) if kpi_results else 0.5
        
        # Get overall confidence interval from mean of KPIs
        all_means = [kpi_results[kpi]['mean'] for kpi in kpi_results.keys()]
        if all_means:
            overall_ci = (
                float(min(all_means)),
                float(max(all_means))
            )
        else:
            overall_ci = (0.0, 1.0)
        
        return MonteCarloScenario(
            scenario_id=f"{segment}_scenario_{scenario_index}",
            pattern_id=pattern.get('id', f'P{scenario_index:03d}'),
            pattern_name=pattern.get('name', f'Strategic Opportunity {scenario_index}'),
            segment=segment,
            strategic_response=pattern.get('strategic_response', 'Strategic opportunity identified from analysis'),
            kpi_results=kpi_results,
            probability_success=success_prob,
            confidence_interval=overall_ci,
            iterations_run=self.iterations
        )
    
    def _generate_samples(self, distribution: str, params: List[float], size: int) -> np.ndarray:
        """Generate random samples based on distribution type"""
        
        try:
            if distribution == 'normal':
                mean = params[0] if len(params) > 0 else 20
                std = params[1] if len(params) > 1 else 8
                return np.random.normal(mean, std, size)
            
            elif distribution == 'triangular':
                left = params[0] if len(params) > 0 else 10
                mode = params[1] if len(params) > 1 else 20
                right = params[2] if len(params) > 2 else 35
                return np.random.triangular(left, mode, right, size)
            
            elif distribution == 'uniform':
                low = params[0] if len(params) > 0 else 10
                high = params[1] if len(params) > 1 else 30
                return np.random.uniform(low, high, size)
            
            elif distribution == 'beta':
                alpha = params[0] if len(params) > 0 else 2
                beta = params[1] if len(params) > 1 else 5
                # Scale beta distribution to percentage range
                return np.random.beta(alpha, beta, size) * 50 + 10
            
            elif distribution == 'lognormal':
                mean = params[0] if len(params) > 0 else 2.5
                sigma = params[1] if len(params) > 1 else 0.5
                return np.random.lognormal(mean, sigma, size)
            
            else:
                # Default to normal distribution
                return np.random.normal(20, 8, size)
        
        except Exception as e:
            logger.warning(f"Error generating {distribution} samples: {e}. Using normal distribution.")
            return np.random.normal(20, 8, size)
    
    def _generate_default_kpi_anchors(self, segment: str, pattern: Dict) -> Dict[str, Any]:
        """Generate default KPI anchors when pattern doesn't have them"""
        
        pattern_type = pattern.get('type', 'Opportunity')
        
        # Segment-specific KPIs
        segment_kpis = {
            'market': {
                'market_share_increase_pp': {
                    'distribution': 'triangular',
                    'params': [8, 15, 25],
                    'bounds': [5, 35]
                },
                'revenue_growth_pct': {
                    'distribution': 'normal',
                    'params': [20, 8],
                    'bounds': [5, 50]
                },
                'market_penetration_rate_pp': {
                    'distribution': 'triangular',
                    'params': [12, 20, 30],
                    'bounds': [8, 40]
                }
            },
            'consumer': {
                'conversion_rate_increase_pp': {
                    'distribution': 'triangular',
                    'params': [10, 18, 30],
                    'bounds': [5, 40]
                },
                'customer_lifetime_value_increase_pct': {
                    'distribution': 'normal',
                    'params': [25, 10],
                    'bounds': [10, 60]
                },
                'retention_rate_increase_pp': {
                    'distribution': 'triangular',
                    'params': [15, 22, 35],
                    'bounds': [8, 45]
                }
            },
            'product': {
                'feature_adoption_rate_pp': {
                    'distribution': 'triangular',
                    'params': [20, 35, 55],
                    'bounds': [15, 70]
                },
                'price_premium_pct': {
                    'distribution': 'normal',
                    'params': [18, 6],
                    'bounds': [8, 35]
                },
                'quality_perception_increase_pp': {
                    'distribution': 'triangular',
                    'params': [18, 28, 40],
                    'bounds': [12, 50]
                }
            },
            'brand': {
                'brand_awareness_increase_pp': {
                    'distribution': 'triangular',
                    'params': [15, 25, 40],
                    'bounds': [10, 50]
                },
                'nps_improvement_pts': {
                    'distribution': 'normal',
                    'params': [12, 5],
                    'bounds': [5, 25]
                },
                'brand_trust_score_increase_pp': {
                    'distribution': 'triangular',
                    'params': [10, 18, 30],
                    'bounds': [5, 35]
                }
            },
            'experience': {
                'satisfaction_score_increase_pts': {
                    'distribution': 'triangular',
                    'params': [8, 15, 25],
                    'bounds': [5, 30]
                },
                'customer_retention_increase_pp': {
                    'distribution': 'normal',
                    'params': [18, 7],
                    'bounds': [8, 35]
                },
                'engagement_time_increase_pct': {
                    'distribution': 'triangular',
                    'params': [25, 40, 60],
                    'bounds': [15, 80]
                }
            }
        }
        
        return segment_kpis.get(segment.lower(), segment_kpis['market'])
    
    def _generate_default_patterns(self, segment: str, count: int) -> List[Dict]:
        """Generate default patterns when not enough are matched"""
        
        default_patterns = []
        
        segment_defaults = {
            'market': [
                {'id': 'PDEF001', 'name': 'Market Expansion Opportunity', 'type': 'Opportunity', 
                 'strategic_response': 'Expand into adjacent markets with proven product-market fit', 'confidence': 0.65},
                {'id': 'PDEF002', 'name': 'Competitive Positioning', 'type': 'Adaptation',
                 'strategic_response': 'Strengthen competitive moat through differentiation', 'confidence': 0.60}
            ],
            'consumer': [
                {'id': 'PDEF003', 'name': 'Customer Acquisition', 'type': 'Opportunity',
                 'strategic_response': 'Optimize conversion funnel and reduce acquisition costs', 'confidence': 0.68},
                {'id': 'PDEF004', 'name': 'Loyalty Enhancement', 'type': 'Success',
                 'strategic_response': 'Build customer loyalty through value-added services', 'confidence': 0.62}
            ],
            'product': [
                {'id': 'PDEF005', 'name': 'Product Innovation', 'type': 'Opportunity',
                 'strategic_response': 'Develop next-generation features based on user feedback', 'confidence': 0.70},
                {'id': 'PDEF006', 'name': 'Quality Excellence', 'type': 'Success',
                 'strategic_response': 'Maintain premium quality standards across product line', 'confidence': 0.65}
            ],
            'brand': [
                {'id': 'PDEF007', 'name': 'Brand Awareness', 'type': 'Opportunity',
                 'strategic_response': 'Increase brand visibility through strategic marketing', 'confidence': 0.63},
                {'id': 'PDEF008', 'name': 'Trust Building', 'type': 'Success',
                 'strategic_response': 'Enhance brand trust through transparency and authenticity', 'confidence': 0.67}
            ],
            'experience': [
                {'id': 'PDEF009', 'name': 'Journey Optimization', 'type': 'Opportunity',
                 'strategic_response': 'Streamline customer journey to reduce friction points', 'confidence': 0.66},
                {'id': 'PDEF010', 'name': 'Service Excellence', 'type': 'Success',
                 'strategic_response': 'Deliver exceptional service across all touchpoints', 'confidence': 0.64}
            ]
        }
        
        patterns_pool = segment_defaults.get(segment.lower(), segment_defaults['market'])
        
        for i in range(min(count, len(patterns_pool))):
            default_patterns.append(patterns_pool[i])
        
        return default_patterns

