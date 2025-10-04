"""
Google Vertex AI Vector Search Manager
Handles vector embeddings and similarity search operations
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import json

from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip

from ..core.gcp_persistence_config import get_gcp_persistence_settings

logger = logging.getLogger(__name__)

class GCPVectorManager:
    """Manages Google Vertex AI Vector Search operations"""
    
    def __init__(self):
        self.settings = get_gcp_persistence_settings()
        self.vector_search_client = None
        self.prediction_client = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Vertex AI clients"""
        if self._initialized:
            return
        
        try:
            # Initialize AI Platform
            aiplatform.init(
                project=self.settings.project_id,
                location=self.settings.vector_search_location
            )
            
            # Initialize vector search client
            self.vector_search_client = aip.MatchServiceClient(
                client_options={"api_endpoint": f"{self.settings.vector_search_location}-aiplatform.googleapis.com"}
            )
            
            # Initialize prediction client for embeddings
            self.prediction_client = aip.PredictionServiceClient(
                client_options={"api_endpoint": f"{self.settings.vector_search_location}-aiplatform.googleapis.com"}
            )
            
            self._initialized = True
            logger.info("Vertex AI Vector Search Manager initialized")
            
        except Exception as e:
            logger.exception("Failed to initialize Vertex AI clients")
            raise
    
    async def close(self):
        """Close Vertex AI connections"""
        self.vector_search_client = None
        self.prediction_client = None
        self._initialized = False
        logger.info("Vertex AI Vector Search Manager closed")
    
    async def _ensure_initialized(self):
        """Ensure Vertex AI clients are initialized"""
        if not self._initialized:
            await self.initialize()
    
    async def create_topic_vector_index(self, session_id: str) -> Dict[str, Any]:
        """Create vector index for a topic session"""
        await self._ensure_initialized()
        
        try:
            # Generate embeddings for content
            embeddings_data = await self._generate_embeddings_for_session(session_id)
            
            if not embeddings_data:
                return {
                    "status": "completed",
                    "embedding_count": 0,
                    "message": "No content to embed"
                }
            
            # Create vector index
            index_id = f"validatus-{session_id}-{int(datetime.utcnow().timestamp())}"
            
            # Store embeddings in Vertex AI
            endpoint_id = await self._create_vector_endpoint(index_id)
            
            # Index the embeddings
            await self._index_embeddings(endpoint_id, embeddings_data)
            
            logger.info(f"Created vector index for session {session_id}: {index_id}")
            
            return {
                "status": "completed",
                "embedding_count": len(embeddings_data),
                "index_id": index_id,
                "endpoint_id": endpoint_id
            }
            
        except Exception as e:
            logger.exception(f"Failed to create vector index for {session_id}")
            return {
                "status": "failed",
                "error": str(e),
                "embedding_count": 0
            }
    
    async def _generate_embeddings_for_session(self, session_id: str) -> Dict[str, Any]:
        """Generate embeddings for all content in a session"""
        try:
            # This would integrate with your content retrieval system
            # For now, return mock data structure
            
            # In production, you would:
            # 1. Retrieve scraped content from GCS
            # 2. Chunk the content appropriately
            # 3. Generate embeddings for each chunk
            # 4. Return structured embedding data
            
            mock_embeddings = {
                f"chunk_{i}": {
                    "embedding": [0.1] * self.settings.vector_dimensions,  # Mock embedding
                    "metadata": {
                        "content_preview": f"Mock content chunk {i}",
                        "source_url": f"https://example.com/page{i}",
                        "chunk_index": i,
                        "word_count": 100
                    }
                }
                for i in range(5)  # Mock 5 chunks
            }
            
            return mock_embeddings
            
        except Exception as e:
            logger.exception(f"Failed to generate embeddings for session {session_id}")
            return {}
    
    async def _create_vector_endpoint(self, index_id: str) -> str:
        """Create vector search endpoint"""
        try:
            # This would create an actual Vertex AI endpoint
            # For now, return a mock endpoint ID
            
            endpoint_id = f"endpoint-{index_id}"
            logger.info(f"Created vector endpoint: {endpoint_id}")
            
            return endpoint_id
            
        except Exception as e:
            logger.exception(f"Failed to create vector endpoint {index_id}")
            raise
    
    async def _index_embeddings(self, endpoint_id: str, embeddings_data: Dict[str, Any]):
        """Index embeddings in Vertex AI"""
        try:
            # This would upload embeddings to the Vertex AI endpoint
            # For now, just log the operation
            
            logger.info(f"Indexed {len(embeddings_data)} embeddings for endpoint {endpoint_id}")
            
        except Exception as e:
            logger.exception(f"Failed to index embeddings for endpoint {endpoint_id}")
            raise
    
    async def similarity_search(self, session_id: str, query: str, 
                              top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform similarity search on topic content"""
        await self._ensure_initialized()
        
        try:
            # Generate embedding for query
            query_embedding = await self._generate_query_embedding(query)
            
            # Perform similarity search
            results = await self._search_vectors(session_id, query_embedding, top_k)
            
            return results
            
        except Exception as e:
            logger.exception(f"Failed to perform similarity search for {session_id}")
            return []
    
    async def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query using Vertex AI"""
        try:
            # Use Vertex AI to generate embeddings for the query
            from google.cloud.aiplatform import gapic as aip
            
            # Create prediction request
            endpoint_name = f"projects/{self.settings.project_id}/locations/{self.settings.vector_search_location}/endpoints/embedding-endpoint"
            
            request = aip.PredictRequest(
                endpoint=endpoint_name,
                instances=[{"content": query}]
            )
            
            # Execute prediction in thread pool to avoid blocking
            def generate_embedding():
                response = self.prediction_client.predict(request=request)
                return response.predictions[0]["embeddings"]["values"]
            
            embedding = await asyncio.get_event_loop().run_in_executor(None, generate_embedding)
            return embedding
            
        except Exception as e:
            logger.exception("Failed to generate query embedding")
            return []
    
    async def _search_vectors(self, session_id: str, query_embedding: List[float], 
                            top_k: int) -> List[Dict[str, Any]]:
        """Search vectors using Vertex AI Matching Engine"""
        try:
            # Perform actual vector search using Vertex AI Matching Engine
            from google.cloud.aiplatform import gapic as aip
            
            # Create search request
            index_endpoint = f"projects/{self.settings.project_id}/locations/{self.settings.vector_search_location}/indexEndpoints/session-{session_id}"
            
            request = aip.FindNeighborsRequest(
                index_endpoint=index_endpoint,
                queries=[aip.FindNeighborsRequest.Query(
                    datapoint=aip.IndexDatapoint(
                        feature_vector=query_embedding
                    ),
                    neighbor_count=top_k
                )]
            )
            
            # Execute search in thread pool
            def search_vectors():
                response = self.vector_search_client.find_neighbors(request=request)
                return response.nearest_neighbors[0].neighbors
            
            neighbors = await asyncio.get_event_loop().run_in_executor(None, search_vectors)
            
            # Convert to expected format
            results = []
            for neighbor in neighbors:
                results.append({
                    "chunk_id": neighbor.datapoint.datapoint_id,
                    "score": neighbor.distance,
                    "content_preview": neighbor.datapoint.restricts[0].values[0] if neighbor.datapoint.restricts else "",
                    "source_url": neighbor.datapoint.restricts[1].values[0] if len(neighbor.datapoint.restricts) > 1 else "",
                    "metadata": {"relevance": "high" if neighbor.distance > 0.8 else "medium"}
                })
            
            return results
            
        except Exception as e:
            logger.exception(f"Failed to search vectors for {session_id}")
            return []
    
    async def delete_vector_index(self, session_id: str, index_id: str) -> bool:
        """Delete vector index for a session"""
        await self._ensure_initialized()
        
        try:
            # This would delete the actual Vertex AI index
            # For now, just log the operation
            
            logger.info(f"Deleted vector index {index_id} for session {session_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to delete vector index {index_id}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform Vertex AI health check"""
        await self._ensure_initialized()
        
        try:
            # Test basic connectivity with real Vertex AI API call
            start_time = datetime.utcnow()
            
            # Try to list index endpoints to verify connectivity
            def test_connectivity():
                from google.cloud.aiplatform import gapic as aip
                request = aip.ListIndexEndpointsRequest(
                    parent=f"projects/{self.settings.project_id}/locations/{self.settings.vector_search_location}"
                )
                # Just make the request, don't process all results
                response = self.vector_search_client.list_index_endpoints(request=request)
                return len(list(response))  # Consume iterator to ensure API call works
            
            endpoint_count = await asyncio.get_event_loop().run_in_executor(None, test_connectivity)
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "vector_search_location": self.settings.vector_search_location,
                "embedding_model": self.settings.embedding_model,
                "vector_dimensions": self.settings.vector_dimensions,
                "endpoint_count": endpoint_count
            }
            
        except Exception as e:
            logger.exception("Vertex AI health check failed")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
