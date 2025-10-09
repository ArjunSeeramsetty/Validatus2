"""
Validatus v2.0 Segment Analysis Engine
Analyzes 5 intelligence segments from 28 factor calculations
"""
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel

from ..core.aliases_config import aliases_config
from ..services.v2_factor_calculation_engine import FactorCalculation

logger = logging.getLogger(__name__)

class SegmentAnalysis(BaseModel):
    """Segment analysis result model"""
    session_id: str
    segment_id: str
    segment_name: str
    attractiveness_score: float
    competitive_intensity: float
    market_size_score: float
    growth_potential: float
    overall_segment_score: float
    key_insights: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    recommendations: List[str]
    factor_contributions: Dict[str, float]
    metadata: Dict[str, Any] = {}
    created_at: datetime

class V2SegmentAnalysisEngine:
    """Analyzes 5 intelligence segments from factor calculations"""
    
    def __init__(self):
        self.aliases = aliases_config
        
        # Segment-specific scoring formulas
        self.segment_formulas = {
            'S1': {  # Product Intelligence
                'attractiveness': lambda factors: factors.get('F7', 0.5) * 0.4 + factors.get('F8', 0.5) * 0.3 + factors.get('F10', 0.5) * 0.3,
                'competitiveness': lambda factors: factors.get('F2', 0.5) * 0.5 + factors.get('F9', 0.5) * 0.5,
                'market_size': lambda factors: factors.get('F1', 0.5) * 0.6 + factors.get('F4', 0.5) * 0.4,
                'growth': lambda factors: factors.get('F8', 0.5) * 0.5 + factors.get('F5', 0.5) * 0.5
            },
            'S2': {  # Consumer Intelligence
                'attractiveness': lambda factors: factors.get('F11', 0.5) * 0.4 + factors.get('F13', 0.5) * 0.3 + factors.get('F15', 0.5) * 0.3,
                'competitiveness': lambda factors: factors.get('F12', 0.5) * 0.6 + factors.get('F14', 0.5) * 0.4,
                'market_size': lambda factors: factors.get('F11', 0.5) * 0.7 + factors.get('F13', 0.5) * 0.3,
                'growth': lambda factors: factors.get('F13', 0.5) * 0.5 + factors.get('F14', 0.5) * 0.5
            },
            'S3': {  # Market Intelligence
                'attractiveness': lambda factors: factors.get('F18', 0.5) * 0.5 + factors.get('F16', 0.5) * 0.5,
                'competitiveness': lambda factors: factors.get('F17', 0.5) * 0.7 + factors.get('F19', 0.5) * 0.3,
                'market_size': lambda factors: factors.get('F18', 0.5) * 0.8 + factors.get('F20', 0.5) * 0.2,
                'growth': lambda factors: factors.get('F18', 0.5) * 0.4 + factors.get('F16', 0.5) * 0.6
            },
            'S4': {  # Brand Intelligence
                'attractiveness': lambda factors: factors.get('F22', 0.5) * 0.4 + factors.get('F23', 0.5) * 0.3 + factors.get('F25', 0.5) * 0.3,
                'competitiveness': lambda factors: factors.get('F21', 0.5) * 0.6 + factors.get('F24', 0.5) * 0.4,
                'market_size': lambda factors: factors.get('F23', 0.5) * 0.6 + factors.get('F22', 0.5) * 0.4,
                'growth': lambda factors: factors.get('F25', 0.5) * 0.5 + factors.get('F24', 0.5) * 0.5
            },
            'S5': {  # Experience Intelligence
                'attractiveness': lambda factors: factors.get('F26', 0.5) * 0.4 + factors.get('F27', 0.5) * 0.4 + factors.get('F28', 0.5) * 0.2,
                'competitiveness': lambda factors: factors.get('F27', 0.5) * 0.6 + factors.get('F26', 0.5) * 0.4,
                'market_size': lambda factors: factors.get('F26', 0.5) * 0.5 + factors.get('F28', 0.5) * 0.5,
                'growth': lambda factors: factors.get('F26', 0.5) * 0.7 + factors.get('F27', 0.5) * 0.3
            }
        }
    
    async def analyze_all_segments(self, session_id: str,
                                  factor_calculations: List[FactorCalculation]) -> List[SegmentAnalysis]:
        """
        Analyze all 5 segments from factor calculations
        
        Args:
            session_id: Session identifier
            factor_calculations: List of 28 factor calculations
            
        Returns:
            List of 5 SegmentAnalysis objects
        """
        logger.info(f"🎯 Analyzing 5 segments from {len(factor_calculations)} factor calculations")
        
        # Group factors by segment
        factors_by_segment = self._group_factors_by_segment(factor_calculations)
        
        # Analyze each segment
        segment_analyses = []
        all_segment_ids = self.aliases.get_all_segment_ids()
        
        for segment_id in all_segment_ids:
            segment_factors = factors_by_segment.get(segment_id, [])
            
            if not segment_factors:
                logger.warning(f"No factors found for segment {segment_id}")
                # Create default segment
                segment_analyses.append(self._create_default_segment(session_id, segment_id))
                continue
            
            try:
                analysis = await self._analyze_single_segment(
                    session_id, segment_id, segment_factors
                )
                segment_analyses.append(analysis)
            except Exception as e:
                logger.error(f"Segment analysis failed for {segment_id}: {e}")
                segment_analyses.append(self._create_default_segment(session_id, segment_id))
        
        logger.info(f"✅ Segment analysis completed: {len(segment_analyses)} segments")
        return segment_analyses
    
    async def _analyze_single_segment(self, session_id: str, segment_id: str,
                                     factor_calculations: List[FactorCalculation]) -> SegmentAnalysis:
        """Analyze single segment from its factor calculations"""
        
        segment_name = self.aliases.get_segment_name(segment_id)
        
        # Convert factor calculations to dict for formula evaluation
        factor_values = {
            fc.factor_id: fc.calculated_value
            for fc in factor_calculations
        }
        
        # Get formulas for this segment
        formulas = self.segment_formulas.get(segment_id, self.segment_formulas['S1'])
        
        # Calculate segment metrics
        attractiveness = formulas['attractiveness'](factor_values)
        competitiveness = formulas['competitiveness'](factor_values)
        market_size = formulas['market_size'](factor_values)
        growth = formulas['growth'](factor_values)
        
        # Calculate overall segment score
        overall_score = (
            attractiveness * 0.35 +
            (1.0 - competitiveness) * 0.25 +  # Lower intensity is better
            market_size * 0.20 +
            growth * 0.20
        )
        
        # Generate insights based on scores
        insights = self._generate_segment_insights(
            segment_name, attractiveness, competitiveness, market_size, growth
        )
        
        # Identify risks and opportunities
        risks = self._identify_segment_risks(
            segment_name, attractiveness, competitiveness, market_size, growth
        )
        
        opportunities = self._identify_segment_opportunities(
            segment_name, attractiveness, competitiveness, market_size, growth
        )
        
        # Generate recommendations
        recommendations = self._generate_segment_recommendations(
            segment_name, attractiveness, competitiveness, market_size, growth
        )
        
        # Track factor contributions
        factor_contributions = {
            fc.factor_id: fc.calculated_value
            for fc in factor_calculations
        }
        
        return SegmentAnalysis(
            session_id=session_id,
            segment_id=segment_id,
            segment_name=segment_name,
            attractiveness_score=round(attractiveness, 4),
            competitive_intensity=round(competitiveness, 4),
            market_size_score=round(market_size, 4),
            growth_potential=round(growth, 4),
            overall_segment_score=round(overall_score, 4),
            key_insights=insights,
            risk_factors=risks,
            opportunities=opportunities,
            recommendations=recommendations,
            factor_contributions=factor_contributions,
            metadata={
                'factor_count': len(factor_calculations),
                'expected_factors': len(self.aliases.get_factors_for_segment(segment_id))
            },
            created_at=datetime.now(timezone.utc)
        )
    
    def _group_factors_by_segment(self, factor_calculations: List[FactorCalculation]) -> Dict[str, List[FactorCalculation]]:
        """Group factor calculations by their parent segment"""
        grouped = {}
        
        for factor_calc in factor_calculations:
            segment_id = self.aliases.get_segment_for_factor(factor_calc.factor_id)
            if not segment_id:
                logger.warning(f"No segment found for factor {factor_calc.factor_id}")
                continue
            
            if segment_id not in grouped:
                grouped[segment_id] = []
            grouped[segment_id].append(factor_calc)
        
        return grouped
    
    def _generate_segment_insights(self, segment_name: str, attractiveness: float,
                                  competitiveness: float, market_size: float, 
                                  growth: float) -> List[str]:
        """Generate strategic insights for segment"""
        insights = []
        
        if attractiveness > 0.7:
            insights.append(f"{segment_name}: High market attractiveness indicates strong strategic opportunity")
        elif attractiveness < 0.4:
            insights.append(f"{segment_name}: Lower attractiveness suggests need for differentiation or niche focus")
        
        if competitiveness > 0.7:
            insights.append(f"{segment_name}: Intense competition requires strong competitive moat")
        elif competitiveness < 0.4:
            insights.append(f"{segment_name}: Lower competitive intensity presents opportunity for market leadership")
        
        if growth > 0.7:
            insights.append(f"{segment_name}: High growth potential suggests early market entry opportunity")
        
        if market_size > 0.7 and growth > 0.6:
            insights.append(f"{segment_name}: Large growing market ideal for scaling strategy")
        
        return insights
    
    def _identify_segment_risks(self, segment_name: str, attractiveness: float,
                               competitiveness: float, market_size: float, 
                               growth: float) -> List[str]:
        """Identify risk factors for segment"""
        risks = []
        
        if competitiveness > 0.75:
            risks.append(f"High competitive intensity may limit market share gains")
        
        if market_size < 0.3:
            risks.append(f"Limited market size may constrain growth potential")
        
        if growth < 0.3:
            risks.append(f"Low growth rate suggests mature or declining market")
        
        if attractiveness < 0.4 and competitiveness > 0.6:
            risks.append(f"Challenging combination of low attractiveness and high competition")
        
        return risks
    
    def _identify_segment_opportunities(self, segment_name: str, attractiveness: float,
                                      competitiveness: float, market_size: float,
                                      growth: float) -> List[str]:
        """Identify opportunities for segment"""
        opportunities = []
        
        if attractiveness > 0.65 and competitiveness < 0.5:
            opportunities.append(f"Attractive market with manageable competition")
        
        if growth > 0.7:
            opportunities.append(f"Strong growth trajectory enables market leadership positioning")
        
        if market_size > 0.6 and growth > 0.5:
            opportunities.append(f"Large growing market supports aggressive expansion strategy")
        
        if competitiveness < 0.4:
            opportunities.append(f"Low competitive intensity allows for differentiation and premium positioning")
        
        return opportunities
    
    def _generate_segment_recommendations(self, segment_name: str, attractiveness: float,
                                        competitiveness: float, market_size: float,
                                        growth: float) -> List[str]:
        """Generate strategic recommendations for segment"""
        recommendations = []
        
        # Scoring-based recommendations
        if attractiveness > 0.7 and competitiveness < 0.5:
            recommendations.append("RECOMMEND: Aggressive market entry with premium positioning")
        elif attractiveness > 0.6 and growth > 0.6:
            recommendations.append("RECOMMEND: Scale quickly to capture growth opportunity")
        elif competitiveness > 0.75:
            recommendations.append("RECOMMEND: Focus on differentiation and niche dominance")
        elif market_size < 0.3:
            recommendations.append("RECOMMEND: Niche strategy with high margins")
        else:
            recommendations.append("RECOMMEND: Balanced approach with measured investment")
        
        # Growth-based recommendations
        if growth > 0.7:
            recommendations.append("TIMING: Enter early to establish market leadership")
        elif growth < 0.3:
            recommendations.append("TIMING: Wait for market catalysts or focus on mature market strategies")
        
        # Size-based recommendations
        if market_size > 0.7:
            recommendations.append("SCALE: Large market supports volume-based strategy")
        elif market_size < 0.4:
            recommendations.append("SCALE: Focus on high-value customers in limited market")
        
        return recommendations
    
    def _create_default_segment(self, session_id: str, segment_id: str) -> SegmentAnalysis:
        """Create default segment analysis when factors unavailable"""
        
        segment_name = self.aliases.get_segment_name(segment_id) or f"Segment {segment_id}"
        
        return SegmentAnalysis(
            session_id=session_id,
            segment_id=segment_id,
            segment_name=segment_name,
            attractiveness_score=0.5,
            competitive_intensity=0.5,
            market_size_score=0.5,
            growth_potential=0.5,
            overall_segment_score=0.5,
            key_insights=[f"{segment_name}: Default analysis applied"],
            risk_factors=["Insufficient data for comprehensive analysis"],
            opportunities=["Collect more data for detailed insights"],
            recommendations=["Enhance data collection before strategic decisions"],
            factor_contributions={},
            metadata={'default': True, 'warning': 'No factor calculations available'},
            created_at=datetime.now(timezone.utc)
        )

# Global engine instance
try:
    v2_segment_engine = V2SegmentAnalysisEngine()
    logger.info("✅ V2 Segment Analysis Engine initialized")
except Exception as e:
    logger.error(f"Failed to initialize V2 Segment Analysis Engine: {e}")
    v2_segment_engine = None

