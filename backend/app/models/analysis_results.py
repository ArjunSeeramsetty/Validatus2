"""
Analysis Results Models for Comprehensive Market Analysis
Supports: Market, Consumer, Product, Brand, and Experience dimensions
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class CompetitorInfo(BaseModel):
    """Competitor analysis information"""
    name: str
    description: Optional[str] = None
    market_share: Optional[float] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class MarketAnalysisData(BaseModel):
    """Market dimension analysis"""
    competitor_analysis: Dict[str, Any] = Field(default_factory=dict)
    opportunities: List[str] = Field(default_factory=list)
    opportunities_rationale: Optional[str] = None
    market_share: Dict[str, float] = Field(default_factory=dict)
    pricing_switching: Dict[str, Any] = Field(default_factory=dict)
    regulation_tariffs: Dict[str, Any] = Field(default_factory=dict)
    growth_demand: Dict[str, Any] = Field(default_factory=dict)
    market_fit: Dict[str, float] = Field(default_factory=lambda: {"overall_score": 0.0})


class PersonaInfo(BaseModel):
    """Consumer persona information"""
    name: str
    age: Optional[int] = None
    description: str
    motivations: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)


class ConsumerAnalysisData(BaseModel):
    """Consumer dimension analysis"""
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    top_motivators: List[str] = Field(default_factory=list)
    relevant_personas: List[Dict[str, Any]] = Field(default_factory=list)
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    consumer_fit: Dict[str, float] = Field(default_factory=lambda: {"overall_score": 0.0})
    additional_recommendations: List[str] = Field(default_factory=list)


class ProductFeature(BaseModel):
    """Product feature information"""
    name: str
    description: str
    importance: Optional[float] = None
    category: Optional[str] = None


class ProductAnalysisData(BaseModel):
    """Product dimension analysis"""
    product_features: List[Dict[str, Any]] = Field(default_factory=list)
    competitive_positioning: Dict[str, Any] = Field(default_factory=dict)
    innovation_opportunities: List[str] = Field(default_factory=list)
    technical_specifications: Dict[str, Any] = Field(default_factory=dict)
    product_roadmap: List[Dict[str, Any]] = Field(default_factory=list)
    product_fit: Dict[str, float] = Field(default_factory=lambda: {"overall_score": 0.0})


class BrandAnalysisData(BaseModel):
    """Brand dimension analysis"""
    brand_positioning: Dict[str, float] = Field(default_factory=dict)
    brand_perception: Dict[str, float] = Field(default_factory=dict)
    competitor_brands: List[Dict[str, Any]] = Field(default_factory=list)
    brand_opportunities: List[str] = Field(default_factory=list)
    messaging_strategy: Dict[str, Any] = Field(default_factory=dict)
    brand_fit: Dict[str, float] = Field(default_factory=lambda: {"overall_score": 0.0})


class JourneyStage(BaseModel):
    """User journey stage information"""
    stage: str
    phase: str
    description: str
    pain_points: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)


class ExperienceAnalysisData(BaseModel):
    """Experience dimension analysis"""
    user_journey: List[Dict[str, Any]] = Field(default_factory=list)
    touchpoints: List[Dict[str, Any]] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    experience_metrics: Dict[str, float] = Field(default_factory=dict)
    improvement_recommendations: List[str] = Field(default_factory=list)
    experience_fit: Dict[str, float] = Field(default_factory=lambda: {"overall_score": 0.0})


class CompleteAnalysisResult(BaseModel):
    """Complete analysis result across all dimensions"""
    session_id: str
    topic_name: str
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    business_case: Optional[Dict[str, Any]] = Field(default_factory=dict)
    market: MarketAnalysisData = Field(default_factory=MarketAnalysisData)
    consumer: ConsumerAnalysisData = Field(default_factory=ConsumerAnalysisData)
    product: ProductAnalysisData = Field(default_factory=ProductAnalysisData)
    brand: BrandAnalysisData = Field(default_factory=BrandAnalysisData)
    experience: ExperienceAnalysisData = Field(default_factory=ExperienceAnalysisData)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "topic-abc123",
                "topic_name": "Pergola Market Analysis",
                "analysis_timestamp": "2025-10-12T14:30:00",
                "market": {
                    "opportunities": ["Growing outdoor living trend", "Smart home integration"],
                    "market_fit": {"overall_score": 0.75}
                },
                "consumer": {
                    "recommendations": [{"type": "Target affluent homeowners", "description": "Focus on premium features"}],
                    "consumer_fit": {"overall_score": 0.81}
                }
            }
        }

