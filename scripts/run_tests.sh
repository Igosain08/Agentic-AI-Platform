#!/bin/bash
# Test runner script

set -e

echo "Running tests..."

# Run with coverage
pytest tests/ \
    --cov=src/agentic_ai \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    -v

echo "Tests complete! Coverage report generated in htmlcov/"

