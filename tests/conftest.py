import shutil
from pathlib import Path

import pytest
from dotenv import load_dotenv
from xprocess import ProcessStarter

# Load environment variables from .env.local
# This needs to be done before the application is imported.
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env.local")


@pytest.fixture(scope="session")
def web_server(xprocess):
    """
    Fixture to run the Uvicorn web server in the background for E2E tests.
    """
    # Find the absolute path to the uvicorn executable in the current venv
    uvicorn_path = shutil.which("uvicorn")
    if not uvicorn_path:
        pytest.fail("uvicorn executable not found in PATH")

    project_root = Path(__file__).parent.parent

    class Starter(ProcessStarter):
        # Command to start the server
        pattern = "Application startup complete"
        args = [
            uvicorn_path,
            "src.mbl2pc.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--env-file",
            str(project_root / ".env.test"),
        ]
        # Set the PYTHONPATH to the project root
        env = {"PYTHONPATH": str(project_root)}

    # Start the server and wait for it to be ready
    xprocess.ensure("web_server", Starter)

    yield

    # Teardown: stop the server
    xprocess.getinfo("web_server").terminate()
