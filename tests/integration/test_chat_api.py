"""
Integration tests for the Chat API endpoints using modern dependency injection.
"""

from fastapi.testclient import TestClient

from mbl2pc.schemas import User

# --- Mock User ---
MOCK_USER = User(sub="test-user-123", name="Test User", email="test@example.com")


# --- Tests ---
def test_send_message_unauthenticated(unauthenticated_client: TestClient) -> None:
    """
    Tests that an unauthenticated user cannot send a message.
    """
    response = unauthenticated_client.post(
        "/send", data={"msg": "Hello from test!", "sender": "tester"}
    )
    assert response.status_code == 401


def test_send_message_authenticated(authenticated_client: TestClient) -> None:
    """
    Tests that an authenticated user can successfully send a message.
    """
    response = authenticated_client.post(
        "/send", data={"msg": "Hello from test!", "sender": "tester"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "Message received"}


def test_send_image_unauthenticated(unauthenticated_client: TestClient) -> None:
    """
    Tests that an unauthenticated user cannot upload an image.
    """
    with open("static/send.html", "rb") as f:  # Using a dummy file for the test
        response = unauthenticated_client.post(
            "/send-image",
            files={"file": ("test.png", f, "image/png")},
            data={"text": "A test image"},
        )
    assert response.status_code == 401


def test_send_image_authenticated(authenticated_client: TestClient) -> None:
    """
    Tests that an authenticated user can successfully upload an image.
    """
    with open("static/send.html", "rb") as f:  # Using a dummy file for the test
        response = authenticated_client.post(
            "/send-image",
            files={"file": ("test.png", f, "image/png")},
            data={"text": "A test image"},
        )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Image received"
    assert response_json["image_url"].startswith(
        "https://mbl2pc-images.s3.amazonaws.com/img_"
    )


def test_get_messages_unauthenticated(unauthenticated_client: TestClient) -> None:
    """
    Tests that an unauthenticated user receives a 401 error.
    """
    response = unauthenticated_client.get("/messages")
    assert response.status_code == 401


def test_get_messages_authenticated(authenticated_client: TestClient) -> None:
    """
    Tests that an authenticated user can retrieve their messages.
    The mock table returns messages for multiple users, so we test
    that the API correctly filters for the logged-in user's messages.
    """
    response = authenticated_client.get("/messages")
    assert response.status_code == 200
    messages = response.json()["messages"]
    # The mock returns 3 messages, 2 for the authenticated user
    assert len(messages) == 2
    # The API doesn't return the user_id, so we can't check it here
    # We can only check that the correct number of messages are returned
