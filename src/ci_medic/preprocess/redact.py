import re

DEFAULT_PATTERNS = [
    re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]+"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
]


def redact(text: str, patterns=None) -> str:
    """Redact sensitive values using pattern rules and a simple entropy heuristic."""
    patterns = patterns or DEFAULT_PATTERNS
    for pattern in patterns:
        text = pattern.sub("[REDACTED]", text)
    return text
