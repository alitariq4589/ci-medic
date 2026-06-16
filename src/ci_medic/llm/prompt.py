SYSTEM = """You are ci-medic, a CI failure triage engine. You receive pre-extracted \
error windows from a failed CI log. Respond with ONLY a JSON object, no markdown fences:
{"category":"code|flake|infra|dependency|config","confidence":0.0-1.0,
"root_cause":"1 short paragraph","evidence":["verbatim log lines"],
"suggested_fix":"concrete next action","retry_recommended":true|false}

Definitions:
- code: the change itself broke build/tests (deterministic, caused by the diff)
- flake: non-deterministic (timeout, race, network blip); likely passes on retry
- infra: runner/platform problem (runner died, disk full, docker pull fail, OOM)
- dependency: external package/registry/version resolution failure
- config: workflow/build config error (bad yaml, missing secret, wrong path)
If evidence is ambiguous, pick the most probable category and lower confidence."""

def triage(provider_factory, models: list[str], windows_text: str):
    """Try each model in priority order; return first valid Verdict."""
    from ci_medic.schema import Verdict
    last_err = None
    for model in models:
        provider = provider_factory(model)   # build a provider bound to this model
        try:
            raw = provider.complete(SYSTEM, windows_text)
            for attempt in range(2):
                try:
                    return Verdict.model_validate_json(
                        raw.strip().removeprefix("```json").removesuffix("```").strip())
                except Exception:
                    if attempt == 0:
                        raw = provider.complete(
                            SYSTEM,
                            f"Your previous output was invalid JSON. Output ONLY the JSON.\n{raw}")
                    else:
                        raise
        except Exception as e:
            last_err = e
            print(f"ci-medic: model {model!r} failed ({type(e).__name__}), trying next…")
            continue
    raise RuntimeError(f"All models failed. Last error: {last_err}")