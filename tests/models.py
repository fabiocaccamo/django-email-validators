from django.db import models


class Subscriber(models.Model):
    """
    Non-user test model with a custom email field name,
    used to test the generic lookup helpers.
    """

    email_address = models.EmailField()

    class Meta:
        app_label = "tests"
