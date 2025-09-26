"""
Advanced Strategy Analysis API Endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()

class AdvancedAnalysisRequest(BaseModel):
    client_inputs: Dict[str, float]
    analysis_options: Optional[Dict[str, Any]] = {}

class ScenarioAnalysisRequest(BaseModel):
    scenario_adjustments: Dict[str, float]

class PatternAnalysisRequest(BaseModel):
    context: Dict[str, Any]
    selected_patterns: Optional[List[str]] = None

# Service instances
from ...services.advanced_strategy_analysis import AdvancedStrategyAnalysisEngine
from ...services.pattern_library import StrategyPatternLibrary

analysis_engine = AdvancedStrategyAnalysisEngine()
pattern_library = StrategyPatternLibrary()

@router.post("/analysis/{session_id}/advanced")
async def run_advanced_analysis(
    session_id: str,
    request: AdvancedAnalysisRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Execute advanced strategy analysis with Monte Carlo simulation"""
    try:
        # Load session data
        session_data = await load_session_data(session_id)
        
        # Run analysis
        results = analysis_engine.analyze_strategy(
            session_id=session_id,
            topic_data=session_data,
            client_inputs=request.client_inputs
        )
        
        # Save results
        logger.info(f"About to save results with keys: {list(results.keys())}")
        logger.info(f"Results type: {type(results)}")
        await save_advanced_results(session_id, results)
        
        return {
            'success': True,
            'session_id': session_id,
            'results': results,
            'analysis_type': 'advanced_monte_carlo'
        }
        
    except Exception as e:
        logger.error(f"Advanced analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Advanced analysis failed: {str(e)}")

@router.get("/analysis/{session_id}/scenarios")
async def get_scenario_analysis(session_id: str) -> Dict[str, Any]:
    """Get scenario analysis results"""
    try:
        results = await load_advanced_results(session_id)
        
        if not results:
            # Return mock data for demo purposes
            logger.info(f"No saved results found for {session_id}, returning mock data")
            return {
                'success': True,
                'scenarios': [
                    {
                        'name': 'Base Case',
                        'probability': 0.5,
                        'kpis': {
                            'roi': 0.18,
                            'adoption_rate': 0.12,
                            'payback_period': 2.5,
                            'npv': 50000
                        },
                        'narrative': 'Steady market conditions with 18% ROI and 12% adoption rate. Moderate growth trajectory with manageable risks.',
                        'key_drivers': ['Market Growth', 'Competitive Position'],
                        'risk_level': 'Medium'
                    },
                    {
                        'name': 'Aggressive Growth',
                        'probability': 0.3,
                        'kpis': {
                            'roi': 0.28,
                            'adoption_rate': 0.18,
                            'payback_period': 1.8,
                            'npv': 80000
                        },
                        'narrative': 'Favorable market conditions driving strong performance with 28% ROI. High adoption rate of 18% indicates market readiness.',
                        'key_drivers': ['Technology Adoption', 'Market Growth'],
                        'risk_level': 'Low'
                    },
                    {
                        'name': 'Crisis',
                        'probability': 0.2,
                        'kpis': {
                            'roi': 0.08,
                            'adoption_rate': 0.05,
                            'payback_period': 4.0,
                            'npv': 20000
                        },
                        'narrative': 'Challenging market conditions with lower ROI of 8% and adoption rate of 5%. Requires careful risk management and contingency planning.',
                        'key_drivers': ['Regulatory Environment', 'Economic Conditions'],
                        'risk_level': 'High'
                    }
                ],
                'business_case_score': {
                    'score': 0.72,
                    'confidence_band': [0.65, 0.79],
                    'components': {
                        'roi': 0.8,
                        'adoption': 0.6,
                        'risk': 0.7
                    }
                },
                'driver_sensitivities': {
                    'F1': 0.3,
                    'F2': 0.2,
                    'F3': 0.25,
                    'F4': 0.15,
                    'F5': 0.1
                },
                'simulation_metadata': {
                    'runs': 10000,
                    'confidence_level': 0.95,
                    'analysis_type': 'mock_data'
                },
                'financial_projections': {
                    'year_1': {'revenue': 150000, 'profit': 30000, 'roi': 0.2},
                    'year_2': {'revenue': 180000, 'profit': 45000, 'roi': 0.25},
                    'year_3': {'revenue': 220000, 'profit': 60000, 'roi': 0.3}
                },
                'assumptions': {
                    'drivers': [
                        {'id': 'F1', 'name': 'Market Growth', 'confidence': 0.8},
                        {'id': 'F2', 'name': 'Competitive Position', 'confidence': 0.7},
                        {'id': 'F3', 'name': 'Technology Adoption', 'confidence': 0.75}
                    ],
                    'constraints': {
                        'min_roi': 0.1,
                        'max_payback_period': 3.0,
                        'min_adoption_rate': 0.05
                    },
                    'business_inputs': {
                        'unit_price': 150,
                        'unit_cost': 75,
                        'expected_volume': 1000
                    }
                }
            }
        
        return {
            'success': True,
            'scenarios': results.get('scenarios', []),
            'business_case_score': results.get('business_case_score', {}),
            'driver_sensitivities': results.get('driver_sensitivities', {}),
            'simulation_metadata': results.get('simulation_metadata', {}),
            'financial_projections': results.get('financial_projections', {}),
            'assumptions': results.get('assumptions', {})
        }
        
    except Exception as e:
        logger.error(f"Failed to get scenario analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis/{session_id}/sensitivity")
