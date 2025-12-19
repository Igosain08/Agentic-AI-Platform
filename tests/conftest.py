"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from agentic_ai.config.settings import Settings
from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.core.mcp_client import MCPClient
from agentic_ai.utils.cache import CacheManager


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    settings = Settings(
        NEBIUS_API_KEY="test_key",
        CB_CONNECTION_STRING="couchbase://localhost",
        CB_USERNAME="test_user",
        CB_PASSWORD="test_pass",
        CB_BUCKET_NAME="test_bucket",
        MCP_SERVER_PATH="/test/path",
        environment="test",
    )
    monkeypatch.setattr("agentic_ai.config.settings.get_settings", lambda: settings)
    return settings


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client."""
    client = MagicMock(spec=MCPClient)
    client.session = AsyncMock()
    return client


@pytest.fixture
def mock_cache_manager():
    """Mock cache manager."""
    manager = MagicMock(spec=CacheManager)
    manager.get = AsyncMock(return_value=None)
    manager.set = AsyncMock(return_value=True)
    manager.delete = AsyncMock(return_value=True)
    return manager


@pytest.fixture
def mock_agent_factory(mock_mcp_client):
    """Mock agent factory."""
    factory = MagicMock(spec=AgentFactory)
    factory.create_agent = AsyncMock()
    factory.mcp_client = mock_mcp_client
    return factory


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = MagicMock()
    client.chat.completions.create = MagicMock()
    return client


@pytest.fixture
def mock_couchbase_cluster():
    """Mock Couchbase cluster for testing."""
    cluster = MagicMock()
    cluster.bucket = MagicMock()
    return cluster


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    client = MagicMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=True)
    return client

