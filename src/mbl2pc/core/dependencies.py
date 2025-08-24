"""
Reusable dependencies for FastAPI endpoints.
"""

import sys

from fastapi import HTTPException, Request

from mbl2pc.schemas import User


def get_current_user(request: Request) -> User:
    """
    Retrieves the current authenticated user from the session.
    Raises HTTPException if the user is not found or the session is invalid.
    """
    try:
        user_data = request.session.get("user")
    except Exception as e:
        print(f"[ERROR] Exception accessing session: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=500, detail="Internal server error accessing session."
        )

    if not user_data:
        raise HTTPException(
            status_code=401, detail="Not authenticated: session missing or expired."
        )

    if not isinstance(user_data, dict) or "sub" not in user_data:
        raise HTTPException(
            status_code=401, detail="Not authenticated: session user invalid."
        )

    return User(**user_data)
