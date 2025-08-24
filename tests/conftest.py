"""
Configuration for pytest.
"""

import pytest
from fastapi.testclient import TestClient

from mbl2pc.core.dependencies import get_current_user
from mbl2pc.core.storage import get_db_table, get_s3_client
from mbl2pc.main import app
from mbl2pc.schemas import User

MOCK_USER = User(sub="test-user-123", name="Test User", email="test@example.com")


def override_get_current_user():
    """
    Mock dependency to override get_current_user.
    """
    return MOCK_USER


class MockBoto3Table:
    """A mock class for boto3's DynamoDB Table resource."""

    def put_item(self, Item):
        print(f"Mock DynamoDB: put_item({Item})")
        pass  # No-op for testing

    def scan(self):
        print("Mock DynamoDB: scan()")
        return {
            "Items": [
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
                    "text": "Hi",
                    "timestamp": "2023-01-01T12:01:00",
                },
            ]
        }


class MockBoto3S3:
    """A mock class for the boto3 S3 client."""

    def upload_fileobj(self, file, bucket, key, ExtraArgs):
        print(f"Mock S3: upload_fileobj to {bucket}/{key}")
        pass  # No-op


def override_get_db_table():
    """Override dependency to return a mock DynamoDB table."""
    return MockBoto3Table()


def override_get_s3_client():
    """Override dependency to return a mock S3 client."""
    return MockBoto3S3()


@pytest.fixture
def client():
    """
    Returns a test client with AWS dependencies mocked.
    """
    app.dependency_overrides[get_db_table] = override_get_db_table
    app.dependency_overrides[get_s3_client] = override_get_s3_client
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


@pytest.fixture
def authenticated_client(client):
    """
    Returns a test client with an authenticated user.
    """
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    del app.dependency_overrides[get_current_user]


@pytest.fixture
def unauthenticated_client(client):
    """
    Returns a test client without any authenticated user.
    """
    yield client
