"""
Topic Models for Validatus Platform
Defines data structures for topic management with Google Cloud Firestore integration
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AnalysisType(str, Enum):
    """Analysis type enumeration"""
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class TopicStatus(str, Enum):
    """Topic status enumeration"""
    DRAFT = "draft"
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TopicConfig(BaseModel):
    """Topic configuration model"""
    session_id: str = Field(..., description="Unique topic identifier")
    topic: str = Field(..., min_length=1, max_length=200, description="Topic name")
    description: str = Field(..., min_length=1, max_length=1000, description="Topic description")
    search_queries: List[str] = Field(default_factory=list, description="List of search queries")
    initial_urls: List[str] = Field(default_factory=list, description="List of initial URLs")
    analysis_type: AnalysisType = Field(default=AnalysisType.COMPREHENSIVE, description="Type of analysis")
    user_id: str = Field(..., description="User identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    status: TopicStatus = Field(default=TopicStatus.CREATED, description="Topic status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TopicCreateRequest(BaseModel):
    """Request model for creating a new topic"""
    topic: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    search_queries: List[str] = Field(default_factory=list)
    initial_urls: List[str] = Field(default_factory=list)
    analysis_type: AnalysisType = Field(default=AnalysisType.COMPREHENSIVE)
    user_id: str = Field(..., description="User identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TopicUpdateRequest(BaseModel):
    """Request model for updating an existing topic"""
    topic: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    search_queries: Optional[List[str]] = None
    initial_urls: Optional[List[str]] = None
    analysis_type: Optional[AnalysisType] = None
    status: Optional[TopicStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class TopicResponse(BaseModel):
    """Response model for topic data"""
    session_id: str
    topic: str
    description: str
    search_queries: List[str]
    initial_urls: List[str]
    analysis_type: AnalysisType
    user_id: str
    created_at: datetime
    updated_at: datetime
    status: TopicStatus
    metadata: Dict[str, Any]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TopicListResponse(BaseModel):
    """Response model for topic list"""
    topics: List[TopicResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


class TopicSearchRequest(BaseModel):
    """Request model for searching topics"""
    query: Optional[str] = None
    analysis_type: Optional[AnalysisType] = None
    status: Optional[TopicStatus] = None
    user_id: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order: asc or desc")
