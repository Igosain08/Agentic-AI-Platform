"""Base agent class for specialized agents."""

import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from agentic_ai.config.settings import get_settings
from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.monitoring.logging import get_logger
from agentic_ai.monitoring.metrics import get_metrics
from agentic_ai.monitoring.mlflow_tracker import get_mlflow_tracker
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
        self.mlflow_tracker = get_mlflow_tracker()
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

        # Log to MLflow if enabled (for individual queries, we log metrics without a run context)
        # Run context should be managed at a higher level (e.g., evaluation script)

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
            
            # Add timeout to prevent hanging - increased for database queries
            import asyncio
            
            # Track pipeline stages for Prometheus metrics
            llm_generation_time = 0.0
            tool_execution_time = 0.0
            
            try:
                logger.debug(f"Invoking agent with message: {message[:100]}...")
                
                # Track LLM generation time (this is the actual LLM call)
                llm_start = time.time()
                # Increased timeout to 120 seconds for database operations
                result = await asyncio.wait_for(
                    agent.ainvoke({"messages": messages}, config),
                    timeout=120.0  # 120 second timeout for database queries
                )
                llm_generation_time = time.time() - llm_start
                
                logger.debug(f"Agent execution completed. Messages: {len(result.get('messages', []))}")
                
                # Track tool execution time (database queries via MCP tools)
                # This is the "embedding/retrieval" equivalent - time spent querying database
                tool_start = time.time()
                for msg in result.get("messages", []):
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        logger.debug(f"Found tool calls: {[tc.get('name') for tc in msg.tool_calls]}")
                        # Estimate tool execution time (in real implementation, would track actual tool calls)
                        # For now, we'll approximate: total time - LLM time = tool time
                    if hasattr(msg, 'content') and 'error' in str(msg.content).lower():
                        logger.warning(f"Tool execution error in message: {msg.content[:200]}")
                
                # Approximate tool execution time (database queries)
                # In a more sophisticated implementation, we'd track each tool call separately
                total_time = time.time() - start_time
                tool_execution_time = max(0, total_time - llm_generation_time - 0.1)  # Subtract small overhead
                
                # Record custom metrics for pipeline breakdown
                settings = get_settings()
                model_name = getattr(settings, 'llm_model', 'unknown')
                self.metrics.record_llm_generation_latency(llm_generation_time, model=model_name, operation_type="chat")
                self.metrics.record_embedding_latency(tool_execution_time, operation_type="database_query")
                self.metrics.record_pipeline_stage(llm_generation_time, stage="llm_generation")
                self.metrics.record_pipeline_stage(tool_execution_time, stage="tool_execution")
                self.metrics.record_pipeline_stage(total_time, stage="total")
                        
            except asyncio.TimeoutError:
                logger.error("Agent execution timed out after 120 seconds")
                raise Exception("Query timed out. This may be due to: 1) Couchbase connection issues (check IP whitelist), 2) Network latency, or 3) Complex query. Try a simpler query or check Couchbase credentials.")
            except Exception as e:
                logger.error(f"Agent execution failed: {e}", exc_info=True)
                # Extract more detailed error message
                error_msg = str(e)
                
                # Handle LangGraph tool call errors specifically
                if "INVALID_CHAT_HISTORY" in error_msg or "tool_calls" in error_msg or "ToolMessage" in error_msg:
                    logger.error("LangGraph tool call error - tool execution may have failed")
                    raise Exception(
                        "Query failed: Tool execution error. This usually means:\n"
                        "1. MCP server connection failed or timed out\n"
                        "2. Couchbase query service is unavailable\n"
                        "3. Database connection credentials are incorrect\n\n"
                        "Please check:\n"
                        "- Couchbase connection string and credentials\n"
                        "- MCP server is running and accessible\n"
                        "- Network connectivity to Couchbase\n"
                        f"Original error: {error_msg[:200]}"
                    )
                # Check for specific error patterns to provide better guidance
                elif "Service unavailable" in error_msg or "ServiceUnavailableException" in error_msg:
                    # Error already contains helpful message from MCP tool
                    raise Exception(f"Query failed: {error_msg}")
                elif "TaskGroup" in error_msg or "Connection" in error_msg or "timeout" in error_msg.lower():
                    error_msg = "Database connection failed. Possible causes: 1) Railway IP not whitelisted in Couchbase Capella, 2) Incorrect credentials, 3) Network connectivity issues. Check Couchbase Capella → Network → Allowed IPs and add Railway's IP addresses."
                    raise Exception(f"Query failed: {error_msg}")
                else:
                    raise Exception(f"Query failed: {error_msg}")
            
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

            # Log to MLflow if enabled
            if self.mlflow_tracker.is_enabled:
                self.mlflow_tracker.log_latency(duration)
                # Log individual query metrics if there's an active run
                try:
                    from mlflow import active_run
                    if active_run():
                        self.mlflow_tracker.log_metric("query_latency_ms", duration * 1000)
                        self.mlflow_tracker.log_metric("query_success", 1)
                        self.mlflow_tracker.log_metric("query_response_length", len(response_content))
                except Exception:
                    pass  # Non-blocking - don't fail if MLflow logging fails

            return response

        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_agent_query(self.agent_type, "error", duration)
            
            # Log error to MLflow if enabled
            if self.mlflow_tracker.is_enabled:
                try:
                    from mlflow import active_run
                    if active_run():
                        self.mlflow_tracker.log_metric("query_latency_ms", duration * 1000)
                        self.mlflow_tracker.log_metric("query_success", 0)
                except Exception:
                    pass  # Non-blocking
            
            logger.error(f"Agent query failed: {e}", exc_info=True)
            raise

