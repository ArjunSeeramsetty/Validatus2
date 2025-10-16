"""
Market Growth & Demand Analyzer
Fixes zero scores for Market Size and Growth Rate
Extracts actual market data from scraped content using LLM analysis
"""
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class MarketGrowthDemandAnalyzer:
    """
    Analyzes scraped content to extract market size and growth data
    Addresses the issue of Growth & Demand showing 0.00 scores
    """
    
    def __init__(self, llm_service=None):
        """Initialize with LLM service for content analysis"""
        self.llm_service = llm_service
        logger.info("Market Growth & Demand Analyzer initialized")
    
    async def analyze_growth_demand(self, session_id: str, scraped_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze growth and demand from scraped content
        
        Returns:
            Dict with market_size_score, growth_rate_score, and supporting data
        """
        try:
            if not scraped_content:
                return self._get_default_response("No content available for analysis")
            
            # Combine scraped content
            combined_content = self._combine_content(scraped_content)
            
            # Extract market metrics using LLM
            market_metrics = await self._extract_market_metrics(combined_content)
            
            # Calculate scores
            market_size_score = self._calculate_market_size_score(market_metrics)
            growth_rate_score = self._calculate_growth_rate_score(market_metrics)
            
            return {
                "session_id": session_id,
                "market_size": {
                    "score": market_size_score['score'],
                    "confidence": market_size_score['confidence'],
                    "value": market_size_score['value'],
                    "currency": market_size_score['currency'],
                    "evidence": market_size_score['evidence'],
                    "data_found": market_size_score['data_found']
                },
                "growth_rate": {
                    "score": growth_rate_score['score'],
                    "confidence": growth_rate_score['confidence'],
                    "cagr": growth_rate_score['cagr'],
                    "projection_period": growth_rate_score['period'],
                    "evidence": growth_rate_score['evidence'],
                    "data_found": growth_rate_score['data_found']
                },
                "demand_drivers": market_metrics.get('demand_drivers', []),
                "market_dynamics": market_metrics.get('market_dynamics', {}),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Growth & Demand analysis failed for {session_id}: {e}", exc_info=True)
            return self._get_default_response(f"Analysis error: {str(e)}")
    
    def _combine_content(self, scraped_content: List[Dict[str, Any]], max_chars: int = 15000) -> str:
        """Combine scraped content into single text for analysis"""
        combined = []
        total_chars = 0
        
        for item in scraped_content:
            content = item.get('content', '')
            title = item.get('title', '')
            
            # Prioritize content with market/growth keywords
            has_market_keywords = any(keyword in content.lower() for keyword in [
                'market size', 'market value', 'billion', 'million', 'cagr', 
                'growth rate', 'forecast', 'projected', 'market research'
            ])
            
            item_text = f"Title: {title}\n{content}\n\n"
            
            if has_market_keywords:
                # Prioritize market-relevant content
                combined.insert(0, item_text)
            else:
                combined.append(item_text)
            
            total_chars += len(item_text)
            if total_chars >= max_chars:
                break
        
        return ''.join(combined)[:max_chars]
    
    async def _extract_market_metrics(self, content: str) -> Dict[str, Any]:
        """Extract market metrics from content using LLM"""
        
        if not self.llm_service:
            # Fallback: simple regex extraction
            return self._regex_fallback_extraction(content)
        
        prompt = f"""
Analyze this market research content and extract specific market metrics.

Content:
{content}

Extract the following metrics. If data is NOT found, mark data_found as false and score as 0.0:

1. **Market Size**: 
   - Look for: "$X billion", "€X million", "market value", "market size"
   - Convert to USD billions
   - Extract currency and exact value

2. **Growth Rate**:
   - Look for: "CAGR", "compound annual growth rate", "growth rate", "% growth", "YoY growth"
   - Extract percentage value
   - Extract time period (e.g., "2024-2030")

3. **Demand Drivers**:
   - List key factors driving market demand
   - Extract 3-5 specific drivers mentioned

4. **Market Maturity**:
   - Assess if market is emerging (score: 0.3), growing (0.6), or mature (0.9)

Return JSON:
{{
  "market_size": {{
    "value_usd_billions": float or null,
    "currency": str,
    "original_text": str,
    "data_found": bool,
    "confidence": float (0-1)
  }},
  "growth_rate": {{
    "cagr_percent": float or null,
    "period": str,
    "original_text": str,
    "data_found": bool,
    "confidence": float (0-1)
  }},
  "demand_drivers": [str],
  "market_maturity": {{
    "stage": str (emerging/growing/mature),
    "score": float (0-1)
  }}
}}

If no data found, return all data_found as false and scores as 0.0.
"""
        
        try:
            # Call LLM service
            response = await self.llm_service.generate_structured_output(
                prompt=prompt,
                response_format="json"
            )
            
            return response
            
        except Exception as e:
            logger.warning(f"LLM extraction failed, using regex fallback: {e}")
            return self._regex_fallback_extraction(content)
    
    def _regex_fallback_extraction(self, content: str) -> Dict[str, Any]:
        """Fallback regex-based extraction when LLM not available"""
        
        # Extract market size
        market_size_patterns = [
            r'\$?(\d+\.?\d*)\s*(billion|trillion)\s*(USD|dollars?)?',
            r'€(\d+\.?\d*)\s*(billion|million)',
            r'market\s+size[:\s]+\$?(\d+\.?\d*)\s*(B|M)',
        ]
        
        market_value = None
        market_text = None
        for pattern in market_size_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit = match.group(2).lower()
                
                # Convert to billions
                if unit in ['million', 'm']:
                    value = value / 1000
                elif unit in ['trillion']:
                    value = value * 1000
                
                market_value = value
                market_text = match.group(0)
                break
        
        # Extract growth rate
        growth_patterns = [
            r'(\d+\.?\d*)%\s+CAGR',
            r'CAGR\s+of\s+(\d+\.?\d*)%',
            r'growth\s+rate\s+of\s+(\d+\.?\d*)%',
            r'growing\s+at\s+(\d+\.?\d*)%'
        ]
        
        growth_rate = None
        growth_text = None
        for pattern in growth_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                growth_rate = float(match.group(1))
                growth_text = match.group(0)
                break
        
        return {
            "market_size": {
                "value_usd_billions": market_value,
                "currency": "USD",
                "original_text": market_text or "No data found",
                "data_found": market_value is not None,
                "confidence": 0.6 if market_value else 0.0
            },
            "growth_rate": {
                "cagr_percent": growth_rate,
                "period": "Unknown",
                "original_text": growth_text or "No data found",
                "data_found": growth_rate is not None,
                "confidence": 0.6 if growth_rate else 0.0
            },
            "demand_drivers": [],
            "market_maturity": {
                "stage": "unknown",
                "score": 0.5
            }
        }
    
    def _calculate_market_size_score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate normalized market size score (0.0-1.0)"""
        
        market_size_data = metrics.get('market_size', {})
        
        if not market_size_data.get('data_found', False):
            return {
                "score": 0.0,
                "confidence": 0.0,
                "value": None,
                "currency": "USD",
                "evidence": "No market size data found in content",
                "data_found": False
            }
        
        value_billions = market_size_data.get('value_usd_billions', 0)
        
        if value_billions <= 0:
            return {
                "score": 0.0,
                "confidence": market_size_data.get('confidence', 0.0),
                "value": 0,
                "currency": market_size_data.get('currency', 'USD'),
                "evidence": market_size_data.get('original_text', 'Invalid market size'),
                "data_found": False
            }
        
        # Logarithmic scoring (0.1B = 0.1, 1B = 0.4, 10B = 0.7, 100B = 0.9, 1T+ = 1.0)
        # Formula: score = min(1.0, 0.2 + 0.25 * log10(value))
        log_value = np.log10(value_billions)
        raw_score = 0.2 + 0.25 * log_value
        normalized_score = min(1.0, max(0.0, raw_score))
        
        return {
            "score": normalized_score,
            "confidence": market_size_data.get('confidence', 0.7),
            "value": value_billions,
            "currency": market_size_data.get('currency', 'USD'),
            "evidence": market_size_data.get('original_text', f"${value_billions:.2f}B market"),
            "data_found": True,
            "calculation": f"Logarithmic: 0.2 + 0.25 * log10({value_billions:.2f}) = {normalized_score:.3f}"
        }
    
    def _calculate_growth_rate_score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate normalized growth rate score (0.0-1.0)"""
        
        growth_data = metrics.get('growth_rate', {})
        
        if not growth_data.get('data_found', False):
            return {
                "score": 0.0,
                "confidence": 0.0,
                "cagr": None,
                "period": "N/A",
                "evidence": "No growth rate data found in content",
                "data_found": False
            }
        
        cagr_percent = growth_data.get('cagr_percent', 0)
        
        if cagr_percent <= 0:
            return {
                "score": 0.0,
                "confidence": growth_data.get('confidence', 0.0),
                "cagr": 0,
                "period": growth_data.get('period', 'N/A'),
                "evidence": growth_data.get('original_text', 'Invalid growth rate'),
                "data_found": False
            }
        
        # Linear-sigmoid scoring (0% = 0.0, 5% = 0.5, 10% = 0.75, 20%+ = 0.95, 30%+ = 1.0)
        # Formula: sigmoid transform of growth rate
        if cagr_percent < 5:
            normalized_score = cagr_percent / 10  # 0-5% → 0-0.5
        elif cagr_percent < 15:
            normalized_score = 0.5 + (cagr_percent - 5) / 20  # 5-15% → 0.5-1.0
        else:
            normalized_score = min(1.0, 0.8 + (cagr_percent - 15) / 30)  # 15%+ → 0.8-1.0
        
        normalized_score = min(1.0, max(0.0, normalized_score))
        
        return {
            "score": normalized_score,
            "confidence": growth_data.get('confidence', 0.7),
            "cagr": cagr_percent,
            "period": growth_data.get('period', 'Unknown'),
            "evidence": growth_data.get('original_text', f"{cagr_percent}% CAGR"),
            "data_found": True,
            "calculation": f"Sigmoid: CAGR {cagr_percent}% → score {normalized_score:.3f}"
        }
    
    def _get_default_response(self, reason: str) -> Dict[str, Any]:
        """Default response when analysis fails"""
        return {
            "session_id": None,
            "market_size": {
                "score": 0.0,
                "confidence": 0.0,
                "value": None,
                "currency": "USD",
                "evidence": reason,
                "data_found": False
            },
            "growth_rate": {
                "score": 0.0,
                "confidence": 0.0,
                "cagr": None,
                "period": "N/A",
                "evidence": reason,
                "data_found": False
            },
            "demand_drivers": [],
            "market_dynamics": {},
            "analyzed_at": datetime.utcnow().isoformat()
        }


# Singleton instance
_analyzer_instance = None

def get_market_growth_demand_analyzer(llm_service=None):
    """Get or create singleton analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = MarketGrowthDemandAnalyzer(llm_service)
    return _analyzer_instance

