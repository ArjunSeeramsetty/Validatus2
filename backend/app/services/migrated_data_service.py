"""
Service layer for migrated v2 data - follows Validatus2 patterns
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MigratedDataService:
    """Service for handling migrated v2 data with proper abstraction"""
    
    def __init__(self):
        self.migrated_data_root = Path(__file__).parents[2] / "migrated_data"
        self.analysis_results_dir = self.migrated_data_root / "analysis_results"
        self.sessions_dir = self.migrated_data_root / "sessions"
        self.topics_dir = self.migrated_data_root / "topics"
        self.vector_store_dir = self.migrated_data_root / "vector_store"
        self.frontend_dir = self.migrated_data_root / "frontend"
        
        # Ensure directories exist
        for dir_path in [self.analysis_results_dir, self.sessions_dir, 
                        self.topics_dir, self.vector_store_dir, self.frontend_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    async def get_available_topics(self) -> Dict[str, Any]:
        """Get list of available migrated topics"""
        try:
            topics_file = self.frontend_dir / "available_topics.json"
            
            if topics_file.exists():
                with open(topics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Fallback: scan analysis results directory
            topics = []
            for result_file in self.analysis_results_dir.glob("*.json"):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    topic_name = data.get('topic', 'Unknown Topic')
                    topics.append({
                        'name': topic_name,
                        'session_id': data.get('session_id'),
                        'status': data.get('status', 'completed'),
                        'created_at': data.get('created_at'),
                        'type': 'migrated'
                    })
                except Exception as e:
                    logger.warning(f"Error reading {result_file}: {str(e)}")
            
            return {
                'available_topics': topics,
                'total_count': len(topics),
                'source': 'migrated_v2'
            }
            
        except Exception as e:
            logger.error(f"Error fetching topics: {str(e)}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information by ID"""
        try:
            session_file = self.sessions_dir / f"{session_id}_session.json"
            
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Fallback: extract from analysis results
            result_file = self.analysis_results_dir / f"{session_id}.json"
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return {
                    'session_id': session_id,
                    'topic': data.get('topic'),
                    'status': data.get('status'),
                    'created_at': data.get('created_at'),
                    'completed_at': data.get('completed_at'),
                    'analysis_metadata': data.get('analysis_metadata', {}),
                    'migration_info': data.get('_migration_metadata', {})
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {str(e)}")
            raise
    
    async def get_analysis_results(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis results by session ID"""
        try:
            result_file = self.analysis_results_dir / f"{session_id}.json"
            
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching results for {session_id}: {str(e)}")
            raise
    
    async def query_vector_store(self, topic: str, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Query the migrated vector store"""
        try:
            # Load collection data
            collection_file = self.vector_store_dir / "collections" / f"{topic}_collection.json"
            
            if not collection_file.exists():
                return {
                    'query': query,
                    'results': [],
                    'total_results': 0,
                    'error': f"No vector collection found for topic: {topic}"
                }
            
            with open(collection_file, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            
            # Simple text-based search (can be enhanced with vector similarity)
            chunks = collection_data.get('chunks', [])
            results = []
            
            query_lower = query.lower()
            for chunk in chunks:
                content = chunk.get('content', '').lower()
                if query_lower in content:
                    results.append({
                        'content': chunk.get('content', ''),
                        'metadata': chunk.get('metadata', {}),
                        'relevance_score': chunk.get('relevance_score', 0.8)
                    })
                    
                    if len(results) >= max_results:
                        break
            
            return {
                'query': query,
                'results': results,
                'total_results': len(results),
                'search_time_ms': 50,  # Mock timing
                'collection_info': {
                    'topic': topic,
                    'total_chunks': len(chunks),
                    'collection_id': collection_data.get('collection_id')
                }
            }
            
        except Exception as e:
            logger.error(f"Error querying vector store for {topic}: {str(e)}")
            raise
    
    async def get_evidence_data(self, topic: str, layer: Optional[str] = None) -> Dict[str, Any]:
        """Get evidence data for a topic, optionally filtered by layer"""
        try:
            # Load collection to get evidence chunks
            collection_file = self.vector_store_dir / "collections" / f"{topic}_collection.json"
            
            if not collection_file.exists():
                return {
                    'topic': topic,
                    'evidence_layers': [],
                    'error': f"No evidence data found for topic: {topic}"
                }
            
            with open(collection_file, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            
            chunks = collection_data.get('chunks', [])
            
            # Group chunks by source or create artificial layers
            evidence_layers = {}
            
            for chunk in chunks:
                metadata = chunk.get('metadata', {})
                source_url = metadata.get('source_url', 'unknown_source')
                layer_name = metadata.get('layer', 'General Evidence')
                
                if layer_name not in evidence_layers:
                    evidence_layers[layer_name] = {
                        'layer_name': layer_name,
                        'evidence_count': 0,
                        'evidence_items': []
                    }
                
                evidence_layers[layer_name]['evidence_items'].append({
                    'url': source_url,
                    'title': metadata.get('title', 'Evidence Item'),
                    'content_preview': chunk.get('content', '')[:200] + '...',
                    'quality_score': chunk.get('relevance_score', 0.8),
                    'scraped_at': metadata.get('scraped_at'),
                    'metadata': metadata
                })
                evidence_layers[layer_name]['evidence_count'] += 1
            
            # Filter by layer if specified
            if layer:
                evidence_layers = {k: v for k, v in evidence_layers.items() if k == layer}
            
            return {
                'topic': topic,
                'evidence_layers': list(evidence_layers.values()),
                'total_layers': len(evidence_layers),
                'filter_applied': layer
            }
            
        except Exception as e:
            logger.error(f"Error fetching evidence for {topic}: {str(e)}")
            raise
    
    async def get_action_layer_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get action layer data for a session"""
        try:
            result_file = self.analysis_results_dir / f"{session_id}.json"
            
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return data.get('action_layer_data')
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching action layer data for {session_id}: {str(e)}")
            raise
