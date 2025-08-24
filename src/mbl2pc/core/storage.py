"""
Handles interactions with AWS services like DynamoDB and S3.
Uses modern dependency injection patterns for better testability.
"""

import contextlib
from collections.abc import AsyncGenerator
from typing import Any, Protocol, runtime_checkable

import boto3
from botocore.exceptions import ClientError
from fastapi import Depends

from mbl2pc.core.config import Settings, get_settings
from mbl2pc.schemas import Message


@runtime_checkable
class DynamoDBTableProtocol(Protocol):
    """Protocol for DynamoDB table operations with runtime checking."""

    def put_item(self, **kwargs: Any) -> Any:
        """Put an item into the table."""
        ...

    def scan(self, **kwargs: Any) -> Any:
        """Scan the table."""
        ...

    def query(self, **kwargs: Any) -> Any:
        """Query the table."""
        ...


@runtime_checkable
class S3ClientProtocol(Protocol):
    """Protocol for S3 client operations with runtime checking."""

    def upload_fileobj(
        self,
        fileobj: Any,
        bucket: str,
        key: str,
        ExtraArgs: dict[str, Any] | None = None,
    ) -> None:
        """Upload a file object to S3."""
        ...


@runtime_checkable
class MessageRepositoryProtocol(Protocol):
    """Protocol for message storage operations."""

    async def add_message(self, message: Message) -> None:
        """Add a message to storage."""
        ...

    async def get_messages(self, user_id: str, limit: int = 100) -> list[Message]:
        """Get messages for a user."""
        ...


class DynamoDBMessageRepository:
    """DynamoDB implementation of message repository."""

    def __init__(self, table: DynamoDBTableProtocol, settings: Settings) -> None:
        self.table = table
        self.settings = settings

    async def add_message(self, message: Message) -> None:
        """Add a message to DynamoDB."""
        try:
            self.table.put_item(Item=message.model_dump())
        except ClientError as e:
            raise RuntimeError(f"Failed to add message: {e}") from e

    async def get_messages(self, user_id: str, limit: int = 100) -> list[Message]:
        """Get messages for a user from DynamoDB."""
        try:
            response = self.table.scan()
            items = response.get("Items", [])

            # Filter by user_id and sort by timestamp
            user_items = [item for item in items if item.get("user_id") == user_id]
            user_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            # Convert to Message objects and limit results
            messages = []
            for item in user_items[:limit]:
                try:
                    message = Message(**item)
                    messages.append(message)
                except Exception:
                    # Skip invalid messages
                    continue

            return messages[::-1]  # Return in chronological order
        except ClientError as e:
            raise RuntimeError(f"Failed to get messages: {e}") from e


def get_db_table(settings: Settings = Depends(get_settings)) -> Any:  # type: ignore[return-value]
    """
    Dependency to get DynamoDB table resource.
    Note: Using Any return type due to boto3 typing complexity.
    """
    try:
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.DYNAMODB_ENDPOINT_URL,
        )
        return dynamodb.Table(settings.MBL2PC_DDB_TABLE)
    except ClientError as e:
        raise RuntimeError(f"Error getting DynamoDB table: {e}") from e


def get_s3_client(settings: Settings = Depends(get_settings)) -> Any:  # type: ignore[return-value]
    """
    Dependency to get S3 client.
    Note: Using Any return type due to boto3 typing complexity.
    """
    try:
        return boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )
    except ClientError as e:
        raise RuntimeError(f"Error getting S3 client: {e}") from e


def get_message_repository(
    table: DynamoDBTableProtocol = Depends(get_db_table),
    settings: Settings = Depends(get_settings),
) -> MessageRepositoryProtocol:
    """
    Dependency to get message repository with all its dependencies injected.
    """
    return DynamoDBMessageRepository(table, settings)


# Modern async context managers for resources
@contextlib.asynccontextmanager
async def get_db_table_context(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[DynamoDBTableProtocol]:
    """Async context manager for DynamoDB table with proper cleanup."""
    table = get_db_table(settings)
    try:
        yield table
    finally:
        # Cleanup if needed
        pass


@contextlib.asynccontextmanager
async def get_s3_client_context(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[S3ClientProtocol]:
    """Async context manager for S3 client with proper cleanup."""
    client = get_s3_client(settings)
    try:
        yield client
    finally:
        # Cleanup if needed
        pass


# Legacy functions - deprecated but maintained for backward compatibility
def get_legacy_db() -> Any:
    """Legacy function for getting database table - deprecated."""
    settings = get_settings()
    dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
    return dynamodb.Table(settings.MBL2PC_DDB_TABLE)


def add_message(message: Message) -> None:
    """Legacy function - deprecated, use MessageRepository instead."""
    table = get_legacy_db()
    table.put_item(Item=message.model_dump())


def get_messages(user_id: str) -> list[Message]:
    """Legacy function - deprecated, use MessageRepository instead."""
    table = get_legacy_db()
    response = table.scan()
    items = response.get("Items", [])

    user_items = [item for item in items if item.get("user_id") == user_id]
    return [Message(**item) for item in user_items]


def get_db():
    """Legacy function maintained for compatibility - deprecated."""
    return get_legacy_db()
