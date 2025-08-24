"""
Handles interactions with AWS services like DynamoDB and S3.
"""

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from src.mbl2pc.core.config import settings


def get_db_table():
    """
    Returns a DynamoDB table resource.
    """
    try:
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.DYNAMODB_ENDPOINT_URL,
        )
        return dynamodb.Table(settings.MBL2PC_DDB_TABLE)
    except ClientError as e:
        print(f"Error getting DynamoDB table: {e}")
        return None


def get_s3_client() -> BaseClient | None:
    """
    Returns an S3 client.
    """
    try:
        return boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )
    except ClientError as e:
        print(f"Error getting S3 client: {e}")
        return None
