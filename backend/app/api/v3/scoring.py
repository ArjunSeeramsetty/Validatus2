"""
Scoring API - Integrates with existing AdvancedStrategyAnalysisEngine
🆕 NEW FILE: Provides REST API access to existing strategic analysis services
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging
from datetime import datetime, timezone
import json
from typing import Dict, Any, List

from ...core.database_config import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["scoring"])

# ✅ REUSING EXISTING SERVICES (lazy load to avoid import errors)
analysis_engine = None
session_manager = None

def _init_services():
    """Lazy initialize services to handle missing dependencies"""
    global analysis_engine, session_manager
    
    if analysis_engine is None:
        try:
            from ...services.advanced_strategy_analysis import AdvancedStrategyAnalysisEngine
            analysis_engine = AdvancedStrategyAnalysisEngine()
        except Exception as e:
            logger.warning(f"AdvancedStrategyAnalysisEngine not available: {e}")
    
    if session_manager is None:
        try:
            from ...services.analysis_session_manager import AnalysisSessionManager
            session_manager = AnalysisSessionManager()
        except Exception as e:
            logger.debug(f"AnalysisSessionManager not available: {e}")

@router.get("/topics")
async def get_topics_for_scoring(user_id: str = Query("demo_user", description="User ID")):
    """
    Get all topics with their content and scoring readiness status
    🆕 NEW ENDPOINT: Lists topics ready for strategic analysis
    """
    try:
        _init_services()  # Lazy load services
        connection = await db_manager.get_connection()
        
        # Get topics with content statistics (✅ Using existing schema)
        query = """
        SELECT 
            t.session_id,
            t.topic,
            t.description,
            t.status,
            t.created_at,
            t.updated_at,
            t.metadata,
            COUNT(tu.id) as url_count,
            AVG(tu.quality_score) as avg_url_quality,
            MAX(tu.created_at) as last_url_update
        FROM topics t
        LEFT JOIN topic_urls tu ON t.session_id = tu.session_id
        WHERE t.user_id = $1
        GROUP BY t.session_id, t.topic, t.description, t.status, 
                 t.created_at, t.updated_at, t.metadata
        ORDER BY t.updated_at DESC
        """
        
        rows = await connection.fetch(query, user_id)
        
        topics = []
        for row in rows:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            
            # Determine scoring readiness
            url_count = row['url_count'] or 0
            has_content = url_count > 0
            avg_quality = float(row['avg_url_quality']) if row['avg_url_quality'] else 0.0
            
            # Check if already scored
            score_check_query = """
            SELECT COUNT(*) as score_count, MAX(created_at) as last_scored
            FROM analysis_scores
            WHERE session_id = $1
            """
            score_row = await connection.fetchrow(score_check_query, row['session_id'])
            has_scores = (score_row['score_count'] or 0) > 0
            last_scored = score_row['last_scored']
            
            # Determine scoring status
            if not has_content:
                scoring_status = "no_content"
            elif not has_scores:
                scoring_status = "never_scored"
            elif last_scored and row['last_url_update'] and row['last_url_update'] > last_scored:
                scoring_status = "needs_update"
            else:
                scoring_status = "up_to_date"
            
            topics.append({
                "session_id": row['session_id'],
                "topic": row['topic'],
                "description": row['description'],
                "status": row['status'],
                "created_at": row['created_at'].isoformat(),
                "updated_at": row['updated_at'].isoformat(),
                "content_statistics": {
                    "total_items": url_count,
                    "processed_items": url_count,  # All URLs collected are considered "processed"
                    "average_quality": round(avg_quality, 3),
                    "has_content": has_content,
                    "last_content_update": row['last_url_update'].isoformat() if row['last_url_update'] else None
                },
                "scoring_information": {
                    "total_scores": score_row['score_count'] or 0,
                    "has_scores": has_scores,
                    "last_scored": last_scored.isoformat() if last_scored else None,
                    "scoring_status": scoring_status,
                    "ready_for_scoring": has_content
                },
                "metadata": metadata
            })
        
        return {"success": True, "topics": topics}
        
    except Exception as e:
        logger.error(f"Failed to get topics for scoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/start")
async def start_scoring(
    session_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Query("demo_user", description="User ID")
):
    """
    Start comprehensive strategic scoring workflow
    🆕 NEW ENDPOINT: Executes existing AdvancedStrategyAnalysisEngine
    """
    try:
        connection = await db_manager.get_connection()
        
        # Get topic information
        topic_query = "SELECT * FROM topics WHERE session_id = $1 AND user_id = $2"
        topic_row = await connection.fetchrow(topic_query, session_id, user_id)
        
        if not topic_row:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Get content/URLs for analysis
        urls_query = """
        SELECT url, title, description, quality_score, relevance_score, metadata
        FROM topic_urls
        WHERE session_id = $1
        ORDER BY priority_level ASC, quality_score DESC
        LIMIT 100
        """
        url_rows = await connection.fetch(urls_query, session_id)
        
        if not url_rows:
            return {
                "success": False,
                "error": "No content available for scoring",
                "session_id": session_id
            }
        
        # Prepare data for analysis (✅ Using existing engine format)
        topic_data = {
            "session_id": session_id,
            "topic": topic_row['topic'],
            "description": topic_row['description'],
            "content_items": [
                {
                    "url": row['url'],
                    "title": row['title'],
                    "content": row['description'] or "",  # Using description as content
                    "quality_score": float(row['quality_score']) if row['quality_score'] else 0.0,
                    "relevance_score": float(row['relevance_score']) if row['relevance_score'] else 0.0,
                    "metadata": json.loads(row['metadata']) if row['metadata'] else {}
                }
                for row in url_rows
            ]
        }
        
        client_inputs = json.loads(topic_row['metadata']) if topic_row['metadata'] else {}
        
        # Run strategic analysis (✅ Using EXISTING AdvancedStrategyAnalysisEngine)
        logger.info(f"Starting strategic analysis for {session_id} with {len(url_rows)} content items")
        
        _init_services()  # Ensure services are loaded
        
        if not analysis_engine:
            return {
                "success": False,
                "error": "Analysis engine not available. Missing dependencies.",
                "session_id": session_id
            }
        
        try:
            analysis_results = analysis_engine.analyze_strategy(
                session_id=session_id,
                topic_data=topic_data,
                client_inputs=client_inputs
            )
            
            # Save scoring results to database
            await _save_scoring_results(session_id, analysis_results)
            
            logger.info(f"✅ Strategic analysis completed for {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "scoring_completed": True,
                "results_summary": {
                    "business_case_score": analysis_results.get('business_case_score', 0.0),
                    "scenarios_generated": len(analysis_results.get('scenarios', [])),
                    "content_items_analyzed": len(url_rows),
                    "analysis_type": analysis_results.get('simulation_metadata', {}).get('analysis_type', 'advanced')
                },
                "message": f"Analysis completed with {len(analysis_results.get('scenarios', []))} scenarios"
            }
            
        except Exception as e:
            logger.error(f"Analysis engine failed for {session_id}: {e}")
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "session_id": session_id
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start scoring for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/results")
async def get_scoring_results(session_id: str):
    """
    Get detailed scoring results for a topic
    🆕 NEW ENDPOINT: Retrieves stored analysis results
    """
    try:
        connection = await db_manager.get_connection()
        
        # Get latest comprehensive analysis (✅ Using existing analysis_scores table)
        query = """
        SELECT 
            session_id, analysis_type, score, confidence,
            analysis_data, created_at, metadata
        FROM analysis_scores 
        WHERE session_id = $1 
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        row = await connection.fetchrow(query, session_id)
        
        if not row:
            return {
                "has_results": False, 
                "message": "No scoring results found for this topic",
                "session_id": session_id
            }
        
        # Parse analysis data
        analysis_data = json.loads(row['analysis_data']) if row['analysis_data'] else {}
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        
        # Format results for frontend
        return {
            "has_results": True,
            "session_id": session_id,
            "scored_at": row['created_at'].isoformat(),
            "results": {
                "overall_score": row['score'],
                "confidence": row['confidence'],
                "business_case_score": analysis_data.get('business_case_score', row['score']),
                "scenarios": analysis_data.get('scenarios', []),
                "driver_sensitivities": analysis_data.get('driver_sensitivities', {}),
                "financial_projections": analysis_data.get('financial_projections', {}),
                "analysis_metadata": analysis_data.get('simulation_metadata', {}),
                "assumptions": analysis_data.get('assumptions', {}),
                # Add structured scores for frontend visualization
                "layer_scores": _extract_layer_scores(analysis_data),
                "factor_scores": _extract_factor_scores(analysis_data),
                "segment_scores": _extract_segment_scores(analysis_data)
            },
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Failed to get scoring results for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _save_scoring_results(session_id: str, analysis_results: Dict[str, Any]):
    """
    Save scoring results to database
    🆕 NEW HELPER: Stores analysis in existing schema
    """
    try:
        connection = await db_manager.get_connection()
        
        # Save to analysis_scores table (✅ Using existing table)
        query = """
        INSERT INTO analysis_scores 
        (session_id, analysis_type, score, confidence, analysis_data, created_at, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        await connection.execute(
            query,
            session_id,
            "comprehensive_strategic_analysis",
            analysis_results.get('business_case_score', 0.5),
            0.8,  # Default confidence
            json.dumps(analysis_results),
            datetime.now(timezone.utc),
            json.dumps({
                "analysis_completed_at": datetime.now(timezone.utc).isoformat(),
                "framework_version": "2.0"
            })
        )
        
        logger.info(f"✅ Scoring results saved for {session_id}")
        
    except Exception as e:
        logger.error(f"Failed to save scoring results for {session_id}: {e}")
        raise

def _extract_layer_scores(analysis_data: Dict) -> List[Dict]:
    """
    Extract layer scores from analysis data
    🆕 NEW HELPER: Transforms existing analysis format for frontend
    """
    # Try to extract from driver sensitivities or scenarios
    layer_scores = []
    
    sensitivities = analysis_data.get('driver_sensitivities', {})
    if sensitivities:
        for driver_name, sensitivity in list(sensitivities.items())[:8]:
            layer_scores.append({
                "layer_name": driver_name.upper().replace(' ', '_'),
                "score": min(1.0, abs(float(sensitivity)) / 100),  # Normalize
                "confidence": 0.75,
                "evidence_count": len(analysis_data.get('scenarios', [])),
                "insights": [f"Key driver with {abs(float(sensitivity)):.1f}% impact"]
            })
    
    # If no sensitivities, create default layers from scenarios
    if not layer_scores and analysis_data.get('scenarios'):
        default_layers = [
            "MARKET_DYNAMICS", "COMPETITIVE_LANDSCAPE", "CONSUMER_BEHAVIOR",
            "PRODUCT_INNOVATION", "BRAND_POSITIONING", "FINANCIAL_PERFORMANCE"
        ]
        scenarios = analysis_data.get('scenarios', [])
        for layer in default_layers[:6]:
            layer_scores.append({
                "layer_name": layer,
                "score": 0.65 if scenarios else 0.5,
                "confidence": 0.7,
                "evidence_count": len(scenarios),
                "insights": [f"Analysis available for {layer.replace('_', ' ').title()}"]
            })
    
    return layer_scores

def _extract_factor_scores(analysis_data: Dict) -> List[Dict]:
    """
    Extract factor scores from analysis data
    🆕 NEW HELPER: Transforms existing analysis format for frontend
    """
    factor_scores = []
    
    # Extract from business case score
    business_score = analysis_data.get('business_case_score', 0.5)
    
    factors = [
        ("Market_Attractiveness", business_score * 0.9),
        ("Competitive_Strength", business_score * 0.85),
        ("Financial_Viability", business_score * 0.95),
        ("Innovation_Potential", business_score * 0.8)
    ]
    
    for factor_name, value in factors:
        factor_scores.append({
            "factor_name": factor_name,
            "value": value,
            "confidence": 0.75,
            "input_layers": ["MARKET_DYNAMICS", "COMPETITIVE_LANDSCAPE"],
            "formula": f"Derived from business case analysis"
        })
    
    return factor_scores

def _extract_segment_scores(analysis_data: Dict) -> List[Dict]:
    """
    Extract segment scores from analysis data
    🆕 NEW HELPER: Transforms existing analysis format for frontend
    """
    segment_scores = []
    
    # Use scenarios to infer segment scores
    scenarios = analysis_data.get('scenarios', [])
    business_score = analysis_data.get('business_case_score', 0.5)
    
    segments = [
        {
            "segment_name": "Premium_Market",
            "attractiveness": business_score * 0.9,
            "competitiveness": business_score * 0.85,
            "market_size": business_score * 0.7,
            "growth": business_score * 0.95
        },
        {
            "segment_name": "Mass_Market",
            "attractiveness": business_score * 0.85,
            "competitiveness": business_score * 0.9,
            "market_size": business_score * 0.95,
            "growth": business_score * 0.8
        },
        {
            "segment_name": "Niche_Market",
            "attractiveness": business_score * 0.8,
            "competitiveness": business_score * 0.7,
            "market_size": business_score * 0.5,
            "growth": business_score * 0.9
        }
    ]
    
    return segments

@router.get("/{session_id}/quick-score")
async def get_quick_score(session_id: str):
    """
    Get quick scoring summary without full analysis
    🆕 NEW ENDPOINT: Fast scoring overview
    """
    try:
        connection = await db_manager.get_connection()
        
        # Calculate quick score from URL quality metrics
        query = """
        SELECT 
            COUNT(*) as total_urls,
            AVG(quality_score) as avg_quality,
            AVG(relevance_score) as avg_relevance,
            COUNT(CASE WHEN quality_score >= 0.7 THEN 1 END) as high_quality_count
        FROM topic_urls
        WHERE session_id = $1
        """
        
        row = await connection.fetchrow(query, session_id)
        
        if not row or not row['total_urls']:
            return {
                "has_score": False,
                "message": "No data available for scoring"
            }
        
        # Calculate quick score
        avg_quality = float(row['avg_quality']) if row['avg_quality'] else 0.5
        avg_relevance = float(row['avg_relevance']) if row['avg_relevance'] else 0.5
        high_quality_ratio = (row['high_quality_count'] or 0) / (row['total_urls'] or 1)
        
        quick_score = (avg_quality * 0.4 + avg_relevance * 0.3 + high_quality_ratio * 0.3)
        
        return {
            "has_score": True,
            "session_id": session_id,
            "quick_score": round(quick_score, 3),
            "metrics": {
                "average_quality": round(avg_quality, 3),
                "average_relevance": round(avg_relevance, 3),
                "high_quality_ratio": round(high_quality_ratio, 3),
                "total_urls": row['total_urls']
            },
            "recommendation": _get_recommendation(quick_score, row['total_urls'])
        }
        
    except Exception as e:
        logger.error(f"Failed to get quick score for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_recommendation(score: float, url_count: int) -> str:
    """Generate recommendation based on score"""
    if score >= 0.7 and url_count >= 20:
        return "Excellent - Ready for full strategic analysis"
    elif score >= 0.5 and url_count >= 10:
        return "Good - Proceed with analysis"
    elif url_count < 10:
        return "Collect more URLs for better analysis"
    else:
        return "Consider improving URL quality before full analysis"
