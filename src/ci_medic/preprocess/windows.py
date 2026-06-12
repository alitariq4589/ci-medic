import re


DEFAULT_SIGNAL_RE = re.compile(r"(error|failed|Traceback|Exception|panic|EPIPE|ModuleNotFoundError)", re.I)


def extract_windows(text: str, signal_re: re.Pattern[str] | None = None, context_lines: int = 2, char_budget: int = 4000) -> str:
    """Scan for signal lines and return nearby windows limited by a character budget."""
    pattern = signal_re or DEFAULT_SIGNAL_RE
    lines = text.splitlines()
    windows = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            windows.append("\n".join(lines[start:end]))

    snippet = "\n\n".join(windows)
    if len(snippet) > char_budget:
        return snippet[:char_budget]
    return snippet
