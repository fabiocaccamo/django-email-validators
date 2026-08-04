"""
Tests for the validate_email_provider_typo function.
"""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from django_email_validators.validators import validate_email_provider_typo


class TestValidateEmailProviderTypo:
    """Test the validate_email_provider_typo function."""

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_passes_on_valid_provider(self, mock_get_mx_hosts):
        """Test that email with valid provider passes."""
        mock_get_mx_hosts.return_value = ["mail.example.com"]
        validate_email_provider_typo("test@gmail.com")  # Should not raise
        validate_email_provider_typo("test@yahoo.com")  # Should not raise
        validate_email_provider_typo("test@outlook.com")  # Should not raise

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_raises_on_typo_missing_char(self, mock_get_mx_hosts):
        """Missing character typo with no MX records is caught."""
        mock_get_mx_hosts.return_value = []
        with pytest.raises(ValidationError, match="Did you mean"):
            validate_email_provider_typo("test@gmai.com")

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_raises_on_typo_extra_char(self, mock_get_mx_hosts):
        """Extra character typo with no MX records is caught."""
        mock_get_mx_hosts.return_value = []
        with pytest.raises(ValidationError, match="Did you mean"):
            validate_email_provider_typo("test@gmaill.com")

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_raises_on_typo_wrong_char(self, mock_get_mx_hosts):
        """Wrong character typo with no MX records is caught."""
        mock_get_mx_hosts.return_value = []
        with pytest.raises(ValidationError, match="Did you mean"):
            validate_email_provider_typo("test@gmeil.com")

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_passes_on_typo_with_valid_mx(self, mock_get_mx_hosts):
        """Similar domain with valid MX records passes (no false positives)."""
        mock_get_mx_hosts.return_value = ["mail.aoly.com"]
        validate_email_provider_typo("test@aoly.com")  # Should not raise

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_passes_on_lookup_failure(self, mock_get_mx_hosts):
        """Potential typo with a failed MX lookup fails open (no rejection)."""
        mock_get_mx_hosts.return_value = None
        validate_email_provider_typo("test@gmai.com")  # Should not raise

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_passes_on_distance_2_typo(self, mock_get_mx_hosts):
        """Distance-2+ typos pass to avoid false positives."""
        mock_get_mx_hosts.return_value = []
        validate_email_provider_typo("test@gmai.co")  # Should not raise
        validate_email_provider_typo("test@gmial.co")  # Should not raise

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_suggestion_format(self, mock_get_mx_hosts):
        """Suggestion includes the corrected email address."""
        mock_get_mx_hosts.return_value = []
        with pytest.raises(ValidationError) as exc_info:
            validate_email_provider_typo("user@gmai.com")
        assert "user@gmail.com" in str(exc_info.value)

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_case_insensitive(self, mock_get_mx_hosts):
        """Provider matching is case-insensitive."""
        mock_get_mx_hosts.return_value = ["mail.example.com"]
        validate_email_provider_typo("test@GMAIL.COM")  # Should not raise
        validate_email_provider_typo("test@Gmail.Com")  # Should not raise

    @patch("django_email_validators.validators.get_mx_hosts")
    def test_custom_message(self, mock_get_mx_hosts):
        """Custom error message is raised."""
        mock_get_mx_hosts.return_value = []
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_provider_typo("test@gmai.com", message="Custom error")

    def test_invalid_email_syntax(self):
        """Invalid email syntax raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_email_provider_typo("invalid-email")
