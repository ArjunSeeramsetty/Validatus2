# backend/app/models/api_models.py

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Request Models

class TopicCreateRequest(BaseModel):
    """Request model for creating a topic"""
    topic: str = Field(..., description="Topic name for analysis", min_length=1, max_length=100)
    urls: List[HttpUrl] = Field(..., description="List of URLs to analyze", min_items=1, max_items=100)

class URLCollectionRequest(BaseModel):
    """Request model for URL collection"""
    search_query: str = Field(..., description="Search query for URL collection", min_length=1, max_length=200)
    max_urls: int = Field(default=50, description="Maximum number of URLs to collect", ge=1, le=1000)
    language: Optional[str] = Field(default="en", description="Language for search results")

class EnhancedTopicCreateRequest(BaseModel):
    """Request model for creating enhanced topic"""
    topic: str = Field(..., description="Topic name for enhanced analysis", min_length=1, max_length=100)
    urls: List[HttpUrl] = Field(..., description="List of URLs to analyze", min_items=1, max_items=100)
    quality_threshold: float = Field(default=0.6, description="Minimum quality threshold", ge=0.0, le=1.0)

class EnhancedTopicUpdateRequest(BaseModel):
    """Request model for updating enhanced topic"""
    new_urls: List[HttpUrl] = Field(..., description="New URLs to add", min_items=1, max_items=100)
    quality_threshold: float = Field(default=0.6, description="Updated quality threshold", ge=0.0, le=1.0)

class AnalysisSessionCreateRequest(BaseModel):
    """Request model for creating analysis session"""
    topic: str = Field(..., description="Topic for strategic analysis", min_length=1, max_length=100)
    user_id: str = Field(..., description="User ID creating the session", min_length=1, max_length=100)
    analysis_parameters: Optional[Dict[str, Any]] = Field(default={}, description="Analysis parameters")

class ContentQualityAnalysisRequest(BaseModel):
    """Request model for content quality analysis"""
    content: str = Field(..., description="Content to analyze", min_length=1, max_length=100000)
    url: HttpUrl = Field(..., description="URL of the content")
    topic: str = Field(..., description="Topic context for analysis", min_length=1, max_length=100)

class ContentDeduplicationRequest(BaseModel):
    """Request model for content deduplication"""
    documents: List[Dict[str, Any]] = Field(..., description="Documents to deduplicate", min_items=1, max_items=1000)
    similarity_threshold: float = Field(default=0.85, description="Similarity threshold for deduplication", ge=0.0, le=1.0)

class ParallelProcessingRequest(BaseModel):
    """Request model for parallel processing optimization"""
    analysis_tasks: List[Dict[str, Any]] = Field(..., description="Analysis tasks to process", min_items=1, max_items=100)
    max_concurrent: int = Field(default=10, description="Maximum concurrent tasks", ge=1, le=50)

# Response Models

class APIResponse(BaseModel):
    """Base API response model"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class TopicListResponse(APIResponse):
    """Response model for topic list"""
    topics: List[str] = Field(..., description="List of available topics")
    total_count: int = Field(..., description="Total number of topics")

class TopicCreateResponse(APIResponse):
    """Response model for topic creation"""
    topic_id: str = Field(..., description="Unique topic identifier")
    topic: str = Field(..., description="Topic name")
    url_count: int = Field(..., description="Number of URLs processed")
    message: str = Field(..., description="Creation status message")

class URLCollectionResponse(APIResponse):
    """Response model for URL collection"""
    urls: List[str] = Field(..., description="Collected URLs")
    total_collected: int = Field(..., description="Total URLs collected")
    collection_metadata: Dict[str, Any] = Field(..., description="Collection metadata")

class EvidenceResponse(APIResponse):
    """Response model for evidence retrieval"""
    evidence: List[Dict[str, Any]] = Field(..., description="Evidence documents")
    layer: str = Field(..., description="Analysis layer")
    total_count: int = Field(..., description="Total evidence count")
    retrieval_metadata: Dict[str, Any] = Field(..., description="Retrieval metadata")

class EnhancedTopicResponse(APIResponse):
    """Response model for enhanced topic operations"""
    topic_id: str = Field(..., description="Enhanced topic identifier")
    topic: str = Field(..., description="Topic name")
    quality_threshold: float = Field(..., description="Applied quality threshold")
    url_count: int = Field(..., description="Number of URLs processed")
    processing_metadata: Dict[str, Any] = Field(..., description="Processing metadata")

class TopicKnowledgeResponse(APIResponse):
    """Response model for topic knowledge retrieval"""
    topic: str = Field(..., description="Topic name")
    knowledge: Dict[str, Any] = Field(..., description="Comprehensive topic knowledge")
    knowledge_metadata: Dict[str, Any] = Field(..., description="Knowledge metadata")

class TopicUpdateResponse(APIResponse):
    """Response model for topic updates"""
    topic: str = Field(..., description="Updated topic name")
    update_result: Dict[str, Any] = Field(..., description="Update operation results")

class TopicPerformanceResponse(APIResponse):
    """Response model for topic performance analysis"""
    topic: str = Field(..., description="Topic name")
    performance_analysis: Dict[str, Any] = Field(..., description="Performance analysis results")

class AnalysisSessionResponse(APIResponse):
    """Response model for analysis session operations"""
    session_id: str = Field(..., description="Unique session identifier")
    topic: str = Field(..., description="Analysis topic")
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="Operation status message")

class AnalysisExecutionResponse(APIResponse):
    """Response model for analysis execution"""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Execution status message")
    status: str = Field(..., description="Current analysis status")

class AnalysisStatusResponse(APIResponse):
    """Response model for analysis status"""
    session_id: str = Field(..., description="Session identifier")
    status: Dict[str, Any] = Field(..., description="Detailed status information")

class AnalysisResultsResponse(APIResponse):
    """Response model for analysis results"""
    session_id: str = Field(..., description="Session identifier")
    results: Dict[str, Any] = Field(..., description="Complete analysis results")

class ContentQualityResponse(APIResponse):
    """Response model for content quality analysis"""
    url: str = Field(..., description="Analyzed content URL")
    topic: str = Field(..., description="Analysis topic")
    quality_scores: Dict[str, Any] = Field(..., description="Quality assessment scores")

class ContentDeduplicationResponse(APIResponse):
    """Response model for content deduplication"""
    original_count: int = Field(..., description="Original document count")
    deduplicated_count: int = Field(..., description="Deduplicated document count")
    duplicates_removed: int = Field(..., description="Number of duplicates removed")
    deduplication_stats: Dict[str, Any] = Field(..., description="Deduplication statistics")
    documents: List[Dict[str, Any]] = Field(..., description="Deduplicated documents")

class ParallelProcessingResponse(APIResponse):
    """Response model for parallel processing optimization"""
    original_task_count: int = Field(..., description="Original task count")
    processed_task_count: int = Field(..., description="Successfully processed task count")
    optimization_results: List[Dict[str, Any]] = Field(..., description="Processing results")

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")

# Error Models

class APIError(BaseModel):
    """API error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

