# backend/app/services/gcp_topic_vector_store_manager.py

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

# Google Cloud imports
from google.cloud import storage
from google.cloud import sql
from google.cloud import aiplatform
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint
from google.cloud import firestore
from google.cloud import secretmanager

# Vector embeddings
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Internal imports
from ..core.gcp_config import GCPSettings
from ..middleware.monitoring import performance_monitor

logger = logging.getLogger(__name__)

@dataclass
class GCPTopicMetadata:
    """GCP-enhanced metadata for topic-based vector stores"""
    topic: str
    topic_id: str
    created_at: str
    last_updated: str
    url_count: int
    document_count: int
    chunk_count: int
    gcs_bucket_path: str
    vertex_index_id: str
    vertex_endpoint_id: str
    search_queries: List[str]
    content_quality_avg: float
    firestore_collection: str
    cloud_sql_table: str

class EvidenceChunk:
    """Evidence chunk for RAG service compatibility"""
    def __init__(self, content: str, layer: str, factor: str, segment: str, 
                 url: str, title: str, quality_score: float, chunk_index: int, 
                 similarity_score: float = 0.0):
        self.content = content
        self.layer = layer
        self.factor = factor
        self.segment = segment
        self.url = url
        self.title = title
        self.quality_score = quality_score
        self.chunk_index = chunk_index
        self.similarity_score = similarity_score

