# Quick Start: MLflow Integration

## 1. Enable MLflow

Add to your `.env` file:
```env
MLFLOW_ENABLED=true
```

Or set environment variable:
```bash
export MLFLOW_ENABLED=true
```

## 2. Run Your First Evaluation

```bash
python scripts/evaluate_agent.py \
    --queries "What hotels are in Paris?" "Show me routes from New York to London" \
    --mlflow-enabled
```

## 3. View Results

Start MLflow UI:
```bash
mlflow ui
```

Open http://localhost:5000 in your browser to see:
- All experiment runs
- Hyperparameters (model, temperature, etc.)
- Metrics (latency, success rate, P99)
- Comparison between runs

## 4. Compare Different Configurations

```bash
# Test with gpt-4o-mini
python scripts/evaluate_agent.py \
    --queries "What hotels are in Paris?" \
    --model gpt-4o-mini \
    --temperature 0.7 \
    --run-name "gpt-4o-mini-temp-0.7" \
    --mlflow-enabled

# Test with gpt-4
python scripts/evaluate_agent.py \
    --queries "What hotels are in Paris?" \
    --model gpt-4 \
    --temperature 0.7 \
    --run-name "gpt-4-temp-0.7" \
    --mlflow-enabled
```

Then compare the runs in MLflow UI to see which performs better!

## What Gets Tracked?

✅ **Hyperparameters**: Model name, temperature, max_tokens, provider  
✅ **Performance Metrics**: P50, P95, P99 latency, success rate  
✅ **Per-Query Data**: Individual query latency and success/failure  
✅ **Response Metrics**: Average response length

## Next Steps

- Read [MLFLOW_USAGE.md](MLFLOW_USAGE.md) for detailed documentation
- Set up periodic evaluations to track performance over time
- Use remote MLflow server for production deployments

