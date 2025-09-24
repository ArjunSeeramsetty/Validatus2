# backend/app/services/enhanced_data_pipeline/bayesian_data_blender.py
import asyncio
import logging
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from scipy import stats
import math

from ..content_quality_analyzer import ContentQualityAnalyzer
from ...core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Represents a data source for Bayesian blending"""
    source_id: str
    source_type: str  # 'client', 'benchmark', 'industry', 'expert'
    data_points: List[Dict[str, Any]]
    reliability_score: float
    recency_weight: float
    source_bias: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 1.0)

@dataclass
class BayesianBlendResult:
    """Result of Bayesian data blending"""
    blended_value: float
    confidence_score: float
    contributing_sources: List[str]
    blend_weights: Dict[str, float]
    posterior_distribution: Dict[str, Any]
    uncertainty_metrics: Dict[str, float]
    blend_metadata: Dict[str, Any]

class BayesianDataBlender:
    """
    Advanced Bayesian data blending for combining client, benchmark, and industry data
    Enhances existing ContentQualityAnalyzer with probabilistic data fusion
    """
    
    def __init__(self):
        self.content_analyzer = ContentQualityAnalyzer()
        
        # Prior distributions for different data types
        self.priors = {
            'market_size': {'alpha': 2.0, 'beta': 2.0},  # Beta distribution
            'growth_rate': {'mu': 0.1, 'sigma': 0.05},   # Normal distribution  
            'market_share': {'alpha': 1.0, 'beta': 3.0}, # Beta distribution
            'pricing': {'shape': 2.0, 'scale': 1.0},     # Gamma distribution
            'quality_score': {'alpha': 5.0, 'beta': 2.0} # Beta distribution
        }
        
        # Source reliability weights
        self.source_reliability = {
            'client': 0.8,        # High reliability for client data
            'benchmark': 0.9,     # Very high for benchmark data
            'industry': 0.7,      # Good reliability for industry data
            'expert': 0.75,       # Good reliability for expert opinions
            'survey': 0.6,        # Moderate reliability for survey data
            'secondary': 0.5      # Lower reliability for secondary sources
        }
        
        logger.info("✅ Bayesian Data Blender initialized with probabilistic fusion capabilities")
    
    async def blend_data_sources(self, 
                                data_sources: List[DataSource],
                                blend_type: str = 'market_size',
                                confidence_threshold: float = 0.7) -> BayesianBlendResult:
        """
        Blend multiple data sources using Bayesian inference
        
        Args:
            data_sources: List of data sources to blend
            blend_type: Type of data being blended (affects prior selection)
            confidence_threshold: Minimum confidence for reliable blending
        
        Returns:
            Comprehensive Bayesian blend result
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"Starting Bayesian blending for {len(data_sources)} sources of type '{blend_type}'")
        
        try:
            if not data_sources:
                return self._create_default_result(blend_type)
            
            # Step 1: Preprocess and validate data sources
            validated_sources = await self._validate_data_sources(data_sources)
            
            # Step 2: Extract numerical values from sources
            extracted_values = await self._extract_values_from_sources(validated_sources, blend_type)
            
            # Step 3: Apply Bayesian inference
            posterior_result = await self._perform_bayesian_inference(
                extracted_values, blend_type, validated_sources
            )
            
            # Step 4: Calculate blend weights
            blend_weights = self._calculate_blend_weights(validated_sources, posterior_result)
            
            # Step 5: Compute uncertainty metrics
            uncertainty_metrics = self._calculate_uncertainty_metrics(
                extracted_values, posterior_result, blend_weights
            )
            
            # Step 6: Generate final blended result
            blended_result = BayesianBlendResult(
                blended_value=posterior_result['posterior_mean'],
                confidence_score=posterior_result['confidence'],
                contributing_sources=[src.source_id for src in validated_sources],
                blend_weights=blend_weights,
                posterior_distribution=posterior_result,
                uncertainty_metrics=uncertainty_metrics,
                blend_metadata={
                    'blend_type': blend_type,
                    'total_sources': len(validated_sources),
                    'processing_time': (datetime.now(timezone.utc) - start_time).total_seconds(),
                    'confidence_threshold': confidence_threshold,
                    'blend_method': 'bayesian_inference',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Validate confidence meets threshold
            if blended_result.confidence_score < confidence_threshold:
                logger.warning(f"Blend confidence {blended_result.confidence_score:.3f} below threshold {confidence_threshold}")
            
            logger.info(f"✅ Bayesian blending completed: value={blended_result.blended_value:.4f}, confidence={blended_result.confidence_score:.3f}")
            return blended_result
            
        except Exception as e:
            logger.error(f"Bayesian blending failed: {e}")
            return self._create_error_result(blend_type, str(e))
    
    async def _validate_data_sources(self, data_sources: List[DataSource]) -> List[DataSource]:
        """Validate and filter data sources for quality"""
        validated_sources = []
        
        for source in data_sources:
            try:
                # Check reliability threshold
                if source.reliability_score < 0.3:
                    logger.warning(f"Source {source.source_id} below reliability threshold: {source.reliability_score}")
                    continue
                
                # Validate data points exist
                if not source.data_points:
                    logger.warning(f"Source {source.source_id} has no data points")
                    continue
                
                # Enhance with content quality analysis if text data present
                if any('text' in dp or 'content' in dp for dp in source.data_points):
                    quality_analysis = await self.content_analyzer.analyze_content_quality(
                        source.data_points
                    )
                    source.reliability_score *= quality_analysis.get('overall_score', 1.0)
                
                validated_sources.append(source)
                
            except Exception as e:
                logger.error(f"Failed to validate source {source.source_id}: {e}")
                continue
        
        logger.info(f"✅ Validated {len(validated_sources)}/{len(data_sources)} data sources")
        return validated_sources
    
    async def _extract_values_from_sources(self, 
                                         sources: List[DataSource], 
                                         blend_type: str) -> List[Tuple[float, float, str]]:
        """Extract numerical values with weights from data sources"""
        extracted_values = []  # (value, weight, source_id)
        
        for source in sources:
            try:
                source_values = []
                
                # Extract values based on blend type
                for data_point in source.data_points:
                    value = await self._extract_single_value(data_point, blend_type)
                    if value is not None:
                        source_values.append(value)
                
                if source_values:
                    # Calculate representative value (median for robustness)
                    representative_value = np.median(source_values)
                    
                    # Calculate source weight based on multiple factors
                    base_reliability = self.source_reliability.get(source.source_type, 0.5)
                    source_weight = (
                        source.reliability_score * 0.4 +
                        base_reliability * 0.3 +
                        source.recency_weight * 0.2 +
                        min(1.0, len(source_values) / 10.0) * 0.1  # Sample size bonus
                    )
                    
                    extracted_values.append((representative_value, source_weight, source.source_id))
                
            except Exception as e:
                logger.error(f"Failed to extract values from source {source.source_id}: {e}")
                continue
        
        logger.info(f"✅ Extracted {len(extracted_values)} value sets from sources")
        return extracted_values
    
    async def _extract_single_value(self, data_point: Dict[str, Any], blend_type: str) -> Optional[float]:
        """Extract a single numerical value from a data point"""
        try:
            # Direct numerical extraction
            if blend_type in data_point:
                raw_value = data_point[blend_type]
                return float(raw_value) if raw_value is not None else None
            
            # Pattern-based extraction for common fields
            extraction_patterns = {
                'market_size': ['market_size', 'tam', 'total_addressable_market', 'market_value'],
                'growth_rate': ['growth_rate', 'cagr', 'growth', 'annual_growth'],
                'market_share': ['market_share', 'share', 'penetration'],
                'pricing': ['price', 'pricing', 'cost', 'value'],
                'quality_score': ['quality', 'score', 'rating', 'grade']
            }
            
            patterns = extraction_patterns.get(blend_type, [blend_type])
            
            for pattern in patterns:
                for key, value in data_point.items():
                    if pattern.lower() in key.lower() and value is not None:
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            continue
            
            # Text-based extraction (if content present)
            if 'content' in data_point or 'text' in data_point:
                text_content = data_point.get('content') or data_point.get('text', '')
                extracted_value = await self._extract_value_from_text(text_content, blend_type)
                if extracted_value is not None:
                    return extracted_value
            
            return None
            
        except Exception as e:
            logger.error(f"Single value extraction failed: {e}")
            return None
    
    async def _extract_value_from_text(self, text: str, blend_type: str) -> Optional[float]:
        """Extract numerical values from text using pattern matching"""
        try:
            import re
            
            # Patterns for different data types
            patterns = {
                'market_size': [
                    r'market.*?(?:size|value).*?[\$€£¥]?([\d,]+(?:\.\d+)?)\s*(?:million|billion|trillion)?',
                    r'[\$€£¥]?([\d,]+(?:\.\d+)?)\s*(?:million|billion|trillion).*?market',
                    r'TAM.*?[\$€£¥]?([\d,]+(?:\.\d+)?)\s*(?:million|billion|trillion)?'
                ],
                'growth_rate': [
                    r'growth.*?rate.*?([\d.]+)\s*%',
                    r'CAGR.*?([\d.]+)\s*%',
                    r'growing.*?([\d.]+)\s*%.*?(?:annually|yearly)'
                ],
                'market_share': [
                    r'market.*?share.*?([\d.]+)\s*%',
                    r'share.*?of.*?market.*?([\d.]+)\s*%',
                    r'penetration.*?([\d.]+)\s*%'
                ]
            }
            
            if blend_type not in patterns:
                return None
            
            for pattern in patterns[blend_type]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value_str = match.group(1).replace(',', '')
                        value = float(value_str)
                        
                        # Apply scaling based on context
                        if 'billion' in match.group(0).lower():
                            value *= 1_000_000_000
                        elif 'million' in match.group(0).lower():
                            value *= 1_000_000
                        elif 'trillion' in match.group(0).lower():
                            value *= 1_000_000_000_000
                        
                        # Convert percentages to decimal
                        if '%' in match.group(0) and blend_type in ['growth_rate', 'market_share']:
                            value /= 100
                        
                        return value
                        
                    except (ValueError, IndexError):
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Text value extraction failed: {e}")
            return None
    
    async def _perform_bayesian_inference(self, 
                                        extracted_values: List[Tuple[float, float, str]], 
                                        blend_type: str,
                                        sources: List[DataSource]) -> Dict[str, Any]:
        """Perform Bayesian inference to blend data sources"""
        try:
            if not extracted_values:
                return {'posterior_mean': 0.5, 'posterior_std': 0.3, 'confidence': 0.1}
            
            values = np.array([v[0] for v in extracted_values])
            weights = np.array([v[1] for v in extracted_values])
            
            # Get appropriate prior for this data type
            prior_params = self.priors.get(blend_type, {'alpha': 1.0, 'beta': 1.0})
            
            # Determine likelihood function based on data distribution
            if blend_type in ['market_share', 'quality_score']:
                # Beta-distributed data (bounded [0,1])
                posterior_result = self._beta_bayesian_update(values, weights, prior_params)
            elif blend_type == 'growth_rate':
                # Normal distributed data
                posterior_result = self._normal_bayesian_update(values, weights, prior_params)
            elif blend_type == 'market_size':
                # Log-normal distributed data (positive, skewed)
                posterior_result = self._lognormal_bayesian_update(values, weights, prior_params)
            else:
                # Default to normal distribution
                posterior_result = self._normal_bayesian_update(values, weights, prior_params)
            
            # Calculate confidence based on posterior variance and sample size
            confidence = self._calculate_posterior_confidence(
                posterior_result, len(extracted_values), weights
            )
            
            result = {
                'posterior_mean': posterior_result['mean'],
                'posterior_std': posterior_result['std'],
                'posterior_params': posterior_result.get('params', {}),
                'confidence': confidence,
                'likelihood_type': posterior_result.get('distribution_type', 'normal'),
                'effective_sample_size': np.sum(weights),
                'data_points': len(extracted_values)
            }
            
            logger.info(f"✅ Bayesian inference completed: mean={result['posterior_mean']:.4f}, std={result['posterior_std']:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Bayesian inference failed: {e}")
            return {'posterior_mean': 0.5, 'posterior_std': 0.3, 'confidence': 0.1}
    
    def _beta_bayesian_update(self, values: np.ndarray, weights: np.ndarray, prior_params: Dict[str, float]) -> Dict[str, Any]:
        """Bayesian update for Beta-distributed data"""
        try:
            # Clip values to valid range [0,1]
            clipped_values = np.clip(values, 0.001, 0.999)
            
            # Prior parameters
            alpha_prior = prior_params.get('alpha', 1.0)
            beta_prior = prior_params.get('beta', 1.0)
            
            # Weighted likelihood calculation for Beta distribution
            # Approximate with method of moments
            weighted_mean = np.average(clipped_values, weights=weights)
            weighted_var = np.average((clipped_values - weighted_mean)**2, weights=weights)
            
            # Convert to alpha, beta parameters
            if weighted_var > 0 and weighted_mean > 0 and weighted_mean < 1:
                common_term = weighted_mean * (1 - weighted_mean) / weighted_var - 1
                alpha_data = weighted_mean * common_term
                beta_data = (1 - weighted_mean) * common_term
            else:
                alpha_data = 1.0
                beta_data = 1.0
            
            # Posterior parameters (conjugate prior)
            effective_n = np.sum(weights)
            alpha_posterior = alpha_prior + alpha_data * effective_n
            beta_posterior = beta_prior + beta_data * effective_n
            
            # Posterior moments
            posterior_mean = alpha_posterior / (alpha_posterior + beta_posterior)
            posterior_var = (alpha_posterior * beta_posterior) / ((alpha_posterior + beta_posterior)**2 * (alpha_posterior + beta_posterior + 1))
            posterior_std = np.sqrt(posterior_var)
            
            return {
                'mean': posterior_mean,
                'std': posterior_std,
                'distribution_type': 'beta',
                'params': {'alpha': alpha_posterior, 'beta': beta_posterior}
            }
            
        except Exception as e:
            logger.error(f"Beta Bayesian update failed: {e}")
            # Fallback to simple weighted average
            return {
                'mean': np.average(values, weights=weights),
                'std': np.sqrt(np.average((values - np.average(values, weights=weights))**2, weights=weights)),
                'distribution_type': 'beta',
                'params': {'alpha': 1.0, 'beta': 1.0}
            }
    
    def _normal_bayesian_update(self, values: np.ndarray, weights: np.ndarray, prior_params: Dict[str, float]) -> Dict[str, Any]:
        """Bayesian update for Normal-distributed data"""
        try:
            # Prior parameters
            mu_prior = prior_params.get('mu', 0.0)
            sigma_prior = prior_params.get('sigma', 1.0)
            
            # Data statistics
            weighted_mean = np.average(values, weights=weights)
            weighted_var = np.average((values - weighted_mean)**2, weights=weights)
            effective_n = np.sum(weights)
            
            # Posterior parameters (conjugate prior for normal with known variance)
            precision_prior = 1.0 / (sigma_prior**2)
            precision_data = effective_n / max(weighted_var, 1e-8)
            
            precision_posterior = precision_prior + precision_data
            mu_posterior = (precision_prior * mu_prior + precision_data * weighted_mean) / precision_posterior
            sigma_posterior = 1.0 / np.sqrt(precision_posterior)
            
            return {
                'mean': mu_posterior,
                'std': sigma_posterior,
                'distribution_type': 'normal',
                'params': {'mu': mu_posterior, 'sigma': sigma_posterior}
            }
            
        except Exception as e:
            logger.error(f"Normal Bayesian update failed: {e}")
            return {
                'mean': np.average(values, weights=weights),
                'std': np.std(values),
                'distribution_type': 'normal',
                'params': {'mu': np.mean(values), 'sigma': np.std(values)}
            }
    
    def _lognormal_bayesian_update(self, values: np.ndarray, weights: np.ndarray, prior_params: Dict[str, float]) -> Dict[str, Any]:
        """Bayesian update for Log-Normal distributed data"""
        try:
            # Transform to log space
            log_values = np.log(np.maximum(values, 1e-8))  # Avoid log(0)
            
            # Apply normal Bayesian update in log space
            log_result = self._normal_bayesian_update(log_values, weights, prior_params)
            
            # Transform back to original space
            original_mean = np.exp(log_result['params']['mu'] + 0.5 * log_result['params']['sigma']**2)
            original_std = original_mean * np.sqrt(np.exp(log_result['params']['sigma']**2) - 1)
            
            return {
                'mean': original_mean,
                'std': original_std,
                'distribution_type': 'lognormal',
                'params': {
                    'log_mu': log_result['params']['mu'],
                    'log_sigma': log_result['params']['sigma']
                }
            }
            
        except Exception as e:
            logger.error(f"Log-normal Bayesian update failed: {e}")
            return {
                'mean': np.average(values, weights=weights),
                'std': np.std(values),
                'distribution_type': 'lognormal',
                'params': {'log_mu': 0.0, 'log_sigma': 1.0}
            }
    
    def _calculate_posterior_confidence(self, 
                                      posterior_result: Dict[str, Any], 
                                      n_sources: int, 
                                      weights: np.ndarray) -> float:
        """Calculate confidence in posterior estimate"""
        try:
            # Base confidence from posterior precision
            posterior_std = posterior_result['std']
            precision_confidence = 1.0 / (1.0 + posterior_std)
            
            # Sample size confidence
            effective_sample_size = np.sum(weights)
            sample_confidence = min(1.0, effective_sample_size / 10.0)
            
            # Source diversity confidence
            diversity_confidence = min(1.0, n_sources / 5.0)
            
            # Weight uniformity confidence (prefer diverse weights)
            if len(weights) > 1:
                weight_entropy = -np.sum((weights / np.sum(weights)) * np.log(weights / np.sum(weights) + 1e-8))
                max_entropy = np.log(len(weights))
                uniformity_confidence = weight_entropy / max_entropy if max_entropy > 0 else 0.0
            else:
                uniformity_confidence = 0.5
            
            # Combined confidence
            confidence = (
                precision_confidence * 0.4 +
                sample_confidence * 0.3 +
                diversity_confidence * 0.2 +
                uniformity_confidence * 0.1
            )
            
            return max(0.1, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5
    
    def _calculate_blend_weights(self, 
                               sources: List[DataSource], 
                               posterior_result: Dict[str, Any]) -> Dict[str, float]:
        """Calculate final blend weights for each source"""
        weights = {}
        total_weight = 0.0
        
        for source in sources:
            # Base weight from source reliability
            base_weight = source.reliability_score * self.source_reliability.get(source.source_type, 0.5)
            
            # Recency bonus
            recency_weight = source.recency_weight
            
            # Data quality bonus
            data_quality = len(source.data_points) / max(10, len(source.data_points))  # Normalize
            
            # Combined weight
            source_weight = base_weight * (1 + recency_weight * 0.2 + data_quality * 0.1)
            weights[source.source_id] = source_weight
            total_weight += source_weight
        
        # Normalize weights
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
        
        return weights
    
    def _calculate_uncertainty_metrics(self, 
                                     extracted_values: List[Tuple[float, float, str]],
                                     posterior_result: Dict[str, Any],
                                     blend_weights: Dict[str, float]) -> Dict[str, float]:
        """Calculate comprehensive uncertainty metrics"""
        try:
            values = np.array([v[0] for v in extracted_values])
            
            return {
                'posterior_variance': posterior_result['std']**2,
                'coefficient_of_variation': posterior_result['std'] / max(posterior_result['mean'], 1e-8),
                'data_spread': np.std(values) if len(values) > 1 else 0.0,
                'source_disagreement': np.var(values) if len(values) > 1 else 0.0,
                'effective_sample_size': posterior_result.get('effective_sample_size', 1.0),
                'weight_concentration': max(blend_weights.values()) if blend_weights else 0.0
            }
            
        except Exception as e:
            logger.error(f"Uncertainty metrics calculation failed: {e}")
            return {'uncertainty': 0.5}
    
    def _create_default_result(self, blend_type: str) -> BayesianBlendResult:
        """Create default result when no data sources available"""
        return BayesianBlendResult(
            blended_value=0.5,
            confidence_score=0.1,
            contributing_sources=[],
            blend_weights={},
            posterior_distribution={'mean': 0.5, 'std': 0.3, 'confidence': 0.1},
            uncertainty_metrics={'high_uncertainty': True},
            blend_metadata={
                'blend_type': blend_type,
                'status': 'no_data_sources',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
    
    def _create_error_result(self, blend_type: str, error_message: str) -> BayesianBlendResult:
        """Create error result when blending fails"""
        return BayesianBlendResult(
            blended_value=0.5,
            confidence_score=0.1,
            contributing_sources=[],
            blend_weights={},
            posterior_distribution={'mean': 0.5, 'std': 0.3, 'confidence': 0.1},
            uncertainty_metrics={'error': True},
            blend_metadata={
                'blend_type': blend_type,
                'status': 'error',
                'error_message': error_message,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )

__all__ = ['BayesianDataBlender', 'DataSource', 'BayesianBlendResult']
