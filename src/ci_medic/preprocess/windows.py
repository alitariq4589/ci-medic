# src/ci_medic/preprocess/windows.py
import re
from dataclasses import dataclass

SIGNALS = [re.compile(p, re.I) for p in [
    r'\bFAILED\b', r'\berror\b[:\s\[]', r'error\[E\d+\]',
    r'Traceback \(most recent', r'panic:', r'Segmentation fault',
    r'npm ERR!', r'exit code [1-9]', r'OOMKilled', r'No such file',
    r'undefined reference', r'AssertionError', r'##\[error\]',
    r'FATAL', r'ModuleNotFoundError', r'Cannot find module',
    r'killed', r'timed? ?out', r'connection refused',
]]

@dataclass
class Window:
    start: int; end: int; score: int; text: str = ''

def extract_windows(lines: list[str], context: int = 15,
                    budget: int = 12000) -> list[Window]:
    hits = []
    for i, ln in enumerate(lines):
        s = sum(1 for rx in SIGNALS if rx.search(ln))
        if s: hits.append((i, s))
    if not hits and len(lines) > 0:
        hits = [(len(lines) - 1, 1)]          # nothing matched: tail only

    wins = [Window(max(0, i - context), min(len(lines)-1, i + context), s)
            for i, s in hits]
    wins.append(Window(max(0, len(lines)-40), len(lines)-1, 1))  # forced tail

    wins.sort(key=lambda w: w.start)           # merge overlapping
    merged = [wins[0]]
    for w in wins[1:]:
        if w.start <= merged[-1].end + 1:
            merged[-1].end = max(merged[-1].end, w.end)
            merged[-1].score += w.score
        else:
            merged.append(w)

    for w in merged:                            # rank by density, budget
        w.text = '\n'.join(lines[w.start:w.end+1])
    merged.sort(key=lambda w: w.score / (w.end - w.start + 1), reverse=True)
    kept, used = [], 0
    for w in merged:
        if used + len(w.text) <= budget:
            kept.append(w); used += len(w.text)
    kept.sort(key=lambda w: w.start)            # back to chronological
    return kept