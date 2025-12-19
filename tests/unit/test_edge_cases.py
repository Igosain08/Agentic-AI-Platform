"""Edge case tests for safety and robustness."""

import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agentic_ai.agents.query_agent import QueryAgent
from agentic_ai.core.agent_factory import AgentFactory


@pytest.fixture
def mock_agent_factory():
    """Create a mock agent factory."""
    factory = MagicMock(spec=AgentFactory)
    mock_agent = MagicMock()
    factory.create_agent = AsyncMock(return_value=mock_agent)
    return factory


@pytest.fixture
def query_agent(mock_agent_factory):
    """Create a query agent instance."""
    return QueryAgent(agent_factory=mock_agent_factory)


async def test_empty_query_string(query_agent, mock_agent_factory):
    """Test handling of empty query string."""
    # Mock the agent that will be returned
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Please provide a valid query.")]
    })
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    result = await query_agent.process(
        message="",
        thread_id="test-thread"
    )
    
    assert "response" in result
    assert "metadata" in result


async def test_very_long_query(query_agent, mock_agent_factory):
    """Test handling of very long query (10k+ characters)."""
    long_query = "What hotels are in Paris? " * 500  # ~12k characters
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Query processed successfully.")]
    })
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    result = await query_agent.process(
        message=long_query,
        thread_id="test-thread"
    )
    
    assert "response" in result
    assert len(result["response"]) > 0


async def test_special_characters_query(query_agent, mock_agent_factory):
    """Test handling of special characters and unicode."""
    special_queries = [
        "What hotels are in Paris? 🏨",
        "Find hotels with price < $100",
        "Query with émojis and spéciál chárs",
        "SELECT * FROM hotels WHERE price = 100; -- SQL injection attempt",
        "Query with\nnewlines\tand\ttabs",
    ]
    
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Query handled safely.")]
    })
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    for query in special_queries:
        result = await query_agent.process(
            message=query,
            thread_id="test-thread"
        )
        assert "response" in result
        assert "metadata" in result


def test_malformed_json_handling():
    """Test that malformed JSON in requests is handled gracefully."""
    from fastapi.testclient import TestClient
    from agentic_ai.api.main import app
    
    client = TestClient(app)
    
    # Test with invalid JSON
    response = client.post(
        "/api/v1/query",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code in [400, 422]  # Bad Request or Unprocessable Entity


def test_missing_required_fields():
    """Test API endpoint with missing required fields."""
    from fastapi.testclient import TestClient
    from agentic_ai.api.main import app
    
    client = TestClient(app)
    
    # Test with missing 'message' field
    response = client.post(
        "/api/v1/query",
        json={"thread_id": "test-thread"}
    )
    
    assert response.status_code == 422  # Unprocessable Entity


def test_invalid_thread_id():
    """Test with invalid thread_id format."""
    from fastapi.testclient import TestClient
    from agentic_ai.api.main import app
    
    client = TestClient(app)
    
    response = client.post(
        "/api/v1/query",
        json={
            "message": "test query",
            "thread_id": ""  # Empty thread_id
        }
    )
    
    # Should either accept or reject gracefully
    assert response.status_code in [200, 400, 422]


async def test_unicode_and_emoji_in_query(query_agent, mock_agent_factory):
    """Test handling of unicode characters and emojis."""
    unicode_queries = [
        "Find hotels in 北京 (Beijing)",
        "Hotels with ⭐⭐⭐⭐⭐ rating",
        "Query with 日本語 characters",
        "Find 🏨 in 🇫🇷",
    ]
    
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Unicode handled correctly.")]
    })
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    for query in unicode_queries:
        result = await query_agent.process(
            message=query,
            thread_id="test-thread"
        )
        assert "response" in result


async def test_sql_injection_attempt(query_agent, mock_agent_factory):
    """Test that SQL injection attempts are handled safely."""
    sql_injection_queries = [
        "'; DROP TABLE hotels; --",
        "1' OR '1'='1",
        "admin'--",
        "'; SELECT * FROM users; --",
    ]
    
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Query processed safely.")]
    })
    mock_agent_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    for query in sql_injection_queries:
        result = await query_agent.process(
            message=query,
            thread_id="test-thread"
        )
        # Should not crash, should handle gracefully
        assert "response" in result
        assert "metadata" in result

