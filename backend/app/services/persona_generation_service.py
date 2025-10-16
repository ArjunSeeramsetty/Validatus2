"""
Persona Generation Service
Generates realistic consumer personas from analysis data
Addresses the "Consumer personas will be generated from analysis" placeholder issue
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PersonaGenerationService:
    """
    Generates data-driven consumer personas
    Uses factor scores and scraped content to create realistic personas
    """
    
    def __init__(self, llm_service=None):
        """Initialize with LLM service"""
        self.llm_service = llm_service
        logger.info("Persona Generation Service initialized")
    
    async def generate_personas(
        self,
        session_id: str,
        consumer_factors: Dict[str, float],
        scraped_content: List[Dict[str, Any]],
        num_personas: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generate consumer personas from analysis data
        
        Args:
            session_id: Topic session ID
            consumer_factors: Consumer factor scores (F11-F15)
            scraped_content: Scraped content for context
            num_personas: Number of personas to generate (3-5)
        
        Returns:
            List of persona dictionaries with demographics, pain points, etc.
        """
        try:
            if not scraped_content:
                logger.warning(f"No content available for persona generation: {session_id}")
                return self._get_default_personas()
            
            # Prepare content summary
            content_summary = self._prepare_content_summary(scraped_content)
            
            # Generate personas using LLM
            personas = await self._generate_personas_with_llm(
                consumer_factors,
                content_summary,
                num_personas
            )
            
            # Validate and normalize
            validated_personas = self._validate_personas(personas)
            
            logger.info(f"Generated {len(validated_personas)} personas for {session_id}")
            
            return validated_personas
            
        except Exception as e:
            logger.error(f"Persona generation failed for {session_id}: {e}", exc_info=True)
            return self._get_default_personas()
    
    def _prepare_content_summary(self, scraped_content: List[Dict[str, Any]], max_chars: int = 8000) -> str:
        """Prepare content summary for persona generation"""
        summaries = []
        total_chars = 0
        
        for item in scraped_content[:10]:  # Limit to top 10 items
            content = item.get('content', '')
            title = item.get('title', '')
            
            # Extract relevant sections about consumers/customers
            consumer_relevant = any(keyword in content.lower() for keyword in [
                'consumer', 'customer', 'buyer', 'user', 'demographic',
                'audience', 'persona', 'segment', 'target market'
            ])
            
            if consumer_relevant or total_chars < 2000:
                summary = f"Source: {title}\n{content[:1500]}\n"
                summaries.append(summary)
                total_chars += len(summary)
                
                if total_chars >= max_chars:
                    break
        
        return '\n---\n'.join(summaries)
    
    async def _generate_personas_with_llm(
        self,
        consumer_factors: Dict[str, float],
        content_summary: str,
        num_personas: int
    ) -> List[Dict[str, Any]]:
        """Generate personas using LLM"""
        
        if not self.llm_service:
            return self._get_default_personas()
        
        prompt = f"""
Based on the following consumer intelligence analysis, generate {num_personas} distinct, realistic consumer personas.

Consumer Factor Scores (0.0-1.0):
- Demand & Need (F11): {consumer_factors.get('F11', 0.5):.2f}
- Behavior & Habits (F12): {consumer_factors.get('F12', 0.5):.2f}
- Loyalty & Retention (F13): {consumer_factors.get('F13', 0.5):.2f}
- Perception & Sentiment (F14): {consumer_factors.get('F14', 0.5):.2f}
- Adoption & Engagement (F15): {consumer_factors.get('F15', 0.5):.2f}

Market Research Content:
{content_summary}

For each persona, provide:
1. **name**: Realistic fictional name
2. **age**: Age or age range
3. **demographics**: {{"location": str, "income_range": str, "occupation": str, "family_status": str}}
4. **psychographics**: {{"values": [str], "lifestyle": str, "motivations": [str]}}
5. **pain_points**: List of 3-5 specific pain points
6. **goals**: List of 3-4 goals related to this product/service
7. **buying_behavior**: {{"research_style": str, "decision_timeline": str, "influences": [str], "price_sensitivity": str}}
8. **market_share**: float (0.1-0.4, must sum to ~1.0 across all personas)
9. **value_tier**: "Premium" | "Mid-Market" | "Budget"
10. **key_messaging**: List of 3-4 messaging points that resonate with this persona
11. **description**: One-sentence persona summary

Make personas distinct and realistic. Ensure market shares sum to approximately 1.0.

Return JSON array:
[
  {{
    "name": str,
    "age": str,
    "demographics": object,
    "psychographics": object,
    "pain_points": [str],
    "goals": [str],
    "buying_behavior": object,
    "market_share": float,
    "value_tier": str,
    "key_messaging": [str],
    "description": str
  }}
]
"""
        
        try:
            response = await self.llm_service.generate_structured_output(
                prompt=prompt,
                response_format="json"
            )
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'personas' in response:
                return response['personas']
            else:
                logger.warning(f"Unexpected LLM response format: {type(response)}")
                return self._get_default_personas()
                
        except Exception as e:
            logger.error(f"LLM persona generation failed: {e}")
            return self._get_default_personas()
    
    def _validate_personas(self, personas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and normalize persona data"""
        
        if not personas:
            return self._get_default_personas()
        
        validated = []
        total_market_share = 0
        
        for persona in personas:
            # Ensure required fields
            if not persona.get('name'):
                continue
            
            # Normalize market share
            market_share = float(persona.get('market_share', 0.25))
            market_share = min(0.5, max(0.05, market_share))
            total_market_share += market_share
            
            # Ensure all fields exist
            validated_persona = {
                "name": persona.get('name', 'Unknown Persona'),
                "age": str(persona.get('age', '30-45')),
                "description": persona.get('description', 'Consumer persona'),
                "demographics": persona.get('demographics', {
                    "location": "Unknown",
                    "income_range": "Unknown",
                    "occupation": "Unknown",
                    "family_status": "Unknown"
                }),
                "psychographics": persona.get('psychographics', {
                    "values": [],
                    "lifestyle": "Unknown",
                    "motivations": []
                }),
                "pain_points": persona.get('pain_points', []),
                "goals": persona.get('goals', []),
                "buying_behavior": persona.get('buying_behavior', {
                    "research_style": "Unknown",
                    "decision_timeline": "Unknown",
                    "influences": [],
                    "price_sensitivity": "Medium"
                }),
                "market_share": market_share,
                "value_tier": persona.get('value_tier', 'Mid-Market'),
                "key_messaging": persona.get('key_messaging', [])
            }
            
            validated.append(validated_persona)
        
        # Normalize market shares to sum to 1.0
        if validated and total_market_share > 0:
            for persona in validated:
                persona['market_share'] = persona['market_share'] / total_market_share
        
        return validated
    
    def _get_default_personas(self) -> List[Dict[str, Any]]:
        """Default personas when generation fails"""
        return [
            {
                "name": "Data-Driven Persona",
                "age": "35-50",
                "description": "Personas will be generated from market analysis data",
                "demographics": {
                    "location": "To be determined from analysis",
                    "income_range": "To be determined",
                    "occupation": "To be determined",
                    "family_status": "To be determined"
                },
                "psychographics": {
                    "values": ["Quality", "Value", "Innovation"],
                    "lifestyle": "To be determined from analysis",
                    "motivations": ["To be extracted from content"]
                },
                "pain_points": ["Analysis in progress"],
                "goals": ["To be determined"],
                "buying_behavior": {
                    "research_style": "To be analyzed",
                    "decision_timeline": "To be determined",
                    "influences": ["To be identified"],
                    "price_sensitivity": "Medium"
                },
                "market_share": 1.0,
                "value_tier": "Mid-Market",
                "key_messaging": ["Messaging to be determined from analysis"]
            }
        ]


# Singleton instance
_persona_service_instance = None

def get_persona_generation_service(llm_service=None):
    """Get or create singleton persona service instance"""
    global _persona_service_instance
    if _persona_service_instance is None:
        _persona_service_instance = PersonaGenerationService(llm_service)
    return _persona_service_instance

