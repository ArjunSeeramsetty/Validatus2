"""
Scraped Content Manager for direct access to migrated research data
"""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class ScrapedContentManager:
    """Manager for scraped content with semantic search capabilities"""
    
    def __init__(self, migrated_data_path: str = "migrated_data"):
        self.migrated_data_path = Path(migrated_data_path)
        self.scraped_content_path = self.migrated_data_path / "knowledge_base" / "scraped_content"
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load and cache scraped content
        self.scraped_content = []
        self.content_embeddings = []
        self._load_scraped_content()
    
    def _load_scraped_content(self):
        """Load all scraped content files and generate embeddings"""
        try:
            if not self.scraped_content_path.exists():
                logger.warning(f"Scraped content path does not exist: {self.scraped_content_path}")
                return
            
            # Load all JSON files
            for file_path in self.scraped_content_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Extract content for embedding
                        content = data.get('content', '')
                        if content and len(content.strip()) > 50:  # Only include substantial content
                            self.scraped_content.append({
                                'id': file_path.stem,
                                'content': content,
                                'title': data.get('title', file_path.stem),
                                'source': data.get('source', 'scraped_content'),
                                'layer': data.get('layer', 'general'),
                                'segment': data.get('segment', 'general'),
                                'url': data.get('url', ''),
                                'metadata': data
                            })
                except Exception as e:
                    logger.warning(f"Failed to load scraped content file {file_path}: {e}")
            
            # Generate embeddings for all content
            if self.scraped_content:
                logger.info(f"Loading {len(self.scraped_content)} scraped content items")
                content_texts = [item['content'] for item in self.scraped_content]
                self.content_embeddings = self.embedding_model.encode(content_texts)
                logger.info(f"Generated embeddings for {len(self.content_embeddings)} content items")
            else:
                logger.warning("No scraped content loaded")
                
        except Exception as e:
            logger.error(f"Failed to load scraped content: {e}")
    
    def similarity_search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search using sentence transformers"""
        try:
            if not self.scraped_content or not self.content_embeddings:
                logger.warning("No content or embeddings available for search")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_embedding, self.content_embeddings).flatten()
            
            # Get top k results
            top_indices = np.argsort(similarities)[::-1][:k]
            
            # Format results
            results = []
            for idx in top_indices:
                content_item = self.scraped_content[idx]
                similarity = similarities[idx]
                
                results.append({
                    'content': content_item['content'],
                    'source': content_item['source'],
                    'title': content_item['title'],
                    'confidence': float(similarity),
                    'category': content_item['layer'],
                    'metadata': content_item['metadata']
                })
            
            logger.info(f"Semantic search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def search_by_keywords(self, keywords: List[str], k: int = 10) -> List[Dict[str, Any]]:
        """Search content by keywords"""
        try:
            if not self.scraped_content:
                return []
            
            results = []
            for item in self.scraped_content:
                content_lower = item['content'].lower()
                title_lower = item['title'].lower()
                
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword.lower() in content_lower or keyword.lower() in title_lower)
                
                if matches > 0:
                    results.append({
                        'content': item['content'],
                        'source': item['source'],
                        'title': item['title'],
                        'confidence': matches / len(keywords),  # Normalize by number of keywords
                        'category': item['layer'],
                        'metadata': item['metadata']
                    })
            
            # Sort by confidence and return top k
            results.sort(key=lambda x: x['confidence'], reverse=True)
            return results[:k]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    def get_content_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get content filtered by category/layer"""
        try:
            if not self.scraped_content:
                return []
            
            filtered_content = [
                {
                    'content': item['content'],
                    'source': item['source'],
                    'title': item['title'],
                    'category': item['layer'],
                    'metadata': item['metadata']
                }
                for item in self.scraped_content
                if item['layer'].lower() == category.lower()
            ]
            
            return filtered_content
            
        except Exception as e:
            logger.error(f"Failed to get content by category: {e}")
            return []
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded content"""
        try:
            if not self.scraped_content:
                return {"total_items": 0}
            
            # Count by category
            categories = {}
            for item in self.scraped_content:
                category = item['layer']
                categories[category] = categories.get(category, 0) + 1
            
            return {
                "total_items": len(self.scraped_content),
                "categories": categories,
                "embedding_available": len(self.content_embeddings) > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get content stats: {e}")
            return {"error": str(e)}

# Export for use in other modules
__all__ = ["ScrapedContentManager"]
