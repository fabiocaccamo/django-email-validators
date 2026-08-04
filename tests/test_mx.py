"""
Tests for the MX lookup helpers in the mx module.
"""

from unittest.mock import MagicMock, patch

import dns.exception
import dns.resolver

from django_email_validators.mx import (
    _resolve_mx_hosts,
    get_domain_suffixes,
    get_mx_hosts,
)


class TestGetDomainSuffixes:
    """Test the get_domain_suffixes function."""

    def test_subdomain_host(self):
        """Test progressive suffixes down to 2 labels (never the bare TLD)."""
        assert get_domain_suffixes("prd-smtp.10minutemail.com") == [
            "prd-smtp.10minutemail.com",
            "10minutemail.com",
        ]

    def test_deep_subdomain_host(self):
        """Test that all intermediate suffixes are returned."""
        assert get_domain_suffixes("a.b.c.d") == ["a.b.c.d", "b.c.d", "c.d"]

    def test_two_label_host(self):
        """Test that a 2-label host returns itself only."""
        assert get_domain_suffixes("example.com") == ["example.com"]

    def test_single_label_host(self):
        """Test that a single-label host returns no suffixes."""
        assert get_domain_suffixes("localhost") == []


class TestGetMXHosts:
    """Test the get_mx_hosts function."""

    def setup_method(self):
        _resolve_mx_hosts.cache_clear()

    @patch("dns.resolver.resolve")
    def test_domain_with_mx_records(self, mock_resolve):
        """Test that MX hostnames are lowercased with no trailing dot."""
        mock_resolve.return_value = [
            MagicMock(exchange="Mail1.Example.COM."),
            MagicMock(exchange="mail2.example.com."),
        ]
        assert get_mx_hosts("example.com") == [
            "mail1.example.com",
            "mail2.example.com",
        ]
        mock_resolve.assert_called_once_with("example.com", "MX")

    @patch("dns.resolver.resolve")
    def test_domain_without_mx_records(self, mock_resolve):
        """Test that a domain with no MX records returns an empty list."""
        mock_resolve.side_effect = dns.resolver.NoAnswer()
        assert get_mx_hosts("example.com") == []

    @patch("dns.resolver.resolve")
    def test_nonexistent_domain(self, mock_resolve):
        """Test that a nonexistent domain returns an empty list."""
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()
        assert get_mx_hosts("nonexistent.example") == []

    @patch("dns.resolver.resolve")
    def test_lookup_timeout_returns_none(self, mock_resolve):
        """Test that an infrastructure error (timeout) returns None (fail open)."""
        mock_resolve.side_effect = dns.exception.Timeout()
        assert get_mx_hosts("example.com") is None

    @patch("dns.resolver.resolve")
    def test_no_nameservers_returns_none(self, mock_resolve):
        """Test that a no-nameservers error returns None (fail open)."""
        mock_resolve.side_effect = dns.resolver.NoNameservers()
        assert get_mx_hosts("example.com") is None

    @patch("dns.resolver.resolve")
    def test_null_mx_record(self, mock_resolve):
        """Test that a null MX record (RFC 7505) yields no hosts."""
        mock_resolve.return_value = [MagicMock(exchange=".")]
        assert get_mx_hosts("example.com") == []

    @patch("dns.resolver.resolve")
    def test_lookup_is_cached(self, mock_resolve):
        """Test that repeated lookups for the same domain hit the cache."""
        mock_resolve.return_value = [MagicMock(exchange="mail.example.com.")]
        assert get_mx_hosts("example.com") == ["mail.example.com"]
        assert get_mx_hosts("example.com") == ["mail.example.com"]
        mock_resolve.assert_called_once()

    @patch("dns.resolver.resolve")
    def test_lookup_failure_is_not_cached(self, mock_resolve):
        """Test that transient failures are not cached (retried on next call)."""
        mock_resolve.side_effect = [
            dns.exception.Timeout(),
            [MagicMock(exchange="mail.example.com.")],
        ]
        assert get_mx_hosts("example.com") is None
        assert get_mx_hosts("example.com") == ["mail.example.com"]
        assert mock_resolve.call_count == 2
