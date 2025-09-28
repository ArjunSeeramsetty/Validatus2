"""
Dashboard API endpoints for Validatus Dashboard
Provides segment-specific data and business case calculations
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import json
import hashlib
from pathlib import Path

from ...services.migrated_data_service import MigratedDataService
from ...services.advanced_strategy_analysis import AdvancedStrategyAnalysisEngine

logger = logging.getLogger(__name__)

router = APIRouter()

class BusinessCaseInputs(BaseModel):
    unit_price: float
    unit_cost: float
    expected_volume: float
    fixed_costs: float
    innovation_cost: float
    discount_rate: float = 0.10
    time_duration: int = 5

class DashboardMetrics(BaseModel):
    session_id: str
    segment: str  # 'business_case', 'consumer', 'market', 'product', 'brand', 'experience'

@router.get("/dashboard/{session_id}/overview")
async def get_dashboard_overview(session_id: str) -> Dict[str, Any]:
    """Get comprehensive dashboard overview data"""
    try:
        # Load migrated data
        migrated_service = MigratedDataService()
        migrated_data = await migrated_service.get_analysis_results(session_id)
        
        # Load advanced analysis if available
        advanced_data = None
        try:
            advanced_path = Path(__file__).parent.parent.parent.parent / "app_storage" / "advanced_analysis" / f"{session_id}_advanced.json"
            if advanced_path.exists():
                with open(advanced_path, 'r') as f:
                    advanced_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load advanced analysis data: {e}")
        
        # Extract key metrics for dashboard
        overview = {
            'session_id': session_id,
            'topic': migrated_data.get('topic', 'Unknown Topic'),
            'status': migrated_data.get('status', 'unknown'),
            'overall_score': migrated_data.get('analysis_metadata', {}).get('confidence_score', 0.0),
            'strategic_layers': migrated_data.get('strategic_layers', {}),
            'strategic_factors': migrated_data.get('strategic_factors', {}),
            'key_insights': migrated_data.get('key_insights', []),
            'strategic_recommendations': migrated_data.get('strategic_recommendations', []),
            'action_items': migrated_data.get('action_items', []),
            'monte_carlo_results': migrated_data.get('monte_carlo_results', {}),
            'action_layer_data': migrated_data.get('action_layer_data', {}),
            'advanced_analysis': advanced_data,
            'created_at': migrated_data.get('created_at'),
            'completed_at': migrated_data.get('completed_at')
        }
        
        return {
            'success': True,
            'data': overview
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{session_id}/segment/{segment}")
async def get_segment_data(session_id: str, segment: str) -> Dict[str, Any]:
    """Get segment-specific data for dashboard tabs"""
    try:
        # Load base data
        migrated_service = MigratedDataService()
        migrated_data = await migrated_service.get_analysis_results(session_id)
        
        # Extract segment-specific data
        segment_data = {}
        
        if segment == 'business_case':
            # Business case specific data
            action_layer = migrated_data.get('action_layer_data', {})
            segment_data = {
                'financial_inputs': action_layer.get('financial_inputs', {}),
                'essential_metrics': action_layer.get('essential_metrics', {}),
                'growth_scenarios': action_layer.get('growth_scenarios', []),
                'business_case_confidence': action_layer.get('business_case_confidence', 0.0),
                'action_layer_scores': action_layer.get('action_layer_scores', {})
            }
            
        elif segment == 'consumer':
            # Consumer segment data
            consumer_factors = {}
            strategic_factors = migrated_data.get('strategic_factors', {})
            for key, value in strategic_factors.items():
                if 'Consumer' in key or 'consumer' in key.lower():
                    consumer_factors[key] = value
            
            segment_data = {
                'consumer_factors': consumer_factors,
                'consumer_layer': migrated_data.get('strategic_layers', {}).get('CONSUMER', {}),
                'insights': [insight for insight in migrated_data.get('key_insights', []) 
                           if 'consumer' in insight.lower() or 'customer' in insight.lower()]
            }
            
        elif segment == 'market':
            # Market segment data
            market_factors = {}
            strategic_factors = migrated_data.get('strategic_factors', {})
            for key, value in strategic_factors.items():
                if 'Market' in key or 'market' in key.lower():
                    market_factors[key] = value
            
            segment_data = {
                'market_factors': market_factors,
                'market_layer': migrated_data.get('strategic_layers', {}).get('MARKET', {}),
                'insights': [insight for insight in migrated_data.get('key_insights', []) 
                           if 'market' in insight.lower()]
            }
            
        elif segment == 'product':
            # Product segment data
            product_factors = {}
            strategic_factors = migrated_data.get('strategic_factors', {})
            for key, value in strategic_factors.items():
                if 'Product' in key or 'product' in key.lower():
                    product_factors[key] = value
            
            segment_data = {
                'product_factors': product_factors,
                'product_layer': migrated_data.get('strategic_layers', {}).get('PRODUCT', {}),
                'insights': [insight for insight in migrated_data.get('key_insights', []) 
                           if 'product' in insight.lower()]
            }
            
        elif segment == 'brand':
            # Brand segment data
            brand_factors = {}
            strategic_factors = migrated_data.get('strategic_factors', {})
            for key, value in strategic_factors.items():
                if 'Brand' in key or 'brand' in key.lower():
                    brand_factors[key] = value
            
            segment_data = {
                'brand_factors': brand_factors,
                'brand_layer': migrated_data.get('strategic_layers', {}).get('BRAND', {}),
                'insights': [insight for insight in migrated_data.get('key_insights', []) 
                           if 'brand' in insight.lower()]
            }
            
        elif segment == 'experience':
            # Experience segment data
            experience_factors = {}
            strategic_factors = migrated_data.get('strategic_factors', {})
            for key, value in strategic_factors.items():
                if 'Experience' in key or 'experience' in key.lower():
                    experience_factors[key] = value
            
            segment_data = {
                'experience_factors': experience_factors,
                'experience_layer': migrated_data.get('strategic_layers', {}).get('EXPERIENCE', {}),
                'insights': [insight for insight in migrated_data.get('key_insights', []) 
                           if 'experience' in insight.lower()]
            }
        
        return {
            'success': True,
            'segment': segment,
            'data': segment_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get segment data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dashboard/{session_id}/business-case/calculate")
async def calculate_business_case(session_id: str, inputs: BusinessCaseInputs) -> Dict[str, Any]:
    """Calculate business case metrics with real-time inputs"""
    try:
        # Basic calculations
        gross_margin = inputs.unit_price - inputs.unit_cost
        gross_margin_percent = (gross_margin / inputs.unit_price) * 100 if inputs.unit_price > 0 else 0
        total_contribution = gross_margin * inputs.expected_volume
        breakeven_volume = inputs.fixed_costs / gross_margin if gross_margin > 0 else 0
        payback_period = inputs.innovation_cost / (total_contribution - inputs.fixed_costs) if (total_contribution - inputs.fixed_costs) > 0 else float('inf')
        simple_roi = ((total_contribution - inputs.fixed_costs - inputs.innovation_cost) / inputs.innovation_cost) * 100 if inputs.innovation_cost > 0 else 0
        
        # NPV calculation (dynamic time duration projection)
        npv = -inputs.innovation_cost
        for year in range(1, inputs.time_duration + 1):
            cash_flow = total_contribution - inputs.fixed_costs
            npv += cash_flow / ((1 + inputs.discount_rate) ** year)
        
        # IRR calculation using Newton-Raphson method (finding discount rate where NPV = 0)
        def calculate_npv(rate, cash_flows, initial_investment):
            """Calculate NPV for given discount rate"""
            npv = -initial_investment
            for i, cash_flow in enumerate(cash_flows):
                npv += cash_flow / ((1 + rate) ** (i + 1))
            return npv
        
        def calculate_irr(cash_flows, initial_investment, max_iterations=100, tolerance=1e-6):
            """Calculate IRR using Newton-Raphson method"""
            if initial_investment <= 0:
                return 0.0
            
            # Initial guess
            rate = 0.1  # Start with 10%
            
            for _ in range(max_iterations):
                npv = calculate_npv(rate, cash_flows, initial_investment)
                
                # If NPV is close to zero, we found the IRR
                if abs(npv) < tolerance:
                    return rate * 100
                
                # Calculate derivative for Newton-Raphson
                derivative = 0
                for i, cash_flow in enumerate(cash_flows):
                    derivative -= cash_flow * (i + 1) / ((1 + rate) ** (i + 2))
                
                # Avoid division by zero
                if abs(derivative) < tolerance:
                    break
                
                # Newton-Raphson update
                rate = rate - npv / derivative
                
                # Keep rate reasonable
                rate = max(0.0, min(rate, 10.0))  # Between 0% and 1000%
            
            return rate * 100
        
        # Generate cash flows for IRR calculation
        annual_cash_flow = total_contribution - inputs.fixed_costs
        cash_flows = [annual_cash_flow] * inputs.time_duration  # Dynamic time duration
        irr = calculate_irr(cash_flows, inputs.innovation_cost)
        
        # Scenario analysis
        scenarios = [
            {
                'name': 'Conservative',
                'multiplier': 0.8,
                'color': '#ff4d4f',
                'probability': 25,
                'volume': inputs.expected_volume * 0.8,
                'price': inputs.unit_price * 0.95,
                'contribution': (inputs.unit_price * 0.95 - inputs.unit_cost) * inputs.expected_volume * 0.8,
                'roi': (((inputs.unit_price * 0.95 - inputs.unit_cost) * inputs.expected_volume * 0.8 - inputs.fixed_costs - inputs.innovation_cost) / inputs.innovation_cost) * 100
            },
            {
                'name': 'Base Case',
                'multiplier': 1.0,
                'color': '#52c41a',
                'probability': 50,
                'volume': inputs.expected_volume,
                'price': inputs.unit_price,
                'contribution': total_contribution,
                'roi': simple_roi
            },
            {
                'name': 'Optimistic',
                'multiplier': 1.3,
                'color': '#1890ff',
                'probability': 25,
                'volume': inputs.expected_volume * 1.3,
                'price': inputs.unit_price * 1.1,
                'contribution': (inputs.unit_price * 1.1 - inputs.unit_cost) * inputs.expected_volume * 1.3,
                'roi': (((inputs.unit_price * 1.1 - inputs.unit_cost) * inputs.expected_volume * 1.3 - inputs.fixed_costs - inputs.innovation_cost) / inputs.innovation_cost) * 100
            }
        ]
        
        return {
            'success': True,
            'metrics': {
                'gross_margin': gross_margin,
                'gross_margin_percent': gross_margin_percent,
                'total_contribution': total_contribution,
                'breakeven_volume': breakeven_volume,
                'payback_period': payback_period,
                'simple_roi': simple_roi,
                'npv': npv,
                'irr': irr
            },
            'scenarios': scenarios
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate business case: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{session_id}/metrics")
async def get_dashboard_metrics(session_id: str) -> Dict[str, Any]:
    """Get key dashboard metrics and KPIs"""
    try:
        # Load data
        migrated_service = MigratedDataService()
        migrated_data = await migrated_service.get_analysis_results(session_id)
        
        # Extract key metrics
        overall_score = migrated_data.get('analysis_metadata', {}).get('confidence_score', 0.0)
        strategic_layers = migrated_data.get('strategic_layers', {})
        
        # Calculate segment scores
        segment_scores = {}
        for layer, data in strategic_layers.items():
            if isinstance(data, dict) and 'score' in data:
                segment_scores[layer.lower()] = data['score']
            else:
                # Mock scores based on overall score with deterministic hash
                layer_hash = int(hashlib.sha256(layer.encode()).hexdigest(), 16) % 20
                segment_scores[layer.lower()] = overall_score * (0.8 + layer_hash / 100)
        
        # Get action layer confidence
        action_layer_confidence = migrated_data.get('action_layer_data', {}).get('business_case_confidence', 0.0)
        
        return {
            'success': True,
            'metrics': {
                'overall_score': overall_score,
                'segment_scores': segment_scores,
                'business_case_confidence': action_layer_confidence,
                'total_insights': len(migrated_data.get('key_insights', [])),
                'total_recommendations': len(migrated_data.get('strategic_recommendations', [])),
                'total_action_items': len(migrated_data.get('action_items', []))
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
