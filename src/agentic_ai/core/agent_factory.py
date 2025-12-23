"""Factory for creating and managing AI agents."""

from functools import wraps
from typing import Any, Type

from langchain_core.tools import BaseTool, StructuredTool
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from agentic_ai.config.settings import get_settings
from agentic_ai.core.mcp_client import MCPClient
from agentic_ai.monitoring.logging import get_logger

logger = get_logger(__name__)


class AgentFactory:
    """Factory for creating ReAct agents with MCP tools.
    
    Maintains a persistent MCP session that stays alive for tool execution.
    """

    SYSTEM_PROMPT = """Couchbase organizes data with the following hierarchy (from top to bottom):

1. Cluster
   The overall container of all Couchbase data and services.

2. Bucket
   A bucket is similar to a database in traditional systems.
   Each bucket contains multiple scopes.
   Example: "users", "analytics", "products"

3. Scope
   A scope is a namespace within a bucket that groups collections.
   Scopes help isolate data for different microservices or tenants.
   Default scope name: _default

4. Collection
   The equivalent of a table in relational databases.
   Collections store JSON documents.
   Default collection name: _default

5. Document
   The atomic data unit (usually JSON) stored in a collection.
   Each document has a unique key within its collection.

Use the tools to read the database and answer questions based on this database.

**IMPORTANT LIMITATIONS:**
- Your access is limited to the `inventory` scope of the `travel-sample` bucket
- You CANNOT list buckets, scopes, or perform cluster-level operations
- You CAN query collections within the inventory scope

**AVAILABLE DATA:**
- Bucket: `travel-sample`
- Scope: `inventory`
- Collections: `hotel`, `route`, `landmark`, `airport`, `airline`
- IMPORTANT: Use the exact collection names as listed above (e.g., `hotel` not `hotels`)

**DATA STRUCTURE GUIDE:**
- **Routes**: Use airport codes (e.g., "JFK", "LHR", "LAX"), NOT city names. Fields: `sourceairport`, `destinationairport`, `airline`, `distance`, `stops`
- **Airports**: Contains airport codes and city names. Use this to find airport codes for cities (e.g., "New York" → "JFK", "LGA", "EWR")
- **Hotels**: Fields include `name`, `city`, `country`, `price`, `reviews`, `rating`
- **Airlines**: Contains airline information with codes and names

**QUERY STRATEGY FOR ROUTES:**
When users ask about routes between cities:
1. FIRST: Query the `airport` collection to find airport codes for the cities (e.g., "New York" → find airports with city="New York")
2. THEN: Query the `route` collection using those airport codes in `sourceairport` and `destinationairport` fields
3. Example: For "routes from New York to London":
   - Find airports: `SELECT airportname, faa FROM airport WHERE city = 'New York'`
   - Then find routes: `SELECT * FROM route WHERE sourceairport IN ('JFK', 'LGA', 'EWR') AND destinationairport IN ('LHR', 'LGW', 'STN')`

**QUERY GUIDELINES:**
- Any query you generate needs to have only the collection name in the FROM clause
- Every field, collection, scope or bucket name inside the query should be inside backticks
- For route queries, ALWAYS use airport codes, not city names
- If a tool returns an error, use the error message to understand what went wrong and try a different approach

**WHEN USERS ASK ABOUT THINGS YOU CAN'T DO:**
- Clearly explain your limitations (e.g., "I cannot list buckets as my access is limited to the inventory scope")
- Suggest what you CAN help with instead (e.g., "I can help you query hotels, routes, landmarks, airports, or airlines in the travel-sample database")

**WHEN ANSWERING QUESTIONS:**
- Be precise and data-driven
- Format responses clearly with proper structure
- Include relevant metrics and numbers when available
- If data is not available, clearly state that
- For recommendations, provide reasoning based on the data
"""

    def __init__(self, mcp_client: MCPClient | None = None, model: Any = None):
        """Initialize agent factory.

        Args:
            mcp_client: Optional MCP client. If None, creates a new one.
            model: Optional LLM model. If None, creates from settings.
        """
        self.settings = get_settings()
        self.mcp_client = mcp_client or MCPClient()
        self.model = model or self._create_model()
        self._checkpoint = InMemorySaver()
        self._mcp_session_context = None
        self._mcp_session = None
        self._tools = None

    def _create_model(self):
        """Create LLM model from settings."""
        import os
        
        try:
            from langchain_litellm import ChatLiteLLM

            # Set API key based on provider
            provider = self.settings.llm_provider.lower()
            api_key = None
            
            if provider == "openai" and self.settings.openai_api_key:
                os.environ["OPENAI_API_KEY"] = self.settings.openai_api_key
                api_key = self.settings.openai_api_key
                logger.info("Using OpenAI provider")
            elif provider == "nebius" and self.settings.nebius_api_key:
                os.environ["NEBIUS_API_KEY"] = self.settings.nebius_api_key
                api_key = self.settings.nebius_api_key
                logger.info("Using Nebius provider")
            elif provider == "anthropic" and hasattr(self.settings, 'anthropic_api_key'):
                os.environ["ANTHROPIC_API_KEY"] = getattr(self.settings, 'anthropic_api_key', '')
                api_key = getattr(self.settings, 'anthropic_api_key', '')
                logger.info("Using Anthropic provider")
            else:
                # Try to auto-detect from environment
                if os.getenv("OPENAI_API_KEY"):
                    logger.info("Auto-detected OpenAI from environment")
                elif os.getenv("ANTHROPIC_API_KEY"):
                    logger.info("Auto-detected Anthropic from environment")
                else:
                    logger.warning("No API key found, will try to use environment variables")

            # Use effective model (auto-fixes for provider)
            model_name = getattr(self.settings, 'effective_model', self.settings.llm_model)
            
            return ChatLiteLLM(
                model=model_name,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
                api_key=api_key if api_key else None,
            )
        except ImportError:
            logger.warning(
                "langchain_litellm not available, falling back to langchain_community"
            )
            from langchain_community.chat_models import ChatLiteLLM

            return ChatLiteLLM(
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
            )

    async def _ensure_mcp_session(self):
        """Ensure MCP session is open and tools are loaded."""
        # Check if MCP is enabled and path exists
        import os
        if not self.settings.mcp_server_path or not os.path.exists(self.settings.mcp_server_path):
            logger.warning(f"MCP server path not found: {self.settings.mcp_server_path}. Running without MCP tools.")
            self._tools = []
            return
        
        if self._mcp_session is None:
            logger.info("Opening MCP session...")
            try:
                self._mcp_session_context = self.mcp_client.session()
                self._mcp_session = await self._mcp_session_context.__aenter__()
                logger.info("MCP session opened")
            except Exception as e:
                logger.error(f"Failed to open MCP session: {e}", exc_info=True)
                logger.warning("Continuing without MCP tools")
                self._tools = []
                return
            
            # Load tools once - tools are bound to this session
            if self._tools is None:
                logger.info("Loading MCP tools...")
                try:
                    raw_tools = await load_mcp_tools(self._mcp_session)
                    # Wrap tools to ensure they always return results (even on errors)
                    # This prevents "missing ToolMessage" errors in LangGraph
                    self._tools = [self._wrap_tool(tool) for tool in raw_tools]
                    logger.info(f"Loaded {len(self._tools)} MCP tools")
                    # Log tool names for debugging
                    tool_names = [getattr(t, 'name', 'unknown') for t in self._tools]
                    logger.debug(f"MCP tool names: {tool_names[:5]}...")
                except Exception as e:
                    logger.error(f"Failed to load MCP tools: {e}", exc_info=True)
                    logger.warning("Continuing without MCP tools")
                    self._tools = []
    
    def _wrap_tool(self, tool: Any) -> Any:
        """Wrap a tool to ensure it always returns a result, even on errors.
        
        This prevents LangGraph errors about missing ToolMessages when tool execution fails.
        LangGraph requires every tool call to have a corresponding ToolMessage.
        
        Args:
            tool: The tool to wrap
            
        Returns:
            Wrapped tool that always returns a result (never raises)
        """
        # If it's already a BaseTool, wrap its invoke/ainvoke methods
        if isinstance(tool, BaseTool):
            original_invoke = tool.invoke
            original_ainvoke = getattr(tool, 'ainvoke', None)
            
            tool_name = getattr(tool, 'name', 'unknown')
            
            # StructuredTool.invoke() expects: invoke(input: Union[str, dict], config: Optional[RunnableConfig] = None, **kwargs)
            @wraps(original_invoke)
            def safe_invoke(input: Any, config: Any = None, **kwargs: Any):
                try:
                    # Pass input as first positional argument
                    result = original_invoke(input, config=config, **kwargs)
                    return result if result is not None else "Tool executed successfully (no result returned)"
                except Exception as e:
                    logger.error(f"Tool {tool_name} execution failed: {e}", exc_info=True)
                    # Return error as string - LangChain will convert to ToolMessage
                    # This ensures LangGraph always gets a ToolMessage, even on errors
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    if "connection" in str(e).lower() or "timeout" in str(e).lower():
                        error_msg += "\n\nThis may be a database connection issue. Check Couchbase credentials and network connectivity."
                    return error_msg
            
            # Also wrap coroutine for async execution
            # The 'coroutine' parameter for StructuredTool should be a simple function that takes input
            # StructuredTool's ainvoke() will handle config and kwargs internally
            async def safe_coroutine(input: Any):
                """Coroutine wrapper that handles errors and always returns a result."""
                try:
                    # Get the original coroutine from the tool
                    # If the tool has an original coroutine, use it; otherwise fallback to sync invoke
                    if original_ainvoke:
                        # Call ainvoke with the input - StructuredTool will handle config internally
                        result = await original_ainvoke(input)
                    else:
                        # Fallback to sync invoke
                        result = original_invoke(input)
                    return result if result is not None else "Tool executed successfully (no result returned)"
                except Exception as e:
                    logger.error(f"Tool {tool_name} execution failed: {e}", exc_info=True)
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    if "connection" in str(e).lower() or "timeout" in str(e).lower():
                        error_msg += "\n\nThis may be a database connection issue. Check Couchbase credentials and network connectivity."
                    return error_msg
            
            # StructuredTool is a Pydantic model - can't modify directly, need to create new instance
            if isinstance(tool, StructuredTool):
                try:
                    # Create a new StructuredTool with wrapped functions
                    tool_kwargs = {
                        'name': tool.name,
                        'description': tool.description,
                        'func': safe_invoke,
                    }
                    
                    if original_ainvoke:
                        tool_kwargs['coroutine'] = safe_coroutine
                    
                    if hasattr(tool, 'args_schema') and tool.args_schema:
                        tool_kwargs['args_schema'] = tool.args_schema
                    
                    if hasattr(tool, 'return_direct'):
                        tool_kwargs['return_direct'] = tool.return_direct
                    
                    if hasattr(tool, 'verbose'):
                        tool_kwargs['verbose'] = tool.verbose
                    
                    wrapped_tool = StructuredTool(**tool_kwargs)
                    logger.debug(f"Successfully wrapped StructuredTool: {tool_name}")
                    return wrapped_tool
                except Exception as e:
                    logger.error(f"Failed to create wrapped StructuredTool for {tool_name}: {e}", exc_info=True)
                    # Return original tool as fallback
                    return tool
            else:
                # For other BaseTool types, try to use handle_tool_error or return as-is
                # Some tools support error handling natively
                logger.debug(f"Tool {tool_name} is not a StructuredTool, returning as-is")
                return tool
        else:
            # For non-BaseTool objects, return as-is
            # Most tools from load_mcp_tools should be BaseTool instances
            logger.warning(f"Tool {type(tool)} is not a BaseTool, cannot wrap it")
            return tool
    
    async def create_agent(self) -> Any:
        """Create a ReAct agent with MCP tools.

        Returns:
            LangGraph agent instance
        """
        logger.info("Creating agent with MCP tools")
        
        try:
            # Ensure MCP session is open (persistent connection)
            await self._ensure_mcp_session()
            
            # If no tools available, use empty list
            if self._tools is None:
                self._tools = []
            
            # Create agent with the tools
            agent = create_react_agent(
                self.model,
                self._tools,
                prompt=self.SYSTEM_PROMPT,
                checkpointer=self._checkpoint,
            )
            
            if len(self._tools) > 0:
                logger.info(f"Agent created successfully with {len(self._tools)} MCP tools")
            else:
                logger.info("Agent created successfully without MCP tools (MCP not available)")
            return agent
                
        except Exception as e:
            logger.error(f"Failed to create agent: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            raise
    
    async def close(self):
        """Close MCP session."""
        if self._mcp_session_context and self._mcp_session:
            logger.info("Closing MCP session")
            await self._mcp_session_context.__aexit__(None, None, None)
            self._mcp_session_context = None
            self._mcp_session = None
            self._tools = None
    

    def get_checkpoint(self) -> InMemorySaver:
        """Get the checkpoint saver for agent memory.

        Returns:
            InMemorySaver instance
        """
        return self._checkpoint

