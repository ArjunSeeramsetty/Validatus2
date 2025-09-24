# backend/app/services/enhanced_knowledge/__init__.py
"""
Enhanced Knowledge Management for Phase C Integration

This package contains advanced knowledge retrieval and management capabilities
that extend the basic Validatus platform with hybrid vector stores, advanced
RAG capabilities, and multi-source knowledge fusion.

Components:
- Hybrid Vector Store Manager: Combines GCP Vertex AI with ChromaDB
- Advanced RAG capabilities with result fusion strategies
- Multi-source knowledge integration and retrieval
"""

from .hybrid_vector_store_manager import (
    HybridVectorStoreManager, 
    ChromaDBAdapter, 
    HybridSearchResult
)

__all__ = [
    'HybridVectorStoreManager',
    'ChromaDBAdapter',
    'HybridSearchResult'
]
