# backend/app/api/v3/data_driven_results_simple.py

"""
Simplified data-driven results API that works with existing services
Bridges to existing results API until full persistence layer is implemented
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database_session import get_db
from app.services.results_analysis_engine import analysis_engine
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/segment/{session_id}/{segment}")
async def get_segment_results(
    session_id: str,
    segment: str,
    regenerate: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get segment results - bridges to existing results API
    """
    
    try:
        logger.info(f"[Data-Driven Bridge] Getting segment results for {session_id}, {segment}")
        
        # Fetch complete analysis from existing engine
        complete_analysis = await analysis_engine.generate_complete_analysis(session_id)
        
        # Get the specific segment
        segment_data = None
        if segment == "market":
            segment_data = complete_analysis.market
        elif segment == "consumer":
            segment_data = complete_analysis.consumer
        elif segment == "product":
            segment_data = complete_analysis.product
        elif segment == "brand":
            segment_data = complete_analysis.brand
        elif segment == "experience":
            segment_data = complete_analysis.experience
        else:
            raise HTTPException(status_code=400, detail=f"Invalid segment: {segment}")
        
        if not segment_data:
            logger.warning(f"No results found for {session_id}, {segment}")
            raise HTTPException(status_code=404, detail=f"No results found for session {session_id}, segment {segment}")
        
        # Convert to dict for transformation
        results = segment_data.dict() if hasattr(segment_data, 'dict') else segment_data
        
        # Transform to data-driven format
        transformed_results = {
            "session_id": session_id,
            "segment": segment,
            "factors": results.get("factors", {}),
            "patterns": results.get("patterns", []),
            "scenarios": results.get("monte_carlo_scenarios", []),
            "personas": results.get("personas", []),
            "rich_content": {
                "opportunities": results.get("opportunities", []),
                "competitor_analysis": results.get("competitor_analysis", {}),
                "market_share": results.get("market_share", {}),
                "insights": results.get("insights", []),
                "recommendations": results.get("recommendations", [])
            },
            "loaded_from_cache": False,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "existing_api_bridge"
        }
        
        logger.info(f"[Data-Driven Bridge] Successfully fetched {segment} results for {session_id}")
        return transformed_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in segment results: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/generate/{session_id}/{topic}")
async def trigger_results_generation(
    session_id: str,
    topic: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger results generation - simplified version
    """
    
    try:
        logger.info(f"Triggering generation for {session_id}, {topic}")
        
        # For now, just return success
        # This will be enhanced with actual generation logic
        
        return {
            "status": "accepted",
            "message": "Results generation request received",
            "session_id": session_id,
            "topic": topic,
            "note": "Generation logic will be implemented after database migration"
        }
        
    except Exception as e:
        logger.error(f"Error triggering generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/status/{session_id}")
async def get_generation_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get generation status - lightweight check without heavy processing"""
    
    try:
        logger.info(f"[Data-Driven Bridge] Getting status for {session_id}")
        
        # Quick check: just verify if v2 results exist without generating analysis
        from app.core.database_config import db_manager
        
        try:
            conn = await db_manager.get_connection()
            
            # Check if session has any analysis results (more flexible)
            query = """
                SELECT COUNT(*) as count, 
                       array_agg(DISTINCT analysis_type) as types
                FROM analysis_results 
                WHERE session_id = $1 
                AND result_data IS NOT NULL
            """
            
            result = await conn.fetchrow(query, session_id)
            
            if result and result['count'] > 0:
                analysis_types = result['types'] or []
                logger.info(f"[Data-Driven Bridge] Found {result['count']} analysis results for {session_id}: {analysis_types}")
                return {
                    "session_id": session_id,
                    "status": "completed",
                    "message": f"Results available ({result['count']} analysis types: {', '.join(analysis_types)})",
                    "progress_percentage": 100,
                    "current_stage": "completed",
                    "completed_segments": 5,
                    "total_segments": 5
                }
            else:
                logger.info(f"[Data-Driven Bridge] No analysis results found for {session_id}")
                return {
                    "session_id": session_id,
                    "status": "pending",
                    "message": "Results not yet available. Please complete scoring first.",
                    "progress_percentage": 0,
                    "current_stage": "waiting_for_scoring",
                    "completed_segments": 0,
                    "total_segments": 5
                }
                
        except Exception as db_error:
            logger.error(f"Database check failed: {db_error}")
            # Fallback to pending status
            return {
                "session_id": session_id,
                "status": "pending",
                "message": "Unable to verify results status",
                "progress_percentage": 0,
                "current_stage": "unknown",
                "completed_segments": 0,
                "total_segments": 5
            }
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the API is working"""
    
    return {
        "status": "success",
        "message": "Data-driven results API is working",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0-simple"
    }
