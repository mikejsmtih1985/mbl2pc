"""
Unit tests for helper functions and business logic.
"""

from unittest.mock import Mock

import pytest

from mbl2pc.api.chat import _guess_sender_from_ua


@pytest.mark.parametrize(
    "user_agent, expected_sender",
    [
        ("Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X)", "iPhone"),
        ("Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36", "Android"),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "PC"),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "unknown",
        ),
        ("", "unknown"),
    ],
)
def test_guess_sender_from_ua(user_agent, expected_sender):
    """
    Tests the _guess_sender_from_ua function with various User-Agent strings.
    """
    mock_request = Mock()
    mock_request.headers.get.return_value = user_agent

    sender = _guess_sender_from_ua(mock_request)

    assert sender == expected_sender
    mock_request.headers.get.assert_called_with("user-agent", "")
