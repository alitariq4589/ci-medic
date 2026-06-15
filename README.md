# ci-medic

**AI triage for failed CI runs.** When your pipeline goes red, ci-medic reads the
logs, finds the actual error, and tells you *why* it failed — code bug, flaky test,
infra problem, dependency, or config — as a comment on your PR.

Works with any CI. Self-hostable. Your logs never leave your runner unless you
choose a cloud model — and ci-medic redacts secrets before any model sees them.

```yaml
# add to the end of your workflow
  triage:
    if: failure()
    needs: [build, test]
    runs-on: ubuntu-latest
    permissions: { actions: read, pull-requests: write }
    steps:
      - uses: alitariq4589/ci-medic@v0.1.0
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          api-key: ${{ secrets.OPENROUTER_KEY }}   # optional
```

## Why ci-medic

- **Vendor-agnostic.** GitHub Actions today; Jenkins and GitLab next. Not locked
  to one CI provider.
- **Private by default.** A deterministic pipeline strips, deduplicates, and
  **redacts secrets** from your logs *before* any LLM call. Run a local model
  (Ollama / llama.cpp) and nothing leaves your network at all.
- **Useful with zero config.** No API key? ci-medic still extracts and posts the
  real error window, just without the AI verdict.
- **Cheap.** Logs are distilled to ~150 lines before the model sees them, so a
  typical analysis costs a fraction of a cent — or nothing on free models.

## What it does

1. Triggers on workflow failure.
2. Pulls the failed jobs' logs via the GitHub API.
3. Deterministically distills them: strip ANSI, drop timestamps, collapse repeats,
   **redact secrets**, extract the highest-signal error windows.
4. Sends only that distilled evidence to a model for a structured verdict.
5. Posts a sticky PR comment + job summary:

> **ci-medic: flake (82%)**
> Root cause: test_upload timed out waiting on a network mock that never
> resolved. Non-deterministic; unrelated to the diff.
> Suggested fix: add a timeout+retry to the mock, or mark the test flaky.
> Retry recommended: yes

## Local / CLI usage

You can run ci-medic directly on a log file, without GitHub — useful for trying it
out or for self-hosted pipelines.

```bash
pip install ci-medic     # or: pip install -e . from a clone

# Distill only — no API key needed, nothing leaves your machine:
ci-medic analyze --file path/to/failed.log --no-llm

# Full triage with an AI verdict:
export CI_MEDIC_API_KEY="your-key"
export CI_MEDIC_BASE_URL="https://openrouter.ai/api/v1"   # any OpenAI-compatible endpoint
export CI_MEDIC_MODEL="anthropic/claude-3.5-haiku"        # or a local Ollama / llama.cpp model
ci-medic analyze --file path/to/failed.log
```

For a fully local, zero-egress setup, point `CI_MEDIC_BASE_URL` at a local model
server (Ollama at `http://localhost:11434/v1`, or llama.cpp's `llama-server`).

## Configuration

Optional `.ci-medic.yml` in your repo root:

```yaml
provider: openai-compat        # or: anthropic
model: anthropic/claude-3.5-haiku
base_url: https://openrouter.ai/api/v1
char_budget: 12000
ignore_jobs: ["lint", "codeql"]
extra_signals: ["MY_CUSTOM_ERROR_TOKEN"]
```

## Privacy & security

ci-medic redacts known secret formats (AWS keys, GitHub tokens, JWTs, private
keys, bearer tokens, credentials-in-URLs) **and** runs an entropy filter that
catches high-randomness strings even in unknown formats — before any model call.
For zero data egress, point it at a local model.

## Status

v0.1 — GitHub Actions. Roadmap: Jenkins (v0.2), GitLab CI (v0.3), flaky-test
memory (v0.4), hardware/LAVA log triage (v0.5).

## License

Apache-2.0