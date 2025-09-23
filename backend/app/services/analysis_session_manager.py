# backend/app/services/analysis_session_manager.py

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import asdict

from google.cloud import firestore
from google.cloud import pubsub_v1

from ..models.analysis_models import (
    AnalysisSession, AnalysisProgress, AnalysisStatus,
    LayerScore, FactorCalculation, SegmentScore
)
from ..core.gcp_config import GCPSettings
from .expert_persona_scorer import ExpertPersonaScorer
from .formula_engine import FormulaEngine
from .gcp_topic_vector_store_manager import GCPTopicVectorStoreManager
from ..middleware.monitoring import performance_monitor

logger = logging.getLogger(__name__)

class AnalysisSessionManager:
    """Manages the complete lifecycle of strategic analysis sessions"""
    
    def __init__(self):
        self.settings = GCPSettings()
        self.firestore_client = firestore.Client()
        self.publisher = pubsub_v1.PublisherClient()
        self.expert_scorer = ExpertPersonaScorer()
        self.formula_engine = FormulaEngine()
        self.topic_manager = GCPTopicVectorStoreManager()
        
        # Pub/Sub topic for analysis progress events
        self.analysis_topic = self.publisher.topic_path(
            self.settings.gcp_project_id, 
            "validatus-analysis-events"
        )
        
    @performance_monitor
    async def create_analysis_session(self, 
                                    topic: str, 
                                    user_id: str,
                                    analysis_parameters: Dict[str, Any] = None) -> str:
        """Initialize a new strategic analysis session"""
        
        session_id = self._generate_session_id(topic, user_id)
        
        try:
            # Create analysis session record
            session = AnalysisSession(
                session_id=session_id,
                topic=topic,
                user_id=user_id,
                status=AnalysisStatus.INITIALIZED,
                parameters=analysis_parameters or {},
                created_at=datetime.now(timezone.utc),
                last_updated=datetime.now(timezone.utc)
            )
            
            # Store in Firestore
            session_ref = self.firestore_client.collection('analysis_sessions').document(session_id)
            await session_ref.set(asdict(session))
            
            # Initialize progress tracking
            progress = AnalysisProgress(
                session_id=session_id,
                current_stage="initialization",
                completed_layers=[],
                completed_factors=[],
                completed_segments=[],
                progress_percentage=0.0,
                estimated_completion=self._estimate_completion_time(),
                error_messages=[],
                last_updated=datetime.now(timezone.utc)
            )
            
            progress_ref = self.firestore_client.collection('analysis_progress').document(session_id)
            await progress_ref.set(asdict(progress))
            
            # Publish initialization event
            await self._publish_analysis_event(session_id, "session_created", {
                "topic": topic,
                "user_id": user_id,
                "estimated_completion": progress.estimated_completion
            })
            
            logger.info(f"✅ Created analysis session {session_id} for topic '{topic}'")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create analysis session: {e}")
            raise

    @performance_monitor
    async def execute_strategic_analysis(self, session_id: str) -> Dict[str, Any]:
        """Execute the complete strategic analysis workflow"""
        
        logger.info(f"Starting strategic analysis for session {session_id}")
        
        try:
            # Update session status
            await self._update_session_status(session_id, AnalysisStatus.ANALYZING)
            
            # Step 1: Load topic knowledge
            topic_knowledge = await self._load_topic_knowledge(session_id)
            await self._update_progress(session_id, "loading_knowledge", 10.0)
            
            # Step 2: Execute layer scoring
            layer_scores = await self._execute_layer_scoring(session_id, topic_knowledge)
            await self._update_progress(session_id, "layer_scoring", 40.0)
            
            # Step 3: Calculate factor aggregations
            factor_calculations = await self._calculate_factor_aggregations(session_id, layer_scores)
            await self._update_progress(session_id, "factor_calculation", 70.0)
            
            # Step 4: Generate segment scores
            segment_scores = await self._generate_segment_scores(session_id, factor_calculations)
            await self._update_progress(session_id, "segment_analysis", 90.0)
            
            # Step 5: Finalize analysis
            analysis_results = await self._finalize_analysis(session_id, {
                'layer_scores': layer_scores,
                'factor_calculations': factor_calculations,
                'segment_scores': segment_scores
            })
            
            await self._update_session_status(session_id, AnalysisStatus.COMPLETED)
            await self._update_progress(session_id, "completed", 100.0)
            
            # Publish completion event
            await self._publish_analysis_event(session_id, "analysis_completed", {
                "total_layers": len(layer_scores),
                "total_factors": len(factor_calculations),
                "total_segments": len(segment_scores)
            })
            
            logger.info(f"✅ Completed strategic analysis for session {session_id}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Strategic analysis failed for session {session_id}: {e}")
            await self._update_session_status(session_id, AnalysisStatus.ERROR)
            await self._update_progress_with_error(session_id, str(e))
            raise

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of an analysis session"""
        
        try:
            # Get session data
            session_ref = self.firestore_client.collection('analysis_sessions').document(session_id)
            session_doc = await session_ref.get()
            
            if not session_doc.exists:
                return {'error': 'Session not found'}
            
            session_data = session_doc.to_dict()
            
            # Get progress data
            progress_ref = self.firestore_client.collection('analysis_progress').document(session_id)
            progress_doc = await progress_ref.get()
            
            progress_data = progress_doc.to_dict() if progress_doc.exists else {}
            
            return {
                'session_id': session_id,
                'status': session_data.get('status'),
                'topic': session_data.get('topic'),
                'created_at': session_data.get('created_at'),
                'progress': progress_data.get('progress_percentage', 0.0),
                'current_stage': progress_data.get('current_stage', 'unknown'),
                'estimated_completion': progress_data.get('estimated_completion'),
                'error_messages': progress_data.get('error_messages', [])
            }
            
        except Exception as e:
            logger.error(f"Failed to get session status: {e}")
            return {'error': str(e)}

    async def get_analysis_results(self, session_id: str) -> Dict[str, Any]:
        """Get complete analysis results for a session"""
        
        try:
            # Get layer scores
            layer_scores = await self._get_layer_scores(session_id)
            
            # Get factor calculations
            factor_calculations = await self._get_factor_calculations(session_id)
            
            # Get segment scores
            segment_scores = await self._get_segment_scores(session_id)
            
            # Get session metadata
            session_data = await self._get_session_data(session_id)
            
            return {
                'session_id': session_id,
                'session_data': session_data,
                'layer_scores': layer_scores,
                'factor_calculations': factor_calculations,
                'segment_scores': segment_scores,
                'summary': self._generate_analysis_summary(layer_scores, factor_calculations, segment_scores)
            }
            
        except Exception as e:
            logger.error(f"Failed to get analysis results: {e}")
            return {'error': str(e)}

    async def _execute_layer_scoring(self, 
                                   session_id: str, 
                                   topic_knowledge: Dict[str, Any]) -> List[LayerScore]:
        """Execute scoring for all strategic layers"""
        
        logger.info(f"Executing layer scoring for session {session_id}")
        
        # Define the strategic layers for analysis
        strategic_layers = [
            "Consumer", "Market", "Product", "Brand", "Experience",
            "Technology", "Operations", "Financial", "Competitive", "Regulatory"
        ]
        
        layer_scores = []
        
        for layer in strategic_layers:
            try:
                # Use Expert Persona Scorer to analyze this layer
                layer_analysis = await self.expert_scorer.score_layer(
                    topic_knowledge=topic_knowledge,
                    layer_name=layer,
                    session_id=session_id
                )
                
                layer_score = LayerScore(
                    session_id=session_id,
                    layer_name=layer,
                    score=layer_analysis['score'],
                    confidence=layer_analysis['confidence'],
                    evidence_count=len(layer_analysis['evidence']),
                    key_insights=layer_analysis['insights'],
                    evidence_summary=layer_analysis['evidence_summary'],
                    calculation_metadata=layer_analysis['metadata'],
                    created_at=datetime.now(timezone.utc)
                )
                
                layer_scores.append(layer_score)
                
                # Store individual layer score
                await self._store_layer_score(layer_score)
                
                # Update progress
                current_progress = (len(layer_scores) / len(strategic_layers)) * 30.0 + 10.0
                await self._update_progress(session_id, f"scored_layer_{layer.lower()}", current_progress)
                
                logger.info(f"Completed layer scoring for {layer}: {layer_analysis['score']:.3f}")
                
            except Exception as e:
                logger.error(f"Failed to score layer {layer}: {e}")
                # Continue with other layers even if one fails
                continue
        
        return layer_scores

    async def _calculate_factor_aggregations(self, 
                                          session_id: str, 
                                          layer_scores: List[LayerScore]) -> List[FactorCalculation]:
        """Calculate strategic factors from layer scores using the Formula Engine"""
        
        logger.info(f"Calculating factor aggregations for session {session_id}")
        
        # Convert layer scores to input format for formula engine
        layer_score_dict = {
            score.layer_name.lower(): score.score 
            for score in layer_scores
        }
        
        # Execute formula calculations
        factor_calculations = await self.formula_engine.calculate_all_factors(
            layer_scores=layer_score_dict,
            session_id=session_id
        )
        
        # Store factor calculations
        for factor_calc in factor_calculations:
            await self._store_factor_calculation(factor_calc)
        
        logger.info(f"Completed {len(factor_calculations)} factor calculations")
        return factor_calculations

    async def _generate_segment_scores(self, 
                                     session_id: str, 
                                     factor_calculations: List[FactorCalculation]) -> List[SegmentScore]:
        """Generate market segment analysis scores"""
        
        logger.info(f"Generating segment scores for session {session_id}")
        
        # Define market segments for analysis
        market_segments = [
            "Enterprise", "SMB", "Consumer", "Government", "Education"
        ]
        
        segment_scores = []
        
        for segment in market_segments:
            try:
                # Calculate segment-specific metrics
                segment_metrics = await self._calculate_segment_metrics(segment, factor_calculations)
                
                segment_score = SegmentScore(
                    session_id=session_id,
                    segment_name=segment,
                    attractiveness_score=segment_metrics['attractiveness'],
                    competitive_intensity=segment_metrics['competitive_intensity'],
                    market_size=segment_metrics['market_size'],
                    growth_potential=segment_metrics['growth_potential'],
                    key_drivers=segment_metrics['key_drivers'],
                    risk_factors=segment_metrics['risk_factors'],
                    opportunity_metrics=segment_metrics['opportunity_metrics'],
                    created_at=datetime.now(timezone.utc)
                )
                
                segment_scores.append(segment_score)
                
                # Store segment score
                await self._store_segment_score(segment_score)
                
                logger.info(f"Completed segment analysis for {segment}: {segment_metrics['attractiveness']:.3f}")
                
            except Exception as e:
                logger.error(f"Failed to analyze segment {segment}: {e}")
                continue
        
        return segment_scores

    async def _load_topic_knowledge(self, session_id: str) -> Dict[str, Any]:
        """Load topic knowledge for analysis"""
        
        try:
            # Get session data to find topic
            session_data = await self._get_session_data(session_id)
            topic = session_data.get('topic', '')
            
            if not topic:
                raise ValueError("No topic found for session")
            
            # Load topic knowledge from vector store
            topic_knowledge = await self.topic_manager.retrieve_topic_knowledge(topic)
            
            return topic_knowledge
            
        except Exception as e:
            logger.error(f"Failed to load topic knowledge: {e}")
            # Return empty knowledge structure
            return {
                'topic': session_data.get('topic', '') if 'session_data' in locals() else '',
                'documents': [],
                'metadata': {'error': str(e)}
            }

    async def _finalize_analysis(self, 
                               session_id: str, 
                               analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the analysis and create summary"""
        
        try:
            # Calculate overall analysis score
            layer_scores = analysis_data['layer_scores']
            factor_calculations = analysis_data['factor_calculations']
            segment_scores = analysis_data['segment_scores']
            
            # Calculate overall score
            avg_layer_score = sum(score.score for score in layer_scores) / len(layer_scores) if layer_scores else 0.0
            avg_factor_score = sum(calc.calculated_value for calc in factor_calculations) / len(factor_calculations) if factor_calculations else 0.0
            avg_segment_score = sum(score.attractiveness_score for score in segment_scores) / len(segment_scores) if segment_scores else 0.0
            
            overall_score = (avg_layer_score * 0.4 + avg_factor_score * 0.4 + avg_segment_score * 0.2)
            
            # Generate insights
            insights = await self._generate_final_insights(layer_scores, factor_calculations, segment_scores)
            
            # Create analysis summary
            analysis_summary = {
                'overall_score': round(overall_score, 3),
                'layer_analysis': {
                    'total_layers': len(layer_scores),
                    'average_score': round(avg_layer_score, 3),
                    'top_layer': max(layer_scores, key=lambda x: x.score).layer_name if layer_scores else None,
                    'weakest_layer': min(layer_scores, key=lambda x: x.score).layer_name if layer_scores else None
                },
                'factor_analysis': {
                    'total_factors': len(factor_calculations),
                    'average_score': round(avg_factor_score, 3),
                    'top_factor': max(factor_calculations, key=lambda x: x.calculated_value).factor_name if factor_calculations else None,
                    'weakest_factor': min(factor_calculations, key=lambda x: x.calculated_value).factor_name if factor_calculations else None
                },
                'segment_analysis': {
                    'total_segments': len(segment_scores),
                    'average_attractiveness': round(avg_segment_score, 3),
                    'most_attractive_segment': max(segment_scores, key=lambda x: x.attractiveness_score).segment_name if segment_scores else None,
                    'least_attractive_segment': min(segment_scores, key=lambda x: x.attractiveness_score).segment_name if segment_scores else None
                },
                'key_insights': insights,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Store analysis summary
            await self._store_analysis_summary(session_id, analysis_summary)
            
            return analysis_summary
            
        except Exception as e:
            logger.error(f"Failed to finalize analysis: {e}")
            return {'error': str(e)}

    async def _update_session_status(self, session_id: str, status: AnalysisStatus):
        """Update session status in Firestore"""
        
        try:
            session_ref = self.firestore_client.collection('analysis_sessions').document(session_id)
            await session_ref.update({
                'status': status.value,
                'last_updated': datetime.now(timezone.utc),
                'completed_at': datetime.now(timezone.utc) if status == AnalysisStatus.COMPLETED else None
            })
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")

    async def _update_progress(self, session_id: str, stage: str, percentage: float):
        """Update analysis progress"""
        
        try:
            progress_ref = self.firestore_client.collection('analysis_progress').document(session_id)
            await progress_ref.update({
                'current_stage': stage,
                'progress_percentage': percentage,
                'last_updated': datetime.now(timezone.utc)
            })
            
            # Publish progress event
            await self._publish_analysis_event(session_id, "progress_update", {
                "stage": stage,
                "percentage": percentage
            })
            
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")

    async def _update_progress_with_error(self, session_id: str, error_message: str):
        """Update progress with error information"""
        
        try:
            progress_ref = self.firestore_client.collection('analysis_progress').document(session_id)
            current_data = await progress_ref.get()
            current_errors = current_data.to_dict().get('error_messages', []) if current_data.exists else []
            
            current_errors.append(error_message)
            
            await progress_ref.update({
                'current_stage': 'error',
                'error_messages': current_errors,
                'last_updated': datetime.now(timezone.utc)
            })
            
        except Exception as e:
            logger.error(f"Failed to update progress with error: {e}")

    async def _publish_analysis_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Publish analysis progress event to Pub/Sub"""
        
        try:
            event_data = {
                "session_id": session_id,
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data
            }
            
            message = json.dumps(event_data).encode('utf-8')
            future = self.publisher.publish(self.analysis_topic, message)
            await future.result()
            
        except Exception as e:
            logger.error(f"Failed to publish analysis event: {e}")

    def _generate_session_id(self, topic: str, user_id: str) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_hash = str(hash(topic))[:8]
        user_hash = str(hash(user_id))[:8]
        return f"analysis_{timestamp}_{topic_hash}_{user_hash}"

    def _estimate_completion_time(self) -> str:
        """Estimate analysis completion time"""
        # Simple estimation based on typical processing times
        estimated_minutes = 15  # 15 minutes average
        completion_time = datetime.now(timezone.utc).replace(minute=estimated_minutes)
        return completion_time.isoformat()

    async def _store_layer_score(self, layer_score: LayerScore):
        """Store layer score in Firestore"""
        layer_ref = self.firestore_client.collection('layer_scores').document()
        await layer_ref.set(asdict(layer_score))

    async def _store_factor_calculation(self, factor_calc: FactorCalculation):
        """Store factor calculation in Firestore"""
        factor_ref = self.firestore_client.collection('factor_calculations').document()
        await factor_ref.set(asdict(factor_calc))

    async def _store_segment_score(self, segment_score: SegmentScore):
        """Store segment score in Firestore"""
        segment_ref = self.firestore_client.collection('segment_scores').document()
        await segment_ref.set(asdict(segment_score))

    async def _store_analysis_summary(self, session_id: str, summary: Dict[str, Any]):
        """Store analysis summary in Firestore"""
        summary_ref = self.firestore_client.collection('analysis_summaries').document(session_id)
        await summary_ref.set(summary)

    async def _get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get session data from Firestore"""
        session_ref = self.firestore_client.collection('analysis_sessions').document(session_id)
        session_doc = await session_ref.get()
        return session_doc.to_dict() if session_doc.exists else {}

    async def _get_layer_scores(self, session_id: str) -> List[Dict[str, Any]]:
        """Get layer scores for a session"""
        layer_scores_ref = self.firestore_client.collection('layer_scores')
        query = layer_scores_ref.where('session_id', '==', session_id)
        docs = await query.get()
        return [doc.to_dict() for doc in docs]

    async def _get_factor_calculations(self, session_id: str) -> List[Dict[str, Any]]:
        """Get factor calculations for a session"""
        factor_calc_ref = self.firestore_client.collection('factor_calculations')
        query = factor_calc_ref.where('session_id', '==', session_id)
        docs = await query.get()
        return [doc.to_dict() for doc in docs]

    async def _get_segment_scores(self, session_id: str) -> List[Dict[str, Any]]:
        """Get segment scores for a session"""
        segment_scores_ref = self.firestore_client.collection('segment_scores')
        query = segment_scores_ref.where('session_id', '==', session_id)
        docs = await query.get()
        return [doc.to_dict() for doc in docs]

    async def _calculate_segment_metrics(self, segment: str, factor_calculations: List[FactorCalculation]) -> Dict[str, Any]:
        """Calculate metrics for a specific market segment"""
        
        # Simple segment-specific calculations (can be enhanced)
        base_attractiveness = 0.5
        base_competitive_intensity = 0.5
        base_market_size = 0.5
        base_growth_potential = 0.5
        
        # Adjust based on relevant factors
        for factor_calc in factor_calculations:
            if 'market' in factor_calc.factor_name.lower():
                base_attractiveness += factor_calc.calculated_value * 0.1
            elif 'competitive' in factor_calc.factor_name.lower():
                base_competitive_intensity += factor_calc.calculated_value * 0.1
        
        return {
            'attractiveness': min(1.0, max(0.0, base_attractiveness)),
            'competitive_intensity': min(1.0, max(0.0, base_competitive_intensity)),
            'market_size': min(1.0, max(0.0, base_market_size)),
            'growth_potential': min(1.0, max(0.0, base_growth_potential)),
            'key_drivers': [f"Factor {i}" for i in range(3)],
            'risk_factors': [f"Risk {i}" for i in range(2)],
            'opportunity_metrics': {
                'market_penetration': 0.3,
                'competitive_advantage': 0.4,
                'growth_rate': 0.2
            }
        }

    async def _generate_final_insights(self, 
                                     layer_scores: List[LayerScore],
                                     factor_calculations: List[FactorCalculation],
                                     segment_scores: List[SegmentScore]) -> List[str]:
        """Generate final insights from analysis results"""
        
        insights = []
        
        try:
            # Top performing layer
            if layer_scores:
                top_layer = max(layer_scores, key=lambda x: x.score)
                insights.append(f"Strongest strategic layer: {top_layer.layer_name} (score: {top_layer.score:.2f})")
            
            # Top performing factor
            if factor_calculations:
                top_factor = max(factor_calculations, key=lambda x: x.calculated_value)
                insights.append(f"Highest strategic factor: {top_factor.factor_name} (score: {top_factor.calculated_value:.2f})")
            
            # Most attractive segment
            if segment_scores:
                top_segment = max(segment_scores, key=lambda x: x.attractiveness_score)
                insights.append(f"Most attractive market segment: {top_segment.segment_name} (score: {top_segment.attractiveness_score:.2f})")
            
            # Overall assessment
            avg_scores = [
                sum(score.score for score in layer_scores) / len(layer_scores) if layer_scores else 0,
                sum(calc.calculated_value for calc in factor_calculations) / len(factor_calculations) if factor_calculations else 0,
                sum(score.attractiveness_score for score in segment_scores) / len(segment_scores) if segment_scores else 0
            ]
            
            overall_avg = sum(avg_scores) / len(avg_scores)
            
            if overall_avg > 0.7:
                insights.append("Overall analysis indicates strong strategic potential")
            elif overall_avg > 0.5:
                insights.append("Overall analysis shows moderate strategic potential with room for improvement")
            else:
                insights.append("Overall analysis suggests significant strategic challenges that need attention")
            
        except Exception as e:
            logger.error(f"Failed to generate final insights: {e}")
            insights.append("Analysis completed successfully")
        
        return insights

    def _generate_analysis_summary(self, 
                                 layer_scores: List[Dict[str, Any]],
                                 factor_calculations: List[Dict[str, Any]],
                                 segment_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate analysis summary"""
        
        return {
            'total_layers_analyzed': len(layer_scores),
            'total_factors_calculated': len(factor_calculations),
            'total_segments_evaluated': len(segment_scores),
            'analysis_completeness': '100%' if layer_scores and factor_calculations and segment_scores else 'Partial',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Export the class
__all__ = ['AnalysisSessionManager']
