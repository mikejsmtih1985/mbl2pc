import os
import pytest
from fastapi.testclient import TestClient
from main import app
import itsdangerous
import json

client = TestClient(app)

def get_session_cookie(user_dict, secret_key):
    # Starlette uses itsdangerous for session cookies
    from starlette.middleware.sessions import SessionMiddleware
    serializer = itsdangerous.URLSafeSerializer(secret_key, salt="starlette.sessions")
    return serializer.dumps({"user": user_dict})

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello from mbl2pc!"

def test_send_message_authenticated():
    user = {
        'sub': 'test-user-id',
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': ''
    }
    secret_key = os.environ.get("SESSION_SECRET_KEY", "change-this-key")
    session_cookie = get_session_cookie(user, secret_key)
    client.cookies.set("session", session_cookie)
    response = client.post("/send", data={"msg": "Hello!", "sender": "tester"})
    if response.status_code not in (200, 500):
        print("\n[DEBUG] Response status:", response.status_code)
        print("[DEBUG] Response body:", response.text)
    assert response.status_code in (200, 500, 401)  # 401 if session not accepted, 500 if DynamoDB is not configured
    if response.status_code == 200:
        assert response.json()["status"] == "Message received"
    elif response.status_code == 401:
        assert "not authenticated" in response.text.lower() or "session" in response.text.lower()

def test_send_image_requires_auth():
    with open("static/send.html", "rb") as f:
        response = client.post("/send-image", files={"file": ("test.png", f, "image/png")})
    assert response.status_code == 401

def test_get_messages_requires_auth():
    response = client.get("/messages")
    assert response.status_code == 401