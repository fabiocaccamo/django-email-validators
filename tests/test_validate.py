"""
Tests for the main validate_email_* functions.
"""
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from django_validate_email_strict.validators import (
    validate_email_mx,
    validate_email_non_disposable,
)


class TestValidateEmailNonDisposable:
    """Test the validate_email_non_disposable function."""

    @patch("django_validate_email_strict.validators.email_is_disposable")
    def test_passes_on_non_disposable(self, mock_is_disposable):
        """Test that non-disposable email passes validation."""
        mock_is_disposable.return_value = False
        validate_email_non_disposable("test@example.com")  # Should not raise

    @patch("django_validate_email_strict.validators.email_is_disposable")
    def test_raises_on_disposable(self, mock_is_disposable):
        """Test that disposable email raises ValidationError."""
        mock_is_disposable.return_value = True
        with pytest.raises(ValidationError):
            validate_email_non_disposable("test@disposable.com")

    @patch("django_validate_email_strict.validators.email_is_disposable")
    def test_custom_message(self, mock_is_disposable):
        """Test custom error message."""
        mock_is_disposable.return_value = True
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_non_disposable("test@disposable.com", message="Custom error")


class TestValidateEmailMX:
    """Test the validate_email_mx function."""

    @patch("django_validate_email_strict.validators.validate_email_deliverability")
    def test_passes_on_valid_mx(self, mock_deliverability):
        """Test that email with valid MX records passes."""
        mock_deliverability.return_value = {"email": "test@example.com"}
        validate_email_mx("test@example.com")  # Should not raise

    @patch("django_validate_email_strict.validators.validate_email_deliverability")
    def test_raises_on_invalid_mx(self, mock_deliverability):
        """Test that email with invalid MX records raises ValidationError."""
        from email_validator import EmailNotValidError

        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError):
            validate_email_mx("test@invalid.com")

    @patch("django_validate_email_strict.validators.validate_email_deliverability")
    def test_custom_message(self, mock_deliverability):
        """Test custom error message."""
        from email_validator import EmailNotValidError

        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_mx("test@invalid.com", message="Custom error")
