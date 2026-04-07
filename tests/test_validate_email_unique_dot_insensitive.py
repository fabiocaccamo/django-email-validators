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

    def test_passes_on_non_dot_insensitive_domain(self, django_assert_num_queries):
        """Email on a non-dot-insensitive domain skips the DB check (no queries)."""
        with django_assert_num_queries(0):
            validate_email_unique_dot_insensitive("fabio.caccamo@example.com")

    def test_passes_when_no_duplicate(self):
        """gmail.com address with no existing user passes."""
        validate_email_unique_dot_insensitive("fabio.caccamo@gmail.com")

    def test_raises_when_dot_variant_exists(self):
        """Dot-variant of an existing gmail.com address raises ValidationError."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="fabiocaccamo@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("fabio.caccamo@gmail.com")

    def test_raises_exact_match(self):
        """Exact email already in DB raises ValidationError."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="fabio.caccamo@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("fabio.caccamo@gmail.com")

    def test_passes_on_update_with_exclude_pk(self):
        """On update, the current user is excluded so no false positive."""
        User = get_user_model()
        user = User.objects.create_user(
            username="user1", email="fabio.caccamo@gmail.com"
        )
        validate_email_unique_dot_insensitive(
            "fabio.caccamo@gmail.com", exclude_pk=user.pk
        )

    def test_raises_on_update_when_other_duplicate_exists(self):
        """On update, a different user with a dot-variant still raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="fabiocaccamo@gmail.com")
        user2 = User.objects.create_user(username="user2", email="other@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive(
                "fabio.caccamo@gmail.com", exclude_pk=user2.pk
            )

    def test_case_insensitive_input(self):
        """Uppercase input is normalised to lowercase before the DB check."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="fabiocaccamo@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("Fabio.Caccamo@Gmail.Com")

    def test_googlemail_domain(self):
        """googlemail.com is also a dot-insensitive domain."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="fabiocaccamo@googlemail.com")
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("fabio.caccamo@googlemail.com")

    def test_custom_error_message(self):
        """Custom error message is raised when a duplicate is found."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="fabiocaccamo@gmail.com")
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_unique_dot_insensitive(
                "fabio.caccamo@gmail.com", message="Custom error"
            )

    def test_invalid_email_syntax(self):
        """Invalid email syntax raises ValidationError before any DB query."""
        with pytest.raises(ValidationError):
            validate_email_unique_dot_insensitive("invalid-email")

    def test_invalid_field_raises_value_error(self):
        """A field name that does not exist on the User model raises ValueError."""
        with pytest.raises(ValueError, match="field 'nonexistent_field' not found"):
            validate_email_unique_dot_insensitive(
                "fabio.caccamo@gmail.com", field="nonexistent_field"
            )
