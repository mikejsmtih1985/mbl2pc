# Contributing to MBL2PC

Thank you for your interest in contributing to MBL2PC! This guide will help you get started with contributing to this modern Python 3.13 project.

## Development Setup

### Quick Start

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/mbl2pc.git
cd mbl2pc

# Install development dependencies and pre-commit hooks
make install

# Run tests to verify setup
make test

# Start development server
make run
```

### Development Environment

- **Python 3.13+** (required)
- **Pre-commit hooks** (automatically installed)
- **Modern tooling** (Ruff, MyPy, pytest)

## Code Standards

### Type Safety

All code must have complete type annotations:

```python
# ✅ Good - Complete type annotations
async def send_message(
    message_data: MessageCreate,
    repository: MessageRepositoryProtocol = Depends(get_message_repository),
    current_user: User = Depends(get_current_user)
) -> MessageResponse:
    pass

# ❌ Bad - Missing type annotations
async def send_message(message_data, repository, current_user):
    pass
```

### Code Quality

We use modern Python tooling for code quality:

```bash
# Linting and formatting (pre-commit hook)
make lint      # Ruff linting
make format    # Ruff formatting

# Type checking (pre-commit hook)
make type-check  # MyPy strict mode

# Run all quality checks
make ci
```

### Dependency Injection

Follow the established dependency injection patterns:

```python
# ✅ Good - Protocol-based dependency injection
from typing import Protocol

@runtime_checkable
class ServiceProtocol(Protocol):
    async def process(self, data: str) -> str: ...

class MyService:
    def __init__(self, service: ServiceProtocol) -> None:
        self._service = service

# ❌ Bad - Direct instantiation
class MyService:
    def __init__(self) -> None:
        self._service = ConcreteService()  # Hard to test
```

## Testing Guidelines

### Test Structure

Follow the established test pyramid:

```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # API endpoint tests
└── e2e/           # Full workflow tests
```

### Writing Tests

#### Unit Tests

```python
# Test pure logic with mocked dependencies
class TestMessageService:
    def test_message_validation(self, mock_repository):
        service = MessageService(mock_repository)
        # Test the logic
```

#### Integration Tests

```python
# Test API endpoints with FastAPI TestClient
def test_send_message_endpoint(client, auth_headers):
    response = client.post("/messages", json={"text": "test"}, headers=auth_headers)
    assert response.status_code == 201
```

#### E2E Tests

```python
# Test complete workflows
def test_complete_messaging_workflow(client):
    # Test authentication → send message → retrieve messages
```

### Test Requirements

- **Coverage**: Maintain 65%+ test coverage
- **All tests pass**: `make test` must pass
- **Fast execution**: Unit tests should be < 1s each
- **Isolated**: Tests should not depend on each other

## Pull Request Process

### 1. Preparation

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... code changes ...

# Run quality checks
make ci

# Commit changes (pre-commit hooks will run)
git commit -m "feat: add your feature description"
```

### 2. Quality Checklist

Before submitting a PR, ensure:

- [ ] **All tests pass**: `make test`
- [ ] **Type checking passes**: `make type-check`
- [ ] **Linting passes**: `make lint`
- [ ] **Coverage maintained**: Above 65%
- [ ] **Documentation updated**: If adding new features
- [ ] **Commit messages follow convention**: See below

### 3. Commit Message Convention

Use conventional commits for clear history:

```
feat: add new messaging feature
fix: resolve OAuth callback issue
docs: update API documentation
test: add unit tests for storage layer
refactor: improve dependency injection pattern
style: format code with Ruff
perf: optimize message retrieval query
```

### 4. Pull Request Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
```

## Architecture Guidelines

### Adding New Features

When adding new features, follow these patterns:

#### 1. Create Protocol Interface

```python
# Define the interface
from typing import Protocol

@runtime_checkable
class NewServiceProtocol(Protocol):
    async def process(self, data: str) -> Result: ...
```

#### 2. Implement Concrete Class

```python
# Implement the interface
class ConcreteNewService:
    def __init__(self, dependency: SomeDependency) -> None:
        self._dependency = dependency

    async def process(self, data: str) -> Result:
        # Implementation
```

#### 3. Add Dependency Injection

```python
# Add to dependencies.py
def get_new_service(
    dependency: SomeDependency = Depends(get_dependency)
) -> NewServiceProtocol:
    return ConcreteNewService(dependency)
```

#### 4. Use in Endpoints

```python
# Use in API endpoints
@router.post("/endpoint")
async def endpoint(
    service: NewServiceProtocol = Depends(get_new_service)
) -> Response:
    result = await service.process(data)
    return Response(result)
```

### Database Changes

For DynamoDB schema changes:

1. **Update Pydantic models** in `schemas.py`
2. **Add migration script** if needed
3. **Update repository methods**
4. **Add comprehensive tests**
5. **Document breaking changes**

### API Changes

For API endpoint changes:

1. **Maintain backward compatibility** when possible
2. **Version APIs** for breaking changes
3. **Update OpenAPI documentation**
4. **Add integration tests**
5. **Update client examples**

## Code Review Guidelines

### As a Reviewer

- **Focus on architecture** and design patterns
- **Check test coverage** for new features
- **Verify type safety** is maintained
- **Look for security issues** (input validation, authentication)
- **Ensure documentation** is updated

### Common Review Points

1. **Type Annotations**: All functions must have complete types
2. **Error Handling**: Proper exception handling and logging
3. **Security**: Input validation, authentication checks
4. **Performance**: Async/await usage, efficient queries
5. **Testing**: Adequate test coverage and quality

## Development Workflow

### Branch Strategy

- **main**: Production-ready code
- **feature/**: New features
- **fix/**: Bug fixes
- **docs/**: Documentation updates

### Release Process

1. **Feature development** on feature branches
2. **Pull request review** and testing
3. **Merge to main** after approval
4. **Automated deployment** (if configured)
5. **Tag releases** for version tracking

## Getting Help

### Resources

- **Architecture Guide**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Documentation**: Run server and visit `/docs`
- **Issue Templates**: Use GitHub issue templates
- **Discussions**: GitHub Discussions for questions

### Common Issues

#### Development Setup

```bash
# Python version issues
pyenv install 3.13.7
pyenv local 3.13.7

# Dependency issues
pip install -e ".[dev]" --force-reinstall

# Pre-commit issues
pre-commit install --force
```

#### Testing Issues

```bash
# Clear cache if tests behave strangely
make clean
make test

# Run specific test category
make test-unit
make test-integration
```

#### Type Checking Issues

```bash
# Common MyPy fixes
# Add type ignores for external libraries
import external_lib  # type: ignore[import-untyped]

# Use protocols for complex dependencies
from typing import Protocol
```

## Project Conventions

### File Organization

```
src/mbl2pc/
├── api/                 # API endpoints (one file per domain)
├── core/               # Core business logic
│   ├── config.py       # Configuration management
│   ├── dependencies.py # Dependency injection
│   └── storage.py      # Data access layer
├── schemas.py          # Pydantic models
└── main.py             # Application entry point
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_CASE`
- **Protocols**: `NameProtocol`

### Import Organization

```python
# Standard library
import asyncio
from datetime import datetime

# Third-party
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# Local imports
from mbl2pc.core.config import Settings
from mbl2pc.schemas import Message
```

---

**Ready to contribute?** Start with a small issue labeled "good first issue" and follow this guide. We appreciate your contributions!
