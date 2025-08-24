# Deployment Guide for MBL2PC

This guide covers various deployment options for the MBL2PC messaging service.

## Prerequisites

Before deploying, ensure you have:

1. **Google OAuth 2.0 credentials** configured for your domain
2. **AWS account** with DynamoDB and S3 access
3. **Environment variables** properly configured

## Quick Deployment Options

### 1. Render.com (Recommended for beginners)

Render.com provides the easiest deployment with automatic builds from GitHub.

#### Setup Steps:

1. **Fork this repository** to your GitHub account

2. **Create Render account** at [render.com](https://render.com)

3. **Connect GitHub** and select your forked repository

4. **Configure Environment Variables** in Render dashboard:
   ```
   GOOGLE_CLIENT_ID=your-production-oauth-client-id
   GOOGLE_CLIENT_SECRET=your-production-oauth-client-secret
   OAUTH_REDIRECT_URI=https://your-app-name.onrender.com/auth
   SESSION_SECRET_KEY=secure-random-32-character-minimum-string
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   MBL2PC_DDB_TABLE=mbl2pc-messages-prod
   S3_BUCKET=mbl2pc-images-prod
   ```

5. **Deploy** - Render will automatically build and deploy on every git push

#### Render Configuration:

The `render.yaml` file is pre-configured with:
- Python 3.13 runtime
- Automatic dependency installation
- Health checks
- Proper port configuration

### 2. Docker Deployment

Perfect for VPS, cloud instances, or local production testing.

#### Build and Run:

```bash
# Build the Docker image
make docker-build

# Run with docker-compose (recommended)
make docker-run

# Or run directly
docker run -p 8000:8000 --env-file .env mbl2pc
```

#### Docker Compose Features:

- **Health checks** for reliability
- **Volume mounts** for development
- **LocalStack integration** for local AWS testing
- **Environment file** support

### 3. AWS Lambda (Serverless)

For cost-effective, auto-scaling deployment.

#### Setup:

1. **Install Mangum** for ASGI compatibility:
   ```bash
   pip install mangum
   ```

2. **Create Lambda handler** (add to `src/mbl2pc/main.py`):
   ```python
   from mangum import Mangum

   # At the end of main.py
   handler = Mangum(app)
   ```

3. **Deploy with AWS SAM**:
   ```yaml
   # template.yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Transform: AWS::Serverless-2016-10-31

   Resources:
     MBL2PCFunction:
       Type: AWS::Serverless::Function
       Properties:
         CodeUri: .
         Handler: src.mbl2pc.main.handler
         Runtime: python3.13
         Environment:
           Variables:
             GOOGLE_CLIENT_ID: !Ref GoogleClientId
             # Add other environment variables
   ```

### 4. Traditional VPS/Server

For maximum control and customization.

#### Production Setup:

```bash
# On your server (Ubuntu/Debian example)
sudo apt update && sudo apt install python3.13 python3.13-venv nginx

# Create application user
sudo useradd --system --shell /bin/bash --home /opt/mbl2pc mbl2pc

# Setup application
sudo -u mbl2pc git clone https://github.com/yourusername/mbl2pc.git /opt/mbl2pc
cd /opt/mbl2pc
sudo -u mbl2pc python3.13 -m venv venv
sudo -u mbl2pc ./venv/bin/pip install -e .

# Install and configure systemd service
sudo cp deploy/mbl2pc.service /etc/systemd/system/
sudo systemctl enable mbl2pc
sudo systemctl start mbl2pc

# Configure Nginx reverse proxy
sudo cp deploy/nginx.conf /etc/nginx/sites-available/mbl2pc
sudo ln -s /etc/nginx/sites-available/mbl2pc /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

#### Systemd Service (`deploy/mbl2pc.service`):

```ini
[Unit]
Description=MBL2PC FastAPI Application
After=network.target

[Service]
User=mbl2pc
Group=mbl2pc
WorkingDirectory=/opt/mbl2pc
Environment="PATH=/opt/mbl2pc/venv/bin"
EnvironmentFile=/opt/mbl2pc/.env
ExecStart=/opt/mbl2pc/venv/bin/gunicorn src.mbl2pc.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Environment Configuration

### Required Environment Variables

```bash
# OAuth Configuration
GOOGLE_CLIENT_ID="your-production-oauth-client-id"
GOOGLE_CLIENT_SECRET="your-production-oauth-client-secret"
OAUTH_REDIRECT_URI="https://yourdomain.com/auth"

# Security
SESSION_SECRET_KEY="secure-random-32-character-minimum-key"

# AWS Configuration
AWS_REGION="us-east-1"
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
MBL2PC_DDB_TABLE="mbl2pc-messages-prod"
S3_BUCKET="mbl2pc-images-prod"

# Optional: Logging and Monitoring
LOG_LEVEL="INFO"
SENTRY_DSN="your-sentry-dsn-for-error-tracking"
```

### Google OAuth Setup for Production

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create/Select Project**
3. **Enable APIs**: Google+ API or People API
4. **Create OAuth 2.0 Credentials**:
   - Application type: Web application
   - Authorized redirect URI: `https://yourdomain.com/auth`
5. **Copy credentials** to your environment variables

### AWS Resources Setup

#### DynamoDB Table:

```bash
aws dynamodb create-table \
    --table-name mbl2pc-messages-prod \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Environment,Value=Production Key=Application,Value=MBL2PC
```

#### S3 Bucket:

```bash
# Create bucket
aws s3 mb s3://mbl2pc-images-prod

# Configure public read access for images (if needed)
aws s3api put-bucket-policy \
    --bucket mbl2pc-images-prod \
    --policy file://bucket-policy.json

# Configure CORS for web uploads
aws s3api put-bucket-cors \
    --bucket mbl2pc-images-prod \
    --cors-configuration file://cors.json
```

## Health Monitoring

### Built-in Health Endpoints

- **`GET /health`** - Basic application health
- **`GET /version`** - Version and build information
- **`GET /docs`** - API documentation

### Monitoring Integration

The application is ready for monitoring integration:

```python
# Example: Add Sentry for error tracking
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
)
```

## Security Considerations

### Production Security Checklist

- [ ] **HTTPS enabled** (TLS/SSL certificates)
- [ ] **Environment variables** properly secured (not in source code)
- [ ] **OAuth redirect URI** matches production domain
- [ ] **SESSION_SECRET_KEY** is randomly generated and secure
- [ ] **AWS credentials** follow least-privilege principle
- [ ] **Database access** restricted to application
- [ ] **Regular security updates** for dependencies

### AWS IAM Policy (Minimal Permissions)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/mbl2pc-messages-prod"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::mbl2pc-images-prod/*"
        }
    ]
}
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Python 3.13+ is used
2. **OAuth Callback Errors**: Verify redirect URI matches exactly
3. **AWS Connection Issues**: Check credentials and regions
4. **Port Binding**: Ensure port 8000 (or configured port) is available

### Logs and Debugging

```bash
# Check application logs
journalctl -u mbl2pc -f

# Docker logs
docker-compose logs -f

# Check health endpoint
curl -f http://localhost:8000/health
```

### Performance Tuning

- **Gunicorn workers**: Adjust based on CPU cores (typically 2x cores + 1)
- **Database connections**: Configure connection pooling
- **Static files**: Use CDN for static assets in production
- **Caching**: Consider Redis for session storage and caching

---

For additional support, check the main README.md or open an issue in the repository.
