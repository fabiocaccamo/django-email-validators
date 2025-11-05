"""
Tests for package imports.
"""


class TestPackageImports:
    """Test that main package exports are available."""

    def test_package_imports(self):
        """Test that all public functions and classes can be imported."""
        from django_validate_email_strict import (
            email_is_disposable,
            validate_email_mx,
            validate_email_non_disposable,
        )

        assert email_is_disposable is not None
        assert validate_email_mx is not None
        assert validate_email_non_disposable is not None
