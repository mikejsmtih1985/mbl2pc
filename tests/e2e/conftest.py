"""
E2E test configuration.
"""

import os
import sys

import pytest
from xprocess import ProcessStarter


@pytest.fixture(scope="session")
def web_server(xprocess):
    """
    Starts the web server as a background process for E2E tests.
    """

    class Starter(ProcessStarter):
        """Process starter for the Uvicorn server."""

        pattern = "Application startup complete"
        args = [
            sys.executable,
            "-c",
            (
                "import sys; sys.path.insert(0, 'src'); import uvicorn; "
                "uvicorn.run('mbl2pc.main:app', host='127.0.0.1', port=8000)"
            ),
        ]

        env = os.environ.copy()
        # Set mock AWS environment variables to avoid credential issues
        env.update(
            {
                "AWS_ACCESS_KEY_ID": "test",
                "AWS_SECRET_ACCESS_KEY": "test",
                "AWS_REGION": "us-east-1",
                "MBL2PC_DDB_TABLE": "test-table",
                "S3_BUCKET": "test-bucket",
                "SESSION_SECRET_KEY": "test-secret-key-for-sessions",
                "DYNAMODB_ENDPOINT_URL": "http://localhost:8001",  # Fail gracefully
                "S3_ENDPOINT_URL": "http://localhost:9000",  # Fail gracefully
                "GOOGLE_CLIENT_ID": "test-client-id",
                "GOOGLE_CLIENT_SECRET": "test-client-secret",
            }
        )

    xprocess.ensure("web_server", Starter)

    yield

    xprocess.getinfo("web_server").terminate()