async def run_sensitivity_analysis(
    session_id: str,
    request: ScenarioAnalysisRequest
) -> Dict[str, Any]:
    """Run what-if sensitivity analysis"""
    try:
        # Load base results
        base_results = await load_advanced_results(session_id)
        
        if not base_results:
            raise HTTPException(status_code=404, detail=f"No base analysis results found for session {session_id}")
        
        # Apply adjustments and re-run
        adjusted_results = analysis_engine.run_sensitivity_analysis(
            session_id, request.scenario_adjustments
        )
        
        # Calculate delta analysis
        delta_analysis = compare_results(base_results, adjusted_results)
        
        return {
            'success': True,
            'base_results': base_results,
            'adjusted_results': adjusted_results,
            'delta_analysis': delta_analysis,
            'adjustments_applied': request.scenario_adjustments
        }
        
    except Exception as e:
        logger.error(f"Sensitivity analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis/{session_id}/patterns")
async def analyze_patterns(
    session_id: str,
    request: PatternAnalysisRequest
) -> Dict[str, Any]:
    """Analyze applicable strategic patterns"""
    try:
        # Load session data to get factors
        session_data = await load_session_data(session_id)
        strategic_layers = session_data.get('strategic_layers', {})
        
        # Extract factor IDs from strategic layers
        factors = []
        for layer_name, layer_data in strategic_layers.items():
            # Map layer to factors (simplified mapping)
            if 'market' in layer_name.lower():
                factors.extend(['F1', 'F3'])
            elif 'competitive' in layer_name.lower():
                factors.extend(['F2', 'F4'])
            elif 'financial' in layer_name.lower():
                factors.extend(['F5', 'F2'])
            elif 'growth' in layer_name.lower():
                factors.extend(['F1', 'F3'])
            elif 'risk' in layer_name.lower():
                factors.extend(['F4', 'F5'])
        
        # Remove duplicates
        factors = list(set(factors))
        
        # Get applicable patterns
        applicable_patterns = pattern_library.get_applicable_patterns(factors, request.context)
        
        # Filter by selected patterns if provided
        if request.selected_patterns:
            applicable_patterns = [
                p for p in applicable_patterns 
                if p['pattern_id'] in request.selected_patterns
            ]
        
        # Get pattern summaries
        pattern_summaries = []
        for pattern in applicable_patterns:
            summary = pattern_library.get_pattern_summary(pattern['pattern_id'])
            summary['activation_weight'] = pattern['activation_weight']
            pattern_summaries.append(summary)
        
        return {
            'success': True,
            'applicable_patterns': pattern_summaries,
            'context_validation': pattern_library.validate_pattern_context(request.context),
            'suggestions': pattern_library.suggest_context_improvements(request.context),
            'factors_analyzed': factors
        }
        
    except Exception as e:
        logger.error(f"Pattern analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/patterns")
