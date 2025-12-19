#!/usr/bin/env python3
"""
Agent evaluation script with MLflow tracking.

This script evaluates agent performance on a set of queries and logs results to MLflow.
Useful for A/B testing different configurations and tracking performance over time.

Example usage:
    python scripts/evaluate_agent.py \
        --queries "What hotels are in Paris?" "Show me routes from New York to London" \
        --model gpt-4o-mini \
        --temperature 0.7 \
        --max-tokens 2000 \
        --run-name "baseline-config"
"""

import argparse
import asyncio
import os
import sys
from typing import Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agentic_ai.agents.orchestrator import AgentOrchestrator
from agentic_ai.config.settings import get_settings
from agentic_ai.core.agent_factory import AgentFactory
from agentic_ai.monitoring.logging import get_logger
from agentic_ai.monitoring.mlflow_tracker import get_mlflow_tracker
from agentic_ai.utils.cache import CacheManager

logger = get_logger(__name__)


async def evaluate_agent(
    queries: list[str],
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    run_name: str | None = None,
    use_cache: bool = False,
) -> dict[str, Any]:
    """Evaluate agent on a set of queries.

    Args:
        queries: List of query strings to evaluate
        model: Optional model name override
        temperature: Optional temperature override
        max_tokens: Optional max_tokens override
        run_name: Optional MLflow run name
        use_cache: Whether to use cache (default False for evaluation)

    Returns:
        Dictionary with evaluation results
    """
    settings = get_settings()
    tracker = get_mlflow_tracker()

    # Override settings if provided
    if model:
        settings.llm_model = model
    if temperature is not None:
        settings.llm_temperature = temperature
    if max_tokens is not None:
        settings.llm_max_tokens = max_tokens

    # Prepare hyperparameters for logging
    hyperparams = {
        "llm_model": settings.llm_model,
        "llm_provider": settings.llm_provider,
        "llm_temperature": settings.llm_temperature,
        "llm_max_tokens": settings.llm_max_tokens,
        "agent_type": "query",
        "cache_enabled": use_cache,
    }

    # Initialize components
    agent_factory = AgentFactory()
    cache_manager = CacheManager() if use_cache else None
    orchestrator = AgentOrchestrator(agent_factory, cache_manager)

    results = []
    success_count = 0
    error_count = 0

    # Start MLflow run
    with tracker.start_run(
        run_name=run_name,
        tags={
            "evaluation": "true",
            "agent_type": "query",
            "model": settings.llm_model,
        },
    ):
        # Log hyperparameters
        tracker.log_params(hyperparams)

        # Evaluate each query
        for i, query in enumerate(queries, 1):
            logger.info(f"Evaluating query {i}/{len(queries)}: {query[:50]}...")
            thread_id = f"eval-{i}"

            try:
                result = await orchestrator.process(
                    message=query,
                    thread_id=thread_id,
                    agent_type="auto",
                    use_cache=use_cache,
                )

                duration_ms = result["metadata"]["execution_time_ms"]
                success_count += 1

                query_result = {
                    "query": query,
                    "success": True,
                    "duration_ms": duration_ms,
                    "response_length": len(result["response"]),
                    "response_preview": result["response"][:200],
                }
                results.append(query_result)

                logger.info(f"Query {i} completed in {duration_ms}ms")

            except Exception as e:
                error_count += 1
                query_result = {
                    "query": query,
                    "success": False,
                    "error": str(e),
                }
                results.append(query_result)
                logger.error(f"Query {i} failed: {e}")

        # Calculate aggregate metrics
        successful_results = [r for r in results if r.get("success", False)]
        latencies = [r["duration_ms"] for r in successful_results]

        if latencies:
            import statistics

            metrics = {
                "total_queries": len(queries),
                "success_rate": success_count / len(queries),
                "error_rate": error_count / len(queries),
                "avg_latency_ms": statistics.mean(latencies),
                "median_latency_ms": statistics.median(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "avg_response_length": statistics.mean([r["response_length"] for r in successful_results]),
            }

            # Calculate percentiles
            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)
            if n > 0:
                metrics["latency_p50_ms"] = sorted_latencies[int(n * 0.50)]
                metrics["latency_p95_ms"] = sorted_latencies[int(n * 0.95)]
                metrics["latency_p99_ms"] = sorted_latencies[int(n * 0.99)]

            # Log metrics to MLflow
            tracker.log_metrics(metrics)
            tracker.log_latency_percentiles()

            logger.info(f"Evaluation complete. Success rate: {metrics['success_rate']:.2%}")
            logger.info(f"Average latency: {metrics['avg_latency_ms']:.2f}ms")
            logger.info(f"P99 latency: {metrics.get('latency_p99_ms', 0):.2f}ms")
        else:
            logger.warning("No successful queries to calculate metrics")

    return {
        "hyperparams": hyperparams,
        "results": results,
        "summary": {
            "total": len(queries),
            "success": success_count,
            "errors": error_count,
        },
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Evaluate agent with MLflow tracking")
    parser.add_argument(
        "--queries",
        nargs="+",
        required=True,
        help="List of queries to evaluate",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model name override (e.g., gpt-4o-mini, gpt-4)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Temperature override",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Max tokens override",
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="MLflow run name",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Enable caching (default: False for evaluation)",
    )
    parser.add_argument(
        "--mlflow-enabled",
        action="store_true",
        default=False,
        help="Enable MLflow tracking (or set MLFLOW_ENABLED=true)",
    )

    args = parser.parse_args()

    # Enable MLflow if requested
    if args.mlflow_enabled:
        os.environ["MLFLOW_ENABLED"] = "true"

    # Run evaluation
    results = asyncio.run(
        evaluate_agent(
            queries=args.queries,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            run_name=args.run_name,
            use_cache=args.use_cache,
        )
    )

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total queries: {results['summary']['total']}")
    print(f"Successful: {results['summary']['success']}")
    print(f"Errors: {results['summary']['errors']}")
    print("\nHyperparameters:")
    for key, value in results["hyperparams"].items():
        print(f"  {key}: {value}")

    # Check if MLflow tracking was used
    tracker = get_mlflow_tracker()
    if tracker.is_enabled:
        print("\n✅ Results logged to MLflow")
        print("   View results: mlflow ui")
    else:
        print("\n⚠️  MLflow tracking is disabled")
        print("   Enable with: --mlflow-enabled or set MLFLOW_ENABLED=true")


if __name__ == "__main__":
    main()

