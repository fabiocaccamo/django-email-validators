from django.core.exceptions import ValidationError
from django.core.validators import validate_email as validate_email_syntax
from django.utils.translation import gettext_lazy as _

# https://github.com/disposable/disposable-email-domains/
from disposable import domains

# https://github.com/disposable-email-domains/disposable-email-domains
from disposable_email_domains import blocklist

# https://pypi.org/project/email-validator/
from email_validator import (
    validate_email as validate_email_deliverability,
    EmailNotValidError,
)

# https://github.com/FGRibreau/mailchecker
from mailchecker import MailChecker

__all__ = [
    "DeliverableEmailValidator",
    "email_is_disposable",
    "NonDisposableEmailValidator",
    "validate_email",
    "ValidationError",
]


def email_is_disposable(email):
    domain = email.partition("@")[2].lower()
    domains = []

    # check using https://github.com/disposable/disposable-email-domains/
    if domain in domains:
        return True

    # check using https://github.com/disposable-email-domains/disposable-email-domains
    if domain in blocklist:
        return True

    # check using https://github.com/FGRibreau/mailchecker
    if not MailChecker.is_valid(email):
        return True

    # good, email is not disposable
    return False


class NonDisposableEmailValidator:
    """
    Raises ValidationError if email is from a known disposable provider.
    """

    def __init__(self, message=None):
        self.message = message or _("Disposable emails are not allowed.")

    def __call__(self, value):
        if email_is_disposable(value):
            raise ValidationError(self.message)


class DeliverableEmailValidator:
    """
    Raises ValidationError if email domain is not deliverable (MX check).
    """

    def __init__(self, message=None):
        self.message = message or _("Email domain is not deliverable.")

    def __call__(self, value):
        try:
            # check using https://pypi.org/project/email-validator/
            validate_email_deliverability(value, check_deliverability=True)
        except EmailNotValidError:
            raise ValidationError(self.message)


def validate_email(value, check_disposable=True, check_deliverability=True):
    """
    Run Django syntax validation, then optional disposable and MX checks.
    """

    validate_email_syntax(value)

    if check_disposable:
        NonDisposableEmailValidator()(value)

    if check_deliverability:
        DeliverableEmailValidator()(value)
