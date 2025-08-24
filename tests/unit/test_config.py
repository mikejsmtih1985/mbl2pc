"""
Unit tests for configuration validation.
"""

import pytest
from pydantic import ValidationError

from mbl2pc.core.config import Settings


class TestSettings:
    """Test suite for Settings configuration."""

    def test_default_settings_creation(self) -> None:
        """Test that Settings can be created with defaults."""
        settings = Settings()  # type: ignore[call-arg]
        assert settings.AWS_REGION == "us-east-1"
        assert settings.MBL2PC_DDB_TABLE == "mbl2pc-messages"

    def test_session_secret_key_validation_too_short(self) -> None:
        """Test that short session keys are rejected."""
        with pytest.raises(ValidationError, match="at least 32 characters"):
            Settings(SESSION_SECRET_KEY="short")  # type: ignore[call-arg]

    def test_session_secret_key_validation_minimum_length(self) -> None:
        """Test that 32-character session keys are accepted."""
        key = "a" * 32
        settings = Settings(SESSION_SECRET_KEY=key)  # type: ignore[call-arg]
        assert key == settings.SESSION_SECRET_KEY

    def test_oauth_credentials_warning_for_test_values(self) -> None:
        """Test that test OAuth credentials trigger warnings."""
        with pytest.warns(UserWarning, match="test OAuth credentials"):
            Settings(GOOGLE_CLIENT_ID="test-client-id")  # type: ignore[call-arg]

    def test_app_version_property(self) -> None:
        """Test that app_version property returns a string."""
        settings = Settings()  # type: ignore[call-arg]
        version = settings.app_version
        assert isinstance(version, str)
        assert len(version) > 0
