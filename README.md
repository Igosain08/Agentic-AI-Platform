# Agentic AI Platform - Production-Ready Multi-Agent System

[![CI/CD](https://github.com/Igosain08/Agentic-AI-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Igosain08/Agentic-AI-Platform/actions)
[![Code Coverage](https://codecov.io/gh/Igosain08/Agentic-AI-Platform/branch/main/graph/badge.svg)](https://codecov.io/gh/Igosain08/Agentic-AI-Platform)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> **Enterprise-grade agentic AI platform** demonstrating advanced multi-agent orchestration, tool use, and database integration via Model Context Protocol (MCP). Built to showcase production-ready AI agent systems.

## 🚀 Key Features

### Core Capabilities
- **Multi-Agent Orchestration**: Sophisticated agent coordination with specialized roles
- **ReAct Agent Framework**: Reasoning and Acting agents powered by LangGraph
- **Model Context Protocol (MCP)**: Standardized integration with Couchbase and extensible to other data sources
- **Advanced Query Optimization**: Intelligent SQL++ query generation and caching
- **Production-Ready API**: FastAPI-based REST API with async support, OpenAPI docs, and comprehensive error handling

### Production Features
- **Observability**: Structured logging, metrics, and distributed tracing
- **Performance**: Query caching, connection pooling, rate limiting
- **Reliability**: Retry logic, circuit breakers, health checks
- **Security**: Input validation, authentication ready, secure credential management
- **Testing**: Comprehensive test suite (unit, integration, E2E)
- **DevOps**: Docker containerization, CI/CD pipeline, Kubernetes-ready

### Advanced Agentic AI Features
- **Specialized Agent Roles**: Query optimizer, data analyst, response formatter
- **Agent Memory Management**: Persistent conversation context with thread-based isolation
- **Tool Selection Intelligence**: Dynamic tool selection based on query complexity
- **Query Result Caching**: Intelligent caching with TTL and invalidation strategies
- **Multi-turn Conversations**: Context-aware follow-up handling

## 🎯 Resume Highlights

This project demonstrates:
- **Production-Grade AI Systems**: Multi-agent orchestration with LangGraph and LangChain
- **Modern DevOps**: CI/CD pipelines, Docker containerization, comprehensive testing
- **Enterprise Integration**: Model Context Protocol (MCP) for standardized tool integration
- **Scalable Architecture**: Async FastAPI, Redis caching, Prometheus metrics
- **Best Practices**: Type hints, structured logging, error handling, security considerations

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Resume Highlights](#-resume-highlights)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST API Layer                    │
│  (Async endpoints, rate limiting, authentication)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Agent Orchestration Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Query Agent  │  │ Data Agent   │  │ Format Agent │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              LangGraph ReAct Agent Framework                 │
│  (Reasoning, Tool Selection, Execution)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Model Context Protocol (MCP)                    │
│  (Standardized tool interface)                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Couchbase Database                              │
│  (Travel sample data, inventory scope)                       │
└─────────────────────────────────────────────────────────────┘
```

### Component Overview

1. **API Layer**: FastAPI application with async endpoints, request validation, and error handling
2. **Agent Orchestrator**: Coordinates multiple specialized agents for complex queries
3. **ReAct Agents**: LangGraph-based agents that reason about queries and select appropriate tools
4. **MCP Integration**: Standardized protocol for database tool access
5. **Caching Layer**: Redis-based caching for query results and tool responses
6. **Monitoring**: Structured logging, Prometheus metrics, and distributed tracing

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Couchbase Capella account (free tier available)
- Nebius Token Factory API key
- `uv` package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))

### 1. Clone and Setup

```bash
git clone https://github.com/Igosain08/Agentic-AI-Platform.git
cd agentic-ai-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.sample .env
# Edit .env with your credentials
```

Required environment variables:
```env
NEBIUS_API_KEY=your_nebius_api_key
CB_CONNECTION_STRING=your_couchbase_connection_string
CB_USERNAME=your_couchbase_username
CB_PASSWORD=your_couchbase_password
CB_BUCKET_NAME=travel-sample
MCP_SERVER_PATH=/path/to/mcp-server-couchbase
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Query the agent
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the database", "thread_id": "test-123"}'
```

## 📦 Installation

### Development Installation

```bash
git clone https://github.com/Igosain08/Agentic-AI-Platform.git
cd agentic-ai-platform
pip install -e ".[dev]"
```

### Production Installation

```bash
pip install agentic-ai-platform
```

## ⚙️ Configuration

Configuration is managed through environment variables and a `config.yaml` file. See [docs/configuration.md](docs/configuration.md) for detailed configuration options.

Key configuration areas:
- **LLM Settings**: Model selection, temperature, max tokens
- **Agent Settings**: Agent roles, tool selection strategies
- **Database**: Connection pooling, query timeouts
- **Caching**: TTL, cache size, invalidation policies
- **Monitoring**: Log levels, metrics collection

## 📚 API Documentation

### Interactive API Docs

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### `POST /api/v1/query`
Submit a natural language query to the agent system.

**Request:**
```json
{
  "message": "List top 5 hotels by rating",
  "thread_id": "user-123",
  "use_cache": true,
  "agent_type": "auto"
}
```

**Response:**
```json
{
  "response": "Based on the database query, here are the top 5 hotels...",
  "thread_id": "user-123",
  "metadata": {
    "agents_used": ["query_agent", "data_agent"],
    "tools_called": ["execute_sql_query"],
    "execution_time_ms": 1234,
    "cache_hit": false
  }
}
```

#### `GET /api/v1/conversation/{thread_id}`
Retrieve conversation history for a thread.

#### `DELETE /api/v1/conversation/{thread_id}`
Clear conversation history for a thread.

#### `GET /api/v1/health`
Health check endpoint with system status.

#### `GET /api/v1/metrics`
Prometheus metrics endpoint.

## 🛠️ Development

### Project Structure

```
agentic-ai-platform/
├── src/
│   └── agentic_ai/
│       ├── core/           # Core agent logic
│       ├── agents/          # Specialized agent implementations
│       ├── api/             # FastAPI application
│       ├── config/          # Configuration management
│       ├── utils/           # Utilities and helpers
│       └── monitoring/      # Logging and metrics
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
└── docker/                  # Docker configurations
```

### Running Locally

```bash
# Start development server
uvicorn src.agentic_ai.api.main:app --reload --port 8000

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src/agentic_ai tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/
```

## 🧪 Testing

Comprehensive test suite with unit, integration, and E2E tests.

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=src/agentic_ai --cov-report=html
```

## 🚢 Deployment

### Docker

```bash
docker build -t agentic-ai-platform .
docker run -p 8000:8000 --env-file .env agentic-ai-platform
```

### Kubernetes

See [docs/deployment/kubernetes.md](docs/deployment/kubernetes.md) for Kubernetes deployment guides.

### Cloud Platforms

- **AWS**: ECS, EKS, or Lambda deployment
- **GCP**: Cloud Run or GKE
- **Azure**: Container Instances or AKS

## 📊 Monitoring

The platform includes comprehensive observability:

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Metrics**: Prometheus-compatible metrics endpoint
- **Tracing**: Distributed tracing support (OpenTelemetry ready)
- **Health Checks**: Liveness and readiness probes

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Learning & Resume Value

This project demonstrates:
- **Production Engineering**: Error handling, monitoring, caching, rate limiting
- **System Design**: Multi-layered architecture, scalability patterns
- **AI/ML Engineering**: Agent orchestration, tool use, prompt engineering
- **DevOps**: Docker containerization, CI/CD pipelines, observability
- **Code Quality**: Comprehensive testing, type checking, documentation
- **Modern Python**: Async/await, type hints, dependency injection

Perfect for showcasing to top tech companies like Google, Meta, and other FAANG companies!

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/) and [LangGraph](https://www.langchain.com/langgraph)
- Uses [Model Context Protocol](https://modelcontextprotocol.io/) for standardized tool integration
- Powered by [Couchbase](https://www.couchbase.com/) and [Nebius AI](https://nebius.com/)

## 📚 Additional Resources

- [Quick Start Guide](QUICKSTART.md) - Get started in minutes
- [Project Summary](PROJECT_SUMMARY.md) - Detailed project overview
- [Architecture Documentation](docs/architecture/overview.md)
- [API Documentation](docs/api/endpoints.md)
- [Configuration Guide](docs/configuration.md)

## 📧 Contact

For questions or support, please open an issue or contact [your-email@example.com](mailto:your-email@example.com)

---

**Built with ❤️ to demonstrate production-ready agentic AI systems**

*Showcasing enterprise-grade AI engineering practices for top tech companies*

