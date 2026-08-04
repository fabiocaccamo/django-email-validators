# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0](https://github.com/fabiocaccamo/django-email-validators/releases/tag/0.7.0) - 2026-08-04
-   Add opt-in `check_mx` argument to `email_is_disposable` and `validate_email_non_disposable`: also check the domain MX hostnames (and their domain suffixes) against the disposable providers blocklists, catching fresh facade domains not yet blocklisted (e.g. `kjkpc.net` -> MX `prd-smtp.10minutemail.com` -> `10minutemail.com`).
-   Add `get_mx_hosts` helper with in-process per-domain cache, so multiple validators checking the same domain cost a single DNS lookup.
-   Refactor `validate_email_mx` and `validate_email_provider_typo` to use the shared (cached) `get_mx_hosts` helper. MX-based checks now fail open on DNS infrastructure errors (e.g. timeouts): valid emails are no longer at risk of rejection when the resolver is unavailable. Domains without MX records but with A/AAAA records (implicit MX, RFC 5321) are now considered not deliverable.
-   Replace the `email-validator` dependency with a direct `dnspython` dependency.
-   Bump test requirements, `pre-commit` hooks and GitHub Actions.

## [0.6.0](https://github.com/fabiocaccamo/django-email-validators/releases/tag/0.6.0) - 2026-08-04
-   Add generic `get_queryset_by_email` and `get_object_by_email` lookup helpers (work with any model / queryset).
-   Refactor `get_user_queryset_by_email` and `get_user_object_by_email` as thin wrappers around the generic helpers.

## [0.5.0](https://github.com/fabiocaccamo/django-email-validators/releases/tag/0.5.0) - 2026-07-30
-   Add `get_user_queryset_by_email` and `get_user_object_by_email` lookup helpers (same matching rules as `validate_email_unique`).
-   Refactor `validate_email_unique` to delegate the lookup to `get_user_queryset_by_email`.

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
