def dedupe(lines: list[str]) -> list[str]:
    out, prev, count = [], object(), 0
    for ln in lines + [object()]:               # sentinel flushes the last group
        if ln == prev: count += 1; continue
        if count > 1: out.append(f'  (repeated ×{count})')
        if isinstance(ln, str): out.append(ln)
        prev, count = ln, 1
    return out