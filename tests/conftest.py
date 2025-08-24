import pytest
from xprocess import ProcessStarter
import sys
import shutil

@pytest.fixture(scope="session")
def web_server(xprocess):
    """
    Fixture to run the Uvicorn web server in the background for E2E tests.
    """
    # Find the absolute path to the uvicorn executable in the current venv
    uvicorn_path = shutil.which("uvicorn")
    if not uvicorn_path:
        pytest.fail("uvicorn executable not found in PATH")

    class Starter(ProcessStarter):
        # Command to start the server
        pattern = "Application startup complete"
        args = [
            uvicorn_path,
            "src.mbl2pc.main:app",
            "--host", "127.0.0.1",
            "--port", "8000"
        ]
        # Set the PYTHONPATH to the project root
        env = {"PYTHONPATH": "."}

    # Start the server and wait for it to be ready
    xprocess.ensure("web_server", Starter)

    yield

    # Teardown: stop the server
    xprocess.getinfo("web_server").terminate()
