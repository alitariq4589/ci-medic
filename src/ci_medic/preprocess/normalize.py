import re

TIMESTAMP_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b")
HEX_RE = re.compile(r"\b0x[0-9a-fA-F]+\b")
UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
RUN_PATH_RE = re.compile(r"/runs/\d+/")


def normalize(text: str) -> str:
    """Replace timestamps, hex addresses, UUIDs, and run-id paths with placeholders."""
    text = TIMESTAMP_RE.sub("<TS>", text)
    text = HEX_RE.sub("<HEX>", text)
    text = UUID_RE.sub("<UUID>", text)
    text = RUN_PATH_RE.sub("/runs/<RUN>/", text)
    return text
