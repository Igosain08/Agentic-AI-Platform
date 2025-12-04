"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel

from agentic_ai.config.settings import get_settings
from agentic_ai.core.mcp_client import MCPClient
from agentic_ai.monitoring.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    environment: str
    checks: dict


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        Health status
    """
    checks = {
        "api": "healthy",
    }

    # Check MCP connection (async check)
    try:
        mcp_client = MCPClient()
        # Note: This is a simple check. In production, you might want
        # to maintain a persistent connection pool
        checks["mcp"] = "configured"
    except Exception as e:
        logger.warning(f"MCP health check failed: {e}")
        checks["mcp"] = "error"

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        checks=checks,
    )


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness check endpoint for Kubernetes.

    Returns:
        Readiness status
    """
    # Add more sophisticated readiness checks here
    return {"status": "ready"}


@router.get("/live")
async def liveness_check() -> dict:
    """Liveness check endpoint for Kubernetes.

    Returns:
        Liveness status
    """
    return {"status": "alive"}

