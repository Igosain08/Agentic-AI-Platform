"""Query agent for handling database queries."""

from typing import Any, Optional

from agentic_ai.agents.base_agent import BaseAgent
from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.utils.cache import CacheManager


class QueryAgent(BaseAgent):
    """Specialized agent for database queries."""

    def __init__(
        self,
        agent_factory: AgentFactory,
        cache_manager: Optional[CacheManager] = None,
    ):
        """Initialize query agent.

        Args:
            agent_factory: Factory for creating agents
            cache_manager: Optional cache manager
        """
        super().__init__(agent_factory, cache_manager, agent_type="query")

    async def process(
        self, message: str, thread_id: str, use_cache: bool = True, **kwargs: Any
    ) -> dict[str, Any]:
        """Process a database query.

        Args:
            message: User message
            thread_id: Conversation thread ID
            use_cache: Whether to use cache
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        return await self._execute_query(message, thread_id, use_cache=use_cache)

