# https://github.com/disposable/disposable-email-domains/

# https://github.com/disposable-email-domains/disposable-email-domains
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

__all__ = [
    "email_is_disposable",
    "validate_email_mx",
    "validate_email_non_disposable",
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
    
    Args:
        value: Email address to validate
        message: Optional custom error message
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
    
    Args:
        value: Email address to validate
        message: Optional custom error message
    """
    validate_email_syntax(value)
    
    try:
        # check using https://pypi.org/project/email-validator/
        validate_email_deliverability(value, check_deliverability=True)
    except EmailNotValidError as error:
        error_message = message or _("Email domain is not deliverable.")
        raise ValidationError(error_message) from error
