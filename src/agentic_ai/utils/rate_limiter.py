"""Rate limiting utilities."""

import time
from collections import defaultdict
from typing import Optional

from agentic_ai.config.settings import get_settings
from agentic_ai.monitoring.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(
        self,
        requests_per_minute: Optional[int] = None,
        enabled: Optional[bool] = None,
    ):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Max requests per minute per key
            enabled: Whether rate limiting is enabled
        """
        self.settings = get_settings()
        self._enabled = (
            enabled if enabled is not None else self.settings.rate_limit_enabled
        )
        self._requests_per_minute = (
            requests_per_minute
            if requests_per_minute is not None
            else self.settings.rate_limit_requests_per_minute
        )
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> tuple[bool, Optional[int]]:
        """Check if request is allowed.

        Args:
            key: Rate limit key (e.g., user ID, IP address)

        Returns:
            Tuple of (is_allowed, seconds_until_next_allowed)
        """
        if not self._enabled:
            return True, None

        now = time.time()
        window_start = now - 60  # Last 60 seconds

        # Clean old requests
        self._requests[key] = [
            req_time
            for req_time in self._requests[key]
            if req_time > window_start
        ]

        # Check limit
        if len(self._requests[key]) >= self._requests_per_minute:
            # Calculate when next request will be allowed
            oldest_request = min(self._requests[key])
            next_allowed = int(oldest_request + 60 - now) + 1
            return False, next_allowed

        # Record request
        self._requests[key].append(now)
        return True, None

    def reset(self, key: str) -> None:
        """Reset rate limit for a key.

        Args:
            key: Rate limit key
        """
        if key in self._requests:
            del self._requests[key]

    def clear(self) -> None:
        """Clear all rate limit data."""
        self._requests.clear()

