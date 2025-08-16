
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Allow all CORS for testing (so your phone can access it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
