"""Caching utilities with Redis support."""

import hashlib
import json
from typing import Any, Optional

import redis.asyncio as redis
from tenacity import retry, stop_after_attempt, wait_exponential

from agentic_ai.config.settings import get_settings
from agentic_ai.monitoring.logging import get_logger
from agentic_ai.monitoring.metrics import get_metrics

logger = get_logger(__name__)


class CacheManager:
    """Manages caching with Redis backend."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize cache manager.

        Args:
            redis_client: Optional Redis client. If None, creates from settings.
        """
        self.settings = get_settings()
        self.redis_client = redis_client
        self._enabled = self.settings.cache_enabled
        self._ttl = self.settings.cache_ttl_seconds
        self.metrics = get_metrics()

    async def _get_client(self) -> Optional[redis.Redis]:
        """Get or create Redis client.

        Returns:
            Redis client or None if caching is disabled
        """
        if not self._enabled:
            return None

        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(
                    f"redis://{self.settings.redis_host}:{self.settings.redis_port}",
                    db=self.settings.redis_db,
                    password=self.settings.redis_password,
                    decode_responses=True,
                )
                logger.info("Redis client connected")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Caching disabled.")
                self._enabled = False
                return None

        return self.redis_client

    def _generate_key(self, prefix: str, *args: Any) -> str:
        """Generate cache key from arguments.

        Args:
            prefix: Key prefix
            *args: Arguments to hash into key

        Returns:
            Cache key string
        """
        key_data = json.dumps(args, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def get(self, prefix: str, *args: Any) -> Optional[Any]:
        """Get value from cache.

        Args:
            prefix: Key prefix
            *args: Arguments used to generate key

        Returns:
            Cached value or None if not found
        """
        if not self._enabled:
            return None

        client = await self._get_client()
        if client is None:
            return None

        try:
            key = self._generate_key(prefix, *args)
            value = await client.get(key)
            if value:
                self.metrics.record_cache_hit(prefix)
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(value)
            else:
                self.metrics.record_cache_miss(prefix)
                logger.debug(f"Cache miss for key: {key}")
                return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def set(
        self, prefix: str, value: Any, ttl: Optional[int] = None, *args: Any
    ) -> bool:
        """Set value in cache.

        Args:
            prefix: Key prefix
            value: Value to cache
            ttl: Optional TTL in seconds (uses default if None)
            *args: Arguments used to generate key

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False

        client = await self._get_client()
        if client is None:
            return False

        try:
            key = self._generate_key(prefix, *args)
            serialized = json.dumps(value, default=str)
            ttl = ttl or self._ttl
            await client.setex(key, ttl, serialized)
            logger.debug(f"Cached value for key: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    async def delete(self, prefix: str, *args: Any) -> bool:
        """Delete value from cache.

        Args:
            prefix: Key prefix
            *args: Arguments used to generate key

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False

        client = await self._get_client()
        if client is None:
            return False

        try:
            key = self._generate_key(prefix, *args)
            await client.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False

    async def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with given prefix.

        Args:
            prefix: Key prefix to clear

        Returns:
            Number of keys deleted
        """
        if not self._enabled:
            return 0

        client = await self._get_client()
        if client is None:
            return 0

        try:
            pattern = f"{prefix}:*"
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await client.delete(*keys)
                logger.info(f"Cleared {deleted} keys with prefix: {prefix}")
                return deleted
            return 0
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return 0

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis client closed")

