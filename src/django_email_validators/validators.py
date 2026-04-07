import re

from disposable_email_domains import blocklist
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldError, ValidationError
from django.core.validators import validate_email as validate_email_syntax
from django.utils.translation import gettext_lazy as _

# https://pypi.org/project/email-validator/
from email_validator import EmailNotValidError
from email_validator import validate_email as validate_email_deliverability

# https://github.com/FGRibreau/mailchecker
from MailChecker import MailChecker

from django_email_validators.providers import COMMON_PROVIDERS, DOT_INSENSITIVE_DOMAINS
from django_email_validators.utils import (
    levenshtein_distance,
    normalize_email,
    split_email,
)

__all__ = [
    "email_is_disposable",
    "validate_email_mx",
    "validate_email_non_disposable",
    "validate_email_provider_typo",
    "validate_email_unique_dot_insensitive",
]


def email_is_disposable(email):
    """
    Check if email is from a disposable email provider.

    Returns True if disposable, False otherwise.
    """
    email = normalize_email(email)
    _, domain = split_email(email)

    # check using https://github.com/disposable-email-domains/disposable-email-domains
    if domain in blocklist:
        return True

    # check using https://github.com/FGRibreau/mailchecker
    if not MailChecker.is_valid(email):
        return True

    # good, email is not disposable
    return False


def validate_email_non_disposable(value, message=None):
    """
    Validate email syntax and check if it's from a disposable provider.

    Raises ValidationError if validation fails.
    """
    email = normalize_email(value)
    validate_email_syntax(email)

    if email_is_disposable(email):
        error_message = message or _("Disposable emails are not allowed.")
        raise ValidationError(error_message)


def validate_email_mx(value, message=None):
    """
    Validate email syntax and check if the domain has valid MX records.

    Raises ValidationError if validation fails.

    Note: This performs a network request and may be slow.
    """
    email = normalize_email(value)
    validate_email_syntax(email)

    try:
        # check using https://pypi.org/project/email-validator/
        validate_email_deliverability(email, check_deliverability=True)
    except EmailNotValidError as error:
        error_message = message or _("Email domain is not deliverable.")
        raise ValidationError(error_message) from error


def validate_email_provider_typo(value, message=None):
    """
    Validate that email domain isn't likely a typo of a common provider.
    Checks if domain is 1 character different from known providers AND
    has no valid MX records (indicating it's likely a typo).

    Raises ValidationError if domain appears to be a typo.

    Note: In case of potential typo, this performs
    a network request to check MX records, so it may be slow.

    Examples that fail:
    - user@gmai.com (should be gmail.com)
    - user@yahooo.com (should be yahoo.com)
    """
    email = normalize_email(value)
    validate_email_syntax(email)
    local, domain = split_email(email)

    # check if domain is exactly 1 character different from a known provider
    for provider in COMMON_PROVIDERS:
        if levenshtein_distance(domain, provider) == 1:
            # found a potential typo, verify by checking MX records
            try:
                validate_email_deliverability(email, check_deliverability=True)
                # MX records exist, so it's a valid domain (not a typo)
                return
            except EmailNotValidError as error:
                # no valid MX records, this is likely a typo
                suggested_email = f"{local}@{provider}"
                error_message = message or _("Did you mean %(email)s?") % {
                    "email": suggested_email
                }
                raise ValidationError(error_message) from error


def validate_email_unique_dot_insensitive(
    value, exclude_pk=None, field="email", message=None
):
    """
    Validate email uniqueness accounting for dot-insensitive email providers
    (e.g. Gmail treats dots in the local part as insignificant, so
    fabio.caccamo@gmail.com and fabiocaccamo@gmail.com are the same inbox).

    Raises ValidationError if a duplicate is found.

    Usage:
        # signup
        validate_email_unique_dot_insensitive("fabio.caccamo@gmail.com")

        # update (exclude current user)
        validate_email_unique_dot_insensitive(
            "fabio.caccamo@gmail.com", exclude_pk=instance.pk
        )
    """
    email = normalize_email(value)
    validate_email_syntax(email)

    local, domain = split_email(email)

    if domain not in DOT_INSENSITIVE_DOMAINS:
        return

    local_stripped = local.replace(".", "")
    local_regex = r"\.?".join(re.escape(char) for char in local_stripped)
    pattern = rf"^{local_regex}@{re.escape(domain)}$"

    User = get_user_model()
    qs = User.objects.all()

    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)

    try:
        duplicate_exists = qs.filter(**{f"{field}__iregex": pattern}).exists()
    except FieldError as exc:
        raise ValueError(
            f"validate_email_unique_dot_insensitive: "
            f"field '{field}' not found on {User.__name__}."
        ) from exc

    if duplicate_exists:
        error_message = message or _("A user with this email address already exists.")
        raise ValidationError(error_message)
