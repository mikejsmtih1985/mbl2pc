# Shared secret for simple authentication
import os
API_KEY = os.environ.get("MBL2PC_API_KEY", "changeme123")

from fastapi import HTTPException

def check_key(key: str):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key.")


from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import shutil


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
    text: str = ""
    image_url: str = ""
    timestamp: str

messages = []  # In-memory message store for now

# Ensure static/images directory exists
if not os.path.exists("static/images"):
    os.makedirs("static/images")

@app.get("/")
def read_root():
    return {"message": "Hello from mbl2pc!"}


# Text message endpoint (unchanged)
@app.post("/send")
async def send_message(request: Request, msg: str = Form(""), sender: str = Form("unknown"), key: str = Form("") ):
    check_key(key)
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
        image_url="",
        timestamp=datetime.now().isoformat(timespec="seconds")
    )
    messages.append(message)
    return {"status": "Message received"}



# Image upload endpoint with optional text
@app.post("/send-image")
async def send_image(
    request: Request,
    file: UploadFile = File(...),
    sender: str = Form("unknown"),
    key: str = Form(""),
    text: str = Form("")
):
    check_key(key)
    # Validate file
    if not file or not hasattr(file, "filename"):
        raise HTTPException(status_code=400, detail="No file uploaded.")
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if not ext:
        raise HTTPException(status_code=400, detail="File must have an extension (e.g. .jpg, .png)")
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    fname = f"img_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}"
    fpath = os.path.join("static/images", fname)
    try:
        with open(fpath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_url = f"/static/images/{fname}"
    except Exception as e:
        # Clean up partial file if it exists
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")
    # Use sender from param or guess
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
        text=text,
        image_url=image_url,
        timestamp=datetime.now().isoformat(timespec="seconds")
    )
    messages.append(message)
    return {"status": "Image received", "image_url": image_url}

@app.get("/messages")
def get_messages(key: str = ""):
    check_key(key)
    return {"messages": [m.dict() for m in messages]}
