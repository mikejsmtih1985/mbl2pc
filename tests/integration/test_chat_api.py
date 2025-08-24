"""
Pytest tests for the Chat API endpoints.
"""
import os
import pytest
from fastapi.testclient import TestClient
from mbl2pc.main import app
from mbl2pc.core.dependencies import get_current_user
from mbl2pc.core.storage import get_db_table, get_s3_client
from mbl2pc.schemas import User

# --- Test Client Setup ---
client = TestClient(app)

# --- Mock User ---
MOCK_USER = User(sub="test-user-123", name="Test User", email="test@example.com")

# --- Mock Dependencies ---
def override_get_current_user():
    """Override dependency to return a mock user."""
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
                    "id": "1", "user_id": "test-user-123", "sender": "Test", 
                    "text": "Hello", "timestamp": "2023-01-01T12:00:00"
                },
                {
                    "id": "2", "user_id": "another-user", "sender": "Other", 
                    "text": "Hi", "timestamp": "2023-01-01T12:01:00"
                }
            ]
        }

class MockBoto3S3:
    """A mock class for the boto3 S3 client."""
    def upload_fileobj(self, file, bucket, key, ExtraArgs):
        print(f"Mock S3: upload_fileobj to {bucket}/{key}")
        pass # No-op

def override_get_db_table():
    """Override dependency to return a mock DynamoDB table."""
    return MockBoto3Table()

def override_get_s3_client():
    """Override dependency to return a mock S3 client."""
    return MockBoto3S3()

# --- Apply Overrides ---
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db_table] = override_get_db_table
app.dependency_overrides[get_s3_client] = override_get_s3_client


# --- API Tests ---
def test_send_message_authenticated():
    """
    Tests that an authenticated user can successfully send a message.
    """
    response = client.post("/send", data={"msg": "Hello from test!", "sender": "tester"})
    assert response.status_code == 200
    assert response.json()["status"] == "Message received"

def test_send_image_authenticated():
    """
    Tests that an authenticated user can successfully upload an image.
    """
    with open("static/send.html", "rb") as f: # Using a dummy file for the test
        response = client.post(
            "/send-image", 
            files={"file": ("test.png", f, "image/png")},
            data={"text": "A test image"}
        )
    assert response.status_code == 200
    assert response.json()["status"] == "Image received"
    assert "image_url" in response.json()

def test_get_messages_authenticated():
    """
    Tests that an authenticated user can retrieve their messages.
    The mock table returns messages for multiple users, so we test
    that the API correctly filters for the logged-in user's messages.
    """
    response = client.get("/messages")
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) == 1
    assert data["messages"][0]["text"] == "Hello"

# --- Unauthenticated Tests (by removing dependency override) ---
def test_get_messages_unauthenticated():
    """
    Tests that an unauthenticated user receives a 401 error.
    """
    app.dependency_overrides.clear() # Temporarily remove auth override
    response = client.get("/messages")
    assert response.status_code == 401
    # Restore overrides for other tests
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db_table] = override_get_db_table
    app.dependency_overrides[get_s3_client] = override_get_s3_client
