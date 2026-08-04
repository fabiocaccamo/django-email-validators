"""
Tests for package imports.
"""


class TestPackageImports:
    """Test that main package exports are available."""

    def test_package_imports(self):
        """Test that all public functions and classes can be imported."""
        from django_email_validators import (
            email_is_disposable,
            get_object_by_email,
            get_queryset_by_email,
            get_user_object_by_email,
            get_user_queryset_by_email,
            validate_email_mx,
            validate_email_non_disposable,
            validate_email_provider_typo,
            validate_email_unique,
            validate_email_unique_dot_insensitive,
            validate_email_unique_subaddress_insensitive,
        )

        assert email_is_disposable is not None
        assert get_object_by_email is not None
        assert get_queryset_by_email is not None
        assert get_user_object_by_email is not None
        assert get_user_queryset_by_email is not None
        assert validate_email_mx is not None
        assert validate_email_non_disposable is not None
        assert validate_email_provider_typo is not None
        assert validate_email_unique is not None
        assert validate_email_unique_dot_insensitive is not None
        assert validate_email_unique_subaddress_insensitive is not None
