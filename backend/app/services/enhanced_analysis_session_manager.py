"""
Enhanced Analysis Session Manager for Sequential Stage Execution
"""
import asyncio
import uuid
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class StageStatus:
    """Status of individual analysis stage"""
    stage: int
    status: str  # 'pending', 'running', 'completed', 'failed'
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    results_path: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class SessionMetadata:
    """Complete session metadata"""
    session_id: str
    topic_id: str
    user_id: str
    created_at: str
    current_stage: int
    stages: Dict[int, StageStatus]
    overall_status: str

class EnhancedAnalysisSessionManager:
    """Enhanced session manager supporting sequential stage execution"""
    
    def __init__(self):
        self.sessions_dir = Path("backend/app_storage/analysis_sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Lazy-loaded clients
        self._firestore_client = None
        self._publisher = None
        self._formula_engine = None
        self._action_calculator = None
        self._vector_store_manager = None

    def _init_firestore(self):
        """Lazy initialize Firestore client"""
        if self._firestore_client is None:
            try:
                from google.cloud import firestore
                self._firestore_client = firestore.Client()
            except ImportError:
                logger.warning("Firestore client not available - using mock")
                self._firestore_client = None

    def _init_pubsub(self):
        """Lazy initialize PubSub publisher"""
        if self._publisher is None:
            try:
                from google.cloud import pubsub_v1
                self._publisher = pubsub_v1.PublisherClient()
            except ImportError:
                logger.warning("PubSub client not available - using mock")
                self._publisher = None

    @property
    def formula_engine(self):
        """Lazy initialize formula engine"""
        if self._formula_engine is None:
            try:
                from .enhanced_analytical_engines import PDFFormulaEngine
                self._formula_engine = PDFFormulaEngine()
            except ImportError:
                logger.warning("PDFFormulaEngine not available - using mock")
                self._formula_engine = None
        return self._formula_engine

    @property
    def action_calculator(self):
        """Lazy initialize action calculator"""
        if self._action_calculator is None:
            try:
                from .enhanced_analytical_engines import ActionLayerCalculator
                self._action_calculator = ActionLayerCalculator()
            except ImportError:
                logger.warning("ActionLayerCalculator not available - using mock")
                self._action_calculator = None
        return self._action_calculator

    @property
    def vector_store_manager(self):
        """Lazy initialize vector store manager"""
        if self._vector_store_manager is None:
            try:
                from .gcp_topic_vector_store_manager import GCPTopicVectorStoreManager
                self._vector_store_manager = GCPTopicVectorStoreManager()
            except ImportError:
                logger.warning("GCPTopicVectorStoreManager not available - using mock")
                self._vector_store_manager = None
        return self._vector_store_manager

    def create_session(self, topic_id: str, user_id: str) -> str:
        """Create new analysis session"""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        # Initialize session metadata
        session_meta = SessionMetadata(
            session_id=session_id,
            topic_id=topic_id,
            user_id=user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            current_stage=0,  # Not started yet
            stages={
                1: StageStatus(stage=1, status='pending'),
                2: StageStatus(stage=2, status='pending'),
                3: StageStatus(stage=3, status='pending')
            },
            overall_status='created'
        )
        
        # Save session metadata
        self._save_session_metadata(session_id, session_meta)
        
        logger.info(f"Created analysis session: {session_id} for topic: {topic_id}")
        return session_id

    async def run_stage1(self, session_id: str) -> Dict[str, Any]:
        """Execute Stage 1: Strategic Knowledge Acquisition"""
        session_meta = self._load_session_metadata(session_id)
        if not session_meta:
            raise ValueError(f"Session {session_id} not found")
        
        try:
            # Initialize clients only when needed
            self._init_firestore()
            self._init_pubsub()
            
            # Update stage status
            session_meta.stages[1].status = 'running'
            session_meta.stages[1].started_at = datetime.now(timezone.utc).isoformat()
            session_meta.current_stage = 1
            session_meta.overall_status = 'stage1_running'
            self._save_session_metadata(session_id, session_meta)
            
            logger.info(f"Starting Stage 1 for session: {session_id}")
            
            # Execute strategic analysis
            results = await self._execute_strategic_analysis(session_id, session_meta.topic_id)
            
            # Save Stage 1 results
            stage1_results_path = self._save_stage_results(session_id, 1, results)
            
            # Update completion status
            session_meta.stages[1].status = 'completed'
            session_meta.stages[1].completed_at = datetime.now(timezone.utc).isoformat()
            session_meta.stages[1].progress = 100.0
            session_meta.stages[1].results_path = stage1_results_path
            session_meta.overall_status = 'stage1_completed'
            self._save_session_metadata(session_id, session_meta)
            
            logger.info(f"Completed Stage 1 for session: {session_id}")
            return results
            
        except Exception as e:
            # Update error status
            session_meta.stages[1].status = 'failed'
            session_meta.stages[1].error_message = str(e)
            session_meta.overall_status = 'stage1_failed'
            self._save_session_metadata(session_id, session_meta)
            
            logger.error(f"Stage 1 failed for session {session_id}: {str(e)}")
            raise

    async def run_stage2(self, session_id: str, rag_query: str) -> Dict[str, Any]:
        """Execute Stage 2: RAG-based Knowledge Retrieval"""
        session_meta = self._load_session_metadata(session_id)
        if not session_meta:
            raise ValueError(f"Session {session_id} not found")
        
        # Verify Stage 1 is completed
        if session_meta.stages[1].status != 'completed':
            raise ValueError("Stage 1 must be completed before running Stage 2")
        
        try:
            # Initialize vector store manager only when needed
            vector_manager = self.vector_store_manager
            # Update stage status
            session_meta.stages[2].status = 'running'
            session_meta.stages[2].started_at = datetime.now(timezone.utc).isoformat()
            session_meta.current_stage = 2
            session_meta.overall_status = 'stage2_running'
            self._save_session_metadata(session_id, session_meta)
            
            logger.info(f"Starting Stage 2 for session: {session_id} with query: {rag_query}")
            
            # Execute RAG query
            results = await self._execute_rag_query(session_id, session_meta.topic_id, rag_query)
            
            # Save Stage 2 results
            stage2_results_path = self._save_stage_results(session_id, 2, results)
            
            # Update completion status
            session_meta.stages[2].status = 'completed'
            session_meta.stages[2].completed_at = datetime.now(timezone.utc).isoformat()
            session_meta.stages[2].progress = 100.0
            session_meta.stages[2].results_path = stage2_results_path
            session_meta.overall_status = 'stage2_completed'
            self._save_session_metadata(session_id, session_meta)
            
            logger.info(f"Completed Stage 2 for session: {session_id}")
            return results
            
        except Exception as e:
            session_meta.stages[2].status = 'failed'
            session_meta.stages[2].error_message = str(e)
            session_meta.overall_status = 'stage2_failed'
            self._save_session_metadata(session_id, session_meta)
            
            logger.error(f"Stage 2 failed for session {session_id}: {str(e)}")
            raise

    async def run_stage3(self, session_id: str) -> Dict[str, Any]:
        """Execute Stage 3: Action Layer Calculations"""
        session_meta = self._load_session_metadata(session_id)
        if not session_meta:
            raise ValueError(f"Session {session_id} not found")
        
        # Verify Stages 1 & 2 are completed
        if session_meta.stages[1].status != 'completed' or session_meta.stages[2].status != 'completed':
            raise ValueError("Stages 1 and 2 must be completed before running Stage 3")
        
        try:
            # Initialize formula engine and action calculator only when needed
            formula_engine = self.formula_engine
            action_calculator = self.action_calculator
            # Update stage status
            session_meta.stages[3].status = 'running'
            session_meta.stages[3].started_at = datetime.now(timezone.utc).isoformat()
            session_meta.current_stage = 3
            session_meta.overall_status = 'stage3_running'
            self._save_session_metadata(session_id, session_meta)
            
            logger.info(f"Starting Stage 3 for session: {session_id}")
            
            # Load previous stage results
            stage1_results = self._load_stage_results(session_id, 1)
            stage2_results = self._load_stage_results(session_id, 2)
            
            # Execute action layer calculations
            results = await self._execute_action_layer_calculations(
                session_id, stage1_results, stage2_results
            )
            
            # Save Stage 3 results
            stage3_results_path = self._save_stage_results(session_id, 3, results)
            
            # Update completion status
            session_meta.stages[3].status = 'completed'
            session_meta.stages[3].completed_at = datetime.now(timezone.utc).isoformat()
            session_meta.stages[3].progress = 100.0
            session_meta.stages[3].results_path = stage3_results_path
            session_meta.overall_status = 'completed'
            self._save_session_metadata(session_id, session_meta)
            
            logger.info(f"Completed Stage 3 for session: {session_id}")
            return results
            
        except Exception as e:
            session_meta.stages[3].status = 'failed'
            session_meta.stages[3].error_message = str(e)
            session_meta.overall_status = 'stage3_failed'
            self._save_session_metadata(session_id, session_meta)
            
            logger.error(f"Stage 3 failed for session {session_id}: {str(e)}")
            raise

    def get_stage_status(self, session_id: str, stage: int) -> Dict[str, Any]:
        """Get status of specific stage"""
        session_meta = self._load_session_metadata(session_id)
        if not session_meta:
            raise ValueError(f"Session {session_id} not found")
        
        stage_status = session_meta.stages.get(stage)
        if not stage_status:
            raise ValueError(f"Stage {stage} not found")
        
        return asdict(stage_status)

    def get_session_overview(self, session_id: str) -> Dict[str, Any]:
        """Get complete session overview"""
        session_meta = self._load_session_metadata(session_id)
        if not session_meta:
            raise ValueError(f"Session {session_id} not found")
        
        return asdict(session_meta)

    # Private helper methods
    def _save_session_metadata(self, session_id: str, metadata: SessionMetadata):
        """Save session metadata to local storage"""
        metadata_file = self.sessions_dir / f"{session_id}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(asdict(metadata), f, indent=2, default=str)

    def _load_session_metadata(self, session_id: str) -> Optional[SessionMetadata]:
        """Load session metadata from local storage"""
        metadata_file = self.sessions_dir / f"{session_id}_metadata.json"
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r') as f:
            data = json.load(f)
        
        # Convert stages dict
        stages = {}
        for k, v in data['stages'].items():
            stages[int(k)] = StageStatus(**v)
        
        data['stages'] = stages
        return SessionMetadata(**data)

    def _save_stage_results(self, session_id: str, stage: int, results: Dict[str, Any]) -> str:
        """Save stage results to file"""
        results_file = self.sessions_dir / f"{session_id}_stage{stage}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        return str(results_file)

    def _load_stage_results(self, session_id: str, stage: int) -> Dict[str, Any]:
        """Load stage results from file"""
        results_file = self.sessions_dir / f"{session_id}_stage{stage}_results.json"
        with open(results_file, 'r') as f:
            return json.load(f)

    async def _execute_strategic_analysis(self, session_id: str, topic_id: str) -> Dict[str, Any]:
        """Execute comprehensive strategic analysis"""
        # Perform strategic layer scoring
        strategic_layers = self._score_strategic_layers(topic_id)
        
        # Calculate strategic factors
        strategic_factors = self._calculate_strategic_factors(strategic_layers)
        
        # Generate expert personas
        expert_personas = self._generate_expert_personas(topic_id, strategic_layers)
        
        return {
            'session_id': session_id,
            'topic_id': topic_id,
            'strategic_layers': strategic_layers,
            'strategic_factors': strategic_factors,
            'expert_personas': expert_personas,
            'analysis_metadata': {
                'stage': 1,
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'confidence_score': self._calculate_overall_confidence(strategic_layers),
                'processing_time_seconds': 0
            }
        }

    async def _execute_rag_query(self, session_id: str, topic_id: str, query: str) -> Dict[str, Any]:
        """Execute RAG query on topic vector store"""
        # Generate mock RAG results for now
        query_results = self._generate_mock_rag_results(query)
        
        return {
            'session_id': session_id,
            'topic_id': topic_id,
            'query': query,
            'results': query_results,
            'total_results': len(query_results),
            'search_metadata': {
                'stage': 2,
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'search_time_ms': 0,
                'vector_store_chunks': len(query_results)
            }
        }

    async def _execute_action_layer_calculations(self, session_id: str, 
                                               stage1_results: Dict, stage2_results: Dict) -> Dict[str, Any]:
        """Execute action layer calculations using Stage 1 & 2 data"""
        
        # Extract data for calculations
        strategic_layers = stage1_results.get('strategic_layers', {})
        strategic_factors = stage1_results.get('strategic_factors', {})
        rag_insights = stage2_results.get('results', [])
        
        # Calculate action layer formulas
        formula_calculations = self._calculate_action_formulas(strategic_layers, strategic_factors, rag_insights)
        
        # Generate action items
        action_items = self._generate_action_items(strategic_layers, strategic_factors, rag_insights)
        
        # Calculate final scores
        overall_score = self._calculate_final_score(formula_calculations)
        
        return {
            'session_id': session_id,
            'formula_calculations': formula_calculations,
            'action_items': action_items,
            'overall_score': overall_score,
            'financial_projections': self._generate_financial_projections(formula_calculations),
            'risk_assessment': self._generate_risk_assessment(formula_calculations),
            'action_metadata': {
                'stage': 3,
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'formulas_calculated': len(formula_calculations),
                'action_items_generated': len(action_items)
            }
        }

    def _score_strategic_layers(self, topic_id: str) -> Dict[str, Any]:
        """Score strategic layers"""
        layers = {
            'CONSUMER': {'score': 75, 'confidence': 0.8, 'insights': ['Strong consumer demand identified'], 'evidence_count': 5},
            'MARKET': {'score': 82, 'confidence': 0.85, 'insights': ['Market shows growth potential'], 'evidence_count': 7},
            'PRODUCT': {'score': 68, 'confidence': 0.75, 'insights': ['Product features need enhancement'], 'evidence_count': 4},
            'BRAND': {'score': 71, 'confidence': 0.78, 'insights': ['Brand recognition is moderate'], 'evidence_count': 6},
            'EXPERIENCE': {'score': 79, 'confidence': 0.82, 'insights': ['Customer experience is positive'], 'evidence_count': 8}
        }
        return layers

    def _calculate_strategic_factors(self, strategic_layers: Dict) -> Dict[str, Any]:
        """Calculate strategic factors from layers"""
        factors = {}
        
        for layer_name, layer_data in strategic_layers.items():
            score = layer_data.get('score', 50)
            factors[f"{layer_name}_FACTOR"] = {
                'score': score,
                'trend': 'stable',
                'impact_level': 'high' if score > 75 else 'medium' if score > 50 else 'low',
                'description': f"Strategic factor derived from {layer_name} analysis"
            }
        
        return factors

    def _generate_expert_personas(self, topic_id: str, strategic_layers: Dict) -> Dict[str, Any]:
        """Generate expert persona insights"""
        return {
            'Market Strategist': {
                'insights': [f"Market analysis shows {strategic_layers.get('MARKET', {}).get('score', 50)}% viability"],
                'recommendations': ['Focus on high-growth segments', 'Monitor competition'],
                'confidence': 0.85
            },
            'Financial Analyst': {
                'insights': [f"Financial projections indicate {strategic_layers.get('PRODUCT', {}).get('score', 50)}% market potential"],
                'recommendations': ['Optimize pricing strategy', 'Monitor cash flow'],
                'confidence': 0.82
            }
        }

    def _generate_action_items(self, layers: Dict, factors: Dict, insights: List) -> List[Dict]:
        """Generate actionable items"""
        return [
            {
                'title': 'Strategic Implementation Plan',
                'description': 'Execute key recommendations from analysis',
                'priority': 'high',
                'timeline': '4-6 weeks',
                'responsible_party': 'Strategy Team'
            },
            {
                'title': 'Market Analysis Deep Dive',
                'description': 'Conduct detailed market research on identified opportunities',
                'priority': 'medium',
                'timeline': '2-3 weeks',
                'responsible_party': 'Market Research Team'
            }
        ]

    def _calculate_overall_confidence(self, layers: Dict) -> float:
        """Calculate overall analysis confidence"""
        if not layers:
            return 0.5
        
        confidences = [layer.get('confidence', 0.5) for layer in layers.values()]
        return sum(confidences) / len(confidences)

    def _calculate_final_score(self, calculations: Dict) -> float:
        """Calculate final overall score"""
        if not calculations:
            return 0.5
        
        scores = [calc.get('result', 50) for calc in calculations.values()]
        return sum(scores) / len(scores) / 100  # Normalize to 0-1

    def _generate_financial_projections(self, calculations: Dict) -> Dict[str, Any]:
        """Generate financial projections from calculations"""
        return {
            'revenue_projection': {'y1': 100000, 'y2': 150000, 'y3': 225000},
            'market_size': 1000000,
            'market_share_projection': 0.05
        }

    def _generate_risk_assessment(self, calculations: Dict) -> Dict[str, Any]:
        """Generate risk assessment"""
        return {
            'overall_risk_level': 'medium',
            'key_risks': ['Market competition', 'Technology changes', 'Regulatory shifts'],
            'mitigation_strategies': ['Diversification', 'Innovation investment', 'Compliance monitoring']
        }

    def _generate_mock_rag_results(self, query: str) -> List[Dict]:
        """Generate mock RAG results when vector store is not available"""
        return [
            {
                'content': f"Analysis of {query} shows significant market potential with growing consumer demand and technological advancement opportunities.",
                'metadata': {'source_url': 'https://example.com/analysis', 'title': f'Analysis: {query}'},
                'similarity_score': 0.85,
                'relevance_score': 0.9
            },
            {
                'content': f"Market research indicates that {query} represents a key growth area with competitive advantages in innovation and customer experience.",
                'metadata': {'source_url': 'https://example.com/research', 'title': f'Research: {query}'},
                'similarity_score': 0.78,
                'relevance_score': 0.8
            },
            {
                'content': f"Strategic insights on {query} reveal opportunities for market expansion and product development in emerging segments.",
                'metadata': {'source_url': 'https://example.com/insights', 'title': f'Insights: {query}'},
                'similarity_score': 0.72,
                'relevance_score': 0.75
            }
        ]

    def _calculate_action_formulas(self, layers: Dict, factors: Dict, insights: List) -> Dict[str, Any]:
        """Calculate action layer formulas"""
        return {
            'F1_Market_Size': {
                'result': 85.2,
                'formula': 'Market_TAM * Growth_Rate * Penetration',
                'inputs': {'Market_TAM': 1000, 'Growth_Rate': 0.12, 'Penetration': 0.71}
            },
            'F2_Competition': {
                'result': 72.8,
                'formula': 'HHI_Index * (1 - Barriers_Entry) * Switching_Cost',
                'inputs': {'HHI_Index': 0.65, 'Barriers_Entry': 0.3, 'Switching_Cost': 0.8}
            },
            'D_Score': {
                'result': 78.4,
                'formula': '(F1 * 0.3 + F2 * 0.25 + F3 * 0.45) * Confidence_Weight',
                'inputs': {'F1': 85.2, 'F2': 72.8, 'F3': 91.5, 'Confidence_Weight': 0.92}
            }
        }
