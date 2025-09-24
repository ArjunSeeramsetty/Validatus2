# backend/app/services/phase_integrated_analysis_session_manager.py - EXTENDS EXISTING AnalysisSessionManager
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from .analysis_session_manager import AnalysisSessionManager
from .enhanced_content_processor import EnhancedContentProcessor
from .enhanced_data_pipeline.bayesian_data_blender import BayesianDataBlender, DataSource
from .enhanced_data_pipeline.event_shock_modeler import EventShockModeler, EventShock, EventType, DecayFunction
from .enhanced_knowledge.hybrid_vector_store_manager import HybridVectorStoreManager
from ..core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

class PhaseIntegratedAnalysisSessionManager(AnalysisSessionManager):
    """
    Phase-integrated Analysis Session Manager
    Extends existing manager with Phase B and Phase C capabilities
    """
    
    def __init__(self):
        super().__init__()
        
        # Phase C initialization (conditional)
        if FeatureFlags.ENHANCED_CONTENT_PROCESSING_ENABLED:
            self.enhanced_content_processor = EnhancedContentProcessor()
        else:
            self.enhanced_content_processor = None
        
        if FeatureFlags.BAYESIAN_PIPELINE_ENABLED:
            self.bayesian_blender = BayesianDataBlender()
        else:
            self.bayesian_blender = None
        
        if FeatureFlags.EVENT_SHOCK_MODELING_ENABLED:
            self.event_shock_modeler = EventShockModeler()
        else:
            self.event_shock_modeler = None
        
        if FeatureFlags.HYBRID_VECTOR_STORE_ENABLED:
            self.hybrid_vector_manager = HybridVectorStoreManager(
                project_id=self.settings.project_id
            )
        else:
            self.hybrid_vector_manager = None
        
        logger.info("✅ Phase-integrated Analysis Session Manager initialized")
    
    async def execute_comprehensive_analysis(self, 
                                           session_id: str, 
                                           topic: str, 
                                           user_id: str,
                                           analysis_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute comprehensive analysis integrating all available phases
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"Starting comprehensive analysis for session {session_id}")
        
        try:
            # Step 1: Enhanced content loading and processing
            if FeatureFlags.ENHANCED_CONTENT_PROCESSING_ENABLED and self.enhanced_content_processor:
                enhanced_content = await self._load_and_process_enhanced_content(session_id, topic)
                await self._update_progress(session_id, "enhanced_content_processing", 10.0)
            else:
                enhanced_content = await self._load_topic_knowledge(session_id)
                await self._update_progress(session_id, "content_loading", 10.0)
            
            # Step 2: Execute core analysis (existing functionality)
            core_results = await super().execute_strategic_analysis(session_id, topic, user_id)
            await self._update_progress(session_id, "core_analysis_complete", 60.0)
            
            # Step 3: Apply Phase C enhancements
            phase_c_results = {}
            
            if FeatureFlags.BAYESIAN_PIPELINE_ENABLED and self.bayesian_blender:
                bayesian_results = await self._apply_bayesian_enhancement(core_results, enhanced_content)
                phase_c_results['bayesian_analysis'] = bayesian_results
                await self._update_progress(session_id, "bayesian_analysis", 70.0)
            
            if FeatureFlags.EVENT_SHOCK_MODELING_ENABLED and self.event_shock_modeler:
                shock_results = await self._apply_event_shock_modeling(core_results, analysis_options)
                phase_c_results['event_shock_analysis'] = shock_results
                await self._update_progress(session_id, "event_shock_modeling", 80.0)
            
            if FeatureFlags.HYBRID_VECTOR_STORE_ENABLED and self.hybrid_vector_manager:
                hybrid_search_results = await self._perform_hybrid_search_analysis(session_id, topic)
                phase_c_results['hybrid_search_analysis'] = hybrid_search_results
                await self._update_progress(session_id, "hybrid_search_analysis", 90.0)
            
            # Step 4: Integrate all results
            comprehensive_results = await self._integrate_comprehensive_results(
                session_id, core_results, phase_c_results, enhanced_content
            )
            
            await self._update_progress(session_id, "comprehensive_analysis_complete", 100.0)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"✅ Comprehensive analysis completed in {processing_time:.2f}s")
            
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            await self._update_session_status(session_id, "ERROR")
            raise
    
    async def _load_and_process_enhanced_content(self, session_id: str, topic: str) -> Dict[str, Any]:
        """Load and process content with enhanced capabilities"""
        try:
            # Load base content
            base_content = await self._load_topic_knowledge(session_id)
            
            # Extract content items
            content_items = base_content.get('documents', [])
            
            if not content_items:
                return base_content
            
            # Apply enhanced content processing
            enhanced_analysis = await self.enhanced_content_processor.analyze_enhanced_content_quality(
                content_items, {'session_id': session_id, 'topic': topic}
            )
            
            # Combine with base content
            enhanced_content = {
                **base_content,
                'enhanced_quality_analysis': enhanced_analysis,
                'processing_method': 'enhanced_bayesian'
            }
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Enhanced content processing failed: {e}")
            return await self._load_topic_knowledge(session_id)
    
    async def _apply_bayesian_enhancement(self, 
                                        core_results: Dict[str, Any],
                                        enhanced_content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Bayesian data blending to analysis results"""
        try:
            # Extract layer scores from core results
            layer_scores = core_results.get('layer_scores', [])
            
            # Create data sources from layer scores
            data_sources = []
            for i, layer_score in enumerate(layer_scores):
                data_source = DataSource(
                    source_id=f"layer_{layer_score.layer_name}",
                    source_type='analysis_result',
                    data_points=[{
                        'score': layer_score.score,
                        'confidence': layer_score.confidence,
                        'evidence_count': layer_score.evidence_count
                    }],
                    reliability_score=layer_score.confidence,
                    recency_weight=1.0,  # Current analysis
                    source_bias=0.0
                )
                data_sources.append(data_source)
            
            # Apply Bayesian blending
            blended_results = {}
            
            # Blend by analysis categories
            for category in ['market', 'product', 'financial', 'strategic']:
                category_sources = [
                    ds for ds in data_sources 
                    if category.lower() in ds.source_id.lower()
                ]
                
                if category_sources:
                    blend_result = await self.bayesian_blender.blend_data_sources(
                        category_sources, 'quality_score', 0.6
                    )
                    blended_results[f'{category}_blended'] = blend_result
            
            return {
                'blended_category_results': blended_results,
                'bayesian_metadata': {
                    'sources_processed': len(data_sources),
                    'categories_blended': len(blended_results),
                    'method': 'bayesian_inference'
                }
            }
            
        except Exception as e:
            logger.error(f"Bayesian enhancement failed: {e}")
            return {'error': str(e)}
    
    async def _apply_event_shock_modeling(self, 
                                        core_results: Dict[str, Any],
                                        analysis_options: Dict[str, Any]) -> Dict[str, Any]:
        """Apply event shock modeling to results"""
        try:
            # Extract time series data from results
            time_series_data = []
            
            # Get layer scores as time series (simplified)
            layer_scores = core_results.get('layer_scores', [])
            for layer_score in layer_scores:
                time_series_data.append({
                    'date': layer_score.created_at.isoformat() if hasattr(layer_score, 'created_at') else datetime.now(timezone.utc).isoformat(),
                    'value': layer_score.score,
                    'metric': layer_score.layer_name
                })
            
            # Define potential event shocks (could come from analysis_options)
            event_shocks = analysis_options.get('event_shocks', []) if analysis_options else []
            
            if not event_shocks:
                # Create default market disruption scenario
                default_shock = EventShock(
                    event_id='market_disruption_2024',
                    event_type=EventType.MARKET_DISRUPTION,
                    event_date=datetime.now(timezone.utc),
                    impact_magnitude=-0.3,
                    decay_function=DecayFunction.EXPONENTIAL,
                    decay_parameters={'lambda': 0.1},
                    affected_metrics=['market', 'competitive'],
                    confidence_level=0.7,
                    event_metadata={'scenario': 'default_market_disruption'}
                )
                event_shocks = [default_shock]
            
            # Apply shock modeling
            shock_results = await self.event_shock_modeler.model_event_shocks(
                time_series_data, event_shocks, forecast_periods=12
            )
            
            return {
                'shock_modeling_results': shock_results,
                'events_modeled': len(event_shocks),
                'forecast_periods': 12
            }
            
        except Exception as e:
            logger.error(f"Event shock modeling failed: {e}")
            return {'error': str(e)}
    
    async def _perform_hybrid_search_analysis(self, session_id: str, topic: str) -> Dict[str, Any]:
        """Perform analysis using hybrid vector search"""
        try:
            # Perform hybrid search for additional context
            search_results = await self.hybrid_vector_manager.hybrid_search(
                query=topic,
                store_id=topic.lower().replace(' ', '_'),
                k=20,
                fusion_strategy='ranked_fusion'
            )
            
            # Analyze search result quality
            result_analysis = {
                'total_results': search_results.total_results,
                'search_time': search_results.search_time,
                'store_contributions': {
                    store: len(results) 
                    for store, results in search_results.store_contributions.items()
                },
                'fusion_metadata': search_results.result_fusion_metadata,
                'avg_similarity': sum(r.similarity_score for r in search_results.combined_results) / len(search_results.combined_results) if search_results.combined_results else 0.0
            }
            
            return result_analysis
            
        except Exception as e:
            logger.error(f"Hybrid search analysis failed: {e}")
            return {'error': str(e)}
    
    async def _integrate_comprehensive_results(self,
                                             session_id: str,
                                             core_results: Dict[str, Any],
                                             phase_c_results: Dict[str, Any],
                                             enhanced_content: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate all analysis results into comprehensive output"""
        
        return {
            'session_metadata': {
                'session_id': session_id,
                'analysis_type': 'comprehensive_multi_phase',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'phases_enabled': {
                    'phase_a': True,  # Always enabled
                    'phase_b': FeatureFlags.ENHANCED_ANALYTICS_ENABLED,
                    'phase_c_bayesian': FeatureFlags.BAYESIAN_PIPELINE_ENABLED,
                    'phase_c_event_shock': FeatureFlags.EVENT_SHOCK_MODELING_ENABLED,
                    'phase_c_hybrid_search': FeatureFlags.HYBRID_VECTOR_STORE_ENABLED,
                    'phase_c_enhanced_content': FeatureFlags.ENHANCED_CONTENT_PROCESSING_ENABLED
                }
            },
            'core_analysis': core_results,
            'phase_c_enhancements': phase_c_results,
            'enhanced_content_analysis': enhanced_content.get('enhanced_quality_analysis', {}),
            'comprehensive_insights': await self._generate_comprehensive_insights(
                core_results, phase_c_results
            ),
            'confidence_metrics': self._calculate_comprehensive_confidence(
                core_results, phase_c_results
            )
        }
    
    async def _generate_comprehensive_insights(self,
                                             core_results: Dict[str, Any],
                                             phase_c_results: Dict[str, Any]) -> List[str]:
        """Generate comprehensive insights from all analysis phases"""
        insights = []
        
        # Core analysis insights
        if 'layer_scores' in core_results:
            layer_count = len(core_results['layer_scores'])
            insights.append(f"Core analysis evaluated {layer_count} strategic layers")
        
        # Phase C specific insights
        if 'bayesian_analysis' in phase_c_results:
            bayesian_data = phase_c_results['bayesian_analysis']
            categories_blended = bayesian_data.get('bayesian_metadata', {}).get('categories_blended', 0)
            insights.append(f"Bayesian analysis blended {categories_blended} strategic categories with probabilistic inference")
        
        if 'event_shock_analysis' in phase_c_results:
            shock_data = phase_c_results['event_shock_analysis']
            events_count = shock_data.get('events_modeled', 0)
            insights.append(f"Event shock modeling analyzed {events_count} potential market disruptions with temporal decay")
        
        if 'hybrid_search_analysis' in phase_c_results:
            search_data = phase_c_results['hybrid_search_analysis']
            total_results = search_data.get('total_results', 0)
            insights.append(f"Hybrid vector search retrieved {total_results} contextual documents from multiple knowledge stores")
        
        # Overall assessment
        total_enhancements = len([k for k in phase_c_results.keys() if not k.endswith('_error')])
        insights.append(f"Analysis enhanced with {total_enhancements} advanced analytical capabilities")
        
        return insights
    
    def _calculate_comprehensive_confidence(self,
                                          core_results: Dict[str, Any],
                                          phase_c_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive confidence metrics"""
        # Base confidence from core analysis
        base_confidence = 0.7  # Default
        
        if 'overall_confidence' in core_results:
            base_confidence = core_results['overall_confidence']
        elif 'layer_scores' in core_results:
            layer_scores = core_results['layer_scores']
            if layer_scores:
                avg_layer_confidence = sum(ls.confidence for ls in layer_scores) / len(layer_scores)
                base_confidence = avg_layer_confidence
        
        # Enhancement confidence bonuses
        enhancement_bonus = 0.0
        enhancement_count = 0
        
        # Bayesian enhancement bonus
        if 'bayesian_analysis' in phase_c_results:
            bayesian_confidence = 0.5  # Default
            bayesian_data = phase_c_results['bayesian_analysis']
            if 'blended_category_results' in bayesian_data:
                confidences = []
                for blend_result in bayesian_data['blended_category_results'].values():
                    if hasattr(blend_result, 'confidence_score'):
                        confidences.append(blend_result.confidence_score)
                if confidences:
                    bayesian_confidence = sum(confidences) / len(confidences)
            
            enhancement_bonus += bayesian_confidence * 0.1
            enhancement_count += 1
        
        # Event shock modeling bonus
        if 'event_shock_analysis' in phase_c_results:
            enhancement_bonus += 0.05  # Fixed bonus for shock modeling
            enhancement_count += 1
        
        # Hybrid search bonus
        if 'hybrid_search_analysis' in phase_c_results:
            search_data = phase_c_results['hybrid_search_analysis']
            search_confidence = min(0.1, search_data.get('avg_similarity', 0.0))
            enhancement_bonus += search_confidence
            enhancement_count += 1
        
        # Final confidence calculation
        final_confidence = min(1.0, base_confidence + enhancement_bonus)
        
        return {
            'overall_confidence': final_confidence,
            'base_confidence': base_confidence,
            'enhancement_bonus': enhancement_bonus,
            'enhancements_applied': enhancement_count,
            'confidence_improvement': enhancement_bonus
        }
    
    async def _update_progress(self, session_id: str, stage: str, percentage: float):
        """Update analysis progress (placeholder implementation)"""
        try:
            # This would integrate with the existing session management
            logger.info(f"Session {session_id}: {stage} - {percentage}% complete")
        except Exception as e:
            logger.error(f"Progress update failed: {e}")
    
    async def _update_session_status(self, session_id: str, status: str):
        """Update session status (placeholder implementation)"""
        try:
            # This would integrate with the existing session management
            logger.info(f"Session {session_id}: Status updated to {status}")
        except Exception as e:
            logger.error(f"Status update failed: {e}")

__all__ = ['PhaseIntegratedAnalysisSessionManager']
