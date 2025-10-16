"""
Segment Content Generator
Generates rich content for Product, Brand, and Experience segments using LLM analysis
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


class SegmentContentGenerator:
    """Generate rich content for Product, Brand, and Experience segments"""
    
    def __init__(self, gemini_service):
        self.gemini = gemini_service
        logger.info("SegmentContentGenerator initialized")
    
    async def generate_product_content(self, 
                                      topic_name: str,
                                      scraped_content: List[Dict[str, Any]],
                                      factors: Dict[str, Any],
                                      patterns: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive Product segment content"""
        
        logger.info(f"Generating product content for topic: {topic_name}")
        
        # Extract text from scraped content
        content_text = self._extract_content_text(scraped_content)
        
        # Extract product insights using LLM
        product_prompt = f"""
        Based on the following market analysis for "{topic_name}", generate comprehensive product insights:
        
        Market Content Summary: {content_text[:3000]}
        
        Product Factor Scores:
        - Quality (F6): {factors.get('F6', {}).get('value', 0.5):.2f}
        - Differentiation (F7): {factors.get('F7', {}).get('value', 0.5):.2f}
        - Technical Feasibility (F8): {factors.get('F8', {}).get('value', 0.5):.2f}
        - Innovation Potential (F10): {factors.get('F10', {}).get('value', 0.5):.2f}
        
        Matched Strategic Patterns: {[p.get('name', 'N/A') for p in patterns[:3]]}
        
        Generate detailed product intelligence:
        
        1. **Key Product Features** (5-7 features):
           - Feature name, description, importance score (0-1), market validation status
        
        2. **Competitive Advantages** (3-5 unique strengths):
           - Advantage description, strength score (0-1), evidence/explanation
        
        3. **Innovation Opportunities** (3-4 specific opportunities):
           - Opportunity name, expected impact, feasibility assessment, timeline estimate
        
        4. **Technical Requirements** (3-5 requirements):
           - Requirement description, priority (High/Medium/Low), complexity estimate
        
        5. **Product Roadmap**:
           - Short-term recommendations (3-6 months): 3-4 actions
           - Long-term strategy (6-18 months): 3-4 strategic initiatives
        
        Return valid JSON only (no markdown, no explanations):
        {{
          "features": [
            {{"name": "Feature Name", "description": "Detailed description", "importance": 0.85, "market_validation": "Strong demand identified"}}
          ],
          "competitive_advantages": [
            {{"advantage": "Unique selling point", "strength_score": 0.80, "explanation": "Why this matters"}}
          ],
          "innovation_opportunities": [
            {{"opportunity": "Innovation area", "impact": "Expected business impact", "feasibility": "High/Medium/Low", "timeline": "3-6 months"}}
          ],
          "technical_requirements": [
            {{"requirement": "Technical need", "priority": "High", "complexity": "Medium"}}
          ],
          "roadmap": {{
            "short_term": ["Action 1", "Action 2", "Action 3"],
            "long_term": ["Strategic initiative 1", "Strategic initiative 2", "Strategic initiative 3"]
          }}
        }}
        """
        
        try:
            product_insights = await self._call_gemini_for_json(product_prompt)
            logger.info("Product content generated successfully")
            return product_insights
        except Exception as e:
            logger.error(f"Error generating product content: {e}")
            return self._get_default_product_content()
    
    async def generate_brand_content(self,
                                    topic_name: str,
                                    scraped_content: List[Dict[str, Any]],
                                    factors: Dict[str, Any],
                                    patterns: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive Brand segment content"""
        
        logger.info(f"Generating brand content for topic: {topic_name}")
        
        content_text = self._extract_content_text(scraped_content)
        
        brand_prompt = f"""
        Generate comprehensive brand strategy insights for "{topic_name}":
        
        Market Content Summary: {content_text[:3000]}
        
        Brand Factor Scores:
        - Positioning (F21): {factors.get('F21', {}).get('value', 0.5):.2f}
        - Brand Equity (F22): {factors.get('F22', {}).get('value', 0.5):.2f}
        - Virality/Cultural Impact (F23): {factors.get('F23', {}).get('value', 0.5):.2f}
        - Brand Trust (F24): {factors.get('F24', {}).get('value', 0.5):.2f}
        - Brand Recognition (F25): {factors.get('F25', {}).get('value', 0.5):.2f}
        
        Strategic Patterns: {[p.get('name', 'N/A') for p in patterns[:3]]}
        
        Generate:
        
        1. **Brand Positioning Strategy**:
           - Current positioning (how brand is perceived now)
           - Desired positioning (target perception)
           - Gap analysis (what needs to change)
           - Strategy to bridge the gap
        
        2. **Brand Perception Analysis**:
           - Key strengths (3-5 points)
           - Areas for improvement (3-5 points)
           - Overall market sentiment description
        
        3. **Trust Building Initiatives** (3-5 initiatives):
           - Initiative name, expected impact, implementation timeline
        
        4. **Brand Differentiation Points** (3-5 points):
           - Unique characteristic, strength score (0-1), supporting evidence
        
        5. **Messaging Framework**:
           - Core brand message
           - Target segment messages (3-4 segments with tailored messages and tone)
        
        Return valid JSON only:
        {{
          "positioning": {{
            "current": "Current market position",
            "desired": "Target positioning",
            "gap_analysis": "Analysis of gaps",
            "strategy": "Strategy to achieve desired position"
          }},
          "perception": {{
            "strengths": ["Strength 1", "Strength 2", "Strength 3"],
            "weaknesses": ["Area 1", "Area 2", "Area 3"],
            "market_sentiment": "Overall sentiment description"
          }},
          "trust_initiatives": [
            {{"initiative": "Initiative name", "impact": "Expected impact", "timeline": "3-6 months"}}
          ],
          "differentiation": [
            {{"point": "Unique characteristic", "strength": 0.75, "evidence": "Supporting data"}}
          ],
          "messaging": {{
            "core_message": "Main brand message",
            "target_segments": [
              {{"segment": "Segment name", "message": "Tailored message", "tone": "Communication tone"}}
            ]
          }}
        }}
        """
        
        try:
            brand_insights = await self._call_gemini_for_json(brand_prompt)
            logger.info("Brand content generated successfully")
            return brand_insights
        except Exception as e:
            logger.error(f"Error generating brand content: {e}")
            return self._get_default_brand_content()
    
    async def generate_experience_content(self,
                                        topic_name: str,
                                        scraped_content: List[Dict[str, Any]],
                                        factors: Dict[str, Any],
                                        patterns: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive Experience segment content"""
        
        logger.info(f"Generating experience content for topic: {topic_name}")
        
        content_text = self._extract_content_text(scraped_content)
        
        experience_prompt = f"""
        Generate comprehensive customer experience insights for "{topic_name}":
        
        Market Content Summary: {content_text[:3000]}
        
        Experience Factor Scores:
        - User Engagement (F26): {factors.get('F26', {}).get('value', 0.5):.2f}
        - Customer Satisfaction (F27): {factors.get('F27', {}).get('value', 0.5):.2f}
        - User Interface Quality (F28): {factors.get('F28', {}).get('value', 0.5):.2f}
        
        Strategic Patterns: {[p.get('name', 'N/A') for p in patterns[:3]]}
        
        Generate:
        
        1. **Customer Journey Map** (5-7 stages):
           - Stage name
           - Key touchpoints (list)
           - Pain points (list)
           - Satisfaction score (0-1)
           - Optimization opportunities (list)
        
        2. **Critical Pain Points** (3-5 major friction areas):
           - Pain point description
           - Severity (High/Medium/Low)
           - Impact on business
           - Recommended solution
        
        3. **Quick Wins** (3-5 easy improvements):
           - Improvement description, effort level, expected impact, timeline
        
        4. **Strategic Improvements** (3-4 long-term improvements):
           - Improvement description, effort level, expected impact, timeline
        
        5. **Touchpoint Quality Scores**:
           - Digital experience: score (0-1)
           - In-person experience: score (0-1)
           - Post-purchase support: score (0-1)
           - Customer support: score (0-1)
        
        Return valid JSON only:
        {{
          "journey_stages": [
            {{
              "stage": "Stage name",
              "touchpoints": ["Touchpoint 1", "Touchpoint 2"],
              "pain_points": ["Pain 1", "Pain 2"],
              "satisfaction_score": 0.75,
              "optimization_opportunities": ["Opportunity 1", "Opportunity 2"]
            }}
          ],
          "critical_pain_points": [
            {{"pain_point": "Description", "severity": "High", "impact": "Business impact", "solution": "Recommended fix"}}
          ],
          "quick_wins": [
            {{"improvement": "Quick improvement", "effort": "Low", "impact": "High", "timeline": "1-2 months"}}
          ],
          "strategic_improvements": [
            {{"improvement": "Strategic change", "effort": "High", "impact": "Very High", "timeline": "6-12 months"}}
          ],
          "touchpoint_scores": {{
            "digital": 0.72,
            "in_person": 0.68,
            "post_purchase": 0.65,
            "support": 0.78
          }}
        }}
        """
        
        try:
            experience_insights = await self._call_gemini_for_json(experience_prompt)
            logger.info("Experience content generated successfully")
            return experience_insights
        except Exception as e:
            logger.error(f"Error generating experience content: {e}")
            return self._get_default_experience_content()
    
    def _extract_content_text(self, scraped_content: List[Dict[str, Any]]) -> str:
        """Extract text from scraped content"""
        if not scraped_content:
            return "No content available"
        
        text_parts = []
        for item in scraped_content[:5]:  # Use first 5 items
            if isinstance(item, dict):
                text = item.get('content', item.get('text', ''))
                if text:
                    text_parts.append(text[:500])  # First 500 chars of each
        
        return " ".join(text_parts) if text_parts else "Limited content available"
    
    async def _call_gemini_for_json(self, prompt: str) -> Dict[str, Any]:
        """Call Gemini API and parse JSON response"""
        try:
            response = await self.gemini.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove trailing ```
            
            response_text = response_text.strip()
            
            # Parse JSON
            data = json.loads(response_text)
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise
    
    def _get_default_product_content(self) -> Dict[str, Any]:
        """Return default product content when generation fails"""
        return {
            "features": [
                {"name": "Core Functionality", "description": "Primary product capabilities", "importance": 0.8, "market_validation": "Market analysis pending"},
                {"name": "User Experience", "description": "Intuitive interface and interaction", "importance": 0.75, "market_validation": "User feedback needed"}
            ],
            "competitive_advantages": [
                {"advantage": "Market positioning", "strength_score": 0.7, "explanation": "Strategic market position"}
            ],
            "innovation_opportunities": [
                {"opportunity": "Feature enhancement", "impact": "Moderate", "feasibility": "High", "timeline": "3-6 months"}
            ],
            "technical_requirements": [
                {"requirement": "Infrastructure scaling", "priority": "Medium", "complexity": "Medium"}
            ],
            "roadmap": {
                "short_term": ["Enhance core features", "Improve user experience", "Gather user feedback"],
                "long_term": ["Expand feature set", "Enter new markets", "Build ecosystem"]
            }
        }
    
    def _get_default_brand_content(self) -> Dict[str, Any]:
        """Return default brand content when generation fails"""
        return {
            "positioning": {
                "current": "Current market position analysis pending",
                "desired": "Target premium/value positioning",
                "gap_analysis": "Positioning strategy under development",
                "strategy": "Build brand equity through consistent messaging"
            },
            "perception": {
                "strengths": ["Product quality", "Customer service", "Innovation"],
                "weaknesses": ["Brand awareness", "Market penetration", "Premium positioning"],
                "market_sentiment": "Positive with room for growth"
            },
            "trust_initiatives": [
                {"initiative": "Transparency program", "impact": "High trust improvement", "timeline": "3-6 months"}
            ],
            "differentiation": [
                {"point": "Unique value proposition", "strength": 0.7, "evidence": "Market analysis"}
            ],
            "messaging": {
                "core_message": "Quality and innovation leader",
                "target_segments": [
                    {"segment": "Early adopters", "message": "Cutting-edge solutions", "tone": "Innovative and bold"}
                ]
            }
        }
    
    def _get_default_experience_content(self) -> Dict[str, Any]:
        """Return default experience content when generation fails"""
        return {
            "journey_stages": [
                {
                    "stage": "Discovery",
                    "touchpoints": ["Website", "Social media", "Search"],
                    "pain_points": ["Limited information", "Complex navigation"],
                    "satisfaction_score": 0.68,
                    "optimization_opportunities": ["Improve SEO", "Simplify navigation"]
                },
                {
                    "stage": "Purchase",
                    "touchpoints": ["Checkout", "Payment", "Confirmation"],
                    "pain_points": ["Long checkout process"],
                    "satisfaction_score": 0.72,
                    "optimization_opportunities": ["Streamline checkout", "Add payment options"]
                }
            ],
            "critical_pain_points": [
                {"pain_point": "Complex user onboarding", "severity": "High", "impact": "Reduces conversions", "solution": "Simplify onboarding flow"}
            ],
            "quick_wins": [
                {"improvement": "Improve page load times", "effort": "Low", "impact": "Medium", "timeline": "1 month"}
            ],
            "strategic_improvements": [
                {"improvement": "Build mobile app", "effort": "High", "impact": "Very High", "timeline": "6-12 months"}
            ],
            "touchpoint_scores": {
                "digital": 0.70,
                "in_person": 0.65,
                "post_purchase": 0.68,
                "support": 0.75
            }
        }

