"""
API endpoints for sending and retrieving messages and images.
"""
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, Depends
from botocore.exceptions import ClientError, NoCredentialsError
from mbl2pc.schemas import Message, User
from mbl2pc.core.dependencies import get_current_user
from mbl2pc.core.storage import get_db_table, get_s3_client
from mbl2pc.core.config import S3_BUCKET

router = APIRouter()

def _guess_sender_from_ua(request: Request) -> str:
    """Determines the sender type based on the User-Agent header."""
    ua = request.headers.get("user-agent", "")
    if "iPhone" in ua:
        return "iPhone"
    elif "Android" in ua:
        return "Android"
    elif "Windows" in ua:
        return "PC"
    return "unknown"

@router.post("/send")
async def send_message(
    request: Request,
    msg: str = Form(""),
    sender: str = Form("unknown"),
    user: User = Depends(get_current_user),
    table = Depends(get_db_table)
):
    """Receives and stores a text message in DynamoDB."""
    if sender == "unknown":
        sender = _guess_sender_from_ua(request)

    message = Message(
        sender=sender,
        text=msg,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        user_id=user.sub
    )

    item = message.model_dump()
    item["id"] = str(uuid.uuid4())

    try:
        table.put_item(Item=item)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB error: {e}")

    return {"status": "Message received"}

@router.post("/send-image")
async def send_image(
    request: Request,
    file: UploadFile = File(...),
    sender: str = Form("unknown"),
    text: str = Form(""),
    user: User = Depends(get_current_user),
    table = Depends(get_db_table),
    s3 = Depends(get_s3_client)
):
    """Receives an image, uploads it to S3, and stores message metadata in DynamoDB."""
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    fname = f"img_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}"

    # Upload to S3
    try:
        file.file.seek(0)
        s3.upload_fileobj(
            file.file,
            S3_BUCKET,
            fname,
            ExtraArgs={"ContentType": file.content_type}
        )
        image_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{fname}"
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found for S3 upload.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image to S3: {e}")

    if sender == "unknown":
        sender = _guess_sender_from_ua(request)

    message = Message(
        sender=sender,
        text=text,
        image_url=image_url,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        user_id=user.sub
    )

    item = message.model_dump()
    item["id"] = str(uuid.uuid4())

    try:
        table.put_item(Item=item)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB error: {e}")

    return {"status": "Image received", "image_url": image_url}

@router.get("/messages")
def get_messages(
    user: User = Depends(get_current_user),
    table = Depends(get_db_table)
):
    """Retrieves the last 100 messages for the current user from DynamoDB."""
    try:
        resp = table.scan()
        items = resp.get("Items", [])

        # Filter by user_id and sort by timestamp
        user_items = [item for item in items if item.get("user_id") == user.sub]
        user_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Format and limit to 100
        messages = [
            {k: v for k, v in item.items() if k in ["sender", "text", "image_url", "timestamp"]}
            for item in user_items[:100]
        ]
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB error: {e}")

    return {"messages": messages[::-1]}  # Return in chronological order
