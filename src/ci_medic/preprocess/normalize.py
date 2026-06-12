SUBS = [
    (re.compile(r'\d{4}-\d{2}-\d{2}[T ][\d:.,]+Z?'), '<TS>'),
    (re.compile(r'0x[0-9a-fA-F]{6,}'), '<ADDR>'),
    (re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<UUID>'),
    (re.compile(r'/home/runner/work/\S+'), '<WS>'),
    (re.compile(r'\b\d+(\.\d+)?(ms|s)\b'), '<DUR>'),
    (re.compile(r'\b(job|run|build)[-_ ]?\d{4,}\b', re.I), '<RUNID>'),
]
def normalize(text: str) -> str:
    for rx, rep in SUBS: text = rx.sub(rep, text)
    return text