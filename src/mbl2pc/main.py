"""
Main FastAPI application startup, middleware configuration, and router inclusion.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from mbl2pc.api import auth, chat
from mbl2pc.core import storage
from mbl2pc.core.config import APP_VERSION, settings

from . import schemas


# --- App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = storage.get_db()
    yield


app = FastAPI(title="mbl2pc", version=APP_VERSION, lifespan=lifespan)

# --- Middleware ---
# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)

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
    user = request.session.get("user")
    if user:
        return HTMLResponse('<h1>Hello</h1> <a href="/logout">logout</a>')
    return HTMLResponse('<a href="/login">login</a>')


@app.get("/version")
def version():
    return {"version": APP_VERSION}


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


# --- OAuth2 with Google ---
oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    client_kwargs={"scope": "openid email profile"},
)


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token["userinfo"]
    request.session["user"] = user
    return RedirectResponse(url="/")


@app.get("/logout")
def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")


@app.get("/messages", response_model=list[schemas.Message])
def get_messages(request: Request):
    user = request.session.get("user")
    if not user:
        return []
    return storage.get_messages(user["email"])


@app.post("/messages")
def post_message(message: schemas.Message, request: Request):
    user = request.session.get("user")
    if not user:
        return {"status": "error", "message": "not logged in"}
    message.user_id = user["email"]
    storage.add_message(message)
    return {"status": "ok"}
