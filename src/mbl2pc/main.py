"""
Main FastAPI application startup, middleware configuration, and router inclusion.
Enhanced with modern dependency injection patterns.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from mbl2pc.api import auth, chat
from mbl2pc.core.config import Settings, get_oauth_client, get_settings
from mbl2pc.core.config import settings as legacy_settings
from mbl2pc.core.storage import MessageRepositoryProtocol, get_message_repository
from mbl2pc.schemas import Message


# --- App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifespan management."""
    # Any startup logic here
    yield
    # Any cleanup logic here


app = FastAPI(title="mbl2pc", version="0.1.0", lifespan=lifespan)


def configure_middleware() -> None:
    """Configure application middleware."""
    # CORS for frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Session middleware for OAuth
    app.add_middleware(SessionMiddleware, secret_key=legacy_settings.SESSION_SECRET_KEY)


# Configure middleware at startup
configure_middleware()

# --- Routers ---
app.include_router(auth.router, tags=["Authentication"])
app.include_router(chat.router, tags=["Chat"])

# --- Static Files ---
# Ensure static directory exists
if not os.path.exists("static"):
    os.mkdir("static")
# Mount static files
# Use an absolute path to the static directory to avoid issues with CWD
static_dir = Path(__file__).parent.parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# --- Root and Version Endpoints ---
@app.get("/")
def read_root(request: Request):
    """Root endpoint with user session check."""
    user = request.session.get("user")
    if user:
        return HTMLResponse('<h1>Hello</h1> <a href="/logout">logout</a>')
    return HTMLResponse('<a href="/login">login</a>')


@app.get("/version")
def version(settings: Settings = Depends(get_settings)):
    """Application version endpoint."""
    return {"version": settings.app_version}


# --- Protected UI Route ---
@app.get("/send.html")
def serve_send_html(request: Request):
    """
    Serves the main chat UI.
    If the user is not logged in, they are redirected to the login page.
    """
    if not request.session.get("user"):
        return RedirectResponse("/login")
    return FileResponse("static/send.html")


@app.get("/login")
async def login(request: Request, oauth_client=Depends(get_oauth_client)):
    """OAuth login endpoint."""
    redirect_uri = request.url_for("auth_callback")
    return await oauth_client.google.authorize_redirect(request, redirect_uri)


@app.get("/auth")
async def auth_callback(request: Request, oauth_client=Depends(get_oauth_client)):
    """OAuth callback endpoint."""
    token = await oauth_client.google.authorize_access_token(request)
    user = token["userinfo"]
    request.session["user"] = user
    return RedirectResponse(url="/")


@app.get("/logout")
def logout(request: Request):
    """Logout endpoint."""
    request.session.pop("user", None)
    return RedirectResponse(url="/")


@app.get("/messages", response_model=list[Message])
def get_messages_legacy(
    request: Request,
    message_repo: MessageRepositoryProtocol = Depends(get_message_repository),
):
    """Legacy messages endpoint - kept for backward compatibility."""
    user = request.session.get("user")
    if not user:
        return []

    # Note: This is async but we're calling it sync for backward compatibility
    # In a real app, this should be refactored to async
    import asyncio

    try:
        messages = asyncio.run(message_repo.get_messages(user["email"]))
        return messages
    except Exception:
        return []


@app.post("/messages")
async def post_message_legacy(
    message: Message,
    request: Request,
    message_repo: MessageRepositoryProtocol = Depends(get_message_repository),
):
    """Legacy message posting endpoint - kept for backward compatibility."""
    user = request.session.get("user")
    if not user:
        return {"status": "error", "message": "not logged in"}

    message.user_id = user["email"]
    try:
        await message_repo.add_message(message)
        return {"status": "ok"}
    except Exception:
        return {"status": "error", "message": "failed to save message"}
