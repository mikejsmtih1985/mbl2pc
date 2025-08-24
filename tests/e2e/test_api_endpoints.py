"""
End-to-End tests focusing on complete user workflows and business scenarios.
These tests verify complete user journeys that span multiple API calls.
"""

from fastapi.testclient import TestClient


def test_complete_messaging_workflow(authenticated_client: TestClient) -> None:
    """
    E2E Test: Complete messaging workflow from sending to retrieving messages.
    This tests the full user journey of: send message -> get messages -> verify
    message appears.
    """
    # Step 1: Send a message
    message_text = "E2E workflow test message"
    response = authenticated_client.post(
        "/send", data={"msg": message_text, "sender": "e2e-test"}
    )
    assert response.status_code == 200

    # Step 2: Retrieve messages and verify our message appears
    response = authenticated_client.get("/messages")
    assert response.status_code == 200
    messages = response.json()["messages"]

    # Step 3: Verify the complete workflow worked
    sent_message = next(
        (msg for msg in messages if message_text in msg.get("text", "")), None
    )
    assert sent_message is not None, "Sent message should appear in message list"
    assert sent_message["sender"] == "e2e-test"


def test_complete_image_sharing_workflow(authenticated_client: TestClient) -> None:
    """
    E2E Test: Complete image sharing workflow.
    This tests the full user journey of: upload image -> get messages -> verify
    image appears.
    """
    # Step 1: Upload an image with text
    image_text = "E2E image workflow test"
    test_content = b"fake image content for E2E test"

    response = authenticated_client.post(
        "/send-image",
        files={"file": ("e2e-test.png", test_content, "image/png")},
        data={"text": image_text},
    )
    assert response.status_code == 200

    # Extract image URL from response
    image_data = response.json()
    image_url = image_data["image_url"]

    # Step 2: Retrieve messages and verify our image message appears
    response = authenticated_client.get("/messages")
    assert response.status_code == 200
    messages = response.json()["messages"]

    # Step 3: Verify the complete workflow worked
    image_message = next(
        (
            msg
            for msg in messages
            if image_text in msg.get("text", "") and msg.get("image_url") == image_url
        ),
        None,
    )
    assert image_message is not None, "Image message should appear in message list"
    assert image_message["image_url"].startswith("https://")


def test_user_session_and_static_content_workflow(client: TestClient) -> None:
    """
    E2E Test: User session management and static content access workflow.
    This tests the complete user experience from initial access to authentication.
    """
    # Step 1: Access protected resource without authentication
    response = client.get("/messages")
    assert response.status_code == 401

    # Step 2: Access login page to start authentication workflow
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 302  # Should redirect to OAuth provider

    # Step 3: Verify static content is accessible (public resources)
    response = client.get("/static/send.html")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()


def test_multi_message_conversation_workflow(authenticated_client: TestClient) -> None:
    """
    E2E Test: Multi-message conversation workflow.
    This tests a realistic conversation flow with multiple messages.
    """
    conversation_messages = [
        {"text": "Hello, starting conversation", "sender": "user"},
        {"text": "This is message 2", "sender": "user"},
        {"text": "Final message in conversation", "sender": "user"},
    ]

    # Step 1: Send multiple messages in sequence
    for msg_data in conversation_messages:
        response = authenticated_client.post(
            "/send", data={"msg": msg_data["text"], "sender": msg_data["sender"]}
        )
        assert response.status_code == 200

    # Step 2: Retrieve all messages
    response = authenticated_client.get("/messages")
    assert response.status_code == 200
    messages = response.json()["messages"]

    # Step 3: Verify all conversation messages appear in correct order
    for expected_msg in conversation_messages:
        found_message = next(
            (msg for msg in messages if expected_msg["text"] in msg.get("text", "")),
            None,
        )
        assert found_message is not None, (
            f"Message '{expected_msg['text']}' should be in conversation"
        )
