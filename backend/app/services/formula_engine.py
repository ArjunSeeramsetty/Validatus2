# backend/app/services/formula_engine.py

import asyncio
import logging
import math
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
import numpy as np

from ..models.analysis_models import FactorCalculation
from ..middleware.monitoring import performance_monitor

logger = logging.getLogger(__name__)

@dataclass
class FormulaDefinition:
    """Definition of a calculation formula"""
    name: str
    description: str
    formula: str
    input_layers: List[str]
    output_type: str
    weight_factors: Dict[str, float]
    validation_rules: List[str]

class FormulaEngine:
    """Advanced formula calculation engine for strategic factors"""
    
    def __init__(self):
        # Define strategic factor formulas
        self.formulas = {
            'market_attractiveness': FormulaDefinition(
                name='Market Attractiveness',
                description='Overall attractiveness of the target market',
                formula='(market_size * growth_rate * competitive_advantage) / competitive_intensity',
                input_layers=['market', 'competitive', 'financial'],
                output_type='float',
                weight_factors={
                    'market_size': 0.3,
                    'growth_rate': 0.25,
                    'competitive_advantage': 0.25,
                    'competitive_intensity': 0.2
                },
                validation_rules=['market_size > 0', 'growth_rate >= 0', 'competitive_intensity > 0']
            ),
            'product_market_fit': FormulaDefinition(
                name='Product-Market Fit',
                description='Alignment between product and market needs',
                formula='(consumer_demand * product_innovation * user_satisfaction) / market_saturation',
                input_layers=['consumer', 'product', 'market', 'experience'],
                output_type='float',
                weight_factors={
                    'consumer_demand': 0.35,
                    'product_innovation': 0.25,
                    'user_satisfaction': 0.25,
                    'market_saturation': 0.15
                },
                validation_rules=['consumer_demand > 0', 'product_innovation >= 0', 'market_saturation >= 0']
            ),
            'operational_efficiency': FormulaDefinition(
                name='Operational Efficiency',
                description='Efficiency of business operations and processes',
                formula='(process_quality * cost_efficiency * scalability) - operational_risk',
                input_layers=['operations', 'financial', 'technology'],
                output_type='float',
                weight_factors={
                    'process_quality': 0.4,
                    'cost_efficiency': 0.3,
                    'scalability': 0.2,
                    'operational_risk': 0.1
                },
                validation_rules=['process_quality >= 0', 'cost_efficiency >= 0', 'scalability >= 0']
            ),
            'brand_strength': FormulaDefinition(
                name='Brand Strength',
                description='Overall strength and recognition of the brand',
                formula='(brand_awareness * brand_perception * brand_loyalty) * marketing_reach',
                input_layers=['brand', 'consumer', 'market'],
                output_type='float',
                weight_factors={
                    'brand_awareness': 0.3,
                    'brand_perception': 0.3,
                    'brand_loyalty': 0.25,
                    'marketing_reach': 0.15
                },
                validation_rules=['brand_awareness >= 0', 'brand_perception >= 0', 'brand_loyalty >= 0', 'marketing_reach >= 0']
            ),
            'technology_readiness': FormulaDefinition(
                name='Technology Readiness',
                description='Readiness and advancement of technology infrastructure',
                formula='(technical_innovation * scalability * security) / technical_complexity',
                input_layers=['technology', 'operations'],
                output_type='float',
                weight_factors={
                    'technical_innovation': 0.4,
                    'scalability': 0.3,
                    'security': 0.2,
                    'technical_complexity': 0.1
                },
                validation_rules=['technical_innovation >= 0', 'scalability >= 0', 'security >= 0', 'technical_complexity > 0']
            ),
            'financial_viability': FormulaDefinition(
                name='Financial Viability',
                description='Financial health and investment attractiveness',
                formula='(profitability * revenue_growth * financial_stability) / risk_factor',
                input_layers=['financial', 'market', 'competitive'],
                output_type='float',
                weight_factors={
                    'profitability': 0.4,
                    'revenue_growth': 0.3,
                    'financial_stability': 0.2,
                    'risk_factor': 0.1
                },
                validation_rules=['profitability >= 0', 'revenue_growth >= 0', 'financial_stability >= 0', 'risk_factor > 0']
            ),
            'regulatory_compliance': FormulaDefinition(
                name='Regulatory Compliance',
                description='Level of regulatory compliance and risk management',
                formula='(compliance_score * legal_stability) - regulatory_risk',
                input_layers=['regulatory', 'operations'],
                output_type='float',
                weight_factors={
                    'compliance_score': 0.6,
                    'legal_stability': 0.3,
                    'regulatory_risk': 0.1
                },
                validation_rules=['compliance_score >= 0', 'legal_stability >= 0']
            ),
            'customer_experience': FormulaDefinition(
                name='Customer Experience',
                description='Quality of customer experience and satisfaction',
                formula='(user_satisfaction * ease_of_use * customer_support) * engagement_score',
                input_layers=['experience', 'consumer', 'product'],
                output_type='float',
                weight_factors={
                    'user_satisfaction': 0.35,
                    'ease_of_use': 0.25,
                    'customer_support': 0.25,
                    'engagement_score': 0.15
                },
                validation_rules=['user_satisfaction >= 0', 'ease_of_use >= 0', 'customer_support >= 0', 'engagement_score >= 0']
            ),
            'competitive_advantage': FormulaDefinition(
                name='Competitive Advantage',
                description='Sustainable competitive advantages in the market',
                formula='(differentiation * market_position * barriers_to_competition) / competitive_intensity',
                input_layers=['competitive', 'product', 'market'],
                output_type='float',
                weight_factors={
                    'differentiation': 0.4,
                    'market_position': 0.3,
                    'barriers_to_competition': 0.2,
                    'competitive_intensity': 0.1
                },
                validation_rules=['differentiation >= 0', 'market_position >= 0', 'barriers_to_competition >= 0', 'competitive_intensity > 0']
            ),
            'innovation_potential': FormulaDefinition(
                name='Innovation Potential',
                description='Potential for future innovation and growth',
                formula='(product_innovation * technical_innovation * market_opportunity) * innovation_capability',
                input_layers=['product', 'technology', 'market'],
                output_type='float',
                weight_factors={
                    'product_innovation': 0.3,
                    'technical_innovation': 0.3,
                    'market_opportunity': 0.25,
                    'innovation_capability': 0.15
                },
                validation_rules=['product_innovation >= 0', 'technical_innovation >= 0', 'market_opportunity >= 0', 'innovation_capability >= 0']
            )
        }
        
    @performance_monitor
    async def calculate_all_factors(self, 
                                   layer_scores: Dict[str, float], 
                                   session_id: str) -> List[FactorCalculation]:
        """Calculate all strategic factors from layer scores"""
        
        logger.info(f"Calculating strategic factors for session {session_id}")
        
        try:
            factor_calculations = []
            
            # Process each formula
            for factor_name, formula_def in self.formulas.items():
                try:
                    # Calculate the factor
                    calculation = await self._calculate_single_factor(
                        factor_name, formula_def, layer_scores, session_id
                    )
                    
                    if calculation:
                        factor_calculations.append(calculation)
                        
                except Exception as e:
                    logger.error(f"Failed to calculate factor {factor_name}: {e}")
                    # Create error calculation
                    error_calculation = FactorCalculation(
                        session_id=session_id,
                        factor_name=factor_name,
                        formula_used=formula_def.formula,
                        input_layers=formula_def.input_layers,
                        calculated_value=0.0,
                        confidence_score=0.0,
                        calculation_steps=[{'step': 'error', 'value': str(e)}],
                        validation_metrics={'error': True, 'error_message': str(e)},
                        created_at=datetime.now(timezone.utc)
                    )
                    factor_calculations.append(error_calculation)
            
            logger.info(f"✅ Calculated {len(factor_calculations)} strategic factors")
            return factor_calculations
            
        except Exception as e:
            logger.error(f"Factor calculation failed: {e}")
            return []
    
    async def _calculate_single_factor(self, 
                                     factor_name: str, 
                                     formula_def: FormulaDefinition,
                                     layer_scores: Dict[str, float], 
                                     session_id: str) -> Optional[FactorCalculation]:
        """Calculate a single strategic factor"""
        
        try:
            # Map layer scores to formula inputs
            input_values = self._map_layer_scores_to_inputs(formula_def, layer_scores)
            
            # Validate inputs
            validation_result = self._validate_inputs(input_values, formula_def.validation_rules)
            
            if not validation_result['valid']:
                logger.warning(f"Validation failed for {factor_name}: {validation_result['errors']}")
            
            # Execute formula calculation
            calculation_steps = []
            calculated_value = await self._execute_formula(
                formula_def.formula, input_values, calculation_steps
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(input_values, validation_result)
            
            # Create validation metrics
            validation_metrics = {
                'input_completeness': validation_result['completeness'],
                'validation_passed': validation_result['valid'],
                'missing_inputs': validation_result['missing_inputs'],
                'validation_errors': validation_result['errors'],
                'calculation_complexity': len(calculation_steps)
            }
            
            # Create factor calculation result
            factor_calculation = FactorCalculation(
                session_id=session_id,
                factor_name=factor_name,
                formula_used=formula_def.formula,
                input_layers=formula_def.input_layers,
                calculated_value=calculated_value,
                confidence_score=confidence_score,
                calculation_steps=calculation_steps,
                validation_metrics=validation_metrics,
                created_at=datetime.now(timezone.utc)
            )
            
            logger.debug(f"Calculated {factor_name}: {calculated_value:.3f} (confidence: {confidence_score:.3f})")
            return factor_calculation
            
        except Exception as e:
            logger.error(f"Single factor calculation failed for {factor_name}: {e}")
            return None
    
    def _map_layer_scores_to_inputs(self, 
                                   formula_def: FormulaDefinition, 
                                   layer_scores: Dict[str, float]) -> Dict[str, float]:
        """Map layer scores to formula input variables"""
        
        input_values = {}
        
        # Define mapping from layers to formula variables
        layer_to_variable_mapping = {
            'consumer': ['consumer_demand', 'user_satisfaction', 'brand_loyalty', 'engagement_score'],
            'market': ['market_size', 'growth_rate', 'market_saturation', 'market_opportunity'],
            'product': ['product_innovation', 'differentiation'],
            'brand': ['brand_awareness', 'brand_perception', 'brand_loyalty', 'marketing_reach'],
            'experience': ['user_satisfaction', 'ease_of_use', 'customer_support', 'engagement_score'],
            'technology': ['technical_innovation', 'scalability', 'security', 'technical_complexity'],
            'operations': ['process_quality', 'cost_efficiency', 'scalability', 'operational_risk'],
            'financial': ['profitability', 'revenue_growth', 'financial_stability', 'risk_factor'],
            'competitive': ['competitive_advantage', 'competitive_intensity', 'market_position', 'barriers_to_competition'],
            'regulatory': ['compliance_score', 'legal_stability', 'regulatory_risk']
        }
        
        # Map layer scores to formula variables
        for layer, score in layer_scores.items():
            variables = layer_to_variable_mapping.get(layer.lower(), [])
            for variable in variables:
                # Use the layer score as base value for all its variables
                input_values[variable] = score
        
        # Handle special cases and combinations
        input_values.update(self._calculate_derived_inputs(layer_scores))
        
        return input_values
    
    def _calculate_derived_inputs(self, layer_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate derived inputs that combine multiple layer scores"""
        
        derived_inputs = {}
        
        try:
            # Market attractiveness components
            market_score = layer_scores.get('market', 0.5)
            competitive_score = layer_scores.get('competitive', 0.5)
            financial_score = layer_scores.get('financial', 0.5)
            
            derived_inputs['market_size'] = market_score * 0.8 + financial_score * 0.2
            derived_inputs['growth_rate'] = market_score * 0.6 + competitive_score * 0.4
            derived_inputs['competitive_intensity'] = 1.0 - competitive_score  # Inverse relationship
            derived_inputs['competitive_advantage'] = competitive_score
            
            # Product-market fit components
            consumer_score = layer_scores.get('consumer', 0.5)
            product_score = layer_scores.get('product', 0.5)
            experience_score = layer_scores.get('experience', 0.5)
            
            derived_inputs['consumer_demand'] = consumer_score
            derived_inputs['product_innovation'] = product_score * 0.7 + technology_score * 0.3 if 'technology' in layer_scores else product_score
            derived_inputs['user_satisfaction'] = experience_score * 0.6 + consumer_score * 0.4
            derived_inputs['market_saturation'] = 1.0 - market_score  # Inverse relationship
            
            # Operational efficiency components
            operations_score = layer_scores.get('operations', 0.5)
            technology_score = layer_scores.get('technology', 0.5)
            
            derived_inputs['process_quality'] = operations_score
            derived_inputs['cost_efficiency'] = operations_score * 0.7 + financial_score * 0.3
            derived_inputs['scalability'] = technology_score * 0.6 + operations_score * 0.4
            derived_inputs['operational_risk'] = 1.0 - operations_score  # Inverse relationship
            
            # Brand strength components
            brand_score = layer_scores.get('brand', 0.5)
            
            derived_inputs['brand_awareness'] = brand_score * 0.8 + market_score * 0.2
            derived_inputs['brand_perception'] = brand_score * 0.9 + experience_score * 0.1
            derived_inputs['brand_loyalty'] = brand_score * 0.7 + consumer_score * 0.3
            derived_inputs['marketing_reach'] = brand_score * 0.6 + market_score * 0.4
            
            # Technology readiness components
            derived_inputs['technical_innovation'] = technology_score
            derived_inputs['scalability'] = technology_score * 0.7 + operations_score * 0.3
            derived_inputs['security'] = technology_score * 0.8 + regulatory_score * 0.2 if 'regulatory' in layer_scores else technology_score
            derived_inputs['technical_complexity'] = 1.0 - technology_score  # Inverse relationship
            
            # Financial viability components
            derived_inputs['profitability'] = financial_score
            derived_inputs['revenue_growth'] = financial_score * 0.7 + market_score * 0.3
            derived_inputs['financial_stability'] = financial_score * 0.8 + operations_score * 0.2
            derived_inputs['risk_factor'] = 1.0 - financial_score  # Inverse relationship
            
            # Regulatory compliance components
            if 'regulatory' in layer_scores:
                regulatory_score = layer_scores['regulatory']
                derived_inputs['compliance_score'] = regulatory_score
                derived_inputs['legal_stability'] = regulatory_score * 0.9 + operations_score * 0.1
                derived_inputs['regulatory_risk'] = 1.0 - regulatory_score  # Inverse relationship
            
            # Customer experience components
            derived_inputs['user_satisfaction'] = experience_score * 0.6 + consumer_score * 0.4
            derived_inputs['ease_of_use'] = experience_score * 0.8 + product_score * 0.2
            derived_inputs['customer_support'] = experience_score * 0.7 + operations_score * 0.3
            derived_inputs['engagement_score'] = experience_score * 0.5 + brand_score * 0.3 + consumer_score * 0.2
            
            # Competitive advantage components
            derived_inputs['differentiation'] = product_score * 0.6 + brand_score * 0.4
            derived_inputs['market_position'] = competitive_score * 0.7 + market_score * 0.3
            derived_inputs['barriers_to_competition'] = competitive_score * 0.8 + technology_score * 0.2
            
            # Innovation potential components
            derived_inputs['product_innovation'] = product_score * 0.7 + technology_score * 0.3
            derived_inputs['technical_innovation'] = technology_score
            derived_inputs['market_opportunity'] = market_score * 0.8 + competitive_score * 0.2
            derived_inputs['innovation_capability'] = product_score * 0.5 + technology_score * 0.5
            
        except Exception as e:
            logger.error(f"Derived input calculation failed: {e}")
            # Set default values
            for key in derived_inputs:
                derived_inputs[key] = 0.5
        
        return derived_inputs
    
    def _validate_inputs(self, 
                        input_values: Dict[str, float], 
                        validation_rules: List[str]) -> Dict[str, Any]:
        """Validate input values against validation rules"""
        
        validation_result = {
            'valid': True,
            'errors': [],
            'missing_inputs': [],
            'completeness': 0.0
        }
        
        try:
            # Check for missing inputs
            required_vars = set()
            for rule in validation_rules:
                # Extract variable names from rules
                var_matches = [var for var in input_values.keys() if var in rule]
                required_vars.update(var_matches)
            
            missing_vars = required_vars - set(input_values.keys())
            validation_result['missing_inputs'] = list(missing_vars)
            
            # Calculate completeness
            total_required = len(required_vars)
            provided = total_required - len(missing_vars)
            validation_result['completeness'] = provided / total_required if total_required > 0 else 1.0
            
            # Validate rules
            for rule in validation_rules:
                try:
                    # Simple rule validation (can be enhanced)
                    if '> 0' in rule:
                        var_name = rule.split(' > 0')[0].strip()
                        if var_name in input_values and input_values[var_name] <= 0:
                            validation_result['errors'].append(f"{var_name} must be greater than 0")
                            validation_result['valid'] = False
                    elif '>= 0' in rule:
                        var_name = rule.split(' >= 0')[0].strip()
                        if var_name in input_values and input_values[var_name] < 0:
                            validation_result['errors'].append(f"{var_name} must be greater than or equal to 0")
                            validation_result['valid'] = False
                except Exception as e:
                    validation_result['errors'].append(f"Rule validation error: {str(e)}")
                    validation_result['valid'] = False
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            validation_result['valid'] = False
            validation_result['errors'].append(str(e))
        
        return validation_result
    
    async def _execute_formula(self, 
                             formula: str, 
                             input_values: Dict[str, float], 
                             calculation_steps: List[Dict[str, Any]]) -> float:
        """Execute the formula calculation with step tracking"""
        
        try:
            # Replace variables in formula with actual values
            formula_with_values = formula
            
            for var_name, value in input_values.items():
                formula_with_values = formula_with_values.replace(var_name, str(value))
                calculation_steps.append({
                    'step': f'substitute_{var_name}',
                    'variable': var_name,
                    'value': value,
                    'formula': formula_with_values
                })
            
            # Safe evaluation of mathematical expressions
            result = self._safe_eval_formula(formula_with_values, calculation_steps)
            
            # Normalize result to 0-1 range
            normalized_result = max(0.0, min(1.0, result))
            
            calculation_steps.append({
                'step': 'normalize_result',
                'raw_result': result,
                'normalized_result': normalized_result
            })
            
            return normalized_result
            
        except Exception as e:
            logger.error(f"Formula execution failed: {e}")
            calculation_steps.append({
                'step': 'error',
                'error': str(e)
            })
            return 0.0
    
    def _safe_eval_formula(self, 
                          formula: str, 
                          calculation_steps: List[Dict[str, Any]]) -> float:
        """Safely evaluate mathematical formula"""
        
        try:
            # Remove spaces
            formula = formula.replace(' ', '')
            
            # Handle parentheses
            while '(' in formula and ')' in formula:
                start = formula.rfind('(')
                end = formula.find(')', start)
                
                if start != -1 and end != -1:
                    sub_formula = formula[start+1:end]
                    sub_result = self._evaluate_simple_expression(sub_formula)
                    
                    calculation_steps.append({
                        'step': 'evaluate_subexpression',
                        'sub_formula': sub_formula,
                        'result': sub_result
                    })
                    
                    formula = formula[:start] + str(sub_result) + formula[end+1:]
                else:
                    break
            
            # Evaluate final expression
            final_result = self._evaluate_simple_expression(formula)
            
            calculation_steps.append({
                'step': 'final_evaluation',
                'formula': formula,
                'result': final_result
            })
            
            return final_result
            
        except Exception as e:
            logger.error(f"Safe formula evaluation failed: {e}")
            return 0.0
    
    def _evaluate_simple_expression(self, expression: str) -> float:
        """Evaluate simple mathematical expressions"""
        
        try:
            # Handle basic operations
            if '*' in expression:
                parts = expression.split('*')
                result = 1.0
                for part in parts:
                    result *= float(part)
                return result
            
            elif '/' in expression:
                parts = expression.split('/')
                if len(parts) == 2:
                    numerator = float(parts[0])
                    denominator = float(parts[1])
                    return numerator / denominator if denominator != 0 else 0.0
                else:
                    # Multiple divisions
                    result = float(parts[0])
                    for part in parts[1:]:
                        denominator = float(part)
                        result = result / denominator if denominator != 0 else 0.0
                    return result
            
            elif '+' in expression:
                parts = expression.split('+')
                result = 0.0
                for part in parts:
                    result += float(part)
                return result
            
            elif '-' in expression and not expression.startswith('-'):
                parts = expression.split('-')
                result = float(parts[0])
                for part in parts[1:]:
                    result -= float(part)
                return result
            
            else:
                # Single number
                return float(expression)
                
        except Exception as e:
            logger.error(f"Simple expression evaluation failed: {e}")
            return 0.0
    
    def _calculate_confidence(self, 
                            input_values: Dict[str, float], 
                            validation_result: Dict[str, Any]) -> float:
        """Calculate confidence score for the calculation"""
        
        try:
            # Base confidence on input completeness and validation
            completeness_score = validation_result.get('completeness', 0.0)
            validation_score = 1.0 if validation_result.get('valid', False) else 0.5
            
            # Factor in input value distribution
            values = list(input_values.values())
            if values:
                value_variance = np.var(values)
                distribution_score = max(0.5, 1.0 - value_variance)  # Lower variance = higher confidence
            else:
                distribution_score = 0.0
            
            # Combine confidence factors
            confidence = (completeness_score * 0.4 + validation_score * 0.4 + distribution_score * 0.2)
            
            return round(confidence, 3)
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5

# Export the class
__all__ = ['FormulaEngine', 'FormulaDefinition']
