# Troubleshooting Guide

This guide covers common issues and their solutions when developing or deploying MBL2PC.

## Development Issues

### Python Version Problems

#### Wrong Python Version

**Problem**: Application fails to start or import errors occur.

**Solution**:
```bash
# Check current Python version
python --version

# Should be Python 3.13+
# If using pyenv:
pyenv install 3.13.7
pyenv local 3.13.7

# Verify installation
make install
```

#### Missing Python Dependencies

**Problem**: `ModuleNotFoundError` or import errors.

**Solution**:
```bash
# Reinstall in development mode
pip install -e ".[dev]" --force-reinstall

# Clear cache and reinstall
pip cache purge
make clean
make install
```

### Environment Configuration

#### Missing Environment Variables

**Problem**: Application starts but authentication or AWS operations fail.

**Symptoms**:
- OAuth login redirects to error page
- AWS operations throw credential errors
- Session management fails

**Solution**:
```bash
# Copy environment template
cp .env.sample .env

# Edit with your actual values
nano .env

# Verify required variables are set
grep -E "^[A-Z]" .env | grep -v "^#"
```

#### Invalid Google OAuth Configuration

**Problem**: OAuth login fails with "redirect_uri_mismatch" or similar errors.

**Solutions**:

1. **Check redirect URI exactly matches**:
   ```
   Google Console: http://localhost:8000/auth
   .env file:      http://localhost:8000/auth
   ```
   - No trailing slashes
   - Exact protocol (http vs https)
   - Exact port number

2. **Verify Google Console setup**:
   - APIs & Services → Credentials
   - OAuth 2.0 Client IDs
   - Authorized redirect URIs must include your exact URI

3. **Test with curl**:
   ```bash
   curl -i http://localhost:8000/login
   # Should redirect to Google OAuth
   ```

#### AWS Credential Issues

**Problem**: AWS operations fail with permission or credential errors.

**Solutions**:

1. **Verify AWS credentials**:
   ```bash
   aws sts get-caller-identity
   # Should return your AWS account info
   ```

