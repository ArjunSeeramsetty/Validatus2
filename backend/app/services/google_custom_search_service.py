"""
Google Custom Search Service for URL Collection
Integrates with existing Validatus repository architecture
"""
import asyncio
import aiohttp
import hashlib
import urllib.parse
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
import json
import logging

from ..core.gcp_persistence_config import get_gcp_persistence_settings

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Single search result from Google Custom Search"""
    title: str
    url: str
    snippet: str
    display_url: str
    formatted_url: str
    domain: str
    relevance_score: float = 0.0
    search_query: str = ""
    metadata: Dict[str, Any] = None

@dataclass
class SearchResultsSet:
    """Collection of search results for a query"""
    query: str
    total_results: int
    search_time_ms: int
    results: List[SearchResult]
    next_start_index: Optional[int] = None
    error: Optional[str] = None

class GoogleCustomSearchService:
    """
    Google Custom Search API integration service
    Uses existing repository configuration and follows established patterns
    """
    
    def __init__(self):
        self.settings = get_gcp_persistence_settings()
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self._url_cache: Set[str] = set()
        
    async def initialize(self):
        """Initialize the search service with secure credentials"""
        if self.session is not None:
            logger.warning("Service already initialized")
            return
            
        self.api_key = self.settings.get_secure_api_key()
        self.cse_id = self.settings.get_secure_cse_id()
        
        if not self.api_key or not self.cse_id:
            raise ValueError("Google Custom Search API key and CSE ID are required")
        
        # Create HTTP session with timeout
        timeout = aiohttp.ClientTimeout(total=self.settings.url_collection_timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        logger.info("Google Custom Search Service initialized")
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    async def search_urls_for_topic(
        self, 
        search_queries: List[str], 
        session_id: str,
        max_results_per_query: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search URLs for a topic using multiple queries
        This is the main integration point with the existing repository
        """
        if not self.session:
            await self.initialize()
        
        max_results = max_results_per_query or self.settings.max_urls_per_query
        all_results = []
        query_stats = {}
        total_api_calls = 0
        
        logger.info(f"Starting URL collection for session {session_id} with {len(search_queries)} queries")
        
        for query in search_queries:
            try:
                logger.info(f"Searching for query: '{query}'")
                
                search_results = await self._execute_search(
                    query=query,
                    num_results=max_results,
                    session_id=session_id
                )
                
                if search_results.error:
                    logger.error(f"Search failed for query '{query}': {search_results.error}")
                    query_stats[query] = {"error": search_results.error, "results": 0}
                    continue
                
                # Apply domain filtering and deduplication
                filtered_results = self._filter_and_dedupe_results(search_results.results, query)
                
                all_results.extend(filtered_results)
                total_api_calls += 1
                
                query_stats[query] = {
                    "total_found": search_results.total_results,
                    "results_returned": len(search_results.results),
                    "results_after_filtering": len(filtered_results),
                    "search_time_ms": search_results.search_time_ms
                }
                
                logger.info(f"Query '{query}': {len(filtered_results)} URLs after filtering")
                
                # Rate limiting - respect Google's API limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error searching for query '{query}': {e}")
                query_stats[query] = {"error": str(e), "results": 0}
        
        # Final deduplication across all queries
        unique_results = self._final_deduplication(all_results)
        
        collection_summary = {
            "session_id": session_id,
            "queries_processed": len(search_queries),
            "total_api_calls": total_api_calls,
            "urls_discovered": len(all_results),
            "urls_after_dedup": len(unique_results),
            "query_stats": query_stats,
            "collection_timestamp": datetime.utcnow().isoformat(),
            "urls": unique_results
        }
        
        logger.info(f"URL collection completed: {len(unique_results)} unique URLs for session {session_id}")
        
        return collection_summary
    
    async def _execute_search(
        self, 
        query: str, 
        num_results: int, 
        session_id: str,
        start_index: int = 1
    ) -> SearchResultsSet:
        """Execute a single Google Custom Search API call"""
        
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": min(num_results, 10),  # Google CSE API max is 10 per request
            "start": start_index,
            "lr": f"lang_{self.settings.search_language}",
            "safe": self.settings.search_safe_search
        }
        
        # Apply site filters if configured
        site_filters = self.settings.get_site_filters()
        if site_filters:
            site_restrict = " OR ".join([f"site:{domain}" for domain in site_filters])
            params["q"] = f"{query} ({site_restrict})"
        
        search_time_ms = 0
        start_time = datetime.now(timezone.utc)
        
        try:
            async with self.session.get(self.base_url, params=params) as response:
                search_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                
                if response.status != 200:
                    error_text = await response.text()
                    return SearchResultsSet(
                        query=query,
                        total_results=0,
                        search_time_ms=search_time_ms,
                        results=[],
                        error=f"HTTP {response.status}: {error_text}"
                    )
                
                data = await response.json()
                
                # Parse search results
                search_results = []
                items = data.get("items", [])
                
                for item in items:
                    url = item.get("link", "")
                    domain = urllib.parse.urlparse(url).netloc
                    
                    search_result = SearchResult(
                        title=item.get("title", ""),
                        url=url,
                        snippet=item.get("snippet", ""),
                        display_url=item.get("displayLink", ""),
                        formatted_url=item.get("formattedUrl", ""),
                        domain=domain,
                        search_query=query,
                        metadata={
                            "session_id": session_id,
                            "search_rank": len(search_results) + 1,
                            "search_timestamp": datetime.now(timezone.utc).isoformat(),
                            "api_response_item": item
                        }
                    )
                    
                    search_results.append(search_result)
                
                # Extract pagination info
                next_page = data.get("queries", {}).get("nextPage", [])
                next_start_index = next_page[0].get("startIndex") if next_page else None
                
                total_results = int(data.get("searchInformation", {}).get("totalResults", "0"))
                
                return SearchResultsSet(
                    query=query,
                    total_results=total_results,
                    search_time_ms=search_time_ms,
                    results=search_results,
                    next_start_index=next_start_index
                )
                
        except asyncio.TimeoutError:
            return SearchResultsSet(
                query=query,
                total_results=0,
                search_time_ms=self.settings.url_collection_timeout * 1000,
                results=[],
                error="Search request timed out"
            )
        except Exception as e:
            return SearchResultsSet(
                query=query,
                total_results=0,
                search_time_ms=search_time_ms,
                results=[],
                error=str(e)
            )
    
    def _filter_and_dedupe_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Apply domain filtering and initial deduplication"""
        excluded_domains = self.settings.get_excluded_domains()
        filtered_results = []
        
        for result in results:
            # Skip excluded domains
            if excluded_domains and any(
                result.domain == excluded or result.domain.endswith(f".{excluded}")
                for excluded in excluded_domains
            ):
                logger.debug(f"Excluded URL from domain {result.domain}: {result.url}")
                continue
            
            # Skip if already seen (basic deduplication)
            url_hash = self._generate_url_hash(result.url)
            if url_hash in self._url_cache:
                logger.debug(f"Duplicate URL skipped: {result.url}")
                continue
            
            # Calculate basic relevance score
            result.relevance_score = self._calculate_relevance_score(result, query)
            
            filtered_results.append(result)
            self._url_cache.add(url_hash)
        
        return filtered_results
    
    def _final_deduplication(self, results: List[SearchResult]) -> List[SearchResult]:
        """Final deduplication and sorting"""
        seen_urls = set()
        unique_results = []
        
        # Sort by relevance score (descending)
        sorted_results = sorted(results, key=lambda x: x.relevance_score, reverse=True)
        
        for result in sorted_results:
            url_hash = self._generate_url_hash(result.url)
            if url_hash not in seen_urls:
                unique_results.append(result)
                seen_urls.add(url_hash)
        
        return unique_results
    
    def _generate_url_hash(self, url: str) -> str:
        """Generate hash for URL deduplication"""
        # Normalize URL for consistent hashing
        parsed = urllib.parse.urlparse(url.lower())
        # Include query params for more precise deduplication
        normalized = f"{parsed.netloc}{parsed.path}{parsed.query}"
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _calculate_relevance_score(self, result: SearchResult, query: str) -> float:
        """Calculate basic relevance score for search result"""
        score = 0.5  # Base score
        
        query_terms = query.lower().split()
        if not query_terms:
            return score
            
        title_lower = result.title.lower()
        snippet_lower = result.snippet.lower()
        
        # Title matching
        title_matches = sum(1 for term in query_terms if term in title_lower)
        score += (title_matches / len(query_terms)) * 0.3
        
        # Snippet matching
        snippet_matches = sum(1 for term in query_terms if term in snippet_lower)
        score += (snippet_matches / len(query_terms)) * 0.2
        
        # Domain quality indicators
        if any(indicator in result.domain for indicator in ['edu', 'gov', 'org']):
            score += 0.1
        
        # Penalize very long URLs (likely generated/dynamic)
        if len(result.url) > 100:
            score -= 0.1
        
        return min(1.0, max(0.0, score))

# Global service instance
_search_service: Optional[GoogleCustomSearchService] = None

async def get_google_search_service() -> GoogleCustomSearchService:
    """Get or create global search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = GoogleCustomSearchService()
        await _search_service.initialize()
    return _search_service
