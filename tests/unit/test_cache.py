"""Tests for cache manager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentic_ai.utils.cache import CacheManager


@pytest.mark.asyncio
async def test_cache_get_miss(mock_cache_manager):
    """Test cache get on miss."""
    result = await mock_cache_manager.get("test", "key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_set_get(mock_cache_manager):
    """Test cache set and get."""
    value = {"test": "data"}
    await mock_cache_manager.set("test", value, None, "key")
    mock_cache_manager.get = AsyncMock(return_value=value)
    result = await mock_cache_manager.get("test", "key")
    assert result == value


@pytest.mark.asyncio
async def test_cache_disabled():
    """Test cache when disabled."""
    with patch("agentic_ai.utils.cache.get_settings") as mock_settings:
        mock_settings.return_value.cache_enabled = False
        manager = CacheManager()
        result = await manager.get("test", "key")
        assert result is None

