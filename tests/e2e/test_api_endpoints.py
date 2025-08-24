"""
Simplified E2E API tests using the test client instead of a real server.
This provides E2E testing without the complexity of starting an external server process.
"""

import pytest
from fastapi.testclient import TestClient
import requests


def test_api_endpoints_work_end_to_end(authenticated_client: TestClient) -> None:
    """
    Test that the main API endpoints work together end-to-end.
    """
    # Test sending a message
    response = authenticated_client.post(
        "/send", 
        data={"msg": "End-to-end test message", "sender": "test"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "Message received"}
    
    # Test retrieving messages
    response = authenticated_client.get("/messages")
    assert response.status_code == 200
    messages = response.json()["messages"]
    
    # Should include our test message
    assert any("End-to-end test message" in msg.get("text", "") for msg in messages)


def test_authentication_flow_end_to_end(client: TestClient) -> None:
    """
    Test that authentication flow works end-to-end.
    """
    # Test unauthenticated access is blocked
    response = client.get("/messages")
    assert response.status_code == 401
    
    # Test that login redirect exists
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 302  # Redirect to OAuth provider


def test_static_files_served_correctly(client: TestClient) -> None:
    """
    Test that static files are served correctly.
    """
    # Test static HTML file exists
    response = client.get("/static/send.html")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()


def test_image_upload_flow_end_to_end(authenticated_client: TestClient) -> None:
    """
    Test the complete image upload flow.
    """
    # Create a test image-like file
    test_content = b"fake image content"
    
    response = authenticated_client.post(
        "/send-image",
        files={"file": ("test.png", test_content, "image/png")},
        data={"text": "Test image upload"}
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "Image received"
    assert "image_url" in response_data
    assert response_data["image_url"].startswith("https://")
