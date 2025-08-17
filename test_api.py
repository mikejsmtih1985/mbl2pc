import os
import io
import pytest
from fastapi.testclient import TestClient
from main import app, API_KEY

test_client = TestClient(app)

def test_send_text_message():
    resp = test_client.post(
        "/send",
        data={"msg": "Hello world!", "sender": "pytest", "key": API_KEY}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "Message received"

def test_send_image_valid():
    img_bytes = io.BytesIO(b"fakeimagedata")
    img_bytes.name = "test.png"
    resp = test_client.post(
        "/send-image",
        data={"sender": "pytest", "key": API_KEY},
        files={"file": ("test.png", img_bytes, "image/png")}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "Image received"
    assert data["image_url"].startswith("/static/images/")

def test_send_image_no_file():
    resp = test_client.post(
        "/send-image",
        data={"sender": "pytest", "key": API_KEY}
    )
    assert resp.status_code == 422  # FastAPI returns 422 for missing required file

def test_send_image_unsupported_type():
    fake = io.BytesIO(b"notanimage")
    fake.name = "test.txt"
    resp = test_client.post(
        "/send-image",
        data={"sender": "pytest", "key": API_KEY},
        files={"file": ("test.txt", fake, "text/plain")}
    )
    assert resp.status_code == 400
    assert "Unsupported file type" in resp.text

def test_send_image_no_extension():
    fake = io.BytesIO(b"notanimage")
    fake.name = "test"
    resp = test_client.post(
        "/send-image",
        data={"sender": "pytest", "key": API_KEY},
        files={"file": ("test", fake, "image/png")}
    )
    assert resp.status_code == 400
    assert "File must have an extension" in resp.text

def test_auth_required():
    resp = test_client.post(
        "/send",
        data={"msg": "fail", "sender": "pytest", "key": "wrongkey"}
    )
    assert resp.status_code == 401
    assert "Invalid API key" in resp.text

def test_get_messages():
    resp = test_client.get(f"/messages?key={API_KEY}")
    assert resp.status_code == 200
    assert "messages" in resp.json()
