"""
API endpoints for migrated v2 data - CORRECTED VERSION
Integrates with existing Validatus2 API structure
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Optional
import json
import logging
from pathlib import Path

from ...services.migrated_data_service import MigratedDataService
from ...models.analysis_models import MigratedSessionInfo, MigratedTopicInfo

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/migrated/topics", tags=["migrated_data"])
async def get_migrated_topics():
    """Get list of migrated topics"""
    try:
        service = MigratedDataService()
        return await service.get_available_topics()
    except Exception as e:
        logger.error(f"Error fetching migrated topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migrated/sessions/{session_id}", tags=["migrated_data"])
async def get_migrated_session(session_id: str):
    """Get migrated session details"""
    try:
        service = MigratedDataService()
        session = await service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migrated/results/{session_id}", tags=["migrated_data"])
async def get_migrated_results(session_id: str):
    """Get migrated analysis results"""
    try:
        service = MigratedDataService()
        results = await service.get_analysis_results(session_id)
        if not results:
            raise HTTPException(status_code=404, detail="Results not found")
        return results
    except Exception as e:
        logger.error(f"Error fetching results for {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migrated/vector/{topic}/query", tags=["migrated_data"])
async def query_migrated_vector_store(
    topic: str,
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum results to return")
):
    """Query migrated vector store"""
    try:
        service = MigratedDataService()
        results = await service.query_vector_store(topic, query, max_results)
        return results
    except Exception as e:
        logger.error(f"Error querying vector store for {topic}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migrated/evidence/{topic}", tags=["migrated_data"])
async def get_migrated_evidence(
    topic: str,
    layer: Optional[str] = Query(None, description="Specific layer filter")
):
    """Get evidence data for migrated topic"""
    try:
        service = MigratedDataService()
        evidence = await service.get_evidence_data(topic, layer)
        return evidence
    except Exception as e:
        logger.error(f"Error fetching evidence for {topic}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migrated/action-layer/{session_id}", tags=["migrated_data"])
async def get_migrated_action_layer(session_id: str):
    """Get action layer data for migrated session"""
    try:
        service = MigratedDataService()
        action_data = await service.get_action_layer_data(session_id)
        if not action_data:
            raise HTTPException(status_code=404, detail="Action layer data not found")
        return action_data
    except Exception as e:
        logger.error(f"Error fetching action layer data for {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
