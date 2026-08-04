"""
Tests for the generic get_queryset_by_email and get_object_by_email
lookup helpers, using a non-user model with a custom email field name.
"""

import pytest
from django.core.exceptions import ValidationError

from django_email_validators.objects import (
    get_object_by_email,
    get_queryset_by_email,
)
from tests.models import Subscriber


@pytest.mark.django_db
class TestGetQuerysetByEmail:
    """Test get_queryset_by_email on a non-user model
    with a custom email field."""

    def test_exact_match(self):
        """user@example.com matches the subscriber with the same email."""
        subscriber = Subscriber.objects.create(email_address="user@example.com")
        qs = get_queryset_by_email(
            "user@example.com", Subscriber.objects.all(), field="email_address"
        )
        assert list(qs) == [subscriber]

    def test_dot_variant_on_dot_insensitive_domain(self):
        """us.er@gmail.com matches user@gmail.com."""
        subscriber = Subscriber.objects.create(email_address="user@gmail.com")
        qs = get_queryset_by_email(
            "us.er@gmail.com", Subscriber.objects.all(), field="email_address"
        )
        assert list(qs) == [subscriber]

    def test_subaddress_variant_on_any_domain(self):
        """user+tag@example.com matches user@example.com."""
        subscriber = Subscriber.objects.create(email_address="user@example.com")
        qs = get_queryset_by_email(
            "user+tag@example.com", Subscriber.objects.all(), field="email_address"
        )
        assert list(qs) == [subscriber]

    def test_no_match_returns_empty_queryset(self):
        """other@example.com does not match user@example.com."""
        Subscriber.objects.create(email_address="user@example.com")
        qs = get_queryset_by_email(
            "other@example.com", Subscriber.objects.all(), field="email_address"
        )
        assert not qs.exists()

    def test_exclude_pk(self):
        """exclude_pk excludes the given object from the results."""
        subscriber = Subscriber.objects.create(email_address="user@example.com")
        qs = get_queryset_by_email(
            "user@example.com",
            Subscriber.objects.all(),
            field="email_address",
            exclude_pk=subscriber.pk,
        )
        assert not qs.exists()

    def test_invalid_field_raises_value_error(self):
        """A non-existent field raises ValueError."""
        with pytest.raises(ValueError):
            get_queryset_by_email(
                "user@example.com", Subscriber.objects.all(), field="invalid_field"
            )

    def test_invalid_email_raises_validation_error(self):
        """An invalid email raises ValidationError (syntax check)."""
        with pytest.raises(ValidationError):
            get_queryset_by_email(
                "not-an-email", Subscriber.objects.all(), field="email_address"
            )

    def test_custom_queryset_is_respected(self):
        """The base queryset restricts the results."""
        subscriber = Subscriber.objects.create(email_address="user@example.com")
        Subscriber.objects.create(email_address="user+tag@example.com")
        qs = get_queryset_by_email(
            "user@example.com",
            Subscriber.objects.filter(pk=subscriber.pk),
            field="email_address",
        )
        assert list(qs) == [subscriber]


@pytest.mark.django_db
class TestGetObjectByEmail:
    """Test get_object_by_email on a non-user model."""

    def test_returns_object_on_match(self):
        """Returns the matching record."""
        subscriber = Subscriber.objects.create(email_address="user@gmail.com")
        obj = get_object_by_email(
            "us.er+tag@gmail.com", Subscriber.objects.all(), field="email_address"
        )
        assert obj == subscriber

    def test_returns_none_on_no_match(self):
        """Returns None (does not raise) when there is no match."""
        obj = get_object_by_email(
            "user@example.com", Subscriber.objects.all(), field="email_address"
        )
        assert obj is None

    def test_exclude_pk(self):
        """exclude_pk excludes the given object."""
        subscriber = Subscriber.objects.create(email_address="user@example.com")
        obj = get_object_by_email(
            "user@example.com",
            Subscriber.objects.all(),
            field="email_address",
            exclude_pk=subscriber.pk,
        )
        assert obj is None
