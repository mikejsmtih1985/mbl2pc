# Getting Started with MBL2PC

This guide will get you up and running with MBL2PC for local development in under 10 minutes.

## Prerequisites

- **Python 3.13+** (required)
- **Git** for version control
- **AWS Account** for cloud services
- **Google Account** for OAuth setup

## Quick Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/mbl2pc.git
cd mbl2pc

# One-command setup (installs dependencies and pre-commit hooks)
make install
```

### 2. Environment Configuration

```bash
# Copy the environment template
cp .env.sample .env

# Edit with your credentials (see sections below)
nano .env  # or use your preferred editor
```

### 3. Start Development Server

```bash
# Run development server with auto-reload
make run

# Or use the combined setup and run command
make dev
```

Your application will be available at:
- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Environment Configuration

### Required Environment Variables

Edit your `.env` file with these values:

```bash
# Google OAuth 2.0 Configuration
GOOGLE_CLIENT_ID="your-google-oauth-client-id"
GOOGLE_CLIENT_SECRET="your-google-oauth-client-secret"
OAUTH_REDIRECT_URI="http://localhost:8000/auth"

# Session Security (generate with: openssl rand -hex 32)
SESSION_SECRET_KEY="your-secure-32-character-minimum-secret-key"

# AWS Configuration
AWS_REGION="us-east-1"
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
MBL2PC_DDB_TABLE="mbl2pc-messages-dev"
S3_BUCKET="mbl2pc-images-dev"

# Optional: Local development with LocalStack
DYNAMODB_ENDPOINT_URL=""  # Leave empty for AWS
S3_ENDPOINT_URL=""        # Leave empty for AWS
```

## Setting up Google OAuth 2.0

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** or select existing
3. **Enable APIs**:
   - Go to "APIs & Services" > "Library"
   - Search and enable "Google+ API" or "People API"
4. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Application type: Web application
   - Name: "MBL2PC Development"
   - Authorized redirect URI: `http://localhost:8000/auth`
5. **Copy credentials** to your `.env` file

## Setting up AWS Resources

### Option A: Use Existing AWS Account

#### Create DynamoDB Table

```bash
aws dynamodb create-table \
    --table-name mbl2pc-messages-dev \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST
```

#### Create S3 Bucket

```bash
# Create bucket (use a unique name)
aws s3 mb s3://mbl2pc-images-dev-yourname

# Update your .env file with the bucket name
# S3_BUCKET="mbl2pc-images-dev-yourname"
```

### Option B: Use LocalStack (Local AWS)

For development without AWS costs:

```bash
# Run with LocalStack for local AWS services
make docker-dev

# Update .env for LocalStack
DYNAMODB_ENDPOINT_URL="http://localhost:4566"
S3_ENDPOINT_URL="http://localhost:4566"
```

## Development Workflow

### Essential Commands

```bash
# Development
make help          # Show all available commands
make dev           # Setup and run development environment
make run           # Run development server only

# Testing
make test          # Run all tests with coverage
make test-unit     # Run only unit tests
make test-integration  # Run only integration tests

# Code Quality
make lint          # Check code style with Ruff
make format        # Format code with Ruff
make type-check    # Run MyPy type checking
make ci            # Run complete CI pipeline

# Docker
make docker-build  # Build Docker image
make docker-run    # Run with Docker Compose
```

### Development Tips

1. **Auto-reload**: The development server automatically reloads on code changes
2. **API Documentation**: Visit `/docs` for interactive API documentation
3. **Health Checks**: Use `/health` to verify everything is working
4. **Pre-commit Hooks**: Automatically run quality checks on commit
5. **Type Safety**: The project uses strict MyPy type checking

## Testing Your Setup

### 1. Run the Test Suite

```bash
make test
```

You should see all tests passing:
```
✅ Tests: 28/28 passing (100%)
✅ Coverage: 67%+ (above threshold)
```

### 2. Test the Web Interface

1. Open http://localhost:8000 in your browser
2. You should see the messaging interface
3. Click "Login with Google" to test OAuth
4. Try sending a test message

### 3. Test the API

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs
```

## Next Steps

- **Read the Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- **Deployment**: Ready to deploy? See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing**: Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Troubleshooting**: Having issues? See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Common Issues

### Python Version

```bash
# Check Python version
python --version  # Should be 3.13+

# If using pyenv
pyenv install 3.13.7
pyenv local 3.13.7
```

### Import Errors

```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

### OAuth Redirect Issues

- Ensure `OAUTH_REDIRECT_URI` in `.env` matches Google Console exactly
- Check that redirect URI is `http://localhost:8000/auth` (no trailing slash)

### AWS Connection Issues

- Verify AWS credentials with `aws sts get-caller-identity`
- Check region matches between `.env` and AWS resources
- Ensure IAM permissions for DynamoDB and S3

---

**Need help?** Open an issue in the repository or check the [troubleshooting guide](TROUBLESHOOTING.md).
