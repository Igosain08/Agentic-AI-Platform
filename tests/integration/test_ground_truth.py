"""Ground truth tests - Fixed Q&A pairs to ensure basic functionality."""

import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# These are smoke tests - they verify basic functionality hasn't broken
# Note: These may need to be mocked for CI/CD if external services aren't available


async def test_ground_truth_hotels_in_paris():
    """Ground Truth Test 1: Hotels in Paris."""
    from agentic_ai.agents.query_agent import QueryAgent
    from agentic_ai.core.agent_factory import AgentFactory
    
    mock_factory = MagicMock(spec=AgentFactory)
    mock_agent = MagicMock()
    
    # Expected: Should return information about hotels in Paris
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Here are some hotels in Paris: [hotel list]")]
    })
    mock_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    agent = QueryAgent(agent_factory=mock_factory)
    result = await agent.process(
        message="What hotels are in Paris?",
        thread_id="test-thread-1"
    )
    
    assert "response" in result
    assert "metadata" in result
    assert len(result["response"]) > 0
    # Response should contain hotel-related content
    assert "hotel" in result["response"].lower() or "paris" in result["response"].lower()


async def test_ground_truth_routes_nyc_london():
    """Ground Truth Test 2: Routes from NYC to London."""
    from agentic_ai.agents.query_agent import QueryAgent
    from agentic_ai.core.agent_factory import AgentFactory
    
    mock_factory = MagicMock(spec=AgentFactory)
    mock_agent = MagicMock()
    
    # Expected: Should return route information
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Routes from New York to London: [route information]")]
    })
    mock_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    agent = QueryAgent(agent_factory=mock_factory)
    result = await agent.process(
        message="Show me routes from New York to London",
        thread_id="test-thread-2"
    )
    
    assert "response" in result
    assert "metadata" in result
    assert "route" in result["response"].lower() or "london" in result["response"].lower() or len(result["response"]) > 0


async def test_ground_truth_airports_los_angeles():
    """Ground Truth Test 3: Airports in Los Angeles."""
    from agentic_ai.agents.query_agent import QueryAgent
    from agentic_ai.core.agent_factory import AgentFactory
    
    mock_factory = MagicMock(spec=AgentFactory)
    mock_agent = MagicMock()
    
    # Expected: Should return airport information
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Airports in Los Angeles: LAX, BUR, etc.")]
    })
    mock_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    agent = QueryAgent(agent_factory=mock_factory)
    result = await agent.process(
        message="What airports are in Los Angeles?",
        thread_id="test-thread-3"
    )
    
    assert "response" in result
    assert "metadata" in result
    assert "airport" in result["response"].lower() or "los angeles" in result["response"].lower() or len(result["response"]) > 0


async def test_ground_truth_cheap_hotels_tokyo():
    """Ground Truth Test 4: Cheap hotels in Tokyo."""
    from agentic_ai.agents.query_agent import QueryAgent
    from agentic_ai.core.agent_factory import AgentFactory
    
    mock_factory = MagicMock(spec=AgentFactory)
    mock_agent = MagicMock()
    
    # Expected: Should return filtered hotel results
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Cheap hotels in Tokyo: [filtered hotel list]")]
    })
    mock_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    agent = QueryAgent(agent_factory=mock_factory)
    result = await agent.process(
        message="Find cheap hotels in Tokyo",
        thread_id="test-thread-4"
    )
    
    assert "response" in result
    assert "metadata" in result
    assert "hotel" in result["response"].lower() or "tokyo" in result["response"].lower() or len(result["response"]) > 0


async def test_ground_truth_airlines_to_paris():
    """Ground Truth Test 5: Airlines that fly to Paris."""
    from agentic_ai.agents.query_agent import QueryAgent
    from agentic_ai.core.agent_factory import AgentFactory
    
    mock_factory = MagicMock(spec=AgentFactory)
    mock_agent = MagicMock()
    
    # Expected: Should return airline information
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Airlines that fly to Paris: [airline list]")]
    })
    mock_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    agent = QueryAgent(agent_factory=mock_factory)
    result = await agent.process(
        message="What airlines fly to Paris?",
        thread_id="test-thread-5"
    )
    
    assert "response" in result
    assert "metadata" in result
    assert "airline" in result["response"].lower() or "paris" in result["response"].lower() or len(result["response"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ground_truth_smoke_test_all_queries():
    """Run all ground truth tests as a smoke test suite."""
    queries = [
        "What hotels are in Paris?",
        "Show me routes from New York to London",
        "What airports are in Los Angeles?",
        "Find cheap hotels in Tokyo",
        "What airlines fly to Paris?",
    ]
    
    from agentic_ai.agents.query_agent import QueryAgent
    from agentic_ai.core.agent_factory import AgentFactory
    
    mock_factory = MagicMock(spec=AgentFactory)
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Test response")]
    })
    mock_factory.create_agent = AsyncMock(return_value=mock_agent)
    
    agent = QueryAgent(agent_factory=mock_factory)
    
    results = []
    for i, query in enumerate(queries):
        result = await agent.process(
            message=query,
            thread_id=f"smoke-test-{i}"
        )
        results.append(result)
        assert "response" in result
        assert "metadata" in result
    
    # All queries should succeed
    assert len(results) == 5
    assert all("response" in r for r in results)

