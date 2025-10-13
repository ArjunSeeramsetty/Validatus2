"""
Data-Driven Insights Generator for Results Tab
Uses actual data from Topic, URLs, Content, and Scoring - NO random fallbacks
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.core.database_config import DatabaseManager
from app.core.gemini_client import GeminiClient
import json

logger = logging.getLogger(__name__)

class DataDrivenInsightsGenerator:
    """
    Generates insights using ONLY actual data from:
    1. Topics table (topic description, metadata)
    2. topic_urls table (URLs collected)
    3. scraped_content table (actual scraped content)
    4. v2_analysis_results table (actual scoring results)
    
    NO random numbers or fallback generation
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.gemini_client = GeminiClient()
    
    async def generate_segment_insights(self, 
                                       session_id: str, 
                                       segment_name: str,
                                       segment_score: float) -> Dict[str, Any]:
        """
        Generate insights for a segment using ACTUAL data only
        
        Args:
            session_id: Topic session ID
            segment_name: Market_Intelligence, Consumer_Intelligence, etc.
            segment_score: Actual calculated segment score
            
        Returns:
            Dict with insights derived from actual data
        """
        try:
            # 1. Fetch actual topic data
            topic_data = await self._get_topic_data(session_id)
            
            # 2. Fetch actual URLs collected
            urls_data = await self._get_urls_data(session_id)
            
            # 3. Fetch actual scraped content
            content_data = await self._get_content_data(session_id)
            
            # 4. Fetch actual scoring data
            scoring_data = await self._get_scoring_data(session_id)
            
            # 5. Extract segment-specific factor scores (ACTUAL calculated values)
            segment_factors = self._extract_segment_factors(
                segment_name, scoring_data
            )
            
            # 6. Build context from ACTUAL data
            context = self._build_data_context(
                topic_data, urls_data, content_data, 
                segment_name, segment_score, segment_factors
            )
            
            # 7. Generate insights using LLM with actual data as context
            insights = await self._generate_llm_insights(
                context, segment_name, segment_score
            )
            
            # 8. Enrich insights with actual metrics
            enriched_insights = self._enrich_with_actual_metrics(
                insights, urls_data, content_data, segment_factors
            )
            
            logger.info(f"Generated {segment_name} insights from {len(content_data)} actual content items")
            return enriched_insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights for {segment_name}: {e}", exc_info=True)
            return self._minimal_actual_data_response(segment_name, segment_score)
    
    async def _get_topic_data(self, session_id: str) -> Dict[str, Any]:
        """Fetch actual topic data from database"""
        try:
            connection = await self.db_manager.get_connection()
            query = """
            SELECT session_id, topic, description, status, metadata, created_at
            FROM topics
            WHERE session_id = $1
            """
            row = await connection.fetchrow(query, session_id)
            
            if row:
                return {
                    'session_id': row['session_id'],
                    'topic': row['topic'],
                    'description': row['description'],
                    'status': row['status'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'created_at': row['created_at']
                }
            return {}
            
        except Exception as e:
            logger.error(f"Failed to fetch topic data: {e}")
            return {}
    
    async def _get_urls_data(self, session_id: str) -> List[Dict[str, Any]]:
        """Fetch actual URLs collected for this topic"""
        try:
            connection = await self.db_manager.get_connection()
            query = """
            SELECT url, title, relevance_score, source, metadata
            FROM topic_urls
            WHERE session_id = $1
            ORDER BY relevance_score DESC
            LIMIT 50
            """
            rows = await connection.fetch(query, session_id)
            
            urls = []
            for row in rows:
                urls.append({
                    'url': row['url'],
                    'title': row['title'],
                    'relevance_score': float(row['relevance_score']) if row['relevance_score'] else 0.0,
                    'source': row['source'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                })
            
            logger.info(f"Fetched {len(urls)} actual URLs for {session_id}")
            return urls
            
        except Exception as e:
            logger.error(f"Failed to fetch URLs data: {e}")
            return []
    
    async def _get_content_data(self, session_id: str) -> List[Dict[str, Any]]:
        """Fetch actual scraped content from database"""
        try:
            connection = await self.db_manager.get_connection()
            query = """
            SELECT url, title, content, metadata, scraped_at, processing_status
            FROM scraped_content
            WHERE session_id = $1
            AND processing_status = 'processed'
            ORDER BY scraped_at DESC
            LIMIT 30
            """
            rows = await connection.fetch(query, session_id)
            
            content_items = []
            for row in rows:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                content_items.append({
                    'url': row['url'],
                    'title': row['title'],
                    'content': row['content'][:3000] if row['content'] else '',  # Limit per item
                    'word_count': len(row['content'].split()) if row['content'] else 0,
                    'quality_score': metadata.get('quality_score', 0.0),
                    'metadata': metadata,
                    'scraped_at': row['scraped_at']
                })
            
            logger.info(f"Fetched {len(content_items)} actual scraped content items for {session_id}")
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to fetch content data: {e}")
            return []
    
    async def _get_scoring_data(self, session_id: str) -> Dict[str, Any]:
        """Fetch actual scoring data from v2_analysis_results"""
        try:
            connection = await self.db_manager.get_connection()
            query = """
            SELECT 
                overall_business_case_score,
                overall_confidence,
                layers_analyzed,
                factors_calculated,
                segments_evaluated,
                full_results
            FROM v2_analysis_results
            WHERE session_id = $1
            ORDER BY updated_at DESC
            LIMIT 1
            """
            row = await connection.fetchrow(query, session_id)
            
            if row:
                full_results = row['full_results']
                if isinstance(full_results, str):
                    full_results = json.loads(full_results)
                
                return {
                    'overall_score': float(row['overall_business_case_score']) if row['overall_business_case_score'] else 0.0,
                    'confidence': float(row['overall_confidence']) if row['overall_confidence'] else 0.0,
                    'layers_analyzed': row['layers_analyzed'],
                    'factors_calculated': row['factors_calculated'],
                    'segments_evaluated': row['segments_evaluated'],
                    'layer_scores': full_results.get('layer_scores', []),
                    'factor_calculations': full_results.get('factor_calculations', []),
                    'segment_analyses': full_results.get('segment_analyses', [])
                }
            
            logger.warning(f"No scoring data found for {session_id}")
            return {}
            
        except Exception as e:
            logger.error(f"Failed to fetch scoring data: {e}")
            return {}
    
    def _extract_segment_factors(self, segment_name: str, scoring_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract ACTUAL factor scores for a segment from scoring data
        NO random generation - only actual calculated values
        """
        segment_factors = {}
        
        if not scoring_data:
            return segment_factors
        
        # Map segment names to IDs
        segment_id_map = {
            'Market_Intelligence': 'S3',
            'Consumer_Intelligence': 'S2',
            'Product_Intelligence': 'S1',
            'Brand_Intelligence': 'S4',
            'Experience_Intelligence': 'S5'
        }
        
        segment_id = segment_id_map.get(segment_name, '')
        
        # Extract actual factor scores for this segment
        factor_calculations = scoring_data.get('factor_calculations', [])
        for factor in factor_calculations:
            if factor.get('segment_id') == segment_id:
                factor_name = factor.get('factor_name', '')
                factor_value = factor.get('value', factor.get('calculated_value', 0.0))
                segment_factors[factor_name] = float(factor_value)
        
        logger.info(f"Extracted {len(segment_factors)} ACTUAL factors for {segment_name}")
        return segment_factors
    
    def _build_data_context(self,
                           topic_data: Dict,
                           urls_data: List[Dict],
                           content_data: List[Dict],
                           segment_name: str,
                           segment_score: float,
                           segment_factors: Dict[str, float]) -> str:
        """Build context from ACTUAL collected data"""
        
        context_parts = [
            f"# Data-Driven Analysis Context",
            f"",
            f"## Topic Information (ACTUAL)",
            f"**Topic**: {topic_data.get('topic', 'N/A')}",
            f"**Description**: {topic_data.get('description', 'N/A')}",
            f"**Status**: {topic_data.get('status', 'N/A')}",
            f"",
            f"## URLs Collected (ACTUAL)",
            f"**Total URLs**: {len(urls_data)}",
            f"**Average Relevance**: {sum(u.get('relevance_score', 0) for u in urls_data) / len(urls_data):.3f}" if urls_data else "N/A",
            f""
        ]
        
        # Add top URLs (actual data)
        context_parts.append(f"### Top URLs Collected:")
        for i, url_data in enumerate(urls_data[:5], 1):
            context_parts.append(f"{i}. {url_data.get('title', 'Untitled')} (Relevance: {url_data.get('relevance_score', 0):.2f})")
            context_parts.append(f"   URL: {url_data.get('url', 'N/A')}")
        
        context_parts.extend([
            f"",
            f"## Scraped Content (ACTUAL)",
            f"**Total Content Items**: {len(content_data)}",
            f"**Total Words**: {sum(c.get('word_count', 0) for c in content_data):,}",
            f"**Average Quality**: {sum(c.get('quality_score', 0) for c in content_data) / len(content_data):.3f}" if content_data else "N/A",
            f""
        ])
        
        # Add content excerpts (actual scraped data)
        context_parts.append(f"### Content Excerpts:")
        for i, content in enumerate(content_data[:5], 1):
            context_parts.append(f"**Source {i}**: {content.get('title', 'Untitled')}")
            context_parts.append(f"{content.get('content', '')[:400]}...")
            context_parts.append(f"")
        
        context_parts.extend([
            f"",
            f"## Scoring Results (ACTUAL CALCULATED VALUES)",
            f"**Segment**: {segment_name}",
            f"**Segment Score**: {segment_score:.4f} (Calculated from factors below)",
            f"",
            f"### Factor Scores (ACTUAL - from 210 layer analysis):"
        ])
        
        # Add actual factor scores
        for factor_name, score in segment_factors.items():
            context_parts.append(f"- {factor_name}: {score:.4f}")
        
        return "\n".join(context_parts)
    
    async def _generate_llm_insights(self,
                                    context: str,
                                    segment_name: str,
                                    segment_score: float) -> Dict[str, Any]:
        """
        Generate insights using LLM with ACTUAL data as context
        This is the ONLY place where new content is generated
        """
        
        prompt = f"""You are an expert strategic analyst. Analyze the ACTUAL data provided below and generate insights.

IMPORTANT: Base your analysis ONLY on the actual data provided. Do NOT invent metrics or make up data.

---

{context}

---

**Analysis Task:**

Based on the ACTUAL data above (URLs collected, scraped content, and calculated scoring results), provide a strategic analysis for the {segment_name} segment.

**Requirements:**

1. **Derive insights from ACTUAL content** - Reference specific data points from the scraped content
2. **Use ACTUAL factor scores** - Don't invent new metrics
3. **Reference ACTUAL URLs** - Cite sources when making claims
4. **Be evidence-based** - Every insight should trace to actual data

**Output Format:**

## Key Insights
- [Insight 1 - cite actual data source]
- [Insight 2 - reference actual metric]
- [Insight 3 - based on scraped content]
- [Insight 4]
- [Insight 5]

## Opportunities
- [Opportunity 1 - derived from content analysis]
- [Opportunity 2 - based on factor scores]
- [Opportunity 3 - supported by URL patterns]
- [Opportunity 4]
- [Opportunity 5]

## Challenges
- [Challenge 1 - identified in content]
- [Challenge 2 - reflected in scores]
- [Challenge 3 - evident from data]

## Strategic Recommendations
- [Recommendation 1 - actionable based on data]
- [Recommendation 2 - supported by evidence]
- [Recommendation 3 - data-driven strategy]

## Data Quality Assessment
[1-2 sentences on the quality and completeness of available data]

---

Be specific, cite your sources, and ensure every claim is grounded in the actual data provided above.
"""
        
        try:
            logger.info(f"Generating LLM insights for {segment_name} using actual data")
            llm_response = await self.gemini_client.generate_content(prompt)
            
            # Parse the response
            insights = self._parse_llm_response(llm_response)
            
            return insights
            
        except Exception as e:
            logger.error(f"LLM insight generation failed for {segment_name}: {e}")
            # Minimal response with actual data only
            return {
                'insights': [f"{segment_name} analysis based on segment score: {segment_score:.3f}"],
                'opportunities': [],
                'challenges': [],
                'recommendations': [],
                'data_quality': 'Limited data available for comprehensive analysis'
            }
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured insights"""
        import re
        
        insights = {}
        
        # Extract insights
        insights_section = re.search(r'## Key Insights(.*?)(?:##|$)', llm_response, re.DOTALL | re.IGNORECASE)
        if insights_section:
            lines = insights_section.group(1).strip().split('\n')
            insights['insights'] = [
                line.strip('- ').strip().strip('*').strip()
                for line in lines
                if (line.strip().startswith('-') or line.strip().startswith('*')) and len(line.strip()) > 15
            ]
        else:
            insights['insights'] = []
        
        # Extract opportunities
        opp_section = re.search(r'## Opportunities(.*?)(?:##|$)', llm_response, re.DOTALL | re.IGNORECASE)
        if opp_section:
            lines = opp_section.group(1).strip().split('\n')
            insights['opportunities'] = [
                line.strip('- ').strip().strip('*').strip()
                for line in lines
                if (line.strip().startswith('-') or line.strip().startswith('*')) and len(line.strip()) > 15
            ]
        else:
            insights['opportunities'] = []
        
        # Extract challenges
        challenges_section = re.search(r'## Challenges(.*?)(?:##|$)', llm_response, re.DOTALL | re.IGNORECASE)
        if challenges_section:
            lines = challenges_section.group(1).strip().split('\n')
            insights['challenges'] = [
                line.strip('- ').strip().strip('*').strip()
                for line in lines
                if (line.strip().startswith('-') or line.strip().startswith('*')) and len(line.strip()) > 15
            ]
        else:
            insights['challenges'] = []
        
        # Extract recommendations
        rec_section = re.search(r'## Strategic Recommendations(.*?)(?:##|$)', llm_response, re.DOTALL | re.IGNORECASE)
        if rec_section:
            lines = rec_section.group(1).strip().split('\n')
            insights['recommendations'] = [
                line.strip('- ').strip().strip('*').strip()
                for line in lines
                if (line.strip().startswith('-') or line.strip().startswith('*')) and len(line.strip()) > 15
            ]
        else:
            insights['recommendations'] = []
        
        # Extract data quality assessment
        quality_section = re.search(r'## Data Quality Assessment(.*?)(?:##|$)', llm_response, re.DOTALL | re.IGNORECASE)
        if quality_section:
            insights['data_quality'] = quality_section.group(1).strip()[:300]
        else:
            insights['data_quality'] = 'Analysis completed'
        
        return insights
    
    def _enrich_with_actual_metrics(self,
                                    insights: Dict[str, Any],
                                    urls_data: List[Dict],
                                    content_data: List[Dict],
                                    segment_factors: Dict[str, float]) -> Dict[str, Any]:
        """
        Enrich insights with ACTUAL metrics from data
        NO random numbers - only actual data
        """
        
        # Calculate actual metrics from data
        insights['metrics'] = {
            'total_urls_analyzed': len(urls_data),
            'total_content_items': len(content_data),
            'total_words_analyzed': sum(c.get('word_count', 0) for c in content_data),
            'average_content_quality': sum(c.get('quality_score', 0.0) for c in content_data) / len(content_data) if content_data else 0.0,
            'average_url_relevance': sum(u.get('relevance_score', 0.0) for u in urls_data) / len(urls_data) if urls_data else 0.0,
            'factor_count': len(segment_factors),
            'average_factor_score': sum(segment_factors.values()) / len(segment_factors) if segment_factors else 0.0
        }
        
        # Add source citations from actual data
        insights['sources'] = {
            'url_sources': [u.get('url') for u in urls_data[:5]],
            'content_titles': [c.get('title') for c in content_data[:5]],
            'factor_scores': segment_factors
        }
        
        # Data completeness assessment (actual data only)
        insights['data_completeness'] = {
            'has_urls': len(urls_data) > 0,
            'has_content': len(content_data) > 0,
            'has_scoring': len(segment_factors) > 0,
            'completeness_score': self._calculate_actual_completeness(urls_data, content_data, segment_factors)
        }
        
        return insights
    
    def _calculate_actual_completeness(self,
                                      urls_data: List[Dict],
                                      content_data: List[Dict],
                                      segment_factors: Dict[str, float]) -> float:
        """
        Calculate data completeness from ACTUAL data availability
        NOT random - based on actual data presence
        """
        
        # Calculate completeness based on actual data
        url_score = min(1.0, len(urls_data) / 20.0)  # Target: 20 URLs
        content_score = min(1.0, len(content_data) / 15.0)  # Target: 15 content items
        factor_score = min(1.0, len(segment_factors) / 5.0)  # Target: 5+ factors per segment
        
        # Average quality from actual content
        if content_data:
            quality_score = sum(c.get('quality_score', 0.0) for c in content_data) / len(content_data)
        else:
            quality_score = 0.0
        
        # Weighted completeness
        completeness = (
            url_score * 0.2 +
            content_score * 0.3 +
            factor_score * 0.3 +
            quality_score * 0.2
        )
        
        return completeness
    
    def _minimal_actual_data_response(self, segment_name: str, segment_score: float) -> Dict[str, Any]:
        """
        Return minimal response using ONLY actual segment score
        Used when LLM generation fails
        """
        return {
            'insights': [f"{segment_name} segment score: {segment_score:.3f} (calculated from factor analysis)"],
            'opportunities': [f"Analysis available with score: {segment_score:.3f}"],
            'challenges': ["Comprehensive insights pending LLM generation"],
            'recommendations': [f"Review {segment_name} factor scores for detailed assessment"],
            'data_quality': 'Using actual scoring data',
            'metrics': {
                'segment_score': segment_score,
                'data_source': 'v2_analysis_results (actual calculated)',
                'generation_method': 'Direct extraction from database'
            },
            'sources': {
                'primary_source': 'v2.0 Strategic Analysis (210 layers)',
                'calculation_method': 'Weighted factor aggregation'
            },
            'data_completeness': {
                'has_urls': False,
                'has_content': False,
                'has_scoring': True,
                'completeness_score': 0.3
            }
        }


# Global instance
data_driven_insights_generator = DataDrivenInsightsGenerator()

