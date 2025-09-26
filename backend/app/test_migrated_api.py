import pytest
from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_migrated_topics():
    """Test the migrated topics endpoint"""
    resp = client.get("/api/v3/migrated/topics")
    assert resp.status_code == 200
    data = resp.json()
    assert "available_topics" in data
    assert isinstance(data["available_topics"], list)

def test_session_endpoint():
    """Test session endpoint"""
    session_id = "v2_analysis_20250905_185553_d5654178"
    resp = client.get(f"/api/v3/migrated/sessions/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["session_id"] == session_id

def test_results_endpoint():
    """Test results endpoint"""
    session_id = "v2_analysis_20250905_185553_d5654178"
    resp = client.get(f"/api/v3/migrated/results/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "strategic_layers" in data

def test_action_layer_endpoint():
    """Test action layer endpoint"""
    session_id = "v2_analysis_20250905_185553_d5654178"
    resp = client.get(f"/api/v3/migrated/action-layer/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "essential_metrics" in data

def test_vector_query():
    """Test vector query endpoint"""
    resp = client.post(
        "/api/v3/migrated/vector/pergola_market/query?query=test&max_results=5"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "query" in data
    assert "results" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
