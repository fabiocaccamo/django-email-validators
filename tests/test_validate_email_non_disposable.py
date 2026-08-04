"""
Tests for the validate_email_non_disposable function.
"""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from django_email_validators.validators import validate_email_non_disposable


class TestValidateEmailNonDisposable:
    """Test the validate_email_non_disposable function."""

    @patch("django_email_validators.validators.email_is_disposable")
    def test_passes_on_non_disposable(self, mock_is_disposable):
        """Test that non-disposable email passes validation."""
        mock_is_disposable.return_value = False
        validate_email_non_disposable("test@example.com")  # Should not raise

    @patch("django_email_validators.validators.email_is_disposable")
    def test_raises_on_disposable(self, mock_is_disposable):
        """Test that disposable email raises ValidationError."""
        mock_is_disposable.return_value = True
        with pytest.raises(ValidationError):
            validate_email_non_disposable("test@disposable.com")

    @patch("django_email_validators.validators.email_is_disposable")
    def test_custom_message(self, mock_is_disposable):
        """Test custom error message."""
        mock_is_disposable.return_value = True
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_non_disposable("test@disposable.com", message="Custom error")

    @patch("django_email_validators.validators.email_is_disposable")
    def test_check_mx_disabled_by_default(self, mock_is_disposable):
        """Test that check_mx defaults to False."""
        mock_is_disposable.return_value = False
        validate_email_non_disposable("test@example.com")
        mock_is_disposable.assert_called_once_with("test@example.com", check_mx=False)

    @patch("django_email_validators.validators.email_is_disposable")
    def test_check_mx_propagation(self, mock_is_disposable):
        """Test that check_mx is propagated to email_is_disposable."""
        mock_is_disposable.return_value = True
        with pytest.raises(ValidationError):
            validate_email_non_disposable("test@fresh-domain.net", check_mx=True)
        mock_is_disposable.assert_called_once_with(
            "test@fresh-domain.net", check_mx=True
        )

    def test_invalid_email_syntax(self):
        """Test that invalid email syntax raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_email_non_disposable("invalid-email")
