"""Tests for rate limiter."""

import pytest
import time

from agentic_ai.utils.rate_limiter import RateLimiter


def test_rate_limiter_allows_requests():
    """Test rate limiter allows requests under limit."""
    limiter = RateLimiter(requests_per_minute=10, enabled=True)
    allowed, _ = limiter.is_allowed("test_key")
    assert allowed is True


def test_rate_limiter_blocks_excess():
    """Test rate limiter blocks excess requests."""
    limiter = RateLimiter(requests_per_minute=2, enabled=True)
    
    # Make 2 requests (should be allowed)
    allowed1, _ = limiter.is_allowed("test_key")
    allowed2, _ = limiter.is_allowed("test_key")
    
    # Third request should be blocked
    allowed3, retry_after = limiter.is_allowed("test_key")
    
    assert allowed1 is True
    assert allowed2 is True
    assert allowed3 is False
    assert retry_after is not None


def test_rate_limiter_disabled():
    """Test rate limiter when disabled."""
    limiter = RateLimiter(enabled=False)
    allowed, _ = limiter.is_allowed("test_key")
    assert allowed is True

