"""
Core application settings and environment variable management.
"""

import subprocess
from functools import lru_cache

from authlib.integrations.starlette_client import OAuth
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    SESSION_SECRET_KEY: str = "change-this-key"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_SESSION_TOKEN: str | None = None
    MBL2PC_DDB_TABLE: str = "mbl2pc-messages"
    S3_BUCKET: str = "mbl2pc-images"
    DYNAMODB_ENDPOINT_URL: str | None = None
    S3_ENDPOINT_URL: str | None = None
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/auth"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def get_git_version():
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return "unknown"


APP_VERSION = get_git_version()
