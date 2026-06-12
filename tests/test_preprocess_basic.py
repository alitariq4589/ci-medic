from ci_medic.preprocess.ansi import strip_ansi
from ci_medic.preprocess.normalize import normalize


def test_strip_ansi_removes_escape_codes():
    assert strip_ansi("\x1b[31mERROR\x1b[0m") == "ERROR"


def test_normalize_replaces_common_tokens():
    text = "2024-06-12T10:11:12Z failed at 0x1A2B and run /runs/42/abc"
    assert normalize(text) == "<TS> failed at <HEX> and run /runs/<RUN>/abc"
