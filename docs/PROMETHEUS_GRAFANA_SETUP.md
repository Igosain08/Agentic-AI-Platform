# Prometheus & Grafana Production Monitoring Setup

## Overview

This setup provides **real-time production monitoring** for the Agentic AI Platform using Prometheus and Grafana. This is the "Senior Engineer" move - showing you can monitor a live system and identify exactly which part of the pipeline is slow.

## Architecture

```
FastAPI App → Prometheus → Grafana
     ↓            ↓           ↓
  /metrics    Scrapes    Visualizes
```

## Features

### 1. Automatic FastAPI Instrumentation
- **prometheus-fastapi-instrumentator**: Automatically exposes `/metrics` endpoint
- Tracks: Request count, duration, status codes, in-progress requests

### 2. Custom Metrics (The "Senior Engineer" Move)
- **Embedding Latency**: Time spent on database queries (RAG retrieval equivalent)
- **LLM Generation Latency**: Time spent on actual LLM calls
- **Pipeline Stage Breakdown**: Total, LLM, Tool execution times

### 3. Grafana Dashboard
- **Request Latency Heatmap**: Visual distribution of request latencies
- **Embedding vs LLM Latency**: Compare which part of pipeline is slow
- **Pipeline Stage Breakdown**: See where time is spent
- **Success Rate**: Monitor system health
- **Latency Percentiles**: P50, P95, P99 tracking

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

This starts:
- **FastAPI API**: `http://localhost:8000`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000` (admin/admin)

### 2. Access Grafana

1. Open `http://localhost:3000`
2. Login with `admin` / `admin`
3. Navigate to **Dashboards** → **Agentic AI Platform - Production Monitoring**

The dashboard is automatically provisioned!

### 3. Generate Traffic

Run your ground truth tests to generate metrics:

```bash
# Run ground truth tests
pytest tests/integration/test_ground_truth.py -v

# Or make API calls
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What hotels are in Paris?", "thread_id": "test-1"}'
```

### 4. View Metrics

- **Prometheus**: `http://localhost:9090` → Query metrics
- **Grafana**: `http://localhost:3000` → View dashboards

## Custom Metrics Explained

### Embedding Latency (`agentic_ai_embedding_latency_seconds`)
- **What**: Time spent on database queries via MCP tools
- **Why**: This is the "RAG retrieval" equivalent - shows how long database operations take
- **Use Case**: Identify if database queries are the bottleneck

### LLM Generation Latency (`agentic_ai_llm_generation_latency_seconds`)
- **What**: Time spent on actual LLM API calls
- **Why**: Shows if LLM calls are slow (model, network, rate limits)
- **Use Case**: Identify if LLM is the bottleneck

### Pipeline Stage Duration (`agentic_ai_pipeline_stage_duration_seconds`)
- **What**: Breakdown of total query time
- **Stages**: `llm_generation`, `tool_execution`, `total`
- **Use Case**: See exactly where time is spent in the pipeline

## Prometheus Queries

### Request Rate
```promql
rate(http_requests_total[5m])
```

### Request Latency P99
```promql
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### Embedding vs LLM Latency
```promql
# Embedding P99
histogram_quantile(0.99, rate(agentic_ai_embedding_latency_seconds_bucket[5m]))

# LLM Generation P99
histogram_quantile(0.99, rate(agentic_ai_llm_generation_latency_seconds_bucket[5m]))
```

### Success Rate
```promql
rate(agentic_ai_agent_queries_total{status="success"}[5m]) / 
rate(agentic_ai_agent_queries_total[5m]) * 100
```

## Dashboard Panels

1. **Request Rate**: Requests per second by method and status
2. **Request Latency Heatmap**: Visual distribution of latencies (THE PROOF OF WORK)
3. **Embedding vs LLM Latency**: Compare which part is slow
4. **Pipeline Stage Breakdown**: See time breakdown
5. **Success Rate**: Monitor system health
6. **Latency Percentiles**: P50, P95, P99

## Production Deployment

### Environment Variables

```bash
# Enable metrics
METRICS_ENABLED=true

# Prometheus scraping interval (in docker-compose)
# Default: 5s for real-time monitoring
```

### Monitoring at 2 AM

If your API starts failing at 2 AM:

1. **Check Grafana Dashboard**: See if request rate dropped or errors increased
2. **Check Prometheus Alerts**: (Future: Set up Alertmanager)
3. **Check Latency Heatmap**: See if latencies spiked
4. **Check Success Rate**: See if success rate dropped

### Alerting (Future Enhancement)

Set up Alertmanager to:
- Alert on high error rate
- Alert on high latency (P99 > threshold)
- Alert on low success rate

## Troubleshooting

### Prometheus can't scrape API

1. Check API is running: `curl http://localhost:8000/health`
2. Check metrics endpoint: `curl http://localhost:8000/metrics`
3. Check Prometheus targets: `http://localhost:9090/targets`

### Grafana can't connect to Prometheus

1. Check Prometheus is running: `curl http://localhost:9090/-/healthy`
2. Check Grafana datasource: Grafana → Configuration → Data Sources → Prometheus
3. Test query: Try a simple query like `up`

### No metrics showing

1. Generate traffic: Make API calls or run tests
2. Wait a few seconds: Prometheus scrapes every 5s
3. Check time range: Make sure time range includes when traffic was generated

## Files Structure

```
.
├── docker-compose.yml              # Orchestrates all services
├── prometheus/
│   └── prometheus.yml              # Prometheus configuration
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── prometheus.yml      # Auto-configure Prometheus datasource
    │   └── dashboards/
    │       └── dashboard.yml      # Auto-load dashboards
    └── dashboards/
        └── agentic-ai-platform.json # Main dashboard
```

## Next Steps

1. **Run Ground Truth Tests**: Generate traffic
2. **Capture Screenshot**: Take screenshot of latency heatmap
3. **Add to GitHub**: This is your "Proof of Work"
4. **Set Up Alerts**: Configure Alertmanager for production

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)

