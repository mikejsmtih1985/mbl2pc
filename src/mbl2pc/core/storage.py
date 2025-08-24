"""
Handles interactions with AWS services like DynamoDB and S3.
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import sys
from mbl2pc.core.config import DDB_TABLE, DDB_REGION, S3_BUCKET

# --- DynamoDB Setup ---
dynamodb_resource = None
table = None
try:
    dynamodb_resource = boto3.resource("dynamodb", region_name=DDB_REGION)
    table = dynamodb_resource.Table(DDB_TABLE)
except Exception as e:
    print(f"[ERROR] Failed to initialize DynamoDB: {e}", file=sys.stderr)

def get_db_table():
    """Dependency to get the DynamoDB table resource."""
    if not table:
        raise ConnectionError("DynamoDB table is not initialized.")
    return table

# --- S3 Setup ---
s3_client = None
try:
    s3_client = boto3.client("s3", region_name=DDB_REGION)
except Exception as e:
    print(f"[ERROR] Failed to initialize S3 client: {e}", file=sys.stderr)

def get_s3_client():
    """Dependency to get the S3 client."""
    if not s3_client:
        raise ConnectionError("S3 client is not initialized.")
    return s3_client
