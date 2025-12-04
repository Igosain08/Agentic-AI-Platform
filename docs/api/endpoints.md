# API Endpoints Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently, the API does not require authentication. In production, implement API key or OAuth2 authentication.

## Endpoints

### POST /query
Submit a natural language query to the agent system.

**Request Body:**
```json
{
  "message": "List top 5 hotels by rating",
  "thread_id": "user-123",
  "agent_type": "auto",
  "use_cache": true
}
```

**Response:**
```json
{
  "response": "Based on the database query, here are the top 5 hotels...",
  "thread_id": "user-123",
  "metadata": {
    "agent_type": "query",
    "execution_time_ms": 1234,
    "cache_hit": false
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "checks": {
    "api": "healthy",
    "mcp": "configured"
  }
}
```

### GET /conversation/{thread_id}
Retrieve conversation history for a thread.

### DELETE /conversation/{thread_id}
Clear conversation history for a thread.

### GET /metrics
Prometheus metrics endpoint (for monitoring).

