# backend/app/services/content_deduplication_service.py

import asyncio
import hashlib
import logging
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
import numpy as np

from google.cloud import aiplatform
# from langchain_google_vertexai import VertexAIEmbeddings

from ..models.analysis_models import DuplicationResult, DuplicateType
from ..middleware.monitoring import performance_monitor

logger = logging.getLogger(__name__)

@dataclass
class DeduplicationStats:
    """Statistics for deduplication process"""
    total_documents: int
    exact_duplicates_removed: int
    near_exact_duplicates_removed: int
    semantic_duplicates_removed: int
    partial_duplicates_removed: int
    final_document_count: int
    processing_time: float
    memory_usage: float

class ContentDeduplicationService:
    """Advanced content deduplication using multiple similarity metrics"""
    
    def __init__(self):
        # self.embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
        self.processed_hashes: Set[str] = set()
        self.semantic_embeddings_cache: Dict[str, np.ndarray] = {}
        self.content_hash_cache: Dict[str, str] = {}
        
        # Similarity thresholds
        self.thresholds = {
            'exact': 1.0,
            'near_exact': 0.95,
            'semantic': 0.85,
            'partial': 0.80
        }
        
    @performance_monitor
    async def deduplicate_content_batch(self, 
                                      documents: List[Dict[str, Any]],
                                      similarity_threshold: float = 0.85) -> Tuple[List[Dict[str, Any]], DeduplicationStats]:
        """Perform comprehensive deduplication on a batch of documents"""
        
        logger.info(f"Starting deduplication for {len(documents)} documents")
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Initialize stats
            stats = DeduplicationStats(
                total_documents=len(documents),
                exact_duplicates_removed=0,
                near_exact_duplicates_removed=0,
                semantic_duplicates_removed=0,
                partial_duplicates_removed=0,
                final_document_count=0,
                processing_time=0.0,
                memory_usage=0.0
            )
            
            # Step 1: Exact hash deduplication
            documents, exact_removed = self._remove_exact_duplicates(documents)
            stats.exact_duplicates_removed = exact_removed
            logger.info(f"After exact deduplication: {len(documents)} documents")
            
            # Step 2: Near-exact text similarity deduplication
            documents, near_exact_removed = await self._remove_near_exact_duplicates(
                documents, threshold=self.thresholds['near_exact']
            )
            stats.near_exact_duplicates_removed = near_exact_removed
            logger.info(f"After near-exact deduplication: {len(documents)} documents")
            
            # Step 3: Semantic similarity deduplication
            documents, semantic_removed = await self._remove_semantic_duplicates(
                documents, similarity_threshold
            )
            stats.semantic_duplicates_removed = semantic_removed
            logger.info(f"After semantic deduplication: {len(documents)} documents")
            
            # Step 4: Partial content deduplication
            documents, partial_removed = await self._remove_partial_duplicates(
                documents, threshold=self.thresholds['partial']
            )
            stats.partial_duplicates_removed = partial_removed
            logger.info(f"Final document count: {len(documents)} documents")
            
            # Calculate final stats
            stats.final_document_count = len(documents)
            stats.processing_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"✅ Deduplication completed in {stats.processing_time:.2f}s")
            logger.info(f"Removed: {stats.exact_duplicates_removed} exact, {stats.near_exact_duplicates_removed} near-exact, {stats.semantic_duplicates_removed} semantic, {stats.partial_duplicates_removed} partial")
            
            return documents, stats
            
        except Exception as e:
            logger.error(f"Deduplication failed: {e}")
            # Return original documents with error stats
            error_stats = DeduplicationStats(
                total_documents=len(documents),
                exact_duplicates_removed=0,
                near_exact_duplicates_removed=0,
                semantic_duplicates_removed=0,
                partial_duplicates_removed=0,
                final_document_count=len(documents),
                processing_time=0.0,
                memory_usage=0.0
            )
            return documents, error_stats

    def _remove_exact_duplicates(self, documents: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """Remove documents with identical content hashes"""
        unique_documents = []
        content_hashes = set()
        duplicates_removed = 0
        
        for doc in documents:
            content = doc.get('content', '')
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            if content_hash not in content_hashes:
                content_hashes.add(content_hash)
                doc['content_hash'] = content_hash
                doc['deduplication_info'] = {
                    'is_duplicate': False,
                    'duplicate_type': None,
                    'similarity_score': 1.0,
                    'deduplication_stage': 'exact_check'
                }
                unique_documents.append(doc)
            else:
                duplicates_removed += 1
                logger.debug(f"Removed exact duplicate: {doc.get('url', 'Unknown URL')}")
                
        return unique_documents, duplicates_removed

    async def _remove_near_exact_duplicates(self, 
                                          documents: List[Dict[str, Any]], 
                                          threshold: float = 0.95) -> Tuple[List[Dict[str, Any]], int]:
        """Remove near-exact duplicates using sequence matching"""
        
        if len(documents) <= 1:
            return documents, 0
            
        unique_documents = []
        duplicates_removed = 0
        
        for i, doc in enumerate(documents):
            is_duplicate = False
            max_similarity = 0.0
            source_doc = None
            
            # Compare with all previously accepted documents
            for existing_doc in unique_documents:
                similarity = SequenceMatcher(
                    None, 
                    doc['content'].lower(), 
                    existing_doc['content'].lower()
                ).ratio()
                
                if similarity > threshold:
                    is_duplicate = True
                    max_similarity = similarity
                    source_doc = existing_doc
                    break
            
            if not is_duplicate:
                # Mark as unique
                doc['deduplication_info'] = {
                    'is_duplicate': False,
                    'duplicate_type': None,
                    'similarity_score': 1.0,
                    'deduplication_stage': 'near_exact_check'
                }
                unique_documents.append(doc)
            else:
                duplicates_removed += 1
                doc['deduplication_info'] = {
                    'is_duplicate': True,
                    'duplicate_type': DuplicateType.NEAR_EXACT.value,
                    'similarity_score': max_similarity,
                    'source_document': source_doc.get('url', 'Unknown') if source_doc else 'Unknown',
                    'deduplication_stage': 'near_exact_check'
                }
                logger.debug(f"Removed near-exact duplicate (similarity: {max_similarity:.3f}): {doc.get('url')}")
                
        return unique_documents, duplicates_removed

    async def _remove_semantic_duplicates(self, 
                                        documents: List[Dict[str, Any]], 
                                        threshold: float = 0.85) -> Tuple[List[Dict[str, Any]], int]:
        """Remove semantically similar documents using embeddings"""
        
        if len(documents) <= 1:
            return documents, 0
            
        logger.info("Computing semantic embeddings for deduplication...")
        
        try:
            # Generate embeddings for all documents
            contents = [doc['content'] for doc in documents]
            embeddings = await self._generate_batch_embeddings(contents)
            
            # Compute pairwise similarities
            similarity_matrix = self._compute_cosine_similarity_matrix(embeddings)
            
            unique_documents = []
            duplicate_indices = set()
            duplicates_removed = 0
            
            for i, doc in enumerate(documents):
                if i in duplicate_indices:
                    continue
                
                # Find duplicates for current document
                for j in range(i + 1, len(documents)):
                    if j in duplicate_indices:
                        continue
                        
                    similarity = similarity_matrix[i][j]
                    
                    if similarity > threshold:
                        # Mark the shorter document as duplicate
                        if len(documents[i]['content']) >= len(documents[j]['content']):
                            duplicate_indices.add(j)
                            documents[j]['deduplication_info'] = {
                                'is_duplicate': True,
                                'duplicate_type': DuplicateType.SEMANTIC.value,
                                'similarity_score': similarity,
                                'source_document': documents[i].get('url', 'Unknown'),
                                'deduplication_stage': 'semantic_check'
                            }
                            duplicates_removed += 1
                        else:
                            duplicate_indices.add(i)
                            documents[i]['deduplication_info'] = {
                                'is_duplicate': True,
                                'duplicate_type': DuplicateType.SEMANTIC.value, 
                                'similarity_score': similarity,
                                'source_document': documents[j].get('url', 'Unknown'),
                                'deduplication_stage': 'semantic_check'
                            }
                            duplicates_removed += 1
                            break
                
                if i not in duplicate_indices:
                    unique_documents.append(doc)
                    
            return unique_documents, duplicates_removed
            
        except Exception as e:
            logger.error(f"Semantic deduplication failed: {e}")
            return documents, 0

    async def _remove_partial_duplicates(self, 
                                       documents: List[Dict[str, Any]], 
                                       threshold: float = 0.80) -> Tuple[List[Dict[str, Any]], int]:
        """Remove documents with significant partial overlap"""
        
        if len(documents) <= 1:
            return documents, 0
            
        unique_documents = []
        duplicates_removed = 0
        
        # Extract key sentences from each document for comparison
        document_sentences = []
        for doc in documents:
            sentences = self._extract_key_sentences(doc['content'])
            document_sentences.append(sentences)
        
        for i, doc in enumerate(documents):
            is_duplicate = False
            max_overlap = 0.0
            source_doc = None
            
            # Compare with previously accepted documents
            for j, existing_doc in enumerate(unique_documents):
                existing_sentences = document_sentences[j]
                current_sentences = document_sentences[i]
                
                overlap_score = self._calculate_sentence_overlap(
                    existing_sentences, current_sentences
                )
                
                if overlap_score > threshold:
                    is_duplicate = True
                    max_overlap = overlap_score
                    source_doc = existing_doc
                    break
            
            if not is_duplicate:
                doc['deduplication_info'] = {
                    'is_duplicate': False,
                    'duplicate_type': None,
                    'similarity_score': 1.0,
                    'deduplication_stage': 'partial_check'
                }
                unique_documents.append(doc)
            else:
                duplicates_removed += 1
                doc['deduplication_info'] = {
                    'is_duplicate': True,
                    'duplicate_type': DuplicateType.PARTIAL.value,
                    'similarity_score': max_overlap,
                    'source_document': source_doc.get('url', 'Unknown') if source_doc else 'Unknown',
                    'deduplication_stage': 'partial_check'
                }
                logger.debug(f"Removed partial duplicate (overlap: {max_overlap:.3f}): {doc.get('url')}")
                
        return unique_documents, duplicates_removed

    async def _generate_batch_embeddings(self, contents: List[str]) -> np.ndarray:
        """Generate embeddings for a batch of content"""
        try:
            embeddings_list = []
            
            # Process in batches to avoid rate limits
            batch_size = 20
            for i in range(0, len(contents), batch_size):
                batch = contents[i:i + batch_size]
                
                # Check cache first
                batch_embeddings = []
                for content in batch:
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    if content_hash in self.semantic_embeddings_cache:
                        batch_embeddings.append(self.semantic_embeddings_cache[content_hash])
                    else:
                        # Generate new embedding
                        embedding = await self.embeddings.aembed_documents([content])
                        if embedding:
                            embedding_vector = np.array(embedding[0])
                            self.semantic_embeddings_cache[content_hash] = embedding_vector
                            batch_embeddings.append(embedding_vector)
                        else:
                            # Fallback to zero vector
                            batch_embeddings.append(np.zeros(768))  # Default embedding size
                
                embeddings_list.extend(batch_embeddings)
                
            return np.array(embeddings_list)
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(contents), 768))
    
    def _compute_cosine_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Compute cosine similarity matrix for embeddings"""
        try:
            # Normalize embeddings
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            normalized_embeddings = embeddings / (norms + 1e-8)
            
            # Compute similarity matrix
            similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)
            
            return similarity_matrix
            
        except Exception as e:
            logger.error(f"Failed to compute similarity matrix: {e}")
            # Return identity matrix as fallback
            return np.eye(len(embeddings))
    
    def _extract_key_sentences(self, content: str, max_sentences: int = 10) -> List[str]:
        """Extract key sentences from content for partial matching"""
        try:
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            
            if len(sentences) <= max_sentences:
                return sentences
            
            # Score sentences by length and position
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                # Prefer longer sentences and those near the beginning
                length_score = min(len(sentence.split()) / 20, 1.0)  # Normalize by 20 words
                position_score = 1.0 - (i / len(sentences))  # Higher score for earlier sentences
                
                total_score = length_score * 0.7 + position_score * 0.3
                sentence_scores.append((total_score, sentence))
            
            # Sort by score and take top sentences
            sentence_scores.sort(key=lambda x: x[0], reverse=True)
            key_sentences = [sentence for _, sentence in sentence_scores[:max_sentences]]
            
            return key_sentences
            
        except Exception as e:
            logger.error(f"Failed to extract key sentences: {e}")
            return []
    
    def _calculate_sentence_overlap(self, 
                                  sentences1: List[str], 
                                  sentences2: List[str]) -> float:
        """Calculate overlap between two sets of sentences"""
        try:
            if not sentences1 or not sentences2:
                return 0.0
            
            # Create word sets for each sentence set
            words1 = set()
            words2 = set()
            
            for sentence in sentences1:
                words1.update(sentence.lower().split())
            
            for sentence in sentences2:
                words2.update(sentence.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception as e:
            logger.error(f"Failed to calculate sentence overlap: {e}")
            return 0.0

    async def get_deduplication_summary(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of deduplication results"""
        
        total_docs = len(documents)
        duplicate_info = [doc.get('deduplication_info', {}) for doc in documents]
        
        # Count duplicates by type
        duplicate_counts = {
            'exact': sum(1 for info in duplicate_info if info.get('duplicate_type') == DuplicateType.EXACT.value),
            'near_exact': sum(1 for info in duplicate_info if info.get('duplicate_type') == DuplicateType.NEAR_EXACT.value),
            'semantic': sum(1 for info in duplicate_info if info.get('duplicate_type') == DuplicateType.SEMANTIC.value),
            'partial': sum(1 for info in duplicate_info if info.get('duplicate_type') == DuplicateType.PARTIAL.value),
            'unique': sum(1 for info in duplicate_info if not info.get('is_duplicate', False))
        }
        
        # Calculate average similarity scores
        duplicate_scores = [info.get('similarity_score', 1.0) for info in duplicate_info if info.get('is_duplicate', False)]
        avg_similarity = np.mean(duplicate_scores) if duplicate_scores else 0.0
        
        summary = {
            'total_documents': total_docs,
            'duplicate_counts': duplicate_counts,
            'duplicate_rate': (total_docs - duplicate_counts['unique']) / total_docs if total_docs > 0 else 0.0,
            'average_similarity': avg_similarity,
            'deduplication_efficiency': duplicate_counts['unique'] / total_docs if total_docs > 0 else 0.0
        }
        
        return summary

# Export the class
__all__ = ['ContentDeduplicationService', 'DeduplicationStats']
