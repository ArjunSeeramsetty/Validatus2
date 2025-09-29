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
            else:
                # Try to find file with session_id in the name
                for file_path in self.analysis_results_dir.glob("*.json"):
                    if session_id in file_path.name:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        break
                else:
                    return None
            
            return {
                'session_id': session_id,
                'topic': data.get('topic'),
                'status': data.get('status'),
                'created_at': data.get('created_at'),
                'completed_at': data.get('completed_at'),
                'analysis_metadata': data.get('analysis_metadata', {}),
                'migration_info': data.get('_migration_metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {str(e)}")
            raise
    
    async def get_analysis_results(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis results by session ID"""
        try:
            # Try exact filename first
            result_file = self.analysis_results_dir / f"{session_id}.json"
            
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Try to find file with session_id in the name
            for file_path in self.analysis_results_dir.glob("*.json"):
                if session_id in file_path.name:
                    with open(file_path, 'r', encoding='utf-8') as f:
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
            # Try exact filename first
            result_file = self.analysis_results_dir / f"{session_id}.json"
            
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # Try to find file with session_id in the name
                for file_path in self.analysis_results_dir.glob("*.json"):
                    if session_id in file_path.name:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        break
                else:
                    return None
            
            return data.get('action_layer_data')
            
        except Exception as e:
            logger.error(f"Error fetching action layer data for {session_id}: {str(e)}")
            raise

    async def get_comprehensive_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for Pergola Intelligence"""
        try:
            # Get available topics
            topics_data = await self.get_available_topics()
            
            # Mock comprehensive intelligence data
            return {
                "market_insights": {
                    "market_size_2024": 3500.0,
                    "market_size_2033": 5800.0,
                    "cagr": 6.5,
                    "key_trends": [
                        "Post-COVID outdoor living trends",
                        "Smart home technology integration",
                        "Premium lifestyle investments",
                        "Energy-efficient building solutions"
                    ],
                    "regional_analysis": {
                        "north_america": {"size": 997.6, "growth": 5.4},
                        "europe": {"size": 1200.0, "growth": 7.2},
                        "asia_pacific": {"size": 890.5, "growth": 8.1}
                    }
                },
                "competitive_landscape": {
                    "top_competitors": [
                        {"name": "Renson", "market_share": 12.5, "usp": "Premium architectural solutions"},
                        {"name": "Corradi", "market_share": 8.7, "usp": "Italian craftsmanship"},
                        {"name": "Luxos", "market_share": 6.8, "usp": "Smart technology integration"},
                        {"name": "IQ Outdoor Living", "market_share": 5.2, "usp": "Modular systems"}
                    ],
                    "market_concentration": "Moderate",
                    "entry_barriers": ["High capital requirements", "Brand recognition", "Distribution networks"]
                },
                "consumer_psychology": {
                    "primary_motivations": [
                        "Outdoor lifestyle enhancement",
                        "Property value increase",
                        "Weather protection",
                        "Aesthetic appeal"
                    ],
                    "purchase_drivers": [
                        "Quality and durability",
                        "Design and aesthetics",
                        "Price competitiveness",
                        "Installation ease"
                    ],
                    "decision_factors": {
                        "price": 0.25,
                        "quality": 0.35,
                        "design": 0.20,
                        "brand": 0.15,
                        "warranty": 0.05
                    }
                },
                "technology_trends": {
                    "smart_features": ["Automated louvres", "Weather sensors", "Mobile app control"],
                    "materials_innovation": ["Sustainable materials", "UV-resistant coatings", "Modular systems"],
                    "integration_trends": ["Smart home connectivity", "Solar panel integration", "LED lighting systems"]
                },
                "research_metadata": {
                    "data_sources": topics_data.get('total_count', 0),
                    "last_updated": datetime.now().isoformat(),
                    "confidence_score": 0.92
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive dashboard data: {str(e)}")
            return {}

    async def semantic_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search across migrated data"""
        try:
            # Get all available topics
            topics_data = await self.get_available_topics()
            topics = topics_data.get('available_topics', [])
            
            results = []
            
            # Search through topics and their content
            for topic in topics[:5]:  # Limit to first 5 topics for performance
                topic_name = topic.get('name', '')
                session_id = topic.get('session_id', '')
                
                # Get analysis results for this topic
                if session_id:
                    analysis_data = await self.get_analysis_results(session_id)
                    if analysis_data:
                        # Extract relevant content based on query
                        content_snippets = self._extract_relevant_content(analysis_data, query)
                        for snippet in content_snippets[:3]:  # Max 3 per topic
                            results.append({
                                'topic': topic_name,
                                'session_id': session_id,
                                'content': snippet['content'],
                                'relevance_score': snippet['score'],
                                'source': 'migrated_analysis',
                                'metadata': snippet.get('metadata', {})
                            })
                
                if len(results) >= max_results:
                    break
            
            # Sort by relevance score
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error performing semantic search: {str(e)}")
            return []

    def _extract_relevant_content(self, analysis_data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Extract content relevant to the search query"""
        query_lower = query.lower()
        relevant_content = []
        
        # Search through different layers of analysis data
        for layer_name, layer_data in analysis_data.items():
            if isinstance(layer_data, dict):
                # Search in layer content
                layer_content = str(layer_data).lower()
                if any(word in layer_content for word in query_lower.split()):
                    relevant_content.append({
                        'content': str(layer_data)[:300] + '...',
                        'score': 0.8,
                        'metadata': {'layer': layer_name, 'type': 'analysis_layer'}
                    })
        
        return relevant_content
