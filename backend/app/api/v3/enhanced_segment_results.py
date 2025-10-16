"""
Enhanced Segment Results API
Provides comprehensive analysis with Monte Carlo scenarios and rich content for all segments
"""

from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.core.database_config import db_manager
from app.services.comprehensive_pattern_library import PatternLibrary
from app.services.segment_monte_carlo_engine import SegmentMonteCarloEngine
from app.services.segment_content_generator import SegmentContentGenerator
from app.services.gemini_service import GeminiService
from app.services.persona_generation_service import PersonaGenerationService
from app.models.session import TopicSession
from app.models.url_collection import CollectedURL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3/enhanced-segment-results", tags=["enhanced-segment-results"])


def get_db():
    """Get database session"""
    db = db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{topic_id}/{segment}")
async def get_enhanced_segment_results(
    topic_id: str = Path(..., description="Topic session ID"),
    segment: str = Path(..., description="Segment name: market, consumer, product, brand, or experience"),
    db: Session = Depends(get_db)
):
    """
    Get fully enhanced segment results with:
    - Segment-specific Monte Carlo scenarios (Market:4, Consumer:4, Brand:4, Product:3, Experience:2)
    - Pattern matching with all 41 patterns
    - Rich content generation for Product/Brand/Experience
    - Persona generation for Consumer
    - WCAG AAA accessible color schemes
    """
    
    try:
        # Validate segment
        valid_segments = ['market', 'consumer', 'product', 'brand', 'experience']
        if segment.lower() not in valid_segments:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid segment. Must be one of: {', '.join(valid_segments)}"
            )
        
        segment = segment.lower()
        
        logger.info(f"Generating enhanced results for topic {topic_id}, segment {segment}")
        
        # Get topic session
        topic_session = db.query(TopicSession).filter(TopicSession.session_id == topic_id).first()
        if not topic_session:
            raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
        
        # Initialize services
        pattern_library = PatternLibrary()
        monte_carlo_engine = SegmentMonteCarloEngine()
        gemini_service = GeminiService()
        content_generator = SegmentContentGenerator(gemini_service)
        
        # 1. Get scraped content for this topic
        scraped_urls = db.query(CollectedURL).filter(
            CollectedURL.session_id == topic_id
        ).all()
        
        scraped_content = [
            {
                'url': url.url,
                'content': url.scraped_content or '',
                'text': url.scraped_content or ''
            }
            for url in scraped_urls if url.scraped_content
        ]
        
        logger.info(f"Found {len(scraped_content)} scraped content items")
        
        # 2. Generate mock factor scores (in production, calculate from actual analysis)
        # For now, use reasonable defaults based on segment
        factors = _generate_mock_factors(segment, scraped_content)
        factor_scores = {fid: f['value'] for fid, f in factors.items()}
        
        # 3. Match patterns for this segment
        matched_patterns = pattern_library.match_patterns_to_segment(segment, factor_scores)
        
        logger.info(f"Matched {len(matched_patterns)} patterns for {segment}")
        
        # 4. Generate Monte Carlo scenarios (segment-specific count)
        monte_carlo_scenarios = await monte_carlo_engine.generate_segment_scenarios(
            segment, matched_patterns, factor_scores
        )
        
        logger.info(f"Generated {len(monte_carlo_scenarios)} Monte Carlo scenarios")
        
        # 5. Generate personas (Consumer only)
        personas = []
        if segment == "consumer":
            try:
                persona_gen = PersonaGenerationService(gemini_service)
                personas = await persona_gen.generate_personas(
                    topic_id, 
                    factor_scores, 
                    scraped_content,
                    num_personas=4
                )
                logger.info(f"Generated {len(personas)} personas")
            except Exception as e:
                logger.warning(f"Persona generation failed: {e}. Using defaults.")
                personas = []
        
        # 6. Generate rich content (Product, Brand, Experience)
        rich_content = {}
        try:
            if segment == "product":
                rich_content = await content_generator.generate_product_content(
                    topic_session.topic_name,
                    scraped_content,
                    factors,
                    matched_patterns
                )
            elif segment == "brand":
                rich_content = await content_generator.generate_brand_content(
                    topic_session.topic_name,
                    scraped_content,
                    factors,
                    matched_patterns
                )
            elif segment == "experience":
                rich_content = await content_generator.generate_experience_content(
                    topic_session.topic_name,
                    scraped_content,
                    factors,
                    matched_patterns
                )
            
            if rich_content:
                logger.info(f"Generated rich content for {segment}")
        except Exception as e:
            logger.warning(f"Rich content generation failed: {e}. Using defaults.")
            rich_content = {}
        
        # 7. Build comprehensive response
        response = {
            "topic_id": topic_id,
            "topic_name": topic_session.topic_name,
            "segment": segment,
            "timestamp": datetime.utcnow().isoformat(),
            
            # Factor Analysis
            "factors": factors,
            
            # Pattern Matches
            "matched_patterns": [
                {
                    "pattern_id": p.get('id', 'P000'),
                    "pattern_name": p.get('name', 'Strategic Pattern'),
                    "pattern_type": p.get('type', 'Opportunity'),
                    "confidence": p.get('confidence', 0.65),
                    "match_score": p.get('match_score', 0.70),
                    "strategic_response": p.get('strategic_response', 'Strategic recommendation'),
                    "effect_size_hints": p.get('effect_size_hints', 'Expected positive impact'),
                    "probability_range": p.get('probability_range', [0.5, 0.8])
                } for p in matched_patterns[:monte_carlo_engine.required_scenarios.get(segment, 4)]
            ],
            
            # Monte Carlo Scenarios
            "monte_carlo_scenarios": [scenario.to_dict() for scenario in monte_carlo_scenarios],
            
            # Personas (Consumer only)
            "personas": personas,
            
            # Rich Content (Product/Brand/Experience)
            "rich_content": rich_content,
            
            # Metadata
            "scenario_count": len(monte_carlo_scenarios),
            "required_scenarios": monte_carlo_engine.required_scenarios.get(segment, 4),
            "patterns_matched": len(matched_patterns),
            "content_items_analyzed": len(scraped_content)
        }
        
        logger.info(f"Successfully generated enhanced results for {segment}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced segment results generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Enhanced segment results generation failed: {str(e)}"
        )


