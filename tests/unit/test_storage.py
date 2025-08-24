"""
Unit tests for the message repository.
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from mbl2pc.core.config import Settings
from mbl2pc.core.storage import DynamoDBMessageRepository
from mbl2pc.schemas import Message


class TestDynamoDBMessageRepository:
    """Test suite for DynamoDBMessageRepository."""

    @pytest.fixture
    def mock_table(self) -> MagicMock:
        """Create a mock DynamoDB table."""
        return MagicMock()

    @pytest.fixture
    def settings(self) -> Settings:
        """Create test settings."""
        return Settings()  # type: ignore[call-arg]

    @pytest.fixture
    def repository(
        self, mock_table: MagicMock, settings: Settings
    ) -> DynamoDBMessageRepository:
        """Create a repository instance with mocked dependencies."""
        return DynamoDBMessageRepository(mock_table, settings)

    async def test_add_message_success(
        self, repository: DynamoDBMessageRepository, mock_table: MagicMock
    ) -> None:
        """Test successful message addition."""
        message = Message(
            sender="test",
            text="Hello world",
            user_id="user123",
            timestamp=datetime.now(UTC),
        )  # type: ignore[call-arg]

        await repository.add_message(message)

        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args[1]["Item"]
        assert call_args["text"] == "Hello world"
        assert call_args["user_id"] == "user123"

    async def test_add_message_client_error(
        self, repository: DynamoDBMessageRepository, mock_table: MagicMock
    ) -> None:
        """Test message addition with DynamoDB client error."""
        mock_table.put_item.side_effect = ClientError(
            {"Error": {"Code": "ValidationException"}}, "PutItem"
        )

        message = Message(
            sender="test",
            text="Hello world",
            user_id="user123",
            timestamp=datetime.now(UTC),
        )  # type: ignore[call-arg]

        with pytest.raises(RuntimeError, match="Failed to add message"):
            await repository.add_message(message)

    async def test_get_messages_success(
        self, repository: DynamoDBMessageRepository, mock_table: MagicMock
    ) -> None:
        """Test successful message retrieval."""
        mock_table.scan.return_value = {
            "Items": [
                {
                    "id": "1",
                    "user_id": "user123",
                    "sender": "test",
                    "text": "Hello",
                    "image_url": "",
                    "timestamp": datetime.now(UTC),
                },
                {
                    "id": "2",
                    "user_id": "other_user",
                    "sender": "other",
                    "text": "Different user",
                    "image_url": "",
                    "timestamp": datetime.now(UTC),
                },
            ]
        }

        messages = await repository.get_messages("user123", limit=10)

        assert len(messages) == 1
        assert messages[0].text == "Hello"
        assert messages[0].user_id == "user123"

    async def test_get_messages_client_error(
        self, repository: DynamoDBMessageRepository, mock_table: MagicMock
    ) -> None:
        """Test message retrieval with DynamoDB client error."""
        mock_table.scan.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "Scan"
        )

        with pytest.raises(RuntimeError, match="Failed to get messages"):
            await repository.get_messages("user123")
