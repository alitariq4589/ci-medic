# src/ci_medic/preprocess/redact.py
import math, re
from collections import Counter

PATTERNS = [re.compile(p) for p in [
    r'AKIA[A-Z0-9]{16}',                      # AWS access key
    r'gh[pousr]_[A-Za-z0-9]{20,}',            # GitHub tokens
    r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',  # JWT
    r'-----BEGIN [A-Z ]*KEY-----[\s\S]+?-----END [A-Z ]*KEY-----',
    r'://[^/\s:]+:[^@\s]+@',                  # creds in URL
    r'(?i)bearer\s+[A-Za-z0-9._\-]{16,}',
]]
TOKEN_RE = re.compile(r'\S{20,}')

def shannon_entropy(s: str) -> float:
    n = len(s); counts = Counter(s)
    return -sum((c/n) * math.log2(c/n) for c in counts.values())

def redact(text: str, threshold: float = 4.0) -> str:
    for rx in PATTERNS:
        text = rx.sub('<REDACTED>', text)
    def _ent(m):
        tok = m.group(0)
        if tok.count('/') >= 3 or tok.startswith(('http://', 'https://')):
            return tok                          # paths/URLs: low risk, high value
        return '<REDACTED>' if shannon_entropy(tok) > threshold else tok
    return TOKEN_RE.sub(_ent, text)