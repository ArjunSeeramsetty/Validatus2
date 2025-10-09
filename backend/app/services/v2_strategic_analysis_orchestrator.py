"""
Validatus v2.0 Strategic Analysis Orchestrator
Coordinates complete 210-layer → 28-factor → 5-segment analysis workflow
"""
import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime, timezone

from ..core.aliases_config import aliases_config
from ..core.database_config import db_manager
from ..services.v2_expert_persona_scorer import V2ExpertPersonaScorer, LayerScore
from ..services.v2_factor_calculation_engine import V2FactorCalculationEngine, FactorCalculation
from ..services.v2_segment_analysis_engine import V2SegmentAnalysisEngine, SegmentAnalysis

logger = logging.getLogger(__name__)

class V2StrategicAnalysisOrchestrator:
    """Master orchestrator for complete v2.0 strategic analysis workflow"""
    
    def __init__(self):
        self.aliases = aliases_config
        self.layer_scorer = V2ExpertPersonaScorer()
        self.factor_engine = V2FactorCalculationEngine()
        self.segment_engine = V2SegmentAnalysisEngine()
    
    async def execute_complete_analysis(self, session_id: str, 
                                      topic_knowledge: Dict) -> Dict[str, Any]:
        """
        Execute complete 210-layer strategic analysis workflow
        
        Workflow:
        1. Score 210 layers using expert personas + Gemini LLM
        2. Calculate 28 factors from layer scores
        3. Analyze 5 segments from factor calculations
        4. Generate scenarios and recommendations
        5. Store all results in database
        
        Args:
            session_id: Unique session identifier
            topic_knowledge: Dict with topic info and scraped content
            
        Returns:
            Complete analysis results
        """
        analysis_start = datetime.now(timezone.utc)
        logger.info(f"🚀 Starting v2.0 complete strategic analysis for session {session_id}")
        logger.info(f"   Content items: {len(topic_knowledge.get('content_items', []))}")
        
        try:
            # Phase 1: Layer Scoring (210 layers)
            logger.info("📊 Phase 1: Scoring 210 strategic layers...")
            layer_start = datetime.now(timezone.utc)
            layer_scores = await self._execute_layer_scoring_phase(session_id, topic_knowledge)
            layer_time = (datetime.now(timezone.utc) - layer_start).total_seconds()
            logger.info(f"   ✅ {len(layer_scores)} layers scored in {layer_time:.1f}s")
            
            # Phase 2: Factor Calculations (28 factors)  
            logger.info("🧮 Phase 2: Calculating 28 strategic factors...")
            factor_start = datetime.now(timezone.utc)
            factor_calculations = await self.factor_engine.calculate_all_factors(
                session_id, layer_scores
            )
            factor_time = (datetime.now(timezone.utc) - factor_start).total_seconds()
            logger.info(f"   ✅ {len(factor_calculations)} factors calculated in {factor_time:.1f}s")
            
            # Phase 3: Segment Analysis (5 segments)
            logger.info("🎯 Phase 3: Analyzing 5 intelligence segments...")
            segment_start = datetime.now(timezone.utc)
            segment_analyses = await self.segment_engine.analyze_all_segments(
                session_id, factor_calculations
            )
            segment_time = (datetime.now(timezone.utc) - segment_start).total_seconds()
            logger.info(f"   ✅ {len(segment_analyses)} segments analyzed in {segment_time:.1f}s")
            
            # Phase 4: Calculate Overall Business Case Score
            logger.info("💼 Phase 4: Calculating overall business case score...")
            overall_score = self._calculate_overall_business_case_score(
                layer_scores, factor_calculations, segment_analyses
            )
            
            # Phase 5: Generate Scenarios
            logger.info("🎲 Phase 5: Generating strategic scenarios...")
            scenarios = self._generate_strategic_scenarios(
                overall_score, layer_scores, factor_calculations, segment_analyses
            )
            
            # Calculate total processing time
            total_time = (datetime.now(timezone.utc) - analysis_start).total_seconds()
            
            # Compile final results
            final_results = {
                'session_id': session_id,
                'analysis_type': 'validatus_v2_complete',
                'version': '2.0',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'processing_time_seconds': round(total_time, 2),
                
                # Core Analysis Results
                'overall_business_case_score': round(overall_score, 4),
                'overall_confidence': self._calculate_overall_confidence(layer_scores, factor_calculations),
                
                # Detailed Results
                'layer_scores': [self._format_layer_score(ls) for ls in layer_scores],
                'factor_calculations': [self._format_factor_calc(fc) for fc in factor_calculations],
                'segment_analyses': [self._format_segment_analysis(sa) for sa in segment_analyses],
                'scenarios': scenarios,
                
                # Summary Metrics
                'summary': {
                    'layers_analyzed': len(layer_scores),
                    'factors_calculated': len(factor_calculations),
                    'segments_evaluated': len(segment_analyses),
                    'scenarios_generated': len(scenarios),
                    'content_items_processed': len(topic_knowledge.get('content_items', [])),
                    'processing_breakdown': {
                        'layer_scoring_seconds': round(layer_time, 2),
                        'factor_calculation_seconds': round(factor_time, 2),
                        'segment_analysis_seconds': round(segment_time, 2),
                        'total_seconds': round(total_time, 2)
                    }
                },
                
                # Configuration Metadata
                'configuration': {
                    'segments_count': 5,
                    'factors_count': 28,
                    'layers_count': 210,
                    'distribution': '30+50+50+50+30',
                    'version': '2.0',
                    'framework': 'Validatus Strategic Intelligence Platform'
                }
            }
            
            # Store comprehensive results in database
            await self._store_complete_analysis(session_id, final_results, 
                                              layer_scores, factor_calculations, segment_analyses)
            
            logger.info(f"✅ v2.0 Strategic analysis completed in {total_time:.2f}s")
            logger.info(f"   Overall Score: {overall_score:.3f}")
            logger.info(f"   Confidence: {final_results['overall_confidence']:.3f}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ v2.0 Strategic analysis failed for {session_id}: {e}")
            raise
    
    async def _execute_layer_scoring_phase(self, session_id: str, 
                                         topic_knowledge: Dict) -> List[LayerScore]:
        """Execute comprehensive layer scoring for all 210 layers"""
        
        # Get all 210 layer IDs from configuration
        all_layer_ids = self.aliases.get_all_layer_ids()
        logger.info(f"   Processing {len(all_layer_ids)} layers in batches")
        
        # Process in batches to avoid memory/timeout issues
        batch_size = 30  # Process 30 layers at a time
        all_layer_scores = []
        
        for i in range(0, len(all_layer_ids), batch_size):
            batch_layers = all_layer_ids[i:i+batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(all_layer_ids) + batch_size - 1) // batch_size
            
            logger.info(f"   Batch {batch_num}/{total_batches}: Scoring {len(batch_layers)} layers")
            
            try:
                batch_scores = await self.layer_scorer.score_layer_batch(
                    session_id, topic_knowledge, batch_layers
                )
                all_layer_scores.extend(batch_scores)
                
                # Store batch results immediately for reliability
                await self._store_layer_scores_batch(batch_scores)
                
                logger.info(f"   ✓ Batch {batch_num} completed: {len(batch_scores)} layers scored")
                
            except Exception as e:
                logger.error(f"   ✗ Batch {batch_num} failed: {e}")
                # Continue with next batch even if one fails
        
        return all_layer_scores
    
    async def _store_layer_scores_batch(self, layer_scores: List[LayerScore]):
        """Store batch of layer scores to database"""
        try:
            import json
            connection = await db_manager.get_connection()
            
            for layer_score in layer_scores:
                await connection.execute(
                    """
                    INSERT INTO layer_scores 
                    (session_id, layer_id, score, confidence, evidence_count, 
                     key_insights, evidence_summary, llm_analysis_raw, expert_persona, 
                     processing_time_ms, metadata, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT DO NOTHING
                    """,
                    layer_score.session_id,
                    layer_score.layer_id,
                    layer_score.score,
                    layer_score.confidence,
                    layer_score.evidence_count,
                    layer_score.key_insights,
                    layer_score.evidence_summary,
                    layer_score.llm_analysis_raw,
                    layer_score.expert_persona,
                    layer_score.processing_time_ms,
                    json.dumps(layer_score.metadata) if isinstance(layer_score.metadata, dict) else layer_score.metadata,
                    layer_score.created_at
                )
                
        except Exception as e:
            logger.error(f"Failed to store layer scores batch: {e}")
    
    async def _store_complete_analysis(self, session_id: str, results: Dict,
                                     layer_scores: List, factor_calculations: List,
                                     segment_analyses: List):
        """Store complete analysis results to database"""
        try:
            connection = await db_manager.get_connection()
            
            # Store factor calculations
            for fc in factor_calculations:
                await connection.execute(
                    """
                    INSERT INTO factor_calculations
                    (session_id, factor_id, calculated_value, confidence_score, 
                     input_layer_count, calculation_method, layer_contributions, 
                     validation_metrics, metadata, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT DO NOTHING
                    """,
                    fc.session_id, fc.factor_id, fc.calculated_value, fc.confidence_score,
                    fc.input_layer_count, fc.calculation_method, 
                    json.dumps(fc.layer_contributions) if isinstance(fc.layer_contributions, dict) else fc.layer_contributions,
                    json.dumps(fc.validation_metrics) if isinstance(fc.validation_metrics, dict) else fc.validation_metrics,
                    json.dumps(fc.metadata) if isinstance(fc.metadata, dict) else fc.metadata,
                    fc.created_at
                )
            
            # Store segment analyses
            for sa in segment_analyses:
                await connection.execute(
                    """
                    INSERT INTO segment_analysis
                    (session_id, segment_id, attractiveness_score, competitive_intensity,
                     market_size_score, growth_potential, overall_segment_score,
                     key_insights, risk_factors, opportunities, recommendations,
                     factor_contributions, metadata, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    ON CONFLICT DO NOTHING
                    """,
                    sa.session_id, sa.segment_id, sa.attractiveness_score, sa.competitive_intensity,
                    sa.market_size_score, sa.growth_potential, sa.overall_segment_score,
                    sa.key_insights, sa.risk_factors, sa.opportunities, sa.recommendations,
                    json.dumps(sa.factor_contributions) if isinstance(sa.factor_contributions, dict) else sa.factor_contributions,
                    json.dumps(sa.metadata) if isinstance(sa.metadata, dict) else sa.metadata,
                    sa.created_at
                )
            
            # Store comprehensive results
            await connection.execute(
                """
                INSERT INTO v2_analysis_results
                (session_id, analysis_type, overall_business_case_score, overall_confidence,
                 layers_analyzed, factors_calculated, segments_evaluated, scenarios_generated,
                 processing_time_seconds, content_items_analyzed, analysis_summary, 
                 full_results, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                ON CONFLICT (session_id) DO UPDATE SET
                    overall_business_case_score = EXCLUDED.overall_business_case_score,
                    overall_confidence = EXCLUDED.overall_confidence,
                    full_results = EXCLUDED.full_results,
                    updated_at = NOW()
                """,
                session_id, results['analysis_type'], results['overall_business_case_score'],
                results['overall_confidence'], results['summary']['layers_analyzed'],
                results['summary']['factors_calculated'], results['summary']['segments_evaluated'],
                results['summary']['scenarios_generated'], results['processing_time_seconds'],
                results['summary']['content_items_processed'], 
                json.dumps(results['summary']) if isinstance(results['summary'], dict) else results['summary'],
                json.dumps(results) if isinstance(results, dict) else results,
                json.dumps(results.get('configuration', {})) if isinstance(results.get('configuration'), dict) else results.get('configuration', {}),
                datetime.now(timezone.utc)
            )
            
            logger.info(f"✅ Complete analysis stored for {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to store complete analysis: {e}")
    
    def _calculate_overall_business_case_score(self, layer_scores: List[LayerScore],
                                              factor_calculations: List[FactorCalculation],
                                              segment_analyses: List[SegmentAnalysis]) -> float:
        """Calculate overall business case score from segment analyses"""
        
        if not segment_analyses:
            return 0.5
        
        # Weight segments equally (0.2 each) for overall score
        segment_weights = {
            'S1': 0.25,  # Product Intelligence - slightly higher
            'S2': 0.20,  # Consumer Intelligence
            'S3': 0.25,  # Market Intelligence - slightly higher
            'S4': 0.15,  # Brand Intelligence
            'S5': 0.15   # Experience Intelligence
        }
        
        overall_score = 0.0
        total_weight = 0.0
        
        for segment_analysis in segment_analyses:
            weight = segment_weights.get(segment_analysis.segment_id, 0.2)
            overall_score += segment_analysis.overall_segment_score * weight
            total_weight += weight
        
        return overall_score / total_weight if total_weight > 0 else 0.5
    
    def _calculate_overall_confidence(self, layer_scores: List[LayerScore],
                                     factor_calculations: List[FactorCalculation]) -> float:
        """Calculate overall confidence from layer and factor confidences"""
        
        # Combine layer and factor confidences
        all_confidences = []
        
        for ls in layer_scores:
            all_confidences.append(ls.confidence)
        
        for fc in factor_calculations:
            all_confidences.append(fc.confidence_score)
        
        if not all_confidences:
            return 0.5
        
        # Use weighted average with factor confidences having higher weight
        layer_weight = 0.4
        factor_weight = 0.6
        
        layer_conf = sum(ls.confidence for ls in layer_scores) / len(layer_scores) if layer_scores else 0.5
        factor_conf = sum(fc.confidence_score for fc in factor_calculations) / len(factor_calculations) if factor_calculations else 0.5
        
        overall_conf = layer_conf * layer_weight + factor_conf * factor_weight
        return round(overall_conf, 4)
    
    def _generate_strategic_scenarios(self, overall_score: float,
                                    layer_scores: List[LayerScore],
                                    factor_calculations: List[FactorCalculation],
                                    segment_analyses: List[SegmentAnalysis]) -> List[Dict]:
        """Generate strategic scenarios based on analysis results"""
        
        scenarios = [
            {
                'name': 'Base Case',
                'description': 'Current trajectory with existing conditions',
                'probability': 0.50,
                'business_case_score': round(overall_score, 3),
                'key_assumptions': [
                    'Market conditions remain stable',
                    'Competitive landscape unchanged',
                    'Current execution capability maintained'
                ]
            },
            {
                'name': 'Optimistic Scenario',
                'description': 'Favorable conditions and strong execution',
                'probability': 0.25,
                'business_case_score': round(min(overall_score + 0.15, 1.0), 3),
                'key_assumptions': [
                    'Market growth accelerates',
                    'Strong competitive positioning achieved',
                    'Execution exceeds expectations',
                    'Customer adoption surpasses projections'
                ]
            },
            {
                'name': 'Pessimistic Scenario',
                'description': 'Challenges and headwinds materialize',
                'probability': 0.25,
                'business_case_score': round(max(overall_score - 0.15, 0.0), 3),
                'key_assumptions': [
                    'Market growth slows',
                    'Competitive pressures increase',
                    'Execution faces obstacles',
                    'Customer adoption below expectations'
                ]
            }
        ]
        
        # Add segment-specific scenario insights
        for scenario in scenarios:
            scenario['segment_implications'] = {}
            for sa in segment_analyses:
                if scenario['name'] == 'Optimistic Scenario':
                    adjusted_score = min(sa.overall_segment_score + 0.1, 1.0)
                elif scenario['name'] == 'Pessimistic Scenario':
                    adjusted_score = max(sa.overall_segment_score - 0.1, 0.0)
                else:
                    adjusted_score = sa.overall_segment_score
                
                scenario['segment_implications'][sa.segment_name] = {
                    'score': round(adjusted_score, 3),
                    'key_driver': sa.opportunities[0] if sa.opportunities else 'Strategic positioning'
                }
        
        return scenarios
    
    def _format_layer_score(self, layer_score: LayerScore) -> Dict:
        """Format layer score for API response"""
        return {
            'layer_id': layer_score.layer_id,
            'layer_name': layer_score.layer_name,
            'score': layer_score.score,
            'confidence': layer_score.confidence,
            'evidence_count': layer_score.evidence_count,
            'insights': layer_score.key_insights,
            'expert_persona': layer_score.expert_persona,
            'factor_id': layer_score.metadata.get('factor_id'),
            'segment_id': layer_score.metadata.get('segment_id')
        }
    
    def _format_factor_calc(self, factor_calc: FactorCalculation) -> Dict:
        """Format factor calculation for API response"""
        return {
            'factor_id': factor_calc.factor_id,
            'factor_name': factor_calc.factor_name,
            'value': factor_calc.calculated_value,
            'confidence': factor_calc.confidence_score,
            'input_layers': factor_calc.input_layer_count,
            'calculation_method': factor_calc.calculation_method,
            'segment_id': factor_calc.metadata.get('segment_id')
        }
    
    def _format_segment_analysis(self, segment_analysis: SegmentAnalysis) -> Dict:
        """Format segment analysis for API response"""
        return {
            'segment_id': segment_analysis.segment_id,
            'segment_name': segment_analysis.segment_name,
            'attractiveness': segment_analysis.attractiveness_score,
            'competitive_intensity': segment_analysis.competitive_intensity,
            'market_size': segment_analysis.market_size_score,
            'growth_potential': segment_analysis.growth_potential,
            'overall_score': segment_analysis.overall_segment_score,
            'insights': segment_analysis.key_insights,
            'risks': segment_analysis.risk_factors,
            'opportunities': segment_analysis.opportunities,
            'recommendations': segment_analysis.recommendations
        }

# Global orchestrator instance
try:
    v2_orchestrator = V2StrategicAnalysisOrchestrator()
    logger.info("✅ V2 Strategic Analysis Orchestrator initialized")
except Exception as e:
    logger.error(f"Failed to initialize V2 Orchestrator: {e}")
    v2_orchestrator = None

