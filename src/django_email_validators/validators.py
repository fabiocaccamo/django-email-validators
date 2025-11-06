from disposable_email_domains import blocklist
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as validate_email_syntax
from django.utils.translation import gettext_lazy as _

# https://pypi.org/project/email-validator/
from email_validator import (
    EmailNotValidError,
)
from email_validator import (
    validate_email as validate_email_deliverability,
)

# https://github.com/FGRibreau/mailchecker
from MailChecker import MailChecker

from django_email_validators.providers import COMMON_PROVIDERS
from django_email_validators.utils import levenshtein_distance

__all__ = [
    "email_is_disposable",
    "validate_email_mx",
    "validate_email_non_disposable",
    "validate_email_provider_typo",
    "ValidationError",
]


def email_is_disposable(email):
    """
    Check if email is from a disposable email provider.

    Returns True if disposable, False otherwise.
    """
    domain = email.partition("@")[2].lower()

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
    validate_email_syntax(value)

    if email_is_disposable(value):
        error_message = message or _("Disposable emails are not allowed.")
        raise ValidationError(error_message)


def validate_email_mx(value, message=None):
    """
    Validate email syntax and check if the domain has valid MX records.

    Raises ValidationError if validation fails.

    Note: This performs a network request and may be slow.
    """
    validate_email_syntax(value)

    try:
        # check using https://pypi.org/project/email-validator/
        validate_email_deliverability(value, check_deliverability=True)
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
    validate_email_syntax(value)

    username, domain = value.split("@")
    domain = domain.lower()

    # check if domain is exactly 1 character different from a known provider
    for provider in COMMON_PROVIDERS:
        if levenshtein_distance(domain, provider) == 1:
            # found a potential typo, verify by checking MX records
            try:
                validate_email_deliverability(value, check_deliverability=True)
                # MX records exist, so it's a valid domain (not a typo)
                return
            except EmailNotValidError as error:
                # no valid MX records, this is likely a typo
                suggested_email = f"{username}@{provider}"
                error_message = message or _(f"Did you mean {suggested_email}?")
                raise ValidationError(error_message) from error
