from functools import lru_cache

import dns.exception
import dns.resolver

__all__ = [
    "get_domain_suffixes",
    "get_mx_hosts",
]


def get_domain_suffixes(hostname):
    """
    Return the progressive domain suffixes of a hostname, from the full
    hostname down to the 2-label suffix (never the bare TLD), e.g.
    "prd-smtp.10minutemail.com" -> ["prd-smtp.10minutemail.com", "10minutemail.com"].
    """
    labels = hostname.split(".")
    return [".".join(labels[index:]) for index in range(len(labels) - 1)]


@lru_cache(maxsize=512)
def _resolve_mx_hosts(domain):
    """
    Resolve the MX records for the domain.

    Returns an empty list on an authoritative negative answer (the domain
    does not exist or has no MX records); raises DNSException on
    infrastructure errors (timeout, no nameservers available), which are
    intentionally not cached (lru_cache does not cache exceptions), so
    transient failures don't stick.
    """
    try:
        answers = dns.resolver.resolve(domain, "MX")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return []
    hosts = [str(answer.exchange).rstrip(".").lower() for answer in answers]
    return [host for host in hosts if host]


def get_mx_hosts(domain):
    """
    Return the list of MX hostnames for the domain (lowercased, no
    trailing dot), an empty list when the domain authoritatively has no
    MX records, or None when the lookup could not be performed
    (e.g. DNS timeout), so callers can fail open.

    Results are cached in-process (per domain), so multiple validators
    checking the same domain cost a single DNS lookup.
    """
    try:
        return _resolve_mx_hosts(domain)
    except dns.exception.DNSException:
        return None
