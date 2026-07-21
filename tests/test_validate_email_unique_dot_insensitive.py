"""
Tests for the validate_email_unique_dot_insensitive function.
Uses a real SQLite in-memory database and Django auth.User model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django_email_validators.validators import validate_email_unique_dot_insensitive


@pytest.mark.django_db
class TestValidateEmailUniqueDotInsensitive:
    """Test validate_email_unique_dot_insensitive against a real SQLite DB."""

    def test_passes_dot_variant_on_non_dot_insensitive_domain(self):
        """Dots are significant on non-dot-insensitive domains."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        validate_email_unique_dot_insensitive("us.er@example.com")

    def test_passes_subaddress_variant(self):
        """The shortcut does not strip the +tag subaddress."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        validate_email_unique_dot_insensitive("user+tag@example.com")

    def test_passes_when_no_duplicate(self):
        """gmail.com address with no existing user passes."""
        validate_email_unique_dot_insensitive("us.er@gmail.com")

    def test_raises_when_dot_variant_exists(self):
        """Dot-variant of an existing gmail.com address raises ValidationError."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("us.er@gmail.com")

    def test_raises_exact_match(self):
        """Exact email already in DB raises ValidationError."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="us.er@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("us.er@gmail.com")

    def test_passes_on_update_with_exclude_pk(self):
        """On update, the current user is excluded so no false positive."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="us.er@gmail.com")
        validate_email_unique_dot_insensitive("us.er@gmail.com", exclude_pk=user.pk)

    def test_raises_on_update_when_other_duplicate_exists(self):
        """On update, a different user with a dot-variant still raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@gmail.com")
        user2 = User.objects.create_user(username="user2", email="other@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive(
                "us.er@gmail.com", exclude_pk=user2.pk
            )

    def test_case_insensitive_input(self):
        """Uppercase input is normalised to lowercase before the DB check."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("Us.Er@Gmail.Com")

    def test_googlemail_domain(self):
        """googlemail.com is also a dot-insensitive domain."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@googlemail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("us.er@googlemail.com")

    def test_custom_error_message(self):
        """Custom error message is raised when a duplicate is found."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@gmail.com")
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_unique_dot_insensitive(
                "us.er@gmail.com", message="Custom error"
            )

    def test_invalid_email_syntax(self):
        """Invalid email syntax raises ValidationError before any DB query."""
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("invalid-email")

    def test_invalid_field_raises_value_error(self):
        """A field name that does not exist on the User model raises ValueError."""
        with pytest.raises(ValueError, match="field 'nonexistent_field' not found"):
            validate_email_unique_dot_insensitive(
                "us.er@gmail.com", field="nonexistent_field"
            )
