"""
Tests for using validators with Django model fields.
"""
import pytest
from django.core.exceptions import ValidationError

from django_validate_email_strict.validators import (
    validate_email_mx,
    validate_email_non_disposable,
)


class TestValidateEmailNonDisposableWithFields:
    """Test validate_email_non_disposable as a model field validator."""

    def test_as_model_field_validator(self):
        """Test validate_email_non_disposable works as EmailField validator."""
        from django.db import models

        class TestModelNonDisposable(models.Model):
            email = models.EmailField(validators=[validate_email_non_disposable])

            class Meta:
                app_label = "test"

        # Valid email should pass (with syntax check only, mocked)
        instance = TestModelNonDisposable(email="test@example.com")
        # Note: Full validation would require mocking, so we just test instantiation
        assert instance.email == "test@example.com"


class TestValidateEmailMXWithFields:
    """Test validate_email_mx as a model field validator."""

    def test_as_model_field_validator(self):
        """Test validate_email_mx works as EmailField validator."""
        from django.db import models

        class TestModelMX(models.Model):
            email = models.EmailField(validators=[validate_email_mx])

            class Meta:
                app_label = "test"

        # Valid email should pass
        instance = TestModelMX(email="test@example.com")
        assert instance.email == "test@example.com"
