from collections import Counter


def collapse_repeats(lines: list[str], threshold: int = 2) -> list[str]:
    """Collapse repeated adjacent lines into a single '(repeated ×N)' marker."""
    result = []
    counts = Counter(lines)
    for line in lines:
        count = counts[line]
        if count >= threshold:
            if not result or result[-1] != f"{line} (repeated ×{count})":
                result.append(f"{line} (repeated ×{count})")
        else:
            result.append(line)
    return result
