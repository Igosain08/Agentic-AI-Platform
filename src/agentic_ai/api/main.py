"""FastAPI application main module."""

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_fastapi_instrumentator import Instrumentator

from agentic_ai.api.dependencies import set_dependencies
from agentic_ai.api.routes import conversation, health, query
from agentic_ai.config.settings import get_settings
from agentic_ai.monitoring.logging import get_logger
from agentic_ai.monitoring.metrics import get_metrics
from agentic_ai.utils.cache import CacheManager
from agentic_ai.utils.rate_limiter import RateLimiter

logger = get_logger(__name__)
settings = get_settings()

# Global instances
cache_manager: CacheManager | None = None
rate_limiter: RateLimiter | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global cache_manager, rate_limiter

    # Startup
    logger.info("Starting application")
    logger.info(f"Couchbase bucket: {settings.cb_bucket_name}")
    logger.info(f"MCP server path: {settings.mcp_server_path}")
    global cache_manager, rate_limiter
    cache_manager = CacheManager()
    rate_limiter = RateLimiter()
    set_dependencies(cache_manager, rate_limiter)
    logger.info("Application started")

    yield

    # Shutdown
    logger.info("Shutting down application")
    if cache_manager:
        await cache_manager.close()
    logger.info("Application shut down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready agentic AI platform with multi-agent orchestration",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus instrumentation - automatically exposes /metrics endpoint
# This provides standard HTTP metrics (request count, duration, etc.)
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health", "/api/v1/health"],
    inprogress_name="agentic_ai_requests_inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app)


# Request timing middleware
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """Middleware to track request timing."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # Record metrics
    metrics = get_metrics()
    status_code = str(response.status_code)
    metrics.record_request(
        method=request.method,
        endpoint=request.url.path,
        status=status_code,
        duration=duration,
    )

    # Add timing header
    response.headers["X-Process-Time"] = str(duration)
    return response


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware for rate limiting."""
    if rate_limiter and not request.url.path.startswith("/health"):
        # Use client IP as rate limit key
        client_ip = request.client.host if request.client else "unknown"
        allowed, retry_after = rate_limiter.is_allowed(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

    return await call_next(request)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# Include routers
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(conversation.router, prefix="/api/v1", tags=["conversation"])


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


# Dependencies are now in dependencies.py to avoid circular imports

