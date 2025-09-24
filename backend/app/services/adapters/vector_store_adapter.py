# backend/app/services/adapters/vector_store_adapter.py
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VectorSearchResult:
    """Standardized vector search result"""
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    source_id: str
    chunk_index: int

@dataclass
class VectorStoreMetadata:
    """Standardized vector store metadata"""
    store_id: str
    store_type: str
    document_count: int
    chunk_count: int
    created_at: str
    last_updated: str

class VectorStoreAdapter(ABC):
    """Abstract adapter for different vector store implementations"""
    
    @abstractmethod
    async def create_store(self, store_id: str, documents: List[Dict[str, Any]]) -> bool:
        """Create a new vector store"""
        pass
    
    @abstractmethod
    async def search(self, query: str, store_id: str, k: int = 10) -> List[VectorSearchResult]:
        """Search for similar content"""
        pass
    
    @abstractmethod
    async def add_documents(self, store_id: str, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to existing store"""
        pass
    
    @abstractmethod
    async def get_metadata(self, store_id: str) -> Optional[VectorStoreMetadata]:
        """Get store metadata"""
        pass
    
    @abstractmethod
    async def delete_store(self, store_id: str) -> bool:
        """Delete a vector store"""
        pass

class GCPVectorStoreAdapter(VectorStoreAdapter):
    """Adapter for GCP Vertex AI Vector Search"""
    
    def __init__(self, gcp_vector_store_manager):
        self.gcp_manager = gcp_vector_store_manager
        self.store_type = "gcp_vertex_ai"
    
    async def create_store(self, store_id: str, documents: List[Dict[str, Any]]) -> bool:
        """Create GCP vector store"""
        try:
            # Extract URLs from documents for GCP manager
            urls = [doc.get('url', '') for doc in documents if doc.get('url')]
            topic_id = await self.gcp_manager.create_topic_store(store_id, urls)
            logger.info(f"✅ GCP vector store created: {topic_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create GCP vector store: {e}")
            return False
    
    async def search(self, query: str, store_id: str, k: int = 10) -> List[VectorSearchResult]:
        """Search GCP vector store"""
        try:
            evidence_chunks = await self.gcp_manager.retrieve_by_topic_layer(
                store_id, query, k
            )
            
            results = []
            for chunk in evidence_chunks:
                result = VectorSearchResult(
                    content=chunk.content,
                    metadata={
                        'layer': chunk.layer,
                        'factor': chunk.factor,
                        'segment': chunk.segment,
                        'url': chunk.url,
                        'title': chunk.title,
                        'quality_score': chunk.quality_score
                    },
                    similarity_score=chunk.similarity_score,
                    source_id=chunk.url,
                    chunk_index=chunk.chunk_index
                )
                results.append(result)
            
            logger.info(f"✅ GCP vector search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"GCP vector search failed: {e}")
            return []
    
    async def add_documents(self, store_id: str, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to GCP vector store"""
        # This would require extending GCP manager functionality
        logger.info("Adding documents to GCP vector store (placeholder)")
        return True
    
    async def get_metadata(self, store_id: str) -> Optional[VectorStoreMetadata]:
        """Get GCP vector store metadata"""
        try:
            # Get metadata from GCP manager
            if hasattr(self.gcp_manager, '_topic_metadata'):
                metadata = self.gcp_manager._topic_metadata.get(store_id)
                if metadata:
                    return VectorStoreMetadata(
                        store_id=metadata.topic_id,
                        store_type=self.store_type,
                        document_count=metadata.document_count,
                        chunk_count=metadata.chunk_count,
                        created_at=metadata.created_at,
                        last_updated=metadata.last_updated
                    )
        except Exception as e:
            logger.error(f"Failed to get GCP vector store metadata: {e}")
        return None
    
    async def delete_store(self, store_id: str) -> bool:
        """Delete GCP vector store"""
        logger.info(f"Deleting GCP vector store: {store_id} (placeholder)")
        return True

class ChromaDBVectorStoreAdapter(VectorStoreAdapter):
    """Adapter for ChromaDB (when integrated in Phase C)"""
    
    def __init__(self):
        self.store_type = "chromadb"
        logger.info("ChromaDB adapter initialized (placeholder for Phase C)")
    
    async def create_store(self, store_id: str, documents: List[Dict[str, Any]]) -> bool:
        """Create ChromaDB vector store"""
        logger.info(f"ChromaDB store creation: {store_id} (Phase C implementation)")
        return True
    
    async def search(self, query: str, store_id: str, k: int = 10) -> List[VectorSearchResult]:
        """Search ChromaDB vector store"""
        logger.info(f"ChromaDB search: {query} (Phase C implementation)")
        return []
    
    async def add_documents(self, store_id: str, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to ChromaDB store"""
        logger.info("ChromaDB add documents (Phase C implementation)")
        return True
    
    async def get_metadata(self, store_id: str) -> Optional[VectorStoreMetadata]:
        """Get ChromaDB store metadata"""
        logger.info("ChromaDB get metadata (Phase C implementation)")
        return None
    
    async def delete_store(self, store_id: str) -> bool:
        """Delete ChromaDB store"""
        logger.info("ChromaDB delete store (Phase C implementation)")
        return True

class HybridVectorStoreManager:
    """Manager for multiple vector store backends"""
    
    def __init__(self, gcp_manager=None):
        self.adapters = {}
        
        # Initialize available adapters
        if gcp_manager:
            self.adapters['gcp'] = GCPVectorStoreAdapter(gcp_manager)
        
        # Import FeatureFlags at runtime to avoid circular imports
        try:
            from ...core.feature_flags import FeatureFlags
            if FeatureFlags.HYBRID_VECTOR_STORE_ENABLED:
                self.adapters['chromadb'] = ChromaDBVectorStoreAdapter()
        except ImportError:
            logger.warning("FeatureFlags not available for hybrid vector store")
        
        self.primary_adapter = 'gcp'  # Default to GCP
        logger.info(f"✅ Hybrid vector store manager initialized with adapters: {list(self.adapters.keys())}")
    
    async def search_all_stores(self, query: str, store_id: str, k: int = 10) -> Dict[str, List[VectorSearchResult]]:
        """Search across all available vector stores"""
        results = {}
        
        for adapter_name, adapter in self.adapters.items():
            try:
                store_results = await adapter.search(query, store_id, k)
                results[adapter_name] = store_results
                logger.info(f"✅ {adapter_name} returned {len(store_results)} results")
            except Exception as e:
                logger.error(f"Search failed for {adapter_name}: {e}")
                results[adapter_name] = []
        
        return results
    
    async def create_in_all_stores(self, store_id: str, documents: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Create vector store in all available backends"""
        results = {}
        
        for adapter_name, adapter in self.adapters.items():
            try:
                success = await adapter.create_store(store_id, documents)
                results[adapter_name] = success
                logger.info(f"✅ {adapter_name} store creation: {success}")
            except Exception as e:
                logger.error(f"Store creation failed for {adapter_name}: {e}")
                results[adapter_name] = False
        
        return results
    
    def get_primary_adapter(self) -> VectorStoreAdapter:
        """Get the primary vector store adapter"""
        return self.adapters.get(self.primary_adapter)
    
    def set_primary_adapter(self, adapter_name: str) -> bool:
        """Set the primary vector store adapter"""
        if adapter_name in self.adapters:
            self.primary_adapter = adapter_name
            logger.info(f"Primary adapter set to: {adapter_name}")
            return True
        return False

__all__ = [
    'VectorStoreAdapter', 
    'GCPVectorStoreAdapter', 
    'ChromaDBVectorStoreAdapter', 
    'HybridVectorStoreManager',
    'VectorSearchResult',
    'VectorStoreMetadata'
]
