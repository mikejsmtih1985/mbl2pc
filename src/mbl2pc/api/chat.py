"""
API endpoints for sending and retrieving messages and images.
Enhanced with modern dependency injection and repository patterns.
"""

import os
from datetime import UTC, datetime
from typing import Annotated

from botocore.exceptions import NoCredentialsError
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from pydantic import ValidationError

from mbl2pc.core.config import Settings, get_settings
from mbl2pc.core.dependencies import get_current_user
from mbl2pc.core.storage import (
    MessageRepositoryProtocol,
    get_message_repository,
    get_s3_client,
)
from mbl2pc.schemas import Message, User

router = APIRouter()


def _guess_sender_from_ua(request: Request) -> str:
    """Determines the sender type based on the User-Agent header."""
    ua = request.headers.get("user-agent", "") or ""  # Handle None values
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
    msg: Annotated[str, Form(description="Message text content")] = "",
    sender: Annotated[str, Form(description="Sender identifier")] = "unknown",
    user: User = Depends(get_current_user),
    message_repo: MessageRepositoryProtocol = Depends(get_message_repository),
) -> dict[str, str]:
    """Receives and stores a text message using the repository pattern."""
    if sender == "unknown":
        sender = _guess_sender_from_ua(request)

    try:
        message = Message(  # type: ignore[call-arg]
            sender=sender,
            text=msg,
            timestamp=datetime.now(UTC),
            user_id=user.sub,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid message data: {e}") from e

    try:
        await message_repo.add_message(message)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {"status": "Message received"}


@router.post("/send-image")
async def send_image(
    request: Request,
    file: Annotated[UploadFile, File(description="Image file to upload")],
    sender: Annotated[str, Form(description="Sender identifier")] = "unknown",
    text: Annotated[str, Form(description="Optional text message")] = "",
    user: User = Depends(get_current_user),
    message_repo: MessageRepositoryProtocol = Depends(get_message_repository),
    s3_client=Depends(get_s3_client),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    """Receives an image, uploads it to S3, and stores message metadata."""
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    fname = f"img_{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}{ext}"

    # Upload to S3
    try:
        file.file.seek(0)
        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET,
            fname,
            ExtraArgs={"ContentType": file.content_type},
        )
        image_url = f"https://{settings.S3_BUCKET}.s3.amazonaws.com/{fname}"
    except NoCredentialsError:
        raise HTTPException(
            status_code=500, detail="AWS credentials not found for S3 upload."
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload image to S3: {e}"
        ) from e

    if sender == "unknown":
        sender = _guess_sender_from_ua(request)

    try:
        message = Message(  # type: ignore[call-arg]
            sender=sender,
            text=text,
            image_url=image_url,
            timestamp=datetime.now(UTC),
            user_id=user.sub,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid message data: {e}") from e

    try:
        await message_repo.add_message(message)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {"status": "Image received", "image_url": image_url}


@router.get("/messages")
async def get_messages(
    user: User = Depends(get_current_user),
    message_repo: MessageRepositoryProtocol = Depends(get_message_repository),
    limit: Annotated[
        int, Query(description="Maximum number of messages", ge=1, le=1000)
    ] = 100,
) -> dict[str, list[dict[str, str]]]:
    """Retrieves messages for the current user using the repository pattern."""
    try:
        messages = await message_repo.get_messages(user.sub, limit=limit)

        # Convert to dict format for API response
        message_dicts = [
            {
                "sender": msg.sender,
                "text": msg.text,
                "image_url": msg.image_url,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in messages
        ]
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {"messages": message_dicts}
