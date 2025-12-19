"""Integration tests for API endpoints using FastAPI TestClient."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from agentic_ai.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_metrics_endpoint(client):
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_query_endpoint_success(client):
    """Test successful query endpoint call."""
    with patch('agentic_ai.api.routes.query.get_orchestrator') as mock_orch:
        mock_orch_instance = MagicMock()
        mock_orch_instance.process = AsyncMock(return_value={
            "response": "Here are hotels in Paris: [hotel list]",
            "metadata": {
                "thread_id": "test-thread",
                "agent_type": "query",
                "execution_time_ms": 2500,
                "cache_hit": False
            }
        })
        mock_orch.return_value = mock_orch_instance
        
        response = client.post(
            "/api/v1/query",
            json={
                "message": "What hotels are in Paris?",
                "thread_id": "test-thread"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "thread_id" in data
        assert "metadata" in data
        assert data["thread_id"] == "test-thread"


def test_query_endpoint_missing_message(client):
    """Test query endpoint with missing message field."""
    response = client.post(
        "/api/v1/query",
        json={
            "thread_id": "test-thread"
        }
    )
    
    assert response.status_code == 422  # Unprocessable Entity


def test_query_endpoint_missing_thread_id(client):
    """Test query endpoint with missing thread_id field."""
    response = client.post(
        "/api/v1/query",
        json={
            "message": "What hotels are in Paris?"
        }
    )
    
    assert response.status_code == 422  # Unprocessable Entity


def test_query_endpoint_empty_message(client):
    """Test query endpoint with empty message."""
    response = client.post(
        "/api/v1/query",
        json={
            "message": "",
            "thread_id": "test-thread"
        }
    )
    
    # Should either accept or reject gracefully
    assert response.status_code in [200, 400, 422]


def test_query_endpoint_invalid_json(client):
    """Test query endpoint with invalid JSON."""
    response = client.post(
        "/api/v1/query",
        data="not json",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code in [400, 422]


def test_query_endpoint_with_agent_type(client):
    """Test query endpoint with specific agent_type."""
    with patch('agentic_ai.api.routes.query.get_orchestrator') as mock_orch:
        mock_orch_instance = MagicMock()
        mock_orch_instance.process = AsyncMock(return_value={
            "response": "Test response",
            "metadata": {
                "thread_id": "test-thread",
                "agent_type": "query",
                "execution_time_ms": 1000,
                "cache_hit": False
            }
        })
        mock_orch.return_value = mock_orch_instance
        
        response = client.post(
            "/api/v1/query",
            json={
                "message": "Test query",
                "thread_id": "test-thread",
                "agent_type": "query"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["agent_type"] == "query"


def test_query_endpoint_with_cache_disabled(client):
    """Test query endpoint with cache disabled."""
    with patch('agentic_ai.api.routes.query.get_orchestrator') as mock_orch:
        mock_orch_instance = MagicMock()
        mock_orch_instance.process = AsyncMock(return_value={
            "response": "Test response",
            "metadata": {
                "thread_id": "test-thread",
                "agent_type": "query",
                "execution_time_ms": 1000,
                "cache_hit": False
            }
        })
        mock_orch.return_value = mock_orch_instance
        
        response = client.post(
            "/api/v1/query",
            json={
                "message": "Test query",
                "thread_id": "test-thread",
                "use_cache": False
            }
        )
        
        assert response.status_code == 200


def test_query_endpoint_error_handling(client):
    """Test query endpoint error handling."""
    with patch('agentic_ai.api.routes.query.get_orchestrator') as mock_orch:
        mock_orch_instance = MagicMock()
        mock_orch_instance.process = AsyncMock(side_effect=Exception("Test error"))
        mock_orch.return_value = mock_orch_instance
        
        response = client.post(
            "/api/v1/query",
            json={
                "message": "Test query",
                "thread_id": "test-thread"
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data or "error" in data


def test_query_endpoint_timeout_simulation(client):
    """Test query endpoint with timeout scenario."""
    import asyncio
    
    with patch('agentic_ai.api.routes.query.get_orchestrator') as mock_orch:
        mock_orch_instance = MagicMock()
        mock_orch_instance.process = AsyncMock(side_effect=asyncio.TimeoutError("Query timed out"))
        mock_orch.return_value = mock_orch_instance
        
        response = client.post(
            "/api/v1/query",
            json={
                "message": "Test query",
                "thread_id": "test-thread"
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        detail = data.get("detail", "").lower()
        assert "timeout" in detail or "timed out" in detail or "error" in data or "query" in detail

