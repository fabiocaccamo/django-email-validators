"""
Tests for the validate_email_mx function.
"""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from email_validator import EmailNotValidError

from django_email_validators.validators import validate_email_mx


class TestValidateEmailMX:
    """Test the validate_email_mx function."""

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_passes_on_valid_mx(self, mock_deliverability):
        """Test that email with valid MX records passes."""
        mock_deliverability.return_value = {"email": "test@example.com"}
        validate_email_mx("test@example.com")  # Should not raise

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_raises_on_invalid_mx(self, mock_deliverability):
        """Test that email with invalid MX records raises ValidationError."""
        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError):
            validate_email_mx("test@invalid.com")

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_custom_message(self, mock_deliverability):
        """Test custom error message."""
        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_mx("test@invalid.com", message="Custom error")

    def test_invalid_email_syntax(self):
        """Test that invalid email syntax raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_email_mx("invalid-email")
