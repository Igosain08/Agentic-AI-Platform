#!/bin/bash
# Start script for Railway/Render deployment
# Handles PORT environment variable properly

# Default to 8000 if PORT is not set
PORT=${PORT:-8000}

# Export PORT so it's available to uvicorn
export PORT

# Start uvicorn with the port
exec uvicorn agentic_ai.api.main:app --host 0.0.0.0 --port "${PORT}"

