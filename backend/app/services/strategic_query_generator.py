"""
Strategic Query Generator for URL Collection
Generates search queries based on Segment + Factor + Layer framework
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class StrategicQueryGenerator:
    """
    Generates comprehensive search queries for strategic analysis based on:
    - SEGMENTS: CONSUMER, MARKET, PRODUCT, BRAND, EXPERIENCE
    - FACTORS: F1-F28 strategic factors
    - LAYERS: Market, Competitive, Financial, etc.
    """
    
    # Strategic Segments
    SEGMENTS = ["CONSUMER", "MARKET", "PRODUCT", "BRAND", "EXPERIENCE"]
    
    # Key Factor Categories
    FACTOR_CATEGORIES = {
        "market_attractiveness": ["market size", "market growth", "market trends"],
        "competitive_position": ["competitive landscape", "market share", "competitors"],
        "customer_insights": ["customer needs", "customer behavior", "customer preferences"],
        "product_value": ["product features", "product benefits", "product innovation"],
        "brand_strength": ["brand awareness", "brand perception", "brand positioning"],
        "financial_performance": ["revenue", "profitability", "financial metrics"],
        "growth_potential": ["growth opportunities", "expansion", "market potential"]
    }
    
    # Strategic Layers
    LAYERS = {
        "market_layer": ["market dynamics", "industry analysis", "market conditions"],
        "competitive_layer": ["competitive analysis", "competitor strategies", "market positioning"],
        "financial_layer": ["financial analysis", "cost structure", "pricing strategy"],
        "operational_layer": ["operations", "supply chain", "distribution"],
        "innovation_layer": ["innovation", "R&D", "technology trends"]
    }
    
    def generate_queries(
        self,
        topic: str,
        description: str = "",
        user_queries: List[str] = None,
        include_segments: bool = True,
        include_factors: bool = True,
        include_layers: bool = True,
        max_queries: int = 50
    ) -> List[str]:
        """
        Generate comprehensive search queries combining user queries with strategic framework
        
        Args:
            topic: Main topic/subject for analysis
            description: Topic description for context and relevance
            user_queries: User-provided search queries
            include_segments: Include segment-based queries
            include_factors: Include factor-based queries
            include_layers: Include layer-based queries
            max_queries: Maximum number of queries to generate
            
        Returns:
            List of unique search queries
        """
        all_queries = []
        
        # Extract key terms from description for enhanced relevance
        context_terms = self._extract_context_terms(description) if description else []
        
        # 1. Add user-provided queries (highest priority)
        if user_queries:
            all_queries.extend(user_queries)
            logger.info(f"Added {len(user_queries)} user-provided queries")
        
        # 1b. Add topic + description combinations for better context
        if description and len(description) > 10:
            all_queries.append(f"{topic} {description[:100]}")  # Truncate long descriptions
            logger.info(f"Added topic+description query for enhanced context")
        
        # 2. Generate Segment-based queries
        if include_segments:
            segment_queries = self._generate_segment_queries(topic, context_terms)
            all_queries.extend(segment_queries)
            logger.info(f"Generated {len(segment_queries)} segment-based queries")
        
        # 3. Generate Factor-based queries
        if include_factors:
            factor_queries = self._generate_factor_queries(topic, context_terms)
            all_queries.extend(factor_queries)
            logger.info(f"Generated {len(factor_queries)} factor-based queries")
        
        # 4. Generate Layer-based queries
        if include_layers:
            layer_queries = self._generate_layer_queries(topic, context_terms)
            all_queries.extend(layer_queries)
            logger.info(f"Generated {len(layer_queries)} layer-based queries")
        
        # 5. Generate Combined queries (Segment + Factor + Topic)
        combined_queries = self._generate_combined_queries(topic, context_terms)
        all_queries.extend(combined_queries)
        logger.info(f"Generated {len(combined_queries)} combined queries")
        
        # Deduplicate and limit
        unique_queries = list(dict.fromkeys(all_queries))  # Preserve order
        
        if len(unique_queries) > max_queries:
            unique_queries = unique_queries[:max_queries]
            logger.info(f"Limited queries to {max_queries} (from {len(all_queries)} total)")
        
        logger.info(f"✅ Generated {len(unique_queries)} unique search queries for topic: '{topic}'")
        return unique_queries
    
    def _generate_segment_queries(self, topic: str, context_terms: List[str] = None) -> List[str]:
        """Generate queries based on strategic segments"""
        queries = []
        
        for segment in self.SEGMENTS:
            # Basic segment queries
            queries.append(f"{topic} {segment.lower()} analysis")
            queries.append(f"{topic} {segment.lower()} insights")
            queries.append(f"{topic} {segment.lower()} strategy")
            
            # Add context-enhanced queries if available
            if context_terms and len(context_terms) > 0:
                # Use first context term for most relevant query
                queries.append(f"{topic} {context_terms[0]} {segment.lower()}")
        
        return queries
    
    def _generate_factor_queries(self, topic: str, context_terms: List[str] = None) -> List[str]:
        """Generate queries based on strategic factors"""
        queries = []
        
        for factor_category, factor_terms in self.FACTOR_CATEGORIES.items():
            for term in factor_terms:
                queries.append(f"{topic} {term}")
        
        return queries
    
    def _generate_layer_queries(self, topic: str, context_terms: List[str] = None) -> List[str]:
        """Generate queries based on strategic layers"""
        queries = []
        
        for layer_name, layer_terms in self.LAYERS.items():
            for term in layer_terms:
                queries.append(f"{topic} {term}")
        
        return queries
    
    def _generate_combined_queries(self, topic: str, context_terms: List[str] = None) -> List[str]:
        """Generate combined queries (Segment + Factor combinations)"""
        queries = []
        
        # High-value combinations
        combinations = [
            ("CONSUMER", "customer needs"),
            ("CONSUMER", "customer behavior"),
            ("MARKET", "market size"),
            ("MARKET", "market growth"),
            ("MARKET", "competitive landscape"),
            ("PRODUCT", "product features"),
            ("PRODUCT", "product innovation"),
            ("BRAND", "brand awareness"),
            ("BRAND", "brand positioning"),
            ("EXPERIENCE", "customer experience")
        ]
        
        for segment, factor in combinations:
            queries.append(f"{topic} {segment.lower()} {factor}")
        
        return queries
    
    def _extract_context_terms(self, description: str) -> List[str]:
        """Extract key terms from topic description for enhanced query relevance"""
        # Simple keyword extraction (can be enhanced with NLP later)
        import re
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Extract words (alphanumeric, 3+ chars)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', description.lower())
        
        # Filter out stop words
        context_terms = [word for word in words if word not in stop_words]
        
        # Return top 5 most relevant terms (unique)
        return list(dict.fromkeys(context_terms))[:5]


# Singleton instance
_query_generator: StrategicQueryGenerator = None

def get_query_generator() -> StrategicQueryGenerator:
    """Get or create strategic query generator singleton"""
    global _query_generator
    if _query_generator is None:
        _query_generator = StrategicQueryGenerator()
    return _query_generator

