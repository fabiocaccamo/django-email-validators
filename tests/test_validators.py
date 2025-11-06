"""
Tests for email validation helper functions.
"""

from unittest.mock import patch

from django_email_validators.validators import email_is_disposable


class TestEmailIsDisposable:
    """Test the email_is_disposable function."""

    @patch("django_email_validators.validators.blocklist", ["disposable.com"])
    @patch("django_email_validators.validators.MailChecker.is_valid")
    def test_blocklist_check(self, mock_mailchecker):
        """Test that blocklist is checked."""
        mock_mailchecker.return_value = True
        assert email_is_disposable("test@disposable.com") is True

    @patch("django_email_validators.validators.blocklist", [])
    @patch("django_email_validators.validators.MailChecker.is_valid")
    def test_mailchecker_check(self, mock_mailchecker):
        """Test that MailChecker is called."""
        mock_mailchecker.return_value = False
        assert email_is_disposable("test@example.com") is True
        mock_mailchecker.assert_called_once_with("test@example.com")

    @patch("django_email_validators.validators.blocklist", [])
    @patch("django_email_validators.validators.MailChecker.is_valid")
    def test_non_disposable_email(self, mock_mailchecker):
        """Test that non-disposable email returns False."""
        mock_mailchecker.return_value = True
        assert email_is_disposable("test@example.com") is False
