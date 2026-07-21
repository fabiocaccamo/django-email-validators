"""
Tests for the validate_email_unique_subaddress_insensitive function.
Uses a real SQLite in-memory database and Django auth.User model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django_email_validators.validators import (
    validate_email_unique_subaddress_insensitive,
)


@pytest.mark.django_db
class TestValidateEmailUniqueSubaddressInsensitive:
    """Test validate_email_unique_subaddress_insensitive against a real SQLite DB."""

    def test_raises_when_subaddress_variant_exists(self):
        """user+tag@example.com with user@example.com existing raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        with pytest.raises(ValidationError):
            validate_email_unique_subaddress_insensitive("user+tag@example.com")

    def test_raises_when_base_of_existing_subaddress(self):
        """user@example.com with user+tag@example.com existing raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user+tag@example.com")
        with pytest.raises(ValidationError):
            validate_email_unique_subaddress_insensitive("user@example.com")

    def test_dots_are_significant_even_on_gmail(self):
        """Dots are significant (dot_insensitive=False), even on gmail.com."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@gmail.com")
        validate_email_unique_subaddress_insensitive("us.er@gmail.com")

    def test_passes_when_no_duplicate(self):
        """user+tag@example.com with no existing user passes."""
        validate_email_unique_subaddress_insensitive("user+tag@example.com")

    def test_passes_on_update_with_exclude_pk(self):
        """On update, the current user is excluded so no false positive."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@example.com")
        validate_email_unique_subaddress_insensitive(
            "user+tag@example.com", exclude_pk=user.pk
        )

    def test_custom_error_message(self):
        """Custom error message is raised when a duplicate is found."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_unique_subaddress_insensitive(
                "user+tag@example.com", message="Custom error"
            )
