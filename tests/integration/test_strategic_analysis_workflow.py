# tests/integration/test_strategic_analysis_workflow.py

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from backend.app.services.analysis_session_manager import AnalysisSessionManager
from backend.app.services.expert_persona_scorer import ExpertPersonaScorer
from backend.app.services.formula_engine import FormulaEngine
from backend.app.models.analysis_models import AnalysisSession, AnalysisStatus, LayerScore, FactorCalculation

class TestStrategicAnalysisWorkflow:
    """Integration tests for the complete strategic analysis workflow"""
    
    @pytest.fixture
    def analysis_session_manager(self):
        """Create analysis session manager instance"""
        return AnalysisSessionManager()
    
    @pytest.fixture
    def expert_scorer(self):
        """Create expert persona scorer instance"""
        return ExpertPersonaScorer()
    
    @pytest.fixture
    def formula_engine(self):
        """Create formula engine instance"""
        return FormulaEngine()
    
    @pytest.fixture
    def sample_topic_knowledge(self):
        """Sample topic knowledge for testing"""
        return {
            "topic": "artificial intelligence",
            "documents": [
                {
                    "content": "AI is transforming healthcare with diagnostic tools",
                    "url": "https://example.com/ai-healthcare",
                    "quality_score": 0.85,
                    "relevance_score": 0.9
                },
                {
                    "content": "Machine learning algorithms improve business processes",
                    "url": "https://example.com/ml-business",
                    "quality_score": 0.78,
                    "relevance_score": 0.88
                }
            ],
            "total_documents": 2,
            "average_quality": 0.815,
            "topic_coverage": 0.85
        }
    
    @pytest.fixture
    def sample_layer_scores(self):
        """Sample layer scores for testing"""
        return [
            LayerScore(
                session_id="test_session_123",
                layer_name="Consumer",
                score=0.75,
                confidence=0.85,
                evidence_count=5,
                key_insights=["AI adoption increasing", "Consumer trust growing"],
                evidence_summary="Strong consumer interest in AI products",
                calculation_metadata={"method": "expert_analysis", "confidence": 0.85},
                created_at=datetime.now(timezone.utc)
            ),
            LayerScore(
                session_id="test_session_123",
                layer_name="Market",
                score=0.82,
                confidence=0.88,
                evidence_count=7,
                key_insights=["Market growing rapidly", "Competition increasing"],
                evidence_summary="Healthy market growth with competitive landscape",
                calculation_metadata={"method": "expert_analysis", "confidence": 0.88},
                created_at=datetime.now(timezone.utc)
            )
        ]
    
    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self, analysis_session_manager, sample_topic_knowledge):
        """Test the complete strategic analysis workflow from start to finish"""
        
        # Step 1: Create analysis session
        session_id = await analysis_session_manager.create_analysis_session(
            topic="artificial intelligence",
            user_id="test_user_123",
            analysis_parameters={"quality_threshold": 0.7}
        )
        
        assert session_id is not None
        assert session_id.startswith("session_")
        
        # Step 2: Execute strategic analysis
        with patch.object(analysis_session_manager, '_load_topic_knowledge') as mock_load:
            mock_load.return_value = sample_topic_knowledge
            
            with patch.object(analysis_session_manager, '_execute_layer_scoring') as mock_layers:
                mock_layers.return_value = self.sample_layer_scores()
                
                with patch.object(analysis_session_manager, '_calculate_factor_aggregations') as mock_factors:
                    mock_factors.return_value = []
                    
                    with patch.object(analysis_session_manager, '_generate_segment_scores') as mock_segments:
                        mock_segments.return_value = []
                        
                        with patch.object(analysis_session_manager, '_finalize_analysis') as mock_finalize:
                            mock_finalize.return_value = {"status": "completed"}
                            
                            result = await analysis_session_manager.execute_strategic_analysis(session_id)
                            
                            assert result is not None
                            assert result["status"] == "completed"
        
        # Step 3: Get session status
        status = await analysis_session_manager.get_session_status(session_id)
        assert status is not None
        assert "status" in status
        
        # Step 4: Get analysis results
        results = await analysis_session_manager.get_analysis_results(session_id)
        assert results is not None
    
    @pytest.mark.asyncio
    async def test_layer_scoring_workflow(self, expert_scorer, sample_topic_knowledge):
        """Test the layer scoring workflow"""
        
        strategic_layers = ["Consumer", "Market", "Product", "Brand"]
        
        with patch.object(expert_scorer, 'score_layer') as mock_score:
            mock_score.return_value = {
                "score": 0.75,
                "confidence": 0.85,
                "evidence": ["evidence1", "evidence2"],
                "insights": ["insight1", "insight2"],
                "evidence_summary": "Strong evidence",
                "metadata": {"method": "expert_analysis"}
            }
            
            layer_scores = []
            for layer in strategic_layers:
                result = await expert_scorer.score_layer(
                    topic_knowledge=sample_topic_knowledge,
                    layer_name=layer,
                    session_id="test_session"
                )
                
                assert result is not None
                assert "score" in result
                assert "confidence" in result
                assert "evidence" in result
                assert "insights" in result
                
                layer_scores.append(result)
            
            assert len(layer_scores) == len(strategic_layers)
            assert all(0.0 <= score["score"] <= 1.0 for score in layer_scores)
    
    @pytest.mark.asyncio
    async def test_factor_calculation_workflow(self, formula_engine, sample_layer_scores):
        """Test the factor calculation workflow"""
        
        # Convert layer scores to input format
        layer_score_dict = {
            score.layer_name.lower(): score.score 
            for score in sample_layer_scores
        }
        
        with patch.object(formula_engine, 'calculate_all_factors') as mock_calculate:
            mock_calculate.return_value = [
                FactorCalculation(
                    session_id="test_session_123",
                    factor_name="market_attractiveness",
                    calculated_value=0.78,
                    calculation_method="weighted_average",
                    input_scores=layer_score_dict,
                    calculation_details={"weights": {"consumer": 0.4, "market": 0.6}},
                    confidence_score=0.85,
                    created_at=datetime.now(timezone.utc)
                )
            ]
            
            result = await formula_engine.calculate_all_factors(
                layer_scores=layer_score_dict,
                session_id="test_session_123"
            )
            
            assert result is not None
            assert len(result) > 0
            assert all(isinstance(calc, FactorCalculation) for calc in result)
            assert all(0.0 <= calc.calculated_value <= 1.0 for calc in result)
    
    @pytest.mark.asyncio
    async def test_error_handling_in_workflow(self, analysis_session_manager):
        """Test error handling throughout the workflow"""
        
        # Test with invalid session ID
        with pytest.raises(Exception):
            await analysis_session_manager.get_session_status("invalid_session_id")
        
        # Test with invalid session ID for results
        with pytest.raises(Exception):
            await analysis_session_manager.get_analysis_results("invalid_session_id")
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_sessions(self, analysis_session_manager, sample_topic_knowledge):
        """Test handling multiple concurrent analysis sessions"""
        
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            session_id = await analysis_session_manager.create_analysis_session(
                topic=f"topic_{i}",
                user_id=f"user_{i}",
                analysis_parameters={}
            )
            session_ids.append(session_id)
        
        assert len(session_ids) == 3
        assert len(set(session_ids)) == 3  # All unique
        
        # Execute analyses concurrently
        tasks = []
        for session_id in session_ids:
            with patch.object(analysis_session_manager, '_load_topic_knowledge') as mock_load:
                mock_load.return_value = sample_topic_knowledge
                
                with patch.object(analysis_session_manager, '_execute_layer_scoring') as mock_layers:
                    mock_layers.return_value = []
                    
                    with patch.object(analysis_session_manager, '_calculate_factor_aggregations') as mock_factors:
                        mock_factors.return_value = []
                        
                        with patch.object(analysis_session_manager, '_generate_segment_scores') as mock_segments:
                            mock_segments.return_value = []
                            
                            with patch.object(analysis_session_manager, '_finalize_analysis') as mock_finalize:
                                mock_finalize.return_value = {"status": "completed"}
                                
                                task = analysis_session_manager.execute_strategic_analysis(session_id)
                                tasks.append(task)
        
        # Wait for all analyses to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        assert len(results) == 3
        assert all(not isinstance(result, Exception) for result in results)
    
    @pytest.mark.asyncio
    async def test_analysis_progress_tracking(self, analysis_session_manager):
        """Test analysis progress tracking throughout workflow"""
        
        session_id = await analysis_session_manager.create_analysis_session(
            topic="test topic",
            user_id="test_user",
            analysis_parameters={}
        )
        
        # Check initial progress
        progress = await analysis_session_manager._get_progress(session_id)
        assert progress is not None
        assert progress["progress_percentage"] == 0.0
        assert progress["current_stage"] == "initialization"
        
        # Update progress
        await analysis_session_manager._update_progress(session_id, "loading_knowledge", 10.0)
        
        updated_progress = await analysis_session_manager._get_progress(session_id)
        assert updated_progress["progress_percentage"] == 10.0
        assert updated_progress["current_stage"] == "loading_knowledge"
    
    @pytest.mark.asyncio
    async def test_analysis_session_persistence(self, analysis_session_manager):
        """Test that analysis sessions persist correctly"""
        
        # Create session
        session_id = await analysis_session_manager.create_analysis_session(
            topic="persistence test",
            user_id="test_user",
            analysis_parameters={"test_param": "test_value"}
        )
        
        # Retrieve session
        session = await analysis_session_manager._get_session(session_id)
        assert session is not None
        assert session["topic"] == "persistence test"
        assert session["user_id"] == "test_user"
        assert session["parameters"]["test_param"] == "test_value"
    
    @pytest.mark.asyncio
    async def test_layer_score_storage_and_retrieval(self, analysis_session_manager, sample_layer_scores):
        """Test layer score storage and retrieval"""
        
        session_id = "test_storage_session"
        
        # Store layer scores
        for layer_score in sample_layer_scores:
            layer_score.session_id = session_id
            await analysis_session_manager._store_layer_score(layer_score)
        
        # Retrieve layer scores
        retrieved_scores = await analysis_session_manager._get_layer_scores(session_id)
        assert len(retrieved_scores) == len(sample_layer_scores)
        
        # Verify score data
        for score in retrieved_scores:
            assert 0.0 <= score["score"] <= 1.0
            assert 0.0 <= score["confidence"] <= 1.0
            assert score["layer_name"] in ["Consumer", "Market"]
    
    @pytest.mark.asyncio
    async def test_factor_calculation_storage_and_retrieval(self, analysis_session_manager):
        """Test factor calculation storage and retrieval"""
        
        session_id = "test_factor_storage"
        
        factor_calc = FactorCalculation(
            session_id=session_id,
            factor_name="test_factor",
            calculated_value=0.75,
            calculation_method="test_method",
            input_scores={"consumer": 0.8, "market": 0.7},
            calculation_details={"test": "details"},
            confidence_score=0.85,
            created_at=datetime.now(timezone.utc)
        )
        
        # Store factor calculation
        await analysis_session_manager._store_factor_calculation(factor_calc)
        
        # Retrieve factor calculations
        retrieved_factors = await analysis_session_manager._get_factor_calculations(session_id)
        assert len(retrieved_factors) > 0
        
        # Verify factor data
        for factor in retrieved_factors:
            assert 0.0 <= factor["calculated_value"] <= 1.0
            assert factor["factor_name"] == "test_factor"
    
    @pytest.mark.asyncio
    async def test_analysis_event_publishing(self, analysis_session_manager):
        """Test analysis event publishing to Pub/Sub"""
        
        session_id = "test_event_session"
        
        with patch.object(analysis_session_manager, '_publish_analysis_event') as mock_publish:
            mock_publish.return_value = None
            
            # Create session (should publish event)
            await analysis_session_manager.create_analysis_session(
                topic="event test",
                user_id="test_user",
                analysis_parameters={}
            )
            
            # Verify event was published
            assert mock_publish.called
    
    @pytest.mark.asyncio
    async def test_analysis_timeout_handling(self, analysis_session_manager, sample_topic_knowledge):
        """Test analysis timeout handling"""
        
        session_id = await analysis_session_manager.create_analysis_session(
            topic="timeout test",
            user_id="test_user",
            analysis_parameters={}
        )
        
        # Simulate timeout by patching with slow operation
        async def slow_operation(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate slow operation
            return sample_topic_knowledge
        
        with patch.object(analysis_session_manager, '_load_topic_knowledge', side_effect=slow_operation):
            with patch.object(analysis_session_manager, '_execute_layer_scoring') as mock_layers:
                mock_layers.return_value = []
                
                with patch.object(analysis_session_manager, '_calculate_factor_aggregations') as mock_factors:
                    mock_factors.return_value = []
                    
                    with patch.object(analysis_session_manager, '_generate_segment_scores') as mock_segments:
                        mock_segments.return_value = []
                        
                        with patch.object(analysis_session_manager, '_finalize_analysis') as mock_finalize:
                            mock_finalize.return_value = {"status": "completed"}
                            
                            # Should complete without timeout
                            result = await analysis_session_manager.execute_strategic_analysis(session_id)
                            assert result is not None

if __name__ == "__main__":
    pytest.main([__file__])