async def get_all_patterns() -> Dict[str, Any]:
    """Get all available strategic patterns"""
    try:
        patterns = pattern_library.get_all_patterns()
        
        return {
            'success': True,
            'patterns': patterns,
            'total_patterns': len(patterns)
        }
        
    except Exception as e:
        logger.error(f"Failed to get patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{session_id}/export")
async def export_analysis_results(session_id: str, format: str = "json") -> Dict[str, Any]:
    """Export analysis results in various formats"""
    try:
        results = await load_advanced_results(session_id)
        
        if not results:
            raise HTTPException(status_code=404, detail=f"No analysis results found for session {session_id}")
        
        if format == "json":
            return {
                'success': True,
                'format': 'json',
                'data': results,
                'export_timestamp': '2024-01-01T00:00:00Z'  # TODO: Add actual timestamp
            }
        elif format == "summary":
            # Generate executive summary
            summary = generate_executive_summary(results)
            return {
                'success': True,
                'format': 'summary',
                'data': summary,
                'export_timestamp': '2024-01-01T00:00:00Z'
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
        
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def load_session_data(session_id: str) -> Dict[str, Any]:
    """Load session data from storage"""
    try:
        # Try to load from migrated data first
        migrated_path = Path(f"backend/migrated_data/analysis_results/{session_id}.json")
        if migrated_path.exists():
            with open(migrated_path, 'r') as f:
                return json.load(f)
        
        # Try to load from analysis sessions
        sessions_path = Path(f"backend/app_storage/analysis_sessions/{session_id}")
        if sessions_path.exists():
            # Load stage 1 results
            stage1_path = sessions_path / "stage1_results.json"
            if stage1_path.exists():
                with open(stage1_path, 'r') as f:
                    return json.load(f)
        
        # Return default structure
        return {
            'strategic_layers': {
                'market_attractiveness': {'score': 0.7, 'confidence': 0.8},
                'competitive_position': {'score': 0.6, 'confidence': 0.7},
                'financial_performance': {'score': 0.8, 'confidence': 0.9},
                'growth_potential': {'score': 0.75, 'confidence': 0.8},
                'risk_assessment': {'score': 0.65, 'confidence': 0.7}
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to load session data: {str(e)}")
        return {}

async def save_advanced_results(session_id: str, results: Dict[str, Any]) -> None:
    """Save advanced analysis results"""
    try:
        # Use absolute path from the project root
        results_dir = Path(__file__).parent.parent.parent.parent / "app_storage" / "advanced_analysis"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        results_path = results_dir / f"{session_id}_advanced.json"
        
        # Write to a temporary file first, then rename to avoid corruption
        temp_path = results_path.with_suffix('.tmp')
        
        # Debug: Check if results are serializable
        try:
            json_str = json.dumps(results, indent=2)
            logger.info(f"JSON serialization successful, length: {len(json_str)}")
        except Exception as e:
            logger.error(f"JSON serialization failed: {str(e)}")
            raise
        
        with open(temp_path, 'w') as f:
            f.write(json_str)
        
        # Rename temp file to final file
        temp_path.rename(results_path)
        
        logger.info(f"Advanced analysis results saved for session {session_id} at {results_path}")
        logger.info(f"Results size: {len(json.dumps(results))} characters")
        
    except Exception as e:
        logger.error(f"Failed to save advanced results: {str(e)}")
        # Clean up temp file if it exists
        try:
            temp_path = results_dir / f"{session_id}_advanced.tmp"
            if temp_path.exists():
                temp_path.unlink()
        except:
            pass

async def load_advanced_results(session_id: str) -> Optional[Dict[str, Any]]:
    """Load advanced analysis results"""
    try:
        # Use absolute path from the project root
        results_path = Path(__file__).parent.parent.parent.parent / "app_storage" / "advanced_analysis" / f"{session_id}_advanced.json"
        
        logger.info(f"Looking for results at: {results_path}")
        logger.info(f"File exists: {results_path.exists()}")
        
        if results_path.exists():
            with open(results_path, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded results with keys: {list(data.keys())}")
                return data
        
        logger.warning(f"No results file found at {results_path}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to load advanced results: {str(e)}")
        return None

def compare_results(base_results: Dict[str, Any], adjusted_results: Dict[str, Any]) -> Dict[str, Any]:
    """Compare base and adjusted results"""
    try:
        delta_analysis = {}
        
        # Compare business case scores
        if 'business_case_score' in base_results and 'business_case_score' in adjusted_results:
            base_score = base_results['business_case_score'].get('score', 0)
            adj_score = adjusted_results['business_case_score'].get('score', 0)
            delta_analysis['business_case_score_delta'] = adj_score - base_score
        
        # Compare scenarios
        if 'scenarios' in base_results and 'scenarios' in adjusted_results:
            base_scenarios = {s['name']: s for s in base_results['scenarios']}
            adj_scenarios = {s['name']: s for s in adjusted_results['scenarios']}
            
            scenario_deltas = {}
            for scenario_name in base_scenarios:
                if scenario_name in adj_scenarios:
                    base_scenario = base_scenarios[scenario_name]
                    adj_scenario = adj_scenarios[scenario_name]
                    
                    kpi_deltas = {}
                    for kpi in base_scenario['kpis']:
                        if kpi in adj_scenario['kpis']:
                            kpi_deltas[kpi] = adj_scenario['kpis'][kpi] - base_scenario['kpis'][kpi]
                    
                    scenario_deltas[scenario_name] = kpi_deltas
            
            delta_analysis['scenario_deltas'] = scenario_deltas
        
        return delta_analysis
        
    except Exception as e:
        logger.error(f"Failed to compare results: {str(e)}")
        return {}

def generate_executive_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate executive summary of analysis results"""
    try:
        business_case_score = results.get('business_case_score', {})
        scenarios = results.get('scenarios', [])
        
        # Find best and worst scenarios
        best_scenario = max(scenarios, key=lambda s: s['kpis'].get('roi', 0)) if scenarios else None
        worst_scenario = min(scenarios, key=lambda s: s['kpis'].get('roi', 0)) if scenarios else None
        
        summary = {
            'overall_score': business_case_score.get('score', 0),
            'confidence_level': business_case_score.get('confidence_band', [0, 0]),
            'key_findings': [
                f"Business case score: {(business_case_score.get('score', 0) * 100):.1f}%",
                f"Best case ROI: {(best_scenario['kpis']['roi'] * 100):.1f}%" if best_scenario else "N/A",
                f"Worst case ROI: {(worst_scenario['kpis']['roi'] * 100):.1f}%" if worst_scenario else "N/A"
            ],
            'recommendations': [
                "Proceed with implementation" if business_case_score.get('score', 0) > 0.7 else "Consider additional analysis",
                "Monitor key risk factors" if any(s['risk_level'] == 'High' for s in scenarios) else "Risk profile acceptable"
            ],
            'scenario_count': len(scenarios),
            'analysis_type': results.get('simulation_metadata', {}).get('analysis_type', 'unknown')
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to generate executive summary: {str(e)}")
        return {'error': 'Failed to generate summary'}
