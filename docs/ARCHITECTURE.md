# Architecture Overview

MBL2PC is built using modern Python 3.13 with a focus on type safety, dependency injection, and clean architecture patterns.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   AWS Services  │
│   (Static HTML) │◄──►│   Backend       │◄──►│   (DynamoDB/S3) │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Google OAuth    │
                       │ Authentication  │
                       └─────────────────┘
```

## Technology Stack

### Core Framework
- **FastAPI**: Modern async web framework with automatic API documentation
- **Python 3.13**: Latest Python with modern syntax and performance improvements
- **Pydantic v2**: Data validation and serialization with enhanced performance
- **Uvicorn**: ASGI server for production deployment

### Database & Storage
- **AWS DynamoDB**: NoSQL database for message storage
- **AWS S3**: Object storage for images and files
- **boto3**: AWS SDK for Python

### Authentication
- **Google OAuth 2.0**: User authentication via Google accounts
- **Authlib**: OAuth client implementation
- **Session management**: Secure session handling with FastAPI

### Development Tools
- **Ruff**: Modern linting and formatting (replaces black, flake8, isort)
- **MyPy**: Static type checking with strict configuration
- **pytest**: Testing framework with asyncio support
- **pre-commit**: Git hooks for automated quality checks

## Project Structure

```
mbl2pc/
├── src/mbl2pc/              # Main application code
│   ├── api/                 # API endpoints
│   │   ├── auth.py         # Authentication endpoints
│   │   └── chat.py         # Message/image endpoints
│   ├── core/               # Core business logic
│   │   ├── config.py       # Configuration management
│   │   ├── dependencies.py # Dependency injection
│   │   ├── exceptions.py   # Custom exception hierarchy
│   │   ├── logging.py      # Structured logging
│   │   └── storage.py      # Data access layer
│   ├── schemas.py          # Pydantic data models
│   └── main.py             # Application entry point
├── static/                 # Frontend assets
│   └── send.html          # Web interface
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
└── docs/                   # Documentation
```

## Design Patterns

### 1. Dependency Injection

The application uses protocol-based dependency injection for better testability:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class MessageRepositoryProtocol(Protocol):
    async def add_message(self, message: Message) -> None: ...
    async def get_messages(self, user_id: str, limit: int = 100) -> list[Message]: ...

class DynamoDBMessageRepository:
    def __init__(self, table: DynamoDBTableProtocol, settings: Settings):
        self._table = table
        self._settings = settings

    async def add_message(self, message: Message) -> None:
        # Implementation
```

### 2. Repository Pattern

Data access is abstracted through repository interfaces:

```python
# Protocol defines the interface
class MessageRepositoryProtocol(Protocol):
    async def add_message(self, message: Message) -> None: ...

# Concrete implementation
class DynamoDBMessageRepository:
    # Actual DynamoDB implementation

# Easy to mock for testing
class MockMessageRepository:
    # In-memory implementation for tests
```

### 3. Configuration Management

Environment-based configuration with validation:

```python
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class Settings(BaseSettings):
    google_client_id: str = Field(..., description="Google OAuth client ID")
    session_secret_key: str = Field(..., min_length=32)

    @field_validator("session_secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SESSION_SECRET_KEY must be at least 32 characters")
        return v
```

## Data Flow

### 1. Authentication Flow

```
User → Frontend → /login → Google OAuth → /auth callback → Session → Frontend
```

1. User clicks "Login with Google"
2. Frontend redirects to `/login` endpoint
3. FastAPI redirects to Google OAuth
4. User authenticates with Google
5. Google redirects to `/auth` callback
6. FastAPI creates secure session
7. User redirected to messaging interface

### 2. Message Flow

```
User → Frontend → /messages → Repository → DynamoDB → Response → Frontend
```

1. User types message in frontend
2. JavaScript sends POST to `/messages`
3. FastAPI validates and processes
4. Repository stores in DynamoDB
5. Response sent back to frontend
6. Frontend updates UI

### 3. Image Upload Flow

```
User → Frontend → /images → S3 Upload → Message with URL → DynamoDB
```

1. User selects image file
2. Frontend sends multipart form to `/images`
3. FastAPI uploads to S3 bucket
4. S3 URL stored in message
5. Message with image URL saved to DynamoDB

