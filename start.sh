#!/bin/bash
set -e

# Debug: Show environment
echo "Environment variables:"
env | grep -E "PORT|RAILWAY" || echo "No PORT or RAILWAY vars found"

# Get PORT - Railway sets this automatically, but default to 8000
PORT="${PORT:-8000}"

# Ensure PORT is numeric
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "WARNING: PORT is not numeric, using 8000"
    PORT=8000
fi

echo "Starting uvicorn on port: $PORT"

# Start uvicorn
exec uvicorn agentic_ai.api.main:app --host 0.0.0.0 --port "$PORT"

