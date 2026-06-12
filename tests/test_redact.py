from ci_medic.preprocess.redact import redact, shannon_entropy

FAKE_SECRETS = [
    "AKIAIOSFODNN7EXAMPLE",
    "ghp_1234567890abcdefghijklmnopqrstuvwx",
    "gho_abcdefghijklmnopqrstuvwxyz1234567890",
    "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123def456",
    "xK9mP2vLq8Rt4Nw7Yz3Bc6Df1Gh5Jk0",          # high-entropy random
    "postgres://admin:s3cr3tP4ssw0rd@db.host/x",
]

def test_known_formats_redacted():
    for s in FAKE_SECRETS:
        assert "<REDACTED>" in redact(f"token={s}"), f"missed: {s}"

def test_normal_text_survives():
    safe = "Building project configuration_path with verbose logging enabled"
    assert "<REDACTED>" not in redact(safe)

def test_entropy_threshold():
    assert shannon_entropy("aaaaaaaaaaaaaaaaaaaa") < 1.0
    assert shannon_entropy("xK9mP2vLq8Rt4Nw7Yz3B") > 4.0