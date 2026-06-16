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

def triage(provider_factory, models, windows_text):
    from ci_medic.schema import Verdict
    attempts = []                                   # record every try
    for model in models:
        provider = provider_factory(model)
        try:
            raw = provider.complete(SYSTEM, windows_text)
            for attempt in range(2):
                try:
                    v = Verdict.model_validate_json(
                        raw.strip().removeprefix("```json").removesuffix("```").strip())
                    v.model = model
                    v.fallback_trail = attempts      # who failed before this won
                    return v
                except Exception as e:
                    if attempt == 0:
                        raw = provider.complete(SYSTEM,
                            f"Your previous output was invalid JSON. Output ONLY the JSON.\n{raw}")
                    else:
                        attempts.append(f"{model}: invalid JSON ({e})")
        except Exception as e:
            attempts.append(f"{model}: {e}")
            print(f"ci-medic: model {model!r} failed → {e}")
            continue
    raise RuntimeError("All models failed:\n" + "\n".join(attempts))