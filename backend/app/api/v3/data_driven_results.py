# backend/app/api/v3/data_driven_results.py

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database_session import get_db
from app.services.results_generation_orchestrator import ResultsGenerationOrchestrator
from app.services.results_persistence_service import ResultsPersistenceService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3/data-driven-results", tags=["data-driven-results"])

@router.get("/segment/{session_id}/{segment}")
async def get_segment_results(
    session_id: str,
    segment: str,
    regenerate: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get segment results - loads from database if exists, generates if not
    100% data-driven, NO MOCK DATA
    """
    
    try:
        orchestrator = ResultsGenerationOrchestrator(db)
        persistence = ResultsPersistenceService(db)
        
        # Check if results exist and are complete
        if persistence.results_exist(session_id) and not regenerate:
            # Load from database (instant)
            logger.info(f"Loading persisted results for session {session_id}, segment {segment}")
            return orchestrator.load_persisted_results(session_id, segment)
        
        else:
            # Check generation status
            status = persistence.get_generation_status(session_id)
            
            if status and status['status'] == 'processing':
                # Results being generated
                logger.info(f"Results generation in progress for session {session_id}")
                return {
                    "status": "processing",
                    "message": "Results are being generated",
                    "progress": status['progress_percentage'],
                    "current_stage": status['current_stage'],
                    "session_id": session_id,
                    "segment": segment
                }
            
            else:
                # Results don't exist - return error
                logger.warning(f"No results found for session {session_id}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Results not found for session {session_id}. Trigger results generation first."
                )
    
    except ValueError as e:
        logger.error(f"Value error for session {session_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error loading results for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading results: {str(e)}")

@router.post("/generate/{session_id}/{topic}")
async def trigger_results_generation(
    session_id: str,
    topic: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger async results generation for all segments
    Called automatically after scoring completion
    """
    
    try:
        orchestrator = ResultsGenerationOrchestrator(db)
        
        # Add to background tasks
        background_tasks.add_task(
            orchestrator.generate_and_persist_complete_results,
            session_id,
            topic
        )
        
        logger.info(f"Started results generation for session {session_id}, topic {topic}")
        
        return {
            "status": "started",
            "message": "Results generation started",
            "session_id": session_id,
            "topic": topic
        }
        
    except Exception as e:
        logger.error(f"Error starting generation for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting generation: {str(e)}")

@router.get("/status/{session_id}")
async def get_generation_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get results generation status"""
    
    try:
        persistence = ResultsPersistenceService(db)
        status = persistence.get_generation_status(session_id)
        
        if not status:
            logger.warning(f"No generation status found for session {session_id}")
            raise HTTPException(status_code=404, detail=f"No generation status found for session {session_id}")
        
        logger.info(f"Retrieved generation status for session {session_id}: {status['status']}")
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@router.get("/complete/{session_id}")
async def get_complete_results(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get complete results for all segments"""
    
    try:
        persistence = ResultsPersistenceService(db)
        
        # Check if results exist
        if not persistence.results_exist(session_id):
            raise HTTPException(
                status_code=404,
                detail=f"Complete results not found for session {session_id}"
            )
        
        # Load all segments
        segments = ['consumer', 'market', 'product', 'brand', 'experience']
        complete_results = {
            'session_id': session_id,
            'segments': {}
        }
        
        for segment in segments:
            try:
                factors = persistence.get_factors(session_id, segment)
                patterns = persistence.get_pattern_matches(session_id, segment)
                scenarios = persistence.get_monte_carlo_scenarios(session_id, segment)
                
                segment_data = {
                    'factors': factors,
                    'patterns': patterns,
                    'scenarios': scenarios
                }
                
                # Add segment-specific data
                if segment == 'consumer':
                    segment_data['personas'] = persistence.get_personas(session_id)
                elif segment in ['product', 'brand', 'experience']:
                    content_type = f'{segment}_intelligence'
                    segment_data['rich_content'] = persistence.get_rich_content(session_id, segment, content_type) or {}
                
                complete_results['segments'][segment] = segment_data
                
            except Exception as e:
                logger.warning(f"Error loading segment {segment} for session {session_id}: {str(e)}")
                complete_results['segments'][segment] = {
                    'error': f"Failed to load {segment} data: {str(e)}"
                }
        
        logger.info(f"Successfully loaded complete results for session {session_id}")
        return complete_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading complete results for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading complete results: {str(e)}")

@router.delete("/clear/{session_id}")
async def clear_results(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Clear all results for a session (for testing/regeneration)"""
    
    try:
        persistence = ResultsPersistenceService(db)
        
        # Clear all data for this session
        from app.models.results_persistence_models import (
            ComputedFactors, PatternMatches, MonteCarloScenarios,
            ConsumerPersonas, SegmentRichContent, ResultsGenerationStatus
        )
        
        # Delete all records for this session
        db.query(ComputedFactors).filter(ComputedFactors.session_id == session_id).delete()
        db.query(PatternMatches).filter(PatternMatches.session_id == session_id).delete()
        db.query(MonteCarloScenarios).filter(MonteCarloScenarios.session_id == session_id).delete()
        db.query(ConsumerPersonas).filter(ConsumerPersonas.session_id == session_id).delete()
        db.query(SegmentRichContent).filter(SegmentRichContent.session_id == session_id).delete()
        db.query(ResultsGenerationStatus).filter(ResultsGenerationStatus.session_id == session_id).delete()
        
        db.commit()
        
        logger.info(f"Cleared all results for session {session_id}")
        
        return {
            "status": "cleared",
            "message": f"All results cleared for session {session_id}",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error clearing results for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing results: {str(e)}")
