#!/bin/bash
# Setup script for agentic-ai-platform

set -e

echo "🚀 Setting up Agentic AI Platform..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.sample..."
    cp .env.sample .env
    echo "⚠️  Please update .env with your credentials"
fi

# Check for MCP server path
if ! grep -q "MCP_SERVER_PATH" .env || grep -q "MCP_SERVER_PATH=/path/to" .env; then
    echo "⚠️  Please update MCP_SERVER_PATH in .env"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your credentials"
echo "2. Run 'make run' to start the development server"
echo "3. Visit http://localhost:8000/docs for API documentation"

