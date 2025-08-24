"""
Custom exception hierarchy for better error handling.
"""

from typing import Any


class MBL2PCError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}


class ValidationError(MBL2PCError):
    """Raised when data validation fails."""


class AuthenticationError(MBL2PCError):
    """Raised when authentication fails."""


class AuthorizationError(MBL2PCError):
    """Raised when authorization fails."""


class StorageError(MBL2PCError):
    """Raised when storage operations fail."""


class ConfigurationError(MBL2PCError):
    """Raised when configuration is invalid."""


class ExternalServiceError(MBL2PCError):
    """Raised when external service calls fail."""
