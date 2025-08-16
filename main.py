

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime


import os
app = FastAPI()

# Allow all CORS for testing (so your phone can access it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (send.html) from /static
if not os.path.exists("static"):
    os.mkdir("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route for /send.html to serve the chat UI
@app.get("/send.html")
def serve_send_html():
    return FileResponse("static/send.html")

class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

messages = []  # In-memory message store for now

@app.get("/")
def read_root():
    return {"message": "Hello from mbl2pc!"}

@app.post("/send")
async def send_message(request: Request, msg: str, sender: str = "unknown"):
    # Use sender from query param, or try to guess from user-agent
    if sender == "unknown":
        ua = request.headers.get("user-agent", "")
        if "iPhone" in ua:
            sender = "iPhone"
        elif "Android" in ua:
            sender = "Android"
        elif "Windows" in ua:
            sender = "PC"
        else:
            sender = "unknown"
    message = Message(
        sender=sender,
        text=msg,
        timestamp=datetime.now().isoformat(timespec="seconds")
    )
    messages.append(message)
    return {"status": "Message received"}

@app.get("/messages")
def get_messages():
    return {"messages": [m.dict() for m in messages]}
