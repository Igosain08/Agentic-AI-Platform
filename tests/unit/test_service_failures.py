"""Tests for service failure scenarios and error handling."""

import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from agentic_ai.agents.query_agent import QueryAgent
from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.api.main import app


@pytest.fixture
def mock_agent_factory():
    """Create a mock agent factory."""
    factory = MagicMock(spec=AgentFactory)
    return factory


@pytest.fixture
def query_agent(mock_agent_factory):
    """Create a query agent instance."""
    return QueryAgent(agent_factory=mock_agent_factory)


async def test_couchbase_service_unavailable(query_agent, mock_agent_factory):
    """Test handling of Couchbase ServiceUnavailableException."""
    mock_agent = MagicMock()
    
    # Simulate ServiceUnavailableException
    error_msg = "ServiceUnavailableException: service_not_available (4)"
    mock_agent.ainvoke = AsyncMock(side_effect=Exception(f"Query failed: {error_msg}"))
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    with pytest.raises(Exception) as exc_info:
        await query_agent.process(
            message="What hotels are in Paris?",
            thread_id="test-thread"
        )
    
    # Should raise exception with helpful message
    assert "Service unavailable" in str(exc_info.value) or "Query failed" in str(exc_info.value)


async def test_couchbase_connection_timeout(query_agent, mock_agent_factory):
    """Test handling of Couchbase connection timeout."""
    import asyncio
    
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(side_effect=asyncio.TimeoutError("Query timed out"))
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    with pytest.raises(Exception) as exc_info:
        await query_agent.process(
            message="What hotels are in Paris?",
            thread_id="test-thread"
        )
    
    # Should handle timeout gracefully
    assert "timeout" in str(exc_info.value).lower() or "timed out" in str(exc_info.value).lower()


async def test_openai_api_503_error(query_agent, mock_agent_factory):
    """Test handling of OpenAI API 503 Service Unavailable."""
    mock_agent = MagicMock()
    
    # Simulate OpenAI 503 error
    error = Exception("OpenAI API error: 503 Service Unavailable")
    mock_agent.ainvoke = AsyncMock(side_effect=error)
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    with pytest.raises(Exception):
        await query_agent.process(
            message="What hotels are in Paris?",
            thread_id="test-thread"
        )


async def test_redis_connection_failure():
    """Test that Redis connection failure doesn't break the system."""
    from agentic_ai.utils.cache import CacheManager
    
    # Mock Redis connection failure
    with patch('redis.asyncio.from_url', side_effect=Exception("Redis connection failed")):
        cache_manager = CacheManager()
        # Should handle gracefully, not crash
        result = await cache_manager.get("test", "key")
        assert result is None  # Should return None, not crash


async def test_mlflow_tracking_failure_doesnt_break_agent(query_agent, mock_agent_factory):
    """Test that MLflow tracking failure doesn't break agent execution."""
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Test response")]
    })
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    # Mock MLflow failure
    with patch('agentic_ai.monitoring.mlflow_tracker.get_mlflow_tracker') as mock_tracker:
        mock_tracker_instance = MagicMock()
        mock_tracker_instance.log_latency = MagicMock(side_effect=Exception("MLflow error"))
        mock_tracker_instance.is_enabled = True
        mock_tracker.return_value = mock_tracker_instance
        
        # Should still work despite MLflow error
        result = await query_agent.process(
            message="What hotels are in Paris?",
            thread_id="test-thread"
        )
        
        assert "response" in result
        assert result["response"] == "Test response"


async def test_agent_timeout_handling(query_agent, mock_agent_factory):
    """Test that agent execution timeout is handled gracefully."""
    import asyncio
    
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(side_effect=asyncio.TimeoutError("Agent execution timed out"))
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    with pytest.raises(Exception) as exc_info:
        await query_agent.process(
            message="What hotels are in Paris?",
            thread_id="test-thread"
        )
    
    # Should provide helpful error message
    assert "timeout" in str(exc_info.value).lower() or "timed out" in str(exc_info.value).lower()


def test_api_endpoint_handles_service_failure():
    """Test that API endpoint handles service failures gracefully."""
    client = TestClient(app)
    
    # Mock orchestrator to raise exception
    with patch('agentic_ai.api.routes.query.get_orchestrator') as mock_orch:
        mock_orch_instance = MagicMock()
        mock_orch_instance.process = AsyncMock(side_effect=Exception("Service unavailable"))
        mock_orch.return_value = mock_orch_instance
        
        response = client.post(
            "/api/v1/query",
            json={
                "message": "What hotels are in Paris?",
                "thread_id": "test-thread"
            }
        )
        
        # Should return 500 with error message, not crash
        assert response.status_code == 500
        assert "error" in response.json() or "detail" in response.json()


async def test_database_connection_error_handling():
    """Test handling of database connection errors."""
    from agentic_ai.agents.query_agent import QueryAgent
    from agentic_ai.core.agent_factory import AgentFactory
    
    mock_factory = MagicMock(spec=AgentFactory)
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(side_effect=Exception("Database connection failed"))
    mock_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    agent = QueryAgent(agent_factory=mock_factory)
    
    with pytest.raises(Exception) as exc_info:
        await agent.process(
            message="What hotels are in Paris?",
            thread_id="test-thread"
        )
    
    # Should provide helpful error message
    assert "connection" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower() or "Query failed" in str(exc_info.value)

