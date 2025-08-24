"""
Handles interactions with AWS services like DynamoDB and S3.
Uses dependency injection for better testability.
"""

import contextlib
import datetime
import uuid
from collections.abc import AsyncGenerator
from typing import Any, Protocol, runtime_checkable

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from ..schemas import Message
from .config import settings


@runtime_checkable
class DynamoDBTableProtocol(Protocol):
    """Enhanced protocol for DynamoDB table operations with runtime checking."""

    def put_item(self, Item: dict[str, Any]) -> dict[str, Any]:
        """Put an item into the table."""
        ...

    def scan(self, **kwargs: Any) -> dict[str, Any]:
        """Scan the table."""
        ...

    def query(self, **kwargs: Any) -> dict[str, Any]:
        """Query the table."""
        ...


@runtime_checkable
class S3ClientProtocol(Protocol):
    """Enhanced protocol for S3 client operations with runtime checking."""

    def upload_fileobj(
        self,
        fileobj: Any,
        bucket: str,
        key: str,
        ExtraArgs: dict[str, Any] | None = None,
    ) -> None:
        """Upload a file object to S3."""
        ...


def get_db_table() -> DynamoDBTableProtocol:
    """
    Returns a DynamoDB table resource with dependency injection support.
    """
    try:
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.DYNAMODB_ENDPOINT_URL,
        )
        return dynamodb.Table(settings.MBL2PC_DDB_TABLE)
    except ClientError as e:
        print(f"Error getting DynamoDB table: {e}")
        raise


def get_s3_client() -> S3ClientProtocol:
    """
    Returns an S3 client with dependency injection support.
    """
    try:
        return boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )
    except ClientError as e:
        print(f"Error getting S3 client: {e}")
        raise


# Modern async context manager for resources
@contextlib.asynccontextmanager
async def get_db_table_context() -> AsyncGenerator[DynamoDBTableProtocol]:
    """Async context manager for DynamoDB table with proper cleanup."""
    table = get_db_table()
    try:
        yield table
    finally:
        # Cleanup if needed
        pass


@contextlib.asynccontextmanager
async def get_s3_client_context() -> AsyncGenerator[S3ClientProtocol]:
    """Async context manager for S3 client with proper cleanup."""
    client = get_s3_client()
    try:
        yield client
    finally:
        # Cleanup if needed
        pass


# Legacy session-based approach (maintained for backward compatibility)
session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    aws_session_token=settings.AWS_SESSION_TOKEN,
    region_name=settings.AWS_REGION,
)


def get_legacy_db() -> DynamoDBTableProtocol:
    """Legacy function for getting database table."""
    dynamodb = session.resource("dynamodb")
    return dynamodb.Table(settings.MBL2PC_DDB_TABLE)


def add_message(message: Message) -> None:
    """Add a message using legacy approach."""
    table = get_legacy_db()
    now = datetime.datetime.now(datetime.UTC).isoformat()
    table.put_item(
        Item={
            "pk": message.user_id,
            "sk": f"{now}#{uuid.uuid4()}",
            "message": message.text if hasattr(message, "text") else message.message,
        }
    )


def get_messages(user_id: str) -> list[Message]:
    """Get messages using legacy approach."""
    table = get_legacy_db()
    response = table.query(KeyConditionExpression=Key("pk").eq(user_id))
    return [
        Message(user_id=item["pk"], text=item.get("message", ""))
        for item in response["Items"]
    ]


def get_db():
    """Legacy function maintained for compatibility."""
    return get_legacy_db()
