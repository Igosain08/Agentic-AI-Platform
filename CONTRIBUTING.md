# Contributing to Agentic AI Platform

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Copy `.env.sample` to `.env` and configure your credentials
5. Run tests to ensure everything works:
   ```bash
   pytest
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use Black for code formatting (line length: 100)
- Use Ruff for linting
- Use type hints where possible
- Write docstrings for all public functions and classes

## Testing

- Write tests for all new features
- Maintain or improve test coverage
- Run tests before submitting:
  ```bash
  pytest --cov=src/agentic_ai
  ```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all tests pass
4. Update documentation if needed
5. Submit a pull request with a clear description

## Commit Messages

Use clear, descriptive commit messages:
- `feat: Add new feature`
- `fix: Fix bug`
- `docs: Update documentation`
- `test: Add tests`
- `refactor: Refactor code`

## Questions?

Open an issue for questions or discussions.

