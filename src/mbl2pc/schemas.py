"""
Pydantic schemas for data validation and serialization.
"""

from datetime import datetime
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Message(BaseModel):
    """Message model with enhanced validation and modern Pydantic v2 features."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    id: Annotated[
        str,
        Field(default_factory=lambda: str(uuid4()), description="Unique message ID"),
    ]
    sender: Annotated[
        str, Field(min_length=1, max_length=50, description="Message sender identifier")
    ]
    text: Annotated[
        str, Field(default="", max_length=2000, description="Message text content")
    ]
    image_url: Annotated[str, Field(default="", description="Optional image URL")]
    timestamp: Annotated[
        datetime, Field(default_factory=datetime.now, description="Message timestamp")
    ]
    user_id: Annotated[
        str, Field(default="", min_length=1, description="User identifier")
    ]

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        """Validate image URL format if provided."""
        if v and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Image URL must be a valid HTTP/HTTPS URL")
        return v


class User(BaseModel):
    """User model with OAuth userinfo validation."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    sub: Annotated[str, Field(min_length=1, description="OAuth subject identifier")]
    email: Annotated[str | None, Field(default=None, description="User email address")]
    name: Annotated[
        str | None, Field(default=None, max_length=100, description="User display name")
    ]
    picture: Annotated[
        HttpUrl | None, Field(default=None, description="User profile picture URL")
    ]
