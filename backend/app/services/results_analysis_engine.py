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
        """Generate comprehensive analysis across all dimensions"""
        
        logger.info(f"Starting complete analysis generation for session {session_id}")
        
        try:
            # Get topic information
            topic_info = await self._get_topic_info(session_id)
            
            # Get scraped content for analysis
            content_data = await self._get_content_data(session_id)
            
            # Run all analysis dimensions in parallel
            market_task = self._analyze_market_dimension(session_id, topic_info, content_data)
            consumer_task = self._analyze_consumer_dimension(session_id, topic_info, content_data)
            product_task = self._analyze_product_dimension(session_id, topic_info, content_data)
            brand_task = self._analyze_brand_dimension(session_id, topic_info, content_data)
            experience_task = self._analyze_experience_dimension(session_id, topic_info, content_data)
            
            results = await asyncio.gather(
                market_task,
                consumer_task,
                product_task,
                brand_task,
                experience_task,
                return_exceptions=True
            )
            
            market_analysis = results[0] if not isinstance(results[0], Exception) else MarketAnalysisData()
            consumer_analysis = results[1] if not isinstance(results[1], Exception) else ConsumerAnalysisData()
            product_analysis = results[2] if not isinstance(results[2], Exception) else ProductAnalysisData()
            brand_analysis = results[3] if not isinstance(results[3], Exception) else BrandAnalysisData()
            experience_analysis = results[4] if not isinstance(results[4], Exception) else ExperienceAnalysisData()
            
            # Get existing business case if available
            business_case = await self._get_business_case(session_id)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(content_data, results)
            
            return CompleteAnalysisResult(
                session_id=session_id,
                topic_name=topic_info.get('topic', 'Unknown'),
                analysis_timestamp=datetime.utcnow(),
                business_case=business_case,
                market=market_analysis,
                consumer=consumer_analysis,
                product=product_analysis,
                brand=brand_analysis,
                experience=experience_analysis,
                confidence_scores=confidence_scores
            )
            
        except Exception as e:
            logger.error(f"Failed to generate complete analysis for {session_id}: {e}", exc_info=True)
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


# Global instance
analysis_engine = ResultsAnalysisEngine()

