"""FastAPI dependencies."""

from typing import TYPE_CHECKING

from fastapi import HTTPException, status

if TYPE_CHECKING:
    from agentic_ai.utils.cache import CacheManager
    from agentic_ai.utils.rate_limiter import RateLimiter

# Import after main module is initialized to avoid circular import
_cache_manager = None
_rate_limiter = None


def set_dependencies(cache_mgr, rate_limit):
    """Set dependency instances (called from main module)."""
    global _cache_manager, _rate_limiter
    _cache_manager = cache_mgr
    _rate_limiter = rate_limit


def get_cache_manager() -> "CacheManager":
    """Get cache manager instance."""
    if _cache_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache manager not initialized",
        )
    return _cache_manager


def get_rate_limiter() -> "RateLimiter":
    """Get rate limiter instance."""
    if _rate_limiter is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiter not initialized",
        )
    return _rate_limiter

