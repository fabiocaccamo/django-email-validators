"""
Tests for the validate_email_provider_typo function.
"""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from email_validator import EmailNotValidError

from django_email_validators.validators import validate_email_provider_typo


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
    def test_raises_on_typo_missing_char(self, mock_deliverability):
        """Missing character typo with no MX records is caught."""
        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError, match="Did you mean"):
            validate_email_provider_typo("test@gmai.com")

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_raises_on_typo_extra_char(self, mock_deliverability):
        """Extra character typo with no MX records is caught."""
        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError, match="Did you mean"):
            validate_email_provider_typo("test@gmaill.com")

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_raises_on_typo_wrong_char(self, mock_deliverability):
        """Wrong character typo with no MX records is caught."""
        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError, match="Did you mean"):
            validate_email_provider_typo("test@gmeil.com")

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_passes_on_typo_with_valid_mx(self, mock_deliverability):
        """Similar domain with valid MX records passes (no false positives)."""
        mock_deliverability.return_value = {"email": "test@aoly.com"}
        validate_email_provider_typo("test@aoly.com")  # Should not raise

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_passes_on_distance_2_typo(self, mock_deliverability):
        """Distance-2+ typos pass to avoid false positives."""
        mock_deliverability.return_value = {"email": "test@example.com"}
        validate_email_provider_typo("test@gmai.co")  # Should not raise
        validate_email_provider_typo("test@gmil.com")  # Should not raise

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_suggestion_format(self, mock_deliverability):
        """Suggestion includes the corrected email address."""
        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError) as exc_info:
            validate_email_provider_typo("user@gmai.com")
        assert "user@gmail.com" in str(exc_info.value)

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_case_insensitive(self, mock_deliverability):
        """Provider matching is case-insensitive."""
        mock_deliverability.return_value = {"email": "test@gmail.com"}
        validate_email_provider_typo("test@GMAIL.COM")  # Should not raise
        validate_email_provider_typo("test@Gmail.Com")  # Should not raise

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_custom_message(self, mock_deliverability):
        """Custom error message is raised."""
        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_provider_typo("test@gmai.com", message="Custom error")

    def test_invalid_email_syntax(self):
        """Invalid email syntax raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_email_provider_typo("invalid-email")
