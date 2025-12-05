#!/bin/sh
# Start script for Railway/Render deployment
# Handles PORT environment variable properly

PORT=${PORT:-8000}
exec uvicorn agentic_ai.api.main:app --host 0.0.0.0 --port "$PORT"

