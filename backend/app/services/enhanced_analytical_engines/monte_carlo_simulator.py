# backend/app/services/enhanced_analytical_engines/monte_carlo_simulator.py
import asyncio
import logging
import random
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from scipy import stats
import math

logger = logging.getLogger(__name__)

@dataclass
class SimulationParameters:
    """Parameters for Monte Carlo simulation"""
    iterations: int = 10000
    confidence_levels: List[float] = None
    random_seed: Optional[int] = 42
    
    def __post_init__(self):
        if self.confidence_levels is None:
            self.confidence_levels = [0.90, 0.95, 0.99]

@dataclass
class SimulationResult:
    """Result of Monte Carlo simulation"""
    mean: float
    median: float
    std_dev: float
    variance: float
    skewness: float
    kurtosis: float
    percentiles: Dict[str, float]
    confidence_intervals: Dict[float, Tuple[float, float]]
    distribution_params: Dict[str, Any]
    risk_metrics: Dict[str, float]

class MonteCarloSimulator:
    """
    Advanced Monte Carlo simulator for strategic pattern analysis
    Supports multiple probability distributions and risk assessment
    """
    
    def __init__(self, simulation_params: SimulationParameters = None):
        self.params = simulation_params or SimulationParameters()
        
        # Set random seeds for reproducibility
        random.seed(self.params.random_seed)
        np.random.seed(self.params.random_seed)
        
        logger.info(f"✅ Monte Carlo Simulator initialized with {self.params.iterations} iterations")
    
    async def run_pattern_simulation(self, 
                                   pattern_data: Dict[str, Any], 
                                   input_uncertainties: Dict[str, Dict[str, float]]) -> SimulationResult:
        """
        Run Monte Carlo simulation for strategic pattern analysis
        
        Args:
            pattern_data: Base pattern data and parameters
            input_uncertainties: Uncertainty distributions for input variables
            
        Returns:
            Comprehensive simulation results
        """
        try:
            start_time = datetime.now(timezone.utc)
            logger.info(f"Starting Monte Carlo simulation with {self.params.iterations} iterations")
            
            # Generate simulation samples
            simulation_samples = await self._generate_simulation_samples(pattern_data, input_uncertainties)
            
            # Calculate statistics
            result = self._calculate_simulation_statistics(simulation_samples)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"✅ Monte Carlo simulation completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Monte Carlo simulation failed: {e}")
            raise
    
    async def _generate_simulation_samples(self, 
                                         pattern_data: Dict[str, Any], 
                                         uncertainties: Dict[str, Dict[str, float]]) -> List[float]:
        """Generate simulation samples based on pattern data and uncertainties"""
        
        samples = []
        base_score = pattern_data.get('expected_score', 0.5)
        
        for i in range(self.params.iterations):
            # Sample from uncertainty distributions
            sampled_adjustments = {}
            
            for variable, uncertainty_params in uncertainties.items():
                distribution_type = uncertainty_params.get('distribution', 'normal')
                
                if distribution_type == 'normal':
                    mean = uncertainty_params.get('mean', 0.0)
                    std = uncertainty_params.get('std', 0.1)
                    sample = np.random.normal(mean, std)
                    
                elif distribution_type == 'triangular':
                    low = uncertainty_params.get('low', -0.2)
                    high = uncertainty_params.get('high', 0.2)
                    mode = uncertainty_params.get('mode', 0.0)
                    sample = np.random.triangular(low, mode, high)
                    
                elif distribution_type == 'beta':
                    alpha = uncertainty_params.get('alpha', 2)
                    beta = uncertainty_params.get('beta', 2)
                    scale = uncertainty_params.get('scale', 1.0)
                    sample = np.random.beta(alpha, beta) * scale
                    
                elif distribution_type == 'lognormal':
                    mu = uncertainty_params.get('mu', 0.0)
                    sigma = uncertainty_params.get('sigma', 0.3)
                    sample = np.random.lognormal(mu, sigma)
                    
                elif distribution_type == 'uniform':
                    low = uncertainty_params.get('low', -0.1)
                    high = uncertainty_params.get('high', 0.1)
                    sample = np.random.uniform(low, high)
                    
                else:
                    # Default to normal distribution
                    sample = np.random.normal(0.0, 0.1)
                
                sampled_adjustments[variable] = sample
            
            # Apply business logic to combine adjustments
            final_sample = self._apply_business_logic(base_score, sampled_adjustments, pattern_data)
            samples.append(final_sample)
        
        return samples
    
    def _apply_business_logic(self, 
                            base_score: float, 
                            adjustments: Dict[str, float], 
                            pattern_data: Dict[str, Any]) -> float:
        """Apply business logic to combine uncertainty adjustments"""
        
        adjusted_score = base_score
        
        # Market condition adjustments
        market_adjustment = adjustments.get('market_conditions', 0.0)
        adjusted_score += market_adjustment * 0.3
        
        # Competitive dynamics adjustments
        competition_adjustment = adjustments.get('competitive_dynamics', 0.0)
        adjusted_score += competition_adjustment * 0.25
        
        # Financial performance adjustments
        financial_adjustment = adjustments.get('financial_performance', 0.0)
        adjusted_score += financial_adjustment * 0.25
        
        # Execution risk adjustments
        execution_adjustment = adjustments.get('execution_risk', 0.0)
        adjusted_score += execution_adjustment * 0.2
        
        # Apply pattern-specific multipliers
        pattern_multiplier = pattern_data.get('pattern_multiplier', 1.0)
        adjusted_score *= pattern_multiplier
        
        # Industry-specific adjustments
        industry_factor = pattern_data.get('industry_factor', 1.0)
        adjusted_score *= industry_factor
        
        # Time-based decay (if applicable)
        time_decay = pattern_data.get('time_decay_factor', 1.0)
        adjusted_score *= time_decay
        
        # Clamp to valid range [0, 1]
        return max(0.0, min(1.0, adjusted_score))
    
    def _calculate_simulation_statistics(self, samples: List[float]) -> SimulationResult:
        """Calculate comprehensive statistics from simulation samples"""
        
        samples_array = np.array(samples)
        
        # Basic statistics
        mean = np.mean(samples_array)
        median = np.median(samples_array)
        std_dev = np.std(samples_array)
        variance = np.var(samples_array)
        
        # Distribution shape statistics
        skewness = stats.skew(samples_array)
        kurtosis = stats.kurtosis(samples_array)
        
        # Percentiles
        percentiles = {
            '1st': np.percentile(samples_array, 1),
            '5th': np.percentile(samples_array, 5),
            '10th': np.percentile(samples_array, 10),
            '25th': np.percentile(samples_array, 25),
            '50th': np.percentile(samples_array, 50),
            '75th': np.percentile(samples_array, 75),
            '90th': np.percentile(samples_array, 90),
            '95th': np.percentile(samples_array, 95),
            '99th': np.percentile(samples_array, 99)
        }
        
        # Confidence intervals
        confidence_intervals = {}
        for confidence_level in self.params.confidence_levels:
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            lower_bound = np.percentile(samples_array, lower_percentile)
            upper_bound = np.percentile(samples_array, upper_percentile)
            confidence_intervals[confidence_level] = (lower_bound, upper_bound)
        
        # Distribution parameters (attempt to fit normal distribution)
        try:
            # Fit normal distribution
            mu, sigma = stats.norm.fit(samples_array)
            distribution_params = {
                'normal_mu': mu,
                'normal_sigma': sigma,
                'normal_goodness_of_fit': self._calculate_goodness_of_fit(samples_array, 'normal', mu, sigma)
            }
            
            # Try other distributions
            try:
                # Fit beta distribution
                beta_params = stats.beta.fit(samples_array, floc=0, fscale=1)
                distribution_params['beta_params'] = beta_params
            except:
                pass
                
        except Exception as e:
            logger.warning(f"Distribution fitting failed: {e}")
            distribution_params = {'normal_mu': mean, 'normal_sigma': std_dev}
        
        # Risk metrics
        risk_metrics = self._calculate_risk_metrics(samples_array, mean)
        
        return SimulationResult(
            mean=mean,
            median=median,
            std_dev=std_dev,
            variance=variance,
            skewness=skewness,
            kurtosis=kurtosis,
            percentiles=percentiles,
            confidence_intervals=confidence_intervals,
            distribution_params=distribution_params,
            risk_metrics=risk_metrics
        )
    
    def _calculate_goodness_of_fit(self, samples: np.ndarray, distribution: str, *params) -> float:
        """Calculate goodness of fit for distribution"""
        try:
            if distribution == 'normal':
                mu, sigma = params
                # Kolmogorov-Smirnov test
                ks_statistic, p_value = stats.kstest(samples, lambda x: stats.norm.cdf(x, mu, sigma))
                return 1.0 - ks_statistic  # Convert to goodness measure
            else:
                return 0.5  # Default for unknown distributions
        except:
            return 0.5
    
    def _calculate_risk_metrics(self, samples: np.ndarray, mean: float) -> Dict[str, float]:
        """Calculate comprehensive risk metrics"""
        
        # Value at Risk (VaR) - 5% and 1% levels
        var_5 = np.percentile(samples, 5)
        var_1 = np.percentile(samples, 1)
        
        # Expected Shortfall (Conditional VaR)
        es_5 = np.mean(samples[samples <= var_5]) if np.sum(samples <= var_5) > 0 else var_5
        es_1 = np.mean(samples[samples <= var_1]) if np.sum(samples <= var_1) > 0 else var_1
        
        # Downside risk (below mean)
        downside_samples = samples[samples < mean]
        downside_risk = np.std(downside_samples) if len(downside_samples) > 0 else 0.0
        
        # Upside potential (above mean)
        upside_samples = samples[samples > mean]
        upside_potential = np.mean(upside_samples) - mean if len(upside_samples) > 0 else 0.0
        
        # Probability of success (above certain threshold)
        success_threshold = 0.6  # Configurable success threshold
        success_probability = np.mean(samples >= success_threshold)
        
        # Maximum drawdown simulation
        max_drawdown = self._calculate_maximum_drawdown(samples)
        
        # Volatility (same as std dev but labeled for clarity)
        volatility = np.std(samples)
        
        # Sharpe ratio approximation (assuming risk-free rate of 0.02)
        risk_free_rate = 0.02
        sharpe_ratio = (mean - risk_free_rate) / volatility if volatility > 0 else 0.0
        
        return {
            'value_at_risk_5': var_5,
            'value_at_risk_1': var_1,
            'expected_shortfall_5': es_5,
            'expected_shortfall_1': es_1,
            'downside_risk': downside_risk,
            'upside_potential': upside_potential,
            'success_probability': success_probability,
            'maximum_drawdown': max_drawdown,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio
        }
    
    def _calculate_maximum_drawdown(self, samples: np.ndarray) -> float:
        """Calculate maximum drawdown from samples"""
        try:
            # Sort samples to simulate time series
            cumulative_returns = np.cumsum(np.diff(np.sort(samples)))
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = cumulative_returns - running_max
            max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0.0
            return abs(max_drawdown)
        except:
            return 0.0
    
    async def run_scenario_analysis(self, 
                                  base_scenario: Dict[str, Any],
                                  scenario_variations: List[Dict[str, Any]]) -> Dict[str, SimulationResult]:
        """Run scenario analysis with multiple scenarios"""
        
        scenario_results = {}
        
        for i, scenario in enumerate(scenario_variations):
            scenario_name = scenario.get('name', f'Scenario_{i+1}')
            
            # Merge base scenario with variations
            combined_scenario = {**base_scenario, **scenario}
            uncertainties = combined_scenario.get('uncertainties', {})
            
            # Run simulation for this scenario
            result = await self.run_pattern_simulation(combined_scenario, uncertainties)
            scenario_results[scenario_name] = result
            
            logger.info(f"✅ Completed scenario analysis: {scenario_name}")
        
        return scenario_results

from datetime import datetime, timezone

__all__ = ['MonteCarloSimulator', 'SimulationParameters', 'SimulationResult']