class GCPTopicVectorStoreManager:
    """GCP-integrated topic vector store manager with enterprise features"""
    
    def __init__(self, project_id: str = None, region: str = "us-central1"):
        self.settings = GCPSettings()
        self.project_id = project_id or self.settings.project_id
        self.region = region
        
        # Initialize GCP clients
        self._init_gcp_clients()
        
        # Vector store configuration
        self.embedding_model = "text-embedding-004"  # Latest Vertex AI model
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
        # Storage paths
        self.bucket_name = f"{self.project_id}-validatus-topics"
        self.firestore_collection = "topic_metadata"
        
        # Active stores cache
        self._topic_stores: Dict[str, Any] = {}
        self._topic_metadata: Dict[str, GCPTopicMetadata] = {}
        
        # Initialize infrastructure
        self._ensure_gcp_infrastructure()
        self._load_existing_topics()
    
    def _init_gcp_clients(self):
        """Initialize Google Cloud service clients"""
        # Storage client
        self.storage_client = storage.Client(project=self.project_id)
        
        # Firestore client
        self.firestore_client = firestore.Client(project=self.project_id)
        
        # Vertex AI client
        aiplatform.init(project=self.project_id, location=self.region)
        
        # Vertex AI embeddings
        self.embeddings = VertexAIEmbeddings(
            model_name=self.embedding_model,
            project=self.project_id,
            location=self.region
        )
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
        )
        
        logger.info("✅ GCP clients initialized successfully")
    
    def _ensure_gcp_infrastructure(self):
        """Ensure required GCP infrastructure exists"""
        try:
            # Create GCS bucket if it doesn't exist
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket = self.storage_client.create_bucket(
                    self.bucket_name,
                    location=self.region
                )
                logger.info(f"Created GCS bucket: {self.bucket_name}")
            
            # Ensure Firestore collections exist
            # Firestore collections are created automatically on first write
            
            logger.info("✅ GCP infrastructure verified")
            
        except Exception as e:
            logger.error(f"Failed to ensure GCP infrastructure: {e}")
            raise
    
    @performance_monitor
    async def create_topic_store(self, topic: str, urls: List[str], 
                               search_queries: List[str] = None) -> str:
        """Create GCP-hosted topic vector store"""
        topic_id = self._generate_topic_id(topic)
        
        logger.info(f"Creating GCP topic store for '{topic}' with {len(urls)} URLs")
        
        try:
            # Process URLs using GCP-enhanced orchestrator
            from .gcp_url_orchestrator import GCPURLOrchestrator
            url_orchestrator = GCPURLOrchestrator(project_id=self.project_id)
            
            # Batch process URLs
            scraping_results = await url_orchestrator.batch_scrape_urls(urls, topic)
            
            if not scraping_results.get("success", False):
                raise ValueError(f"Failed to scrape URLs for topic: {topic}")
            
            documents = scraping_results.get("documents", [])
            if not documents:
                raise ValueError(f"No valid content extracted for topic: {topic}")
            
            # Create embeddings and store in Vertex AI Vector Search
            vector_docs = await self._create_vector_documents(documents, topic, topic_id)
            
            # Create Vertex AI Vector Search index
            vertex_index_id, vertex_endpoint_id = await self._create_vertex_ai_index(
                topic_id, vector_docs
            )
            
            # Store processed documents in GCS
            gcs_path = await self._store_documents_gcs(topic_id, documents)
            
            # Create metadata
            metadata = GCPTopicMetadata(
                topic=topic,
                topic_id=topic_id,
                created_at=datetime.now(timezone.utc).isoformat(),
                last_updated=datetime.now(timezone.utc).isoformat(),
                url_count=len(urls),
                document_count=len(documents),
                chunk_count=len(vector_docs),
                gcs_bucket_path=gcs_path,
                vertex_index_id=vertex_index_id,
                vertex_endpoint_id=vertex_endpoint_id,
                search_queries=search_queries or [],
                content_quality_avg=self._calculate_avg_quality(vector_docs),
                firestore_collection=self.firestore_collection,
                cloud_sql_table=f"topic_{topic_id}_chunks"
            )
            
            # Store metadata in Firestore
            await self._store_metadata_firestore(metadata)
            
            # Store chunk details in Cloud SQL
            await self._store_chunks_cloud_sql(topic_id, vector_docs)
            
            # Cache metadata
            self._topic_metadata[topic_id] = metadata
            
            logger.info(f"✅ Created GCP topic store '{topic}' with {len(vector_docs)} chunks")
            return topic_id
            
        except Exception as e:
            logger.error(f"Failed to create GCP topic store for '{topic}': {e}")
            raise
    
    async def _create_vector_documents(self, documents: List[Dict], 
                                     topic: str, topic_id: str) -> List[Document]:
        """Create vector documents with embeddings"""
        vector_docs = []
        
        for doc_data in documents:
            # Chunk the content
            chunks = self.text_splitter.split_text(doc_data.get("content", ""))
            
            for i, chunk_content in enumerate(chunks):
                metadata = {
                    "topic": topic,
                    "topic_id": topic_id,
                    "source_url": doc_data.get("url", ""),
                    "title": doc_data.get("title", ""),
                    "chunk_index": i,
                    "quality_score": doc_data.get("quality_score", 0.0),
                    "layer": doc_data.get("layer", ""),
                    "factor": doc_data.get("factor", ""),
                    "segment": doc_data.get("segment", ""),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                vector_docs.append(Document(
                    page_content=chunk_content,
                    metadata=metadata
                ))
        
        return vector_docs
    
    async def _create_vertex_ai_index(self, topic_id: str, 
                                    vector_docs: List[Document]) -> Tuple[str, str]:
        """Create Vertex AI Vector Search index"""
        try:
            # Generate embeddings
            texts = [doc.page_content for doc in vector_docs]
            embeddings = await self.embeddings.aembed_documents(texts)
            
            # Create index
            index_display_name = f"validatus-topic-{topic_id}"
            
            # Vector index configuration
            index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
                display_name=index_display_name,
                contents_delta_uri=f"gs://{self.bucket_name}/indexes/{topic_id}",
                dimensions=len(embeddings[0]),
                approximate_neighbors_count=10,
                leaf_node_embedding_count=1000,
                leaf_nodes_to_search_percent=10,
                description=f"Vector index for topic: {topic_id}",
                labels={"topic_id": topic_id, "created_by": "validatus"}
            )
            
            # Create endpoint
            endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
                display_name=f"validatus-endpoint-{topic_id}",
                description=f"Vector search endpoint for topic: {topic_id}",
                labels={"topic_id": topic_id}
            )
            
            # Deploy index to endpoint
            endpoint.deploy_index(
                index=index,
                deployed_index_id=f"deployed_{topic_id}",
                display_name=f"deployed-{topic_id}"
            )
            
            logger.info(f"✅ Created Vertex AI index and endpoint for topic {topic_id}")
            return index.resource_name, endpoint.resource_name
            
        except Exception as e:
            logger.error(f"Failed to create Vertex AI index: {e}")
            raise
    
    async def _store_documents_gcs(self, topic_id: str, documents: List[Dict]) -> str:
        """Store processed documents in Google Cloud Storage"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob_path = f"topics/{topic_id}/processed_documents.json"
            blob = bucket.blob(blob_path)
            
            # Upload documents as JSON
            blob.upload_from_string(
                json.dumps(documents, indent=2, default=str),
                content_type='application/json'
            )
            
            gcs_path = f"gs://{self.bucket_name}/{blob_path}"
            logger.info(f"✅ Stored documents in GCS: {gcs_path}")
            return gcs_path
            
        except Exception as e:
            logger.error(f"Failed to store documents in GCS: {e}")
            raise
    
    async def _store_metadata_firestore(self, metadata: GCPTopicMetadata):
        """Store topic metadata in Firestore"""
        try:
            doc_ref = self.firestore_client.collection(self.firestore_collection).document(metadata.topic_id)
            doc_ref.set(asdict(metadata))
            
            logger.info(f"✅ Stored metadata in Firestore for topic {metadata.topic_id}")
            
        except Exception as e:
            logger.error(f"Failed to store metadata in Firestore: {e}")
            raise
    
    async def _store_chunks_cloud_sql(self, topic_id: str, vector_docs: List[Document]):
        """Store chunk details in Cloud SQL"""
        try:
            # This would connect to Cloud SQL and store chunk metadata
            # Implementation depends on your Cloud SQL setup
            # For now, we'll simulate the structure
            
            chunks_data = []
            for i, doc in enumerate(vector_docs):
                chunk_data = {
                    "chunk_id": f"{topic_id}_{i}",
                    "topic_id": topic_id,
                    "content": doc.page_content,
                    "metadata": json.dumps(doc.metadata),
                    "created_at": datetime.now(timezone.utc)
                }
                chunks_data.append(chunk_data)
            
            # Store in Cloud SQL table (implementation needed)
            logger.info(f"✅ Prepared {len(chunks_data)} chunks for Cloud SQL storage")
            
        except Exception as e:
            logger.error(f"Failed to store chunks in Cloud SQL: {e}")
            raise
    
    def _load_existing_topics(self):
        """Load existing topic metadata from Firestore"""
        try:
            docs = self.firestore_client.collection(self.firestore_collection).stream()
            
            for doc in docs:
                data = doc.to_dict()
                metadata = GCPTopicMetadata(**data)
                self._topic_metadata[metadata.topic_id] = metadata
                logger.info(f"Loaded GCP topic metadata: {metadata.topic}")
                
        except Exception as e:
            logger.error(f"Failed to load existing topics: {e}")
    
    @performance_monitor
    async def retrieve_by_topic_layer(self, topic: str, layer: str, 
                                    k: int = 10) -> List[EvidenceChunk]:
        """Retrieve evidence using Vertex AI Vector Search"""
        topic_id = self._generate_topic_id(topic)
        
        if topic_id not in self._topic_metadata:
            raise ValueError(f"Topic '{topic}' does not exist")
        
        try:
            metadata = self._topic_metadata[topic_id]
            
            # Create search query embedding
            search_query = f"layer: {layer} analysis evidence insights"
            query_embedding = await self.embeddings.aembed_query(search_query)
            
            # Get Vertex AI endpoint
            endpoint = aiplatform.MatchingEngineIndexEndpoint(
                index_endpoint_name=metadata.vertex_endpoint_id
            )
            
            # Perform vector search
            search_results = endpoint.find_neighbors(
                deployed_index_id=f"deployed_{topic_id}",
                queries=[query_embedding],
                num_neighbors=k * 2  # Get more for filtering
            )
            
            # Convert results to EvidenceChunk objects
            evidence_chunks = []
            for neighbor in search_results[0]:
                # Retrieve chunk data from Cloud SQL using neighbor.id
                chunk_data = await self._get_chunk_from_cloud_sql(neighbor.id)
                
                if chunk_data and self._matches_layer(chunk_data, layer):
                    chunk = EvidenceChunk(
                        content=chunk_data["content"],
                        layer=chunk_data["layer"],
                        factor=chunk_data["factor"],
                        segment=chunk_data["segment"],
                        url=chunk_data["url"],
                        title=chunk_data["title"],
                        quality_score=chunk_data["quality_score"],
                        chunk_index=chunk_data["chunk_index"],
                        similarity_score=neighbor.distance
                    )
                    evidence_chunks.append(chunk)
                    
                    if len(evidence_chunks) >= k:
                        break
            
            logger.info(f"Retrieved {len(evidence_chunks)} evidence chunks for topic '{topic}', layer '{layer}'")
            return evidence_chunks
            
        except Exception as e:
            logger.error(f"Failed to retrieve evidence for topic '{topic}', layer '{layer}': {e}")
            return []
    
    async def get_available_topics(self) -> List[Dict[str, Any]]:
        """Get list of all available topics from Firestore"""
        try:
            docs = self.firestore_client.collection(self.firestore_collection).stream()
            
            topics = []
            for doc in docs:
                metadata = doc.to_dict()
                topics.append({
                    "topic": metadata["topic"],
                    "topic_id": metadata["topic_id"],
                    "created_at": metadata["created_at"],
                    "last_updated": metadata["last_updated"],
                    "url_count": metadata["url_count"],
                    "document_count": metadata["document_count"],
                    "chunk_count": metadata["chunk_count"],
                    "content_quality_avg": metadata["content_quality_avg"]
                })
            
            return sorted(topics, key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get available topics: {e}")
            return []
    
    # Helper methods
    def _generate_topic_id(self, topic: str) -> str:
        """Generate consistent topic ID"""
        return hashlib.md5(topic.lower().encode()).hexdigest()[:12]
    
    def _calculate_avg_quality(self, vector_docs: List[Document]) -> float:
        """Calculate average content quality"""
        if not vector_docs:
            return 0.0
        
        total_quality = sum(doc.metadata.get("quality_score", 0.0) for doc in vector_docs)
        return total_quality / len(vector_docs)
    
    def _matches_layer(self, chunk_data: Dict, target_layer: str) -> bool:
        """Check if chunk matches target layer"""
        chunk_layer = chunk_data.get("layer", "").lower()
        return chunk_layer == target_layer.lower() if chunk_layer else True
    
    async def _get_chunk_from_cloud_sql(self, chunk_id: str) -> Dict[str, Any]:
        """Retrieve chunk data from Cloud SQL"""
        # Implementation needed for Cloud SQL connection
        # This is a placeholder
        return {}

# Export for use in other modules
__all__ = ['GCPTopicVectorStoreManager', 'GCPTopicMetadata', 'EvidenceChunk']
