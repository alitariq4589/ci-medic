import re
ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]|\x1b\][^\x07]*\x07')
GH_TS = re.compile(r'^\d{4}-\d{2}-\d{2}T[\d:.]+Z ', re.M)  # Actions prefixes every line
def strip(text: str) -> str:
    return GH_TS.sub('', ANSI.sub('', text))