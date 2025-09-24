"""
Unit tests for Phase C Bayesian Data Blender component.

Tests Bayesian inference, data source blending, and probabilistic data fusion.
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from app.services.enhanced_data_pipeline.bayesian_data_blender import (
    BayesianDataBlender,
    DataSource,
    BayesianBlendResult
)


@pytest.mark.unit
@pytest.mark.phase_c
class TestBayesianDataBlender:
    """Test suite for Bayesian Data Blender."""

    @pytest.fixture
    def blender(self):
        """Create a test Bayesian Data Blender instance."""
        with patch('app.services.enhanced_data_pipeline.bayesian_data_blender.ContentQualityAnalyzer'):
            return BayesianDataBlender()

    @pytest.fixture
    def sample_data_sources(self):
        """Create sample data sources for testing."""
        return [
            DataSource(
                source_id="client_data",
                source_type="client",
                data_points=[
                    {"market_size": 1000000000, "growth_rate": 0.15, "quality_score": 0.85}
                ],
                reliability_score=0.8,
                recency_weight=0.9,
                source_bias=0.0
            ),
            DataSource(
                source_id="benchmark_data",
                source_type="benchmark",
                data_points=[
                    {"market_size": 1200000000, "growth_rate": 0.12, "quality_score": 0.78}
                ],
                reliability_score=0.9,
                recency_weight=0.8,
                source_bias=0.1
            ),
            DataSource(
                source_id="industry_data",
                source_type="industry",
                data_points=[
                    {"market_size": 950000000, "growth_rate": 0.18, "quality_score": 0.82}
                ],
                reliability_score=0.7,
                recency_weight=0.85,
                source_bias=-0.05
            )
        ]

    @pytest.mark.asyncio
    async def test_blender_initialization(self, blender):
        """Test Bayesian Data Blender initialization."""
        assert blender.content_analyzer is not None
        assert 'market_size' in blender.priors
        assert 'growth_rate' in blender.priors
        assert 'market_share' in blender.priors
        assert 'pricing' in blender.priors
        assert 'quality_score' in blender.priors
        
        # Check source reliability weights
        assert blender.source_reliability['client'] == 0.8
        assert blender.source_reliability['benchmark'] == 0.9
        assert blender.source_reliability['industry'] == 0.7
        assert blender.source_reliability['expert'] == 0.75
        assert blender.source_reliability['survey'] == 0.6
        assert blender.source_reliability['secondary'] == 0.5

    @pytest.mark.asyncio
    async def test_data_source_validation(self, blender, sample_data_sources):
        """Test data source validation."""
        validated_sources = await blender._validate_data_sources(sample_data_sources)
        
        assert len(validated_sources) == 3
        assert all(src.reliability_score >= 0.3 for src in validated_sources)
        assert all(len(src.data_points) > 0 for src in validated_sources)

    @pytest.mark.asyncio
    async def test_data_source_validation_filtering(self, blender):
        """Test data source validation with filtering."""
        mixed_sources = [
            DataSource(
                source_id="good_source",
                source_type="client",
                data_points=[{"market_size": 1000000}],
                reliability_score=0.8,
                recency_weight=0.9
            ),
            DataSource(
                source_id="bad_reliability",
                source_type="secondary",
                data_points=[{"market_size": 500000}],
                reliability_score=0.2,  # Below threshold
                recency_weight=0.7
            ),
            DataSource(
                source_id="no_data",
                source_type="expert",
                data_points=[],  # No data points
                reliability_score=0.8,
                recency_weight=0.8
            )
        ]
        
        validated_sources = await blender._validate_data_sources(mixed_sources)
        
        # Should filter out sources with low reliability or no data
        assert len(validated_sources) == 1
        assert validated_sources[0].source_id == "good_source"

    @pytest.mark.asyncio
    async def test_value_extraction_from_sources(self, blender, sample_data_sources):
        """Test value extraction from data sources."""
        extracted_values = await blender._extract_values_from_sources(
            sample_data_sources, 'market_size'
        )
        
        assert len(extracted_values) == 3
        
        # Check that values are extracted correctly
        values = [v[0] for v in extracted_values]  # Extract values
        weights = [v[1] for v in extracted_values]  # Extract weights
        source_ids = [v[2] for v in extracted_values]  # Extract source IDs
        
        assert all(val > 0 for val in values)
        assert all(weight > 0 for weight in weights)
        assert "client_data" in source_ids
        assert "benchmark_data" in source_ids
        assert "industry_data" in source_ids

    @pytest.mark.asyncio
    async def test_single_value_extraction(self, blender):
        """Test single value extraction from data points."""
        data_point = {
            "market_size": 1000000000,
            "growth_rate": 0.15,
            "quality_score": 0.85,
            "content": "The market size is $1.2 billion with 18% annual growth"
        }
        
        # Test direct extraction
        value = await blender._extract_single_value(data_point, 'market_size')
        assert value == 1000000000
        
        # Test pattern-based extraction
        value = await blender._extract_single_value(data_point, 'growth_rate')
        assert value == 0.15

    @pytest.mark.asyncio
    async def test_text_value_extraction(self, blender):
        """Test value extraction from text content."""
        text_content = "The total addressable market is approximately $2.5 billion, growing at 22% CAGR annually."
        
        # Test market size extraction
        market_size = await blender._extract_value_from_text(text_content, 'market_size')
        assert market_size is not None
        assert market_size > 0
        
        # Test growth rate extraction
        growth_rate = await blender._extract_value_from_text(text_content, 'growth_rate')
        assert growth_rate is not None
        assert 0 <= growth_rate <= 1  # Should be normalized to decimal

    @pytest.mark.asyncio
    async def test_beta_bayesian_update(self, blender):
        """Test Beta distribution Bayesian update."""
        values = np.array([0.8, 0.85, 0.82, 0.78, 0.88])
        weights = np.array([0.8, 0.9, 0.7, 0.6, 0.85])
        prior_params = {'alpha': 2.0, 'beta': 2.0}
        
        result = blender._beta_bayesian_update(values, weights, prior_params)
        
        assert 'mean' in result
        assert 'std' in result
        assert 'distribution_type' in result
        assert 'params' in result
        
        assert 0 <= result['mean'] <= 1  # Beta distribution bounds
        assert result['std'] >= 0
        assert result['distribution_type'] == 'beta'
        assert 'alpha' in result['params']
        assert 'beta' in result['params']

    @pytest.mark.asyncio
    async def test_normal_bayesian_update(self, blender):
        """Test Normal distribution Bayesian update."""
        values = np.array([0.12, 0.15, 0.18, 0.14, 0.16])
        weights = np.array([0.8, 0.9, 0.7, 0.6, 0.85])
        prior_params = {'mu': 0.1, 'sigma': 0.05}
        
        result = blender._normal_bayesian_update(values, weights, prior_params)
        
        assert 'mean' in result
        assert 'std' in result
        assert 'distribution_type' in result
        assert 'params' in result
        
        assert result['std'] >= 0
        assert result['distribution_type'] == 'normal'

    @pytest.mark.asyncio
    async def test_lognormal_bayesian_update(self, blender):
        """Test Log-Normal distribution Bayesian update."""
        values = np.array([1000000000, 1200000000, 950000000, 1100000000])
        weights = np.array([0.8, 0.9, 0.7, 0.85])
        prior_params = {'mu': 20.0, 'sigma': 0.5}
        
        result = blender._lognormal_bayesian_update(values, weights, prior_params)
        
        assert 'mean' in result
        assert 'std' in result
        assert 'distribution_type' in result
        assert 'params' in result
        
        assert result['mean'] > 0  # Log-normal is positive
        assert result['std'] >= 0
        assert result['distribution_type'] == 'lognormal'

    @pytest.mark.asyncio
    async def test_bayesian_inference_market_size(self, blender, sample_data_sources):
        """Test Bayesian inference for market size data."""
        extracted_values = await blender._extract_values_from_sources(
            sample_data_sources, 'market_size'
        )
        
        result = await blender._perform_bayesian_inference(
            extracted_values, 'market_size', sample_data_sources
        )
        
        assert 'posterior_mean' in result
        assert 'posterior_std' in result
        assert 'confidence' in result
        assert 'likelihood_type' in result
        
        assert result['posterior_mean'] > 0
        assert result['posterior_std'] >= 0
        assert 0 <= result['confidence'] <= 1

    @pytest.mark.asyncio
    async def test_bayesian_inference_growth_rate(self, blender, sample_data_sources):
        """Test Bayesian inference for growth rate data."""
        extracted_values = await blender._extract_values_from_sources(
            sample_data_sources, 'growth_rate'
        )
        
        result = await blender._perform_bayesian_inference(
            extracted_values, 'growth_rate', sample_data_sources
        )
        
        assert 'posterior_mean' in result
        assert 'posterior_std' in result
        assert 'confidence' in result
        assert result['likelihood_type'] == 'normal'

    @pytest.mark.asyncio
    async def test_blend_weights_calculation(self, blender, sample_data_sources):
        """Test blend weights calculation."""
        # Mock posterior result
        posterior_result = {
            'posterior_mean': 1000000000,
            'posterior_std': 100000000,
            'confidence': 0.85
        }
        
        blend_weights = blender._calculate_blend_weights(sample_data_sources, posterior_result)
        
        assert len(blend_weights) == 3
        assert all(weight > 0 for weight in blend_weights.values())
        assert abs(sum(blend_weights.values()) - 1.0) < 0.01  # Should sum to ~1.0
        
        # Benchmark should have higher weight due to higher reliability
        assert blend_weights['benchmark_data'] >= blend_weights['client_data']
        assert blend_weights['client_data'] >= blend_weights['industry_data']

    @pytest.mark.asyncio
    async def test_uncertainty_metrics_calculation(self, blender, sample_data_sources):
        """Test uncertainty metrics calculation."""
        extracted_values = [(1000000000, 0.8, "source1"), (1200000000, 0.9, "source2")]
        posterior_result = {
            'posterior_mean': 1100000000,
            'posterior_std': 100000000,
            'confidence': 0.85
        }
        blend_weights = {"source1": 0.4, "source2": 0.6}
        
        uncertainty_metrics = blender._calculate_uncertainty_metrics(
            extracted_values, posterior_result, blend_weights
        )
        
        assert 'coefficient_of_variation' in uncertainty_metrics
        assert 'confidence_interval_lower' in uncertainty_metrics
        assert 'confidence_interval_upper' in uncertainty_metrics
        assert 'entropy' in uncertainty_metrics
        assert 'effective_sample_size' in uncertainty_metrics
        
        assert uncertainty_metrics['coefficient_of_variation'] >= 0
        assert uncertainty_metrics['confidence_interval_lower'] <= posterior_result['posterior_mean']
        assert uncertainty_metrics['confidence_interval_upper'] >= posterior_result['posterior_mean']
        assert uncertainty_metrics['entropy'] >= 0
        assert uncertainty_metrics['effective_sample_size'] > 0

    @pytest.mark.asyncio
    async def test_full_bayesian_blending_workflow(self, blender, sample_data_sources):
        """Test complete Bayesian blending workflow."""
        result = await blender.blend_data_sources(
            data_sources=sample_data_sources,
            blend_type='market_size',
            confidence_threshold=0.7
        )
        
        assert isinstance(result, BayesianBlendResult)
        assert result.blended_value > 0
        assert 0 <= result.confidence_score <= 1
        assert len(result.contributing_sources) == 3
        assert len(result.blend_weights) == 3
        assert 'posterior_distribution' in result.posterior_distribution
        assert 'uncertainty_metrics' in result.uncertainty_metrics
        
        # Check metadata
        assert result.blend_metadata['blend_type'] == 'market_size'
        assert result.blend_metadata['total_sources'] == 3
        assert result.blend_metadata['blend_method'] == 'bayesian_inference'
        assert 'processing_time' in result.blend_metadata
        assert 'timestamp' in result.blend_metadata

    @pytest.mark.asyncio
    async def test_blending_with_empty_sources(self, blender):
        """Test blending with empty data sources."""
        result = await blender.blend_data_sources(
            data_sources=[],
            blend_type='market_size',
            confidence_threshold=0.7
        )
        
        assert isinstance(result, BayesianBlendResult)
        assert result.blended_value == 0.5  # Default value
        assert result.confidence_score == 0.1  # Low confidence for empty data

    @pytest.mark.asyncio
    async def test_blending_with_low_confidence(self, blender, sample_data_sources):
        """Test blending with confidence below threshold."""
        # Use very high confidence threshold
        result = await blender.blend_data_sources(
            data_sources=sample_data_sources,
            blend_type='market_size',
            confidence_threshold=0.99  # Very high threshold
        )
        
        assert isinstance(result, BayesianBlendResult)
        # Should still return result but with warning logged

    @pytest.mark.asyncio
    async def test_different_blend_types(self, blender, sample_data_sources):
        """Test blending with different data types."""
        blend_types = ['market_size', 'growth_rate', 'market_share', 'quality_score']
        
        for blend_type in blend_types:
            result = await blender.blend_data_sources(
                data_sources=sample_data_sources,
                blend_type=blend_type,
                confidence_threshold=0.7
            )
            
            assert isinstance(result, BayesianBlendResult)
            assert result.blend_metadata['blend_type'] == blend_type
            assert result.blended_value is not None

    @pytest.mark.asyncio
    async def test_error_handling_in_blending(self, blender):
        """Test error handling during blending process."""
        # Create invalid data source
        invalid_source = DataSource(
            source_id="invalid_source",
            source_type="invalid",
            data_points=[{"invalid_field": "invalid_value"}],
            reliability_score=0.5,
            recency_weight=0.5
        )
        
        result = await blender.blend_data_sources(
            data_sources=[invalid_source],
            blend_type='market_size',
            confidence_threshold=0.7
        )
        
        # Should handle errors gracefully and return default result
        assert isinstance(result, BayesianBlendResult)


@pytest.mark.unit
@pytest.mark.phase_c
class TestDataSource:
    """Test suite for Data Source."""

    def test_data_source_creation(self):
        """Test DataSource creation."""
        data_points = [{"market_size": 1000000}]
        source = DataSource(
            source_id="test_source",
            source_type="client",
            data_points=data_points,
            reliability_score=0.8,
            recency_weight=0.9
        )
        
        assert source.source_id == "test_source"
        assert source.source_type == "client"
        assert source.data_points == data_points
        assert source.reliability_score == 0.8
        assert source.recency_weight == 0.9
        assert source.source_bias == 0.0
        assert source.confidence_interval == (0.0, 1.0)

    def test_data_source_with_custom_bias(self):
        """Test DataSource with custom bias and confidence interval."""
        source = DataSource(
            source_id="biased_source",
            source_type="expert",
            data_points=[{"growth_rate": 0.15}],
            reliability_score=0.7,
            recency_weight=0.8,
            source_bias=0.1,
            confidence_interval=(0.05, 0.25)
        )
        
        assert source.source_bias == 0.1
        assert source.confidence_interval == (0.05, 0.25)


@pytest.mark.unit
@pytest.mark.phase_c
class TestBayesianBlendResult:
    """Test suite for Bayesian Blend Result."""

    def test_blend_result_creation(self):
        """Test BayesianBlendResult creation."""
        result = BayesianBlendResult(
            blended_value=1000000000,
            confidence_score=0.85,
            contributing_sources=["source1", "source2"],
            blend_weights={"source1": 0.6, "source2": 0.4},
            posterior_distribution={"mean": 1000000000, "std": 100000000},
            uncertainty_metrics={"cv": 0.1, "entropy": 0.5},
            blend_metadata={"type": "market_size", "timestamp": "2024-01-01T00:00:00Z"}
        )
        
        assert result.blended_value == 1000000000
        assert result.confidence_score == 0.85
        assert len(result.contributing_sources) == 2
        assert len(result.blend_weights) == 2
        assert result.blend_weights["source1"] == 0.6
        assert result.blend_weights["source2"] == 0.4
        assert result.posterior_distribution["mean"] == 1000000000
        assert result.uncertainty_metrics["cv"] == 0.1
        assert result.blend_metadata["type"] == "market_size"
