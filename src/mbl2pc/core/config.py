"""
Core application settings and environment variable management.
"""

import subprocess
from functools import lru_cache
from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with enhanced validation and modern Pydantic v2 features."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # OAuth Configuration
    GOOGLE_CLIENT_ID: Annotated[
        str, Field(default="test-client-id", description="Google OAuth client ID")
    ]
    GOOGLE_CLIENT_SECRET: Annotated[
        str,
        Field(default="test-client-secret", description="Google OAuth client secret"),
    ]
    SESSION_SECRET_KEY: Annotated[
        str,
        Field(
            default="change-this-key-with-32-characters",
            min_length=32,
            description="Session encryption key",
        ),
    ]

    # AWS Configuration
    AWS_REGION: Annotated[str, Field(default="us-east-1", description="AWS region")]
    AWS_ACCESS_KEY_ID: Annotated[
        str | None, Field(default=None, description="AWS access key ID")
    ]
    AWS_SECRET_ACCESS_KEY: Annotated[
        str | None, Field(default=None, description="AWS secret access key")
    ]
    AWS_SESSION_TOKEN: Annotated[
        str | None, Field(default=None, description="AWS session token")
    ]

    # DynamoDB Configuration
    MBL2PC_DDB_TABLE: Annotated[
        str, Field(default="mbl2pc-messages", description="DynamoDB table name")
    ]
    DYNAMODB_ENDPOINT_URL: Annotated[
        str | None, Field(default=None, description="Custom DynamoDB endpoint")
    ]

    # S3 Configuration
    S3_BUCKET: Annotated[
        str, Field(default="mbl2pc-images", description="S3 bucket name")
    ]
    S3_ENDPOINT_URL: Annotated[
        str | None, Field(default=None, description="Custom S3 endpoint")
    ]

    # OAuth Configuration
    OAUTH_REDIRECT_URI: Annotated[
        str,
        Field(default="http://localhost:8000/auth", description="OAuth redirect URI"),
    ]

    @property
    def app_version(self) -> str:
        """Get the application version from git."""
        return get_git_version()

    @field_validator("SESSION_SECRET_KEY")
    @classmethod
    def validate_session_secret_key(cls, v: str) -> str:
        """Ensure session secret key is sufficiently secure."""
        if len(v) < 32:
            raise ValueError("SESSION_SECRET_KEY must be at least 32 characters long")
        if v == "change-this-key-with-32-characters":
            import warnings

            warnings.warn(
                "Using default SESSION_SECRET_KEY in production is insecure",
                UserWarning,
                stacklevel=2,
            )
        return v

    @field_validator("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET")
    @classmethod
    def validate_oauth_credentials(cls, v: str) -> str:
        """Validate OAuth credentials are not using defaults in production."""
        if v.startswith("test-"):
            import warnings

            warnings.warn(
                "Using test OAuth credentials - ensure this is intentional",
                UserWarning,
                stacklevel=2,
            )
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached dependency for getting application settings."""
    return Settings()  # type: ignore[call-arg]


def get_oauth_client(settings: Settings = Depends(get_settings)) -> OAuth:
    """Dependency for getting configured OAuth client."""
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    return oauth


def get_git_version() -> str:
    """Get the current git commit hash for versioning."""
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return "unknown"


# Legacy global instances - deprecated but maintained for backward compatibility
settings = get_settings()
oauth = get_oauth_client(settings)
APP_VERSION = get_git_version()
