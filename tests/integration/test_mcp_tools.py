"""Integration tests for MCP tools."""

import pytest
from unittest.mock import patch, AsyncMock

from agentic_ai.core.mcp_client import MCPClient
from agentic_ai.core.agent_factory import AgentFactory


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mcp_tools_load():
    """Test that MCP tools can be loaded."""
    # Skip if MCP server not configured
    import os
    if not os.getenv("MCP_SERVER_PATH"):
        pytest.skip("MCP_SERVER_PATH not set")
    
    client = MCPClient()
    factory = AgentFactory(mcp_client=client)
    
    try:
        agent = await factory.create_agent()
        assert agent is not None
    finally:
        await factory.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_with_mcp_tools():
    """Test agent can be created with MCP tools."""
    # Skip if MCP server not configured
    import os
    if not os.getenv("MCP_SERVER_PATH"):
        pytest.skip("MCP_SERVER_PATH not set")
    
    client = MCPClient()
    factory = AgentFactory(mcp_client=client)
    
    try:
        agent = await factory.create_agent()
        
        # Verify agent has tools
        # This is a basic smoke test
        assert agent is not None
    finally:
        await factory.close()

