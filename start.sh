#!/bin/bash
# Start script for Railway/Render deployment
# Handles PORT environment variable properly

# Get PORT from environment, default to 8000
# Railway sets PORT automatically, but we need to ensure it's a number
if [ -z "$PORT" ]; then
    PORT=8000
fi

# Ensure PORT is a valid number
PORT=$(echo "$PORT" | grep -oE '[0-9]+' | head -1)
if [ -z "$PORT" ]; then
    PORT=8000
fi

# Debug: Print the port we're using
echo "Starting server on port: $PORT"

# Start uvicorn with the port
exec uvicorn agentic_ai.api.main:app --host 0.0.0.0 --port "$PORT"

