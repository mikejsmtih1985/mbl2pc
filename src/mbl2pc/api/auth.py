"""
API endpoints for authentication (Login, Logout, OAuth callback).
"""
import sys
from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import RedirectResponse
from mbl2pc.core.config import oauth, OAUTH_REDIRECT_URI

router = APIRouter()

@router.get('/login')
async def login(request: Request):
    """Redirects the user to Google for authentication."""
    if not oauth or not hasattr(oauth, 'google'):
        print("[ERROR] OAuth is not configured properly.", file=sys.stderr)
        raise HTTPException(status_code=500, detail="OAuth is not configured properly.")

    return await oauth.google.authorize_redirect(request, OAUTH_REDIRECT_URI)

@router.get('/auth')
async def auth(request: Request):
    """
    Handles the OAuth callback from Google, authenticates the user,
    and stores their information in the session.
    """
    if not oauth or not hasattr(oauth, 'google'):
        print("[ERROR] OAuth is not configured properly.", file=sys.stderr)
        raise HTTPException(status_code=500, detail="OAuth is not configured properly.")

    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
    except Exception as e:
        print(f"[ERROR] OAuth authentication failed: {e}", file=sys.stderr)
        return RedirectResponse('/login')

    if not user_info:
        raise HTTPException(status_code=401, detail="Failed to authenticate user.")

    request.session['user'] = {
        'sub': user_info['sub'],
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture')
    }
    return RedirectResponse('/send.html')

@router.get('/logout')
def logout(request: Request):
    """Clears the user session and redirects to the login page."""
    request.session.clear()
    return RedirectResponse('/login')
