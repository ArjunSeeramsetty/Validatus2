"""
ChromaDB Manager for Pergola Analysis using existing migrated data
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class PergolaChromaDBManager:
    """ChromaDB manager for Pergola analysis using existing migrated data"""
    
    def __init__(self, migrated_data_path: str = "migrated_data"):
        self.migrated_data_path = Path(migrated_data_path)
        self.chromadb_path = self.migrated_data_path / "knowledge_base" / "chromadb"
        
        # Initialize ChromaDB client with existing data
        self.client = chromadb.PersistentClient(
            path=str(self.chromadb_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = None
        self.load_existing_collection()
    
    def load_existing_collection(self):
        """Load existing ChromaDB collection"""
        try:
            # Get all collections
            collections = self.client.list_collections()
            
            if collections:
                # Use the first available collection (should be the pergola data)
                self.collection = collections[0]
                logger.info(f"Loaded existing ChromaDB collection: {self.collection.name}")
            else:
                # Create a new collection if none exists
                self.collection = self.client.create_collection(
                    name="pergola_analysis",
                    metadata={"description": "Pergola market analysis data"}
                )
                logger.info("Created new ChromaDB collection: pergola_analysis")
                
        except Exception as e:
            logger.error(f"Failed to load ChromaDB collection: {e}")
            # Create a new collection as fallback
            self.collection = self.client.create_collection(
                name="pergola_analysis",
                metadata={"description": "Pergola market analysis data"}
            )
    
    def similarity_search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Perform similarity search using ChromaDB"""
        try:
            if not self.collection:
                logger.error("No ChromaDB collection available")
                return []
            
            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0] if results['metadatas'] else [],
                    results['distances'][0] if results['distances'] else []
                )):
                    # Convert distance to confidence score (ChromaDB uses cosine distance)
                    confidence = max(0, 1 - distance) if distance is not None else 0.8
                    
                    formatted_results.append({
                        'content': doc,
                        'source': metadata.get('source', 'chromadb') if metadata else 'chromadb',
                        'title': metadata.get('title', f'Result {i+1}') if metadata else f'Result {i+1}',
                        'confidence': confidence,
                        'category': metadata.get('category', 'general') if metadata else 'general',
                        'metadata': metadata or {}
                    })
            
            logger.info(f"ChromaDB search returned {len(formatted_results)} results for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"ChromaDB similarity search failed: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the ChromaDB collection"""
        try:
            if not self.collection:
                return {"error": "No collection available"}
            
            # Get collection count
            count = self.collection.count()
            
            return {
                "collection_name": self.collection.name,
                "document_count": count,
                "collection_metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to ChromaDB collection (for future use)"""
        try:
            if not self.collection:
                logger.error("No ChromaDB collection available")
                return False
            
            # Prepare data for ChromaDB
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                ids.append(doc['id'])
                texts.append(doc['content'])
                metadatas.append(doc.get('metadata', {}))
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB collection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            return False

# Export for use in other modules
__all__ = ["PergolaChromaDBManager"]
