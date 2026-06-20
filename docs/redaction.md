# Redaction & secret handling

ci-medic redacts secrets from logs **before** any model call. Distillation and
redaction run locally regardless of which model provider you use, so even with a
cloud model only the distilled, redacted window is ever transmitted. With a
local model, nothing leaves your machine at all.

## What gets redacted

> **⚠️ FILL THIS IN FROM `src/ci_medic/preprocess/redact.py` — DO NOT PUBLISH CLAIMS YOU HAVE NOT VERIFIED.**
>
> List ONLY the secret formats your `redact.py` actually has patterns for. For
> each one, confirm the pattern exists in the code before listing it here.
>
> Verified so far (proven in GitHub + Jenkins runs):
> - **AWS access keys** (e.g. `AKIA…`) — confirmed redacted in posted output
>
> Candidates to verify against redact.py before adding (remove any that aren't
> actually implemented):
> - GitHub tokens (`ghp_…`, `gho_…`, etc.)
> - JWTs (`eyJ…` three-part dot-separated)
> - Private keys (`-----BEGIN … PRIVATE KEY-----` blocks)
> - Bearer tokens (`Authorization: Bearer …`)
> - Credentials embedded in URLs (`https://user:pass@…`)
> - Generic high-entropy strings (entropy filter) — only list if the filter
>   actually exists in code
>
> Delete this whole callout block once the list below is real.


ci-medic redacts the following before any model sees the log:

- **AWS access keys** — `AKIA`-prefixed identifiers
- **GitHub tokens** — `ghp_`, `gho_`, `ghs_`, `ghr_` prefixes
- **Credentials in URL**
- **JWTs**

A full list of these is present in [src/ci_medic/preprocess/redact.py](src/ci_medic/preprocess/redact.py).




## How to verify it yourself
 
Check any format directly against the redactor:
 
```bash
# Run this in the ci-medic project root after activating python venv and installing ci-medic
python3 -c "from ci_medic.preprocess.redact import redact; print(redact('YOUR_TEST_STRING'))"
```
 
If the secret comes back as `<REDACTED>`, it's covered; if it comes back
unchanged, it is not.
 
For an end-to-end check, put a dummy secret on the *failing* line of a build (so
it lands in the extracted error window) and confirm it appears redacted in the
posted verdict. `AKIAIOSFODNN7EXAMPLE` is AWS's public documentation key — safe
to use in tests because it is not a real credential.


## Design note

Redaction is intentionally a **local, deterministic preprocessing step**, not
something the model is trusted to do. The model never receives raw logs, so a
redaction miss is a bug to fix in `redact.py`, not a prompt to tune. If you find a
secret format that slips through, please open an issue with a sanitized example.