"""
API endpoints for authentication (Login, Logout, OAuth callback).
"""

from fastapi import APIRouter, Request
from starlette.responses import JSONResponse, RedirectResponse

from src.mbl2pc.core.config import oauth, settings

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    """
    Redirects the user to Google's OAuth 2.0 consent screen.
    """
    return await oauth.google.authorize_redirect(request, settings.OAUTH_REDIRECT_URI)


@router.get("/auth")
async def auth(request: Request):
    """
    Handles the callback from Google after the user has granted consent.
    """
    try:
        token = await oauth.google.authorize_access_token(request)
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
