"""
Integration tests for the authentication API endpoints.
"""
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from mbl2pc.main import app

client = TestClient(app)

def test_login_redirects():
    """
    Tests that the /login endpoint correctly redirects to Google's OAuth service.
    """
    with patch('mbl2pc.api.auth.oauth') as mock_oauth:
        # Mock the authorize_redirect method to prevent an actual redirect in the test
        mock_oauth.google.authorize_redirect = AsyncMock(return_value=MagicMock(status_code=307))

        response = client.get("/login", follow_redirects=False)

        assert response.status_code == 307 # Check for redirect status
        mock_oauth.google.authorize_redirect.assert_called_once()

def test_logout_redirects():
    """
    Tests that the /logout endpoint clears the session and redirects to /login.
    """
    # Set a dummy session cookie to simulate a logged-in user
    client.cookies.set("session", "some-dummy-session-cookie")

    response = client.get("/logout", follow_redirects=False)

    # Check that the user is redirected to the login page
    assert response.status_code == 307
    assert response.headers["location"] == "/login"

    # Verify the session cookie was cleared
    assert "session" not in response.cookies

@patch('mbl2pc.api.auth.oauth')
async def test_auth_callback_success(mock_oauth):
    """
    Tests the successful authentication callback from Google.
    """
    # Mock the response from Google's authorize_access_token
    mock_token = {
        "userinfo": {
            "sub": "12345",
            "name": "Test User",
            "email": "test@example.com",
            "picture": "http://example.com/pic.jpg"
        }
    }
    # Use AsyncMock for awaitable methods
    mock_oauth.google.authorize_access_token = AsyncMock(return_value=mock_token)

    response = client.get("/auth", follow_redirects=False)

    # Check for redirect to the main application page
    assert response.status_code == 307
    assert response.headers["location"] == "/send.html"

    # Check that the user information is stored in the session
    assert "session" in response.cookies

@patch('mbl2pc.api.auth.oauth')
async def test_auth_callback_failure(mock_oauth):
    """
    Tests the authentication callback when Google returns an error or no user.
    """
    # Simulate an exception during token authorization
    mock_oauth.google.authorize_access_token = AsyncMock(side_effect=Exception("OAuth Failed"))

    response = client.get("/auth", follow_redirects=False)

    # Should redirect back to the login page on failure
    assert response.status_code == 307
    assert response.headers["location"] == "/login"