class ValidationError(BaseModel):
    """Validation error model"""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Any = Field(..., description="Invalid value")

# Enum Models

class AnalysisStatus(str, Enum):
    """Analysis status enumeration"""
    INITIALIZED = "initialized"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    ERROR = "error"

class QualityDimension(str, Enum):
    """Quality dimension enumeration"""
    TOPIC_RELEVANCE = "topic_relevance"
    READABILITY = "readability"
    DOMAIN_AUTHORITY = "domain_authority"
    CONTENT_FRESHNESS = "content_freshness"
    FACTUAL_ACCURACY = "factual_accuracy"
    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    ENGAGEMENT_POTENTIAL = "engagement_potential"

class StrategicLayer(str, Enum):
    """Strategic layer enumeration"""
    CONSUMER = "consumer"
    MARKET = "market"
    PRODUCT = "product"
    BRAND = "brand"
    EXPERIENCE = "experience"
    TECHNOLOGY = "technology"
    OPERATIONS = "operations"
    FINANCIAL = "financial"
    COMPETITIVE = "competitive"
    REGULATORY = "regulatory"

class DuplicateType(str, Enum):
    """Duplicate type enumeration"""
    EXACT = "exact"
    NEAR_EXACT = "near_exact"
    SEMANTIC = "semantic"
    PARTIAL = "partial"

class RecoveryStrategy(str, Enum):
    """Error recovery strategy enumeration"""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FAIL_FAST = "fail_fast"

# Metadata Models

class ProcessingMetadata(BaseModel):
    """Processing metadata model"""
    processing_time: float = Field(..., description="Processing time in seconds")
    memory_usage: float = Field(..., description="Memory usage in MB")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    throughput: float = Field(..., description="Processing throughput")
    error_count: int = Field(..., description="Number of errors encountered")

class QualityMetadata(BaseModel):
    """Quality assessment metadata model"""
    content_length: int = Field(..., description="Content length in characters")
    word_count: int = Field(..., description="Word count")
    sentence_count: int = Field(..., description="Sentence count")
    paragraph_count: int = Field(..., description="Paragraph count")
    analysis_timestamp: datetime = Field(..., description="Analysis timestamp")
    url_domain: str = Field(..., description="URL domain")
    topic_analyzed: str = Field(..., description="Analyzed topic")

class AnalysisMetadata(BaseModel):
    """Analysis metadata model"""
    session_duration: float = Field(..., description="Analysis session duration")
    layers_analyzed: List[str] = Field(..., description="Analyzed strategic layers")
    factors_calculated: List[str] = Field(..., description="Calculated strategic factors")
    evidence_sources: int = Field(..., description="Number of evidence sources")
    confidence_score: float = Field(..., description="Overall confidence score")

# Export all models
__all__ = [
    # Request Models
    'TopicCreateRequest', 'URLCollectionRequest', 'EnhancedTopicCreateRequest',
    'EnhancedTopicUpdateRequest', 'AnalysisSessionCreateRequest', 'ContentQualityAnalysisRequest',
    'ContentDeduplicationRequest', 'ParallelProcessingRequest',
    
    # Response Models
    'APIResponse', 'TopicListResponse', 'TopicCreateResponse', 'URLCollectionResponse',
    'EvidenceResponse', 'EnhancedTopicResponse', 'TopicKnowledgeResponse',
    'TopicUpdateResponse', 'TopicPerformanceResponse', 'AnalysisSessionResponse',
    'AnalysisExecutionResponse', 'AnalysisStatusResponse', 'AnalysisResultsResponse',
    'ContentQualityResponse', 'ContentDeduplicationResponse', 'ParallelProcessingResponse',
    'HealthResponse',
    
    # Error Models
    'APIError', 'ValidationError',
    
    # Enum Models
    'AnalysisStatus', 'QualityDimension', 'StrategicLayer', 'DuplicateType', 'RecoveryStrategy',
    
    # Metadata Models
    'ProcessingMetadata', 'QualityMetadata', 'AnalysisMetadata'
]
