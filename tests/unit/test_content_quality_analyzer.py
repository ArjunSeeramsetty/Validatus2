# tests/unit/test_content_quality_analyzer.py

import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.app.services.content_quality_analyzer import ContentQualityAnalyzer
from backend.app.models.analysis_models import ContentQualityScores

class TestContentQualityAnalyzer:
    """Test suite for Content Quality Analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        return ContentQualityAnalyzer()
    
    @pytest.fixture
    def sample_content(self):
        """Sample content for testing"""
        return """
        This is a comprehensive article about artificial intelligence and machine learning.
        It covers various topics including deep learning, neural networks, and natural language processing.
        The article provides detailed explanations with examples and use cases.
        It includes references to recent research and industry applications.
        """
    
    @pytest.fixture
    def sample_url(self):
        """Sample URL for testing"""
        return "https://example.com/ai-article"
    
    @pytest.fixture
    def sample_topic(self):
        """Sample topic for testing"""
        return "artificial intelligence"
    
    @pytest.mark.asyncio
    async def test_analyze_content_quality_success(self, analyzer, sample_content, sample_url, sample_topic):
        """Test successful content quality analysis"""
        
        result = await analyzer.analyze_content_quality(
            content=sample_content,
            url=sample_url,
            topic=sample_topic
        )
        
        assert isinstance(result, ContentQualityScores)
        assert 0.0 <= result.overall_score <= 1.0
        assert 0.0 <= result.topic_relevance <= 1.0
        assert 0.0 <= result.readability <= 1.0
        assert 0.0 <= result.domain_authority <= 1.0
        assert result.assessment_metadata is not None
        assert result.assessment_metadata['content_length'] > 0
        assert result.assessment_metadata['word_count'] > 0
    
    @pytest.mark.asyncio
    async def test_analyze_content_quality_empty_content(self, analyzer, sample_url, sample_topic):
        """Test content quality analysis with empty content"""
        
        result = await analyzer.analyze_content_quality(
            content="",
            url=sample_url,
            topic=sample_topic
        )
        
        assert isinstance(result, ContentQualityScores)
        assert result.overall_score == 0.5  # Default score
        assert result.assessment_metadata['content_length'] == 0
        assert result.assessment_metadata['word_count'] == 0
    
    @pytest.mark.asyncio
    async def test_assess_topic_relevance(self, analyzer, sample_content, sample_topic):
        """Test topic relevance assessment"""
        
        result = await analyzer._assess_topic_relevance(sample_content, sample_topic)
        
        assert 0.0 <= result <= 1.0
        assert result > 0.5  # Should be high for relevant content
    
    @pytest.mark.asyncio
    async def test_assess_topic_relevance_irrelevant(self, analyzer, sample_topic):
        """Test topic relevance assessment with irrelevant content"""
        
        irrelevant_content = "This is about cooking recipes and food preparation techniques."
        
        result = await analyzer._assess_topic_relevance(irrelevant_content, sample_topic)
        
        assert 0.0 <= result <= 1.0
        assert result < 0.5  # Should be low for irrelevant content
    
    @pytest.mark.asyncio
    async def test_assess_readability(self, analyzer):
        """Test readability assessment"""
        
        good_readability_content = """
        This is a simple sentence. It has good readability.
        The sentences are short and clear. They are easy to understand.
        Each paragraph has a few sentences. This makes it readable.
        """
        
        result = await analyzer._assess_readability(good_readability_content)
        
        assert 0.0 <= result <= 1.0
        assert result > 0.6  # Should be good readability
    
    @pytest.mark.asyncio
    async def test_assess_readability_poor(self, analyzer):
        """Test readability assessment with poor readability content"""
        
        poor_readability_content = """
        This extraordinarily complex and convoluted sentence structure, replete with numerous
        subordinate clauses, technical jargon, and excessively lengthy constructions that
        significantly impede comprehension and reduce overall readability scores dramatically.
        """
        
        result = await analyzer._assess_readability(poor_readability_content)
        
        assert 0.0 <= result <= 1.0
        assert result < 0.7  # Should be lower readability
    
    @pytest.mark.asyncio
    async def test_assess_domain_authority_high(self, analyzer):
        """Test domain authority assessment for high-authority domains"""
        
        high_authority_urls = [
            "https://www.google.com/article",
            "https://www.microsoft.com/blog",
            "https://en.wikipedia.org/wiki/ai",
            "https://github.com/repo",
            "https://www.harvard.edu/research"
        ]
        
        for url in high_authority_urls:
            result = await analyzer._assess_domain_authority(url)
            assert 0.0 <= result <= 1.0
            assert result >= 0.7  # Should be high authority
    
    @pytest.mark.asyncio
    async def test_assess_domain_authority_low(self, analyzer):
        """Test domain authority assessment for low-authority domains"""
        
        low_authority_url = "https://unknown-blog-site.com/article"
        
        result = await analyzer._assess_domain_authority(low_authority_url)
        
        assert 0.0 <= result <= 1.0
        assert result < 0.7  # Should be lower authority
    
    @pytest.mark.asyncio
    async def test_assess_content_freshness(self, analyzer):
        """Test content freshness assessment"""
        
        recent_content = """
        In 2024, the latest developments in artificial intelligence have shown remarkable progress.
        Recent studies published this year demonstrate significant advances in machine learning.
        Current research indicates that AI technology is evolving rapidly.
        """
        
        result = await analyzer._assess_content_freshness(recent_content)
        
        assert 0.0 <= result <= 1.0
        assert result >= 0.6  # Should be relatively fresh
    
    @pytest.mark.asyncio
    async def test_assess_factual_accuracy(self, analyzer):
        """Test factual accuracy assessment"""
        
        factual_content = """
        According to recent research published in Nature, machine learning algorithms
        have achieved 95% accuracy in image recognition tasks. The study, conducted
        by researchers at Stanford University, analyzed over 10,000 test cases.
        """
        
        result = await analyzer._assess_factual_accuracy(factual_content)
        
        assert 0.0 <= result <= 1.0
        assert result >= 0.5  # Should be relatively factual
    
    @pytest.mark.asyncio
    async def test_assess_completeness(self, analyzer):
        """Test content completeness assessment"""
        
        complete_content = " ".join(["word"] * 1000)  # 1000 words
        
        result = await analyzer._assess_completeness(complete_content)
        
        assert 0.0 <= result <= 1.0
        assert result == 1.0  # Should be complete for 1000+ words
    
    @pytest.mark.asyncio
    async def test_assess_uniqueness(self, analyzer):
        """Test content uniqueness assessment"""
        
        unique_content = """
        This is a unique article about quantum computing applications in healthcare.
        It discusses novel approaches to drug discovery using quantum algorithms.
        The content presents original insights and analysis.
        """
        
        result = await analyzer._assess_uniqueness(unique_content, "https://example.com/unique")
        
        assert 0.0 <= result <= 1.0
        assert result >= 0.5  # Should be relatively unique
    
    @pytest.mark.asyncio
    async def test_assess_engagement_potential(self, analyzer):
        """Test engagement potential assessment"""
        
        engaging_content = """
        Have you ever wondered how artificial intelligence works? In this article,
        we'll explore the fascinating world of machine learning. Here are some
        tips and examples to help you understand the concepts better.
        """
        
        result = await analyzer._assess_engagement_potential(engaging_content)
        
        assert 0.0 <= result <= 1.0
        assert result >= 0.5  # Should be relatively engaging
    
    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer, sample_url, sample_topic):
        """Test error handling in content quality analysis"""
        
        # Test with None content
        result = await analyzer.analyze_content_quality(
            content=None,
            url=sample_url,
            topic=sample_topic
        )
        
        assert isinstance(result, ContentQualityScores)
        assert result.overall_score == 0.5  # Default score
    
    @pytest.mark.asyncio
    async def test_quality_weights(self, analyzer):
        """Test that quality weights are properly configured"""
        
        assert hasattr(analyzer, 'quality_weights')
        assert 'topic_relevance' in analyzer.quality_weights
        assert 'readability' in analyzer.quality_weights
        assert 'domain_authority' in analyzer.quality_weights
        
        # Check that weights sum to approximately 1.0
        total_weight = sum(analyzer.quality_weights.values())
        assert abs(total_weight - 1.0) < 0.01
    
    @pytest.mark.asyncio
    async def test_performance_with_large_content(self, analyzer, sample_url, sample_topic):
        """Test performance with large content"""
        
        large_content = "This is a test sentence. " * 10000  # Large content
        
        import time
        start_time = time.time()
        
        result = await analyzer.analyze_content_quality(
            content=large_content,
            url=sample_url,
            topic=sample_topic
        )
        
        execution_time = time.time() - start_time
        
        assert isinstance(result, ContentQualityScores)
        assert execution_time < 10.0  # Should complete within 10 seconds
        assert result.assessment_metadata['content_length'] > 100000
    
    @pytest.mark.asyncio
    async def test_metadata_generation(self, analyzer, sample_content, sample_url, sample_topic):
        """Test metadata generation in assessment"""
        
        result = await analyzer.analyze_content_quality(
            content=sample_content,
            url=sample_url,
            topic=sample_topic
        )
        
        metadata = result.assessment_metadata
        
        assert 'content_length' in metadata
        assert 'word_count' in metadata
        assert 'sentence_count' in metadata
        assert 'paragraph_count' in metadata
        assert 'analysis_timestamp' in metadata
        assert 'url_domain' in metadata
        assert 'topic_analyzed' in metadata
        
        assert metadata['content_length'] > 0
        assert metadata['word_count'] > 0
        assert metadata['sentence_count'] > 0
        assert metadata['paragraph_count'] > 0
        assert metadata['url_domain'] == 'example.com'
        assert metadata['topic_analyzed'] == sample_topic

if __name__ == "__main__":
    pytest.main([__file__])
