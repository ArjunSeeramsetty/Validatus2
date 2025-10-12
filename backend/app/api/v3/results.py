"""
Results Analysis API Endpoints
Provides comprehensive analysis across Market, Consumer, Product, Brand, and Experience dimensions
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.models.analysis_results import (
    CompleteAnalysisResult,
    MarketAnalysisData,
    ConsumerAnalysisData,
    ProductAnalysisData,
    BrandAnalysisData,
    ExperienceAnalysisData
)
from app.services.results_analysis_engine import analysis_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3/results", tags=["results_analysis"])


@router.get("/complete/{session_id}", response_model=CompleteAnalysisResult)
async def get_complete_analysis(session_id: str):
    """
    Get complete analysis results for a topic across all dimensions:
    - Market Analysis
    - Consumer Analysis
    - Product Analysis
    - Brand Analysis
    - Experience Analysis
    """
    try:
        logger.info(f"Generating complete analysis for session {session_id}")
        result = await analysis_engine.generate_complete_analysis(session_id)
        return result
    except Exception as e:
        logger.error(f"Analysis generation failed for {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analysis: {str(e)}"
        )


@router.get("/market/{session_id}", response_model=MarketAnalysisData)
async def get_market_analysis(session_id: str):
    """
    Get market analysis specifically for a topic:
    - Competitor analysis
    - Market opportunities
    - Pricing & switching costs
    - Regulatory environment
    - Market size & growth
    - Market fit score
    """
    try:
        logger.info(f"Generating market analysis for session {session_id}")
        complete_analysis = await analysis_engine.generate_complete_analysis(session_id)
        return complete_analysis.market
    except Exception as e:
        logger.error(f"Market analysis failed for {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate market analysis: {str(e)}"
        )


@router.get("/consumer/{session_id}", response_model=ConsumerAnalysisData)
async def get_consumer_analysis(session_id: str):
    """
    Get consumer analysis specifically for a topic:
    - Consumer personas
    - Buying motivations
    - Challenges & pain points
    - Target audience definition
    - Consumer fit score
    """
    try:
        logger.info(f"Generating consumer analysis for session {session_id}")
        complete_analysis = await analysis_engine.generate_complete_analysis(session_id)
        return complete_analysis.consumer
    except Exception as e:
        logger.error(f"Consumer analysis failed for {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate consumer analysis: {str(e)}"
        )


@router.get("/product/{session_id}", response_model=ProductAnalysisData)
async def get_product_analysis(session_id: str):
    """
    Get product analysis specifically for a topic:
    - Product features analysis
    - Competitive positioning
    - Innovation opportunities
    - Technical specifications
    - Product roadmap
    - Product fit score
    """
    try:
        logger.info(f"Generating product analysis for session {session_id}")
        complete_analysis = await analysis_engine.generate_complete_analysis(session_id)
        return complete_analysis.product
    except Exception as e:
        logger.error(f"Product analysis failed for {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate product analysis: {str(e)}"
        )


@router.get("/brand/{session_id}", response_model=BrandAnalysisData)
async def get_brand_analysis(session_id: str):
    """
    Get brand analysis specifically for a topic:
    - Brand positioning
    - Brand perception metrics
    - Competitor brand analysis
    - Brand opportunities
    - Messaging strategy
    - Brand fit score
    """
    try:
        logger.info(f"Generating brand analysis for session {session_id}")
        complete_analysis = await analysis_engine.generate_complete_analysis(session_id)
        return complete_analysis.brand
    except Exception as e:
        logger.error(f"Brand analysis failed for {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate brand analysis: {str(e)}"
        )


@router.get("/experience/{session_id}", response_model=ExperienceAnalysisData)
async def get_experience_analysis(session_id: str):
    """
    Get experience analysis specifically for a topic:
    - User journey mapping
    - Customer touchpoints
    - Experience pain points
    - Experience metrics
    - Improvement recommendations
    - Experience fit score
    """
    try:
        logger.info(f"Generating experience analysis for session {session_id}")
        complete_analysis = await analysis_engine.generate_complete_analysis(session_id)
        return complete_analysis.experience
    except Exception as e:
        logger.error(f"Experience analysis failed for {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate experience analysis: {str(e)}"
        )


@router.get("/status/{session_id}")
async def get_analysis_status(session_id: str) -> Dict[str, Any]:
    """
    Get the status of analysis for a topic
    Checks if content is available and analysis can be generated
    """
    try:
        from app.core.database_config import DatabaseManager
        
        db_manager = DatabaseManager()
        connection = await db_manager.get_connection()
        
        # Check topic exists
        topic_query = "SELECT topic, status FROM topics WHERE session_id = $1"
        topic_row = await connection.fetchrow(topic_query, session_id)
        
        if not topic_row:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Check content availability
        content_query = """
        SELECT COUNT(*) as content_count
        FROM scraped_content
        WHERE session_id = $1
        AND processing_status = 'completed'
        AND LENGTH(TRIM(COALESCE(content, ''))) > 100
        """
        content_row = await connection.fetchrow(content_query, session_id)
        
        content_count = content_row['content_count'] if content_row else 0
        
        return {
            "session_id": session_id,
            "topic": topic_row['topic'],
            "status": topic_row['status'],
            "content_items": content_count,
            "analysis_ready": content_count > 0,
            "recommended_action": "Run analysis" if content_count > 0 else "Scrape content first"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed for {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check analysis status: {str(e)}"
        )
