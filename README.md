## Version

**Current version:** `8e6cba1` (auto-updated from latest git commit)

## Requirements Explained

| Package           | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| fastapi           | Web framework for building the backend API                               |
| uvicorn           | ASGI server to run FastAPI apps                                          |
| pydantic          | Data validation and settings management (used by FastAPI)                |
| starlette         | ASGI toolkit/framework (FastAPI is built on top of Starlette)            |
| python-multipart  | Handles file uploads (image upload support in FastAPI)                   |
| authlib           | OAuth client integration for Google login                                |
| httpx             | Async HTTP client (used by Authlib and for any HTTP requests)            |
| boto3             | AWS SDK for Python (DynamoDB and S3 integration)                         |
| botocore          | Core library for AWS SDK (dependency of boto3)                           |
| itsdangerous      | Secure session management (used by Starlette's SessionMiddleware)        |
| pytest            | Testing framework for Python (backend API tests)                         |

# mbl2pc

Send messages from my phone to my computer

## Setup

1.  Create a virtual environment

    ```bash
    python3.13 -m venv .venv
    source .venv/bin/activate
    ```

2.  Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

3.  Set up your environment. Create a `.env` file with the following:

    ```ini
    GOOGLE_CLIENT_ID=xxx
    GOOGLE_CLIENT_SECRET=xxx
    SESSION_SECRET_KEY=xxx
    ```

4.  Run the app

    ```bash
    uvicorn src.mbl2pc.main:app --reload
    ```

5.  Open your browser to <http://localhost:8000/send.html>

## Deployment (Render.com)

1.  **Push your code to GitHub.**
2.  **Create a new Web Service on Render.com:**
    -   Environment: Python 3.12
    -   Build Command: `pip install -r requirements.txt`
    -   Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
    -   Set environment variables as above (use your Render.com URL for `OAUTH_REDIRECT_URI`)
    -   Expose port 10000 (Render uses the `PORT` env var)
3.  **Set up AWS IAM permissions:**
    -   The IAM user must have `dynamodb:Scan`, `dynamodb:PutItem`, and `dynamodb:GetItem` permissions on your table.
    -   The IAM user must have `s3:PutObject`, `s3:GetObject` permissions on your S3 bucket.
4.  **Set up Google OAuth:**
    -   In Google Cloud Console, set the authorized redirect URI to your Render.com URL (e.g. `https://your-app.onrender.com/auth`)

## Usage

-   Visit `/send.html` to access the chat UI.
-   Log in with Google.
-   Send text or image messages from your phone or PC.
-   Messages are stored per user and persist across devices.
-   The app version (git commit hash) is shown in the UI footer and at `/version`.

## Testing

-   Backend: Run `pytest` to test API endpoints.
-   Frontend: Playwright tests are included for public and error routes.

## File Structure

-   `main.py` — FastAPI backend, OAuth, DynamoDB integration
-   `static/send.html` — Chat UI (HTML/JS/CSS)
-   `requirements.txt` — Python dependencies
-   `render.yaml` — Render.com deployment config

## License

MIT