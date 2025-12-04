"""MCP (Model Context Protocol) client for connecting to MCP servers."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agentic_ai.config.settings import get_settings
from agentic_ai.monitoring.logging import get_logger

logger = get_logger(__name__)


class MCPClient:
    """Client for managing MCP server connections."""

    def __init__(self, server_params: StdioServerParameters | None = None):
        """Initialize MCP client.

        Args:
            server_params: Optional custom server parameters. If None, uses default from settings.
        """
        self.settings = get_settings()
        self.server_params = server_params or self._create_server_params()
        self._session: ClientSession | None = None
        self._read = None
        self._write = None

    def _create_server_params(self) -> StdioServerParameters:
        """Create server parameters from settings."""
        return StdioServerParameters(
            command="uv",
            args=[
                "--directory",
                self.settings.mcp_server_path,
                "run",
                "src/mcp_server.py",
            ],
            env=self.settings.couchbase_env,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[ClientSession]:
        """Get an MCP session context manager.

        Yields:
            ClientSession: Active MCP session
        """
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self._session = session
                self._read = read
                self._write = write
                try:
                    logger.info("Initializing MCP connection")
                    await session.initialize()
                    logger.info("MCP connection established")
                    yield session
                finally:
                    logger.info("Closing MCP connection")
                    self._session = None
                    self._read = None
                    self._write = None

    async def is_connected(self) -> bool:
        """Check if MCP client is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._session is not None

