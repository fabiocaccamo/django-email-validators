"""
Tests for the email_is_disposable function.
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

    @patch("django_email_validators.validators.blocklist", [])
    @patch("django_email_validators.validators.MailChecker.is_valid")
    @patch("django_email_validators.validators.get_mx_hosts")
    def test_check_mx_disabled_by_default(self, mock_get_mx_hosts, mock_mailchecker):
        """Test that no MX lookup is performed with the default check_mx=False."""
        mock_mailchecker.return_value = True
        assert email_is_disposable("test@example.com") is False
        mock_get_mx_hosts.assert_not_called()

    @patch("django_email_validators.validators.blocklist", ["10minutemail.com"])
    @patch("django_email_validators.validators.MailChecker.is_valid")
    @patch("django_email_validators.validators.get_mx_hosts")
    def test_check_mx_detects_fresh_domain_via_blocklist(
        self, mock_get_mx_hosts, mock_mailchecker
    ):
        """
        Test that a fresh facade domain is detected via its MX records.

        Real-world case: "kjkpc.net" is not in any blocklist, but its MX
        record points to "prd-smtp.10minutemail.com", and "10minutemail.com"
        is blocklisted.
        """
        mock_mailchecker.return_value = True
        mock_get_mx_hosts.return_value = ["prd-smtp.10minutemail.com"]
        assert email_is_disposable("test@kjkpc.net", check_mx=True) is True
        mock_get_mx_hosts.assert_called_once_with("kjkpc.net")

    @patch("django_email_validators.validators.blocklist", [])
    @patch(
        "django_email_validators.validators.MailChecker.blacklist", {"tempmail.example"}
    )
    @patch("django_email_validators.validators.MailChecker.is_valid")
    @patch("django_email_validators.validators.get_mx_hosts")
    def test_check_mx_detects_fresh_domain_via_mailchecker(
        self, mock_get_mx_hosts, mock_mailchecker
    ):
        """Test that MX hostnames are also checked against the MailChecker blacklist."""
        mock_mailchecker.return_value = True
        mock_get_mx_hosts.return_value = ["mx.tempmail.example"]
        assert email_is_disposable("test@fresh-domain.net", check_mx=True) is True

    @patch("django_email_validators.validators.blocklist", [])
    @patch("django_email_validators.validators.MailChecker.blacklist", set())
    @patch("django_email_validators.validators.MailChecker.is_valid")
    @patch("django_email_validators.validators.get_mx_hosts")
    def test_check_mx_passes_on_clean_mx(self, mock_get_mx_hosts, mock_mailchecker):
        """Test that check_mx=True returns False when MX hosts are not blocklisted."""
        mock_mailchecker.return_value = True
        mock_get_mx_hosts.return_value = ["mail.example.com"]
        assert email_is_disposable("test@example.com", check_mx=True) is False

    @patch("django_email_validators.validators.blocklist", [])
    @patch("django_email_validators.validators.MailChecker.is_valid")
    @patch("django_email_validators.validators.get_mx_hosts")
    def test_check_mx_passes_on_no_mx_records(
        self, mock_get_mx_hosts, mock_mailchecker
    ):
        """Test that check_mx=True returns False when the domain has no MX records."""
        mock_mailchecker.return_value = True
        mock_get_mx_hosts.return_value = []
        assert email_is_disposable("test@example.com", check_mx=True) is False
