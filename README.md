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
| boto3             | AWS SDK for Python (DynamoDB integration)                                |
| botocore          | Core library for AWS SDK (dependency of boto3)                           |
| itsdangerous      | Secure session management (used by Starlette's SessionMiddleware)        |
| pytest            | Testing framework for Python (backend API tests)                         |

# mbl2pc

mbl2pc is a cloud-based chat app that lets you send text and image messages from your phone to your PC (or vice versa) using a FastAPI backend, Google OAuth login, and AWS DynamoDB for persistent, per-user chat history. The app is designed for free hosting on Render.com.

## Features
- Google OAuth login (secure, per-user chat)
- Send and receive text messages
- Upload and send images with optional captions
- Persistent chat history stored in DynamoDB
- Responsive web UI (works on mobile and desktop)

## Prerequisites
- Python 3.8+
- AWS account with DynamoDB table (default: `mbl2pc-messages`)
- Google Cloud project with OAuth 2.0 credentials
- (For deployment) Render.com account

## Local Development
1. **Clone the repo:**
	```bash
	git clone https://github.com/mikejsmtih1985/mbl2pc.git
	cd mbl2pc
	```
2. **Install dependencies:**
	```bash
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
	```
3. **Set environment variables:**
	- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: from Google Cloud Console
	- `OAUTH_REDIRECT_URI`: e.g. `http://localhost:8000/auth` (for local dev)
	- `SESSION_SECRET_KEY`: any random string
	- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: for DynamoDB access
	- `AWS_REGION`: e.g. `us-east-2`
	- `MBL2PC_DDB_TABLE`: (optional) DynamoDB table name
4. **Run the app:**
	```bash
	uvicorn main:app --reload
	```
5. **Open in browser:**
	- Go to `http://localhost:8000/send.html`

## Deployment (Render.com)
1. **Push your code to GitHub.**
2. **Create a new Web Service on Render.com:**
	- Environment: Python
	- Build Command: `pip install -r requirements.txt`
	- Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
	- Set environment variables as above (use your Render.com URL for `OAUTH_REDIRECT_URI`)
	- Expose port 10000 (Render uses the `PORT` env var)
3. **Set up AWS IAM permissions:**
	- The IAM user must have `dynamodb:Scan`, `dynamodb:PutItem`, and `dynamodb:GetItem` permissions on your table.
4. **Set up Google OAuth:**
	- In Google Cloud Console, set the authorized redirect URI to your Render.com URL (e.g. `https://your-app.onrender.com/auth`)

## Usage
- Visit `/send.html` to access the chat UI.
- Log in with Google.
- Send text or image messages from your phone or PC.
- Messages are stored per user and persist across devices.

## Testing
- Backend: Run `pytest` to test API endpoints.
- Frontend: Playwright tests are included for public and error routes.

## File Structure
- `main.py` — FastAPI backend, OAuth, DynamoDB integration
- `static/send.html` — Chat UI (HTML/JS/CSS)
- `requirements.txt` — Python dependencies
- `render.yaml` — Render.com deployment config

## License
MIT