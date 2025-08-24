"""
Configuration for pytest.
"""

import pytest
from fastapi.testclient import TestClient

from mbl2pc.core.dependencies import get_current_user
from mbl2pc.main import app
from mbl2pc.schemas import User

MOCK_USER = User(sub="test-user-123", name="Test User", email="test@example.com")


def override_get_current_user():
    """
    Mock dependency to override get_current_user.
    """
    return MOCK_USER


@pytest.fixture
def authenticated_client():
    """
    Returns a test client with an authenticated user.
    """
    app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(app)
    yield client
    del app.dependency_overrides[get_current_user]
