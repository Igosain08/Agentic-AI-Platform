"""Unit tests for agents."""

import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agentic_ai.agents.query_agent import QueryAgent
from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.core.mcp_client import MCPClient


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


async def test_query_agent_process(query_agent, mock_agent_factory):
    """Test query agent processing."""
    mock_agent = await mock_agent_factory.create_agent()
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Test response")]
    })
    
    result = await query_agent.process(
        message="Test query",
        thread_id="test-thread"
    )
    
    assert "response" in result
    assert "metadata" in result
    assert result["response"] == "Test response"
    assert result["metadata"]["thread_id"] == "test-thread"


async def test_query_agent_uses_cache(query_agent, mock_agent_factory):
    """Test that query agent uses cache when available."""
    from agentic_ai.utils.cache import CacheManager
    
    cache_manager = MagicMock(spec=CacheManager)
    cache_manager.get = AsyncMock(return_value={"response": "Cached", "metadata": {}})
    query_agent.cache_manager = cache_manager
    
    result = await query_agent.process(
        message="Test query",
        thread_id="test-thread"
    )
    
    assert result["response"] == "Cached"
    cache_manager.get.assert_called_once()

