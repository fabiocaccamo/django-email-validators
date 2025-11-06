"""
Tests for the main validate_email_* functions.
"""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from django_email_validators.validators import (
    validate_email_mx,
    validate_email_non_disposable,
    validate_email_provider_typo,
)


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
        from email_validator import EmailNotValidError

        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError):
            validate_email_mx("test@invalid.com")

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_custom_message(self, mock_deliverability):
        """Test custom error message."""
        from email_validator import EmailNotValidError

        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_mx("test@invalid.com", message="Custom error")


class TestValidateEmailProviderTypo:
    """Test the validate_email_provider_typo function."""

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_passes_on_valid_provider(self, mock_deliverability):
        """Test that email with valid provider passes."""
        mock_deliverability.return_value = {"email": "test@gmail.com"}
        validate_email_provider_typo("test@gmail.com")  # Should not raise
        validate_email_provider_typo("test@yahoo.com")  # Should not raise
        validate_email_provider_typo("test@outlook.com")  # Should not raise

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_raises_on_typo_with_no_mx(self, mock_deliverability):
        """Test that distance-1 typos with no MX records are caught."""
        from email_validator import EmailNotValidError

        mock_deliverability.side_effect = EmailNotValidError("No MX records")

        # Missing character
        with pytest.raises(ValidationError, match="Did you mean"):
            validate_email_provider_typo("test@gmai.com")

        # Extra character
        with pytest.raises(ValidationError, match="Did you mean"):
            validate_email_provider_typo("test@gmaill.com")

        # Wrong character
        with pytest.raises(ValidationError, match="Did you mean"):
            validate_email_provider_typo("test@gmeil.com")

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_passes_on_typo_with_valid_mx(self, mock_deliverability):
        """Test that similar domains with valid MX records pass (no false positives)."""
        mock_deliverability.return_value = {"email": "test@aoly.com"}
        validate_email_provider_typo(
            "test@aoly.com"
        )  # Should not raise (similar to aol.com but valid)

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_passes_on_distance_2_typo(self, mock_deliverability):
        """Test that distance-2+ typos pass to avoid false positives."""
        mock_deliverability.return_value = {"email": "test@example.com"}
        validate_email_provider_typo("test@gmai.co")  # Should not raise
        validate_email_provider_typo("test@gmil.com")  # Should not raise

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_suggestion_format(self, mock_deliverability):
        """Test that suggestion includes corrected email."""
        from email_validator import EmailNotValidError

        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError) as exc_info:
            validate_email_provider_typo("user@gmai.com")
        assert "user@gmail.com" in str(exc_info.value)

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_case_insensitive(self, mock_deliverability):
        """Test that provider matching is case-insensitive."""
        mock_deliverability.return_value = {"email": "test@gmail.com"}
        validate_email_provider_typo("test@GMAIL.COM")  # Should not raise
        validate_email_provider_typo("test@Gmail.Com")  # Should not raise

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_custom_message(self, mock_deliverability):
        """Test custom error message."""
        from email_validator import EmailNotValidError

        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_provider_typo("test@gmai.com", message="Custom error")

    def test_invalid_email_syntax(self):
        """Test that invalid email syntax raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_email_provider_typo("invalid-email")
