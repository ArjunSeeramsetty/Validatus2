# backend/app/api/v3/results.py

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import logging

from ...services.analysis_results_manager import AnalysisResultsManager
from ...services.analysis_session_manager import AnalysisSessionManager
from ...middleware.monitoring import performance_monitor

router = APIRouter(prefix="/api/v3/results", tags=["results"])
logger = logging.getLogger(__name__)

results_manager = AnalysisResultsManager()
session_manager = AnalysisSessionManager()

@router.get("/sessions/{session_id}/complete")
@performance_monitor
async def get_complete_analysis_results(session_id: str):
    """Get complete analysis results with all components"""
    try:
        results = await results_manager.get_analysis_results(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "results": results
        }
    except Exception as e:
        logger.error(f"Failed to get complete results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{user_id}")
@performance_monitor
async def get_dashboard_summary(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None)
):
    """Get dashboard summary for user"""
    try:
        summaries = await results_manager.get_results_summary(user_id, limit)
        
        if status:
            summaries = [s for s in summaries if s.status == status]
        
        return {
            "success": True,
            "user_id": user_id,
            "summaries": summaries,
            "total_count": len(summaries)
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/export")
@performance_monitor
async def export_analysis_results(
    session_id: str,
    export_request: dict,
    background_tasks: BackgroundTasks
):
    """Export analysis results in specified format"""
    try:
        format_type = export_request.get('format', 'json').lower()
        user_id = export_request.get('user_id')
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        # Start export in background
        background_tasks.add_task(
            results_manager.export_results,
            session_id, format_type, user_id
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "format": format_type,
            "status": "export_started",
            "message": "Export process initiated"
        }
    except Exception as e:
        logger.error(f"Failed to initiate export: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/progress")
@performance_monitor
async def get_real_time_progress(session_id: str):
    """Get real-time progress for analysis session"""
    try:
        progress = await results_manager.get_real_time_progress(session_id)
        return {
            "success": True,
            "progress": progress
        }
    except Exception as e:
        logger.error(f"Failed to get progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/trends")
@performance_monitor
async def get_analytics_trends(
    user_id: str,
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$")
):
    """Get analytics trends for dashboard"""
    try:
        # Mock trends data for now
        trends = {
            "timeframe": timeframe,
            "total_analyses": 25,
            "average_score": 0.78,
            "completion_rate": 0.95,
            "top_topics": ["AI", "Machine Learning", "Data Science"],
            "score_trends": [
                {"date": "2024-01-01", "score": 0.75},
                {"date": "2024-01-02", "score": 0.78},
                {"date": "2024-01-03", "score": 0.82}
            ]
        }
        
        return {
            "success": True,
            "trends": trends,
            "timeframe": timeframe
        }
    except Exception as e:
        logger.error(f"Failed to get analytics trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))
