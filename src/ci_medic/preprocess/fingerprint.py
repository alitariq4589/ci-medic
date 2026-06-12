import hashlib


def fingerprint(text: str) -> str:
    """Create a 12-character SHA256 fingerprint from the normalized top error lines."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return digest[:12]
