"""
Tests for the canonicalize_email helper.
"""

from django_email_validators.utils import canonicalize_email


class TestCanonicalizeEmail:
    """Test canonicalize_email: one canonical form per inbox."""

    def test_plain_email_is_normalized(self):
        """User@Example.com (with whitespace) -> user@example.com."""
        assert canonicalize_email(" User@Example.com ") == "user@example.com"

    def test_value_without_domain_is_only_normalized(self):
        """Us.Er+tag (no domain) -> us.er+tag, no "@" appended."""
        assert canonicalize_email(" Us.Er+tag ") == "us.er+tag"

    def test_subaddress_is_dropped_on_any_domain(self):
        """user+tag@example.com -> user@example.com."""
        assert canonicalize_email("user+tag@example.com") == "user@example.com"

    def test_dots_are_dropped_on_dot_insensitive_domain(self):
        """us.er@gmail.com -> user@gmail.com."""
        assert canonicalize_email("us.er@gmail.com") == "user@gmail.com"

    def test_dots_are_kept_on_other_domains(self):
        """us.er@example.com stays us.er@example.com."""
        assert canonicalize_email("us.er@example.com") == "us.er@example.com"

    def test_dots_and_subaddress_together(self):
        """Us.Er+tag@Gmail.com -> user@gmail.com."""
        assert canonicalize_email("Us.Er+tag@Gmail.com") == "user@gmail.com"

    def test_only_subaddress_local_part_is_kept(self):
        """+tag@example.com stays +tag@example.com (no base to keep)."""
        assert canonicalize_email("+tag@example.com") == "+tag@example.com"

    def test_dot_insensitive_disabled(self):
        """us.er@gmail.com stays us.er@gmail.com."""
        assert (
            canonicalize_email("us.er@gmail.com", dot_insensitive=False)
            == "us.er@gmail.com"
        )

    def test_subaddress_insensitive_disabled(self):
        """user+tag@example.com stays user+tag@example.com."""
        assert (
            canonicalize_email("user+tag@example.com", subaddress_insensitive=False)
            == "user+tag@example.com"
        )
