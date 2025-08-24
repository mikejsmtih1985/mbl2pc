"""
Integration tests for the authentication API endpoints.
"""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.mbl2pc.core import config as app_config
from src.mbl2pc.main import app


@pytest.mark.asyncio
async def test_login_redirects():
    """
    Test that the /login route redirects to the Google OAuth URL.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/login", follow_redirects=False)
        assert response.status_code == 307  # Temporary Redirect
        assert "accounts.google.com" in response.headers["location"]


@pytest.mark.asyncio
async def test_auth_callback_success(mocker):
    """
    Test the /auth callback with a successful token exchange.
    """
    # Mock the OAuth client's fetch_token method to return a dummy token
    mock_token = {
        "access_token": "dummy_token",
        "userinfo": {"name": "Test User", "email": "test@example.com"},
    }

    # Patch the oauth object in the config module
    mock_authorize = mocker.patch.object(
        app_config.oauth.google,
        "authorize_access_token",
        new_callable=AsyncMock,
        return_value=mock_token,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Make the request to the /auth endpoint
        response = await client.get("/auth", follow_redirects=False)

        # Assert that the user is redirected to the send page
        assert response.status_code == 307
        assert response.headers["location"] == "/send.html"

        # Assert that the session contains the user info
        assert "session" in response.cookies

    # Ensure the mock was called
    mock_authorize.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_callback_failure(mocker):
    """
    Test the /auth callback with a failed token exchange.
    """
    # Mock the OAuth client's fetch_token method to raise an exception
    mock_authorize = mocker.patch.object(
        app_config.oauth.google,
        "authorize_access_token",
        new_callable=AsyncMock,
        side_effect=Exception("Token exchange failed"),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Make the request to the /auth endpoint
        response = await client.get("/auth", follow_redirects=False)

        # Assert that the response is a 401 Unauthorized
        assert response.status_code == 401
        assert response.json() == {"detail": "Could not log in."}

    # Ensure the mock was called
    mock_authorize.assert_awaited_once()