## Type Safety

The application maintains 100% type coverage:

```python
# All functions have complete type annotations
async def send_message(
    message_data: MessageCreate,
    repository: MessageRepositoryProtocol = Depends(get_message_repository),
    current_user: User = Depends(get_current_user)
) -> MessageResponse:
    # Implementation with full type safety

# Pydantic models ensure runtime validation
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    sender: str
    text: str
    image_url: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

## Error Handling

### Custom Exception Hierarchy

```python
class MBL2PCError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}

class ValidationError(MBL2PCError):
    """Data validation errors."""

class AuthenticationError(MBL2PCError):
    """Authentication and authorization errors."""

class StorageError(MBL2PCError):
    """Database and storage errors."""
```

### Error Response Format

```python
{
    "error": {
        "type": "ValidationError",
        "message": "Invalid message format",
        "code": "INVALID_MESSAGE",
        "details": {
            "field": "text",
            "constraint": "max_length"
        }
    }
}
```

## Security

### Authentication Security
- **OAuth 2.0**: Industry-standard authentication
- **Session Management**: Secure session cookies
- **CSRF Protection**: Built into OAuth flow
- **Secret Management**: Environment variables only

### Data Security
- **Input Validation**: Pydantic models validate all input
- **SQL Injection**: Not applicable (NoSQL DynamoDB)
- **File Upload**: Validated file types and sizes
- **AWS IAM**: Least-privilege access policies

### Configuration Security
- **Environment Variables**: No secrets in code
- **Session Secrets**: 32+ character random keys
- **AWS Credentials**: IAM roles in production
- **HTTPS**: Required for production OAuth

## Performance

### Async/Await
- **Non-blocking I/O**: All database operations are async
- **Concurrent Requests**: FastAPI handles multiple requests efficiently
- **Connection Pooling**: boto3 handles AWS connection pooling

### Caching Strategy
- **Static Assets**: Served with appropriate cache headers
- **API Responses**: Can add Redis for response caching
- **Session Storage**: In-memory sessions (can upgrade to Redis)

### Monitoring
- **Health Endpoints**: `/health` for basic monitoring
- **Structured Logging**: JSON logs for observability
- **Error Tracking**: Ready for Sentry integration
- **Metrics**: Ready for Prometheus/CloudWatch

## Testing Strategy

### Test Pyramid

```
    /\     E2E Tests (4 tests)
   /  \    Full workflow testing
  /____\
 /      \  Integration Tests (7 tests)
/        \ API endpoint testing
\________/
 \      /  Unit Tests (17 tests)
  \____/   Component isolation testing
```

### Test Categories

1. **Unit Tests**: Pure logic testing with mocked dependencies
2. **Integration Tests**: API testing with FastAPI TestClient
3. **E2E Tests**: Complete workflow testing with authentication

### Test Fixtures

```python
# Dependency injection makes testing easy
@pytest.fixture
def mock_repository():
    return MockMessageRepository()

def test_send_message(mock_repository):
    # Test uses mock instead of real DynamoDB
    pass
```

## Deployment Architecture

### Production Components

```
Internet → Load Balancer → Application Servers → AWS Services
                ↓
            TLS/SSL Certificates
                ↓
            WAF (Web Application Firewall)
                ↓
            Auto Scaling Groups
                ↓
            Health Checks
```

### Scalability

- **Horizontal Scaling**: Multiple application instances
- **Database Scaling**: DynamoDB auto-scaling
- **Storage Scaling**: S3 unlimited storage
- **CDN**: CloudFront for static assets

## Development Workflow

### Code Quality Pipeline

```
Developer → Pre-commit Hooks → CI Pipeline → Deployment
    ↓              ↓               ↓            ↓
Local Tests → Linting/Format → Full Test Suite → Production
```

### Quality Gates

1. **Pre-commit**: Ruff formatting, MyPy type checking
2. **CI Pipeline**: Full test suite, coverage check
3. **Code Review**: Manual review process
4. **Deployment**: Automated with health checks

---

For implementation details, see:
- [ONBOARDING.md](ONBOARDING.md) - Getting started
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment strategies
