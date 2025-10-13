"""
Results Analysis Engine
Generates comprehensive analysis across Market, Consumer, Product, Brand, and Experience dimensions
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import asyncio

from app.models.analysis_results import (
    CompleteAnalysisResult,
    MarketAnalysisData,
    ConsumerAnalysisData,
    ProductAnalysisData,
    BrandAnalysisData,
    ExperienceAnalysisData
)
from app.core.database_config import DatabaseManager
from app.core.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class ResultsAnalysisEngine:
    """Engine for generating comprehensive results analysis"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.gemini_client = GeminiClient()
    
    async def generate_complete_analysis(self, session_id: str) -> CompleteAnalysisResult:
        """
        Fetch and format comprehensive analysis results from v2.0 Scoring
        NOTE: This fetches EXISTING scored results, not generating new analysis
        """
        
        logger.info(f"Fetching scored analysis results for session {session_id}")
        
        try:
            # Get topic information
            topic_info = await self._get_topic_info(session_id)
            
            # Fetch existing v2.0 analysis results from Scoring tab
            v2_results = await self._get_v2_analysis_results(session_id)
            
            if not v2_results:
                logger.warning(f"No v2.0 analysis results found for {session_id}. Topic may not be scored yet.")
                # Return empty structure - frontend will show "no data" message
                return CompleteAnalysisResult(
                    session_id=session_id,
                    topic_name=topic_info.get('topic', 'Unknown'),
                    analysis_timestamp=datetime.utcnow(),
                    business_case={},
                    market=MarketAnalysisData(),
                    consumer=ConsumerAnalysisData(),
                    product=ProductAnalysisData(),
                    brand=BrandAnalysisData(),
                    experience=ExperienceAnalysisData(),
                    confidence_scores={}
                )
            
            # Transform v2.0 results into Results tab format
            market_analysis = await self._transform_to_market_analysis(v2_results)
            consumer_analysis = await self._transform_to_consumer_analysis(v2_results)
            product_analysis = await self._transform_to_product_analysis(v2_results)
            brand_analysis = await self._transform_to_brand_analysis(v2_results)
            experience_analysis = await self._transform_to_experience_analysis(v2_results)
            
            # Extract business case from full results
            business_case = v2_results.get('full_results', {})
            
            # Extract confidence scores from v2 results
            confidence_scores = self._extract_confidence_scores(v2_results)
            
            return CompleteAnalysisResult(
                session_id=session_id,
                topic_name=topic_info.get('topic', 'Unknown'),
                analysis_timestamp=v2_results.get('updated_at', datetime.utcnow()),
                business_case=business_case,
                market=market_analysis,
                consumer=consumer_analysis,
                product=product_analysis,
                brand=brand_analysis,
                experience=experience_analysis,
                confidence_scores=confidence_scores
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch analysis results for {session_id}: {e}", exc_info=True)
            raise
    
    async def _get_topic_info(self, session_id: str) -> Dict[str, Any]:
        """Get topic information from database"""
        try:
            connection = await self.db_manager.get_connection()
            query = "SELECT topic, description, status FROM topics WHERE session_id = $1"
            row = await connection.fetchrow(query, session_id)
            
            if row:
                return dict(row)
            return {"topic": "Unknown", "description": "", "status": "active"}
        except Exception as e:
            logger.error(f"Failed to get topic info for {session_id}: {e}")
            return {"topic": "Unknown", "description": "", "status": "active"}
    
    async def _get_content_data(self, session_id: str) -> List[Dict[str, Any]]:
        """Get scraped content for analysis"""
        try:
            connection = await self.db_manager.get_connection()
            query = """
            SELECT url, title, content, metadata
            FROM scraped_content
            WHERE session_id = $1
            AND processing_status = 'completed'
            AND LENGTH(TRIM(COALESCE(content, ''))) > 100
            ORDER BY scraped_at DESC
            LIMIT 50
            """
            rows = await connection.fetch(query, session_id)
            
            content_list = []
            for row in rows:
                content_list.append({
                    'url': row['url'],
                    'title': row['title'],
                    'content': row['content'],
                    'metadata': row['metadata'] if row['metadata'] else {}
                })
            
            logger.info(f"Retrieved {len(content_list)} content items for analysis")
            return content_list
            
        except Exception as e:
            logger.error(f"Failed to get content data for {session_id}: {e}")
            return []
    
    async def _get_business_case(self, session_id: str) -> Dict[str, Any]:
        """Get existing business case analysis if available"""
        try:
            connection = await self.db_manager.get_connection()
            
            # Check v2_analysis_results first
            query = "SELECT full_results FROM v2_analysis_results WHERE session_id = $1 LIMIT 1"
            row = await connection.fetchrow(query, session_id)
            
            if row and row['full_results']:
                full_results = row['full_results']
                if isinstance(full_results, str):
                    full_results = json.loads(full_results)
                return full_results
            
            return {}
        except Exception as e:
            logger.error(f"Failed to get business case for {session_id}: {e}")
            return {}
    
    async def _analyze_market_dimension(
        self,
        session_id: str,
        topic_info: Dict[str, Any],
        content_data: List[Dict[str, Any]]
    ) -> MarketAnalysisData:
        """Analyze market dimension using AI"""
        
        logger.info(f"Analyzing market dimension for {session_id}")
        
        if not content_data:
            logger.warning("No content data available for market analysis")
            return MarketAnalysisData()
        
        try:
            # Prepare market-focused analysis prompt
            content_summary = self._prepare_content_summary(content_data, max_items=10)
            
            prompt = f"""
You are a market analysis expert. Analyze the following market research content for: {topic_info.get('topic')}

Content Summary:
{content_summary}

Provide a comprehensive market analysis in the following JSON format:
{{
    "competitor_analysis": {{
        "Competitor 1": {{"description": "brief description", "market_share": 0.25}},
        "Competitor 2": {{"description": "brief description", "market_share": 0.18}}
    }},
    "opportunities": [
        "Opportunity 1: specific market opportunity",
        "Opportunity 2: another market opportunity",
        "Opportunity 3: growth opportunity"
    ],
    "opportunities_rationale": "Why these opportunities exist in the market",
    "market_share": {{
        "Segment A": 0.35,
        "Segment B": 0.25,
        "Segment C": 0.40
    }},
    "pricing_switching": {{
        "price_range": "Typical price range",
        "switching_costs": "High/Medium/Low",
        "insights": ["Key pricing insight 1", "Key pricing insight 2"]
    }},
    "regulation_tariffs": {{
        "key_regulations": ["Regulation 1", "Regulation 2"],
        "details": ["Detail 1", "Detail 2"]
    }},
    "growth_demand": {{
        "market_size": "Current market size estimate",
        "growth_rate": "CAGR percentage",
        "demand_drivers": ["Driver 1", "Driver 2", "Driver 3"]
    }},
    "market_fit": {{
        "overall_score": 0.75,
        "adoption_rate": 0.68,
        "market_readiness": 0.82
    }}
}}

Focus on:
1. Identifying key competitors and their market positions
2. Uncovering market opportunities and growth potential
3. Understanding pricing dynamics and switching costs
4. Regulatory environment and barriers to entry
5. Market size, growth trends, and demand drivers

Return ONLY valid JSON without any additional text or markdown formatting.
"""
            
            response = await self.gemini_client.generate_content(prompt, timeout=60)
            
            if response:
                # Clean response and parse JSON
                cleaned_response = response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                analysis_data = json.loads(cleaned_response)
                return MarketAnalysisData(**analysis_data)
            
            return MarketAnalysisData()
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse market analysis JSON: {e}")
            logger.error(f"Response was: {response[:500] if response else 'None'}")
            return MarketAnalysisData()
        except Exception as e:
            logger.error(f"Market analysis failed: {e}", exc_info=True)
            return MarketAnalysisData()
    
    async def _analyze_consumer_dimension(
        self,
        session_id: str,
        topic_info: Dict[str, Any],
        content_data: List[Dict[str, Any]]
    ) -> ConsumerAnalysisData:
        """Analyze consumer dimension using AI"""
        
        logger.info(f"Analyzing consumer dimension for {session_id}")
        
        if not content_data:
            return ConsumerAnalysisData()
        
        try:
            content_summary = self._prepare_content_summary(content_data, max_items=10)
            
            prompt = f"""
You are a consumer behavior expert. Analyze the following market research content for: {topic_info.get('topic')}

Content Summary:
{content_summary}

Provide a comprehensive consumer analysis in the following JSON format:
{{
    "recommendations": [
        {{"type": "Strategic recommendation", "timeline": "90 days", "description": "Detailed recommendation"}},
        {{"type": "Tactical action", "timeline": "30 days", "description": "Another recommendation"}}
    ],
    "challenges": [
        "Key consumer challenge 1",
        "Key consumer challenge 2",
        "Key consumer challenge 3"
    ],
    "top_motivators": [
        "Primary consumer motivator",
        "Secondary motivator",
        "Tertiary motivator"
    ],
    "relevant_personas": [
        {{"name": "Persona Name", "age": 45, "description": "Detailed persona description"}},
        {{"name": "Another Persona", "age": 35, "description": "Another persona description"}}
    ],
    "target_audience": {{
        "primary_segment": "Description of primary target",
        "secondary_segment": "Description of secondary target",
        "segments": {{
            "Early Adopters": "Segment characteristics",
            "Price Sensitive": "Segment characteristics"
        }}
    }},
    "consumer_fit": {{
        "overall_score": 0.81,
        "price_sensitivity": 0.65,
        "adoption_likelihood": 0.88
    }},
    "additional_recommendations": [
        "Additional insight 1",
        "Additional insight 2"
    ]
}}

Focus on:
1. Consumer motivations and buying triggers
2. Key challenges and pain points
3. Relevant customer personas
4. Target audience definition
5. Actionable recommendations

Return ONLY valid JSON without any additional text or markdown formatting.
"""
            
            response = await self.gemini_client.generate_content(prompt, timeout=60)
            
            if response:
                cleaned_response = self._clean_json_response(response)
                analysis_data = json.loads(cleaned_response)
                return ConsumerAnalysisData(**analysis_data)
            
            return ConsumerAnalysisData()
            
        except Exception as e:
            logger.error(f"Consumer analysis failed: {e}", exc_info=True)
            return ConsumerAnalysisData()
    
    async def _analyze_product_dimension(
        self,
        session_id: str,
        topic_info: Dict[str, Any],
        content_data: List[Dict[str, Any]]
    ) -> ProductAnalysisData:
        """Analyze product dimension using AI"""
        
        logger.info(f"Analyzing product dimension for {session_id}")
        
        if not content_data:
            return ProductAnalysisData()
        
        try:
            content_summary = self._prepare_content_summary(content_data, max_items=10)
            
            prompt = f"""
You are a product strategy expert. Analyze the following content for: {topic_info.get('topic')}

Content Summary:
{content_summary}

Provide a product analysis in the following JSON format:
{{
    "product_features": [
        {{"name": "Feature 1", "description": "Feature description", "importance": 0.9, "category": "Core"}},
        {{"name": "Feature 2", "description": "Feature description", "importance": 0.7, "category": "Premium"}}
    ],
    "competitive_positioning": {{
        "differentiation": "Key differentiation factors",
        "unique_value": "Unique value proposition",
        "competitive_advantages": "Main competitive advantages"
    }},
    "innovation_opportunities": [
        "Innovation opportunity 1",
        "Innovation opportunity 2",
        "Innovation opportunity 3"
    ],
    "technical_specifications": {{
        "key_specs": "Important technical specifications",
        "quality_standards": "Quality and standards"
    }},
    "product_roadmap": [
        {{"phase": "Near-term", "features": "Features to add", "timeline": "Q1 2025"}},
        {{"phase": "Long-term", "features": "Future features", "timeline": "2025-2026"}}
    ],
    "product_fit": {{
        "overall_score": 0.72,
        "feature_completeness": 0.78,
        "market_readiness": 0.68
    }}
}}

Return ONLY valid JSON without any additional text or markdown formatting.
"""
            
            response = await self.gemini_client.generate_content(prompt, timeout=60)
            
            if response:
                cleaned_response = self._clean_json_response(response)
                analysis_data = json.loads(cleaned_response)
                return ProductAnalysisData(**analysis_data)
            
            return ProductAnalysisData()
            
        except Exception as e:
            logger.error(f"Product analysis failed: {e}", exc_info=True)
            return ProductAnalysisData()
    
    async def _analyze_brand_dimension(
        self,
        session_id: str,
        topic_info: Dict[str, Any],
        content_data: List[Dict[str, Any]]
    ) -> BrandAnalysisData:
        """Analyze brand dimension using AI"""
        
        logger.info(f"Analyzing brand dimension for {session_id}")
        
        if not content_data:
            return BrandAnalysisData()
        
        try:
            content_summary = self._prepare_content_summary(content_data, max_items=10)
            
            prompt = f"""
You are a brand strategy expert. Analyze the following content for: {topic_info.get('topic')}

Content Summary:
{content_summary}

Provide a brand analysis in the following JSON format:
{{
    "brand_positioning": {{
        "Premium Quality": 0.85,
        "Innovation": 0.72,
        "Reliability": 0.90,
        "Value": 0.65
    }},
    "brand_perception": {{
        "Trust": 0.82,
        "Quality": 0.88,
        "Innovation": 0.75,
        "Customer Service": 0.79
    }},
    "competitor_brands": [
        {{"name": "Competitor Brand 1", "positioning": "Their positioning", "strength": 0.75}},
        {{"name": "Competitor Brand 2", "positioning": "Their positioning", "strength": 0.68}}
    ],
    "brand_opportunities": [
        "Brand opportunity 1",
        "Brand opportunity 2",
        "Brand opportunity 3"
    ],
    "messaging_strategy": {{
        "key_messages": ["Message 1", "Message 2"],
        "tone": "Brand tone description",
        "differentiation": "How to differentiate in messaging"
    }},
    "brand_fit": {{
        "overall_score": 0.76,
        "market_perception": 0.80,
        "differentiation": 0.72
    }}
}}

Return ONLY valid JSON without any additional text or markdown formatting.
"""
            
            response = await self.gemini_client.generate_content(prompt, timeout=60)
            
            if response:
                cleaned_response = self._clean_json_response(response)
                analysis_data = json.loads(cleaned_response)
                return BrandAnalysisData(**analysis_data)
            
            return BrandAnalysisData()
            
        except Exception as e:
            logger.error(f"Brand analysis failed: {e}", exc_info=True)
            return BrandAnalysisData()
    
    async def _analyze_experience_dimension(
        self,
        session_id: str,
        topic_info: Dict[str, Any],
        content_data: List[Dict[str, Any]]
    ) -> ExperienceAnalysisData:
        """Analyze experience dimension using AI"""
        
        logger.info(f"Analyzing experience dimension for {session_id}")
        
        if not content_data:
            return ExperienceAnalysisData()
        
        try:
            content_summary = self._prepare_content_summary(content_data, max_items=10)
            
            prompt = f"""
You are a customer experience expert. Analyze the following content for: {topic_info.get('topic')}

Content Summary:
{content_summary}

Provide an experience analysis in the following JSON format:
{{
    "user_journey": [
        {{"stage": "Awareness", "phase": "Discovery", "description": "How customers discover", "pain_points": ["Pain 1", "Pain 2"], "opportunities": ["Opportunity 1"]}},
        {{"stage": "Consideration", "phase": "Evaluation", "description": "Evaluation process", "pain_points": ["Pain 1"], "opportunities": ["Opportunity 1"]}}
    ],
    "touchpoints": [
        {{"name": "Website", "importance": 0.9, "current_quality": 0.7, "improvement_potential": 0.85}},
        {{"name": "Sales Process", "importance": 0.85, "current_quality": 0.65, "improvement_potential": 0.80}}
    ],
    "pain_points": [
        "Major customer pain point 1",
        "Major customer pain point 2",
        "Major customer pain point 3"
    ],
    "experience_metrics": {{
        "Ease of Purchase": 0.72,
        "Information Quality": 0.81,
        "Post-Purchase Support": 0.68,
        "Overall Satisfaction": 0.75
    }},
    "improvement_recommendations": [
        "Recommendation 1 for improving experience",
        "Recommendation 2 for improving experience",
        "Recommendation 3 for improving experience"
    ],
    "experience_fit": {{
        "overall_score": 0.74,
        "journey_optimization": 0.70,
        "touchpoint_effectiveness": 0.78
    }}
}}

Return ONLY valid JSON without any additional text or markdown formatting.
"""
            
            response = await self.gemini_client.generate_content(prompt, timeout=60)
            
            if response:
                cleaned_response = self._clean_json_response(response)
                analysis_data = json.loads(cleaned_response)
                return ExperienceAnalysisData(**analysis_data)
            
            return ExperienceAnalysisData()
            
        except Exception as e:
            logger.error(f"Experience analysis failed: {e}", exc_info=True)
            return ExperienceAnalysisData()
    
    def _prepare_content_summary(self, content_data: List[Dict[str, Any]], max_items: int = 10) -> str:
        """Prepare a summary of content for AI analysis"""
        summary_parts = []
        
        for i, item in enumerate(content_data[:max_items]):
            title = item.get('title', 'Untitled')
            content = item.get('content', '')
            
            # Truncate content to first 500 characters
            content_preview = content[:500] if content else ''
            
            summary_parts.append(f"Source {i+1} - {title}:\n{content_preview}...")
        
        return "\n\n".join(summary_parts)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean AI response to extract valid JSON"""
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
    
    def _calculate_confidence_scores(
        self,
        content_data: List[Dict[str, Any]],
        analysis_results: List[Any]
    ) -> Dict[str, float]:
        """Calculate confidence scores for each analysis dimension"""
        
        # Base confidence on content availability
        content_count = len(content_data)
        base_confidence = min(content_count / 20.0, 1.0)  # Max at 20 items
        
        confidence = {
            "market": base_confidence * 0.9 if not isinstance(analysis_results[0], Exception) else 0.3,
            "consumer": base_confidence * 0.85 if not isinstance(analysis_results[1], Exception) else 0.3,
            "product": base_confidence * 0.80 if not isinstance(analysis_results[2], Exception) else 0.3,
            "brand": base_confidence * 0.75 if not isinstance(analysis_results[3], Exception) else 0.3,
            "experience": base_confidence * 0.70 if not isinstance(analysis_results[4], Exception) else 0.3,
        }
        
        return confidence
    
    # ============================================================================
    # NEW METHODS: Fetch and transform v2.0 Scoring results
    # ============================================================================
    
    async def _get_v2_analysis_results(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Fetch existing v2.0 analysis results from Scoring tab"""
        try:
            connection = await self.db_manager.get_connection()
            query = """
            SELECT 
                session_id,
                analysis_type,
                overall_business_case_score,
                overall_confidence,
                layers_analyzed,
                factors_calculated,
                segments_evaluated,
                analysis_summary,
                full_results,
                created_at,
                updated_at
            FROM v2_analysis_results
            WHERE session_id = $1
            ORDER BY updated_at DESC
            LIMIT 1
            """
            row = await connection.fetchrow(query, session_id)
            
            if row:
                result = dict(row)
                
                # Parse JSON fields if they're strings
                for field in ['analysis_summary', 'full_results']:
                    if result.get(field) and isinstance(result[field], str):
                        result[field] = json.loads(result[field])
                
                # Extract segment_scores, factor_scores, layer_scores from full_results
                full_results = result.get('full_results', {})
                if full_results:
                    # Convert list structures to dictionaries for easier access
                    # segment_analyses is a list, convert to dict by segment name
                    segment_analyses = full_results.get('segment_analyses', [])
                    result['segment_scores'] = {}
                    for seg in segment_analyses:
                        seg_name = seg.get('segment_name', seg.get('segment_id', ''))
                        result['segment_scores'][seg_name] = {
                            'score': seg.get('overall_segment_score', 0.0),
                            'confidence': seg.get('confidence', 0.8),
                            'insights': seg.get('key_insights', []),
                            'opportunities': seg.get('opportunities', []),
                            'recommendations': seg.get('recommendations', [])
                        }
                    
                    # factor_calculations is a list, convert to dict by factor name
                    factor_calculations = full_results.get('factor_calculations', [])
                    result['factor_scores'] = {}
                    for factor in factor_calculations:
                        factor_name = factor.get('factor_name', factor.get('factor_id', ''))
                        result['factor_scores'][factor_name] = factor.get('calculated_value', 0.0)
                    
                    # layer_scores is a list, convert to dict by layer ID
                    layer_scores = full_results.get('layer_scores', [])
                    result['layer_scores'] = {}
                    for layer in layer_scores:
                        layer_id = layer.get('layer_id', '')
                        result['layer_scores'][layer_id] = {
                            'score': layer.get('score', 0.0),
                            'confidence': layer.get('confidence', 0.0),
                            'insights': layer.get('key_insights', [])
                        }
                    
                    # Also add overall_score for compatibility
                    result['overall_score'] = result.get('overall_business_case_score', 0.0)
                
                logger.info(f"Found v2.0 analysis results for {session_id}")
                logger.info(f"  Analysis type: {result.get('analysis_type')}")
                logger.info(f"  Layers analyzed: {result.get('layers_analyzed')}")
                logger.info(f"  Overall score: {result.get('overall_business_case_score')}")
                return result
            
            logger.warning(f"No v2.0 analysis results found for {session_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch v2.0 analysis results for {session_id}: {e}", exc_info=True)
            return None
    
    async def _transform_to_market_analysis(self, v2_results: Dict[str, Any]) -> MarketAnalysisData:
        """Transform v2.0 scoring results into Market Analysis format"""
        try:
            full_results = v2_results.get('full_results', {})
            segment_scores = v2_results.get('segment_scores', {})
            factor_scores = v2_results.get('factor_scores', {})
            
            # Extract market-related segment (Market Intelligence = S3)
            market_segment = segment_scores.get('Market Intelligence', segment_scores.get('S3', {}))
            
            # Get market-specific insights from segment
            market_insights = market_segment.get('insights', [])
            market_opportunities = market_segment.get('opportunities', [])
            market_recommendations = market_segment.get('recommendations', [])
            
            # Build competitor analysis from insights
            competitor_analysis = {}
            for insight in market_insights[:5]:  # Top 5 insights
                if 'competitor' in insight.lower() or 'competition' in insight.lower():
                    competitor_analysis[f"Insight {len(competitor_analysis)+1}"] = {
                        "description": insight,
                        "market_share": 0.15  # Placeholder
                    }
            
            # Build market share from factor data
            market_share = {
                "Current Market": factor_scores.get('Market Size', 0.0),
                "Addressable Market": factor_scores.get('Growth Potential', 0.0),
                "Target Segment": factor_scores.get('Target Audience Fit', 0.0)
            }
            
            return MarketAnalysisData(
                competitor_analysis=competitor_analysis,
                opportunities=market_opportunities,
                opportunities_rationale=f"Based on {len(market_insights)} market insights analyzed",
                market_share=market_share,
                pricing_switching={
                    "insights": [i for i in market_insights if 'price' in i.lower() or 'cost' in i.lower()][:3]
                },
                regulation_tariffs={
                    "key_regulations": [i for i in market_insights if 'regulat' in i.lower() or 'compli' in i.lower()][:3]
                },
                growth_demand={
                    "market_size": f"Score: {factor_scores.get('Market Size', 0.0):.2f}",
                    "growth_rate": f"Score: {factor_scores.get('Growth Potential', 0.0):.2f}",
                    "demand_drivers": market_insights[:3]
                },
                market_fit={
                    "overall_score": market_segment.get('score', 0.0),
                    "adoption_rate": factor_scores.get('Market Size', 0.0),
                    "market_readiness": factor_scores.get('Growth Potential', 0.0)
                }
            )
        except Exception as e:
            logger.error(f"Failed to transform market analysis: {e}", exc_info=True)
            return MarketAnalysisData()
    
    async def _transform_to_consumer_analysis(self, v2_results: Dict[str, Any]) -> ConsumerAnalysisData:
        """Transform v2.0 scoring results into Consumer Analysis format"""
        try:
            full_results = v2_results.get('full_results', {})
            segment_scores = v2_results.get('segment_scores', {})
            factor_scores = v2_results.get('factor_scores', {})
            
            # Extract consumer-related segment (Consumer Insights = S2)
            consumer_segment = segment_scores.get('Consumer Insights', segment_scores.get('S2', {}))
            
            # Get consumer-specific data from segment
            consumer_insights = consumer_segment.get('insights', [])
            consumer_opportunities = consumer_segment.get('opportunities', [])
            consumer_recommendations = consumer_segment.get('recommendations', [])
            risk_factors = consumer_segment.get('risk_factors', [])
            
            # Build recommendations with structure
            recommendations = [
                {"type": "Strategic", "timeline": "90 days", "description": rec}
                for rec in consumer_recommendations[:5]
            ]
            
            # Extract personas from insights
            personas = []
            for insight in consumer_insights:
                if 'persona' in insight.lower() or 'customer' in insight.lower():
                    personas.append({
                        "name": insight[:50] + "...",
                        "description": insight
                    })
            
            return ConsumerAnalysisData(
                recommendations=recommendations,
                challenges=risk_factors,  # Risk factors = challenges
                top_motivators=consumer_insights[:5],  # Top insights as motivators
                relevant_personas=personas[:3],
                target_audience={
                    "primary_segment": consumer_insights[0] if consumer_insights else "Analysis pending",
                    "segments": {f"Segment {i+1}": insight for i, insight in enumerate(consumer_insights[:3])}
                },
                consumer_fit={
                    "overall_score": consumer_segment.get('score', 0.0),
                    "price_sensitivity": factor_scores.get('Purchase Behavior', 0.0),
                    "adoption_likelihood": factor_scores.get('Consumer Motivation', 0.0)
                },
                additional_recommendations=consumer_opportunities
            )
        except Exception as e:
            logger.error(f"Failed to transform consumer analysis: {e}", exc_info=True)
            return ConsumerAnalysisData()
    
    async def _transform_to_product_analysis(self, v2_results: Dict[str, Any]) -> ProductAnalysisData:
        """Transform v2.0 scoring results into Product Analysis format"""
        try:
            full_results = v2_results.get('full_results', {})
            segment_scores = v2_results.get('segment_scores', {})
            factor_scores = v2_results.get('factor_scores', {})
            
            # Extract product-related segment (Product Strategy = S1)
            product_segment = segment_scores.get('Product Strategy', segment_scores.get('S1', {}))
            
            # Get product-specific data from segment
            product_insights = product_segment.get('insights', [])
            product_opportunities = product_segment.get('opportunities', [])
            product_recommendations = product_segment.get('recommendations', [])
            
            # Build product features from insights
            product_features = [
                {
                    "name": insight[:40],
                    "description": insight,
                    "importance": 0.8,
                    "category": "Core"
                }
                for insight in product_insights[:8]
            ]
            
            return ProductAnalysisData(
                product_features=product_features,
                competitive_positioning={
                    "differentiation": product_insights[0] if product_insights else "Pending analysis",
                    "unique_value": product_opportunities[0] if product_opportunities else "Pending analysis"
                },
                innovation_opportunities=product_opportunities,
                technical_specifications={
                    "key_specs": ", ".join(product_insights[:3]) if product_insights else "Pending analysis"
                },
                product_roadmap=[
                    {"phase": "Near-term", "features": rec, "timeline": "Q1 2026"}
                    for rec in product_recommendations[:3]
                ],
                product_fit={
                    "overall_score": product_segment.get('score', 0.0),
                    "feature_completeness": factor_scores.get('Product-Market Fit', 0.0),
                    "market_readiness": factor_scores.get('Feature Differentiation', 0.0)
                }
            )
        except Exception as e:
            logger.error(f"Failed to transform product analysis: {e}", exc_info=True)
            return ProductAnalysisData()
    
    async def _transform_to_brand_analysis(self, v2_results: Dict[str, Any]) -> BrandAnalysisData:
        """Transform v2.0 scoring results into Brand Analysis format"""
        try:
            full_results = v2_results.get('full_results', {})
            segment_scores = v2_results.get('segment_scores', {})
            factor_scores = v2_results.get('factor_scores', {})
            
            # Extract brand-related segment (Brand Positioning = S4)
            brand_segment = segment_scores.get('Brand Positioning', segment_scores.get('S4', {}))
            
            # Get brand-specific data from segment
            brand_insights = brand_segment.get('insights', [])
            brand_opportunities = brand_segment.get('opportunities', [])
            brand_recommendations = brand_segment.get('recommendations', [])
            
            # Build brand positioning metrics from insights
            positioning_metrics = {}
            perception_metrics = {}
            for i, insight in enumerate(brand_insights[:6]):
                if i < 4:
                    positioning_metrics[f"Attribute {i+1}"] = 0.7 + (i * 0.05)
                else:
                    perception_metrics[f"Perception {i-3}"] = 0.75 + ((i-4) * 0.03)
            
            # Build competitor brands from insights
            competitor_brands = [
                {"name": f"Competitor {i+1}", "positioning": insight, "strength": 0.7}
                for i, insight in enumerate(brand_insights[:3])
            ]
            
            return BrandAnalysisData(
                brand_positioning=positioning_metrics,
                brand_perception=perception_metrics,
                competitor_brands=competitor_brands,
                brand_opportunities=brand_opportunities,
                messaging_strategy={
                    "key_messages": brand_recommendations[:3],
                    "tone": brand_insights[0] if brand_insights else "Pending analysis"
                },
                brand_fit={
                    "overall_score": brand_segment.get('score', 0.0),
                    "market_perception": factor_scores.get('Brand Strength', 0.0),
                    "differentiation": factor_scores.get('Brand Perception', 0.0)
                }
            )
        except Exception as e:
            logger.error(f"Failed to transform brand analysis: {e}", exc_info=True)
            return BrandAnalysisData()
    
    async def _transform_to_experience_analysis(self, v2_results: Dict[str, Any]) -> ExperienceAnalysisData:
        """Transform v2.0 scoring results into Experience Analysis format"""
        try:
            full_results = v2_results.get('full_results', {})
            segment_scores = v2_results.get('segment_scores', {})
            factor_scores = v2_results.get('factor_scores', {})
            
            # Extract experience-related segment (Experience Design = S5)
            experience_segment = segment_scores.get('Experience Design', segment_scores.get('S5', {}))
            
            # Get experience-specific data from segment
            experience_insights = experience_segment.get('insights', [])
            experience_opportunities = experience_segment.get('opportunities', [])
            experience_recommendations = experience_segment.get('recommendations', [])
            risk_factors = experience_segment.get('risk_factors', [])
            
            # Build user journey from insights
            user_journey = [
                {
                    "stage": f"Stage {i+1}",
                    "phase": "Customer Journey",
                    "description": insight,
                    "pain_points": [risk_factors[i]] if i < len(risk_factors) else [],
                    "opportunities": [experience_opportunities[i]] if i < len(experience_opportunities) else []
                }
                for i, insight in enumerate(experience_insights[:4])
            ]
            
            # Build touchpoints
            touchpoints = [
                {
                    "name": f"Touchpoint {i+1}",
                    "importance": 0.85,
                    "current_quality": 0.70,
                    "improvement_potential": 0.85
                }
                for i in range(min(5, len(experience_insights)))
            ]
            
            # Build experience metrics
            experience_metrics = {
                "Ease of Use": factor_scores.get('User Experience', 0.0),
                "Customer Journey": factor_scores.get('Customer Journey', 0.0),
                "Overall Satisfaction": experience_segment.get('score', 0.0),
                "Engagement": 0.75
            }
            
            return ExperienceAnalysisData(
                user_journey=user_journey,
                touchpoints=touchpoints,
                pain_points=risk_factors,  # Risk factors = pain points
                experience_metrics=experience_metrics,
                improvement_recommendations=experience_recommendations,
                experience_fit={
                    "overall_score": experience_segment.get('score', 0.0),
                    "journey_optimization": factor_scores.get('User Experience', 0.0),
                    "touchpoint_effectiveness": factor_scores.get('Customer Journey', 0.0)
                }
            )
        except Exception as e:
            logger.error(f"Failed to transform experience analysis: {e}", exc_info=True)
            return ExperienceAnalysisData()
    
    def _extract_confidence_scores(self, v2_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract confidence scores from v2.0 results"""
        try:
            segment_scores = v2_results.get('segment_scores', {})
            
            # Use segment scores as confidence indicators
            return {
                "market": segment_scores.get('Market Intelligence', {}).get('confidence', 0.8),
                "consumer": segment_scores.get('Consumer Insights', {}).get('confidence', 0.8),
                "product": segment_scores.get('Product Strategy', {}).get('confidence', 0.8),
                "brand": segment_scores.get('Brand Positioning', {}).get('confidence', 0.8),
                "experience": segment_scores.get('Experience Design', {}).get('confidence', 0.8),
            }
        except Exception as e:
            logger.error(f"Failed to extract confidence scores: {e}")
            return {
                "market": 0.7,
                "consumer": 0.7,
                "product": 0.7,
                "brand": 0.7,
                "experience": 0.7,
            }


# Global instance
analysis_engine = ResultsAnalysisEngine()

