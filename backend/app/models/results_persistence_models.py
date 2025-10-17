# backend/app/models/results_persistence_models.py

from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

# Create SQLAlchemy declarative base for ORM models
Base = declarative_base()

class ComputedFactors(Base):
    __tablename__ = 'computed_factors'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    segment = Column(String(50), nullable=False)
    factor_id = Column(String(10), nullable=False)
    factor_value = Column(DECIMAL(10,6), nullable=False)
    confidence = Column(DECIMAL(10,6), nullable=False)
    formula_applied = Column(Text)
    calculation_metadata = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_factors_session', 'session_id'),
        Index('idx_factors_segment', 'session_id', 'segment'),
        {'extend_existing': True}
    )

class PatternMatches(Base):
    __tablename__ = 'pattern_matches'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    segment = Column(String(50), nullable=False)
    pattern_id = Column(String(10), nullable=False)
    pattern_name = Column(String(255), nullable=False)
    pattern_type = Column(String(50), nullable=False)
    confidence = Column(DECIMAL(10,6), nullable=False)
    match_score = Column(DECIMAL(10,6), nullable=False)
    strategic_response = Column(Text)
    effect_size_hints = Column(Text)
    probability_range = Column(JSON)
    factors_triggered = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_patterns_session', 'session_id'),
        Index('idx_patterns_segment', 'session_id', 'segment'),
        {'extend_existing': True}
    )

class MonteCarloScenarios(Base):
    __tablename__ = 'monte_carlo_scenarios'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    segment = Column(String(50), nullable=False)
    scenario_id = Column(String(100), nullable=False)
    pattern_id = Column(String(10), nullable=False)
    pattern_name = Column(String(255), nullable=False)
    strategic_response = Column(Text)
    kpi_results = Column(JSON, nullable=False)
    probability_success = Column(DECIMAL(10,6), nullable=False)
    confidence_interval = Column(JSON, nullable=False)
    iterations = Column(Integer, default=1000)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_scenarios_session', 'session_id'),
        Index('idx_scenarios_segment', 'session_id', 'segment'),
        {'extend_existing': True}
    )

class ConsumerPersonas(Base):
    __tablename__ = 'consumer_personas'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    persona_name = Column(String(255), nullable=False)
    age = Column(String(50))
    demographics = Column(JSON)
    psychographics = Column(JSON)
    pain_points = Column(JSON)
    goals = Column(JSON)
    buying_behavior = Column(JSON)
    market_share = Column(DECIMAL(10,6))
    value_tier = Column(String(50))
    key_messaging = Column(JSON)
    confidence = Column(DECIMAL(10,6))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_personas_session', 'session_id'),
        {'extend_existing': True}
    )

class SegmentRichContent(Base):
    __tablename__ = 'segment_rich_content'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    segment = Column(String(50), nullable=False)
    content_type = Column(String(100), nullable=False)
    content_data = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_rich_content_session', 'session_id'),
        {'extend_existing': True}
    )

class ResultsGenerationStatus(Base):
    __tablename__ = 'results_generation_status'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    topic = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    current_stage = Column(String(100))
    progress_percentage = Column(Integer, default=0)
    total_segments = Column(Integer, default=5)
    completed_segments = Column(Integer, default=0)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    error_message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_results_status', 'session_id', 'status'),
        {'extend_existing': True}
    )
