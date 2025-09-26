# backend/app/models/analysis_models.py

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel

class AnalysisStatus(Enum):
    """Analysis session status enumeration"""
    INITIALIZED = "initialized"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    ERROR = "error"

class DuplicateType(Enum):
    """Content duplication type enumeration"""
    EXACT = "exact"
    NEAR_EXACT = "near_exact"
    SEMANTIC = "semantic"
    PARTIAL = "partial"

@dataclass
class AnalysisSession:
    """Strategic analysis session model"""
    session_id: str
    topic: str
    user_id: str
    status: AnalysisStatus
    parameters: Dict[str, Any]
    created_at: datetime
    last_updated: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    total_layers: int = 0
    completed_layers: int = 0
    total_factors: int = 0
    completed_factors: int = 0

@dataclass
class AnalysisProgress:
    """Analysis progress tracking model"""
    session_id: str
    current_stage: str
    completed_layers: List[str]
    completed_factors: List[str]
    completed_segments: List[str]
    progress_percentage: float
    estimated_completion: str
    error_messages: List[str]
    last_updated: datetime

@dataclass
class LayerScore:
    """Strategic layer scoring result model"""
    session_id: str
    layer_name: str
    score: float
    confidence: float
    evidence_count: int
    key_insights: List[str]
    evidence_summary: str
    calculation_metadata: Dict[str, Any]
    created_at: datetime

@dataclass
class FactorCalculation:
    """Strategic factor calculation result model"""
    session_id: str
    factor_name: str
    formula_used: str
    input_layers: List[str]
    calculated_value: float
    confidence_score: float
    calculation_steps: List[Dict[str, Any]]
    validation_metrics: Dict[str, float]
    created_at: datetime

@dataclass
class SegmentScore:
    """Market segment analysis result model"""
    session_id: str
    segment_name: str
    attractiveness_score: float
    competitive_intensity: float
    market_size: float
    growth_potential: float
    key_drivers: List[str]
    risk_factors: List[str]
    opportunity_metrics: Dict[str, float]
    created_at: datetime

@dataclass
class ContentQualityScores:
    """Content quality assessment model"""
    overall_score: float
    topic_relevance: float
    readability: float
    domain_authority: float
    content_freshness: float
    factual_accuracy: float
    completeness: float
    uniqueness: float
    engagement_potential: float
    assessment_metadata: Dict[str, Any]

@dataclass
class DuplicationResult:
    """Content duplication analysis result"""
    is_duplicate: bool
    similarity_score: float
    duplicate_type: DuplicateType
    source_document: str
    confidence: float
    matching_content: Optional[str] = None

@dataclass
class TopicClassification:
    """Topic classification result model"""
    primary_category: str
    secondary_categories: List[str]
    confidence_scores: Dict[str, float]
    topic_keywords: List[str]
    semantic_clusters: List[Dict[str, Any]]
    classification_metadata: Dict[str, Any]

@dataclass
class OptimizationMetrics:
    """Analysis optimization metrics model"""
    processing_time: float
    memory_usage: float
    cache_hit_rate: float
    error_rate: float
    throughput: float
    quality_score: float
    parallel_efficiency: float
    resource_utilization: Dict[str, float]

@dataclass
class EnhancedTopicMetadata:
    """Enhanced topic metadata with quality metrics"""
    topic: str
    topic_id: str
    classification_scores: Dict[str, float]
    quality_distribution: Dict[str, int]
    semantic_clusters: List[Dict[str, Any]]
    processing_metrics: Dict[str, float]
    created_at: str
    last_updated: str
    total_documents: int = 0
    high_quality_documents: int = 0
    average_quality_score: float = 0.0

@dataclass
class AnalysisResults:
    """Complete analysis results model"""
    session_id: str
    topic: str
    user_id: str
    status: AnalysisStatus
    layer_scores: List[LayerScore]
    factor_calculations: List[FactorCalculation]
    segment_scores: List[SegmentScore]
    enhanced_analysis: Dict[str, Any]
    comprehensive_insights: List[str]
    unified_recommendations: List[str]
    confidence_metrics: Dict[str, float]
    processing_metadata: Dict[str, Any]
    created_at: datetime
    completed_at: datetime

class ExportFormat(Enum):
    """Export format enumeration"""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    CSV = "csv"

@dataclass
class ExportRequest:
    """Analysis results export request model"""
    session_id: str
    user_id: str
    export_format: ExportFormat
    include_charts: bool = True
    include_raw_data: bool = False
    include_metadata: bool = True
    custom_filters: Optional[Dict[str, Any]] = None
    requested_at: Optional[datetime] = None

@dataclass
class ExportResult:
    """Export operation result model"""
    export_id: str
    session_id: str
    user_id: str
    export_format: ExportFormat
    created_at: datetime
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    export_status: str = "pending"
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None

# Migrated Data Models
class MigratedSessionInfo(BaseModel):
    """Information about a migrated v2 session"""
    session_id: str
    topic: str
    status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    analysis_metadata: Dict[str, Any] = {}
    migration_info: Dict[str, Any] = {}

class MigratedTopicInfo(BaseModel):
    """Information about a migrated topic"""
    name: str
    display_name: str
    session_id: Optional[str] = None
    status: str = "completed"
    type: str = "migrated"
    has_results: bool = True
    has_vector_store: bool = False
    migration_date: Optional[str] = None

class VectorQueryResult(BaseModel):
    """Result from vector store query"""
    content: str
    metadata: Dict[str, Any] = {}
    relevance_score: float = 0.8

class VectorQueryResponse(BaseModel):
    """Response from vector store query"""
    query: str
    results: List[VectorQueryResult] = []
    total_results: int = 0
    search_time_ms: int = 0
    collection_info: Optional[Dict[str, Any]] = None

class EvidenceItem(BaseModel):
    """Evidence item for migrated data"""
    url: str
    title: str
    content_preview: str
    quality_score: float
    scraped_at: Optional[str] = None
    metadata: Dict[str, Any] = {}

class EvidenceLayer(BaseModel):
    """Evidence layer grouping"""
    layer_name: str
    evidence_count: int
    evidence_items: List[EvidenceItem] = []

# Export all models
__all__ = [
    'AnalysisStatus', 'DuplicateType', 'ExportFormat',
    'AnalysisSession', 'AnalysisProgress', 'LayerScore', 'FactorCalculation',
    'SegmentScore', 'ContentQualityScores', 'DuplicationResult',
    'TopicClassification', 'OptimizationMetrics', 'EnhancedTopicMetadata',
    'AnalysisResults', 'ExportRequest', 'ExportResult',
    'MigratedSessionInfo', 'MigratedTopicInfo', 'VectorQueryResult',
    'VectorQueryResponse', 'EvidenceItem', 'EvidenceLayer'
]
