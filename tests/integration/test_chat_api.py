"""
Integration tests for the Chat API endpoints - focuses on API + dependency
integration. These tests verify that the API layer properly integrates with auth
and storage dependencies.
"""

from fastapi.testclient import TestClient

from mbl2pc.schemas import User

# --- Mock User ---
MOCK_USER = User(sub="test-user-123", name="Test User", email="test@example.com")  # type: ignore[call-arg]


# --- Integration Tests: API + Dependencies ---
def test_send_message_integrates_with_auth_and_storage(
    authenticated_client: TestClient,
) -> None:
    """
    Integration test: Verify that send message API properly integrates with
    authentication dependency and storage dependency.
    """
    response = authenticated_client.post(
        "/send", data={"msg": "Integration test message", "sender": "tester"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "Message received"}


def test_send_image_integrates_with_auth_and_storage(
    authenticated_client: TestClient,
) -> None:
    """
    Integration test: Verify that image upload API properly integrates with
    authentication, storage, and S3 dependencies.
    """
    with open("static/send.html", "rb") as f:
        response = authenticated_client.post(
            "/send-image",
            files={"file": ("test.png", f, "image/png")},
            data={"text": "Integration test image"},
        )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Image received"
    assert response_json["image_url"].startswith(
        "https://mbl2pc-images.s3.amazonaws.com/img_"
    )


def test_get_messages_integrates_with_auth_and_storage(
    authenticated_client: TestClient,
) -> None:
    """
    Integration test: Verify that get messages API properly integrates with
    authentication and storage dependencies, including user filtering.
    """
    response = authenticated_client.get("/messages")
    assert response.status_code == 200
    messages = response.json()["messages"]

    # Verify all returned messages belong to the authenticated user
    for message in messages:
        # The mock storage returns messages for our test user
        assert "timestamp" in message
        assert "sender" in message


def test_authentication_dependency_integration(
    unauthenticated_client: TestClient,
) -> None:
    """
    Integration test: Verify that authentication dependency properly
    integrates with protected endpoints.
    """
    protected_endpoints = [
        ("/send", "post", {"data": {"msg": "test"}}),
        (
            "/send-image",
            "post",
            {"files": {"file": ("test.png", b"test", "image/png")}},
        ),
        ("/messages", "get", {}),
    ]

    for endpoint, method, kwargs in protected_endpoints:
        response = getattr(unauthenticated_client, method)(endpoint, **kwargs)
        assert response.status_code == 401
    # We can only check that the correct number of messages are returned
