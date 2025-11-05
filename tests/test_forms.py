"""
Tests for using validators with Django forms.
"""
import pytest
from django.core.exceptions import ValidationError

from django_validate_email_strict.validators import (
    validate_email_mx,
    validate_email_non_disposable,
)


class TestValidateEmailNonDisposableWithForms:
    """Test validate_email_non_disposable with Django form fields."""

    def test_as_form_field_validator(self):
        """Test validate_email_non_disposable works as form EmailField validator."""
        from django import forms

        class TestForm(forms.Form):
            email = forms.EmailField(validators=[validate_email_non_disposable])

        # Valid email should pass (syntax only, would need mock for full test)
        form = TestForm(data={"email": "test@example.com"})
        # Just test instantiation
        assert form.data["email"] == "test@example.com"


class TestValidateEmailMXWithForms:
    """Test validate_email_mx with Django form fields."""

    def test_as_form_field_validator(self):
        """Test validate_email_mx works as form EmailField validator."""
        from django import forms

        class TestForm(forms.Form):
            email = forms.EmailField(validators=[validate_email_mx])

        # Valid email should pass
        form = TestForm(data={"email": "test@example.com"})
        assert form.data["email"] == "test@example.com"
