"""
Tests for the get_user_queryset_by_email and get_user_object_by_email
lookup helpers.
Uses a real SQLite in-memory database and Django auth.User model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django_email_validators.users import (
    get_user_object_by_email,
    get_user_queryset_by_email,
)
from django_email_validators.validators import validate_email_unique


@pytest.mark.django_db
class TestGetUserQuerysetByEmail:
    """Test get_user_queryset_by_email with default options
    (dot_insensitive=True, subaddress_insensitive=True)."""

    def test_exact_match(self):
        """user@example.com matches the user with the same email."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@example.com")
        qs = get_user_queryset_by_email("user@example.com")
        assert list(qs) == [user]

    def test_case_insensitive_match(self):
        """User@Example.com matches user@example.com."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@example.com")
        qs = get_user_queryset_by_email("User@Example.com")
        assert list(qs) == [user]

    def test_dot_variant_on_dot_insensitive_domain(self):
        """us.er@gmail.com matches user@gmail.com."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@gmail.com")
        qs = get_user_queryset_by_email("us.er@gmail.com")
        assert list(qs) == [user]

    def test_subaddress_variant(self):
        """user+tag@example.com matches user@example.com."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@example.com")
        qs = get_user_queryset_by_email("user+tag@example.com")
        assert list(qs) == [user]

    def test_combined_dots_and_subaddress_on_gmail(self):
        """us.er+tag@gmail.com matches user@gmail.com."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@gmail.com")
        qs = get_user_queryset_by_email("us.er+tag@gmail.com")
        assert list(qs) == [user]

    def test_no_match_returns_empty_queryset(self):
        """other@example.com does not match user@example.com."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        qs = get_user_queryset_by_email("other@example.com")
        assert not qs.exists()

    def test_dots_are_significant_on_non_dot_insensitive_domain(self):
        """us.er@example.com does not match user@example.com."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        qs = get_user_queryset_by_email("us.er@example.com")
        assert not qs.exists()

    def test_multiple_matches(self):
        """All matching users are returned."""
        User = get_user_model()
        user1 = User.objects.create_user(username="user1", email="user@example.com")
        user2 = User.objects.create_user(username="user2", email="user+tag@example.com")
        qs = get_user_queryset_by_email("user@example.com")
        assert set(qs) == {user1, user2}

    def test_exclude_pk(self):
        """exclude_pk excludes the given user from the results."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@example.com")
        qs = get_user_queryset_by_email("user@example.com", exclude_pk=user.pk)
        assert not qs.exists()

    def test_invalid_field_raises_value_error(self):
        """A non-existent field raises ValueError."""
        with pytest.raises(ValueError):
            get_user_queryset_by_email("user@example.com", field="invalid_field")

    def test_invalid_email_raises_validation_error(self):
        """An invalid email raises ValidationError (syntax check)."""
        with pytest.raises(ValidationError):
            get_user_queryset_by_email("not-an-email")

    def test_custom_queryset_is_respected(self):
        """A custom base queryset restricts the results."""
        User = get_user_model()
        user1 = User.objects.create_user(username="user1", email="user@example.com")
        user2 = User.objects.create_user(username="user2", email="user+tag@example.com")
        user2.is_active = False
        user2.save()
        qs = get_user_queryset_by_email(
            "user@example.com", queryset=User.objects.filter(is_active=True)
        )
        assert list(qs) == [user1]


@pytest.mark.django_db
class TestGetUserQuerysetByEmailFlags:
    """Test get_user_queryset_by_email with individual flags disabled."""

    def test_subaddress_insensitive_false_plus_is_significant(self):
        """With subaddress_insensitive=False, user+tag does not match user."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        qs = get_user_queryset_by_email(
            "user+tag@example.com", subaddress_insensitive=False
        )
        assert not qs.exists()

    def test_dot_insensitive_false_dots_are_significant_on_gmail(self):
        """With dot_insensitive=False, us.er@gmail.com does not match
        user@gmail.com."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@gmail.com")
        qs = get_user_queryset_by_email("us.er@gmail.com", dot_insensitive=False)
        assert not qs.exists()

    def test_both_flags_false_plain_case_insensitive_match(self):
        """With both flags disabled, User@Example.com matches
        user@example.com."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@example.com")
        qs = get_user_queryset_by_email(
            "User@Example.com",
            dot_insensitive=False,
            subaddress_insensitive=False,
        )
        assert list(qs) == [user]


@pytest.mark.django_db
class TestGetUserObjectByEmail:
    """Test get_user_object_by_email."""

    def test_returns_user_on_match(self):
        """Returns the matching user record."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@gmail.com")
        assert get_user_object_by_email("us.er+tag@gmail.com") == user

    def test_returns_none_on_no_match(self):
        """Returns None (does not raise) when there is no match."""
        assert get_user_object_by_email("user@example.com") is None

    def test_exclude_pk(self):
        """exclude_pk excludes the given user."""
        User = get_user_model()
        user = User.objects.create_user(username="user1", email="user@example.com")
        assert get_user_object_by_email("user@example.com", exclude_pk=user.pk) is None


@pytest.mark.django_db
class TestLookupValidatorEquivalence:
    """The validator flags a duplicate if and only if the lookup
    returns at least one record (shared pattern helper)."""

    emails = [
        "user@example.com",
        "User@Example.com",
        "user+tag@example.com",
        "user+a@example.com",
        "us.er@example.com",
        "us.er+tag@example.com",
        "user@gmail.com",
        "us.er@gmail.com",
        "user+tag@gmail.com",
        "us.er+tag@gmail.com",
        "other@example.com",
        "+tag@example.com",
    ]

    flags = [
        {"dot_insensitive": True, "subaddress_insensitive": True},
        {"dot_insensitive": True, "subaddress_insensitive": False},
        {"dot_insensitive": False, "subaddress_insensitive": True},
        {"dot_insensitive": False, "subaddress_insensitive": False},
    ]

    def test_equivalence(self):
        """For every input/flags combination, validator and lookup agree."""
        User = get_user_model()
        User.objects.create_user(username="user1", email="user@example.com")
        User.objects.create_user(username="user2", email="user@gmail.com")
        User.objects.create_user(username="user3", email="user+b@example.com")

        for email in self.emails:
            for flags in self.flags:
                validator_flags_duplicate = False
                try:
                    validate_email_unique(email, **flags)
                except ValidationError:
                    validator_flags_duplicate = True
                lookup_has_match = get_user_queryset_by_email(email, **flags).exists()
                assert validator_flags_duplicate == lookup_has_match, (
                    f"validator/lookup mismatch for {email!r} with {flags!r}"
                )
