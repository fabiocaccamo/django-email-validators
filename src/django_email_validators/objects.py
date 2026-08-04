"""
Generic lookup helpers that retrieve objects by email address, using the
same matching rules as the uniqueness validators (case-insensitive,
optionally dot-insensitive and subaddress-insensitive).

Unlike the validators, these functions never raise ValidationError:
they return the matching queryset / object.
"""

import re

from django.core.exceptions import FieldError
from django.core.validators import validate_email as validate_email_syntax

from django_email_validators.providers import DOT_INSENSITIVE_DOMAINS
from django_email_validators.utils import normalize_email, split_email

__all__ = [
    "get_object_by_email",
    "get_queryset_by_email",
]


def _build_email_match_pattern(email, dot_insensitive, subaddress_insensitive):
    """
    Build a regex pattern matching all the email addresses that map to the
    same inbox as the given (pre-normalized) email address.

    The pattern is anchored and meant to be used with a case-insensitive
    match (the "iregex" queryset lookup).
    """
    local, domain = split_email(email)

    subaddress_regex = ""
    if subaddress_insensitive:
        local_base = local.split("+", 1)[0]
        if local_base:
            local = local_base
        subaddress_regex = r"(\+[^@]*)?"

    if dot_insensitive and domain in DOT_INSENSITIVE_DOMAINS:
        local_stripped = local.replace(".", "")
        local_regex = r"\.?".join(re.escape(char) for char in local_stripped)
    else:
        local_regex = re.escape(local)

    return rf"^{local_regex}{subaddress_regex}@{re.escape(domain)}$"


def get_queryset_by_email(
    value,
    queryset,
    field="email",
    exclude_pk=None,
    dot_insensitive=True,
    subaddress_insensitive=True,
):
    """
    Return the queryset of objects whose email maps to the same inbox as
    the given email address, using the same matching rules as
    validate_email_unique.

    Options:
    - queryset: the base queryset to filter (required).
    - field: the model field name to match against (default: "email").
    - exclude_pk: exclude the object with this pk (e.g. the current object).
    - dot_insensitive: on dot-insensitive providers (e.g. Gmail) dots in the
      local part are ignored when comparing.
    - subaddress_insensitive: the "+tag" subaddress (RFC 5233) is ignored
      when comparing, on any domain.

    Returns a queryset (0..N records). Does not raise ValidationError for
    missing matches; raises ValueError if the field does not exist.
    """
    email = normalize_email(value)
    validate_email_syntax(email)

    pattern = _build_email_match_pattern(
        email,
        dot_insensitive=dot_insensitive,
        subaddress_insensitive=subaddress_insensitive,
    )

    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)

    model_name = queryset.model.__name__
    try:
        return queryset.filter(**{f"{field}__iregex": pattern})
    except FieldError as exc:
        raise ValueError(f"field '{field}' not found on {model_name}.") from exc


def get_object_by_email(
    value,
    queryset,
    field="email",
    exclude_pk=None,
    dot_insensitive=True,
    subaddress_insensitive=True,
):
    """
    Return the first object whose email maps to the same inbox as the given
    email address, or None if there is no match.

    Accepts the same arguments as get_queryset_by_email.

    Unlike Manager.get, this never raises for missing matches:
    it returns None.
    """
    return get_queryset_by_email(
        value,
        queryset,
        field=field,
        exclude_pk=exclude_pk,
        dot_insensitive=dot_insensitive,
        subaddress_insensitive=subaddress_insensitive,
    ).first()
