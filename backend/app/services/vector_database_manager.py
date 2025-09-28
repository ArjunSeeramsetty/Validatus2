"""
Enhanced Vector Database Manager for Pergola Analysis Chat Interface
"""
import os
import json
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings

@dataclass
class DocumentChunk:
    """Document chunk with metadata"""
    id: str
    content: str
    source: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

class PergolaVectorDatabase:
    """Vector database specifically for Pergola analysis content"""
    
    def __init__(self, base_path: str = "knowledge_db"):
        self.base_path = Path(base_path)
        self.vector_path = self.base_path / "vector" / "pergola_analysis"
        self.metadata_path = self.base_path / "metadata"
        
        # Ensure directories exist
        self.vector_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize or load FAISS index
        self.index = None
        self.document_chunks = []
        self.load_or_create_index()
    
    def load_or_create_index(self):
        """Load existing index or create new one"""
        index_file = self.vector_path / "faiss_index.bin"
        metadata_file = self.metadata_path / "pergola_metadata.json"
        
        if index_file.exists() and metadata_file.exists():
            # Load existing index
            self.index = faiss.read_index(str(index_file))
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                self.document_chunks = [
                    DocumentChunk(**chunk_data) 
                    for chunk_data in metadata['chunks']
                ]
        else:
            # Create new index (384 dimensions for all-MiniLM-L6-v2)
            self.index = faiss.IndexFlatIP(384)
            self.document_chunks = []
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector database"""
        new_chunks = []
        embeddings = []
        
        for doc in documents:
            # Split document into chunks
            chunks = self._split_document(doc)
            
            for i, chunk_content in enumerate(chunks):
                chunk = DocumentChunk(
                    id=f"{doc['id']}_{i}",
                    content=chunk_content,
                    source=doc.get('source', 'unknown'),
                    metadata=doc.get('metadata', {})
                )
                
                # Generate embedding
                embedding = self.embedding_model.encode(chunk_content)
                chunk.embedding = embedding
                
                new_chunks.append(chunk)
                embeddings.append(embedding)
        
        if embeddings:
            # Add to FAISS index
            embeddings_array = np.array(embeddings).astype('float32')
            faiss.normalize_L2(embeddings_array)
            self.index.add(embeddings_array)
            
            # Update document chunks
            self.document_chunks.extend(new_chunks)
            
            # Save updated index
            self.save_index()
    
    def similarity_search(self, query: str, k: int = 5) -> List[DocumentChunk]:
        """Search for similar documents"""
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, k)
        
        # Return relevant chunks
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.document_chunks):
                chunk = self.document_chunks[idx]
                results.append(chunk)
        
        return results
    
    def save_index(self):
        """Save FAISS index and metadata"""
        # Save FAISS index
        index_file = self.vector_path / "faiss_index.bin"
        faiss.write_index(self.index, str(index_file))
        
        # Save metadata
        metadata_file = self.metadata_path / "pergola_metadata.json"
        metadata = {
            'chunks': [
                {
                    'id': chunk.id,
                    'content': chunk.content,
                    'source': chunk.source,
                    'metadata': chunk.metadata
                }
                for chunk in self.document_chunks
            ],
            'total_chunks': len(self.document_chunks),
            'embedding_model': 'all-MiniLM-L6-v2'
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _split_document(self, document: Dict[str, Any]) -> List[str]:
        """Split document into chunks"""
        content = document.get('content', '')
        
        # Simple splitting by sentences/paragraphs
        # You can make this more sophisticated
        chunks = []
        sentences = content.split('. ')
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > 500:  # Max chunk size
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += ". " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [content]