def _generate_mock_factors(segment: str, scraped_content: List[Dict]) -> Dict[str, Any]:
    """
    Generate mock factor scores based on segment and content availability
    In production, these would be calculated from actual analysis
    """
    
    has_content = len(scraped_content) > 0
    base_score = 0.65 if has_content else 0.50
    
    segment_factors = {
        'market': {
            'F1': {'value': base_score + 0.05, 'confidence': 0.72, 'name': 'Market Timing'},
            'F2': {'value': base_score + 0.08, 'confidence': 0.68, 'name': 'Market Access'},
            'F3': {'value': base_score, 'confidence': 0.70, 'name': 'Market Dynamics'},
            'F4': {'value': base_score + 0.10, 'confidence': 0.75, 'name': 'Regulatory Environment'},
            'F16': {'value': base_score + 0.12, 'confidence': 0.70, 'name': 'Market Size'},
            'F19': {'value': base_score + 0.15, 'confidence': 0.73, 'name': 'Market Growth'}
        },
        'consumer': {
            'F11': {'value': base_score + 0.10, 'confidence': 0.70, 'name': 'Consumer Demand'},
            'F12': {'value': base_score + 0.08, 'confidence': 0.68, 'name': 'Willingness to Pay'},
            'F13': {'value': base_score, 'confidence': 0.65, 'name': 'Customer Loyalty'},
            'F14': {'value': base_score + 0.05, 'confidence': 0.67, 'name': 'Purchase Frequency'},
            'F15': {'value': base_score + 0.12, 'confidence': 0.72, 'name': 'Adoption Readiness'},
            'F20': {'value': base_score + 0.07, 'confidence': 0.69, 'name': 'Target Audience Fit'}
        },
        'product': {
            'F6': {'value': base_score + 0.15, 'confidence': 0.78, 'name': 'Product Quality'},
            'F7': {'value': base_score + 0.10, 'confidence': 0.70, 'name': 'Differentiation'},
            'F8': {'value': base_score + 0.12, 'confidence': 0.72, 'name': 'Technical Feasibility'},
            'F9': {'value': base_score + 0.08, 'confidence': 0.68, 'name': 'Scalability'},
            'F10': {'value': base_score + 0.18, 'confidence': 0.75, 'name': 'Innovation Potential'}
        },
        'brand': {
            'F21': {'value': base_score + 0.08, 'confidence': 0.67, 'name': 'Brand Positioning'},
            'F22': {'value': base_score + 0.10, 'confidence': 0.70, 'name': 'Brand Equity'},
            'F23': {'value': base_score + 0.05, 'confidence': 0.65, 'name': 'Virality/Cultural Impact'},
            'F24': {'value': base_score + 0.12, 'confidence': 0.73, 'name': 'Brand Trust'},
            'F25': {'value': base_score, 'confidence': 0.68, 'name': 'Brand Recognition'}
        },
        'experience': {
            'F26': {'value': base_score + 0.10, 'confidence': 0.70, 'name': 'User Engagement'},
            'F27': {'value': base_score + 0.08, 'confidence': 0.72, 'name': 'Customer Satisfaction'},
            'F28': {'value': base_score + 0.12, 'confidence': 0.75, 'name': 'User Interface Quality'}
        }
    }
    
    return segment_factors.get(segment, segment_factors['market'])

