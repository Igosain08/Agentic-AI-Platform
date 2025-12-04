# Configuration Guide

## Environment Variables

The application is configured through environment variables. Copy `.env.sample` to `.env` and update with your values.

### Application Settings

- `ENVIRONMENT`: Application environment (`development`, `production`, `test`)
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `APP_NAME`: Application name
- `APP_VERSION`: Application version

### API Settings

- `API_HOST`: Host to bind to (default: `0.0.0.0`)
- `API_PORT`: Port to listen on (default: `8000`)
- `API_WORKERS`: Number of worker processes (default: `4`)

### Nebius AI Configuration

- `NEBIUS_API_KEY`: Your Nebius Token Factory API key

### Couchbase Configuration

- `CB_CONNECTION_STRING`: Couchbase connection string
- `CB_USERNAME`: Couchbase username
- `CB_PASSWORD`: Couchbase password
- `CB_BUCKET_NAME`: Couchbase bucket name (default: `travel-sample`)

### MCP Server

- `MCP_SERVER_PATH`: Path to your cloned `mcp-server-couchbase` repository

### Redis Configuration

- `REDIS_HOST`: Redis host (default: `localhost`)
- `REDIS_PORT`: Redis port (default: `6379`)
- `REDIS_DB`: Redis database number (default: `0`)
- `REDIS_PASSWORD`: Redis password (optional)

### Cache Settings

- `CACHE_ENABLED`: Enable caching (default: `true`)
- `CACHE_TTL_SECONDS`: Cache TTL in seconds (default: `3600`)

### Rate Limiting

- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: `true`)
- `RATE_LIMIT_REQUESTS_PER_MINUTE`: Max requests per minute (default: `60`)

### Monitoring

- `METRICS_ENABLED`: Enable Prometheus metrics (default: `true`)
- `TRACING_ENABLED`: Enable distributed tracing (default: `false`)

### LLM Settings

- `LLM_MODEL`: LLM model identifier (default: `nebius/Qwen/Qwen3-235B-A22B`)
- `LLM_TEMPERATURE`: LLM temperature (default: `0.7`)
- `LLM_MAX_TOKENS`: Maximum tokens (default: `2000`)

## Configuration Priority

1. Environment variables (highest priority)
2. `.env` file
3. Default values (lowest priority)

