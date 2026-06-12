import hashlib
def fingerprint(window_texts: list[str]) -> str:
    sig = '\n'.join(window_texts)[:2000]        # normalized already
    return hashlib.sha256(sig.encode()).hexdigest()[:12]