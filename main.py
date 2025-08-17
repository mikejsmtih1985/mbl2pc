
# --- Google OAuth setup ---
import os
from fastapi import HTTPException, Depends, Response
from starlette.requests import Request as StarletteRequest
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
OAUTH_REDIRECT_URI = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:8000/auth")

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
    }
)

from fastapi import Cookie

def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import shutil



import boto3
import uuid
from botocore.exceptions import ClientError


from fastapi.middleware.sessions import SessionMiddleware
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SESSION_SECRET_KEY", "change-this-key"))

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
def serve_send_html(request: Request):
    # If not logged in, redirect to login
    if not request.session.get('user'):
        return RedirectResponse('/login')
    return FileResponse("static/send.html")

# Google OAuth login
@app.get('/login')
async def login(request: Request):
    redirect_uri = OAUTH_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Google OAuth callback
@app.route('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse('/login')
    user = await oauth.google.parse_id_token(request, token)
    request.session['user'] = {
        'sub': user['sub'],
        'email': user.get('email'),
        'name': user.get('name'),
        'picture': user.get('picture')
    }
    return RedirectResponse('/send.html')

# Logout
@app.get('/logout')
def logout(request: Request):
    request.session.clear()
    return RedirectResponse('/login')


class Message(BaseModel):
    sender: str
    text: str = ""
    image_url: str = ""
    timestamp: str
    user_id: str


# DynamoDB setup
DDB_TABLE = os.environ.get("MBL2PC_DDB_TABLE", "mbl2pc-messages")
DDB_REGION = os.environ.get("AWS_REGION", "us-east-1")
dynamodb = boto3.resource("dynamodb", region_name=DDB_REGION)
table = dynamodb.Table(DDB_TABLE)

# Ensure static/images directory exists
if not os.path.exists("static/images"):
    os.makedirs("static/images")

@app.get("/")
def read_root():
    return {"message": "Hello from mbl2pc!"}



# Text message endpoint (DynamoDB)

@app.post("/send")
async def send_message(request: Request, msg: str = Form(""), sender: str = Form("unknown")):
    user = get_current_user(request)
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
        text=msg,
        image_url="",
        timestamp=datetime.now().isoformat(timespec="seconds"),
        user_id=user['sub']
    )
    item = message.dict()
    item["id"] = str(uuid.uuid4())
    try:
        table.put_item(Item=item)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB error: {e}")
    return {"status": "Message received"}




# Image upload endpoint with optional text (DynamoDB)

@app.post("/send-image")
async def send_image(
    request: Request,
    file: UploadFile = File(...),
    sender: str = Form("unknown"),
    text: str = Form("")
):
    user = get_current_user(request)
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
        timestamp=datetime.now().isoformat(timespec="seconds"),
        user_id=user['sub']
    )
    item = message.dict()
    item["id"] = str(uuid.uuid4())
    try:
        table.put_item(Item=item)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB error: {e}")
    return {"status": "Image received", "image_url": image_url}



# Retrieve messages for the current user from DynamoDB (sorted by timestamp descending, limit 100)
@app.get("/messages")
def get_messages(request: Request):
    user = get_current_user(request)
    try:
        resp = table.scan()
        items = resp.get("Items", [])
        # Filter by user_id
        items = [item for item in items if item.get("user_id") == user['sub']]
        # Sort by timestamp descending, then return most recent 100
        items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        messages = [
            {k: v for k, v in item.items() if k in ["sender", "text", "image_url", "timestamp"]}
            for item in items[:100]
        ]
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB error: {e}")
    return {"messages": messages[::-1]}  # Return in ascending order
