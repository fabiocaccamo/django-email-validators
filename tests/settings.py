SECRET_KEY = "django-email-validators"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_email_validators",
    "tests",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_VALIDATORS_EXTEND_DOT_INSENSITIVE_DOMAINS = [
    "dotless.test",
]

USE_TZ = True
