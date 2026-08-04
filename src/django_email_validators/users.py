"""
Lookup helpers that retrieve users by email address, using the same
matching rules as the uniqueness validators (case-insensitive, optionally
dot-insensitive and subaddress-insensitive).

Unlike the validators, these functions never raise ValidationError:
they return the matching queryset / object.
"""

from django.contrib.auth import get_user_model

from django_email_validators.objects import (
    get_object_by_email,
    get_queryset_by_email,
)

__all__ = [
    "get_user_object_by_email",
    "get_user_queryset_by_email",
]


def get_user_queryset_by_email(
    value,
    field="email",
    exclude_pk=None,
    dot_insensitive=True,
    subaddress_insensitive=True,
    queryset=None,
):
    """
    Return the queryset of users whose email maps to the same inbox as the
    given email address, using the same matching rules as
    validate_email_unique.

    Accepts the same arguments as get_queryset_by_email, except that
    queryset is optional (default: all users).

    Returns a queryset (0..N records). Does not raise ValidationError for
    missing matches; raises ValueError if the field does not exist.
    """
    if queryset is None:
        queryset = get_user_model().objects.all()

    return get_queryset_by_email(
        value,
        queryset,
        field=field,
        exclude_pk=exclude_pk,
        dot_insensitive=dot_insensitive,
        subaddress_insensitive=subaddress_insensitive,
    )


def get_user_object_by_email(
    value,
    field="email",
    exclude_pk=None,
    dot_insensitive=True,
    subaddress_insensitive=True,
    queryset=None,
):
    """
    Return the first user whose email maps to the same inbox as the given
    email address, or None if there is no match.

    Accepts the same arguments as get_user_queryset_by_email.

    Unlike Manager.get, this never raises for missing matches:
    it returns None.
    """
    if queryset is None:
        queryset = get_user_model().objects.all()

    return get_object_by_email(
        value,
        queryset,
        field=field,
        exclude_pk=exclude_pk,
        dot_insensitive=dot_insensitive,
        subaddress_insensitive=subaddress_insensitive,
    )
