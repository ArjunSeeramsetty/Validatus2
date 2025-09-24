# backend/app/services/enhanced_data_pipeline/event_shock_modeler.py
import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import math

logger = logging.getLogger(__name__)

class DecayFunction(Enum):
    """Types of decay functions for event shock modeling"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    STEP = "step"
    POWER_LAW = "power_law"
    SIGMOID = "sigmoid"

class EventType(Enum):
    """Types of events that can cause shocks"""
    MARKET_DISRUPTION = "market_disruption"
    ECONOMIC_CRISIS = "economic_crisis"
    TECHNOLOGY_BREAKTHROUGH = "technology_breakthrough"
    REGULATORY_CHANGE = "regulatory_change"
    COMPETITIVE_ENTRY = "competitive_entry"
    PRODUCT_LAUNCH = "product_launch"
    EXTERNAL_SHOCK = "external_shock"

@dataclass
class EventShock:
    """Represents an event that impacts analysis metrics"""
    event_id: str
    event_type: EventType
    event_date: datetime
    impact_magnitude: float  # -1.0 to 1.0
    decay_function: DecayFunction
    decay_parameters: Dict[str, float]
    affected_metrics: List[str]
    confidence_level: float
    event_metadata: Dict[str, Any]

@dataclass
class ShockModelResult:
    """Result of event shock modeling"""
    original_values: List[float]
    adjusted_values: List[float]
    shock_contributions: Dict[str, List[float]]
    cumulative_impact: List[float]
    confidence_intervals: List[Tuple[float, float]]
    model_metadata: Dict[str, Any]

class EventShockModeler:
    """
    Advanced event shock modeling for temporal decay analysis
    Models how external events impact strategic metrics over time
    """
    
    def __init__(self):
        # Default decay parameters for different functions
        self.default_decay_params = {
            DecayFunction.EXPONENTIAL: {'lambda': 0.1, 'baseline': 0.0},
            DecayFunction.LINEAR: {'slope': -0.02, 'intercept': 1.0},
            DecayFunction.LOGARITHMIC: {'scale': 0.5, 'offset': 1.0},
            DecayFunction.STEP: {'half_life': 30.0, 'step_size': 0.1},
            DecayFunction.POWER_LAW: {'alpha': -0.5, 'scale': 1.0},
            DecayFunction.SIGMOID: {'midpoint': 50.0, 'steepness': 0.1}
        }
        
        # Event impact multipliers by type
        self.event_multipliers = {
            EventType.MARKET_DISRUPTION: 1.0,
            EventType.ECONOMIC_CRISIS: 1.2,
            EventType.TECHNOLOGY_BREAKTHROUGH: 0.8,
            EventType.REGULATORY_CHANGE: 0.9,
            EventType.COMPETITIVE_ENTRY: 0.7,
            EventType.PRODUCT_LAUNCH: 0.6,
            EventType.EXTERNAL_SHOCK: 1.1
        }
        
        logger.info("✅ Event Shock Modeler initialized with temporal decay functions")
    
    async def model_event_shocks(self,
                                time_series_data: List[Dict[str, Any]],
                                event_shocks: List[EventShock],
                                forecast_periods: int = 12,
                                confidence_level: float = 0.95) -> ShockModelResult:
        """
        Model the impact of event shocks on time series data
        
        Args:
            time_series_data: Historical time series data points
            event_shocks: List of event shocks to model
            forecast_periods: Number of periods to forecast
            confidence_level: Statistical confidence level for intervals
        
        Returns:
            Complete shock modeling result
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"Starting event shock modeling for {len(event_shocks)} events over {forecast_periods} periods")
        
        try:
            # Step 1: Prepare time series data
            processed_data = await self._prepare_time_series_data(time_series_data)
            
            # Step 2: Validate and process event shocks
            validated_shocks = await self._validate_event_shocks(event_shocks, processed_data)
            
            # Step 3: Calculate baseline trend
            baseline_trend = await self._calculate_baseline_trend(processed_data, forecast_periods)
            
            # Step 4: Apply event shock models
            shock_adjustments = await self._apply_event_shocks(
                baseline_trend, validated_shocks, processed_data['dates']
            )
            
            # Step 5: Calculate confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(
                baseline_trend, shock_adjustments, confidence_level
            )
            
            # Step 6: Generate comprehensive result
            result = ShockModelResult(
                original_values=processed_data['values'],
                adjusted_values=shock_adjustments['final_values'],
                shock_contributions=shock_adjustments['individual_contributions'],
                cumulative_impact=shock_adjustments['cumulative_impact'],
                confidence_intervals=confidence_intervals,
                model_metadata={
                    'total_events': len(validated_shocks),
                    'forecast_periods': forecast_periods,
                    'confidence_level': confidence_level,
                    'processing_time': (datetime.now(timezone.utc) - start_time).total_seconds(),
                    'baseline_trend': baseline_trend.get('trend_info', {}),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
            
            logger.info(f"✅ Event shock modeling completed in {result.model_metadata['processing_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Event shock modeling failed: {e}")
            return self._create_fallback_result(time_series_data, forecast_periods)
    
    async def _prepare_time_series_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare and validate time series data"""
        try:
            dates = []
            values = []
            
            # Extract dates and values
            for data_point in raw_data:
                try:
                    # Parse date
                    date_str = data_point.get('date') or data_point.get('timestamp')
                    if isinstance(date_str, str):
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    elif isinstance(date_str, datetime):
                        date = date_str
                    else:
                        continue
                    
                    # Parse value
                    value = data_point.get('value') or data_point.get('score')
                    if value is not None:
                        dates.append(date)
                        values.append(float(value))
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse data point: {e}")
                    continue
            
            if not dates or not values:
                raise ValueError("No valid time series data found")
            
            # Sort by date
            sorted_pairs = sorted(zip(dates, values), key=lambda x: x[0])
            dates, values = zip(*sorted_pairs)
            
            # Create time index
            start_date = min(dates)
            time_indices = [(date - start_date).days for date in dates]
            
            return {
                'dates': list(dates),
                'values': list(values),
                'time_indices': time_indices,
                'start_date': start_date,
                'data_points': len(values)
            }
            
        except Exception as e:
            logger.error(f"Time series data preparation failed: {e}")
            raise
    
    async def _validate_event_shocks(self, 
                                   event_shocks: List[EventShock],
                                   processed_data: Dict[str, Any]) -> List[EventShock]:
        """Validate and filter event shocks"""
        validated_shocks = []
        data_start = processed_data['start_date']
        data_end = max(processed_data['dates'])
        
        for shock in event_shocks:
            try:
                # Check date validity
                if shock.event_date < data_start - timedelta(days=365):
                    logger.warning(f"Event {shock.event_id} too far in past, skipping")
                    continue
                
                if shock.event_date > data_end + timedelta(days=365):
                    logger.warning(f"Event {shock.event_id} too far in future, skipping")
                    continue
                
                # Check impact magnitude
                if abs(shock.impact_magnitude) > 1.0:
                    logger.warning(f"Event {shock.event_id} impact magnitude clamped to [-1,1]")
                    shock.impact_magnitude = max(-1.0, min(1.0, shock.impact_magnitude))
                
                # Ensure decay parameters exist
                if not shock.decay_parameters:
                    shock.decay_parameters = self.default_decay_params[shock.decay_function]
                
                validated_shocks.append(shock)
                
            except Exception as e:
                logger.error(f"Failed to validate shock {shock.event_id}: {e}")
                continue
        
        logger.info(f"✅ Validated {len(validated_shocks)}/{len(event_shocks)} event shocks")
        return validated_shocks
    
    async def _calculate_baseline_trend(self, 
                                      processed_data: Dict[str, Any],
                                      forecast_periods: int) -> Dict[str, Any]:
        """Calculate baseline trend without event impacts"""
        try:
            values = np.array(processed_data['values'])
            time_indices = np.array(processed_data['time_indices'])
            
            # Fit polynomial trend (degree 2 for slight curvature)
            trend_coeffs = np.polyfit(time_indices, values, deg=min(2, len(values)-1))
            trend_poly = np.poly1d(trend_coeffs)
            
            # Generate baseline forecast
            last_time_index = max(time_indices)
            forecast_indices = np.arange(
                last_time_index + 1, 
                last_time_index + 1 + forecast_periods
            )
            
            historical_trend = trend_poly(time_indices)
            forecast_trend = trend_poly(forecast_indices)
            
            # Calculate trend strength (R-squared)
            ss_res = np.sum((values - historical_trend) ** 2)
            ss_tot = np.sum((values - np.mean(values)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
            
            return {
                'historical_values': historical_trend.tolist(),
                'forecast_values': forecast_trend.tolist(),
                'combined_values': np.concatenate([historical_trend, forecast_trend]).tolist(),
                'trend_coefficients': trend_coeffs.tolist(),
                'trend_info': {
                    'r_squared': r_squared,
                    'trend_strength': min(1.0, r_squared),
                    'polynomial_degree': len(trend_coeffs) - 1
                },
                'forecast_indices': forecast_indices.tolist(),
                'time_indices': np.concatenate([time_indices, forecast_indices]).tolist()
            }
            
        except Exception as e:
            logger.error(f"Baseline trend calculation failed: {e}")
            # Fallback to simple average
            avg_value = np.mean(processed_data['values'])
            total_periods = len(processed_data['values']) + forecast_periods
            return {
                'historical_values': [avg_value] * len(processed_data['values']),
                'forecast_values': [avg_value] * forecast_periods,
                'combined_values': [avg_value] * total_periods,
                'trend_info': {'r_squared': 0.0, 'trend_strength': 0.0}
            }
    
    async def _apply_event_shocks(self,
                                baseline_trend: Dict[str, Any],
                                event_shocks: List[EventShock],
                                reference_dates: List[datetime]) -> Dict[str, Any]:
        """Apply event shock models to baseline trend"""
        try:
            combined_values = np.array(baseline_trend['combined_values'])
            time_indices = np.array(baseline_trend['time_indices'])
            
            # Initialize shock tracking
            individual_contributions = {}
            cumulative_shock_impact = np.zeros_like(combined_values)
            
            for shock in event_shocks:
                # Calculate time distance from event
                event_time_index = (shock.event_date - reference_dates[0]).days
                time_distances = time_indices - event_time_index
                
                # Calculate decay function values
                decay_values = await self._calculate_decay_function(
                    time_distances, shock.decay_function, shock.decay_parameters
                )
                
                # Apply impact magnitude and event type multiplier
                event_multiplier = self.event_multipliers.get(shock.event_type, 1.0)
                shock_impact = (shock.impact_magnitude * event_multiplier * 
                               decay_values * shock.confidence_level)
                
                # Store individual contribution
                individual_contributions[shock.event_id] = shock_impact.tolist()
                
                # Add to cumulative impact
                cumulative_shock_impact += shock_impact
            
            # Apply shocks to baseline (multiplicative for positive, additive for negative)
            final_values = combined_values.copy()
            for i, shock_value in enumerate(cumulative_shock_impact):
                if shock_value >= 0:
                    # Positive shock - multiplicative boost
                    final_values[i] *= (1.0 + shock_value)
                else:
                    # Negative shock - additive reduction
                    final_values[i] += shock_value * combined_values[i]
            
            # Ensure values remain non-negative
            final_values = np.maximum(final_values, 0.0)
            
            return {
                'final_values': final_values.tolist(),
                'individual_contributions': individual_contributions,
                'cumulative_impact': cumulative_shock_impact.tolist(),
                'shock_summary': {
                    'total_events': len(event_shocks),
                    'max_positive_impact': float(np.max(cumulative_shock_impact)),
                    'max_negative_impact': float(np.min(cumulative_shock_impact)),
                    'avg_impact': float(np.mean(np.abs(cumulative_shock_impact)))
                }
            }
            
        except Exception as e:
            logger.error(f"Event shock application failed: {e}")
            return {
                'final_values': baseline_trend['combined_values'],
                'individual_contributions': {},
                'cumulative_impact': [0.0] * len(baseline_trend['combined_values'])
            }
    
    async def _calculate_decay_function(self,
                                      time_distances: np.ndarray,
                                      decay_function: DecayFunction,
                                      parameters: Dict[str, float]) -> np.ndarray:
        """Calculate decay function values for given time distances"""
        try:
            # Convert negative time distances (before event) to zero impact
            future_mask = time_distances >= 0
            decay_values = np.zeros_like(time_distances, dtype=float)
            
            if not np.any(future_mask):
                return decay_values
            
            future_times = time_distances[future_mask]
            
            if decay_function == DecayFunction.EXPONENTIAL:
                lambda_param = parameters.get('lambda', 0.1)
                baseline = parameters.get('baseline', 0.0)
                future_decay = np.exp(-lambda_param * future_times) + baseline
                
            elif decay_function == DecayFunction.LINEAR:
                slope = parameters.get('slope', -0.02)
                intercept = parameters.get('intercept', 1.0)
                future_decay = np.maximum(0.0, intercept + slope * future_times)
                
            elif decay_function == DecayFunction.LOGARITHMIC:
                scale = parameters.get('scale', 0.5)
                offset = parameters.get('offset', 1.0)
                future_decay = offset / (1.0 + scale * np.log(1.0 + future_times))
                
            elif decay_function == DecayFunction.STEP:
                half_life = parameters.get('half_life', 30.0)
                step_size = parameters.get('step_size', 0.1)
                steps = np.floor(future_times / half_life)
                future_decay = np.maximum(0.0, 1.0 - steps * step_size)
                
            elif decay_function == DecayFunction.POWER_LAW:
                alpha = parameters.get('alpha', -0.5)
                scale = parameters.get('scale', 1.0)
                future_decay = scale * np.power(1.0 + future_times, alpha)
                
            elif decay_function == DecayFunction.SIGMOID:
                midpoint = parameters.get('midpoint', 50.0)
                steepness = parameters.get('steepness', 0.1)
                future_decay = 1.0 / (1.0 + np.exp(steepness * (future_times - midpoint)))
                
            else:
                # Default to exponential
                future_decay = np.exp(-0.1 * future_times)
            
            # Ensure non-negative decay values
            future_decay = np.maximum(0.0, future_decay)
            decay_values[future_mask] = future_decay
            
            return decay_values
            
        except Exception as e:
            logger.error(f"Decay function calculation failed: {e}")
            return np.zeros_like(time_distances)
    
    async def _calculate_confidence_intervals(self,
                                            baseline_trend: Dict[str, Any],
                                            shock_adjustments: Dict[str, Any],
                                            confidence_level: float) -> List[Tuple[float, float]]:
        """Calculate confidence intervals for shock-adjusted predictions"""
        try:
            adjusted_values = np.array(shock_adjustments['final_values'])
            cumulative_impact = np.array(shock_adjustments['cumulative_impact'])
            
            # Estimate uncertainty from shock magnitude and baseline trend quality
            baseline_uncertainty = 0.1  # Base uncertainty
            trend_quality = baseline_trend.get('trend_info', {}).get('r_squared', 0.0)
            trend_uncertainty = (1.0 - trend_quality) * 0.2
            
            # Shock-induced uncertainty proportional to impact magnitude
            shock_uncertainty = np.abs(cumulative_impact) * 0.1
            
            # Total uncertainty
            total_uncertainty = baseline_uncertainty + trend_uncertainty + shock_uncertainty
            
            # Convert confidence level to z-score
            z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
            z_score = z_scores.get(confidence_level, 1.96)
            
            # Calculate intervals
            confidence_intervals = []
            for i, (value, uncertainty) in enumerate(zip(adjusted_values, total_uncertainty)):
                margin = z_score * uncertainty * value  # Proportional margin
                lower_bound = max(0.0, value - margin)
                upper_bound = value + margin
                confidence_intervals.append((lower_bound, upper_bound))
            
            return confidence_intervals
            
        except Exception as e:
            logger.error(f"Confidence interval calculation failed: {e}")
            # Fallback to 10% intervals
            values = shock_adjustments.get('final_values', [])
            return [(max(0.0, v * 0.9), v * 1.1) for v in values]
    
    def _create_fallback_result(self, 
                               original_data: List[Dict[str, Any]], 
                               forecast_periods: int) -> ShockModelResult:
        """Create fallback result when modeling fails"""
        try:
            values = [dp.get('value', 0.5) for dp in original_data]
            avg_value = np.mean(values) if values else 0.5
            
            total_periods = len(values) + forecast_periods
            fallback_values = values + [avg_value] * forecast_periods
            
            return ShockModelResult(
                original_values=values,
                adjusted_values=fallback_values,
                shock_contributions={},
                cumulative_impact=[0.0] * total_periods,
                confidence_intervals=[(v * 0.9, v * 1.1) for v in fallback_values],
                model_metadata={
                    'status': 'fallback',
                    'total_events': 0,
                    'forecast_periods': forecast_periods,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Fallback result creation failed: {e}")
            return ShockModelResult(
                original_values=[],
                adjusted_values=[],
                shock_contributions={},
                cumulative_impact=[],
                confidence_intervals=[],
                model_metadata={'status': 'error', 'error': str(e)}
            )

__all__ = [
    'EventShockModeler', 'EventShock', 'ShockModelResult',
    'DecayFunction', 'EventType'
]
