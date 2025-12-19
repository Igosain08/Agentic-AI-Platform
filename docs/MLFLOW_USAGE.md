# MLflow Integration Guide

This guide explains how to use MLflow for experiment tracking and agent evaluation in the Agentic AI Platform.

## Overview

MLflow integration enables:
- **Hyperparameter tracking**: Compare different LLM configurations (model, temperature, max_tokens)
- **Performance metrics**: Track latency percentiles (P50, P95, P99), success rates, response quality
- **Experiment comparison**: A/B test different configurations side-by-side
- **Model versioning**: Track which configurations work best over time

## Setup

### 1. Install MLflow

MLflow is already included in `requirements.txt`. Install it:

```bash
pip install -r requirements.txt
```

### 2. Enable MLflow Tracking

Set environment variables to enable MLflow:

```bash
export MLFLOW_ENABLED=true
export MLFLOW_EXPERIMENT_NAME="agentic-ai-platform"  # Optional, defaults to this
export MLFLOW_TRACKING_URI="file://./mlruns"  # Optional, defaults to local ./mlruns
```

Or add to your `.env` file:

```env
MLFLOW_ENABLED=true
MLFLOW_EXPERIMENT_NAME=agentic-ai-platform
MLFLOW_TRACKING_URI=file://./mlruns
```

### 3. Start MLflow UI (Optional)

To view experiments in a web UI:

```bash
mlflow ui
```

Then open http://localhost:5000 in your browser.

## Usage

### Running Agent Evaluation

Use the evaluation script to test different configurations:

```bash
# Basic evaluation
python scripts/evaluate_agent.py \
    --queries "What hotels are in Paris?" "Show me routes from New York to London" \
    --mlflow-enabled

# Compare different models
python scripts/evaluate_agent.py \
    --queries "What hotels are in Paris?" \
    --model gpt-4o-mini \
    --temperature 0.7 \
    --run-name "gpt-4o-mini-temp-0.7" \
    --mlflow-enabled

python scripts/evaluate_agent.py \
    --queries "What hotels are in Paris?" \
    --model gpt-4 \
    --temperature 0.7 \
    --run-name "gpt-4-temp-0.7" \
    --mlflow-enabled

# Test different temperatures
python scripts/evaluate_agent.py \
    --queries "What hotels are in Paris?" \
    --model gpt-4o-mini \
    --temperature 0.3 \
    --run-name "temp-0.3" \
    --mlflow-enabled

python scripts/evaluate_agent.py \
    --queries "What hotels are in Paris?" \
    --model gpt-4o-mini \
    --temperature 0.9 \
    --run-name "temp-0.9" \
    --mlflow-enabled
```

### Programmatic Usage

You can also use MLflow tracking programmatically in your code:

```python
from agentic_ai.monitoring.mlflow_tracker import get_mlflow_tracker

tracker = get_mlflow_tracker()

# Start a run
with tracker.start_run(run_name="my-experiment", tags={"test": "true"}):
    # Log hyperparameters
    tracker.log_params({
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2000
    })
    
    # Record latency
    tracker.log_latency(1.23)  # in seconds
    
    # Log metrics
    tracker.log_metrics({
        "success_rate": 0.95,
        "avg_latency_ms": 1200
    })
    
    # Calculate and log percentiles at the end
    tracker.log_latency_percentiles()
```

### Automatic Tracking in Production

When MLflow is enabled, the agent automatically tracks:
- Query latency (logged per query)
- Success/error rates
- Response lengths

Hyperparameters are logged at the start of each MLflow run (e.g., in evaluation scripts).

## Metrics Tracked

### Hyperparameters
- `llm_model`: Model name (e.g., "gpt-4o-mini")
- `llm_provider`: Provider (e.g., "openai")
- `llm_temperature`: Temperature setting (0.0-2.0)
- `llm_max_tokens`: Maximum tokens
- `agent_type`: Type of agent used
- `cache_enabled`: Whether caching is enabled

### Metrics
- `query_latency_ms`: Individual query latency (per query)
- `query_success`: 1 for success, 0 for error (per query)
- `query_response_length`: Length of response (per query)
- `total_queries`: Total number of queries in evaluation
- `success_rate`: Percentage of successful queries
- `error_rate`: Percentage of failed queries
- `avg_latency_ms`: Average latency across all queries
- `median_latency_ms`: Median latency
- `latency_p50_ms`: 50th percentile latency
- `latency_p95_ms`: 95th percentile latency
- `latency_p99_ms`: 99th percentile latency (tail latency)
- `min_latency_ms`: Minimum latency
- `max_latency_ms`: Maximum latency
- `avg_response_length`: Average response length

## Best Practices

1. **Use descriptive run names**: Include key config details (e.g., "gpt-4-temp-0.7-max-2000")

2. **Compare systematically**: Run the same evaluation queries with different configs for fair comparison

3. **Track P99 latency**: This is critical for production RAG systems - tracks worst-case performance

4. **Use tags**: Add tags to categorize runs (e.g., "baseline", "experiment", "production")

5. **Regular evaluations**: Set up periodic evaluations to track performance over time

## Example Evaluation Workflow

```bash
# 1. Baseline evaluation
python scripts/evaluate_agent.py \
    --queries "query1" "query2" "query3" \
    --model gpt-4o-mini \
    --temperature 0.7 \
    --run-name "baseline" \
    --mlflow-enabled

# 2. Test different model
python scripts/evaluate_agent.py \
    --queries "query1" "query2" "query3" \
    --model gpt-4 \
    --temperature 0.7 \
    --run-name "gpt-4-comparison" \
    --mlflow-enabled

# 3. View results
mlflow ui

# 4. Compare in MLflow UI:
# - Compare runs side-by-side
# - Filter by tags/metrics
# - Export results
```

## Troubleshooting

**MLflow not tracking:**
- Check `MLFLOW_ENABLED=true` is set
- Verify MLflow is installed: `pip list | grep mlflow`
- Check logs for MLflow initialization messages

**Can't see runs in UI:**
- Ensure you're pointing to the correct tracking URI
- Check that `mlruns/` directory exists and has data
- Try: `mlflow ui --backend-store-uri ./mlruns`

**High memory usage:**
- MLflow stores run data locally by default
- Consider using a remote tracking server for production
- Periodically clean up old runs

## Remote Tracking Server

For production, use a remote MLflow tracking server:

```bash
# Start MLflow server
mlflow server --host 0.0.0.0 --port 5000

# Set tracking URI
export MLFLOW_TRACKING_URI=http://your-server:5000
```

Or use MLflow hosted solutions like Databricks MLflow.

