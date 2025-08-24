"""
Main FastAPI application startup, middleware configuration, and router inclusion.
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from mbl2pc.api import auth, chat
from mbl2pc.core.config import APP_VERSION, SESSION_SECRET_KEY

# --- App Initialization ---
app = FastAPI(
    title="mbl2pc",
    version=APP_VERSION
)

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
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

# --- Routers ---
app.include_router(auth.router, tags=["Authentication"])
app.include_router(chat.router, tags=["Chat"])

# --- Static Files ---
# Ensure static directory exists
if not os.path.exists("static"):
    os.mkdir("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Root and Version Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Hello from mbl2pc!"}

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
    if not request.session.get('user'):
        return RedirectResponse('/login')
    return FileResponse("static/send.html")
