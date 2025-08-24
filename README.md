# MBL2PC - Modern Python 3.13 Messaging Service

[![CI](https://github.com/mikejsmtih1985/mbl2pc/workflows/CI/badge.svg)](https://github.com/mikejsmtih1985/mbl2pc/actions)
[![Code Quality](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked](https://img.shields.io/badge/typing-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

A modern, fully typed FastAPI application for sending messages and images from mobile devices to computers. Built with Python 3.13 and following industry best practices.

## ✨ Key Features

- **🐍 Modern Python 3.13** with cutting-edge language features and union type syntax
- **🔒 Type Safety** with Pydantic v2, MyPy strict mode, and comprehensive type annotations
- **🏗️ Dependency Injection** using protocols for excellent testability and clean architecture
- **🧪 Comprehensive Testing** - Unit, Integration, and E2E tests with 67%+ coverage
- **⚡ Code Quality** - Ruff for linting/formatting, MyPy for type checking, pre-commit hooks
- **☁️ Cloud Ready** - AWS DynamoDB and S3 integration with boto3
- **🔐 OAuth Authentication** via Google OAuth 2.0 with Authlib
- **🚀 FastAPI** with modern async/await patterns and automatic API documentation

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/mbl2pc.git
cd mbl2pc

# One-command setup (installs dependencies and pre-commit hooks)
make install

# Configure environment
cp .env.sample .env
# Edit .env with your credentials (see Getting Started guide)

# Start development server
make run
```

**🎯 Ready in under 5 minutes!** Visit `http://localhost:8000` to see your messaging interface.

## 📚 Documentation

### Getting Started
- **[📖 Getting Started Guide](docs/ONBOARDING.md)** - Complete setup walkthrough
- **[🏗️ Architecture Overview](docs/ARCHITECTURE.md)** - System design and patterns
- **[🔧 Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Development
- **[🤝 Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute to the project
- **[🚀 Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment options

### Reference
- **API Documentation**: `http://localhost:8000/docs` (when running)
- **Health Check**: `http://localhost:8000/health`
- **Version Info**: `http://localhost:8000/version`

## 🛠️ Development Commands

```bash
# Development workflow
make help          # Show all available commands
make dev           # Setup and run development environment
make test          # Run all tests with coverage
make ci            # Run complete CI pipeline (lint + type-check + test)

# Code quality
make lint          # Ruff linting
make format        # Ruff formatting
make type-check    # MyPy type checking

# Docker deployment
make docker-build  # Build production Docker image
make docker-run    # Run with Docker Compose
```

## 🏗️ Architecture Highlights

### Modern Python Patterns
```python
# Protocol-based dependency injection
@runtime_checkable
class MessageRepositoryProtocol(Protocol):
    async def add_message(self, message: Message) -> None: ...

# Type-safe configuration with validation
class Settings(BaseSettings):
    google_client_id: str = Field(..., description="Google OAuth client ID")

    @field_validator("session_secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SESSION_SECRET_KEY must be at least 32 characters")
        return v
```

### Clean Architecture
```
├── api/                 # FastAPI endpoints with dependency injection
├── core/               # Business logic, config, dependencies
│   ├── config.py       # Pydantic Settings with field validators
│   ├── storage.py      # Repository pattern with protocols
│   └── dependencies.py # Dependency injection configuration
├── schemas.py          # Pydantic v2 models with validation
└── main.py             # Application entry point
```

## 📊 Quality Metrics

```text
✅ Tests: 28/28 passing (100%)
✅ Coverage: 67%+ (above threshold)
✅ Type Safety: MyPy strict mode compliance
✅ Code Style: Ruff formatting and linting
✅ Python: 3.13 with modern features
```

## 🚀 Deployment Options

Choose your preferred deployment method:

1. **[Render.com](docs/DEPLOYMENT.md#rendercom-recommended)** - One-click deployment (recommended for beginners)
2. **[Docker](docs/DEPLOYMENT.md#docker-deployment)** - Containerized deployment for any platform
3. **[AWS Lambda](docs/DEPLOYMENT.md#aws-lambda-serverless)** - Serverless auto-scaling deployment
4. **[Traditional Server](docs/DEPLOYMENT.md#traditional-vpsserver)** - VPS/cloud instance deployment

Each option includes complete setup instructions and configuration examples.

## 🔧 Technology Stack

### Core Technologies
- **FastAPI**: Modern async web framework with automatic API docs
- **Python 3.13**: Latest Python with enhanced performance and syntax
- **Pydantic v2**: Data validation with improved performance
- **AWS**: DynamoDB (database) + S3 (file storage)
- **Google OAuth 2.0**: Secure authentication

### Development Tools
- **Ruff**: Modern linting and formatting (replaces black, flake8, isort)
- **MyPy**: Static type checking with strict configuration
- **pytest**: Testing with asyncio support and comprehensive fixtures
- **pre-commit**: Automated quality checks on commit

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for:

- **Development setup** and workflow
- **Code standards** and quality requirements
- **Testing guidelines** and coverage requirements
- **Pull request process** and review guidelines

### Quick Contribution Setup

```bash
# Fork and clone your fork
git clone https://github.com/yourusername/mbl2pc.git
cd mbl2pc

# Setup development environment
make install

# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
make ci

# Commit and push
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎯 Ready to get started?** Follow the [Getting Started Guide](docs/ONBOARDING.md) for a complete walkthrough, or jump to [Deployment](docs/DEPLOYMENT.md) if you're ready to go live!

## 🧪 Testing

### Running Tests

```bash
# All tests with coverage report
make test

# Specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # E2E tests only

# Parallel execution for faster CI
make test-parallel

# Coverage report with HTML output
pytest --cov=src/mbl2pc --cov-report=html
```

### Test Categories

- **Unit Tests**: Isolated component testing with mocked dependencies
- **Integration Tests**: API endpoint testing with FastAPI TestClient
- **E2E Tests**: Complete workflow testing with real authentication flow

## � Deployment

### Environment Variables for Production

```bash
# Required Production Environment Variables
GOOGLE_CLIENT_ID="production-google-oauth-client-id"
GOOGLE_CLIENT_SECRET="production-google-oauth-client-secret"
OAUTH_REDIRECT_URI="https://yourdomain.com/auth"
SESSION_SECRET_KEY="secure-random-32-character-minimum-key"

# AWS Configuration
AWS_REGION="us-east-1"
AWS_ACCESS_KEY_ID="production-aws-access-key"
AWS_SECRET_ACCESS_KEY="production-aws-secret-key"
MBL2PC_DDB_TABLE="mbl2pc-messages-prod"
S3_BUCKET="mbl2pc-images-prod"

# Optional: For monitoring and debugging
LOG_LEVEL="INFO"
```

### Deployment Options

#### 1. Render.com (Easiest)

The project includes `render.yaml` for one-click deployment:

1. Fork this repository
2. Connect your GitHub account to Render.com
3. Create new Web Service from your fork
4. Set environment variables in Render dashboard
5. Deploy automatically on git push

#### 2. AWS Lambda (Serverless)

```bash
# Install deployment dependencies
pip install mangum

# Add to main.py:
from mangum import Mangum
handler = Mangum(app)

# Deploy with AWS SAM, Serverless Framework, or AWS CDK
```

#### 3. Docker Deployment

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install -e ".[dev]"
EXPOSE 8000

CMD ["uvicorn", "src.mbl2pc.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t mbl2pc .
docker run -p 8000:8000 --env-file .env mbl2pc
```

#### 4. Production Server Setup

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn (production WSGI server)
gunicorn src.mbl2pc.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With systemd service (recommended)
sudo cp deploy/mbl2pc.service /etc/systemd/system/
sudo systemctl enable mbl2pc
sudo systemctl start mbl2pc
```

### Health Checks and Monitoring

The application includes built-in health endpoints:

- `GET /health` - Basic health check
- `GET /version` - Application version info
- `GET /docs` - Interactive API documentation

## 📊 Code Quality Metrics

Current quality metrics:

```text
✅ Tests: 28/28 passing (100%)
✅ Coverage: 67.29% (above 65% threshold)
✅ Type Safety: MyPy strict mode compliance
✅ Code Style: Ruff formatting and linting
✅ Security: OAuth 2.0 authentication
```

### Quality Tools

- **Ruff**: Modern linting and formatting (replaces black, flake8, isort)
- **MyPy**: Strict static type checking with Python 3.13 support
- **pytest**: Modern testing framework with asyncio support
- **pre-commit**: Automated quality checks on commit
- **structlog**: Structured logging for production observability

## 📦 Dependencies

### Core Production Dependencies

- **FastAPI**: Modern async web framework with automatic API documentation
- **Pydantic v2**: Data validation and serialization with enhanced performance
- **boto3**: AWS SDK for DynamoDB and S3 integration
- **Authlib**: OAuth 2.0 client implementation
- **uvicorn**: ASGI server for production deployment
- **structlog**: Structured logging for observability

### Development Dependencies

- **ruff**: Next-generation Python linter and formatter
- **mypy**: Static type checking with strict configuration
- **pytest ecosystem**: Comprehensive testing with asyncio, coverage, and parallel execution
- **pre-commit**: Git hooks for automated quality checks
- **boto3-stubs**: Type stubs for AWS SDK

## 🤝 Contributing

1. **Setup**: `make install` (installs dev dependencies and pre-commit hooks)
2. **Code**: Follow the established patterns with dependency injection and type safety
3. **Quality**: `make ci` (runs all quality checks)
4. **Test**: Ensure all tests pass and maintain coverage above 65%
5. **Submit**: Create a pull request with clear description

### Code Standards

- **Type Safety**: All functions must have complete type annotations
- **Testing**: New features require unit and integration tests
- **Documentation**: Public APIs need docstrings
- **Dependency Injection**: Use protocols for better testability

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using modern Python 3.13 and industry best practices**

*This application demonstrates advanced Python development patterns including dependency injection, protocol-based design, comprehensive testing, and production-ready deployment strategies.*
