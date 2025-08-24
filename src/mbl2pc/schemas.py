"""
Pydantic schemas for data validation and serialization.
"""

from pydantic import BaseModel


class Message(BaseModel):
    sender: str
    text: str = ""
    image_url: str = ""
    timestamp: str
    user_id: str


class User(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None
    picture: str | None = None
