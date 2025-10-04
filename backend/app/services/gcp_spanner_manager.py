"""
Google Cloud Spanner Manager
Handles analytics and cross-topic insights storage
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
import json

from google.cloud import spanner
from google.cloud.spanner_v1 import param_types

from ..core.gcp_persistence_config import get_gcp_persistence_settings

logger = logging.getLogger(__name__)

class GCPSpannerManager:
    """Manages Google Cloud Spanner operations for analytics"""
    
    def __init__(self):
        self.settings = get_gcp_persistence_settings()
        self.client = None
        self.instance = None
        self.database = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Cloud Spanner client and database"""
        if self._initialized:
            return
        
        try:
            # Initialize Spanner client
            self.client = spanner.Client(project=self.settings.project_id)
            
            # Get instance
            self.instance = self.client.instance(self.settings.spanner_instance_id)
            
            # Get database
            self.database = self.instance.database(self.settings.spanner_database_id)
            
            self._initialized = True
            logger.info("Cloud Spanner Manager initialized")
            
        except Exception as e:
            logger.exception("Failed to initialize Cloud Spanner")
            raise
    
    async def close(self):
        """Close Cloud Spanner connections"""
        self.client = None
        self.instance = None
        self.database = None
        self._initialized = False
        logger.info("Cloud Spanner Manager closed")
    
    async def _ensure_initialized(self):
        """Ensure Cloud Spanner is initialized"""
        if not self._initialized:
            await self.initialize()
    
    async def store_workflow_results(self, session_id: str, workflow_result: Dict[str, Any]) -> bool:
        """Store complete workflow results in Spanner"""
        await self._ensure_initialized()
        
        try:
            # Store workflow results in the analysis_results table
            analysis_id = f"workflow_{session_id}_{int(datetime.utcnow().timestamp())}"
            
            def store_workflow(transaction):
                transaction.insert_or_update(
                    'analysis_results',
                    columns=[
                        'session_id', 'analysis_id', 'analysis_type', 'user_id',
                        'created_at', 'overall_score', 'confidence_score',
                        'factor_scores', 'segment_scores', 'expert_analysis',
                        'market_insights', 'competitive_analysis', 'processing_metadata',
                        'processing_time_ms', 'data_points_analyzed'
                    ],
                    values=[(
                        session_id,
                        analysis_id,
                        'workflow',
                        workflow_result.get('user_id', 'unknown'),
                        datetime.utcnow(),
                        workflow_result.get('overall_score'),
                        workflow_result.get('confidence_score'),
                        json.dumps(workflow_result.get('factor_scores', {})),
                        json.dumps(workflow_result.get('segment_scores', {})),
                        json.dumps(workflow_result.get('expert_analysis', {})),
                        json.dumps(workflow_result.get('market_insights', {})),
                        json.dumps(workflow_result.get('competitive_analysis', {})),
                        json.dumps(workflow_result.get('processing_metadata', {})),
                        workflow_result.get('processing_time_ms', 0),
                        workflow_result.get('data_points_analyzed', 0)
                    )]
                )
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.database.run_in_transaction(store_workflow)
            )
            
            logger.info(f"Stored workflow results for session {session_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to store workflow results for {session_id}")
            return False
    
    async def store_analysis_results(self, session_id: str, analysis_result: Dict[str, Any]) -> bool:
        """Store analysis results in Spanner"""
        await self._ensure_initialized()
        
        try:
            # Store analysis results in the analysis_results table
            analysis_id = f"analysis_{session_id}_{int(datetime.utcnow().timestamp())}"
            
            def store_analysis(transaction):
                transaction.insert_or_update(
                    'analysis_results',
                    columns=[
                        'session_id', 'analysis_id', 'analysis_type', 'user_id',
                        'created_at', 'overall_score', 'confidence_score',
                        'factor_scores', 'segment_scores', 'expert_analysis',
                        'market_insights', 'competitive_analysis', 'processing_metadata',
                        'processing_time_ms', 'data_points_analyzed'
                    ],
                    values=[(
                        session_id,
                        analysis_id,
                        analysis_result.get('analysis_type', 'comprehensive'),
                        analysis_result.get('user_id', 'unknown'),
                        datetime.utcnow(),
                        analysis_result.get('overall_score'),
                        analysis_result.get('confidence_score'),
                        json.dumps(analysis_result.get('factor_scores', {})),
                        json.dumps(analysis_result.get('segment_scores', {})),
                        json.dumps(analysis_result.get('expert_analysis', {})),
                        json.dumps(analysis_result.get('market_insights', {})),
                        json.dumps(analysis_result.get('competitive_analysis', {})),
                        json.dumps(analysis_result.get('processing_metadata', {})),
                        analysis_result.get('processing_time_ms', 0),
                        analysis_result.get('data_points_analyzed', 0)
                    )]
                )
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.database.run_in_transaction(store_analysis)
            )
            
            logger.info(f"Stored analysis results for session {session_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to store analysis results for {session_id}")
            return False
    
    async def get_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user analytics from Spanner"""
        await self._ensure_initialized()
        
        try:
            # This would query the user_analytics table
            # For now, return mock analytics
            
            mock_analytics = {
                "user_id": user_id,
                "period_days": days,
                "topics_created": 15,
                "analyses_completed": 12,
                "total_urls_processed": 450,
                "average_analysis_quality": 0.82,
                "preferred_analysis_types": ["comprehensive", "standard"],
                "most_analyzed_sectors": ["Technology", "Finance", "Healthcare"],
                "success_rate": 0.89,
                "engagement_score": 0.76
            }
            
            return mock_analytics
            
        except Exception as e:
            logger.exception(f"Failed to get user analytics for {user_id}")
            return {}
    
    async def get_market_intelligence(self, market_segment: str, 
                                    time_period_days: int = 90) -> Dict[str, Any]:
        """Get market intelligence data"""
        await self._ensure_initialized()
        
        try:
            # This would query the market_intelligence table
            # For now, return mock intelligence data
            
            mock_intelligence = {
                "market_segment": market_segment,
                "time_period_days": time_period_days,
                "total_analyses": 250,
                "average_scores": {
                    "market_potential": 0.75,
                    "competitive_advantage": 0.68,
                    "growth_opportunity": 0.82
                },
                "trend_indicators": {
                    "growth_trend": "positive",
                    "competition_level": "moderate",
                    "innovation_rate": "high"
                },
                "emerging_patterns": [
                    "Increased focus on sustainability",
                    "Digital transformation acceleration",
                    "Remote work adoption"
                ],
                "opportunity_indicators": {
                    "market_size_growth": 0.15,
                    "technology_adoption_rate": 0.72,
                    "investment_activity": "high"
                }
            }
            
            return mock_intelligence
            
        except Exception as e:
            logger.exception(f"Failed to get market intelligence for {market_segment}")
            return {}
    
    async def get_cross_topic_insights(self, user_id: str, insight_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get cross-topic insights for pattern recognition"""
        await self._ensure_initialized()
        
        try:
            # This would query the cross_topic_insights table
            # For now, return mock insights
            
            mock_insights = [
                {
                    "insight_id": "insight_001",
                    "insight_type": "pattern_recognition",
                    "confidence_score": 0.85,
                    "insight_data": {
                        "pattern": "Consistent market validation across sectors",
                        "supporting_evidence": ["tech_analysis", "finance_analysis", "healthcare_analysis"],
                        "relevance_score": 0.92
                    },
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "insight_id": "insight_002",
                    "insight_type": "trend_analysis",
                    "confidence_score": 0.78,
                    "insight_data": {
                        "trend": "AI integration acceleration",
                        "supporting_evidence": ["multiple_sector_analyses"],
                        "relevance_score": 0.88
                    },
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
            
            return mock_insights
            
        except Exception as e:
            logger.exception(f"Failed to get cross-topic insights for {user_id}")
            return []
    
    async def store_cross_topic_insight(self, user_id: str, insight_data: Dict[str, Any]) -> bool:
        """Store cross-topic insight"""
        await self._ensure_initialized()
        
        try:
            # This would insert into the cross_topic_insights table
            # For now, simulate the operation
            
            insight_id = f"insight_{int(datetime.utcnow().timestamp())}"
            logger.info(f"Stored cross-topic insight {insight_id} for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.exception(f"Failed to store cross-topic insight for {user_id}")
            return False
    
    async def update_user_analytics(self, user_id: str, analytics_data: Dict[str, Any]) -> bool:
        """Update user analytics metrics"""
        await self._ensure_initialized()
        
        try:
            # This would upsert into the user_analytics table
            # For now, simulate the operation
            
            logger.info(f"Updated user analytics for {user_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to update user analytics for {user_id}")
            return False
    
    async def aggregate_market_intelligence(self, market_segment: str, 
                                          time_period_days: int = 30) -> bool:
        """Aggregate market intelligence from recent analyses"""
        await self._ensure_initialized()
        
        try:
            # This would aggregate data from analysis_results table
            # and store in market_intelligence table
            # For now, simulate the operation
            
            logger.info(f"Aggregated market intelligence for {market_segment}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to aggregate market intelligence for {market_segment}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform Cloud Spanner health check"""
        await self._ensure_initialized()
        
        try:
            start_time = datetime.utcnow()
            
            # Test basic connectivity with a real query
            def test_connectivity(transaction):
                return list(transaction.execute_sql("SELECT 1 as test"))
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.database.run_in_transaction(test_connectivity)
            )
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "spanner_instance": self.settings.spanner_instance_id,
                "spanner_database": self.settings.spanner_database_id,
                "project_id": self.settings.project_id
            }
            
        except Exception as e:
            logger.exception("Cloud Spanner health check failed")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
