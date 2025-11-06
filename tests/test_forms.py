"""
Tests for using validators with Django forms.
"""

from django_email_validators.validators import (
    validate_email_mx,
    validate_email_non_disposable,
)


class TestFormFieldIntegration:
    """Test that validators can be used with Django form fields."""

    def test_validators_can_be_assigned_to_form_fields(self):
        """Test that validators can be assigned to form EmailField."""
        from django import forms

        class TestForm(forms.Form):
            email1 = forms.EmailField(validators=[validate_email_non_disposable])
            email2 = forms.EmailField(validators=[validate_email_mx])

        # Just verify the form can be created with our validators
        form = TestForm()
        assert form.fields["email1"].validators
        assert form.fields["email2"].validators
