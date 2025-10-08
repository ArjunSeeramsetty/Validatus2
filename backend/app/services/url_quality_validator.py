"""
URL Quality Validator for Strategic Analysis
Validates and scores URLs based on relevance, quality, and usefulness for strategy analysis
"""
import re
import urllib.parse
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class URLQualityValidator:
    """
    Validates URL quality and relevance for strategic analysis
    
    Scoring Criteria:
    1. Domain Authority (0-0.3): .edu, .gov, .org domains get higher scores
    2. Content Indicators (0-0.3): Keywords in URL indicating strategic content
    3. Source Type (0-0.2): News, research, reports, etc.
    4. URL Structure (0-0.2): Clean vs dynamic/generated URLs
    5. Relevance Match (0-0.3): Match with topic and strategic keywords
    """
    
    # High-authority domain TLDs
    HIGH_AUTHORITY_TLDS = ['.edu', '.gov', '.org']
    
    # Trusted research and news domains
    TRUSTED_DOMAINS = [
        'harvard.edu', 'mit.edu', 'stanford.edu',
        'mckinsey.com', 'bcg.com', 'bain.com',
        'gartner.com', 'forrester.com', 'idc.com',
        'reuters.com', 'bloomberg.com', 'wsj.com',
        'ft.com', 'economist.com', 'forbes.com',
        'hbr.org', 'sloanreview.mit.edu',
        'statista.com', 'nielsen.com', 'pewresearch.org'
    ]
    
    # Strategic content indicators in URL
    STRATEGIC_INDICATORS = [
        'market-analysis', 'market-research', 'industry-report',
        'competitive-analysis', 'strategy', 'insights',
        'trends', 'forecast', 'outlook', 'whitepaper',
        'case-study', 'report', 'research', 'analysis',
        'survey', 'study', 'data', 'statistics'
    ]
    
    # Low-quality URL patterns to penalize
    LOW_QUALITY_PATTERNS = [
        r'\?.*id=\d+.*&.*&.*',  # Multiple query parameters
        r'/tag/', r'/category/', r'/author/',  # Blog navigation
        r'/page/\d+', r'/p/\d+',  # Pagination
        r'\.pdf$',  # PDF files (may not be scrapable)
        r'/login', r'/signin', r'/register',  # Auth pages
        r'/cart', r'/checkout', r'/account'  # E-commerce pages
    ]
    
    # File extensions to exclude
    EXCLUDED_EXTENSIONS = [
        '.pdf', '.doc', '.docx', '.ppt', '.pptx',
        '.xls', '.xlsx', '.zip', '.rar', '.exe'
    ]
    
    def validate_and_score(
        self,
        url: str,
        title: str,
        snippet: str,
        topic: str,
        relevance_score: float
    ) -> Dict[str, Any]:
        """
        Validate URL and calculate comprehensive quality score
        
        Args:
            url: The URL to validate
            title: Page title
            snippet: Page description/snippet
            topic: Main topic for relevance checking
            relevance_score: Pre-calculated relevance score
            
        Returns:
            Dict with validation results including:
            - is_valid: bool
            - quality_score: float (0-1)
            - confidence: float (0-1)
            - rejection_reason: str (if rejected)
            - scoring_breakdown: Dict with component scores
        """
        parsed_url = urllib.parse.urlparse(url.lower())
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # Initialize scores
        domain_score = 0.0
        content_score = 0.0
        structure_score = 0.0
        source_score = 0.0
        topic_match_score = relevance_score * 0.3  # Use provided relevance
        
        # Check for exclusions
        is_valid, rejection_reason = self._check_exclusions(url, parsed_url)
        if not is_valid:
            return {
                "is_valid": False,
                "quality_score": 0.0,
                "confidence": 1.0,
                "rejection_reason": rejection_reason,
                "priority_level": 10,  # Lowest priority
                "scoring_breakdown": {}
            }
        
        # 1. Domain Authority Score (0-0.3)
        domain_score = self._calculate_domain_score(domain)
        
        # 2. Content Indicators Score (0-0.3)
        content_score = self._calculate_content_score(url, title, snippet)
        
        # 3. Source Type Score (0-0.2)
        source_score = self._calculate_source_score(domain, path)
        
        # 4. URL Structure Score (0-0.2)
        structure_score = self._calculate_structure_score(url, path)
        
        # Calculate total quality score
        quality_score = (
            domain_score + 
            content_score + 
            source_score + 
            structure_score + 
            topic_match_score
        )
        
        # Clamp to 0-1 range
        quality_score = min(1.0, max(0.0, quality_score))
        
        # Calculate confidence based on available signals
        confidence = self._calculate_confidence(title, snippet, domain)
        
        # Determine priority level (1=highest, 10=lowest)
        priority_level = self._calculate_priority(quality_score, domain_score)
        
        # Determine if URL should be used
        is_valid = quality_score >= 0.3  # Minimum threshold
        
        return {
            "is_valid": is_valid,
            "quality_score": round(quality_score, 3),
            "confidence": round(confidence, 3),
            "priority_level": priority_level,
            "rejection_reason": "Quality score below threshold" if not is_valid else None,
            "scoring_breakdown": {
                "domain_authority": round(domain_score, 3),
                "content_indicators": round(content_score, 3),
                "source_type": round(source_score, 3),
                "url_structure": round(structure_score, 3),
                "topic_relevance": round(topic_match_score, 3)
            }
        }
    
    def _check_exclusions(self, url: str, parsed_url) -> tuple[bool, str]:
        """Check if URL should be excluded"""
        # Check file extensions
        for ext in self.EXCLUDED_EXTENSIONS:
            if url.lower().endswith(ext):
                return False, f"Excluded file type: {ext}"
        
        # Check low-quality patterns
        for pattern in self.LOW_QUALITY_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return False, f"Low-quality URL pattern detected"
        
        return True, None
    
    def _calculate_domain_score(self, domain: str) -> float:
        """Calculate domain authority score"""
        score = 0.0
        
        # Check trusted domains (full match)
        if any(trusted in domain for trusted in self.TRUSTED_DOMAINS):
            score = 0.3
            return score
        
        # Check high-authority TLDs
        for tld in self.HIGH_AUTHORITY_TLDS:
            if domain.endswith(tld):
                score = 0.25
                break
        
        # Generic TLDs get baseline score
        if score == 0.0:
            if domain.endswith('.com') or domain.endswith('.net'):
                score = 0.1
        
        return score
    
    def _calculate_content_score(self, url: str, title: str, snippet: str) -> float:
        """Calculate content quality score based on strategic indicators"""
        score = 0.0
        found_indicators = 0
        
        # Check URL for strategic indicators
        url_lower = url.lower()
        for indicator in self.STRATEGIC_INDICATORS:
            if indicator in url_lower or indicator.replace('-', ' ') in url_lower:
                found_indicators += 1
        
        # Check title for strategic indicators
        title_lower = title.lower() if title else ""
        for indicator in self.STRATEGIC_INDICATORS:
            if indicator.replace('-', ' ') in title_lower:
                found_indicators += 1
        
        # Check snippet for strategic keywords
        snippet_lower = snippet.lower() if snippet else ""
        strategic_keywords = ['analysis', 'research', 'market', 'strategy', 'report', 'insights']
        for keyword in strategic_keywords:
            if keyword in snippet_lower:
                found_indicators += 1
        
        # Calculate score (max 0.3)
        score = min(0.3, found_indicators * 0.05)
        
        return score
    
    def _calculate_source_score(self, domain: str, path: str) -> float:
        """Calculate source type score"""
        score = 0.1  # Baseline
        
        # Research/report indicators
        if any(term in path for term in ['/research/', '/report/', '/insights/', '/whitepaper/']):
            score = 0.2
        
        # News/article indicators
        if any(term in path for term in ['/news/', '/article/', '/blog/', '/post/']):
            score = 0.15
        
        return score
    
    def _calculate_structure_score(self, url: str, path: str) -> float:
        """Calculate URL structure quality score"""
        score = 0.2  # Start with full score
        
        # Penalize very long URLs
        if len(url) > 150:
            score -= 0.05
        if len(url) > 200:
            score -= 0.05
        
        # Penalize excessive query parameters
        query_params = url.count('&')
        if query_params > 3:
            score -= 0.05
        
        # Penalize deep nesting (>5 levels)
        path_depth = path.count('/')
        if path_depth > 5:
            score -= 0.03
        
        return max(0.0, score)
    
    def _calculate_confidence(self, title: str, snippet: str, domain: str) -> float:
        """Calculate confidence in quality assessment"""
        confidence = 0.5  # Base confidence
        
        # More signals = higher confidence
        if title and len(title) > 10:
            confidence += 0.15
        if snippet and len(snippet) > 20:
            confidence += 0.15
        if any(trusted in domain for trusted in self.TRUSTED_DOMAINS):
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _calculate_priority(self, quality_score: float, domain_score: float) -> int:
        """Calculate processing priority (1=highest, 10=lowest)"""
        # Combine quality and domain scores for priority
        combined_score = (quality_score * 0.7) + (domain_score * 0.3)
        
        if combined_score >= 0.8:
            return 1  # Highest priority
        elif combined_score >= 0.7:
            return 2
        elif combined_score >= 0.6:
            return 3
        elif combined_score >= 0.5:
            return 4
        elif combined_score >= 0.4:
            return 5
        else:
            return max(6, min(10, int((1 - combined_score) * 10)))


# Singleton instance
_url_validator: URLQualityValidator = None

def get_url_validator() -> URLQualityValidator:
    """Get or create URL quality validator singleton"""
    global _url_validator
    if _url_validator is None:
        _url_validator = URLQualityValidator()
    return _url_validator

