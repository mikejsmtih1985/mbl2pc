# MBL2PC - Modern Python 3.13 Messaging Service

[![CI](https://github.com/mikejsmtih1985/mbl2pc/workflows/CI/badge.svg)](https://github.com/mikejsmtih1985/mbl2pc/actions)
[![Code Quality](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked](https://img.shields.io/badge/typing-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

A modern, fully typed FastAPI application for sending messages from mobile devices to computers, built with Python 3.13 and following the latest best practices.

## 🎯 Features

- **Modern Python 3.13** with cutting-edge language features
- **Type Safety** with Pydantic v2 and MyPy strict mode
- **Dependency Injection** for excellent testability
- **Comprehensive Testing** - Unit, Integration, and E2E tests with 67%+ coverage
- **Code Quality** - Ruff for linting/formatting, pre-commit hooks
- **Cloud Ready** - AWS DynamoDB and S3 integration
- **OAuth Authentication** via Authlib
- **FastAPI** with modern async/await patterns

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/mikejsmtih1985/mbl2pc.git
cd mbl2pc
pip install -e ".[dev]"

# Set up development environment
make install

# Run tests
make test

# Start development server
uvicorn src.mbl2pc.main:app --reload
```

## 🛠️ Development

### Prerequisites

- Python 3.13+
- AWS credentials (for DynamoDB and S3)

### Modern Development Workflow

```bash
# Install with all development dependencies
make install

# Code quality checks
make lint         # Ruff linting
make format       # Ruff formatting
make type-check   # MyPy type checking

# Testing
make test              # Unit and integration tests
make test-parallel     # Parallel test execution

# Run all quality checks
make ci

# Clean up generated files
make clean
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:

```bash
pre-commit install
pre-commit run --all-files
```

## 🏗️ Architecture

### Dependency Injection

The application uses modern dependency injection patterns for better testability:

```python
from mbl2pc.core.storage import get_db_table, DynamoDBTableProtocol
from fastapi import Depends

@app.post("/messages")
async def send_message(
    message: MessageCreate,
    db_table: DynamoDBTableProtocol = Depends(get_db_table),
    current_user: User = Depends(get_current_user)
):
    # Implementation with injected dependencies
```

### Modern Type Safety

Full type coverage with runtime validation:

```python
from typing import Protocol, runtime_checkable
from pydantic import BaseModel

@runtime_checkable
class StorageProtocol(Protocol):
    def store_message(self, message: dict[str, Any]) -> dict[str, Any]: ...

class Message(BaseModel):
    user_id: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
```

### Test Architecture

- **Unit Tests**: Pure logic testing with mocked dependencies
- **Integration Tests**: API testing with real FastAPI app
- **E2E Tests**: Full workflow testing with Playwright

## 📊 Code Quality

- **Ruff**: Modern linting and formatting (replaces black, flake8, isort)
- **MyPy**: Strict type checking
- **pytest**: Modern testing with asyncio support
- **Coverage**: 65%+ test coverage requirement
- **Pre-commit**: Automated quality checks

## 🔧 Configuration

Environment-based configuration with Pydantic Settings:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    mbl2pc_ddb_table: str = "mbl2pc-messages"

    class Config:
        env_file = ".env"
```

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest

# Specific test types
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # E2E tests only

# With coverage
pytest --cov=src/mbl2pc --cov-report=html

# Parallel execution
pytest -n auto
```

### Test Structure

```
tests/
├── unit/           # Pure unit tests
├── integration/    # API integration tests
├── e2e/           # End-to-end tests
└── conftest.py    # Shared fixtures with dependency injection
```

## 📦 Dependencies

### Production
- FastAPI - Modern web framework
- Pydantic v2 - Data validation and serialization
- boto3 - AWS SDK
- uvicorn - ASGI server

### Development
- ruff - Linting and formatting
- mypy - Static type checking
- pytest - Testing framework
- pre-commit - Git hooks

## 🚀 Deployment

The application is designed for modern cloud deployment:

- Docker ready
- AWS Lambda compatible
- Environment-based configuration
- Health checks included

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Install development dependencies: `make install`
2. Set up pre-commit hooks: `pre-commit install`
3. Run quality checks: `make ci`
4. Submit a pull request

---

Built with ❤️ using modern Python 3.13 and best practices.
-   Messages are stored per user and persist across devices.
-   The app version (git commit hash) is shown in the UI footer and at `/version`.

## Testing

-   Backend: Run `pytest` to test API endpoints.
-   Frontend: Playwright tests are included for public and error routes.

## File Structure

-   `main.py` — FastAPI backend, OAuth, DynamoDB integration
-   `static/send.html` — Chat UI (HTML/JS/CSS)
-   `requirements.txt` — Python dependencies
-   `render.yaml` — Render.com deployment config

## License

MIT
