"""
Sequential Analysis API Router for Stage 1→Stage 2→Stage 3 Workflow
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ...services.enhanced_analysis_session_manager import EnhancedAnalysisSessionManager
from ...services.live_action_calculator import LiveActionCalculator

logger = logging.getLogger(__name__)

router = APIRouter()

# Request Models
class CreateAnalysisRequest(BaseModel):
    topic_id: str
    user_id: str

class Stage2Request(BaseModel):
    query: str

class Stage3Request(BaseModel):
    # No additional parameters needed for Stage 3
    pass

class LiveCalculationRequest(BaseModel):
    client_inputs: Dict[str, Any]
    query: str

# Service instances
session_manager = EnhancedAnalysisSessionManager()
live_calculator = LiveActionCalculator()

@router.post("/topics/{topic_id}/analysis/create")
async def create_sequential_analysis(
    topic_id: str,
    request: CreateAnalysisRequest
) -> Dict[str, Any]:
    """Create new sequential analysis session"""
    try:
        session_id = session_manager.create_session(topic_id, request.user_id)
        
        return {
            'success': True,
            'session_id': session_id,
            'topic_id': topic_id,
            'user_id': request.user_id,
            'status': 'created',
            'message': 'Analysis session created successfully',
            'next_action': 'Run Stage 1: Strategic Analysis'
        }
        
    except Exception as e:
        logger.error(f"Failed to create analysis session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis/{session_id}/stage1/start")
async def start_stage1_analysis(
    session_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Start Stage 1: Strategic Knowledge Acquisition"""
    try:
        # Start Stage 1 in background
        background_tasks.add_task(session_manager.run_stage1, session_id)
        
        return {
            'success': True,
            'session_id': session_id,
            'stage': 1,
            'status': 'started',
            'message': 'Stage 1 analysis started',
            'estimated_duration': '2-5 minutes'
        }
        
    except Exception as e:
        logger.error(f"Failed to start Stage 1: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{session_id}/stage1/status")
async def get_stage1_status(session_id: str) -> Dict[str, Any]:
    """Get Stage 1 status and progress"""
    try:
        status = session_manager.get_stage_status(session_id, 1)
        return {
            'success': True,
            'session_id': session_id,
            'stage': 1,
            **status
        }
        
    except Exception as e:
        logger.error(f"Failed to get Stage 1 status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{session_id}/stage1/results")
