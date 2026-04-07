__all__ = [
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
