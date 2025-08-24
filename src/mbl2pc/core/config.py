"""
Core application settings and environment variable management.
"""
import os
import sys
from authlib.integrations.starlette_client import OAuth

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Ignore if not available

# --- Google OAuth setup ---
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
OAUTH_REDIRECT_URI = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:8000/auth")
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "change-this-key")

missing_oauth_vars = []
if not GOOGLE_CLIENT_ID:
    missing_oauth_vars.append("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_SECRET:
    missing_oauth_vars.append("GOOGLE_CLIENT_SECRET")
if not OAUTH_REDIRECT_URI:
    missing_oauth_vars.append("OAUTH_REDIRECT_URI")

oauth: OAuth | None = None
if missing_oauth_vars:
    print(f"[ERROR] Missing OAuth environment variables: {', '.join(missing_oauth_vars)}", file=sys.stderr)
else:
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

# --- AWS/DB/Storage Settings ---
DDB_TABLE = os.environ.get("MBL2PC_DDB_TABLE", "mbl2pc-messages")
DDB_REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "mbl2pc-images")

# --- App Version ---
import subprocess
def get_git_version():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()
    except Exception:
        return "unknown"

APP_VERSION = get_git_version()
