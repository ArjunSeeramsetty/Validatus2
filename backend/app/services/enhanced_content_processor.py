# backend/app/services/enhanced_content_processor.py - EXTENDS EXISTING ContentQualityAnalyzer
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import math
import numpy as np

from .content_quality_analyzer import ContentQualityAnalyzer
from .enhanced_data_pipeline.bayesian_data_blender import BayesianDataBlender, DataSource
from ..core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

class EnhancedContentProcessor(ContentQualityAnalyzer):
    """
    Enhanced Content Processor extending existing ContentQualityAnalyzer
    Adds Bayesian blending and advanced quality metrics
    """
    
    def __init__(self):
        super().__init__()  # Initialize parent ContentQualityAnalyzer
        
        # Initialize enhanced components only if Phase C enabled
        if FeatureFlags.BAYESIAN_PIPELINE_ENABLED:
            self.bayesian_blender = BayesianDataBlender()
        else:
            self.bayesian_blender = None
        
        # Enhanced quality metrics
        self.quality_dimensions = {
            'content_depth': 0.2,
            'source_diversity': 0.15,
            'temporal_relevance': 0.15,
            'statistical_validity': 0.15,
            'expert_consensus': 0.1,
            'data_completeness': 0.1,
            'citation_quality': 0.1,
            'methodology_rigor': 0.05
        }
        
        logger.info("✅ Enhanced Content Processor initialized")
    
    async def analyze_enhanced_content_quality(self, 
                                             content_items: List[Dict[str, Any]],
                                             analysis_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhanced content quality analysis with Bayesian integration
        Extends parent class functionality
        """
        try:
            # First run existing content quality analysis
            base_analysis = await super().analyze_content_quality(content_items)
            
            if not FeatureFlags.BAYESIAN_PIPELINE_ENABLED or not self.bayesian_blender:
                logger.info("Bayesian enhancement disabled - returning base analysis")
                return self._enhance_base_analysis(base_analysis, content_items)
            
            # Enhanced analysis with Bayesian blending
            enhanced_metrics = await self._perform_enhanced_analysis(
                content_items, analysis_context or {}
            )
            
            # Blend base and enhanced results
            final_analysis = await self._blend_analysis_results(
                base_analysis, enhanced_metrics, content_items
            )
            
            logger.info(f"✅ Enhanced content analysis completed for {len(content_items)} items")
            return final_analysis
            
        except Exception as e:
            logger.error(f"Enhanced content analysis failed: {e}")
            # Fallback to base analysis
            return await super().analyze_content_quality(content_items)
    
    async def _perform_enhanced_analysis(self,
                                       content_items: List[Dict[str, Any]], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform enhanced quality analysis with multiple dimensions"""
        
        enhanced_metrics = {
            'bayesian_quality_scores': {},
            'source_reliability_analysis': {},
            'temporal_decay_analysis': {},
            'statistical_validity_scores': {},
            'expert_consensus_metrics': {},
            'enhanced_metadata': {}
        }
        
        # Parallel analysis of different quality dimensions
        analysis_tasks = [
            self._analyze_bayesian_quality(content_items, context),
            self._analyze_source_reliability(content_items, context),
            self._analyze_temporal_relevance(content_items, context),
            self._analyze_statistical_validity(content_items, context),
            self._analyze_expert_consensus(content_items, context)
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Enhanced analysis task {i} failed: {result}")
                continue
            
            if i == 0:  # Bayesian quality
                enhanced_metrics['bayesian_quality_scores'] = result
            elif i == 1:  # Source reliability
                enhanced_metrics['source_reliability_analysis'] = result
            elif i == 2:  # Temporal relevance
                enhanced_metrics['temporal_decay_analysis'] = result
            elif i == 3:  # Statistical validity
                enhanced_metrics['statistical_validity_scores'] = result
            elif i == 4:  # Expert consensus
                enhanced_metrics['expert_consensus_metrics'] = result
        
        return enhanced_metrics
    
    async def _analyze_bayesian_quality(self,
                                      content_items: List[Dict[str, Any]],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content quality using Bayesian methods"""
        try:
            # Convert content items to data sources
            data_sources = []
            
            for i, item in enumerate(content_items):
                # Extract quality indicators
                quality_score = item.get('quality_score', 0.5)
                source_type = item.get('source_type', 'secondary')
                publication_date = item.get('date') or item.get('timestamp')
                
                # Calculate recency weight
                recency_weight = self._calculate_recency_weight(publication_date)
                
                # Create data source
                data_source = DataSource(
                    source_id=f"content_{i}",
                    source_type=source_type,
                    data_points=[{
                        'quality_score': quality_score,
                        'content_length': len(item.get('content', '')),
                        'citation_count': item.get('citations', 0),
                        'author_credibility': item.get('author_credibility', 0.5)
                    }],
                    reliability_score=quality_score,
                    recency_weight=recency_weight,
                    confidence_interval=(max(0.0, quality_score - 0.2), min(1.0, quality_score + 0.2))
                )
                
                data_sources.append(data_source)
            
            # Perform Bayesian blending
            blend_result = await self.bayesian_blender.blend_data_sources(
                data_sources, 'quality_score', 0.6
            )
            
            return {
                'blended_quality_score': blend_result.blended_value,
                'quality_confidence': blend_result.confidence_score,
                'source_weights': blend_result.blend_weights,
                'uncertainty_metrics': blend_result.uncertainty_metrics
            }
            
        except Exception as e:
            logger.error(f"Bayesian quality analysis failed: {e}")
            return {'blended_quality_score': 0.5, 'quality_confidence': 0.3}
    
    async def _analyze_source_reliability(self,
                                        content_items: List[Dict[str, Any]], 
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze reliability of content sources"""
        try:
            source_metrics = {}
            source_types = {}
            
            for item in content_items:
                source = item.get('source', 'unknown')
                source_type = item.get('source_type', 'secondary')
                
                # Initialize if not seen
                if source not in source_metrics:
                    source_metrics[source] = {
                        'content_count': 0,
                        'avg_quality': 0.0,
                        'citation_count': 0,
                        'credibility_scores': []
                    }
                    source_types[source] = source_type
                
                # Update metrics
                source_metrics[source]['content_count'] += 1
                source_metrics[source]['avg_quality'] += item.get('quality_score', 0.5)
                source_metrics[source]['citation_count'] += item.get('citations', 0)
                source_metrics[source]['credibility_scores'].append(
                    item.get('author_credibility', 0.5)
                )
            
            # Calculate final reliability scores
            reliability_scores = {}
            for source, metrics in source_metrics.items():
                count = metrics['content_count']
                avg_quality = metrics['avg_quality'] / count if count > 0 else 0.5
                avg_credibility = sum(metrics['credibility_scores']) / len(metrics['credibility_scores']) if metrics['credibility_scores'] else 0.5
                citation_density = metrics['citation_count'] / count if count > 0 else 0.0
                
                # Composite reliability score
                reliability_score = (
                    avg_quality * 0.4 +
                    avg_credibility * 0.3 +
                    min(1.0, citation_density / 10.0) * 0.2 +
                    min(1.0, count / 5.0) * 0.1  # Volume bonus
                )
                
                reliability_scores[source] = {
                    'reliability_score': reliability_score,
                    'source_type': source_types[source],
                    'content_count': count,
                    'avg_quality': avg_quality,
                    'avg_credibility': avg_credibility,
                    'citation_density': citation_density
                }
            
            return {
                'source_reliability_scores': reliability_scores,
                'most_reliable_source': max(reliability_scores.keys(), 
                                          key=lambda k: reliability_scores[k]['reliability_score']) if reliability_scores else None,
                'avg_source_reliability': sum(s['reliability_score'] for s in reliability_scores.values()) / len(reliability_scores) if reliability_scores else 0.5
            }
            
        except Exception as e:
            logger.error(f"Source reliability analysis failed: {e}")
            return {'avg_source_reliability': 0.5}
    
    async def _analyze_temporal_relevance(self,
                                        content_items: List[Dict[str, Any]], 
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal relevance with decay modeling"""
        try:
            current_time = datetime.now(timezone.utc)
            temporal_scores = []
            
            for item in content_items:
                publication_date = item.get('date') or item.get('timestamp')
                if not publication_date:
                    temporal_scores.append(0.5)  # Default for unknown dates
                    continue
                
                # Parse date
                if isinstance(publication_date, str):
                    try:
                        pub_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
                    except ValueError:
                        temporal_scores.append(0.5)
                        continue
                elif isinstance(publication_date, datetime):
                    pub_date = publication_date
                else:
                    temporal_scores.append(0.5)
                    continue
                
                # Calculate days since publication
                days_old = (current_time - pub_date).days
                
                # Temporal decay function (exponential with different rates by content type)
                content_type = item.get('content_type', 'general')
                decay_rates = {
                    'news': 0.1,      # Fast decay
                    'research': 0.02, # Slow decay
                    'data': 0.05,     # Medium decay
                    'opinion': 0.15,  # Very fast decay
                    'general': 0.07   # Default decay
                }
                
                decay_rate = decay_rates.get(content_type, 0.07)
                temporal_score = math.exp(-decay_rate * days_old / 30.0)  # Monthly decay
                temporal_scores.append(temporal_score)
            
            return {
                'temporal_scores': temporal_scores,
                'avg_temporal_relevance': sum(temporal_scores) / len(temporal_scores) if temporal_scores else 0.5,
                'freshness_distribution': {
                    'very_fresh': len([s for s in temporal_scores if s > 0.8]),
                    'fresh': len([s for s in temporal_scores if 0.6 < s <= 0.8]),
                    'moderate': len([s for s in temporal_scores if 0.4 < s <= 0.6]),
                    'old': len([s for s in temporal_scores if s <= 0.4])
                }
            }
            
        except Exception as e:
            logger.error(f"Temporal relevance analysis failed: {e}")
            return {'avg_temporal_relevance': 0.5}
    
    async def _analyze_statistical_validity(self,
                                          content_items: List[Dict[str, Any]], 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze statistical validity of content"""
        try:
            validity_scores = []
            
            for item in content_items:
                validity_indicators = {
                    'sample_size': item.get('sample_size', 0),
                    'methodology': item.get('methodology', ''),
                    'confidence_interval': item.get('confidence_interval'),
                    'p_value': item.get('p_value'),
                    'statistical_test': item.get('statistical_test', ''),
                    'peer_reviewed': item.get('peer_reviewed', False)
                }
                
                validity_score = 0.0
                
                # Sample size score
                sample_size = validity_indicators['sample_size']
                if sample_size > 1000:
                    validity_score += 0.3
                elif sample_size > 100:
                    validity_score += 0.2
                elif sample_size > 30:
                    validity_score += 0.1
                
                # Methodology score
                methodology = validity_indicators['methodology'].lower()
                if any(term in methodology for term in ['randomized', 'controlled', 'experimental']):
                    validity_score += 0.2
                elif any(term in methodology for term in ['survey', 'observational', 'correlation']):
                    validity_score += 0.1
                
                # Statistical rigor score
                if validity_indicators['confidence_interval']:
                    validity_score += 0.1
                if validity_indicators['p_value']:
                    validity_score += 0.1
                if validity_indicators['statistical_test']:
                    validity_score += 0.1
                
                # Peer review bonus
                if validity_indicators['peer_reviewed']:
                    validity_score += 0.2
                
                validity_scores.append(min(1.0, validity_score))
            
            return {
                'validity_scores': validity_scores,
                'avg_statistical_validity': sum(validity_scores) / len(validity_scores) if validity_scores else 0.3,
                'high_validity_count': len([s for s in validity_scores if s > 0.7]),
                'low_validity_count': len([s for s in validity_scores if s < 0.3])
            }
            
        except Exception as e:
            logger.error(f"Statistical validity analysis failed: {e}")
            return {'avg_statistical_validity': 0.3}
    
    async def _analyze_expert_consensus(self,
                                      content_items: List[Dict[str, Any]], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze expert consensus across content"""
        try:
            expert_opinions = {}
            topics = {}
            
            for item in content_items:
                # Extract expert information
                author = item.get('author', 'unknown')
                expert_level = item.get('expert_level', 'general')
                topic = item.get('topic', 'general')
                opinion_score = item.get('opinion_score') or item.get('sentiment_score', 0.5)
                
                # Track by topic
                if topic not in topics:
                    topics[topic] = {'opinions': [], 'experts': []}
                
                topics[topic]['opinions'].append(opinion_score)
                topics[topic]['experts'].append(expert_level)
                
                # Track by expert
                if author not in expert_opinions:
                    expert_opinions[author] = {
                        'opinions': [],
                        'expert_level': expert_level,
                        'consistency_score': 0.0
                    }
                
                expert_opinions[author]['opinions'].append(opinion_score)
            
            # Calculate consensus metrics
            consensus_results = {}
            for topic, data in topics.items():
                opinions = data['opinions']
                if len(opinions) < 2:
                    consensus_score = 0.5
                else:
                    # Calculate agreement (inverse of variance)
                    opinion_variance = np.var(opinions)
                    consensus_score = 1.0 / (1.0 + opinion_variance * 4.0)  # Scale variance
                
                expert_diversity = len(set(data['experts'])) / len(data['experts'])
                
                consensus_results[topic] = {
                    'consensus_score': consensus_score,
                    'opinion_count': len(opinions),
                    'expert_diversity': expert_diversity,
                    'avg_opinion': np.mean(opinions)
                }
            
            return {
                'topic_consensus': consensus_results,
                'overall_consensus': np.mean([r['consensus_score'] for r in consensus_results.values()]) if consensus_results else 0.5,
                'expert_diversity': np.mean([r['expert_diversity'] for r in consensus_results.values()]) if consensus_results else 0.5
            }
            
        except Exception as e:
            logger.error(f"Expert consensus analysis failed: {e}")
            return {'overall_consensus': 0.5}
    
    def _calculate_recency_weight(self, publication_date) -> float:
        """Calculate recency weight for content"""
        if not publication_date:
            return 0.5
        
        try:
            if isinstance(publication_date, str):
                pub_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
            elif isinstance(publication_date, datetime):
                pub_date = publication_date
            else:
                return 0.5
            
            days_old = (datetime.now(timezone.utc) - pub_date).days
            # Exponential decay with 6-month half-life
            recency_weight = math.exp(-days_old / (6 * 30))
            return max(0.1, min(1.0, recency_weight))
            
        except Exception:
            return 0.5
    
    async def _blend_analysis_results(self,
                                    base_analysis: Dict[str, Any],
                                    enhanced_metrics: Dict[str, Any],
                                    content_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Blend base and enhanced analysis results"""
        try:
            # Extract scores from both analyses
            base_score = base_analysis.get('overall_score', 0.5)
            
            # Extract enhanced scores
            bayesian_score = enhanced_metrics.get('bayesian_quality_scores', {}).get('blended_quality_score', 0.5)
            reliability_score = enhanced_metrics.get('source_reliability_analysis', {}).get('avg_source_reliability', 0.5)
            temporal_score = enhanced_metrics.get('temporal_decay_analysis', {}).get('avg_temporal_relevance', 0.5)
            statistical_score = enhanced_metrics.get('statistical_validity_scores', {}).get('avg_statistical_validity', 0.5)
            consensus_score = enhanced_metrics.get('expert_consensus_metrics', {}).get('overall_consensus', 0.5)
            
            # Weighted combination using quality dimensions
            enhanced_overall_score = (
                base_score * self.quality_dimensions['content_depth'] +
                bayesian_score * self.quality_dimensions['source_diversity'] +
                reliability_score * self.quality_dimensions['data_completeness'] +
                temporal_score * self.quality_dimensions['temporal_relevance'] +
                statistical_score * self.quality_dimensions['statistical_validity'] +
                consensus_score * self.quality_dimensions['expert_consensus'] +
                base_score * (self.quality_dimensions['citation_quality'] + self.quality_dimensions['methodology_rigor'])
            )
            
            # Create comprehensive result
            final_result = {
                **base_analysis,  # Include all base analysis results
                'enhanced_overall_score': enhanced_overall_score,
                'enhancement_confidence': enhanced_metrics.get('bayesian_quality_scores', {}).get('quality_confidence', 0.5),
                'quality_dimensions': {
                    'base_content_quality': base_score,
                    'bayesian_quality': bayesian_score,
                    'source_reliability': reliability_score,
                    'temporal_relevance': temporal_score,
                    'statistical_validity': statistical_score,
                    'expert_consensus': consensus_score
                },
                'enhanced_metrics': enhanced_metrics,
                'quality_improvement': enhanced_overall_score - base_score,
                'enhancement_metadata': {
                    'bayesian_enabled': True,
                    'content_items_processed': len(content_items),
                    'enhancement_timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
            
            return final_result
            
        except Exception as e:
            logger.error(f"Analysis result blending failed: {e}")
            # Fallback to base analysis with enhancement flag
            base_analysis['enhanced_overall_score'] = base_analysis.get('overall_score', 0.5)
            base_analysis['enhancement_metadata'] = {'error': str(e)}
            return base_analysis
    
    def _enhance_base_analysis(self, base_analysis: Dict[str, Any], content_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance base analysis when Bayesian features are disabled"""
        base_analysis['enhanced_overall_score'] = base_analysis.get('overall_score', 0.5)
        base_analysis['enhancement_metadata'] = {
            'bayesian_enabled': False,
            'content_items_processed': len(content_items),
            'enhancement_timestamp': datetime.now(timezone.utc).isoformat()
        }
        return base_analysis

__all__ = ['EnhancedContentProcessor']
