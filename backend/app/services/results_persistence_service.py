# backend/app/services/results_persistence_service.py

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.results_persistence_models import (
    ComputedFactors, PatternMatches, MonteCarloScenarios,
    ConsumerPersonas, SegmentRichContent, ResultsGenerationStatus
)
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResultsPersistenceService:
    """Service to persist and retrieve all analysis results from Cloud SQL"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # ============ PERSISTENCE METHODS ============
    
    def persist_factors(self, session_id: str, topic: str, segment: str, 
                       factors: Dict[str, Any]) -> None:
        """Persist computed factors to database"""
        
        logger.info(f"Persisting {len(factors)} factors for session {session_id}, segment {segment}")
        
        for factor_id, factor_data in factors.items():
            existing = self.db.query(ComputedFactors).filter(
                and_(
                    ComputedFactors.session_id == session_id,
                    ComputedFactors.factor_id == factor_id
                )
            ).first()
            
            if existing:
                # Update existing
                existing.factor_value = factor_data['value']
                existing.confidence = factor_data['confidence']
                existing.formula_applied = factor_data.get('formula_applied')
                existing.calculation_metadata = json.dumps(factor_data.get('metadata', {}))
            else:
                # Create new
                factor_record = ComputedFactors(
                    session_id=session_id,
                    topic=topic,
                    segment=segment,
                    factor_id=factor_id,
                    factor_value=factor_data['value'],
                    confidence=factor_data['confidence'],
                    formula_applied=factor_data.get('formula_applied'),
                    calculation_metadata=json.dumps(factor_data.get('metadata', {}))
                )
                self.db.add(factor_record)
        
        self.db.commit()
        logger.info(f"Successfully persisted factors for {session_id}")
    
    def persist_pattern_matches(self, session_id: str, topic: str, segment: str,
                               patterns: List[Dict[str, Any]]) -> None:
        """Persist matched patterns to database"""
        
        logger.info(f"Persisting {len(patterns)} patterns for session {session_id}, segment {segment}")
        
        # Delete existing patterns for this session/segment
        self.db.query(PatternMatches).filter(
            and_(
                PatternMatches.session_id == session_id,
                PatternMatches.segment == segment
            )
        ).delete()
        
        # Insert new patterns
        for pattern in patterns:
            pattern_record = PatternMatches(
                session_id=session_id,
                topic=topic,
                segment=segment,
                pattern_id=pattern['id'],
                pattern_name=pattern['name'],
                pattern_type=pattern['type'],
                confidence=pattern['confidence'],
                match_score=pattern.get('match_score', 0.7),
                strategic_response=pattern.get('strategic_response', ''),
                effect_size_hints=pattern.get('effect_size_hints', ''),
                probability_range=json.dumps(pattern.get('probability_range', [0.5, 0.8])),
                factors_triggered=json.dumps(pattern.get('factors', []))
            )
            self.db.add(pattern_record)
        
        self.db.commit()
        logger.info(f"Successfully persisted patterns for {session_id}")
    
    def persist_monte_carlo_scenarios(self, session_id: str, topic: str, segment: str,
                                     scenarios: List[Dict[str, Any]]) -> None:
        """Persist Monte Carlo scenarios to database"""
        
        logger.info(f"Persisting {len(scenarios)} scenarios for session {session_id}, segment {segment}")
        
        # Delete existing scenarios for this session/segment
        self.db.query(MonteCarloScenarios).filter(
            and_(
                MonteCarloScenarios.session_id == session_id,
                MonteCarloScenarios.segment == segment
            )
        ).delete()
        
        # Insert new scenarios
        for scenario in scenarios:
            scenario_record = MonteCarloScenarios(
                session_id=session_id,
                topic=topic,
                segment=segment,
                scenario_id=scenario['scenario_id'],
                pattern_id=scenario['pattern_id'],
                pattern_name=scenario['pattern_name'],
                strategic_response=scenario.get('strategic_response', ''),
                kpi_results=json.dumps(scenario['kpi_results']),
                probability_success=scenario['probability_success'],
                confidence_interval=json.dumps(scenario['confidence_interval']),
                iterations=scenario.get('iterations', 1000)
            )
            self.db.add(scenario_record)
        
        self.db.commit()
        logger.info(f"Successfully persisted scenarios for {session_id}")
    
    def persist_personas(self, session_id: str, topic: str, 
                        personas: List[Dict[str, Any]]) -> None:
        """Persist consumer personas to database"""
        
        logger.info(f"Persisting {len(personas)} personas for session {session_id}")
        
        # Delete existing personas for this session
        self.db.query(ConsumerPersonas).filter(
            ConsumerPersonas.session_id == session_id
        ).delete()
        
        # Insert new personas
        for persona in personas:
            persona_record = ConsumerPersonas(
                session_id=session_id,
                topic=topic,
                persona_name=persona['name'],
                age=persona.get('age'),
                demographics=json.dumps(persona.get('demographics', {})),
                psychographics=json.dumps(persona.get('psychographics', {})),
                pain_points=json.dumps(persona.get('pain_points', [])),
                goals=json.dumps(persona.get('goals', [])),
                buying_behavior=json.dumps(persona.get('buying_behavior', {})),
                market_share=persona.get('market_share', 0.0),
                value_tier=persona.get('value_tier', 'Mid'),
                key_messaging=json.dumps(persona.get('key_messaging', [])),
                confidence=persona.get('confidence', 0.7)
            )
            self.db.add(persona_record)
        
        self.db.commit()
        logger.info(f"Successfully persisted personas for {session_id}")
    
    def persist_rich_content(self, session_id: str, topic: str, segment: str,
                           content_type: str, content_data: Dict[str, Any]) -> None:
        """Persist rich content (Product/Brand/Experience) to database"""
        
        logger.info(f"Persisting rich content for session {session_id}, segment {segment}, type {content_type}")
        
        existing = self.db.query(SegmentRichContent).filter(
            and_(
                SegmentRichContent.session_id == session_id,
                SegmentRichContent.segment == segment,
                SegmentRichContent.content_type == content_type
            )
        ).first()
        
        if existing:
            existing.content_data = json.dumps(content_data)
        else:
            content_record = SegmentRichContent(
                session_id=session_id,
                topic=topic,
                segment=segment,
                content_type=content_type,
                content_data=json.dumps(content_data)
            )
            self.db.add(content_record)
        
        self.db.commit()
        logger.info(f"Successfully persisted rich content for {session_id}")
    
    # ============ RETRIEVAL METHODS ============
    
    def get_factors(self, session_id: str, segment: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve computed factors from database"""
        
        query = self.db.query(ComputedFactors).filter(
            ComputedFactors.session_id == session_id
        )
        
        if segment:
            query = query.filter(ComputedFactors.segment == segment)
        
        factors_records = query.all()
        
        factors = {}
        for record in factors_records:
            factors[record.factor_id] = {
                'value': float(record.factor_value),
                'confidence': float(record.confidence),
                'formula_applied': record.formula_applied,
                'metadata': json.loads(record.calculation_metadata) if record.calculation_metadata else {}
            }
        
        logger.info(f"Retrieved {len(factors)} factors for session {session_id}")
        return factors
    
    def get_pattern_matches(self, session_id: str, segment: str) -> List[Dict[str, Any]]:
        """Retrieve pattern matches from database"""
        
        patterns_records = self.db.query(PatternMatches).filter(
            and_(
                PatternMatches.session_id == session_id,
                PatternMatches.segment == segment
            )
        ).all()
        
        patterns = []
        for record in patterns_records:
            patterns.append({
                'id': record.pattern_id,
                'name': record.pattern_name,
                'type': record.pattern_type,
                'confidence': float(record.confidence),
                'match_score': float(record.match_score),
                'strategic_response': record.strategic_response,
                'effect_size_hints': record.effect_size_hints,
                'probability_range': json.loads(record.probability_range),
                'factors_triggered': json.loads(record.factors_triggered)
            })
        
        logger.info(f"Retrieved {len(patterns)} patterns for session {session_id}, segment {segment}")
        return patterns
    
    def get_monte_carlo_scenarios(self, session_id: str, segment: str) -> List[Dict[str, Any]]:
        """Retrieve Monte Carlo scenarios from database"""
        
        scenarios_records = self.db.query(MonteCarloScenarios).filter(
            and_(
                MonteCarloScenarios.session_id == session_id,
                MonteCarloScenarios.segment == segment
            )
        ).all()
        
        scenarios = []
        for record in scenarios_records:
            scenarios.append({
                'scenario_id': record.scenario_id,
                'pattern_id': record.pattern_id,
                'pattern_name': record.pattern_name,
                'strategic_response': record.strategic_response,
                'kpi_results': json.loads(record.kpi_results),
                'probability_success': float(record.probability_success),
                'confidence_interval': json.loads(record.confidence_interval),
                'iterations': record.iterations
            })
        
        logger.info(f"Retrieved {len(scenarios)} scenarios for session {session_id}, segment {segment}")
        return scenarios
    
    def get_personas(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve consumer personas from database"""
        
        personas_records = self.db.query(ConsumerPersonas).filter(
            ConsumerPersonas.session_id == session_id
        ).all()
        
        personas = []
        for record in personas_records:
            personas.append({
                'name': record.persona_name,
                'age': record.age,
                'demographics': json.loads(record.demographics) if record.demographics else {},
                'psychographics': json.loads(record.psychographics) if record.psychographics else {},
                'pain_points': json.loads(record.pain_points) if record.pain_points else [],
                'goals': json.loads(record.goals) if record.goals else [],
                'buying_behavior': json.loads(record.buying_behavior) if record.buying_behavior else {},
                'market_share': float(record.market_share) if record.market_share else 0.0,
                'value_tier': record.value_tier,
                'key_messaging': json.loads(record.key_messaging) if record.key_messaging else [],
                'confidence': float(record.confidence) if record.confidence else 0.7
            })
        
        logger.info(f"Retrieved {len(personas)} personas for session {session_id}")
        return personas
    
    def get_rich_content(self, session_id: str, segment: str, content_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve rich content from database"""
        
        content_record = self.db.query(SegmentRichContent).filter(
            and_(
                SegmentRichContent.session_id == session_id,
                SegmentRichContent.segment == segment,
                SegmentRichContent.content_type == content_type
            )
        ).first()
        
        if content_record:
            logger.info(f"Retrieved rich content for session {session_id}, segment {segment}, type {content_type}")
            return json.loads(content_record.content_data)
        
        logger.info(f"No rich content found for session {session_id}, segment {segment}, type {content_type}")
        return None
    
    # ============ STATUS TRACKING ============
    
    def create_generation_status(self, session_id: str, topic: str) -> None:
        """Create results generation status record"""
        
        existing = self.db.query(ResultsGenerationStatus).filter(
            ResultsGenerationStatus.session_id == session_id
        ).first()
        
        if not existing:
            status_record = ResultsGenerationStatus(
                session_id=session_id,
                topic=topic,
                status='pending',
                progress_percentage=0
            )
            self.db.add(status_record)
            self.db.commit()
            logger.info(f"Created generation status for session {session_id}")
    
    def update_generation_status(self, session_id: str, status: str, 
                                 current_stage: Optional[str] = None,
                                 progress: Optional[int] = None,
                                 completed_segments: Optional[int] = None,
                                 error_message: Optional[str] = None) -> None:
        """Update results generation status"""
        
        status_record = self.db.query(ResultsGenerationStatus).filter(
            ResultsGenerationStatus.session_id == session_id
        ).first()
        
        if status_record:
            status_record.status = status
            if current_stage:
                status_record.current_stage = current_stage
            if progress is not None:
                status_record.progress_percentage = progress
            if completed_segments is not None:
                status_record.completed_segments = completed_segments
            if error_message:
                status_record.error_message = error_message
            
            if status == 'processing' and not status_record.started_at:
                status_record.started_at = datetime.utcnow()
            elif status == 'completed':
                status_record.completed_at = datetime.utcnow()
                status_record.progress_percentage = 100
            
            status_record.updated_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Updated generation status for session {session_id}: {status}")
    
    def get_generation_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get results generation status"""
        
        status_record = self.db.query(ResultsGenerationStatus).filter(
            ResultsGenerationStatus.session_id == session_id
        ).first()
        
        if status_record:
            return {
                'session_id': status_record.session_id,
                'topic': status_record.topic,
                'status': status_record.status,
                'current_stage': status_record.current_stage,
                'progress_percentage': status_record.progress_percentage,
                'completed_segments': status_record.completed_segments,
                'total_segments': status_record.total_segments,
                'started_at': status_record.started_at.isoformat() if status_record.started_at else None,
                'completed_at': status_record.completed_at.isoformat() if status_record.completed_at else None,
                'error_message': status_record.error_message
            }
        
        return None
    
    def results_exist(self, session_id: str) -> bool:
        """Check if complete results exist for session"""
        
        status = self.get_generation_status(session_id)
        return status is not None and status['status'] == 'completed'
