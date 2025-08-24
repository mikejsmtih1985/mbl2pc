"""
Handles interactions with AWS services like DynamoDB and S3.
"""

import datetime
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from .config import settings
from ..schemas import Message


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


session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    aws_session_token=settings.AWS_SESSION_TOKEN,
    region_name=settings.AWS_REGION,
)
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(settings.MBL2PC_DDB_TABLE)


def add_message(message: Message):
    now = datetime.datetime.now(datetime.UTC).isoformat()
    table.put_item(
        Item={
            "pk": message.user_id,
            "sk": f"{now}#{uuid.uuid4()}",
            "message": message.message,
        }
    )


def get_messages(user_id: str) -> list[Message]:
    response = table.query(KeyConditionExpression=Key("pk").eq(user_id))
    return [
        Message(user_id=item["pk"], message=item["message"])
        for item in response["Items"]
    ]


def get_db():
    return table