2. **Check IAM permissions**:
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
               "Resource": "arn:aws:dynamodb:*:*:table/mbl2pc-messages*"
           },
           {
               "Effect": "Allow",
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject"
               ],
               "Resource": "arn:aws:s3:::mbl2pc-images*/*"
           }
       ]
   }
   ```

3. **Test AWS connectivity**:
   ```bash
   # Test DynamoDB
   aws dynamodb describe-table --table-name mbl2pc-messages-dev

   # Test S3
   aws s3 ls s3://your-bucket-name
   ```

### Testing Issues

#### Tests Failing Unexpectedly

**Problem**: Tests that previously passed are now failing.

**Solutions**:

1. **Clear test cache**:
   ```bash
   make clean
   pytest --cache-clear
   ```

2. **Check for environment pollution**:
   ```bash
   # Run tests in isolation
   python -m pytest tests/unit/test_specific.py::test_function -v
   ```

3. **Verify test dependencies**:
   ```bash
   # Check if mock objects are properly isolated
   pytest tests/ -v --tb=short
   ```

#### Coverage Issues

**Problem**: Test coverage below required threshold (65%).

**Solutions**:

1. **Identify uncovered code**:
   ```bash
   make test
   # Open htmlcov/index.html to see coverage report
   ```

2. **Add missing tests**:
   ```python
   # Focus on the red lines in coverage report
   def test_missing_functionality():
       # Test the uncovered code paths
   ```

### Code Quality Issues

#### MyPy Type Checking Errors

**Problem**: Type checking fails with MyPy errors.

**Common Solutions**:

1. **Missing type annotations**:
   ```python
   # ❌ Bad
   def process_data(data):
       return data.upper()

   # ✅ Good
   def process_data(data: str) -> str:
       return data.upper()
   ```

2. **Incompatible types**:
   ```python
   # ❌ Bad
   user_id: str = None

   # ✅ Good
   user_id: str | None = None
   ```

3. **External library issues**:
   ```python
   # Add type ignore for libraries without stubs
   import external_lib  # type: ignore[import-untyped]
   ```

#### Ruff Linting Errors

**Problem**: Code style violations reported by Ruff.

**Solutions**:

1. **Auto-fix most issues**:
   ```bash
   make format  # Auto-format code
   ruff check . --fix  # Fix auto-fixable issues
   ```

2. **Common manual fixes**:
   ```python
   # F401: Unused imports
   # Remove unused imports

   # E501: Line too long
   # Break long lines
   very_long_function_call(
       parameter1="value1",
       parameter2="value2"
   )

   # B008: Do not perform function calls in argument defaults
   # Use dependency injection instead
   def endpoint(service: Service = Depends(get_service)):
   ```

### Database Issues

#### DynamoDB Connection Problems

**Problem**: Cannot connect to DynamoDB or operations fail.

**Solutions**:

1. **Check table exists**:
   ```bash
   aws dynamodb describe-table --table-name mbl2pc-messages-dev
   ```

2. **Verify region configuration**:
   ```bash
   # .env file
   AWS_REGION=us-east-1

   # AWS CLI
   aws configure get region
   ```

3. **Test with LocalStack** (for development):
   ```bash
   # Start LocalStack
   make docker-dev

   # Update .env for LocalStack
   DYNAMODB_ENDPOINT_URL=http://localhost:4566
   ```

#### S3 Upload Issues

**Problem**: Image uploads fail or return errors.

**Solutions**:

1. **Check bucket exists and permissions**:
   ```bash
   aws s3 ls s3://your-bucket-name
   aws s3api get-bucket-location --bucket your-bucket-name
   ```

2. **Test upload manually**:
   ```bash
   echo "test" | aws s3 cp - s3://your-bucket-name/test.txt
   ```

3. **Verify CORS configuration** (if accessing from browser):
   ```json
   {
       "CORSRules": [
           {
               "AllowedOrigins": ["http://localhost:8000"],
               "AllowedMethods": ["GET", "POST", "PUT"],
               "AllowedHeaders": ["*"]
           }
       ]
   }
   ```

## Deployment Issues

### Docker Problems

#### Container Build Failures

**Problem**: Docker build fails with dependency or permission errors.

**Solutions**:

1. **Check Dockerfile syntax**:
   ```bash
   docker build -t mbl2pc . --no-cache
   ```

2. **Common fixes**:
   ```dockerfile
   # Ensure Python 3.13 is available
   FROM python:3.13-slim

   # Install system dependencies if needed
   RUN apt-get update && apt-get install -y build-essential

   # Copy requirements before source code for better caching
   COPY pyproject.toml ./
   RUN pip install -e .
   ```

#### Container Runtime Issues

**Problem**: Container starts but application fails.

**Solutions**:

1. **Check container logs**:
   ```bash
   docker logs container-name
   docker-compose logs -f
   ```

2. **Environment variable issues**:
   ```bash
   # Check environment variables are passed correctly
   docker run -it --env-file .env mbl2pc env | grep -E "^[A-Z]"
   ```

3. **Port binding issues**:
   ```bash
   # Ensure port is properly exposed
   docker run -p 8000:8000 mbl2pc
   ```

### Cloud Deployment Issues

#### Render.com Deployment

**Problem**: Deployment fails or application doesn't start.

**Solutions**:

1. **Check build logs** in Render dashboard

2. **Common issues**:
   ```yaml
   # render.yaml - ensure correct configuration
   services:
     - type: web
       runtime: python
       buildCommand: "pip install -e ."
       startCommand: "uvicorn src.mbl2pc.main:app --host 0.0.0.0 --port $PORT"
   ```

3. **Environment variables**:
   - Ensure all required variables are set in Render dashboard
   - Check `OAUTH_REDIRECT_URI` matches your Render URL

#### AWS Lambda Deployment

**Problem**: Lambda function fails to start or times out.

**Solutions**:

1. **Check handler configuration**:
   ```python
   # main.py
   from mangum import Mangum

   app = FastAPI()
   handler = Mangum(app)
   ```

2. **Cold start optimization**:
   ```python
   # Keep connections warm
   @app.on_event("startup")
   async def startup():
       # Initialize connections
       pass
   ```

3. **Memory and timeout settings**:
   - Increase Lambda memory (512MB+)
   - Increase timeout (30s+)

## Performance Issues

### Slow Response Times

**Problem**: API responses are slower than expected.

**Solutions**:

1. **Check database queries**:
   ```python
   # Use efficient DynamoDB queries
   # Avoid scans when possible
   response = table.query(
       KeyConditionExpression=Key('user_id').eq(user_id)
   )
   ```

2. **Monitor async/await usage**:
   ```python
   # ✅ Good - Properly async
   async def process_data():
       result = await async_operation()
       return result

   # ❌ Bad - Blocking operation
   async def process_data():
       result = blocking_operation()  # Blocks event loop
       return result
   ```

3. **Add connection pooling**:
   ```python
   # Configure boto3 with connection pooling
   session = boto3.Session()
   dynamodb = session.resource(
       'dynamodb',
       config=Config(
           max_pool_connections=50
       )
   )
   ```

### Memory Issues

**Problem**: Application consumes too much memory or has memory leaks.

**Solutions**:

1. **Monitor memory usage**:
   ```bash
   # In development
   python -m memory_profiler your_script.py

   # In production
   # Use CloudWatch or similar monitoring
   ```

2. **Check for memory leaks**:
   ```python
   # Avoid storing large objects in memory
   # Use generators for large datasets

   def process_messages():
       for message in get_messages_generator():
           yield process(message)
   ```

## Getting Help

### Debug Information to Collect

When reporting issues, include:

1. **Environment info**:
   ```bash
   python --version
   pip list | grep -E "(fastapi|pydantic|boto3)"
   ```

2. **Configuration** (sanitized):
   ```bash
   # .env file (remove sensitive values)
   cat .env | sed 's/=.*/=***/'
   ```

3. **Error logs**:
   ```bash
   # Application logs
   journalctl -u mbl2pc -n 50

   # Docker logs
   docker-compose logs --tail=50
   ```

4. **Test results**:
   ```bash
   make ci 2>&1 | head -100
   ```

### Resources

- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share solutions
- **Documentation**: [All docs](./README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

### Emergency Fixes

#### Application Won't Start

```bash
# Quick diagnostic
python -c "import src.mbl2pc.main; print('✅ Import successful')"

# Check dependencies
pip check

# Reset environment
rm -rf .venv
make install
```

#### Database Connection Lost

```bash
# Test AWS connectivity
aws sts get-caller-identity

# Check table status
aws dynamodb describe-table --table-name your-table-name

# Verify credentials
aws configure list
```

#### Authentication Broken

```bash
# Check OAuth configuration
curl -i http://localhost:8000/login

# Verify environment variables
grep -E "GOOGLE|OAUTH|SESSION" .env

# Test with new session
# Clear browser cookies and try again
```

---

**Still stuck?** Open an issue with the debug information above, and we'll help you resolve it!
