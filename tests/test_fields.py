"""
Tests for using validators with Django model fields.
"""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from django_email_validators.validators import (
    validate_email_mx,
    validate_email_non_disposable,
)


class TestModelFieldIntegration:
    """Test that validators can be used with Django model fields."""

    def test_validators_can_be_assigned_to_model_fields(self):
        """Test that validators can be assigned to EmailField."""
        from django.db import models

        class TestModel(models.Model):
            email1 = models.EmailField(validators=[validate_email_non_disposable])
            email2 = models.EmailField(validators=[validate_email_mx])

            class Meta:
                app_label = "test"

        # Just verify the model can be created with our validators
        assert TestModel._meta.get_field("email1").validators
        assert TestModel._meta.get_field("email2").validators

    @patch("django_email_validators.validators.email_is_disposable")
    def test_non_disposable_validator_raises_on_save(self, mock_is_disposable):
        """Test that non-disposable validator raises ValidationError on full_clean."""
        from django.db import models

        class TestModelNonDisposable(models.Model):
            email = models.EmailField(validators=[validate_email_non_disposable])

            class Meta:
                app_label = "test"

        mock_is_disposable.return_value = True
        instance = TestModelNonDisposable(email="test@disposable.com")

        with pytest.raises(ValidationError) as exc_info:
            instance.full_clean()

        assert "email" in exc_info.value.error_dict

    @patch("django_email_validators.validators.validate_email_deliverability")
    def test_mx_validator_raises_on_save(self, mock_deliverability):
        """Test that MX validator raises ValidationError on full_clean."""
        from django.db import models
        from email_validator import EmailNotValidError

        class TestModelMX(models.Model):
            email = models.EmailField(validators=[validate_email_mx])

            class Meta:
                app_label = "test"

        mock_deliverability.side_effect = EmailNotValidError("No MX records")
        instance = TestModelMX(email="test@invalid.com")

        with pytest.raises(ValidationError) as exc_info:
            instance.full_clean()

        assert "email" in exc_info.value.error_dict
