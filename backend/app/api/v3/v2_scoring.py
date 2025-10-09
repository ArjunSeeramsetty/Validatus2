"""
Validatus v2.0 Scoring API
Complete 5-segment, 28-factor, 210-layer strategic analysis
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path
from typing import Optional, List, Dict, Any
import logging
import json
from datetime import datetime, timezone

from ...core.aliases_config import aliases_config
from ...core.database_config import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["v2-scoring"])

# Lazy load v2 orchestrator to avoid import errors
v2_orchestrator = None

def _init_v2_services():
    """Lazy initialize v2 services"""
    global v2_orchestrator
    
    if v2_orchestrator is None:
        try:
            from ...services.v2_strategic_analysis_orchestrator import V2StrategicAnalysisOrchestrator
            v2_orchestrator = V2StrategicAnalysisOrchestrator()
            logger.info("✅ V2 Orchestrator loaded")
        except Exception as e:
            logger.warning(f"V2 Orchestrator not available: {e}")

@router.get("/configuration")
async def get_v2_configuration():
    """
    Get complete v2.0 configuration with all mappings
    Returns structure of 5 segments, 28 factors, 210 layers
    """
    try:
        if not aliases_config:
            raise HTTPException(status_code=500, detail="Configuration not available")
        
        summary = aliases_config.get_configuration_summary()
        validation = aliases_config.validate_configuration()
        
        return {
            "success": True,
            "version": "2.0",
            "structure": {
                "segments": 5,
                "factors": 28,
                "layers": 210,
                "distribution": "30+50+50+50+30"
            },
            "validation": validation,
            "segments": {
                segment_id: aliases_config.get_segment_name(segment_id)
                for segment_id in aliases_config.get_all_segment_ids()
            },
            "configuration_summary": summary
        }
    except Exception as e:
        logger.error(f"Failed to get v2 configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/analyze")
async def execute_v2_analysis(
    session_id: str = Path(..., description="Session ID"),
    background_tasks: BackgroundTasks = None,
    user_id: Optional[str] = Query(None, description="User ID (optional)")
):
    """
    Execute complete v2.0 strategic analysis
    - Scores 210 layers using expert personas + Gemini LLM
    - Calculates 28 strategic factors
    - Analyzes 5 intelligence segments
    - Generates scenarios
    """
    try:
        _init_v2_services()
        
        # Validate session exists and has content
        connection = await db_manager.get_connection()
        
        if user_id:
            topic_query = "SELECT * FROM topics WHERE session_id = $1 AND user_id = $2"
            topic_row = await connection.fetchrow(topic_query, session_id, user_id)
        else:
            topic_query = "SELECT * FROM topics WHERE session_id = $1"
            topic_row = await connection.fetchrow(topic_query, session_id)
        
        if not topic_row:
            raise HTTPException(status_code=404, detail="Topic/Session not found")
        
        # Get scraped content for analysis
        content_query = """
        SELECT url, title, content, metadata
        FROM scraped_content
        WHERE session_id = $1 AND processing_status = 'processed'
        ORDER BY scraped_at DESC
        """
        content_rows = await connection.fetch(content_query, session_id)
        
        if not content_rows:
            return {
                "success": False,
                "error": "No processed content available for analysis",
                "session_id": session_id,
                "recommendation": "Please scrape content first in Content Tab"
            }
        
        # Prepare topic knowledge
        topic_knowledge = {
            "session_id": session_id,
            "topic": topic_row['topic'],
            "description": topic_row['description'],
            "content_items": [
                {
                    "url": row['url'],
                    "title": row['title'] or "Untitled",
                    "content": row['content'] or "",
                    "quality_score": json.loads(row['metadata']).get('quality_score', 0.5) if row['metadata'] else 0.5
                }
                for row in content_rows
            ]
        }
        
        logger.info(f"🚀 Starting v2.0 analysis for {session_id} with {len(content_rows)} documents")
        
        # Check if orchestrator is available
        if not v2_orchestrator:
            return {
                "success": False,
                "error": "V2 Orchestrator not available",
                "session_id": session_id,
                "note": "This requires full v2.0 services to be deployed"
            }
        
        # Execute complete analysis
        analysis_results = await v2_orchestrator.execute_complete_analysis(
            session_id, topic_knowledge
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "analysis_type": "validatus_v2_complete",
            "results_summary": {
                "overall_score": analysis_results['overall_business_case_score'],
                "confidence": analysis_results['overall_confidence'],
                "layers_analyzed": analysis_results['summary']['layers_analyzed'],
                "factors_calculated": analysis_results['summary']['factors_calculated'],
                "segments_evaluated": analysis_results['summary']['segments_evaluated'],
                "scenarios_generated": analysis_results['summary']['scenarios_generated'],
                "processing_time": analysis_results['processing_time_seconds'],
                "content_items": len(content_rows)
            },
            "message": f"v2.0 Analysis completed: {analysis_results['summary']['layers_analyzed']} layers analyzed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"v2.0 analysis failed for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/results")
async def get_v2_results(session_id: str):
    """
    Get complete v2.0 analysis results
    Returns all layer scores, factor calculations, and segment analyses
    """
    try:
        connection = await db_manager.get_connection()
        
        # Get main analysis record
        analysis_query = """
        SELECT * FROM v2_analysis_results
        WHERE session_id = $1
        ORDER BY created_at DESC
        LIMIT 1
        """
        analysis_row = await connection.fetchrow(analysis_query, session_id)
        
        if not analysis_row:
            return {
                "has_results": False,
                "message": "No v2.0 analysis results found",
                "session_id": session_id,
                "recommendation": "Run v2.0 analysis first"
            }
        
        # Get detailed results from full_results JSONB
        full_results = analysis_row['full_results']
        
        return {
            "has_results": True,
            "session_id": session_id,
            "analyzed_at": analysis_row['created_at'].isoformat(),
            "results": {
                "overall_score": float(analysis_row['overall_business_case_score']),
                "confidence": float(analysis_row['overall_confidence']),
                "summary": analysis_row['analysis_summary'],
                "layer_scores": full_results.get('layer_scores', []),
                "factor_calculations": full_results.get('factor_calculations', []),
                "segment_analyses": full_results.get('segment_analyses', []),
                "scenarios": full_results.get('scenarios', [])
            },
            "metadata": {
                "layers_analyzed": analysis_row['layers_analyzed'],
                "factors_calculated": analysis_row['factors_calculated'],
                "segments_evaluated": analysis_row['segments_evaluated'],
                "processing_time": float(analysis_row['processing_time_seconds']),
                "version": "2.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get v2.0 results for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/segment/{segment_id}")
async def get_segment_details(
    session_id: str = Path(..., description="Session ID"),
    segment_id: str = Path(..., description="Segment ID (S1-S5)")
):
    """Get detailed results for specific intelligence segment"""
    try:
        if not aliases_config:
            raise HTTPException(status_code=500, detail="Configuration not available")
        
        # Validate segment ID
        segment_name = aliases_config.get_segment_name(segment_id)
        if not segment_name:
            raise HTTPException(status_code=400, detail=f"Invalid segment ID: {segment_id}")
        
        connection = await db_manager.get_connection()
        
        # Get segment analysis
        segment_query = """
        SELECT * FROM segment_analysis
        WHERE session_id = $1 AND segment_id = $2
        """
        segment_row = await connection.fetchrow(segment_query, session_id, segment_id)
        
        if not segment_row:
            return {
                "has_results": False,
                "message": f"No analysis found for segment {segment_id}",
                "session_id": session_id,
                "segment_id": segment_id
            }
        
        # Get factors for this segment
        factor_ids = aliases_config.get_factors_for_segment(segment_id)
        
        factor_query = """
        SELECT * FROM factor_calculations
        WHERE session_id = $1 AND factor_id = ANY($2)
        ORDER BY factor_id
        """
        factor_rows = await connection.fetch(factor_query, session_id, factor_ids)
        
        # Get layer scores for this segment's factors
        all_layer_ids = []
        for factor_id in factor_ids:
            layer_ids = aliases_config.get_layers_for_factor(factor_id)
            all_layer_ids.extend(layer_ids)
        
        layer_query = """
        SELECT * FROM layer_scores
        WHERE session_id = $1 AND layer_id = ANY($2)
        ORDER BY layer_id
        """
        layer_rows = await connection.fetch(layer_query, session_id, all_layer_ids) if all_layer_ids else []
        
        return {
            "has_results": True,
            "session_id": session_id,
            "segment": {
                "id": segment_id,
                "name": segment_name,
                "attractiveness": float(segment_row['attractiveness_score']),
                "competitive_intensity": float(segment_row['competitive_intensity']),
                "market_size": float(segment_row['market_size_score']),
                "growth_potential": float(segment_row['growth_potential']),
                "overall_score": float(segment_row['overall_segment_score']),
                "insights": segment_row['key_insights'],
                "risks": segment_row['risk_factors'],
                "opportunities": segment_row['opportunities'],
                "recommendations": segment_row['recommendations']
            },
            "factors": [
                {
                    "id": row['factor_id'],
                    "name": aliases_config.get_factor_name(row['factor_id']),
                    "value": float(row['calculated_value']),
                    "confidence": float(row['confidence_score']),
                    "input_layers": row['input_layer_count']
                }
                for row in factor_rows
            ],
            "layers": [
                {
                    "id": row['layer_id'],
                    "name": aliases_config.get_layer_name(row['layer_id']),
                    "score": float(row['score']),
                    "confidence": float(row['confidence']),
                    "insights": row['key_insights']
                }
                for row in layer_rows
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get segment details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_v2_status():
    """Get v2.0 system status and configuration"""
    try:
        _init_v2_services()
        
        return {
            "success": True,
            "version": "2.0",
            "status": {
                "configuration_loaded": aliases_config is not None,
                "orchestrator_available": v2_orchestrator is not None,
                "gemini_client_available": False  # Will check in next version
            },
            "configuration": {
                "segments": 5,
                "factors": 28,
                "layers": 210
            },
            "message": "Validatus v2.0 Strategic Analysis API"
        }
    except Exception as e:
        logger.error(f"Failed to get v2 status: {e}")
        return {
            "success": False,
            "error": str(e)
        }

