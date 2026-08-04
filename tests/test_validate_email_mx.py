"""
Tests for the validate_email_mx function.
"""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from django_email_validators.validators import validate_email_mx


class TestValidateEmailMX:
    """Test the validate_email_mx function."""

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_passes_on_valid_mx(self, mock_get_mx_hosts):
        """Test that email with valid MX records passes."""
        mock_get_mx_hosts.return_value = ["mail.example.com"]
        validate_email_mx("test@example.com")  # Should not raise
        mock_get_mx_hosts.assert_called_once_with("example.com")

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_raises_on_invalid_mx(self, mock_get_mx_hosts):
        """Test that email without MX records raises ValidationError."""
        mock_get_mx_hosts.return_value = []
        with pytest.raises(ValidationError):
            validate_email_mx("test@invalid.com")

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_passes_on_lookup_failure(self, mock_get_mx_hosts):
        """Test that an infrastructure DNS failure fails open (no rejection)."""
        mock_get_mx_hosts.return_value = None
        validate_email_mx("test@example.com")  # Should not raise

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_custom_message(self, mock_get_mx_hosts):
        """Test custom error message."""
        mock_get_mx_hosts.return_value = []
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_mx("test@invalid.com", message="Custom error")

    def test_invalid_email_syntax(self):
        """Test that invalid email syntax raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_email_mx("invalid-email")
