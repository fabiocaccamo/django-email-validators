"""
Tests for package metadata.
"""

import re


class TestMetadata:
    """Test package metadata and version."""

    def test_metadata(self):
        """Test that all metadata fields exist and are strings."""
        from django_email_validators.metadata import (
            __author__,
            __copyright__,
            __description__,
            __email__,
            __license__,
            __title__,
            __version__,
        )

        assert isinstance(__author__, str)
        assert isinstance(__copyright__, str)
        assert isinstance(__description__, str)
        assert isinstance(__email__, str)
        assert isinstance(__license__, str)
        assert isinstance(__title__, str)
        assert isinstance(__version__, str)

    def test_version(self):
        """Test that version follows semantic versioning format."""
        from django_email_validators.metadata import __version__

        v = __version__
        v_re = re.compile(r"^([0-9]+)(\.([0-9]+)){1,2}$")
        v_match = v_re.match(v)
        assert v_match is not None
