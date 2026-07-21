[![](https://img.shields.io/pypi/pyversions/django-email-validators.svg?color=3776AB&logo=python&logoColor=white)](https://www.python.org/)
[![](https://img.shields.io/pypi/djversions/django-email-validators?color=0C4B33&logo=django&logoColor=white&label=django)](https://www.djangoproject.com/)

[![](https://img.shields.io/pypi/v/django-email-validators.svg?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-email-validators/)
[![](https://static.pepy.tech/badge/django-email-validators/month)](https://pepy.tech/project/django-email-validators)
[![](https://img.shields.io/github/stars/fabiocaccamo/django-email-validators?logo=github&style=flat)](https://github.com/fabiocaccamo/django-email-validators/stargazers)
[![](https://img.shields.io/pypi/l/django-email-validators.svg?color=blue)](https://github.com/fabiocaccamo/django-email-validators/blob/main/LICENSE.txt)

[![](https://results.pre-commit.ci/badge/github/fabiocaccamo/django-email-validators/main.svg)](https://results.pre-commit.ci/latest/github/fabiocaccamo/django-email-validators/main)
[![](https://img.shields.io/github/actions/workflow/status/fabiocaccamo/django-email-validators/test-package.yml?branch=main&label=build&logo=github)](https://github.com/fabiocaccamo/django-email-validators)
[![](https://img.shields.io/codecov/c/gh/fabiocaccamo/django-email-validators?logo=codecov)](https://codecov.io/gh/fabiocaccamo/django-email-validators)
[![](https://img.shields.io/badge/code%20style-black-000000.svg?logo=python&logoColor=black)](https://github.com/psf/black)
[![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/fabiocaccamo/django-email-validators/badge)](https://securityscorecards.dev/viewer/?uri=github.com/fabiocaccamo/django-email-validators)

# django-email-validators
no more invalid or disposable emails in your database.

## Installation
-   Run `pip install django-email-validators`
-   Add `django_email_validators` to `settings.INSTALLED_APPS`
-   Restart your application server

## Usage

### Validators
- 🗑️ `validate_email_non_disposable`
- 🌐 `validate_email_mx`
- ✍️ `validate_email_provider_typo`
- 👤 `validate_email_unique`
    - ⚫ `validate_email_unique_dot_insensitive`
    - ➕ `validate_email_unique_subaddress_insensitive`

#### `validate_email_non_disposable`
Validates that the email is not from a disposable email provider *(fast, offline check)*.

#### `validate_email_mx`
Validates that the email domain has valid MX records *(slow, requires network access)*.

#### `validate_email_provider_typo`
Validates that the email domain is not a likely typo of a common email provider.
Checks a one-character diff against 80+ common providers and verifies the domain has no valid MX records (prevents false positives).

**Examples that will be caught:**
- `user@gmai.com` -> suggests `user@gmail.com`
- `user@gmail.co` -> suggests `user@gmail.com`
- `user@yahooo.com` -> suggests `user@yahoo.com`

#### `validate_email_unique`
Validates that the email is unique in the database, preventing multiple accounts that map to the same inbox:

- **`dot_insensitive`** (default: `True`): on dot-insensitive providers (e.g. Gmail) dots in the local part are ignored when comparing, so `us.er@gmail.com` and `user@gmail.com` are treated as the same inbox.
- **`subaddress_insensitive`** (default: `True`): the `+tag` subaddress ([RFC 5233](https://datatracker.ietf.org/doc/html/rfc5233)) is ignored when comparing, on any domain, so `user+tag@example.com` and `user@example.com` are treated as the same inbox. Emails with `+` remain valid and are stored as entered: only the uniqueness check changes.

With both options disabled it performs a plain case-insensitive uniqueness check.

Accepts an optional `exclude_pk` argument to exclude the current user when updating an existing account, and an optional `field` argument (default: `"email"`) to specify the model field name.

**Examples that will be caught:**
- `user@gmail.com` already exists → `us.er@gmail.com` is rejected
- `user@example.com` already exists → `user+tag@example.com` is rejected (and vice versa)
- `user@gmail.com` already exists → `us.er+tag@gmail.com` is rejected

Since this validator requires access to the model instance (to exclude it on update), it cannot be used directly in a field's `validators=[...]`. Call it explicitly in a form or serializer:

```python
from django_email_validators import validate_email_unique

# Form example
class UserForm(forms.ModelForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        validate_email_unique(
            email,
            exclude_pk=self.instance.pk,  # exclude the current user on update
            field="email",  # model field name (default: "email")
            message=None,  # custom error message (default: localized message)
            dot_insensitive=True,  # ignore dots on dot-insensitive providers
            subaddress_insensitive=True,  # ignore the "+tag" subaddress
        )
        return email
```

Or via `validate_unique` on the model:

```python
class User(models.Model):
    email = models.EmailField()

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        validate_email_unique(
            self.email,
            exclude_pk=self.pk,  # exclude the current instance on update
            field="email",  # model field name (default: "email")
            message=None,  # custom error message (default: localized message)
            dot_insensitive=True,  # ignore dots on dot-insensitive providers
            subaddress_insensitive=True,  # ignore the "+tag" subaddress
        )
```

#### `validate_email_unique_dot_insensitive`
Validates that the email is unique in the database, accounting only for dot-insensitive providers (e.g. Gmail treats dots in the local part as insignificant), while the `+tag` subaddress is significant.

Equivalent to `validate_email_unique(dot_insensitive=True, subaddress_insensitive=False)`, it accepts the same `exclude_pk`, `field` and `message` arguments.

**Examples that will be caught:**
- `user@gmail.com` already exists → `us.er@gmail.com` is rejected

**Examples that will pass:**
- `user@example.com` already exists → `us.er@example.com` passes (non dot-insensitive domain)
- `user@gmail.com` already exists → `user+tag@gmail.com` passes (subaddress is significant)

#### `validate_email_unique_subaddress_insensitive`
Validates that the email is unique in the database, ignoring only the `+tag` subaddress ([RFC 5233](https://datatracker.ietf.org/doc/html/rfc5233)), on any domain, while dots in the local part are always significant.

Equivalent to `validate_email_unique(dot_insensitive=False, subaddress_insensitive=True)`, it accepts the same `exclude_pk`, `field` and `message` arguments.

**Examples that will be caught:**
- `user@example.com` already exists → `user+tag@example.com` is rejected (and vice versa)

**Examples that will pass:**
- `user@gmail.com` already exists → `us.er@gmail.com` passes (dots are significant)

#### Usage

> **Note:** `validate_email_unique` requires access to the model instance and cannot be used in `validators=[...]`. See the [dedicated section above](#validate_email_unique) for usage examples.

```python
from django.db import models
from django_email_validators import (
    validate_email_non_disposable,
    validate_email_mx,
    validate_email_provider_typo,
)

class User(models.Model):
    email = models.EmailField(
        validators=[
            validate_email_non_disposable,
            validate_email_mx,
            validate_email_provider_typo,
        ]
    )
```

### Extending the providers list for typo check
You can extend the list of common email providers used by `validate_email_provider_typo` by adding your own list in Django settings:
```python
EMAIL_VALIDATORS_EXTEND_COMMON_PROVIDERS = [
    'hey.com',
]
```

### Extending the dot-insensitive domains list
You can extend the list of dot-insensitive domains used by `validate_email_unique` by adding your own list in Django settings:
```python
EMAIL_VALIDATORS_EXTEND_DOT_INSENSITIVE_DOMAINS = [
    'fastmail.com',
]
```

## Testing
```bash
# clone repository
git clone https://github.com/fabiocaccamo/django-email-validators.git && cd django-email-validators

# create virtualenv and activate it
python -m venv venv && . venv/bin/activate

# upgrade pip
python -m pip install --upgrade pip

# install requirements
pip install -r requirements.txt -r requirements-test.txt

# install pre-commit to run formatters and linters
pre-commit install --install-hooks

# run tests
tox
# or
pytest
```

## License
Released under [MIT License](LICENSE.txt).

---

## Supporting

- :star: Star this project on [GitHub](https://github.com/fabiocaccamo/django-email-validators)
- :octocat: Follow me on [GitHub](https://github.com/fabiocaccamo)
- :blue_heart: Follow me on [Bluesky](https://bsky.app/profile/fabiocaccamo.bsky.social)
- :moneybag: Sponsor me on [Github](https://github.com/sponsors/fabiocaccamo)

## See also

- [`django-admin-interface`](https://github.com/fabiocaccamo/django-admin-interface) - the default admin interface made customizable by the admin itself. popup windows replaced by modals. 🧙 ⚡

- [`django-cache-cleaner`](https://github.com/fabiocaccamo/django-cache-cleaner) - clear the entire cache or individual caches easily using the admin panel or management command. 🧹

- [`django-colorfield`](https://github.com/fabiocaccamo/django-colorfield) - simple color field for models with a nice color-picker in the admin. 🎨

- [`django-extra-settings`](https://github.com/fabiocaccamo/django-extra-settings) - config and manage typed extra settings using just the django admin. ⚙️

- [`django-maintenance-mode`](https://github.com/fabiocaccamo/django-maintenance-mode) - shows a 503 error page when maintenance-mode is on. 🚧 🛠️

- [`django-redirects`](https://github.com/fabiocaccamo/django-redirects) - redirects with full control. ↪️

- [`django-treenode`](https://github.com/fabiocaccamo/django-treenode) - probably the best abstract model / admin for your tree based stuff. 🌳

- [`python-benedict`](https://github.com/fabiocaccamo/python-benedict) - dict subclass with keylist/keypath support, I/O shortcuts (base64, csv, json, pickle, plist, query-string, toml, xml, yaml) and many utilities. 📘

- [`python-codicefiscale`](https://github.com/fabiocaccamo/python-codicefiscale) - encode/decode Italian fiscal codes - codifica/decodifica del Codice Fiscale. 🇮🇹 💳

- [`python-fontbro`](https://github.com/fabiocaccamo/python-fontbro) - friendly font operations. 🧢

- [`python-fsutil`](https://github.com/fabiocaccamo/python-fsutil) - file-system utilities for lazy devs. 🧟‍♂️
