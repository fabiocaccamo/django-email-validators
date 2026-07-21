# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0](https://github.com/fabiocaccamo/django-email-validators/releases/tag/0.4.0) - 2026-07-21
-   Add `validate_email_unique` validator with `dot_insensitive` and `subaddress_insensitive` options (plus-addressing / RFC 5233 support).
-   Add `validate_email_unique_subaddress_insensitive` shortcut validator.
-   Refactor `validate_email_unique_dot_insensitive` as a shortcut for `validate_email_unique`.
-   Bump requirements and `pre-commit` hooks.

## [0.3.0](https://github.com/fabiocaccamo/django-email-validators/releases/tag/0.3.0) - 2026-04-07
-   Add `validate_email_unique_dot_insensitive` validator.
-   Refactor validators tests.
-   Bump requirements and `pre-commit` hooks.

## [0.2.1](https://github.com/fabiocaccamo/django-email-validators/releases/tag/0.2.1) - 2026-01-03
-   Add possibility to extend common providers. (by [DmytroLitvinov](https://github.com/DmytroLitvinov) in #12)
-   Fix `makemessages` message extraction.
-   Update translations.
-   Add localization for Ukrainian. (by [DmytroLitvinov](https://github.com/DmytroLitvinov) in #11)

## [0.2.0](https://github.com/fabiocaccamo/django-email-validators/releases/tag/0.2.0) - 2025-12-17
-   Remove `django` from dependencies in `pyproject.toml`.

## [0.1.0](https://github.com/fabiocaccamo/django-email-validators/releases/tag/0.1.0) - 2025-11-06
-   Publish package.
