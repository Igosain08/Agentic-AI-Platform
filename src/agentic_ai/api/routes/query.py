"""Query API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from agentic_ai.api.dependencies import get_cache_manager
from agentic_ai.agents.orchestrator import AgentOrchestrator
from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.monitoring.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    """Query request model."""

    message: str = Field(..., description="Natural language query", min_length=1, max_length=5000)
    thread_id: str = Field(..., description="Conversation thread ID", min_length=1)
    agent_type: str = Field(
        default="auto",
        description="Type of agent to use (auto, query, data, format)",
    )
    use_cache: bool = Field(default=True, description="Whether to use response caching")


class QueryResponse(BaseModel):
    """Query response model."""

    response: str = Field(..., description="Agent response")
    thread_id: str = Field(..., description="Conversation thread ID")
    metadata: dict = Field(..., description="Response metadata")


# Global orchestrator instance (in production, use dependency injection)
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create agent orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        agent_factory = AgentFactory()
        cache_manager = get_cache_manager()
        _orchestrator = AgentOrchestrator(agent_factory, cache_manager)
    return _orchestrator


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_agent(request: QueryRequest) -> QueryResponse:
    """Submit a query to the agent system.

    Args:
        request: Query request

    Returns:
        Agent response
    """
    try:
        logger.info(
            f"Received query: thread_id={request.thread_id}, "
            f"agent_type={request.agent_type}"
        )

        orchestrator = get_orchestrator()
        result = await orchestrator.process(
            message=request.message,
            thread_id=request.thread_id,
            agent_type=request.agent_type,
            use_cache=request.use_cache,
        )

        return QueryResponse(
            response=result["response"],
            thread_id=result["metadata"]["thread_id"],
            metadata=result["metadata"],
        )

    except Exception as e:
        logger.error(f"Query processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}",
        )

