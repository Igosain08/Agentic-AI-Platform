"""Prometheus metrics collection."""

import asyncio
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable

from prometheus_client import Counter, Gauge, Histogram

from agentic_ai.config.settings import get_settings
from agentic_ai.monitoring.logging import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collects and exposes Prometheus metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.settings = get_settings()
        self._enabled = self.settings.metrics_enabled

        if not self._enabled:
            logger.info("Metrics collection disabled")
            return

        # Request metrics
        self.request_count = Counter(
            "agentic_ai_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status"],
        )

        self.request_duration = Histogram(
            "agentic_ai_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
        )

        # Agent metrics
        self.agent_queries = Counter(
            "agentic_ai_agent_queries_total",
            "Total number of agent queries",
            ["agent_type", "status"],
        )

        self.agent_query_duration = Histogram(
            "agentic_ai_agent_query_duration_seconds",
            "Agent query duration in seconds",
            ["agent_type"],
        )

        # Tool metrics
        self.tool_calls = Counter(
            "agentic_ai_tool_calls_total",
            "Total number of tool calls",
            ["tool_name", "status"],
        )

        self.tool_call_duration = Histogram(
            "agentic_ai_tool_call_duration_seconds",
            "Tool call duration in seconds",
            ["tool_name"],
        )

        # Cache metrics
        self.cache_hits = Counter(
            "agentic_ai_cache_hits_total",
            "Total number of cache hits",
            ["cache_type"],
        )

        self.cache_misses = Counter(
            "agentic_ai_cache_misses_total",
            "Total number of cache misses",
            ["cache_type"],
        )

        # System metrics
        self.active_connections = Gauge(
            "agentic_ai_active_connections",
            "Number of active connections",
        )

        self.active_threads = Gauge(
            "agentic_ai_active_threads",
            "Number of active conversation threads",
        )

        # Custom metrics: Embedding Latency vs LLM Generation Latency
        # This is the "Senior Engineer" move - tracking which part of pipeline is slow
        self.embedding_latency = Histogram(
            "agentic_ai_embedding_latency_seconds",
            "Time spent on embedding/vector operations (RAG retrieval)",
            ["operation_type"],  # e.g., "query_embedding", "document_embedding"
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0),
        )

        self.llm_generation_latency = Histogram(
            "agentic_ai_llm_generation_latency_seconds",
            "Time spent on LLM generation (text generation)",
            ["model", "operation_type"],  # e.g., "completion", "chat"
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0),
        )

        # Pipeline breakdown: Total query time breakdown
        self.pipeline_stage_duration = Histogram(
            "agentic_ai_pipeline_stage_duration_seconds",
            "Duration of different pipeline stages",
            ["stage"],  # e.g., "embedding", "llm_generation", "tool_execution", "total"
            buckets=(0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0),
        )

        logger.info("Metrics collector initialized")

    def record_request(
        self, method: str, endpoint: str, status: str, duration: float
    ) -> None:
        """Record HTTP request metrics.

        Args:
            method: HTTP method
            endpoint: API endpoint
            status: Response status code
            duration: Request duration in seconds
        """
        if not self._enabled:
            return

        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_agent_query(
        self, agent_type: str, status: str, duration: float
    ) -> None:
        """Record agent query metrics.

        Args:
            agent_type: Type of agent used
            status: Query status (success, error)
            duration: Query duration in seconds
        """
        if not self._enabled:
            return

        self.agent_queries.labels(agent_type=agent_type, status=status).inc()
        self.agent_query_duration.labels(agent_type=agent_type).observe(duration)

    def record_tool_call(
        self, tool_name: str, status: str, duration: float
    ) -> None:
        """Record tool call metrics.

        Args:
            tool_name: Name of the tool
            status: Call status (success, error)
            duration: Call duration in seconds
        """
        if not self._enabled:
            return

        self.tool_calls.labels(tool_name=tool_name, status=status).inc()
        self.tool_call_duration.labels(tool_name=tool_name).observe(duration)

    def record_cache_hit(self, cache_type: str) -> None:
        """Record cache hit.

        Args:
            cache_type: Type of cache (query, tool_response, etc.)
        """
        if not self._enabled:
            return

        self.cache_hits.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str) -> None:
        """Record cache miss.

        Args:
            cache_type: Type of cache (query, tool_response, etc.)
        """
        if not self._enabled:
            return

        self.cache_misses.labels(cache_type=cache_type).inc()

    @contextmanager
    def track_connection(self):
        """Context manager to track active connections."""
        if not self._enabled:
            yield
            return

        self.active_connections.inc()
        try:
            yield
        finally:
            self.active_connections.dec()

    def set_active_threads(self, count: int) -> None:
        """Set the number of active conversation threads.

        Args:
            count: Number of active threads
        """
        if not self._enabled:
            return

        self.active_threads.set(count)

    def record_embedding_latency(self, duration: float, operation_type: str = "query_embedding") -> None:
        """Record embedding/vector operation latency.

        Args:
            duration: Duration in seconds
            operation_type: Type of embedding operation (e.g., "query_embedding", "document_embedding")
        """
        if not self._enabled:
            return

        self.embedding_latency.labels(operation_type=operation_type).observe(duration)

    def record_llm_generation_latency(
        self, duration: float, model: str = "unknown", operation_type: str = "completion"
    ) -> None:
        """Record LLM generation latency.

        Args:
            duration: Duration in seconds
            model: Model name (e.g., "gpt-4o-mini", "claude-3")
            operation_type: Type of operation (e.g., "completion", "chat")
        """
        if not self._enabled:
            return

        self.llm_generation_latency.labels(model=model, operation_type=operation_type).observe(duration)

    def record_pipeline_stage(self, duration: float, stage: str) -> None:
        """Record pipeline stage duration.

        Args:
            duration: Duration in seconds
            stage: Pipeline stage name (e.g., "embedding", "llm_generation", "tool_execution", "total")
        """
        if not self._enabled:
            return

        self.pipeline_stage_duration.labels(stage=stage).observe(duration)


# Global metrics collector instance
_metrics_collector: MetricsCollector | None = None


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector instance.

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def track_execution_time(metric_name: str):
    """Decorator to track function execution time.

    Args:
        metric_name: Name of the metric to record
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                get_metrics().record_tool_call(metric_name, "success", duration)
                return result
            except Exception:
                duration = time.time() - start_time
                get_metrics().record_tool_call(metric_name, "error", duration)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                get_metrics().record_tool_call(metric_name, "success", duration)
                return result
            except Exception:
                duration = time.time() - start_time
                get_metrics().record_tool_call(metric_name, "error", duration)
                raise

        try:
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
        except (AttributeError, TypeError):
            # Fallback for non-async functions
            pass
        return sync_wrapper

    return decorator

