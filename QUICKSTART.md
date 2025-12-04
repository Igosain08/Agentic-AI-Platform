# Quick Start Guide

Get up and running with the Agentic AI Platform in minutes!

## Prerequisites

- Python 3.10+
- Docker and Docker Compose (optional, for containerized deployment)
- Couchbase Capella account (free tier available)
- Nebius Token Factory API key
- `uv` package manager ([install here](https://docs.astral.sh/uv/getting-started/installation/))

## Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Igosain08/Agentic-AI-Platform.git
   cd agentic-ai-platform
   ```

2. **Configure environment**
   ```bash
   cp .env.sample .env
   # Edit .env with your credentials
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Test the API**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

5. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Option 2: Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/Igosain08/Agentic-AI-Platform.git
   cd agentic-ai-platform
   ./scripts/setup.sh
   ```

2. **Configure environment**
   ```bash
   # Edit .env with your credentials
   nano .env
   ```

3. **Start Redis** (if not using Docker)
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

4. **Run the application**
   ```bash
   make run
   # or
   uvicorn src.agentic_ai.api.main:app --reload --port 8000
   ```

## First Query

Test the agent with a simple query:

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about the database",
    "thread_id": "test-123"
  }'
```

## Example Queries

```bash
# List top hotels
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List the top 5 hotels by rating",
    "thread_id": "user-123"
  }'

# Travel recommendations
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Recommend a flight and hotel from New York to San Francisco",
    "thread_id": "user-123"
  }'
```

## Next Steps

- Read the [full documentation](README.md)
- Explore the [API documentation](http://localhost:8000/docs)
- Check out the [architecture overview](docs/architecture/overview.md)
- Review [configuration options](docs/configuration.md)

## Troubleshooting

### MCP Server Connection Issues
- Ensure `MCP_SERVER_PATH` in `.env` points to your cloned `mcp-server-couchbase` repository
- Verify the MCP server can be executed with `uv run src/mcp_server.py`

### Couchbase Connection Issues
- Verify your Couchbase credentials in `.env`
- Ensure your IP is whitelisted in Couchbase Capella
- Check that the bucket name matches your Capella bucket

### Redis Connection Issues
- Ensure Redis is running: `docker ps | grep redis`
- Check Redis connection settings in `.env`
- If Redis is unavailable, caching will be disabled automatically

## Getting Help

- Check the [documentation](docs/)
- Open an [issue](https://github.com/Igosain08/Agentic-AI-Platform/issues)
- Review [troubleshooting guide](docs/troubleshooting.md)

