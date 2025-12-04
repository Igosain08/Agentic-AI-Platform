"""Unit tests for agent factory."""

import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.core.mcp_client import MCPClient
from agentic_ai.config.settings import get_settings


@pytest.fixture
def mock_mcp_client():
    """Create a mock MCP client."""
    client = MagicMock(spec=MCPClient)
    session = AsyncMock()
    session_context = AsyncMock()
    session_context.__aenter__ = AsyncMock(return_value=session)
    session_context.__aexit__ = AsyncMock(return_value=None)
    client.session.return_value = session_context
    return client


@pytest.fixture
def agent_factory(mock_mcp_client):
    """Create an agent factory instance."""
    return AgentFactory(mcp_client=mock_mcp_client)


async def test_create_agent(agent_factory, mock_mcp_client):
    """Test agent creation."""
    with patch("agentic_ai.core.agent_factory.load_mcp_tools") as mock_load_tools:
        mock_load_tools.return_value = []
        
        agent = await agent_factory.create_agent()
        
        assert agent is not None
        mock_mcp_client.session.assert_called_once()
        mock_load_tools.assert_called_once()


async def test_create_agent_loads_tools(agent_factory, mock_mcp_client):
    """Test that agent creation loads MCP tools."""
    mock_tools = [MagicMock(name="test_tool")]
    
    with patch("agentic_ai.core.agent_factory.load_mcp_tools") as mock_load_tools:
        mock_load_tools.return_value = mock_tools
        
        await agent_factory.create_agent()
        
        mock_load_tools.assert_called_once()


async def test_close_agent_factory(agent_factory, mock_mcp_client):
    """Test closing agent factory."""
    # First create agent to set up session
    with patch("agentic_ai.core.agent_factory.load_mcp_tools") as mock_load_tools:
        mock_load_tools.return_value = []
        await agent_factory.create_agent()
    
    # Now close
    await agent_factory.close()
    
    # Verify session was closed
    assert agent_factory._mcp_session is None


async def test_agent_factory_reuses_session(agent_factory, mock_mcp_client):
    """Test that agent factory reuses MCP session."""
    with patch("agentic_ai.core.agent_factory.load_mcp_tools") as mock_load_tools:
        mock_load_tools.return_value = []
        
        # Create agent twice
        await agent_factory.create_agent()
        await agent_factory.create_agent()
        
        # Session should only be created once
        assert mock_mcp_client.session.call_count == 1

