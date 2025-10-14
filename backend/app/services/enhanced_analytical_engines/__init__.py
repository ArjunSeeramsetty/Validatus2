# backend/app/services/enhanced_analytical_engines/__init__.py
"""
Enhanced Analytical Engines for Phase B Integration

This package contains sophisticated analytical capabilities that extend
the basic Validatus platform with advanced mathematical models, formula
engines, and strategic assessment tools.

Components:
- Mathematical Models: Advanced normalization and robustness calculations
- PDF Formula Engine: F1-F28 factor calculations with mathematical precision
- Action Layer Calculator: 18 strategic assessment layers
- Monte Carlo Simulator: Risk analysis and scenario modeling
- Formula Adapters: Bridge between existing and enhanced engines
"""

from .mathematical_models import MathematicalModels, NormalizationMethod, RobustnessMultipliers, FactorWeight
from .pdf_formula_engine import PDFFormulaEngine, FactorInput, FactorResult, PDFAnalysisResult
from .action_layer_calculator import ActionLayerCalculator, ActionLayerAnalysis, ActionLayerResult, ActionRecommendation
from .monte_carlo_simulator import MonteCarloSimulator, SimulationParameters, SimulationResult
from .pattern_library import PatternLibrary, PatternMatch, PatternType

# Formula adapters are optional - only import if needed (requires full dependencies)
try:
    from .formula_adapters import EnhancedFormulaAdapter
    FORMULA_ADAPTERS_AVAILABLE = True
except ImportError:
    EnhancedFormulaAdapter = None
    FORMULA_ADAPTERS_AVAILABLE = False

__all__ = [
    # Mathematical Models
    'MathematicalModels',
    'NormalizationMethod', 
    'RobustnessMultipliers',
    'FactorWeight',
    
    # PDF Formula Engine
    'PDFFormulaEngine',
    'FactorInput',
    'FactorResult', 
    'PDFAnalysisResult',
    
    # Action Layer Calculator
    'ActionLayerCalculator',
    'ActionLayerAnalysis',
    'ActionLayerResult',
    'ActionRecommendation',
    
    # Monte Carlo Simulator
    'MonteCarloSimulator',
    'SimulationParameters',
    'SimulationResult',
    
    # Pattern Library
    'PatternLibrary',
    'PatternMatch',
    'PatternType',
    
    # Conditional exports
    'FORMULA_ADAPTERS_AVAILABLE'
]

# Add EnhancedFormulaAdapter to exports if available
if FORMULA_ADAPTERS_AVAILABLE:
    __all__.append('EnhancedFormulaAdapter')
