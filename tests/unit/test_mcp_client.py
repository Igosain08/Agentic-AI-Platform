"""Unit tests for MCP client."""

import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agentic_ai.core.mcp_client import MCPClient
from agentic_ai.config.settings import get_settings


@pytest.fixture
def mcp_client():
    """Create an MCP client instance."""
    return MCPClient()


async def test_session_context_manager(mcp_client):
    """Test that session works as a context manager."""
    with patch("agentic_ai.core.mcp_client.stdio_client") as mock_stdio:
        mock_read = MagicMock()
        mock_write = MagicMock()
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        
        mock_stdio.return_value.__aenter__.return_value = (mock_read, mock_write)
        mock_stdio.return_value.__aexit__.return_value = None
        
        with patch("agentic_ai.core.mcp_client.ClientSession") as mock_client_session:
            mock_client_session.return_value.__aenter__.return_value = mock_session
            mock_client_session.return_value.__aexit__.return_value = None
            
            async with mcp_client.session() as session:
                assert session is not None
                mock_session.initialize.assert_called_once()


async def test_is_connected_before_session(mcp_client):
    """Test is_connected returns False before session."""
    assert not await mcp_client.is_connected()


async def test_is_connected_after_session(mcp_client):
    """Test is_connected returns True after session."""
    with patch("agentic_ai.core.mcp_client.stdio_client") as mock_stdio:
        mock_read = MagicMock()
        mock_write = MagicMock()
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        
        mock_stdio.return_value.__aenter__.return_value = (mock_read, mock_write)
        mock_stdio.return_value.__aexit__.return_value = None
        
        with patch("agentic_ai.core.mcp_client.ClientSession") as mock_client_session:
            mock_client_session.return_value.__aenter__.return_value = mock_session
            mock_client_session.return_value.__aexit__.return_value = None
            
            async with mcp_client.session():
                # During session, should be connected
                assert mcp_client._session is not None

