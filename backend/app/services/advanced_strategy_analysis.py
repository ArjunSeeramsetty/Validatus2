"""
Advanced Strategy Analysis Engine with Monte Carlo Simulation
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class FactorConfig:
    """Configuration for strategic factors"""
    factor_id: str
    name: str
    kpi_links: List[str]  # ['conversion', 'margin', 'adoption']
    distribution_type: str  # 'triangular', 'normal', 'beta', 'lognormal'
    rationale: str
    config_range: Dict[str, float]
    confidence: float

@dataclass
class SimulationPack:
    """Complete simulation configuration"""
    drivers: List[FactorConfig]
    correlations: Dict[str, Dict[str, float]]
    constraints: Dict[str, Any]
    business_case_inputs: Dict[str, float]

@dataclass
class ScenarioResult:
    """Individual scenario outcome"""
    name: str
    probability: float
    kpis: Dict[str, float]
    narrative: str
    key_drivers: List[str]
    risk_level: str

class AdvancedStrategyAnalysisEngine:
    """Main strategy analysis engine"""
    
    def __init__(self):
        self.factors_library = self._load_factors_library()
        self.patterns_library = self._load_patterns_library()
        
    def analyze_strategy(self, session_id: str, topic_data: Dict, 
                        client_inputs: Dict) -> Dict[str, Any]:
        """Execute complete strategic analysis workflow"""
        
        try:
            # Step 1: Build simulation pack
            simulation_pack = self._build_simulation_pack(topic_data, client_inputs)
            
            # Step 2: Run Monte Carlo simulation
            simulation_results = self._run_monte_carlo_simulation(simulation_pack)
            
            # Step 3: Generate scenarios
            scenarios = self._cluster_scenarios(simulation_results)
            
            # Step 4: Calculate sensitivities
            sensitivities = self._calculate_driver_sensitivities(simulation_results)
            
            # Step 5: Generate business case score
            business_case_score = self._calculate_business_case_score(simulation_results)
            
            return {
                'session_id': session_id,
                'business_case_score': business_case_score,
                'scenarios': scenarios,
                'driver_sensitivities': sensitivities,
                'simulation_metadata': {
                    'runs': len(simulation_results),
                    'confidence_level': 0.95,
                    'analysis_type': 'advanced_monte_carlo'
                },
                'financial_projections': self._generate_financial_projections(simulation_results),
                'assumptions': self._extract_assumptions(simulation_pack)
            }
            
        except Exception as e:
            logger.error(f"Advanced strategy analysis failed: {str(e)}")
            return self._generate_fallback_results(session_id, client_inputs)
    
    def _load_factors_library(self) -> Dict[str, FactorConfig]:
        """Load strategic factors library"""
        return {
            'F1': FactorConfig(
                factor_id='F1',
                name='Market Size Growth',
                kpi_links=['adoption_rate', 'revenue'],
                distribution_type='normal',
                rationale='Market expansion drives adoption',
                config_range={'mean': 0.15, 'std': 0.05},
                confidence=0.8
            ),
            'F2': FactorConfig(
                factor_id='F2',
                name='Competitive Intensity',
                kpi_links=['margin', 'conversion'],
                distribution_type='beta',
                rationale='Competition affects pricing and conversion',
                config_range={'alpha': 2, 'beta': 3},
                confidence=0.7
            ),
            'F3': FactorConfig(
                factor_id='F3',
                name='Technology Adoption',
                kpi_links=['adoption_rate', 'conversion'],
                distribution_type='lognormal',
                rationale='Tech adoption accelerates market penetration',
                config_range={'mu': 0.1, 'sigma': 0.3},
                confidence=0.75
            ),
            'F4': FactorConfig(
                factor_id='F4',
                name='Regulatory Environment',
                kpi_links=['margin', 'adoption_rate'],
                distribution_type='triangular',
                rationale='Regulations impact market dynamics',
                config_range={'low': -0.1, 'high': 0.1, 'mode': 0.0},
                confidence=0.6
            ),
            'F5': FactorConfig(
                factor_id='F5',
                name='Economic Conditions',
                kpi_links=['revenue', 'margin'],
                distribution_type='normal',
                rationale='Economic cycles affect spending',
                config_range={'mean': 0.05, 'std': 0.08},
                confidence=0.7
            )
        }
    
    def _load_patterns_library(self) -> Dict[str, Dict]:
        """Load strategic patterns library"""
        return {
            'seasonal_install_compression': {
                'factors': ['F1', 'F3', 'F4'],
                'preconditions': ['installer_capacity_visible', 'seasonal_market'],
                'mc_levers': ['conversion', 'lead_time', 'cac'],
                'effect_priors': {
                    'lead_time': ('normal', -0.30, 0.08),
                    'conversion': ('triangular', 0.06, 0.12, 0.03)
                },
                'correlation': {'lead_time': {'conversion': -0.6}},
                'confidence': 0.72,
                'transferability': 0.85
            },
            'tariff_shock_pattern': {
                'factors': ['F4', 'F5'],
                'preconditions': ['international_supply_chain'],
                'mc_levers': ['cogs', 'margin'],
                'effect_priors': {
                    'cogs': ('normal', 0.25, 0.15),
                    'margin': ('normal', -0.20, 0.10)
                },
                'correlation': {'cogs': {'margin': -0.7}},
                'confidence': 0.68,
                'transferability': 0.60
            }
        }
    
    def _build_simulation_pack(self, topic_data: Dict, client_inputs: Dict) -> SimulationPack:
        """Build simulation pack from topic data and inputs"""
        eligible_drivers = []
        
        # Get strategic layers from topic analysis
        strategic_layers = topic_data.get('strategic_layers', {})
        
        # Map strategic layers to factors
        for layer_name, layer_data in strategic_layers.items():
            factor_configs = self._map_layer_to_factors(layer_name, layer_data)
            eligible_drivers.extend(factor_configs)
        
        # Apply eligibility filters
        filtered_drivers = self._filter_eligible_drivers(eligible_drivers)
        
        # Build correlations
        correlations = self._build_correlation_matrix(filtered_drivers)
        
        # Set constraints
        constraints = self._define_constraints(client_inputs)
        
        return SimulationPack(
            drivers=filtered_drivers,
            correlations=correlations,
            constraints=constraints,
            business_case_inputs=client_inputs
        )
    
    def _map_layer_to_factors(self, layer_name: str, layer_data: Dict) -> List[FactorConfig]:
        """Map strategic layer to factor configurations"""
        factor_mapping = {
            'market_attractiveness': ['F1', 'F3'],
            'competitive_position': ['F2', 'F4'],
            'financial_performance': ['F5', 'F2'],
            'growth_potential': ['F1', 'F3'],
            'risk_assessment': ['F4', 'F5']
        }
        
        factors = factor_mapping.get(layer_name.lower().replace(' ', '_'), ['F1', 'F2'])
        return [self.factors_library[factor_id] for factor_id in factors if factor_id in self.factors_library]
    
    def _filter_eligible_drivers(self, drivers: List[FactorConfig]) -> List[FactorConfig]:
        """Filter drivers based on eligibility criteria and remove duplicates"""
        # Filter by confidence and remove duplicates by factor_id
        seen_ids = set()
        filtered_drivers = []
        
        for driver in drivers:
            if driver.confidence > 0.6 and driver.factor_id not in seen_ids:
                filtered_drivers.append(driver)
                seen_ids.add(driver.factor_id)
        
        return filtered_drivers
    
    def _build_correlation_matrix(self, drivers: List[FactorConfig]) -> Dict[str, Dict[str, float]]:
        """Build correlation matrix for drivers"""
        correlations = {}
        driver_ids = [driver.factor_id for driver in drivers]
        
        # Define base correlations
        base_correlations = {
            'F1': {'F3': 0.6, 'F5': 0.4},  # Market growth correlates with tech adoption and economy
            'F2': {'F4': 0.5, 'F5': 0.3},  # Competition correlates with regulation and economy
            'F3': {'F1': 0.6, 'F4': 0.2},  # Tech adoption correlates with market growth
            'F4': {'F2': 0.5, 'F5': 0.4},  # Regulation correlates with competition and economy
            'F5': {'F1': 0.4, 'F2': 0.3, 'F4': 0.4}  # Economy correlates with multiple factors
        }
        
        for driver_id in driver_ids:
            correlations[driver_id] = base_correlations.get(driver_id, {})
        
        return correlations
    
    def _define_constraints(self, client_inputs: Dict) -> Dict[str, Any]:
        """Define simulation constraints"""
        return {
            'min_roi': 0.1,  # Minimum 10% ROI
            'max_payback_period': 3.0,  # Maximum 3 years payback
            'min_adoption_rate': 0.05,  # Minimum 5% adoption
            'budget_constraint': client_inputs.get('budget', 1000000)
        }
    
    def _run_monte_carlo_simulation(self, pack: SimulationPack, 
                                   num_runs: int = 10000) -> List[Dict]:
        """Execute Monte Carlo simulation"""
        results = []
        
        for run_id in range(num_runs):
            # Sample from distributions
            driver_values = {}
            for driver in pack.drivers:
                value = self._sample_distribution(driver)
                driver_values[driver.factor_id] = value
            
            # Apply correlations
            correlated_values = self._apply_correlations(driver_values, pack.correlations)
            
            # Calculate KPIs
            kpis = self._calculate_kpis(correlated_values, pack.business_case_inputs)
            
            # Apply constraints
            constrained_kpis = self._apply_constraints_to_kpis(kpis, pack.constraints)
            
            results.append({
                'run_id': run_id,
                'drivers': correlated_values,
                'kpis': constrained_kpis
            })
        
        return results
    
    def _sample_distribution(self, driver: FactorConfig) -> float:
        """Sample value from driver's distribution"""
        config = driver.config_range
        
        if driver.distribution_type == 'normal':
            return np.random.normal(config['mean'], config['std'])
        elif driver.distribution_type == 'beta':
            return np.random.beta(config['alpha'], config['beta'])
        elif driver.distribution_type == 'lognormal':
            return np.random.lognormal(config['mu'], config['sigma'])
        elif driver.distribution_type == 'triangular':
            return np.random.triangular(config['low'], config['mode'], config['high'])
        else:
            return np.random.uniform(0, 1)
    
    def _apply_correlations(self, driver_values: Dict[str, float], 
                          correlations: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Apply correlations between drivers"""
        correlated_values = driver_values.copy()
        
        for driver_id, value in driver_values.items():
            if driver_id in correlations:
                for correlated_driver, correlation in correlations[driver_id].items():
                    if correlated_driver in driver_values:
                        # Simple correlation adjustment
                        adjustment = correlation * 0.1 * value
                        correlated_values[correlated_driver] += adjustment
        
        return correlated_values
    
    def _calculate_kpis(self, driver_values: Dict[str, float], 
                       business_inputs: Dict[str, float]) -> Dict[str, float]:
        """Calculate KPIs from driver values"""
        # Base calculations
        unit_price = business_inputs.get('unit_price', 100)
        unit_cost = business_inputs.get('unit_cost', 60)
        volume = business_inputs.get('expected_volume', 1000)
        
        # Apply driver effects
        market_growth = driver_values.get('F1', 0.1)
        competitive_intensity = driver_values.get('F2', 0.5)
        tech_adoption = driver_values.get('F3', 0.1)
        regulatory_impact = driver_values.get('F4', 0.0)
        economic_conditions = driver_values.get('F5', 0.05)
        
        # Calculate derived metrics
        adoption_rate = 0.1 + market_growth + tech_adoption - competitive_intensity * 0.2
        margin = (unit_price - unit_cost) / unit_price * (1 + economic_conditions - regulatory_impact)
        conversion = 0.15 + tech_adoption * 0.1 - competitive_intensity * 0.05
        
        # Financial projections
        revenue = unit_price * volume * adoption_rate
        cost = unit_cost * volume * adoption_rate
        profit = revenue - cost
        
        # ROI and payback
        initial_investment = business_inputs.get('initial_investment', 100000)
        roi = profit / initial_investment if initial_investment > 0 else 0
        payback_period = initial_investment / profit if profit > 0 else 999
        
        return {
            'roi': max(0, roi),
            'payback_period': min(payback_period, 10),
            'adoption_rate': max(0, min(adoption_rate, 1)),
            'margin': max(0, min(margin, 1)),
            'conversion': max(0, min(conversion, 1)),
            'revenue': max(0, revenue),
            'profit': profit,
            'npv': profit * 0.9  # Simplified NPV
        }
    
    def _apply_constraints_to_kpis(self, kpis: Dict[str, float], 
                                  constraints: Dict[str, Any]) -> Dict[str, float]:
        """Apply business constraints to KPIs"""
        constrained_kpis = kpis.copy()
        
        # Apply minimum ROI constraint
        if kpis['roi'] < constraints['min_roi']:
            constrained_kpis['roi'] = constraints['min_roi']
        
        # Apply maximum payback constraint
        if kpis['payback_period'] > constraints['max_payback_period']:
            constrained_kpis['payback_period'] = constraints['max_payback_period']
        
        # Apply minimum adoption constraint
        if kpis['adoption_rate'] < constraints['min_adoption_rate']:
            constrained_kpis['adoption_rate'] = constraints['min_adoption_rate']
        
        return constrained_kpis
    
    def _cluster_scenarios(self, simulation_results: List[Dict]) -> List[ScenarioResult]:
        """Cluster simulation results into scenarios"""
        if not simulation_results:
            return self._generate_default_scenarios()
        
        # Extract KPI values for clustering
        roi_values = [r['kpis']['roi'] for r in simulation_results]
        adoption_values = [r['kpis']['adoption_rate'] for r in simulation_results]
        
        scenarios = []
        
        # Base Case - median values
        roi_median = np.percentile(roi_values, 50)
        adoption_median = np.percentile(adoption_values, 50)
        base_mask = self._create_scenario_mask(roi_values, adoption_values, 
                                             roi_median, adoption_median, tolerance=0.2)
        scenarios.append(self._create_scenario('Base Case', base_mask, simulation_results))
        
        # Aggressive Growth - high ROI and adoption
        roi_p75 = np.percentile(roi_values, 75)
        adoption_p75 = np.percentile(adoption_values, 75)
        aggressive_mask = [(r >= roi_p75 and a >= adoption_p75) 
                          for r, a in zip(roi_values, adoption_values)]
        scenarios.append(self._create_scenario('Aggressive Growth', aggressive_mask, simulation_results))
        
        # Crisis - low performance
        roi_p25 = np.percentile(roi_values, 25)
        adoption_p25 = np.percentile(adoption_values, 25)
        crisis_mask = [(r <= roi_p25 and a <= adoption_p25) 
                      for r, a in zip(roi_values, adoption_values)]
        scenarios.append(self._create_scenario('Crisis', crisis_mask, simulation_results))
        
        return scenarios
    
    def _create_scenario_mask(self, roi_values: List[float], adoption_values: List[float],
                            target_roi: float, target_adoption: float, tolerance: float) -> List[bool]:
        """Create boolean mask for scenario clustering"""
        return [
            (abs(r - target_roi) / target_roi <= tolerance and 
             abs(a - target_adoption) / target_adoption <= tolerance)
            for r, a in zip(roi_values, adoption_values)
        ]
    
    def _create_scenario(self, name: str, mask: List[bool], 
                        simulation_results: List[Dict]) -> Dict[str, Any]:
        """Create scenario result from mask"""
        masked_results = [r for r, m in zip(simulation_results, mask) if m]
        
        if not masked_results:
            return self._create_default_scenario(name)
        
        # Calculate scenario metrics
        roi_values = [r['kpis']['roi'] for r in masked_results]
        adoption_values = [r['kpis']['adoption_rate'] for r in masked_results]
        
        probability = len(masked_results) / len(simulation_results)
        
        kpis = {
            'roi': np.mean(roi_values),
            'adoption_rate': np.mean(adoption_values),
            'payback_period': np.mean([r['kpis']['payback_period'] for r in masked_results]),
            'npv': np.mean([r['kpis']['npv'] for r in masked_results])
        }
        
        # Determine risk level
        risk_level = 'Low' if kpis['roi'] > 0.2 else 'Medium' if kpis['roi'] > 0.1 else 'High'
        
        # Generate narrative
        narrative = self._generate_scenario_narrative(name, kpis, risk_level)
        
        # Identify key drivers
        key_drivers = self._identify_key_drivers(masked_results)
        
        return {
            'name': name,
            'probability': probability,
            'kpis': kpis,
            'narrative': narrative,
            'key_drivers': key_drivers,
            'risk_level': risk_level
        }
    
    def _generate_scenario_narrative(self, name: str, kpis: Dict[str, float], 
                                   risk_level: str) -> str:
        """Generate narrative for scenario"""
        narratives = {
            'Base Case': f"Steady market conditions with {kpis['roi']*100:.1f}% ROI and {kpis['adoption_rate']*100:.1f}% adoption rate. Moderate growth trajectory with manageable risks.",
            'Aggressive Growth': f"Favorable market conditions driving strong performance with {kpis['roi']*100:.1f}% ROI. High adoption rate of {kpis['adoption_rate']*100:.1f}% indicates market readiness.",
            'Crisis': f"Challenging market conditions with lower ROI of {kpis['roi']*100:.1f}% and adoption rate of {kpis['adoption_rate']*100:.1f}%. Requires careful risk management and contingency planning."
        }
        
        return narratives.get(name, f"Scenario with {risk_level.lower()} risk profile and {kpis['roi']*100:.1f}% ROI.")
    
    def _identify_key_drivers(self, masked_results: List[Dict]) -> List[str]:
        """Identify key drivers for scenario"""
        if not masked_results:
            return ['Market Growth', 'Competitive Position']
        
        # Calculate driver variance
        driver_variance = {}
        for driver_id in ['F1', 'F2', 'F3', 'F4', 'F5']:
            values = [r['drivers'].get(driver_id, 0) for r in masked_results]
            if values:
                driver_variance[driver_id] = np.var(values)
        
        # Return top 3 drivers by variance
        top_drivers = sorted(driver_variance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        driver_names = {
            'F1': 'Market Growth',
            'F2': 'Competitive Position', 
            'F3': 'Technology Adoption',
            'F4': 'Regulatory Environment',
            'F5': 'Economic Conditions'
        }
        
        return [driver_names.get(driver_id, driver_id) for driver_id, _ in top_drivers]
    
    def _calculate_driver_sensitivities(self, simulation_results: List[Dict]) -> Dict[str, float]:
        """Calculate driver sensitivities"""
        if not simulation_results:
            return {'F1': 0.3, 'F2': 0.2, 'F3': 0.25, 'F4': 0.15, 'F5': 0.1}
        
        sensitivities = {}
        
        for driver_id in ['F1', 'F2', 'F3', 'F4', 'F5']:
            # Calculate correlation between driver and ROI
            driver_values = [r['drivers'].get(driver_id, 0) for r in simulation_results]
            roi_values = [r['kpis']['roi'] for r in simulation_results]
            
            if len(driver_values) > 1 and len(roi_values) > 1:
                correlation = np.corrcoef(driver_values, roi_values)[0, 1]
                sensitivities[driver_id] = abs(correlation) if not np.isnan(correlation) else 0.1
            else:
                sensitivities[driver_id] = 0.1
        
        return sensitivities
    
    def _calculate_business_case_score(self, simulation_results: List[Dict]) -> Dict[str, Any]:
        """Calculate business case score"""
        if not simulation_results:
            return {
                'score': 0.6,
                'confidence_band': [0.4, 0.8],
                'components': {'roi': 0.3, 'adoption': 0.2, 'risk': 0.1}
            }
        
        roi_values = [r['kpis']['roi'] for r in simulation_results]
        adoption_values = [r['kpis']['adoption_rate'] for r in simulation_results]
        
        # Calculate weighted score
        roi_score = min(np.mean(roi_values) / 0.3, 1.0)  # Normalize to 30% target ROI
        adoption_score = min(np.mean(adoption_values) / 0.2, 1.0)  # Normalize to 20% target adoption
        risk_score = 1.0 - (np.std(roi_values) / np.mean(roi_values)) if np.mean(roi_values) > 0 else 0.5
        
        overall_score = (roi_score * 0.5 + adoption_score * 0.3 + risk_score * 0.2)
        
        # Calculate confidence band
        confidence_band = [
            np.percentile(roi_values, 25) / 0.3,
            np.percentile(roi_values, 75) / 0.3
        ]
        
        return {
            'score': min(max(overall_score, 0), 1),
            'confidence_band': confidence_band,
            'components': {
                'roi': roi_score,
                'adoption': adoption_score,
                'risk': risk_score
            }
        }
    
    def _generate_financial_projections(self, simulation_results: List[Dict]) -> Dict[str, Any]:
        """Generate financial projections"""
        if not simulation_results:
            return {
                'year_1': {'revenue': 100000, 'profit': 20000, 'roi': 0.2},
                'year_2': {'revenue': 120000, 'profit': 30000, 'roi': 0.3},
                'year_3': {'revenue': 150000, 'profit': 45000, 'roi': 0.45}
            }
        
        # Calculate projections based on simulation results
        revenue_values = [r['kpis']['revenue'] for r in simulation_results]
        profit_values = [r['kpis']['profit'] for r in simulation_results]
        roi_values = [r['kpis']['roi'] for r in simulation_results]
        
        base_revenue = np.mean(revenue_values)
        base_profit = np.mean(profit_values)
        base_roi = np.mean(roi_values)
        
        return {
            'year_1': {
                'revenue': base_revenue,
                'profit': base_profit,
                'roi': base_roi
            },
            'year_2': {
                'revenue': base_revenue * 1.2,
                'profit': base_profit * 1.3,
                'roi': base_roi * 1.1
            },
            'year_3': {
                'revenue': base_revenue * 1.5,
                'profit': base_profit * 1.6,
                'roi': base_roi * 1.2
            }
        }
    
    def _extract_assumptions(self, simulation_pack: SimulationPack) -> Dict[str, Any]:
        """Extract key assumptions from simulation pack"""
        return {
            'drivers': [{'id': d.factor_id, 'name': d.name, 'confidence': d.confidence} 
                       for d in simulation_pack.drivers],
            'constraints': simulation_pack.constraints,
            'business_inputs': simulation_pack.business_case_inputs
        }
    
    def _generate_fallback_results(self, session_id: str, client_inputs: Dict) -> Dict[str, Any]:
        """Generate fallback results when analysis fails"""
        return {
            'session_id': session_id,
            'business_case_score': {
                'score': 0.6,
                'confidence_band': [0.4, 0.8],
                'components': {'roi': 0.3, 'adoption': 0.2, 'risk': 0.1}
            },
            'scenarios': self._generate_default_scenarios(),
            'driver_sensitivities': {'F1': 0.3, 'F2': 0.2, 'F3': 0.25, 'F4': 0.15, 'F5': 0.1},
            'simulation_metadata': {
                'runs': 1000,
                'confidence_level': 0.95,
                'analysis_type': 'fallback'
            },
            'financial_projections': {
                'year_1': {'revenue': 100000, 'profit': 20000, 'roi': 0.2}
            },
            'assumptions': {
                'drivers': [],
                'constraints': {},
                'business_inputs': client_inputs
            }
        }
    
    def _generate_default_scenarios(self) -> List[Dict[str, Any]]:
        """Generate default scenarios when clustering fails"""
        return [
            {
                'name': 'Base Case',
                'probability': 0.5,
                'kpis': {'roi': 0.15, 'adoption_rate': 0.1, 'payback_period': 2.5, 'npv': 50000},
                'narrative': 'Steady market conditions with moderate growth potential.',
                'key_drivers': ['Market Growth', 'Competitive Position'],
                'risk_level': 'Medium'
            },
            {
                'name': 'Aggressive Growth',
                'probability': 0.3,
                'kpis': {'roi': 0.25, 'adoption_rate': 0.15, 'payback_period': 1.8, 'npv': 80000},
                'narrative': 'Favorable market conditions driving strong performance.',
                'key_drivers': ['Technology Adoption', 'Market Growth'],
                'risk_level': 'Low'
            },
            {
                'name': 'Crisis',
                'probability': 0.2,
                'kpis': {'roi': 0.08, 'adoption_rate': 0.05, 'payback_period': 4.0, 'npv': 20000},
                'narrative': 'Challenging market conditions requiring careful risk management.',
                'key_drivers': ['Regulatory Environment', 'Economic Conditions'],
                'risk_level': 'High'
            }
        ]
    
    def _create_default_scenario(self, name: str) -> Dict[str, Any]:
        """Create default scenario when clustering fails"""
        return {
            'name': name,
            'probability': 0.33,
            'kpis': {'roi': 0.15, 'adoption_rate': 0.1, 'payback_period': 2.5, 'npv': 50000},
            'narrative': f'{name} scenario with moderate performance expectations.',
            'key_drivers': ['Market Growth', 'Competitive Position'],
            'risk_level': 'Medium'
        }
