"""
Integration tests for the authentication API endpoints.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from mbl2pc.main import app
from src.mbl2pc.core.config import Settings, get_settings


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_settings():
    return Settings(
        GOOGLE_CLIENT_ID="test_id",
        GOOGLE_CLIENT_SECRET="test_secret",
        SESSION_SECRET_KEY="test_session_secret",
    )


@pytest.fixture(autouse=True)
def _override_settings(test_settings):
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield
    app.dependency_overrides = {}


def test_login_redirects(client, test_settings):  # noqa: ARG001
    """
    Test that the /login route redirects to the Google OAuth URL.
    """
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 302  # Found
    assert "accounts.google.com" in response.headers["location"]


def test_auth_callback_success(client, mocker, test_settings):  # noqa: ARG001
    """
    Test the /auth callback with a successful token exchange.
    """
    # Mock the OAuth client's fetch_token method to return a dummy token
    mock_token = {
        "access_token": "dummy_token",
        "userinfo": {"sub": "123", "name": "Test User", "email": "test@example.com"},
    }

    # We need to access the oauth object that is configured with the test settings
    from src.mbl2pc.core.config import oauth

    # Patch the oauth object
    mocker.patch.object(
        oauth.google,
        "authorize_access_token",
        new_callable=AsyncMock,
        return_value=mock_token,
    )

    # Make the request to the /auth endpoint
    response = client.get("/auth", follow_redirects=False)

    # Assert that the user is redirected to the send page
    assert response.status_code == 307
    assert response.headers["location"] == "/send.html"

    # Assert that the session contains the user info
    assert "session" in response.cookies


def test_auth_callback_failure(client, mocker, test_settings):  # noqa: ARG001
    """
    Test the /auth callback with a failed token exchange.
    """
    # We need to access the oauth object that is configured with the test settings
    from src.mbl2pc.core.config import oauth

    # Mock the OAuth client's fetch_token method to raise an exception
    mocker.patch.object(
        oauth.google,
        "authorize_access_token",
        new_callable=AsyncMock,
        side_effect=Exception("Token exchange failed"),
    )

    # Make the request to the /auth endpoint
    response = client.get("/auth", follow_redirects=False)

    # Assert that the response is a 401 Unauthorized
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not log in."}
