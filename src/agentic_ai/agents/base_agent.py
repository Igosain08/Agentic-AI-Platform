"""Base agent class for specialized agents."""

import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.monitoring.logging import get_logger
from agentic_ai.monitoring.metrics import get_metrics
from agentic_ai.utils.cache import CacheManager

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Base class for specialized agents."""

    def __init__(
        self,
        agent_factory: AgentFactory,
        cache_manager: Optional[CacheManager] = None,
        agent_type: str = "base",
    ):
        """Initialize base agent.

        Args:
            agent_factory: Factory for creating agents
            cache_manager: Optional cache manager
            agent_type: Type identifier for this agent
        """
        self.agent_factory = agent_factory
        self.cache_manager = cache_manager
        self.agent_type = agent_type
        self.metrics = get_metrics()
        self._agent: Optional[Any] = None

    async def _get_agent(self) -> Any:
        """Get or create the agent instance.

        Returns:
            LangGraph agent instance
        """
        if self._agent is None:
            logger.info("Creating new agent instance...")
            try:
                self._agent = await self.agent_factory.create_agent()
                logger.info("Agent created successfully")
            except Exception as e:
                logger.error(f"Failed to create agent: {e}", exc_info=True)
                raise
        return self._agent

    @abstractmethod
    async def process(self, message: str, thread_id: str, **kwargs: Any) -> dict[str, Any]:
        """Process a message with this agent.

        Args:
            message: User message
            thread_id: Conversation thread ID
            **kwargs: Additional parameters

        Returns:
            Response dictionary with 'response' and 'metadata' keys
        """
        pass

    async def _execute_query(
        self, message: str, thread_id: str, use_cache: bool = True
    ) -> dict[str, Any]:
        """Execute a query with the agent.

        Args:
            message: User message
            thread_id: Conversation thread ID
            use_cache: Whether to use cache

        Returns:
            Response dictionary
        """
        start_time = time.time()
        config = {"configurable": {"thread_id": thread_id}}

        # Check cache
        cache_key = (message, thread_id)
        if use_cache and self.cache_manager:
            cached = await self.cache_manager.get("agent_response", *cache_key)
            if cached:
                logger.info(f"Cache hit for query: {message[:50]}...")
                return cached

        try:
            agent = await self._get_agent()
            # LangGraph expects messages as a list
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=message)]
            
            # Add timeout to prevent hanging
            import asyncio
            try:
                logger.debug(f"Invoking agent with message: {message[:100]}...")
                result = await asyncio.wait_for(
                    agent.ainvoke({"messages": messages}, config),
                    timeout=60.0  # 60 second timeout
                )
                logger.debug(f"Agent execution completed. Messages: {len(result.get('messages', []))}")
                
                # Check for tool call errors
                for msg in result.get("messages", []):
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        logger.debug(f"Found tool calls: {[tc.get('name') for tc in msg.tool_calls]}")
                    if hasattr(msg, 'content') and 'error' in str(msg.content).lower():
                        logger.warning(f"Tool execution error in message: {msg.content[:200]}")
                        
            except asyncio.TimeoutError:
                logger.error("Agent execution timed out after 60 seconds")
                raise Exception("Agent execution timed out. The query may be too complex or MCP server is not responding.")
            except Exception as e:
                logger.error(f"Agent execution failed: {e}", exc_info=True)
                raise
            
            response_content = result["messages"][-1].content

            response = {
                "response": response_content,
                "metadata": {
                    "agent_type": self.agent_type,
                    "thread_id": thread_id,
                    "execution_time_ms": int((time.time() - start_time) * 1000),
                    "cache_hit": False,
                },
            }

            # Cache response
            if use_cache and self.cache_manager:
                await self.cache_manager.set("agent_response", response, *cache_key)

            duration = time.time() - start_time
            self.metrics.record_agent_query(self.agent_type, "success", duration)

            return response

        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_agent_query(self.agent_type, "error", duration)
            logger.error(f"Agent query failed: {e}", exc_info=True)
            raise

