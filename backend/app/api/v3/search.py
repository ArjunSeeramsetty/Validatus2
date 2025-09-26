"""
Live Web Search API
"""
from fastapi import APIRouter, HTTPException, Query
import requests
import os
import logging

router = APIRouter(tags=["live_search"])
logger = logging.getLogger(__name__)

@router.get("/search/live", summary="Perform live web search")
async def live_search(q: str = Query(..., description="Search query"), num: int = Query(3, description="Max results")):
    """Perform live web search using Google Custom Search API"""
    try:
        # For development, use mock data if API keys are not available
        api_key = os.getenv("LIVE_SEARCH_API_KEY")
        cx = os.getenv("LIVE_SEARCH_CX")
        
        if not api_key or not cx:
            logger.warning("Live search API keys not configured, returning mock data")
            return generate_mock_search_results(q, num)
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": api_key, "cx": cx, "q": q, "num": num}
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        results = [{
            "title": it.get("title"),
            "snippet": it.get("snippet"),
            "link": it.get("link")
        } for it in items]
        return {"query": q, "results": results}
    except Exception as e:
        logger.error(f"Live search failed: {str(e)}")
        # Return mock data on error for development
        return generate_mock_search_results(q, num)

def generate_mock_search_results(query: str, num: int):
    """Generate mock search results for development"""
    mock_results = [
        {
            "title": f"Market Analysis: {query}",
            "snippet": f"Comprehensive market analysis and trends for {query}. Industry insights and growth projections.",
            "link": "https://example.com/market-analysis"
        },
        {
            "title": f"Industry Report: {query}",
            "snippet": f"Latest industry report covering {query} market dynamics, competitive landscape, and opportunities.",
            "link": "https://example.com/industry-report"
        },
        {
            "title": f"Business Intelligence: {query}",
            "snippet": f"Strategic business intelligence and data insights for {query} market segment.",
            "link": "https://example.com/business-intelligence"
        }
    ]
    
    return {
        "query": query,
        "results": mock_results[:num],
        "source": "mock_data"
    }
