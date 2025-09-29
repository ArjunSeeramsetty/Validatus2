"""
Pergola Intelligence API Endpoints
Dedicated router for Pergola Intelligence functionality
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from ...services.pergola_intelligence_service import PergolaIntelligenceService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v3/pergola-intelligence", tags=["pergola-intelligence"])

# Initialize intelligence service
intelligence_service = PergolaIntelligenceService()

@router.get("/")
async def get_pergola_intelligence_dashboard():
    """Get main pergola intelligence dashboard data"""
    try:
        intelligence_data = await intelligence_service.get_market_intelligence()
        
        return {
            "status": "success",
            "data": intelligence_data,
            "message": "Pergola intelligence dashboard loaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get pergola intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_pergola_intelligence(query: str, max_results: int = 10):
    """Search through pergola intelligence data"""
    try:
        results = await intelligence_service.search_intelligence(query, max_results)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Intelligence search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-insights")
async def get_market_insights():
    """Get detailed market insights"""
    try:
        intelligence_data = await intelligence_service.get_market_intelligence()
        
        return {
            "status": "success",
            "market_insights": intelligence_data.get("market_insights", {}),
            "message": "Market insights retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get market insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/competitive-landscape")
async def get_competitive_landscape():
    """Get competitive landscape analysis"""
    try:
        intelligence_data = await intelligence_service.get_market_intelligence()
        
        return {
            "status": "success",
            "competitive_landscape": intelligence_data.get("competitive_landscape", {}),
            "message": "Competitive landscape retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get competitive landscape: {e}")
        raise HTTPException(status_code=500, detail=str(e))