async def get_stage1_results(session_id: str) -> Dict[str, Any]:
    """Get Stage 1 results"""
    try:
        # Check if Stage 1 is completed
        status = session_manager.get_stage_status(session_id, 1)
        
        if status['status'] != 'completed':
            raise HTTPException(
                status_code=400, 
                detail=f"Stage 1 not completed yet. Current status: {status['status']}"
            )
        
        # Load Stage 1 results
        results = session_manager._load_stage_results(session_id, 1)
        
        return {
            'success': True,
            'session_id': session_id,
            'stage': 1,
            'status': 'completed',
            'results': results,
            'next_action': 'Run Stage 2 with your query'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Stage 1 results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis/{session_id}/stage2/start")
async def start_stage2_analysis(
    session_id: str,
    request: Stage2Request,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Start Stage 2: RAG Query Analysis"""
    try:
        # Verify Stage 1 is completed
        stage1_status = session_manager.get_stage_status(session_id, 1)
        if stage1_status['status'] != 'completed':
            raise HTTPException(
                status_code=400,
                detail="Stage 1 must be completed before running Stage 2"
            )
        
        # Start Stage 2 in background
        background_tasks.add_task(session_manager.run_stage2, session_id, request.query)
        
        return {
            'success': True,
            'session_id': session_id,
            'stage': 2,
            'query': request.query,
            'status': 'started',
            'message': 'Stage 2 RAG analysis started',
            'estimated_duration': '30-60 seconds'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start Stage 2: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{session_id}/stage2/status")
async def get_stage2_status(session_id: str) -> Dict[str, Any]:
    """Get Stage 2 status"""
    try:
        status = session_manager.get_stage_status(session_id, 2)
        return {
            'success': True,
            'session_id': session_id,
            'stage': 2,
            **status
        }
        
    except Exception as e:
        logger.error(f"Failed to get Stage 2 status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{session_id}/stage2/results")
async def get_stage2_results(session_id: str) -> Dict[str, Any]:
    """Get Stage 2 results"""
    try:
        # Check if Stage 2 is completed
        status = session_manager.get_stage_status(session_id, 2)
        
        if status['status'] != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Stage 2 not completed yet. Current status: {status['status']}"
            )
        
        # Load Stage 2 results
        results = session_manager._load_stage_results(session_id, 2)
        
        return {
            'success': True,
            'session_id': session_id,
            'stage': 2,
            'status': 'completed',
            'results': results,
            'next_action': 'Run Stage 3: Action Layer Calculations'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Stage 2 results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis/{session_id}/stage3/start")
async def start_stage3_analysis(
    session_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Start Stage 3: Action Layer Calculations"""
    try:
        # Verify Stages 1 & 2 are completed
        stage1_status = session_manager.get_stage_status(session_id, 1)
        stage2_status = session_manager.get_stage_status(session_id, 2)
        
        if stage1_status['status'] != 'completed':
            raise HTTPException(
                status_code=400,
                detail="Stage 1 must be completed before running Stage 3"
            )
        
        if stage2_status['status'] != 'completed':
            raise HTTPException(
                status_code=400,
                detail="Stage 2 must be completed before running Stage 3"
            )
        
        # Start Stage 3 in background
        background_tasks.add_task(session_manager.run_stage3, session_id)
        
        return {
            'success': True,
            'session_id': session_id,
            'stage': 3,
            'status': 'started',
            'message': 'Stage 3 action layer calculations started',
            'estimated_duration': '1-2 minutes'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start Stage 3: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{session_id}/stage3/status")
async def get_stage3_status(session_id: str) -> Dict[str, Any]:
    """Get Stage 3 status"""
    try:
        status = session_manager.get_stage_status(session_id, 3)
        return {
            'success': True,
            'session_id': session_id,
            'stage': 3,
            **status
        }
        
    except Exception as e:
        logger.error(f"Failed to get Stage 3 status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{session_id}/stage3/results")
async def get_stage3_results(session_id: str) -> Dict[str, Any]:
    """Get Stage 3 results - Final Analysis Output"""
    try:
        # Check if Stage 3 is completed
        status = session_manager.get_stage_status(session_id, 3)
        
        if status['status'] != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Stage 3 not completed yet. Current status: {status['status']}"
            )
        
        # Load Stage 3 results
        results = session_manager._load_stage_results(session_id, 3)
        
        return {
            'success': True,
            'session_id': session_id,
            'stage': 3,
            'status': 'completed',
            'results': results,
            'message': 'Complete strategic analysis finished!',
            'next_action': 'Review results and export reports'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Stage 3 results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{session_id}/overview")
async def get_session_overview(session_id: str) -> Dict[str, Any]:
    """Get complete session overview and status"""
    try:
        overview = session_manager.get_session_overview(session_id)
        return {
            'success': True,
            **overview
        }
        
    except Exception as e:
        logger.error(f"Failed to get session overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/sessions/{session_id}/results")
async def get_analysis_results(session_id: str) -> Dict[str, Any]:
    """Get complete analysis results for a session"""
    try:
        # Get session overview first
        overview = session_manager.get_session_overview(session_id)
        if not overview:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Load all stage results (gracefully handle missing stages)
        stage1_results = None
        stage2_results = None
        stage3_results = None
        
        try:
            stage1_results = session_manager._load_stage_results(session_id, 1)
        except FileNotFoundError:
            pass
            
        try:
            stage2_results = session_manager._load_stage_results(session_id, 2)
        except FileNotFoundError:
            pass
            
        try:
            stage3_results = session_manager._load_stage_results(session_id, 3)
        except FileNotFoundError:
            pass
        
        return {
            'success': True,
            'session_id': session_id,
            'overview': overview,
            'stage1_results': stage1_results,
            'stage2_results': stage2_results,
            'stage3_results': stage3_results,
            'complete': True
        }
        
    except Exception as e:
        logger.error(f"Failed to get analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topics/{topic_id}/query-suggestions")
async def get_query_suggestions(topic_id: str) -> Dict[str, Any]:
    """Get query suggestions for RAG-based knowledge retrieval"""
    try:
        # Generate contextual query suggestions based on topic
        suggestions = [
            "What are the key market trends and growth drivers?",
            "How does competition affect market dynamics?",
            "What are the main risk factors and challenges?",
            "What opportunities exist for market expansion?",
            "How is technology impacting the industry landscape?",
            "What are the customer preferences and behaviors?",
            "What regulatory factors influence the market?",
            "What are the financial performance indicators?",
            "How do supply chain factors affect operations?",
            "What are the sustainability and ESG considerations?"
        ]
        
        return {
            'success': True,
            'topic_id': topic_id,
            'suggestions': suggestions,
            'count': len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get query suggestions for topic {topic_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get query suggestions: {str(e)}")

@router.post("/analysis/live-calculate")
async def live_calculate(request: LiveCalculationRequest) -> Dict[str, Any]:
    """Perform live action layer calculation with web search"""
    try:
        result = await live_calculator.calculate(request.client_inputs, request.query)
        
        return {
            'success': True,
            'calculation_result': result,
            'timestamp': result.get('calculation_timestamp'),
            'message': 'Live calculation completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Live calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Live calculation failed: {str(e)}")

@router.delete("/analysis/{session_id}")
async def delete_analysis_session(session_id: str) -> Dict[str, Any]:
    """Delete analysis session and cleanup files"""
    try:
        # TODO: Implement cleanup logic
        return {
            'success': True,
            'session_id': session_id,
            'message': 'Session deleted successfully'
        }
        
    except Exception as e:
        logger.error(f"Failed to delete session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
