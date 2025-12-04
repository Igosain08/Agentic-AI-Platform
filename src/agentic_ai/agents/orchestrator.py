"""Agent orchestrator for coordinating multiple specialized agents."""

from typing import Any, Optional

from agentic_ai.agents.base_agent import BaseAgent
from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.monitoring.logging import get_logger
from agentic_ai.utils.cache import CacheManager

logger = get_logger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple specialized agents for complex queries."""

    def __init__(
        self,
        agent_factory: AgentFactory,
        cache_manager: Optional[CacheManager] = None,
    ):
        """Initialize agent orchestrator.

        Args:
            agent_factory: Factory for creating agents
            cache_manager: Optional cache manager
        """
        self.agent_factory = agent_factory
        self.cache_manager = cache_manager
        self._default_agent: Optional[BaseAgent] = None

    async def _get_default_agent(self) -> BaseAgent:
        """Get or create default agent.

        Returns:
            Default agent instance
        """
        if self._default_agent is None:
            from agentic_ai.agents.query_agent import QueryAgent

            self._default_agent = QueryAgent(
                self.agent_factory, self.cache_manager
            )
        return self._default_agent

    async def process(
        self,
        message: str,
        thread_id: str,
        agent_type: str = "auto",
        use_cache: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Process a query using appropriate agent(s).

        Args:
            message: User message
            thread_id: Conversation thread ID
            agent_type: Type of agent to use ('auto', 'query', 'data', 'format')
            use_cache: Whether to use cache

        Returns:
            Response dictionary
        """
        logger.info(f"Processing query with agent_type={agent_type}")

        # For now, use default agent. In future, can add routing logic
        # based on query complexity, type, etc.
        agent = await self._get_default_agent()
        return await agent.process(message, thread_id, use_cache=use_cache, **kwargs)

