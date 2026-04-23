from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def canonicalize_url(url: str) -> str:
    """Normalize URL for deduplication: strip tracking params, lower host."""
    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    # Drop common tracking query params
    drop = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "gclid",
        "fbclid",
    }
    q = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() not in drop]
    query = urlencode(q)
    path = parsed.path or "/"
    return urlunparse((parsed.scheme.lower(), host, path, "", query, ""))
