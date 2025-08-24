"""
Modern pytest configuration with Python 3.13 features.
Enhanced dependency injection patterns for better testability.
"""

from collections.abc import Generator
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from mbl2pc.core.dependencies import get_current_user
from mbl2pc.core.storage import (
    get_db_table,
    get_message_repository,
    get_s3_client,
)
from mbl2pc.main import app
from mbl2pc.schemas import Message, User

MOCK_USER = User(sub="test-user-123", name="Test User", email="test@example.com")


# Modern fixture with proper typing
@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio backend for async tests."""
    return "asyncio"


def create_mock_user() -> User:
    """Factory function to create mock authenticated user."""
    return MOCK_USER


class MockDynamoDBTable:
    """Mock DynamoDB table with proper typing and modern Python patterns."""

    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = [
            {
                "id": "1",
                "user_id": "test-user-123",
                "sender": "Test",
                "text": "Hello",
                "timestamp": "2023-01-01T12:00:00",
            },
            {
                "id": "2",
                "user_id": "test-user-123",
                "sender": "Other",
                "text": "Hi",
                "timestamp": "2023-01-01T12:01:00",
            },
            {
                "id": "3",
                "user_id": "another-user",
                "sender": "Other",
                "text": "Different user message",
                "timestamp": "2023-01-01T12:02:00",
            },
        ]

    def put_item(self, Item: dict[str, Any]) -> dict[str, Any]:
        """Mock put_item operation."""
        print(f"Mock DynamoDB: put_item({Item})")
        self._items.append(Item)
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def scan(self) -> dict[str, Any]:
        """Mock scan operation."""
        print("Mock DynamoDB: scan()")
        return {"Items": self._items}


class MockS3Client:
    """Mock S3 client with proper typing and modern Python patterns."""

    def upload_fileobj(
        self,
        fileobj: Any,  # noqa: ARG002
        bucket: str,
        key: str,
        ExtraArgs: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> None:
        """Mock upload_fileobj operation."""
        print(f"Mock S3: upload_fileobj to {bucket}/{key}")
        # Simulate successful upload


class MockMessageRepository:
    """Mock message repository for testing."""

    def __init__(self) -> None:
        self._messages: list[Message] = [
            Message(
                id="1",
                user_id="test-user-123",
                sender="Test",
                text="Hello",
                timestamp=datetime.fromisoformat("2023-01-01T12:00:00"),
            ),
            Message(
                id="2",
                user_id="test-user-123",
                sender="Other",
                text="Hi",
                timestamp=datetime.fromisoformat("2023-01-01T12:01:00"),
            ),
            Message(
                id="3",
                user_id="another-user",
                sender="Other",
                text="Different user message",
                timestamp=datetime.fromisoformat("2023-01-01T12:02:00"),
            ),
        ]

    async def add_message(self, message: Message) -> None:
        """Mock add_message operation."""
        print(f"Mock Repository: add_message({message})")
        self._messages.append(message)

    async def get_messages(self, user_id: str, limit: int = 100) -> list[Message]:
        """Mock get_messages operation."""
        print(f"Mock Repository: get_messages({user_id}, {limit})")
        user_messages = [msg for msg in self._messages if msg.user_id == user_id]
        return user_messages[:limit]


@pytest.fixture
def mock_db_table() -> MockDynamoDBTable:
    """Fixture providing a mock DynamoDB table."""
    return MockDynamoDBTable()


@pytest.fixture
def mock_s3_client() -> MockS3Client:
    """Fixture providing a mock S3 client."""
    return MockS3Client()


@pytest.fixture
def mock_message_repository() -> MockMessageRepository:
    """Fixture providing a mock message repository."""
    return MockMessageRepository()


@pytest.fixture
def client(
    mock_db_table: MockDynamoDBTable,
    mock_s3_client: MockS3Client,
    mock_message_repository: MockMessageRepository,
) -> Generator[TestClient]:
    """
    Enhanced test client with AWS dependencies properly mocked
    using dependency injection.
    """
    # Override dependencies with our mocks
    app.dependency_overrides[get_db_table] = lambda: mock_db_table
    app.dependency_overrides[get_s3_client] = lambda: mock_s3_client
    app.dependency_overrides[get_message_repository] = lambda: mock_message_repository

    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        # Explicit cleanup
        app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client: TestClient) -> Generator[TestClient]:
    """
    Test client with an authenticated user using dependency injection.
    """
    app.dependency_overrides[get_current_user] = create_mock_user
    try:
        yield client
    finally:
        # Remove only the user override, keep others
        app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def unauthenticated_client(client: TestClient) -> Generator[TestClient]:
    """
    Test client without authentication - dependency injection ensures 401s.
    """
    # Ensure no user override is present
    app.dependency_overrides.pop(get_current_user, None)
    try:
        yield client
    finally:
        pass
