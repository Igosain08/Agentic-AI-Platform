#!/bin/bash
set -e

# DEBUG: Print everything
echo "=== DEBUG START ==="
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo "All environment variables:"
env | sort
echo "---"
echo "PORT variable specifically:"
echo "PORT='$PORT'"
echo "PORT length: ${#PORT}"
echo "PORT type check:"
if [ -z "$PORT" ]; then
    echo "  PORT is empty or unset"
else
    echo "  PORT is set to: '$PORT'"
fi
echo "---"

# Get PORT - Railway sets this automatically, but default to 8000
if [ -z "$PORT" ]; then
    echo "PORT not set, using default 8000"
    PORT=8000
else
    echo "PORT is set to: '$PORT'"
fi

# Ensure PORT is numeric
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "WARNING: PORT='$PORT' is not numeric, forcing to 8000"
    PORT=8000
fi

echo "Final PORT value: $PORT"
echo "=== DEBUG END ==="

# Start uvicorn
echo "Executing: uvicorn agentic_ai.api.main:app --host 0.0.0.0 --port $PORT"
exec uvicorn agentic_ai.api.main:app --host 0.0.0.0 --port "$PORT"

