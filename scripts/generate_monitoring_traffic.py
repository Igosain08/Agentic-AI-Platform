#!/usr/bin/env python3
"""Generate traffic for monitoring dashboard testing.

This script runs ground truth tests to generate metrics that will appear
in the Grafana dashboard. Use this to populate the dashboard before
taking screenshots.
"""

import asyncio
import time
from typing import Any

import httpx


# Ground truth test queries
GROUND_TRUTH_QUERIES = [
    {
        "message": "What hotels are in Paris?",
        "thread_id": "monitoring-test-1",
    },
    {
        "message": "Show me routes from New York to London",
        "thread_id": "monitoring-test-2",
    },
    {
        "message": "What airports are in Los Angeles?",
        "thread_id": "monitoring-test-3",
    },
    {
        "message": "Find cheap hotels in Tokyo",
        "thread_id": "monitoring-test-4",
    },
    {
        "message": "What airlines fly to Paris?",
        "thread_id": "monitoring-test-5",
    },
]


async def make_query(client: httpx.AsyncClient, query: dict[str, str]) -> dict[str, Any]:
    """Make a query to the API.

    Args:
        client: HTTP client
        query: Query dictionary with message and thread_id

    Returns:
        Response dictionary
    """
    try:
        response = await client.post(
            "http://localhost:8000/api/v1/query",
            json=query,
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error querying {query['message']}: {e}")
        return {"error": str(e)}


async def generate_traffic(num_iterations: int = 3, delay: float = 2.0) -> None:
    """Generate traffic by running ground truth queries.

    Args:
        num_iterations: Number of times to run all queries
        delay: Delay between queries in seconds
    """
    print(f"🚀 Generating monitoring traffic ({num_iterations} iterations)...")
    print(f"   API: http://localhost:8000")
    print(f"   Grafana: http://localhost:3000")
    print()

    async with httpx.AsyncClient() as client:
        # Check API is running
        try:
            health = await client.get("http://localhost:8000/api/v1/health", timeout=5.0)
            health.raise_for_status()
            print("✅ API is running")
        except Exception as e:
            print(f"❌ API is not running: {e}")
            print("   Start API with: docker-compose up -d api")
            return

        # Run queries
        for iteration in range(num_iterations):
            print(f"\n📊 Iteration {iteration + 1}/{num_iterations}")
            for i, query in enumerate(GROUND_TRUTH_QUERIES, 1):
                print(f"   Query {i}/{len(GROUND_TRUTH_QUERIES)}: {query['message'][:50]}...")
                start = time.time()
                result = await make_query(client, query)
                duration = time.time() - start
                
                if "error" not in result:
                    print(f"      ✅ Success ({duration:.2f}s)")
                else:
                    print(f"      ❌ Error: {result.get('error', 'Unknown')}")
                
                # Delay between queries
                if i < len(GROUND_TRUTH_QUERIES):
                    await asyncio.sleep(delay)

        print("\n✅ Traffic generation complete!")
        print("\n📈 Next steps:")
        print("   1. Open Grafana: http://localhost:3000")
        print("   2. Navigate to: Dashboards → Agentic AI Platform - Production Monitoring")
        print("   3. Check the 'Request Latency Heatmap' panel")
        print("   4. Take a screenshot for your GitHub!")


if __name__ == "__main__":
    import sys
    
    num_iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    
    asyncio.run(generate_traffic(num_iterations, delay))

