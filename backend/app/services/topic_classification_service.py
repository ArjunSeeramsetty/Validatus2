# backend/app/services/topic_classification_service.py

import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

from ..models.analysis_models import TopicClassification
from ..middleware.monitoring import performance_monitor

logger = logging.getLogger(__name__)

class TopicClassificationService:
    """Advanced topic classification and semantic clustering service"""
    
    def __init__(self):
        # Predefined topic categories
        self.topic_categories = {
            'technology': {
                'keywords': ['ai', 'artificial intelligence', 'machine learning', 'software', 'hardware', 'tech', 'digital', 'automation', 'blockchain', 'cloud', 'data', 'algorithm'],
                'subcategories': ['ai_ml', 'software_dev', 'cybersecurity', 'fintech', 'biotech', 'gaming', 'mobile']
            },
            'business': {
                'keywords': ['business', 'company', 'startup', 'entrepreneur', 'market', 'finance', 'investment', 'strategy', 'management', 'leadership', 'growth'],
                'subcategories': ['startups', 'finance', 'marketing', 'operations', 'strategy', 'hr', 'sales']
            },
            'science': {
                'keywords': ['research', 'study', 'experiment', 'discovery', 'scientific', 'lab', 'theory', 'hypothesis', 'analysis', 'data', 'results'],
                'subcategories': ['physics', 'chemistry', 'biology', 'medicine', 'environment', 'space', 'psychology']
            },
            'health': {
                'keywords': ['health', 'medical', 'disease', 'treatment', 'therapy', 'medicine', 'patient', 'doctor', 'hospital', 'wellness', 'fitness'],
                'subcategories': ['medicine', 'mental_health', 'nutrition', 'fitness', 'public_health', 'pharmaceuticals']
            },
            'education': {
                'keywords': ['education', 'learning', 'school', 'university', 'student', 'teacher', 'course', 'training', 'knowledge', 'skill', 'academic'],
                'subcategories': ['k12', 'higher_ed', 'online_learning', 'vocational', 'research', 'pedagogy']
            },
            'entertainment': {
                'keywords': ['movie', 'music', 'game', 'entertainment', 'show', 'film', 'artist', 'celebrity', 'sports', 'gaming', 'media'],
                'subcategories': ['movies', 'music', 'gaming', 'sports', 'television', 'books', 'art']
            },
            'lifestyle': {
                'keywords': ['lifestyle', 'food', 'travel', 'fashion', 'home', 'family', 'relationship', 'culture', 'social', 'personal'],
                'subcategories': ['food', 'travel', 'fashion', 'home_garden', 'relationships', 'culture']
            },
            'politics': {
                'keywords': ['politics', 'government', 'policy', 'election', 'democracy', 'law', 'regulation', 'public', 'social', 'economic'],
                'subcategories': ['domestic', 'international', 'policy', 'elections', 'law', 'economics']
            }
        }
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    @performance_monitor
    async def classify_content(self, 
                             content: List[Dict[str, Any]], 
                             primary_topic: str) -> Dict[str, Any]:
        """Classify content and perform semantic clustering"""
        
        logger.info(f"Classifying {len(content)} documents for topic: {primary_topic}")
        
        try:
            # Extract text content for classification
            text_contents = [doc.get('content', '') for doc in content]
            
            # Perform topic classification
            classification_results = await self._classify_documents(text_contents, primary_topic)
            
            # Perform semantic clustering
            clustering_results = await self._perform_semantic_clustering(text_contents, classification_results)
            
            # Calculate topic scores
            topic_scores = self._calculate_topic_scores(classification_results)
            
            # Generate insights
            insights = await self._generate_classification_insights(
                classification_results, clustering_results, primary_topic
            )
            
            result = {
                'topic_scores': topic_scores,
                'clusters': clustering_results,
                'classification_results': classification_results,
                'insights': insights,
                'primary_topic': primary_topic,
                'total_documents': len(content)
            }
            
            logger.info(f"Classification completed - Primary: {primary_topic}, Clusters: {len(clustering_results)}")
            return result
            
        except Exception as e:
            logger.error(f"Content classification failed: {e}")
            return {
                'topic_scores': {primary_topic: 1.0},
                'clusters': [],
                'classification_results': [],
                'insights': [],
                'primary_topic': primary_topic,
                'total_documents': len(content),
                'error': str(e)
            }
    
    async def _classify_documents(self, 
                                text_contents: List[str], 
                                primary_topic: str) -> List[Dict[str, Any]]:
        """Classify individual documents into topic categories"""
        
        classification_results = []
        
        for i, content in enumerate(text_contents):
            try:
                # Extract keywords and phrases
                keywords = self._extract_keywords(content)
                
                # Calculate category scores
                category_scores = {}
                for category, config in self.topic_categories.items():
                    score = self._calculate_category_score(keywords, config['keywords'])
                    category_scores[category] = score
                
                # Determine primary and secondary categories
                sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
                primary_category = sorted_categories[0][0]
                secondary_categories = [cat for cat, score in sorted_categories[1:3] if score > 0.3]
                
                # Calculate confidence
                max_score = sorted_categories[0][1]
                confidence = min(max_score * 2, 1.0)  # Normalize confidence
                
                # Generate topic keywords
                topic_keywords = self._extract_topic_keywords(content, primary_category)
                
                classification_result = {
                    'document_index': i,
                    'primary_category': primary_category,
                    'secondary_categories': secondary_categories,
                    'confidence_scores': category_scores,
                    'topic_keywords': topic_keywords,
                    'confidence': confidence,
                    'content_length': len(content),
                    'keyword_density': len(keywords) / max(len(content.split()), 1)
                }
                
                classification_results.append(classification_result)
                
            except Exception as e:
                logger.error(f"Document classification failed for document {i}: {e}")
                # Add default classification
                classification_results.append({
                    'document_index': i,
                    'primary_category': 'general',
                    'secondary_categories': [],
                    'confidence_scores': {'general': 0.5},
                    'topic_keywords': [],
                    'confidence': 0.5,
                    'content_length': len(content),
                    'keyword_density': 0.0,
                    'error': str(e)
                })
        
        return classification_results
    
    async def _perform_semantic_clustering(self, 
                                        text_contents: List[str],
                                        classification_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform semantic clustering on the content"""
        
        try:
            if len(text_contents) < 2:
                return []
            
            # Prepare text for clustering
            cleaned_contents = [self._clean_text_for_clustering(content) for content in text_contents]
            
            # Create TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(cleaned_contents)
            
            # Determine optimal number of clusters
            optimal_clusters = min(max(2, len(text_contents) // 3), 10)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Organize clusters
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = {
                        'cluster_id': label,
                        'documents': [],
                        'keywords': [],
                        'centroid_keywords': []
                    }
                
                clusters[label]['documents'].append({
                    'document_index': i,
                    'content_preview': text_contents[i][:200] + '...',
                    'classification': classification_results[i] if i < len(classification_results) else {}
                })
            
            # Extract cluster keywords
            for cluster_id, cluster_data in clusters.items():
                cluster_contents = [text_contents[doc['document_index']] for doc in cluster_data['documents']]
                cluster_keywords = self._extract_cluster_keywords(cluster_contents)
                cluster_data['keywords'] = cluster_keywords
                
                # Get centroid keywords from TF-IDF
                if cluster_id < len(kmeans.cluster_centers_):
                    centroid = kmeans.cluster_centers_[cluster_id]
                    feature_names = self.tfidf_vectorizer.get_feature_names_out()
                    top_indices = centroid.argsort()[-10:][::-1]
                    centroid_keywords = [feature_names[i] for i in top_indices]
                    cluster_data['centroid_keywords'] = centroid_keywords
            
            # Convert to list format
            cluster_list = list(clusters.values())
            
            # Sort by cluster size
            cluster_list.sort(key=lambda x: len(x['documents']), reverse=True)
            
            logger.info(f"Created {len(cluster_list)} semantic clusters")
            return cluster_list
            
        except Exception as e:
            logger.error(f"Semantic clustering failed: {e}")
            return []
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count keyword frequency
        keyword_counts = Counter(keywords)
        
        # Return top keywords
        return [word for word, count in keyword_counts.most_common(20)]
    
    def _calculate_category_score(self, keywords: List[str], category_keywords: List[str]) -> float:
        """Calculate how well content matches a category"""
        if not keywords:
            return 0.0
        
        # Convert to lowercase for comparison
        content_keywords = set(keyword.lower() for keyword in keywords)
        category_keywords_lower = set(keyword.lower() for keyword in category_keywords)
        
        # Calculate overlap
        overlap = len(content_keywords.intersection(category_keywords_lower))
        total_keywords = len(category_keywords_lower)
        
        if total_keywords == 0:
            return 0.0
        
        # Normalize score
        score = overlap / total_keywords
        return min(score, 1.0)
    
    def _extract_topic_keywords(self, content: str, category: str) -> List[str]:
        """Extract topic-specific keywords from content"""
        keywords = self._extract_keywords(content)
        
        # Get category-specific keywords
        if category in self.topic_categories:
            category_keywords = self.topic_categories[category]['keywords']
            category_keywords_lower = [kw.lower() for kw in category_keywords]
            
            # Filter keywords that match category
            topic_keywords = [
                kw for kw in keywords 
                if any(cat_kw in kw or kw in cat_kw for cat_kw in category_keywords_lower)
            ]
            
            return topic_keywords[:10]  # Return top 10
        
        return keywords[:10]
    
    def _clean_text_for_clustering(self, content: str) -> str:
        """Clean text for clustering analysis"""
        # Remove extra whitespace and special characters
        cleaned = re.sub(r'\s+', ' ', content)
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        return cleaned.lower()
    
    def _extract_cluster_keywords(self, cluster_contents: List[str]) -> List[str]:
        """Extract representative keywords for a cluster"""
        all_keywords = []
        for content in cluster_contents:
            keywords = self._extract_keywords(content)
            all_keywords.extend(keywords)
        
        # Count keyword frequency across cluster
        keyword_counts = Counter(all_keywords)
        
        # Return most common keywords
        return [word for word, count in keyword_counts.most_common(15)]
    
    def _calculate_topic_scores(self, classification_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate overall topic scores across all documents"""
        topic_totals = {}
        total_documents = len(classification_results)
        
        for result in classification_results:
            confidence_scores = result.get('confidence_scores', {})
            for topic, score in confidence_scores.items():
                if topic not in topic_totals:
                    topic_totals[topic] = 0
                topic_totals[topic] += score
        
        # Normalize scores
        topic_scores = {
            topic: total / total_documents 
            for topic, total in topic_totals.items()
        }
        
        return topic_scores
    
    async def _generate_classification_insights(self, 
                                             classification_results: List[Dict[str, Any]],
                                             clustering_results: List[Dict[str, Any]],
                                             primary_topic: str) -> List[str]:
        """Generate insights from classification and clustering results"""
        
        insights = []
        
        try:
            # Topic distribution insights
            category_counts = {}
            for result in classification_results:
                primary_cat = result.get('primary_category', 'unknown')
                category_counts[primary_cat] = category_counts.get(primary_cat, 0) + 1
            
            if category_counts:
                dominant_category = max(category_counts.items(), key=lambda x: x[1])
                insights.append(f"Dominant category: {dominant_category[0]} ({dominant_category[1]} documents)")
            
            # Clustering insights
            if clustering_results:
                largest_cluster = max(clustering_results, key=lambda x: len(x['documents']))
                insights.append(f"Largest content cluster contains {len(largest_cluster['documents'])} documents")
                
                if len(clustering_results) > 1:
                    insights.append(f"Content is distributed across {len(clustering_results)} distinct semantic clusters")
            
            # Quality insights
            high_confidence_count = sum(1 for result in classification_results if result.get('confidence', 0) > 0.7)
            insights.append(f"High-confidence classifications: {high_confidence_count}/{len(classification_results)}")
            
            # Topic alignment insights
            topic_aligned_count = sum(1 for result in classification_results 
                                    if result.get('primary_category', '').lower() in primary_topic.lower())
            insights.append(f"Documents aligned with primary topic: {topic_aligned_count}/{len(classification_results)}")
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            insights.append(f"Analysis completed with {len(classification_results)} documents")
        
        return insights

# Export the class
__all__ = ['TopicClassificationService']
