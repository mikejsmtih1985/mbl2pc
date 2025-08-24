"""
API endpoints for authentication (Login, Logout, OAuth callback).
Enhanced with modern dependency injection patterns.
"""

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse, RedirectResponse

from mbl2pc.core.config import Settings, get_oauth_client, get_settings

router = APIRouter()


@router.get("/login")
async def login(
    request: Request,
    oauth_client: OAuth = Depends(get_oauth_client),
    settings: Settings = Depends(get_settings),
):
    """
    Redirects the user to Google's OAuth 2.0 consent screen.
    """
    return await oauth_client.google.authorize_redirect(
        request, settings.OAUTH_REDIRECT_URI
    )


@router.get("/auth")
async def auth(
    request: Request,
    oauth_client: OAuth = Depends(get_oauth_client),
):
    """
    Handles the callback from Google after the user has granted consent.
    """
    try:
        token = await oauth_client.google.authorize_access_token(request)
        user = token["userinfo"]
        request.session["user"] = user
        return RedirectResponse(url="/send.html")
    except Exception as e:
        # Log the error for debugging
        print(f"Login failed: {e}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Could not log in."},
        )


@router.get("/logout")
async def logout(request: Request):
    """
    Clears the user's session and redirects to the home page.
    """
    request.session.pop("user", None)
    return RedirectResponse(url="/")
