"""
E2E test configuration.
"""

import pytest
from xprocess import ProcessStarter
import sys


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
            "-m",
            "uvicorn",
            "mbl2pc.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ]

    xprocess.ensure("web_server", Starter)

    yield

    xprocess.getinfo("web_server").terminate()
