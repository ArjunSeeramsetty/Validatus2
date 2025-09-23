# backend/app/services/expert_persona_scorer.py

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json
import re
from collections import Counter

from google.cloud import aiplatform
from langchain_google_vertexai import VertexAI
from langchain_google_vertexai import VertexAIEmbeddings

from ..models.analysis_models import LayerScore
from ..middleware.monitoring import performance_monitor

logger = logging.getLogger(__name__)

class ExpertPersonaScorer:
    """AI-powered expert persona scoring for strategic analysis layers"""
    
    def __init__(self):
        # Initialize Vertex AI models
        self.llm = VertexAI(
            model_name="gemini-1.5-pro",
            temperature=0.1,
            max_output_tokens=2048
        )
        self.embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
        
        # Define expert personas for each strategic layer
        self.expert_personas = {
            'consumer': {
                'name': 'Dr. Sarah Chen - Consumer Psychology Expert',
                'background': 'PhD in Consumer Psychology, 15 years at leading market research firms',
                'expertise': ['consumer behavior', 'market segmentation', 'brand perception', 'purchase decisions'],
                'perspective': 'Focus on understanding consumer motivations, pain points, and decision-making processes',
                'scoring_criteria': ['market demand', 'consumer adoption', 'user experience', 'brand resonance']
            },
            'market': {
                'name': 'Michael Rodriguez - Market Strategy Consultant',
                'background': 'MBA from Wharton, 20 years at McKinsey and BCG',
                'expertise': ['market analysis', 'competitive landscape', 'growth opportunities', 'market sizing'],
                'perspective': 'Analyze market dynamics, competitive positioning, and growth potential',
                'scoring_criteria': ['market size', 'growth rate', 'competitive intensity', 'barriers to entry']
            },
            'product': {
                'name': 'Alex Kim - Product Innovation Lead',
                'background': 'MS in Engineering, Former Product Manager at Google and Apple',
                'expertise': ['product development', 'innovation', 'user experience', 'technical feasibility'],
                'perspective': 'Evaluate product-market fit, innovation potential, and technical viability',
                'scoring_criteria': ['innovation level', 'product-market fit', 'technical feasibility', 'differentiation']
            },
            'brand': {
                'name': 'Emma Thompson - Brand Strategy Director',
                'background': 'MA in Marketing, 12 years at top advertising agencies',
                'expertise': ['brand strategy', 'brand positioning', 'brand equity', 'marketing communications'],
                'perspective': 'Assess brand strength, positioning clarity, and marketing effectiveness',
                'scoring_criteria': ['brand awareness', 'brand perception', 'brand loyalty', 'marketing reach']
            },
            'experience': {
                'name': 'David Park - Customer Experience Designer',
                'background': 'UX Design Certification, Former CX Lead at Amazon and Netflix',
                'expertise': ['user experience', 'customer journey', 'service design', 'digital transformation'],
                'perspective': 'Focus on customer experience quality, touchpoint optimization, and satisfaction',
                'scoring_criteria': ['user satisfaction', 'ease of use', 'customer support', 'digital experience']
            },
            'technology': {
                'name': 'Dr. Lisa Wang - Technology Innovation Researcher',
                'background': 'PhD in Computer Science, Research Director at MIT Technology Review',
                'expertise': ['emerging technologies', 'AI/ML', 'blockchain', 'cybersecurity', 'scalability'],
                'perspective': 'Evaluate technological innovation, scalability, security, and future readiness',
                'scoring_criteria': ['technical innovation', 'scalability', 'security', 'future readiness']
            },
            'operations': {
                'name': 'James Foster - Operations Excellence Manager',
                'background': 'MBA in Operations, Former COO at Fortune 500 companies',
                'expertise': ['operational efficiency', 'supply chain', 'process optimization', 'quality management'],
                'perspective': 'Assess operational efficiency, process quality, and scalability',
                'scoring_criteria': ['operational efficiency', 'process quality', 'supply chain', 'cost management']
            },
            'financial': {
                'name': 'Rachel Green - Financial Strategy Advisor',
                'background': 'CFA Charterholder, Former Investment Banker at Goldman Sachs',
                'expertise': ['financial modeling', 'investment analysis', 'risk assessment', 'valuation'],
                'perspective': 'Analyze financial viability, profitability, and investment attractiveness',
                'scoring_criteria': ['profitability', 'financial stability', 'growth potential', 'risk profile']
            },
            'competitive': {
                'name': 'Tom Anderson - Competitive Intelligence Analyst',
                'background': 'MS in Business Intelligence, Former Strategy Consultant at Bain',
                'expertise': ['competitive analysis', 'market positioning', 'strategic planning', 'industry trends'],
                'perspective': 'Evaluate competitive positioning, market share potential, and strategic advantages',
                'scoring_criteria': ['competitive advantage', 'market position', 'barriers to competition', 'differentiation']
            },
            'regulatory': {
                'name': 'Jennifer Liu - Regulatory Compliance Expert',
                'background': 'JD from Harvard Law, Former Regulatory Affairs Director at Pfizer',
                'expertise': ['regulatory compliance', 'legal risk', 'policy analysis', 'government relations'],
                'perspective': 'Assess regulatory environment, compliance requirements, and legal risks',
                'scoring_criteria': ['regulatory compliance', 'legal risk', 'policy support', 'government relations']
            }
        }
        
    @performance_monitor
    async def score_layer(self, 
                         topic_knowledge: Dict[str, Any], 
                         layer_name: str, 
                         session_id: str) -> Dict[str, Any]:
        """Score a strategic layer using expert persona analysis"""
        
        logger.info(f"Scoring {layer_name} layer for session {session_id}")
        
        try:
            # Get expert persona for the layer
            persona = self.expert_personas.get(layer_name.lower(), self.expert_personas['market'])
            
            # Prepare analysis context
            analysis_context = await self._prepare_analysis_context(topic_knowledge, layer_name, persona)
            
            # Generate expert analysis
            expert_analysis = await self._generate_expert_analysis(analysis_context, persona)
            
            # Extract scoring components
            score_components = await self._extract_score_components(expert_analysis, persona)
            
            # Calculate final score
            final_score = self._calculate_final_score(score_components, persona)
            
            # Generate insights and evidence
            insights = await self._generate_insights(expert_analysis, score_components)
            evidence = await self._extract_evidence(topic_knowledge, layer_name, insights)
            
            # Create confidence score
            confidence = self._calculate_confidence_score(score_components, evidence)
            
            result = {
                'score': final_score,
                'confidence': confidence,
                'insights': insights,
                'evidence': evidence,
                'evidence_summary': self._summarize_evidence(evidence),
                'score_components': score_components,
                'expert_persona': persona['name'],
                'metadata': {
                    'layer_name': layer_name,
                    'session_id': session_id,
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                    'expert_background': persona['background']
                }
            }
            
            logger.info(f"✅ {layer_name} layer scored: {final_score:.3f} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to score {layer_name} layer: {e}")
            return {
                'score': 0.5,
                'confidence': 0.3,
                'insights': [f"Analysis failed for {layer_name} layer"],
                'evidence': [],
                'evidence_summary': f"Unable to analyze {layer_name} layer due to technical issues",
                'score_components': {},
                'expert_persona': 'Unknown',
                'metadata': {'error': str(e)}
            }
    
    async def _prepare_analysis_context(self, 
                                      topic_knowledge: Dict[str, Any], 
                                      layer_name: str, 
                                      persona: Dict[str, Any]) -> str:
        """Prepare context for expert analysis"""
        
        # Extract relevant content from topic knowledge
        documents = topic_knowledge.get('documents', [])
        relevant_content = []
        
        for doc in documents[:10]:  # Limit to top 10 documents
            content = doc.get('content', '')
            if content:
                # Extract key paragraphs related to the layer
                key_paragraphs = self._extract_layer_relevant_content(content, layer_name)
                if key_paragraphs:
                    relevant_content.extend(key_paragraphs)
        
        # Combine content
        analysis_content = '\n\n'.join(relevant_content[:5])  # Top 5 relevant sections
        
        # Create context prompt
        context = f"""
Topic: {topic_knowledge.get('topic', 'Unknown')}
Layer: {layer_name.title()}
Expert: {persona['name']}
Expert Background: {persona['background']}
Expert Perspective: {persona['perspective']}

Relevant Content:
{analysis_content}

Please analyze this content from the perspective of {persona['name']} and provide insights on {layer_name} aspects.
"""
        
        return context
    
    async def _generate_expert_analysis(self, 
                                      context: str, 
                                      persona: Dict[str, Any]) -> str:
        """Generate expert analysis using AI"""
        
        prompt = f"""
You are {persona['name']}, {persona['background']}.

Your expertise areas: {', '.join(persona['expertise'])}
Your analytical perspective: {persona['perspective']}

Please provide a comprehensive analysis focusing on these criteria:
{', '.join(persona['scoring_criteria'])}

Context to analyze:
{context}

Provide your analysis in the following format:
1. Key Observations
2. Strengths and Opportunities
3. Weaknesses and Risks
4. Strategic Recommendations
5. Scoring Rationale (rate each criterion 1-10)

Be specific, evidence-based, and professional in your analysis.
"""
        
        try:
            analysis = await self.llm.ainvoke(prompt)
            return analysis.content if hasattr(analysis, 'content') else str(analysis)
        except Exception as e:
            logger.error(f"AI analysis generation failed: {e}")
            return f"Analysis unavailable due to technical issues: {str(e)}"
    
    async def _extract_score_components(self, 
                                      expert_analysis: str, 
                                      persona: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical scores from expert analysis"""
        
        score_components = {}
        criteria = persona['scoring_criteria']
        
        try:
            # Look for scoring patterns in the analysis
            for criterion in criteria:
                # Search for criterion mentions with scores
                pattern = rf'{criterion}.*?(\d+(?:\.\d+)?)'
                matches = re.findall(pattern, expert_analysis.lower())
                
                if matches:
                    # Take the last mentioned score
                    score = float(matches[-1])
                    # Normalize to 0-1 scale
                    normalized_score = min(score / 10.0, 1.0)
                    score_components[criterion] = normalized_score
                else:
                    # Default score based on sentiment analysis
                    score_components[criterion] = await self._estimate_score_from_sentiment(
                        expert_analysis, criterion
                    )
            
            # Ensure all criteria have scores
            for criterion in criteria:
                if criterion not in score_components:
                    score_components[criterion] = 0.5
            
            return score_components
            
        except Exception as e:
            logger.error(f"Score extraction failed: {e}")
            # Return default scores
            return {criterion: 0.5 for criterion in criteria}
    
    async def _estimate_score_from_sentiment(self, 
                                           analysis: str, 
                                           criterion: str) -> float:
        """Estimate score based on sentiment analysis of the analysis text"""
        
        try:
            # Simple sentiment analysis based on keywords
            positive_words = ['strong', 'excellent', 'good', 'positive', 'opportunity', 'advantage', 'benefit']
            negative_words = ['weak', 'poor', 'negative', 'risk', 'challenge', 'disadvantage', 'concern']
            
            # Count positive and negative mentions
            positive_count = sum(1 for word in positive_words if word in analysis.lower())
            negative_count = sum(1 for word in negative_words if word in analysis.lower())
            
            # Calculate sentiment score
            total_sentiment_words = positive_count + negative_count
            if total_sentiment_words == 0:
                return 0.5
            
            sentiment_ratio = positive_count / total_sentiment_words
            return sentiment_ratio
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return 0.5
    
    def _calculate_final_score(self, 
                             score_components: Dict[str, float], 
                             persona: Dict[str, Any]) -> float:
        """Calculate final weighted score from components"""
        
        try:
            criteria = persona['scoring_criteria']
            
            # Equal weighting for now (can be customized per persona)
            weights = {criterion: 1.0 / len(criteria) for criterion in criteria}
            
            # Calculate weighted average
            weighted_sum = sum(score_components.get(criterion, 0.5) * weights[criterion] 
                             for criterion in criteria)
            
            return round(weighted_sum, 3)
            
        except Exception as e:
            logger.error(f"Final score calculation failed: {e}")
            return 0.5
    
    async def _generate_insights(self, 
                               expert_analysis: str, 
                               score_components: Dict[str, float]) -> List[str]:
        """Generate key insights from expert analysis"""
        
        insights = []
        
        try:
            # Extract key observations
            lines = expert_analysis.split('\n')
            for line in lines:
                line = line.strip()
                if (line and 
                    not line.startswith('#') and 
                    not line.startswith('1.') and 
                    not line.startswith('2.') and
                    not line.startswith('3.') and
                    not line.startswith('4.') and
                    not line.startswith('5.') and
                    len(line) > 20):
                    insights.append(line)
            
            # Limit to top insights
            insights = insights[:5]
            
            # Add score-based insights
            top_criteria = sorted(score_components.items(), key=lambda x: x[1], reverse=True)[:2]
            for criterion, score in top_criteria:
                insights.append(f"Strong performance in {criterion.replace('_', ' ')} (score: {score:.2f})")
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return ["Analysis insights unavailable"]
    
    async def _extract_evidence(self, 
                              topic_knowledge: Dict[str, Any], 
                              layer_name: str, 
                              insights: List[str]) -> List[Dict[str, Any]]:
        """Extract supporting evidence from topic knowledge"""
        
        evidence = []
        
        try:
            documents = topic_knowledge.get('documents', [])
            
            # Find documents that support the insights
            for insight in insights[:3]:  # Top 3 insights
                supporting_docs = []
                
                for doc in documents:
                    content = doc.get('content', '').lower()
                    insight_words = insight.lower().split()
                    
                    # Check if document contains relevant keywords
                    if any(word in content for word in insight_words if len(word) > 3):
                        supporting_docs.append({
                            'url': doc.get('url', 'Unknown'),
                            'title': doc.get('title', 'Untitled'),
                            'relevance_score': sum(1 for word in insight_words if word in content) / len(insight_words)
                        })
                
                # Sort by relevance
                supporting_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
                
                evidence.append({
                    'insight': insight,
                    'supporting_documents': supporting_docs[:3],  # Top 3 supporting docs
                    'evidence_strength': len(supporting_docs)
                })
            
            return evidence
            
        except Exception as e:
            logger.error(f"Evidence extraction failed: {e}")
            return []
    
    def _summarize_evidence(self, evidence: List[Dict[str, Any]]) -> str:
        """Create a summary of evidence"""
        
        try:
            total_docs = sum(len(ev.get('supporting_documents', [])) for ev in evidence)
            
            if total_docs == 0:
                return "No supporting evidence found"
            
            return f"Analysis supported by {total_docs} relevant documents across {len(evidence)} key insights"
            
        except Exception as e:
            logger.error(f"Evidence summarization failed: {e}")
            return "Evidence summary unavailable"
    
    def _calculate_confidence_score(self, 
                                  score_components: Dict[str, float], 
                                  evidence: List[Dict[str, Any]]) -> float:
        """Calculate confidence in the scoring"""
        
        try:
            # Base confidence on score consistency and evidence strength
            scores = list(score_components.values())
            
            # Calculate variance (lower variance = higher confidence)
            if len(scores) > 1:
                mean_score = sum(scores) / len(scores)
                variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
                consistency_score = max(0, 1 - variance)
            else:
                consistency_score = 0.5
            
            # Evidence strength component
            total_evidence = sum(len(ev.get('supporting_documents', [])) for ev in evidence)
            evidence_score = min(total_evidence / 10.0, 1.0)  # Normalize to 0-1
            
            # Combine confidence factors
            confidence = (consistency_score * 0.6 + evidence_score * 0.4)
            
            return round(confidence, 3)
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5
    
    def _extract_layer_relevant_content(self, content: str, layer_name: str) -> List[str]:
        """Extract content relevant to a specific strategic layer"""
        
        # Define keywords for each layer
        layer_keywords = {
            'consumer': ['customer', 'user', 'buyer', 'audience', 'demand', 'preference', 'behavior'],
            'market': ['market', 'industry', 'sector', 'competition', 'growth', 'size', 'trend'],
            'product': ['product', 'feature', 'innovation', 'technology', 'development', 'design'],
            'brand': ['brand', 'image', 'reputation', 'identity', 'positioning', 'marketing'],
            'experience': ['experience', 'interface', 'usability', 'satisfaction', 'service', 'support'],
            'technology': ['technology', 'tech', 'software', 'hardware', 'system', 'platform', 'api'],
            'operations': ['operation', 'process', 'efficiency', 'production', 'supply', 'quality'],
            'financial': ['financial', 'revenue', 'profit', 'cost', 'investment', 'funding', 'valuation'],
            'competitive': ['competitive', 'competitor', 'advantage', 'position', 'differentiation'],
            'regulatory': ['regulation', 'compliance', 'legal', 'policy', 'government', 'law']
        }
        
        keywords = layer_keywords.get(layer_name.lower(), [layer_name.lower()])
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        relevant_paragraphs = []
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            # Check if paragraph contains layer-relevant keywords
            if any(keyword in paragraph_lower for keyword in keywords):
                relevant_paragraphs.append(paragraph)
        
        return relevant_paragraphs[:3]  # Return top 3 relevant paragraphs

# Export the class
__all__ = ['ExpertPersonaScorer']
