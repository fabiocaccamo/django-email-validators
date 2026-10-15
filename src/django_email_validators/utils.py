from django_email_validators.providers import DOT_INSENSITIVE_DOMAINS

__all__ = [
    "canonicalize_email",
    "levenshtein_distance",
    "normalize_email",
    "split_email",
]


def levenshtein_distance(s1, s2):
    """
    Calculate Levenshtein distance between two strings.
    Returns the minimum number of single-character edits needed.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for s1_index, s1_char in enumerate(s1):
        current_row = [s1_index + 1]
        for s2_index, s2_char in enumerate(s2):
            insertions = previous_row[s2_index + 1] + 1
            deletions = current_row[s2_index] + 1
            substitutions = previous_row[s2_index] + (s1_char != s2_char)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def normalize_email(email):
    """
    Normalize email by stripping whitespace and lowercasing.
    """
    return email.strip().lower()


def split_email(email):
    """
    Split a pre-normalized email address into local part and domain.
    Expects the email to already be stripped and lowercased (e.g. via normalize_email).
    Returns a tuple (local, domain).
    """
    local, _, domain = email.partition("@")
    return local, domain


def canonicalize_email(email, dot_insensitive=True, subaddress_insensitive=True):
    """
    Return the canonical form of an email address: every address that maps
    to the same inbox (same matching rules as validate_email_unique) gets
    the same canonical form, e.g. "Us.Er+tag@gmail.com" -> "user@gmail.com".

    The email is normalized, then the subaddress ("+tag") is dropped when
    subaddress_insensitive (unless the local part is only a subaddress),
    and the dots of the local part are dropped when dot_insensitive and
    the domain is dot-insensitive (DOT_INSENSITIVE_DOMAINS).
    Useful to key per-inbox data, e.g. rate limits.
    A value without domain is returned normalized only.
    """
    email = normalize_email(email)
    local, domain = split_email(email)
    if not domain:
        return email
    if subaddress_insensitive:
        local_base = local.split("+", 1)[0]
        if local_base:
            local = local_base
    if dot_insensitive and domain in DOT_INSENSITIVE_DOMAINS:
        local = local.replace(".", "")
    return f"{local}@{domain}"
