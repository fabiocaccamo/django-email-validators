"""
Tests for the validate_email_unique function.
Uses a real SQLite in-memory database and Django auth.User model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django_email_validators.validators import validate_email_unique


@pytest.mark.django_db
class TestValidateEmailUniqueDefaults:
    """Test validate_email_unique with default options
    (dot_insensitive=True, subaddress_insensitive=True)."""

    def test_raises_when_subaddress_variant_exists(self):
        """user+tag@example.com with user@example.com existing raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        with pytest.raises(ValidationError):
            validate_email_unique("user+tag@example.com")

    def test_raises_when_base_of_existing_subaddress(self):
        """user@example.com with user+tag@example.com existing raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user+tag@example.com")
        with pytest.raises(ValidationError):
            validate_email_unique("user@example.com")

    def test_raises_when_different_subaddress_exists(self):
        """user+a@example.com with user+b@example.com existing raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user+b@example.com")
        with pytest.raises(ValidationError):
            validate_email_unique("user+a@example.com")

    def test_raises_combined_dots_and_subaddress_on_gmail(self):
        """us.er+tag@gmail.com with user@gmail.com existing raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique("us.er+tag@gmail.com")

    def test_passes_dots_on_non_dot_insensitive_domain(self):
        """us.er+tag@example.com with user@example.com existing passes
        (dots are significant on non-dot-insensitive domains)."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        validate_email_unique("us.er+tag@example.com")

    def test_case_insensitive_input(self):
        """User+Tag@Example.com with user@example.com existing raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        with pytest.raises(ValidationError):
            validate_email_unique("User+Tag@Example.com")

    def test_passes_when_no_duplicate(self):
        """user+tag@example.com with no existing user passes."""
        validate_email_unique("user+tag@example.com")

    def test_empty_base_local_part_does_not_crash(self):
        """+tag@example.com (empty base) keeps the original local part."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="+tag@example.com")
        with pytest.raises(ValidationError):
            validate_email_unique("+tag@example.com")

    def test_empty_base_local_part_does_not_match_other_locals(self):
        """+tag@example.com does not match user@example.com."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        validate_email_unique("+tag@example.com")


@pytest.mark.django_db
class TestValidateEmailUniqueFlags:
    """Test validate_email_unique with individual flags disabled."""

    def test_subaddress_insensitive_false_ignores_plus(self):
        """With subaddress_insensitive=False, user+tag does not match user."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        validate_email_unique("user+tag@example.com", subaddress_insensitive=False)

    def test_subaddress_insensitive_false_dot_variant_on_gmail_raises(self):
        """With subaddress_insensitive=False, gmail dot-variants still match."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@gmail.com")
        with pytest.raises(ValidationError):
            validate_email_unique("us.er@gmail.com", subaddress_insensitive=False)

    def test_dot_insensitive_false_dots_are_significant_on_gmail(self):
        """With dot_insensitive=False, us.er@gmail.com vs user@gmail.com passes."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@gmail.com")
        validate_email_unique("us.er@gmail.com", dot_insensitive=False)

    def test_dot_insensitive_false_subaddress_still_matches(self):
        """With dot_insensitive=False, user+tag@x.com vs user@x.com raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@x.com")
        with pytest.raises(ValidationError):
            validate_email_unique("user+tag@x.com", dot_insensitive=False)

    def test_both_flags_false_plain_case_insensitive_check(self):
        """With both flags disabled, User@Example.com vs user@example.com raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        with pytest.raises(ValidationError):
            validate_email_unique(
                "User@Example.com",
                dot_insensitive=False,
                subaddress_insensitive=False,
            )

    def test_both_flags_false_different_emails_pass(self):
        """With both flags disabled, different emails pass."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        validate_email_unique(
            "user+tag@example.com",
            dot_insensitive=False,
            subaddress_insensitive=False,
        )


@pytest.mark.django_db
class TestValidateEmailUniqueInfrastructure:
    """Test validate_email_unique infrastructure options."""

    def test_passes_on_update_with_exclude_pk(self):
        """On update, the current user is excluded so no false positive."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@example.com")
        validate_email_unique("user+tag@example.com", exclude_pk=user.pk)

    def test_raises_on_update_when_other_duplicate_exists(self):
        """On update, a different user with a matching variant still raises."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        user2 = User.objects.create_user(username="user2", email="other@example.com")
        with pytest.raises(ValidationError):
            validate_email_unique("user+tag@example.com", exclude_pk=user2.pk)

    def test_invalid_field_raises_value_error(self):
        """A field name that does not exist on the User model raises ValueError."""
        with pytest.raises(ValueError, match="field 'nonexistent_field' not found"):
            validate_email_unique("user@example.com", field="nonexistent_field")

    def test_custom_error_message(self):
        """Custom error message is raised when a duplicate is found."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        with pytest.raises(ValidationError, match="Custom error"):
            validate_email_unique("user+tag@example.com", message="Custom error")

    def test_invalid_email_syntax(self):
        """Invalid email syntax raises ValidationError before any DB query."""
        with pytest.raises(ValidationError):
            validate_email_unique("invalid-email")

    def test_extended_dot_insensitive_domains_setting(self):
        """EMAIL_VALIDATORS_EXTEND_DOT_INSENSITIVE_DOMAINS is respected."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@dotless.test")
        with pytest.raises(ValidationError):
            validate_email_unique("us.er@dotless.test")
