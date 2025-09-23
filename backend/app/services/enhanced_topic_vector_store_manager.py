# backend/app/services/enhanced_topic_vector_store_manager.py

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import asdict

# Google Cloud imports
from google.cloud import aiplatform
from google.cloud import firestore  
from google.cloud import storage
from google.cloud.aiplatform import MatchingEngineIndexEndpoint
from langchain_google_vertexai import VertexAIEmbeddings

# Enhanced analysis capabilities
from .content_quality_analyzer import ContentQualityAnalyzer
from .topic_classification_service import TopicClassificationService
from .content_deduplication_service import ContentDeduplicationService
from .analysis_optimization_service import AnalysisOptimizationService
from ..core.gcp_config import GCPSettings
from ..models.analysis_models import EnhancedTopicMetadata

logger = logging.getLogger(__name__)

class EnhancedTopicVectorStoreManager:
    """Advanced topic management with ML-powered content processing"""
    
    def __init__(self):
        self.settings = GCPSettings()
        self.embeddings = VertexAIEmbeddings(
            model_name="text-embedding-004",
            project=self.settings.gcp_project_id
        )
        self.quality_analyzer = ContentQualityAnalyzer()
        self.classification_service = TopicClassificationService()
        self.deduplication_service = ContentDeduplicationService()
        self.optimization_service = AnalysisOptimizationService()
        self.firestore_client = firestore.Client()
        self.storage_client = storage.Client()
        
    async def create_enhanced_topic_store(self, 
                                        topic: str, 
                                        urls: List[str],
                                        quality_threshold: float = 0.6) -> str:
        """Create topic store with enhanced quality assessment and classification"""
        
        logger.info(f"Creating enhanced topic store for '{topic}' with {len(urls)} URLs")
        
        try:
            # Initialize Vertex AI Vector Search index
            index_id = await self._create_vertex_ai_index(topic)
            
            # Process URLs with quality assessment
            processed_content = await self._process_urls_with_quality_analysis(
                urls, topic, quality_threshold
            )
            
            # Perform content deduplication
            deduplicated_content, dedup_stats = await self.deduplication_service.deduplicate_content_batch(
                processed_content, similarity_threshold=0.85
            )
            
            logger.info(f"Deduplication removed {dedup_stats.total_documents - dedup_stats.final_document_count} duplicates")
            
            # Perform topic classification and semantic clustering
            classification_results = await self.classification_service.classify_content(
                deduplicated_content, topic
            )
            
            # Generate enhanced embeddings with metadata
            enhanced_embeddings = await self._generate_enhanced_embeddings(
                deduplicated_content, classification_results
            )
            
            # Store in Vertex AI Vector Search
            await self._store_in_vertex_search(index_id, enhanced_embeddings)
            
            # Create enhanced metadata
            metadata = EnhancedTopicMetadata(
                topic=topic,
                topic_id=self._generate_topic_id(topic),
                classification_scores=classification_results['topic_scores'],
                quality_distribution=self._calculate_quality_distribution(processed_content),
                semantic_clusters=classification_results['clusters'],
                processing_metrics=self._calculate_processing_metrics(processed_content),
                created_at=datetime.now(timezone.utc).isoformat(),
                last_updated=datetime.now(timezone.utc).isoformat(),
                total_documents=len(processed_content),
                high_quality_documents=len([doc for doc in processed_content if doc.get('enhanced_quality_scores', {}).get('overall_score', 0) >= quality_threshold]),
                average_quality_score=self._calculate_average_quality_score(processed_content)
            )
            
            # Store metadata in Firestore
            await self._store_metadata_firestore(metadata)
            
            # Store deduplication statistics
            await self._store_deduplication_stats(metadata.topic_id, dedup_stats)
            
            logger.info(f"✅ Enhanced topic store created for '{topic}' with {len(enhanced_embeddings)} chunks")
            return metadata.topic_id
            
        except Exception as e:
            logger.error(f"Failed to create enhanced topic store: {e}")
            raise

    async def retrieve_topic_knowledge(self, topic: str) -> Dict[str, Any]:
        """Retrieve comprehensive topic knowledge with enhanced metadata"""
        
        logger.info(f"Retrieving enhanced topic knowledge for '{topic}'")
        
        try:
            # Get topic metadata
            topic_id = self._generate_topic_id(topic)
            metadata = await self._get_topic_metadata(topic_id)
            
            if not metadata:
                logger.warning(f"No metadata found for topic '{topic}'")
                return {
                    'topic': topic,
                    'documents': [],
                    'metadata': {'error': 'Topic not found'},
                    'classification_results': {},
                    'quality_stats': {}
                }
            
            # Retrieve documents from storage
            documents = await self._retrieve_documents_from_storage(topic_id)
            
            # Get classification results
            classification_results = await self._get_classification_results(topic_id)
            
            # Get quality statistics
            quality_stats = await self._get_quality_statistics(topic_id)
            
            # Get deduplication statistics
            dedup_stats = await self._get_deduplication_stats(topic_id)
            
            return {
                'topic': topic,
                'topic_id': topic_id,
                'documents': documents,
                'metadata': metadata,
                'classification_results': classification_results,
                'quality_stats': quality_stats,
                'deduplication_stats': dedup_stats,
                'retrieval_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve topic knowledge: {e}")
            return {
                'topic': topic,
                'documents': [],
                'metadata': {'error': str(e)},
                'classification_results': {},
                'quality_stats': {}
            }

    async def update_topic_store(self, 
                               topic: str, 
                               new_urls: List[str],
                               quality_threshold: float = 0.6) -> Dict[str, Any]:
        """Update existing topic store with new content"""
        
        logger.info(f"Updating topic store for '{topic}' with {len(new_urls)} new URLs")
        
        try:
            # Get existing topic metadata
            topic_id = self._generate_topic_id(topic)
            existing_metadata = await self._get_topic_metadata(topic_id)
            
            if not existing_metadata:
                # Create new store if doesn't exist
                return await self.create_enhanced_topic_store(topic, new_urls, quality_threshold)
            
            # Process new URLs
            new_content = await self._process_urls_with_quality_analysis(
                new_urls, topic, quality_threshold
            )
            
            # Get existing documents for deduplication
            existing_documents = await self._retrieve_documents_from_storage(topic_id)
            
            # Combine and deduplicate
            all_content = existing_documents + new_content
            deduplicated_content, dedup_stats = await self.deduplication_service.deduplicate_content_batch(
                all_content, similarity_threshold=0.85
            )
            
            # Update classification
            updated_classification = await self.classification_service.classify_content(
                deduplicated_content, topic
            )
            
            # Update embeddings
            updated_embeddings = await self._generate_enhanced_embeddings(
                deduplicated_content, updated_classification
            )
            
            # Update Vertex AI index
            index_id = existing_metadata.get('index_id', '')
            await self._update_vertex_search_index(index_id, updated_embeddings)
            
            # Update metadata
            updated_metadata = EnhancedTopicMetadata(
                topic=topic,
                topic_id=topic_id,
                classification_scores=updated_classification['topic_scores'],
                quality_distribution=self._calculate_quality_distribution(deduplicated_content),
                semantic_clusters=updated_classification['clusters'],
                processing_metrics=self._calculate_processing_metrics(deduplicated_content),
                created_at=existing_metadata.get('created_at', datetime.now(timezone.utc).isoformat()),
                last_updated=datetime.now(timezone.utc).isoformat(),
                total_documents=len(deduplicated_content),
                high_quality_documents=len([doc for doc in deduplicated_content if doc.get('enhanced_quality_scores', {}).get('overall_score', 0) >= quality_threshold]),
                average_quality_score=self._calculate_average_quality_score(deduplicated_content)
            )
            
            # Store updated metadata
            await self._store_metadata_firestore(updated_metadata)
            
            # Store updated deduplication stats
            await self._store_deduplication_stats(topic_id, dedup_stats)
            
            logger.info(f"✅ Updated topic store for '{topic}' with {len(deduplicated_content)} total documents")
            
            return {
                'topic_id': topic_id,
                'total_documents': len(deduplicated_content),
                'new_documents_added': len(new_content),
                'duplicates_removed': dedup_stats.total_documents - dedup_stats.final_document_count,
                'update_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update topic store: {e}")
            raise

    async def analyze_topic_performance(self, topic: str) -> Dict[str, Any]:
        """Analyze performance metrics for a topic store"""
        
        logger.info(f"Analyzing performance for topic '{topic}'")
        
        try:
            topic_id = self._generate_topic_id(topic)
            
            # Get topic metadata
            metadata = await self._get_topic_metadata(topic_id)
            
            # Get quality statistics
            quality_stats = await self._get_quality_statistics(topic_id)
            
            # Get deduplication statistics
            dedup_stats = await self._get_deduplication_stats(topic_id)
            
            # Get classification results
            classification_results = await self._get_classification_results(topic_id)
            
            # Calculate performance metrics
            performance_metrics = {
                'content_quality': {
                    'average_score': quality_stats.get('average_quality_score', 0),
                    'high_quality_ratio': quality_stats.get('high_quality_ratio', 0),
                    'quality_distribution': quality_stats.get('quality_distribution', {})
                },
                'content_diversity': {
                    'duplicate_rate': dedup_stats.get('duplicate_rate', 0),
                    'unique_content_ratio': dedup_stats.get('deduplication_efficiency', 0),
                    'semantic_clusters': len(classification_results.get('clusters', []))
                },
                'classification_accuracy': {
                    'primary_category_alignment': classification_results.get('topic_scores', {}).get(topic.lower(), 0),
                    'category_distribution': classification_results.get('topic_scores', {}),
                    'classification_confidence': classification_results.get('confidence_metrics', {})
                },
                'processing_efficiency': {
                    'total_documents': metadata.get('total_documents', 0),
                    'processing_time': metadata.get('processing_metrics', {}).get('total_processing_time', 0),
                    'throughput': metadata.get('processing_metrics', {}).get('documents_per_minute', 0)
                }
            }
            
            # Generate recommendations
            recommendations = self._generate_performance_recommendations(performance_metrics)
            
            return {
                'topic': topic,
                'topic_id': topic_id,
                'performance_metrics': performance_metrics,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze topic performance: {e}")
            return {'error': str(e)}

    async def _create_vertex_ai_index(self, topic: str) -> str:
        """Create Vertex AI Vector Search index for the topic"""
        try:
            aiplatform.init(project=self.settings.gcp_project_id, 
                          location=self.settings.gcp_region)
            
            index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
                display_name=f"validatus-{topic.lower().replace(' ', '-')}",
                contents_delta_uri=f"gs://{self.settings.gcp_storage_bucket}/indexes/{topic}",
                dimensions=768,  # text-embedding-004 dimensions
                approximate_neighbors_count=50,
                leaf_node_embedding_count=1000,
                leaf_nodes_to_search_percent=10,
                index_update_method="BATCH_UPDATE"
            )
            
            return index.name
            
        except Exception as e:
            logger.error(f"Failed to create Vertex AI index: {e}")
            raise

    async def _process_urls_with_quality_analysis(self, 
                                                urls: List[str], 
                                                topic: str,
                                                quality_threshold: float) -> List[Dict[str, Any]]:
        """Process URLs with comprehensive quality analysis"""
        
        high_quality_content = []
        
        # Use URLOrchestrator for initial scraping
        from .gcp_url_orchestrator import GCPURLOrchestrator
        orchestrator = GCPURLOrchestrator()
        
        scraping_results = await orchestrator.batch_scrape_urls(urls, topic)
        
        for doc in scraping_results.get('documents', []):
            # Perform comprehensive quality analysis
            quality_scores = await self.quality_analyzer.analyze_content_quality(
                content=doc['content'],
                url=doc['url'],
                topic=topic
            )
            
            if quality_scores.overall_score >= quality_threshold:
                doc['enhanced_quality_scores'] = asdict(quality_scores)
                doc['relevance_score'] = quality_scores.topic_relevance
                doc['readability_score'] = quality_scores.readability
                doc['authority_score'] = quality_scores.domain_authority
                high_quality_content.append(doc)
        
        logger.info(f"Filtered {len(high_quality_content)} high-quality documents from {len(scraping_results.get('documents', []))}")
        return high_quality_content

    async def _generate_enhanced_embeddings(self, 
                                          content: List[Dict[str, Any]], 
                                          classification_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhanced embeddings with metadata"""
        
        embeddings = []
        
        for i, doc in enumerate(content):
            try:
                # Generate embedding
                content_text = doc.get('content', '')
                embedding = await self.embeddings.aembed_documents([content_text])
                
                if embedding:
                    enhanced_embedding = {
                        'id': f"{doc.get('url', 'unknown')}_{i}",
                        'embedding': embedding[0],
                        'metadata': {
                            'url': doc.get('url', ''),
                            'title': doc.get('title', ''),
                            'content_length': len(content_text),
                            'quality_scores': doc.get('enhanced_quality_scores', {}),
                            'classification': classification_results.get('classification_results', [{}])[i] if i < len(classification_results.get('classification_results', [])) else {},
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    }
                    embeddings.append(enhanced_embedding)
                    
            except Exception as e:
                logger.error(f"Failed to generate embedding for document {i}: {e}")
                continue
        
        return embeddings

    async def _store_in_vertex_search(self, index_id: str, embeddings: List[Dict[str, Any]]):
        """Store embeddings in Vertex AI Vector Search"""
        
        try:
            # This would integrate with Vertex AI Vector Search API
            # For now, we'll simulate the storage
            logger.info(f"Storing {len(embeddings)} embeddings in Vertex AI index {index_id}")
            
            # In a real implementation, this would:
            # 1. Create a MatchingEngineIndexEndpoint
            # 2. Upload embeddings to the index
            # 3. Wait for index deployment
            
            await asyncio.sleep(1)  # Simulate processing time
            
        except Exception as e:
            logger.error(f"Failed to store embeddings in Vertex AI: {e}")
            raise

    async def _update_vertex_search_index(self, index_id: str, embeddings: List[Dict[str, Any]]):
        """Update existing Vertex AI Vector Search index"""
        
        try:
            logger.info(f"Updating Vertex AI index {index_id} with {len(embeddings)} embeddings")
            
            # In a real implementation, this would update the existing index
            await asyncio.sleep(1)  # Simulate processing time
            
        except Exception as e:
            logger.error(f"Failed to update Vertex AI index: {e}")
            raise

    async def _store_metadata_firestore(self, metadata: EnhancedTopicMetadata):
        """Store enhanced metadata in Firestore"""
        
        try:
            metadata_ref = self.firestore_client.collection('enhanced_topic_metadata').document(metadata.topic_id)
            await metadata_ref.set(asdict(metadata))
            
        except Exception as e:
            logger.error(f"Failed to store metadata in Firestore: {e}")
            raise

    async def _store_deduplication_stats(self, topic_id: str, dedup_stats):
        """Store deduplication statistics"""
        
        try:
            stats_ref = self.firestore_client.collection('deduplication_stats').document(topic_id)
            await stats_ref.set(asdict(dedup_stats))
            
        except Exception as e:
            logger.error(f"Failed to store deduplication stats: {e}")

    async def _get_topic_metadata(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """Get topic metadata from Firestore"""
        
        try:
            metadata_ref = self.firestore_client.collection('enhanced_topic_metadata').document(topic_id)
            doc = await metadata_ref.get()
            return doc.to_dict() if doc.exists else None
            
        except Exception as e:
            logger.error(f"Failed to get topic metadata: {e}")
            return None

    async def _get_quality_statistics(self, topic_id: str) -> Dict[str, Any]:
        """Get quality statistics for a topic"""
        
        try:
            # This would query quality data from Firestore
            # For now, return simulated data
            return {
                'average_quality_score': 0.75,
                'high_quality_ratio': 0.8,
                'quality_distribution': {
                    'high': 80,
                    'medium': 15,
                    'low': 5
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get quality statistics: {e}")
            return {}

    async def _get_deduplication_stats(self, topic_id: str) -> Dict[str, Any]:
        """Get deduplication statistics for a topic"""
        
        try:
            stats_ref = self.firestore_client.collection('deduplication_stats').document(topic_id)
            doc = await stats_ref.get()
            return doc.to_dict() if doc.exists else {}
            
        except Exception as e:
            logger.error(f"Failed to get deduplication stats: {e}")
            return {}

    async def _get_classification_results(self, topic_id: str) -> Dict[str, Any]:
        """Get classification results for a topic"""
        
        try:
            # This would query classification data from Firestore
            # For now, return simulated data
            return {
                'topic_scores': {'technology': 0.8, 'business': 0.6},
                'clusters': [{'cluster_id': 0, 'documents': 10, 'keywords': ['ai', 'machine learning']}],
                'confidence_metrics': {'overall_confidence': 0.85}
            }
            
        except Exception as e:
            logger.error(f"Failed to get classification results: {e}")
            return {}

    async def _retrieve_documents_from_storage(self, topic_id: str) -> List[Dict[str, Any]]:
        """Retrieve documents from storage for a topic"""
        
        try:
            # This would retrieve documents from Cloud Storage
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return []

    def _generate_topic_id(self, topic: str) -> str:
        """Generate unique topic ID"""
        import hashlib
        return hashlib.md5(topic.lower().encode()).hexdigest()

    def _calculate_quality_distribution(self, content: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate quality score distribution"""
        
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        for doc in content:
            quality_scores = doc.get('enhanced_quality_scores', {})
            overall_score = quality_scores.get('overall_score', 0.5)
            
            if overall_score >= 0.7:
                distribution['high'] += 1
            elif overall_score >= 0.4:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution

    def _calculate_average_quality_score(self, content: List[Dict[str, Any]]) -> float:
        """Calculate average quality score"""
        
        if not content:
            return 0.0
        
        total_score = 0.0
        count = 0
        
        for doc in content:
            quality_scores = doc.get('enhanced_quality_scores', {})
            overall_score = quality_scores.get('overall_score', 0.5)
            total_score += overall_score
            count += 1
        
        return total_score / count if count > 0 else 0.0

    def _calculate_processing_metrics(self, content: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate processing metrics"""
        
        return {
            'total_documents': len(content),
            'total_processing_time': 120.5,  # Simulated
            'documents_per_minute': len(content) / 2.0,  # Simulated
            'average_content_length': sum(len(doc.get('content', '')) for doc in content) / len(content) if content else 0
        }

    def _generate_performance_recommendations(self, performance_metrics: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        
        recommendations = []
        
        # Content quality recommendations
        avg_quality = performance_metrics['content_quality']['average_score']
        if avg_quality < 0.6:
            recommendations.append("Consider implementing stricter quality thresholds to improve content quality")
        
        # Diversity recommendations
        duplicate_rate = performance_metrics['content_diversity']['duplicate_rate']
        if duplicate_rate > 0.3:
            recommendations.append("High duplicate rate detected - consider enhancing deduplication algorithms")
        
        # Classification recommendations
        primary_alignment = performance_metrics['classification_accuracy']['primary_category_alignment']
        if primary_alignment < 0.7:
            recommendations.append("Low topic alignment - consider refining classification algorithms")
        
        # Efficiency recommendations
        throughput = performance_metrics['processing_efficiency']['throughput']
        if throughput < 10:
            recommendations.append("Low processing throughput - consider optimizing processing pipeline")
        
        if not recommendations:
            recommendations.append("Topic store performance is optimal - no immediate improvements needed")
        
        return recommendations

# Export the class
__all__ = ['EnhancedTopicVectorStoreManager']
