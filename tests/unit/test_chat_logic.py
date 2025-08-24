"""
Unit tests for pure business logic and helper functions.
These tests focus on isolated functions without dependencies.
"""

from unittest.mock import Mock
import pytest
from mbl2pc.api.chat import _guess_sender_from_ua


class TestUserAgentDetection:
    """Unit tests for user agent detection logic."""
    
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
            (None, "unknown"),  # Edge case: None user agent
        ],
    )
    def test_guess_sender_from_user_agent_string(self, user_agent, expected_sender):
        """
        Unit test: Verify user agent string parsing logic works correctly.
        Tests the pure logic without any HTTP dependencies.
        """
        mock_request = Mock()
        mock_request.headers.get.return_value = user_agent

        result = _guess_sender_from_ua(mock_request)

        assert result == expected_sender
        mock_request.headers.get.assert_called_once_with("user-agent", "")

    def test_handles_missing_user_agent_header(self):
        """
        Unit test: Verify function handles missing user-agent header gracefully.
        """
        mock_request = Mock()
        mock_request.headers.get.return_value = ""  # Simulates missing header

        result = _guess_sender_from_ua(mock_request)

        assert result == "unknown"

    def test_case_sensitivity_in_user_agent_detection(self):
        """
        Unit test: Verify user agent detection is case-sensitive as expected.
        """
        test_cases = [
            ("iphone", "unknown"),  # lowercase should not match
            ("IPHONE", "unknown"),  # uppercase should not match  
            ("iPhone", "iPhone"),   # exact case should match
        ]
        
        for user_agent, expected in test_cases:
            mock_request = Mock()
            mock_request.headers.get.return_value = f"Mozilla/5.0 ({user_agent})"
            
            result = _guess_sender_from_ua(mock_request)
            assert result == expected
