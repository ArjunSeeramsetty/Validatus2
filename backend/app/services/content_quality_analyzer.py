# backend/app/services/content_quality_analyzer.py

import asyncio
import logging
import re
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone
import hashlib

from ..models.analysis_models import ContentQualityScores

# Optional monitoring import (requires google-cloud-monitoring)
try:
    from ..middleware.monitoring import performance_monitor
    MONITORING_AVAILABLE = True
except ImportError:
    # Create a no-op decorator when monitoring not available
    def performance_monitor(func):
        return func
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)

class ContentQualityAnalyzer:
    """Advanced content quality analysis using multiple metrics"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Validatus-ContentAnalyzer/1.0'
        })
        
        # Quality assessment weights
        self.quality_weights = {
            'topic_relevance': 0.25,
            'readability': 0.15,
            'domain_authority': 0.20,
            'content_freshness': 0.10,
            'factual_accuracy': 0.15,
            'completeness': 0.10,
            'uniqueness': 0.05
        }
        
    @performance_monitor
    async def analyze_content_quality(self, 
                                    content: str, 
                                    url: str, 
                                    topic: str) -> ContentQualityScores:
        """Comprehensive content quality analysis"""
        
        logger.info(f"Analyzing content quality for URL: {url}")
        
        try:
            # Perform parallel quality assessments
            tasks = [
                self._assess_topic_relevance(content, topic),
                self._assess_readability(content),
                self._assess_domain_authority(url),
                self._assess_content_freshness(content),
                self._assess_factual_accuracy(content),
                self._assess_completeness(content),
                self._assess_uniqueness(content, url)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Extract individual scores
            topic_relevance = results[0] if not isinstance(results[0], Exception) else 0.5
            readability = results[1] if not isinstance(results[1], Exception) else 0.5
            domain_authority = results[2] if not isinstance(results[2], Exception) else 0.5
            content_freshness = results[3] if not isinstance(results[3], Exception) else 0.5
            factual_accuracy = results[4] if not isinstance(results[4], Exception) else 0.5
            completeness = results[5] if not isinstance(results[5], Exception) else 0.5
            uniqueness = results[6] if not isinstance(results[6], Exception) else 0.5
            
            # Calculate engagement potential
            engagement_potential = await self._assess_engagement_potential(content)
            
            # Calculate weighted overall score
            overall_score = (
                topic_relevance * self.quality_weights['topic_relevance'] +
                readability * self.quality_weights['readability'] +
                domain_authority * self.quality_weights['domain_authority'] +
                content_freshness * self.quality_weights['content_freshness'] +
                factual_accuracy * self.quality_weights['factual_accuracy'] +
                completeness * self.quality_weights['completeness'] +
                uniqueness * self.quality_weights['uniqueness']
            )
            
            # Create assessment metadata
            assessment_metadata = {
                'content_length': len(content),
                'word_count': len(content.split()),
                'sentence_count': len([s for s in content.split('.') if s.strip()]),
                'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'url_domain': urlparse(url).netloc,
                'topic_analyzed': topic
            }
            
            quality_scores = ContentQualityScores(
                overall_score=round(overall_score, 3),
                topic_relevance=round(topic_relevance, 3),
                readability=round(readability, 3),
                domain_authority=round(domain_authority, 3),
                content_freshness=round(content_freshness, 3),
                factual_accuracy=round(factual_accuracy, 3),
                completeness=round(completeness, 3),
                uniqueness=round(uniqueness, 3),
                engagement_potential=round(engagement_potential, 3),
                assessment_metadata=assessment_metadata
            )
            
            logger.info(f"Quality analysis completed - Overall score: {overall_score:.3f}")
            return quality_scores
            
        except Exception as e:
            logger.error(f"Content quality analysis failed: {e}")
            # Return default scores on failure
            return ContentQualityScores(
                overall_score=0.5,
                topic_relevance=0.5,
                readability=0.5,
                domain_authority=0.5,
                content_freshness=0.5,
                factual_accuracy=0.5,
                completeness=0.5,
                uniqueness=0.5,
                engagement_potential=0.5,
                assessment_metadata={'error': str(e)}
            )
    
    async def _assess_topic_relevance(self, content: str, topic: str) -> float:
        """Assess how relevant the content is to the specified topic"""
        try:
            # Extract topic keywords
            topic_keywords = set(topic.lower().split())
            content_words = set(content.lower().split())
            
            # Calculate keyword overlap
            keyword_overlap = len(topic_keywords.intersection(content_words))
            keyword_density = keyword_overlap / len(topic_keywords) if topic_keywords else 0
            
            # Check for topic-related phrases
            topic_phrases = [
                f"{topic}",
                f"{topic.lower()}",
                f"{topic.upper()}",
                f"{topic.title()}"
            ]
            
            phrase_matches = sum(1 for phrase in topic_phrases if phrase in content.lower())
            phrase_relevance = min(phrase_matches * 0.2, 1.0)
            
            # Combine metrics
            relevance_score = min(keyword_density + phrase_relevance, 1.0)
            
            return relevance_score
            
        except Exception as e:
            logger.error(f"Topic relevance assessment failed: {e}")
            return 0.5
    
    async def _assess_readability(self, content: str) -> float:
        """Assess content readability using multiple metrics"""
        try:
            words = content.split()
            sentences = [s for s in content.split('.') if s.strip()]
            paragraphs = [p for p in content.split('\n\n') if p.strip()]
            
            if not words or not sentences:
                return 0.5
            
            # Average words per sentence
            avg_words_per_sentence = len(words) / len(sentences)
            
            # Sentence length score (optimal range: 15-20 words)
            if 15 <= avg_words_per_sentence <= 20:
                sentence_score = 1.0
            elif avg_words_per_sentence < 15:
                sentence_score = avg_words_per_sentence / 15
            else:
                sentence_score = max(0.3, 1.0 - (avg_words_per_sentence - 20) / 20)
            
            # Paragraph structure score
            if paragraphs:
                avg_sentences_per_paragraph = len(sentences) / len(paragraphs)
                if 3 <= avg_sentences_per_paragraph <= 7:
                    paragraph_score = 1.0
                else:
                    paragraph_score = max(0.5, 1.0 - abs(avg_sentences_per_paragraph - 5) / 5)
            else:
                paragraph_score = 0.5
            
            # Vocabulary complexity (simple heuristic)
            complex_words = sum(1 for word in words if len(word) > 6)
            vocabulary_complexity = complex_words / len(words)
            
            if 0.1 <= vocabulary_complexity <= 0.3:
                vocabulary_score = 1.0
            else:
                vocabulary_score = max(0.3, 1.0 - abs(vocabulary_complexity - 0.2) / 0.2)
            
            # Combined readability score
            readability_score = (
                sentence_score * 0.4 +
                paragraph_score * 0.3 +
                vocabulary_score * 0.3
            )
            
            return min(readability_score, 1.0)
            
        except Exception as e:
            logger.error(f"Readability assessment failed: {e}")
            return 0.5
    
    async def _assess_domain_authority(self, url: str) -> float:
        """Assess domain authority and credibility"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Known high-authority domains
            high_authority_domains = {
                'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
                'wikipedia.org', 'github.com', 'stackoverflow.com',
                'medium.com', 'techcrunch.com', 'forbes.com',
                'reuters.com', 'bloomberg.com', 'wsj.com',
                'harvard.edu', 'mit.edu', 'stanford.edu'
            }
            
            # Check if domain is in high-authority list
            if any(auth_domain in domain for auth_domain in high_authority_domains):
                return 1.0
            
            # Check for educational institutions
            if '.edu' in domain:
                return 0.9
            
            # Check for government domains
            if '.gov' in domain:
                return 0.9
            
            # Check for established organizations
            if '.org' in domain:
                return 0.7
            
            # Check domain length and structure (heuristic)
            domain_parts = domain.split('.')
            if len(domain_parts) == 2 and len(domain_parts[0]) > 5:
                return 0.6
            
            # Default for unknown domains
            return 0.4
            
        except Exception as e:
            logger.error(f"Domain authority assessment failed: {e}")
            return 0.5
    
    async def _assess_content_freshness(self, content: str) -> float:
        """Assess content freshness and recency"""
        try:
            # Look for date indicators in content
            current_year = datetime.now().year
            year_pattern = r'\b(19|20)\d{2}\b'
            years_found = re.findall(year_pattern, content)
            
            if years_found:
                latest_year = max(int(year) for year in years_found)
                years_old = current_year - latest_year
                
                if years_old == 0:
                    return 1.0
                elif years_old == 1:
                    return 0.9
                elif years_old <= 3:
                    return 0.7
                elif years_old <= 5:
                    return 0.5
                else:
                    return 0.3
            
            # Check for temporal keywords
            recent_keywords = [
                'recently', 'latest', 'new', 'current', 'today',
                '2024', '2025', 'this year', 'nowadays'
            ]
            
            recent_mentions = sum(1 for keyword in recent_keywords 
                                if keyword.lower() in content.lower())
            
            if recent_mentions > 0:
                return min(0.6 + (recent_mentions * 0.1), 1.0)
            
            # Default freshness score
            return 0.4
            
        except Exception as e:
            logger.error(f"Content freshness assessment failed: {e}")
            return 0.5
    
    async def _assess_factual_accuracy(self, content: str) -> float:
        """Assess factual accuracy using heuristics"""
        try:
            # Check for factual indicators
            factual_indicators = [
                'according to', 'research shows', 'study found',
                'data indicates', 'statistics show', 'evidence suggests',
                'peer-reviewed', 'published in', 'journal article'
            ]
            
            factual_mentions = sum(1 for indicator in factual_indicators 
                                 if indicator.lower() in content.lower())
            
            # Check for citation patterns
            citation_patterns = [
                r'\[\d+\]',  # [1], [2], etc.
                r'\(\d{4}\)',  # (2024), etc.
                r'http[s]?://',  # URLs
                r'www\.',  # www references
            ]
            
            citations_found = sum(1 for pattern in citation_patterns 
                                if re.search(pattern, content))
            
            # Check for objective language vs subjective
            subjective_words = ['i think', 'i believe', 'in my opinion', 'probably', 'maybe']
            subjective_count = sum(1 for word in subjective_words 
                                 if word.lower() in content.lower())
            
            # Calculate accuracy score
            factual_score = min(factual_mentions * 0.15 + citations_found * 0.1, 0.8)
            subjective_penalty = min(subjective_count * 0.1, 0.3)
            
            accuracy_score = max(0.3, factual_score - subjective_penalty)
            
            return accuracy_score
            
        except Exception as e:
            logger.error(f"Factual accuracy assessment failed: {e}")
            return 0.5
    
    async def _assess_completeness(self, content: str) -> float:
        """Assess content completeness and depth"""
        try:
            word_count = len(content.split())
            
            # Minimum length thresholds
            if word_count < 100:
                return 0.2
            elif word_count < 300:
                return 0.4
            elif word_count < 600:
                return 0.6
            elif word_count < 1000:
                return 0.8
            else:
                return 1.0
                
        except Exception as e:
            logger.error(f"Completeness assessment failed: {e}")
            return 0.5
    
    async def _assess_uniqueness(self, content: str, url: str) -> float:
        """Assess content uniqueness (simplified implementation)"""
        try:
            # Simple uniqueness check based on content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # In a real implementation, this would check against a database
            # of known content hashes. For now, we'll use a heuristic.
            
            # Check for common boilerplate text
            boilerplate_phrases = [
                'copyright', 'all rights reserved', 'terms of service',
                'privacy policy', 'cookie policy', 'contact us'
            ]
            
            boilerplate_count = sum(1 for phrase in boilerplate_phrases 
                                  if phrase.lower() in content.lower())
            
            # More boilerplate = less unique
            uniqueness_score = max(0.3, 1.0 - (boilerplate_count * 0.2))
            
            return uniqueness_score
            
        except Exception as e:
            logger.error(f"Uniqueness assessment failed: {e}")
            return 0.5
    
    async def _assess_engagement_potential(self, content: str) -> float:
        """Assess potential for user engagement"""
        try:
            # Check for engagement elements
            engagement_elements = [
                'questions', '?', 'how to', 'tips', 'guide',
                'examples', 'case study', 'tutorial', 'step by step'
            ]
            
            engagement_count = sum(1 for element in engagement_elements 
                                 if element.lower() in content.lower())
            
            # Check for interactive elements
            interactive_elements = ['click here', 'download', 'sign up', 'subscribe']
            interactive_count = sum(1 for element in interactive_elements 
                                  if element.lower() in content.lower())
            
            # Calculate engagement score
            engagement_score = min(
                engagement_count * 0.1 + interactive_count * 0.15, 
                1.0
            )
            
            return max(0.3, engagement_score)
            
        except Exception as e:
            logger.error(f"Engagement potential assessment failed: {e}")
            return 0.5

# Export the class
__all__ = ['ContentQualityAnalyzer']
