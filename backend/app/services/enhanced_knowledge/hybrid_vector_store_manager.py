# backend/app/services/enhanced_knowledge/hybrid_vector_store_manager.py
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import numpy as np

from ..gcp_topic_vector_store_manager import GCPTopicVectorStoreManager
from ..adapters.vector_store_adapter import VectorStoreAdapter, VectorSearchResult
from ...core.feature_flags import FeatureFlags

# Conditional ChromaDB import
try:
    if FeatureFlags.HYBRID_VECTOR_STORE_ENABLED:
        import chromadb
        from chromadb.config import Settings
        CHROMADB_AVAILABLE = True
    else:
        chromadb = None
        CHROMADB_AVAILABLE = False
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class HybridSearchResult:
    """Enhanced search result combining multiple vector stores"""
    query: str
    combined_results: List[VectorSearchResult]
    store_contributions: Dict[str, List[VectorSearchResult]]
    result_fusion_metadata: Dict[str, Any]
    total_results: int
    search_time: float

class ChromaDBAdapter(VectorStoreAdapter):
    """ChromaDB adapter for hybrid vector store"""
    
    def __init__(self, persist_directory: str = "./chromadb_data"):
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB not available - install with: pip install chromadb")
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collections = {}
        logger.info("✅ ChromaDB adapter initialized")
    
    async def create_store(self, store_id: str, documents: List[Dict[str, Any]]) -> bool:
        """Create ChromaDB collection"""
        try:
            # Create or get collection
            collection = self.client.get_or_create_collection(
                name=store_id,
                metadata={"created_at": datetime.now(timezone.utc).isoformat()}
            )
            
            self.collections[store_id] = collection
            
            # Add documents if provided
            if documents:
                await self.add_documents(store_id, documents)
            
            logger.info(f"✅ ChromaDB store created: {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create ChromaDB store {store_id}: {e}")
            return False
    
    async def add_documents(self, store_id: str, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to ChromaDB collection"""
        try:
            if store_id not in self.collections:
                await self.create_store(store_id, [])
            
            collection = self.collections[store_id]
            
            # Prepare documents for ChromaDB
            ids = []
            texts = []
            metadatas = []
            
            for i, doc in enumerate(documents):
                doc_id = doc.get('id', f"{store_id}_{i}")
                content = doc.get('content', doc.get('text', ''))
                metadata = {
                    'source': doc.get('source', 'unknown'),
                    'timestamp': doc.get('timestamp', datetime.now(timezone.utc).isoformat()),
                    'quality_score': doc.get('quality_score', 0.5)
                }
                
                ids.append(doc_id)
                texts.append(content)
                metadatas.append(metadata)
            
            # Add to collection in batches
            batch_size = 100
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_texts = texts[i:i+batch_size]
                batch_metadatas = metadatas[i:i+batch_size]
                
                collection.add(
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
            
            logger.info(f"✅ Added {len(documents)} documents to ChromaDB store {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB store {store_id}: {e}")
            return False
    
    async def search(self, query: str, store_id: str, k: int = 10) -> List[VectorSearchResult]:
        """Search ChromaDB collection"""
        try:
            if store_id not in self.collections:
                logger.warning(f"ChromaDB store {store_id} not found")
                return []
            
            collection = self.collections[store_id]
            
            # Perform search
            search_results = collection.query(
                query_texts=[query],
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Convert to VectorSearchResult format
            results = []
            if search_results['documents'] and search_results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    search_results['documents'][0],
                    search_results['metadatas'][0],
                    search_results['distances'][0]
                )):
                    # Convert distance to similarity (ChromaDB uses cosine distance)
                    similarity_score = 1.0 - distance
                    
                    result = VectorSearchResult(
                        content=doc,
                        metadata=metadata,
                        similarity_score=similarity_score,
                        source_id=metadata.get('source', 'chromadb'),
                        chunk_index=i
                    )
                    results.append(result)
            
            logger.info(f"✅ ChromaDB search returned {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"ChromaDB search failed for store {store_id}: {e}")
            return []
    
    async def get_metadata(self, store_id: str) -> Optional[Dict[str, Any]]:
        """Get ChromaDB store metadata"""
        try:
            if store_id not in self.collections:
                return None
            
            collection = self.collections[store_id]
            count = collection.count()
            
            return {
                'store_id': store_id,
                'store_type': 'chromadb',
                'document_count': count,
                'chunk_count': count,  # ChromaDB counts at document level
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get ChromaDB metadata for {store_id}: {e}")
            return None
    
    async def delete_store(self, store_id: str) -> bool:
        """Delete ChromaDB collection"""
        try:
            if store_id in self.collections:
                self.client.delete_collection(name=store_id)
                del self.collections[store_id]
                logger.info(f"✅ ChromaDB store deleted: {store_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete ChromaDB store {store_id}: {e}")
            return False

class HybridVectorStoreManager:
    """
    Hybrid Vector Store Manager extending GCP capabilities with ChromaDB
    Provides unified interface for multiple vector store backends
    """
    
    def __init__(self, project_id: str = None):
        self.gcp_manager = GCPTopicVectorStoreManager(project_id=project_id)
        
        # Initialize ChromaDB adapter if enabled
        if FeatureFlags.HYBRID_VECTOR_STORE_ENABLED and CHROMADB_AVAILABLE:
            try:
                self.chromadb_adapter = ChromaDBAdapter()
                self.hybrid_enabled = True
                logger.info("✅ Hybrid vector store with ChromaDB enabled")
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed: {e}")
                self.chromadb_adapter = None
                self.hybrid_enabled = False
        else:
            self.chromadb_adapter = None
            self.hybrid_enabled = False
            logger.info("Hybrid vector store disabled - using GCP only")
        
        # Store selection strategy
        self.store_strategy = {
            'primary': 'gcp',      # Primary store for new data
            'fallback': 'chromadb', # Fallback for additional search
            'fusion_method': 'ranked_fusion'  # Method for combining results
        }
    
    async def create_hybrid_store(self, 
                                store_id: str, 
                                documents: List[Dict[str, Any]],
                                store_in_both: bool = True) -> Dict[str, bool]:
        """Create vector store in both GCP and ChromaDB"""
        results = {'gcp': False, 'chromadb': False}
        
        try:
            # Always create in GCP (primary)
            urls = [doc.get('url', '') for doc in documents if doc.get('url')]
            if urls:
                gcp_result = await self.gcp_manager.create_topic_store(store_id, urls)
                results['gcp'] = bool(gcp_result)
            
            # Create in ChromaDB if hybrid enabled and requested
            if self.hybrid_enabled and store_in_both and self.chromadb_adapter:
                chromadb_result = await self.chromadb_adapter.create_store(store_id, documents)
                results['chromadb'] = chromadb_result
            
            logger.info(f"✅ Hybrid store creation: GCP={results['gcp']}, ChromaDB={results['chromadb']}")
            return results
            
        except Exception as e:
            logger.error(f"Hybrid store creation failed: {e}")
            return results
    
    async def hybrid_search(self, 
                          query: str, 
                          store_id: str, 
                          k: int = 10,
                          fusion_strategy: str = 'ranked_fusion') -> HybridSearchResult:
        """Search across multiple vector stores with result fusion"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Parallel search across stores
            search_tasks = []
            
            # GCP search (always available)
            gcp_task = self._search_gcp_store(query, store_id, k)
            search_tasks.append(('gcp', gcp_task))
            
            # ChromaDB search (if available)
            if self.hybrid_enabled and self.chromadb_adapter:
                chromadb_task = self._search_chromadb_store(query, store_id, k)
                search_tasks.append(('chromadb', chromadb_task))
            
            # Execute searches in parallel
            search_results = {}
            for store_name, task in search_tasks:
                try:
                    results = await task
                    search_results[store_name] = results
                except Exception as e:
                    logger.error(f"Search failed for {store_name}: {e}")
                    search_results[store_name] = []
            
            # Fuse results from multiple stores
            fused_results = await self._fuse_search_results(
                search_results, fusion_strategy, k
            )
            
            # Calculate metadata
            search_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = HybridSearchResult(
                query=query,
                combined_results=fused_results,
                store_contributions=search_results,
                result_fusion_metadata={
                    'fusion_strategy': fusion_strategy,
                    'stores_searched': list(search_results.keys()),
                    'total_raw_results': sum(len(results) for results in search_results.values())
                },
                total_results=len(fused_results),
                search_time=search_time
            )
            
            logger.info(f"✅ Hybrid search completed: {len(fused_results)} results in {search_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return self._create_fallback_search_result(query, store_id)
    
    async def _search_gcp_store(self, query: str, store_id: str, k: int) -> List[VectorSearchResult]:
        """Search GCP vector store"""
        try:
            # Use existing GCP manager
            evidence_chunks = await self.gcp_manager.retrieve_by_topic_layer(store_id, query, k)
            
            # Convert to standard format
            results = []
            for chunk in evidence_chunks:
                result = VectorSearchResult(
                    content=chunk.content,
                    metadata={
                        'layer': getattr(chunk, 'layer', 'unknown'),
                        'factor': getattr(chunk, 'factor', 'unknown'),
                        'segment': getattr(chunk, 'segment', 'unknown'),
                        'url': getattr(chunk, 'url', ''),
                        'title': getattr(chunk, 'title', ''),
                        'quality_score': getattr(chunk, 'quality_score', 0.5)
                    },
                    similarity_score=getattr(chunk, 'similarity_score', 0.5),
                    source_id=getattr(chunk, 'url', 'gcp_source'),
                    chunk_index=getattr(chunk, 'chunk_index', 0)
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"GCP search failed: {e}")
            return []
    
    async def _search_chromadb_store(self, query: str, store_id: str, k: int) -> List[VectorSearchResult]:
        """Search ChromaDB store"""
        if not self.chromadb_adapter:
            return []
        
        return await self.chromadb_adapter.search(query, store_id, k)
    
    async def _fuse_search_results(self, 
                                 store_results: Dict[str, List[VectorSearchResult]], 
                                 fusion_strategy: str,
                                 k: int) -> List[VectorSearchResult]:
        """Fuse search results from multiple stores"""
        try:
            if fusion_strategy == 'ranked_fusion':
                return await self._ranked_fusion(store_results, k)
            elif fusion_strategy == 'score_fusion':
                return await self._score_fusion(store_results, k)
            elif fusion_strategy == 'round_robin':
                return await self._round_robin_fusion(store_results, k)
            else:
                # Default to ranked fusion
                return await self._ranked_fusion(store_results, k)
                
        except Exception as e:
            logger.error(f"Result fusion failed: {e}")
            # Fallback to simple concatenation
            all_results = []
            for results in store_results.values():
                all_results.extend(results)
            return sorted(all_results, key=lambda x: x.similarity_score, reverse=True)[:k]
    
    async def _ranked_fusion(self, store_results: Dict[str, List[VectorSearchResult]], k: int) -> List[VectorSearchResult]:
        """Reciprocal Rank Fusion (RRF) for combining ranked results"""
        fusion_scores = {}
        
        for store_name, results in store_results.items():
            for rank, result in enumerate(results):
                # Create unique key for deduplication
                result_key = f"{result.content[:100]}_{result.source_id}"
                
                # RRF score: 1 / (rank + 60)
                rrf_score = 1.0 / (rank + 60)
                
                if result_key in fusion_scores:
                    fusion_scores[result_key]['score'] += rrf_score
                    fusion_scores[result_key]['sources'].append(store_name)
                else:
                    fusion_scores[result_key] = {
                        'result': result,
                        'score': rrf_score,
                        'sources': [store_name]
                    }
        
        # Sort by fusion score and return top k
        sorted_results = sorted(
            fusion_scores.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )
        
        # Update metadata with fusion information
        fused_results = []
        for i, item in enumerate(sorted_results[:k]):
            result = item['result']
            result.metadata['fusion_score'] = item['score']
            result.metadata['contributing_stores'] = item['sources']
            result.metadata['fusion_rank'] = i + 1
            fused_results.append(result)
        
        return fused_results
    
    async def _score_fusion(self, store_results: Dict[str, List[VectorSearchResult]], k: int) -> List[VectorSearchResult]:
        """Score-based fusion using similarity scores"""
        all_results = []
        seen_content = set()
        
        for store_name, results in store_results.items():
            store_weight = 0.6 if store_name == 'gcp' else 0.4  # Prefer GCP slightly
            
            for result in results:
                content_hash = hash(result.content[:200])  # Deduplicate by content
                
                if content_hash not in seen_content:
                    # Weight the similarity score by store preference
                    weighted_score = result.similarity_score * store_weight
                    result.similarity_score = weighted_score
                    result.metadata['store_source'] = store_name
                    result.metadata['original_score'] = result.similarity_score / store_weight
                    
                    all_results.append(result)
                    seen_content.add(content_hash)
        
        # Sort by weighted similarity score
        return sorted(all_results, key=lambda x: x.similarity_score, reverse=True)[:k]
    
    async def _round_robin_fusion(self, store_results: Dict[str, List[VectorSearchResult]], k: int) -> List[VectorSearchResult]:
        """Round-robin fusion for balanced representation"""
        fused_results = []
        store_names = list(store_results.keys())
        store_indices = {name: 0 for name in store_names}
        seen_content = set()
        
        round_count = 0
        max_rounds = k * 2  # Prevent infinite loop
        
        while len(fused_results) < k and round_count < max_rounds:
            added_this_round = False
            
            for store_name in store_names:
                if len(fused_results) >= k:
                    break
                
                store_index = store_indices[store_name]
                store_results_list = store_results[store_name]
                
                if store_index < len(store_results_list):
                    result = store_results_list[store_index]
                    content_hash = hash(result.content[:200])
                    
                    if content_hash not in seen_content:
                        result.metadata['store_source'] = store_name
                        result.metadata['round_robin_position'] = len(fused_results)
                        fused_results.append(result)
                        seen_content.add(content_hash)
                        added_this_round = True
                    
                    store_indices[store_name] += 1
            
            if not added_this_round:
                break
            
            round_count += 1
        
        return fused_results
    
    def _create_fallback_search_result(self, query: str, store_id: str) -> HybridSearchResult:
        """Create fallback search result on error"""
        return HybridSearchResult(
            query=query,
            combined_results=[],
            store_contributions={},
            result_fusion_metadata={'error': 'Search failed', 'fallback': True},
            total_results=0,
            search_time=0.0
        )
    
    async def get_store_health(self) -> Dict[str, Any]:
        """Get health status of all vector stores"""
        health_status = {
            'gcp': {'status': 'unknown', 'details': {}},
            'chromadb': {'status': 'disabled', 'details': {}}
        }
        
        # Check GCP store health
        try:
            # Basic health check - try to get available topics
            topics = await self.gcp_manager.get_available_topics()
            health_status['gcp'] = {
                'status': 'healthy',
                'details': {'available_topics': len(topics)}
            }
        except Exception as e:
            health_status['gcp'] = {
                'status': 'unhealthy',
                'details': {'error': str(e)}
            }
        
        # Check ChromaDB health
        if self.hybrid_enabled and self.chromadb_adapter:
            try:
                collections = len(self.chromadb_adapter.collections)
                health_status['chromadb'] = {
                    'status': 'healthy',
                    'details': {'collections': collections}
                }
            except Exception as e:
                health_status['chromadb'] = {
                    'status': 'unhealthy',
                    'details': {'error': str(e)}
                }
        
        return health_status

__all__ = ['HybridVectorStoreManager', 'ChromaDBAdapter', 'HybridSearchResult']
