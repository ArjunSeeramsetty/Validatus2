# backend/app/services/enhanced_data_pipeline/__init__.py
"""
Enhanced Data Pipeline for Phase C Integration

This package contains advanced data processing capabilities that extend
the basic Validatus platform with sophisticated Bayesian methods, event
modeling, and enhanced content processing.

Components:
- Bayesian Data Blender: Probabilistic fusion of multiple data sources
- Event Shock Modeler: Temporal decay analysis for external events
- Enhanced Content Processor: Advanced quality analysis with multi-dimensional metrics
"""

from .bayesian_data_blender import BayesianDataBlender, DataSource, BayesianBlendResult
from .event_shock_modeler import EventShockModeler, EventShock, ShockModelResult, DecayFunction, EventType

__all__ = [
    # Bayesian Data Blender
    'BayesianDataBlender',
    'DataSource',
    'BayesianBlendResult',
    
    # Event Shock Modeler
    'EventShockModeler',
    'EventShock',
    'ShockModelResult',
    'DecayFunction',
    'EventType'
]
