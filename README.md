# ci-medic

**AI triage for failed CI runs.** When your pipeline goes red, ci-medic reads the logs, finds the real error in the noise, and posts an AI-based verdict — **code**, **flake**, **infra**, **dependency**, or **config** — right where you already look.

Secrets are redacted before any model sees them. Point it at a local model and your logs never leave your network.

> Not a button you click to "explain this error". `ci-medic` runs automatically on failure, distills thousands of noisy log lines to the real error, redacts secrets, and posts a structured verdict on CI systems where single hosted AI assistant doesn't reach.

## Supported CI platforms

- [x] **GitHub Actions**: sticky editable PR comment, zero setup
- [x] **Jenkins**: build description (requires one-time setup on your agent; native plugin on the roadmap)
- [ ] **GitLab CI**: planned
- [ ] **Bitbucket Pipelines**: planned

Any other CI can use the [CLI](#cli--local-use) against a log file today.

---

## Installation

### GitHub Actions

Add a triage job that runs only on failure:

```yaml
# .github/workflows/ci.yml
  triage:
    if: failure()
    needs: [build, test]          # the jobs to triage
    runs-on: ubuntu-latest
    permissions:
      actions: read               # read failed job logs
      pull-requests: write        # post the comment
    steps:
      - uses: alitariq4589/ci-medic@v0.1.0
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }} 
          api-key: ${{ secrets.CI_MEDIC_API_KEY }}   # optional (see Model providers)
```

`github-token` uses the built-in token in the pipeline automatically. Without `api-key`, ci-medic still posts the extracted error window, just without the AI verdict. The comment is sticky and re-runs update it in place.

Full walkthrough with screenshots: [docs/github-actions.md](docs/github-actions.md)

### Jenkins

Jenkins has no marketplace that provisions tools into pipelines, so setup has two roles: an **admin** makes `ci-medic` available on the agent once, then **pipeline authors** add a small block. (A native Jenkins plugin that removes the admin step is on the roadmap.)

**1. Admin setup: make ci-medic available on your agent (one-time).** Any one of:

- Install it on the agent environment: `pip install git+https://github.com/alitariq4589/ci-medic`
- Or, if you run Docker-based agents, add it to your agent image.

Provide the model key to the agent as the `CI_MEDIC_API_KEY` environment variable (or a Jenkins credential injected into the stage).

**2. Pipeline author setup: add the triage block.** Tee build output to a file, then triage it on failure:

```groovy
post {
  failure {
    script {
      def verdict = sh(
        script: 'ci-medic jenkins --file ci-medic-console.log --job "$JOB_NAME"',
        returnStdout: true
      ).trim()
      currentBuild.description = verdict
    }
  }
}
```

where your build stage writes the log:

```groovy
sh '''#!/bin/bash
  set -o pipefail
  { ./your-build-and-test; } 2>&1 | tee ci-medic-console.log
'''
```

`set -o pipefail` keeps the stage failing on error (so the `failure` block fires); the verdict lands at the top of the build page. No Jenkins API token and no script-approval needed because ci-medic only reads a file.

→ Full walkthrough with screenshots: [docs/jenkins.md](docs/jenkins.md)

### CLI / local use

Run ci-medic on any log file (no CI integration required):

```bash
pip install git+https://github.com/alitariq4589/ci-medic

# Distill only: No key, nothing leaves your machine:
ci-medic analyze --file failed.log --no-llm

# Full AI-based triage:
export CI_MEDIC_API_KEY="your-key" # can be openrouter, anthropic, openai API token
ci-medic analyze --file failed.log
```

---

## Model providers

ci-medic works with any OpenAI-compatible API or the Anthropic API. Set the provider via environment variables or `.ci-medic.yml`:

- **OpenRouter**: one key, many models (this is default as it includes free models too. The default openrouter selected models are in `src/ci_medic/config.py`) - Tested
- **OpenAI** - Untested
- **Anthropic** - Untested
- **Ollama**: local, zero egress - Untested
- **llama.cpp** (`llama-server`): local, zero egress - Untested
- Any other OpenAI-compatible endpoint

```bash
export CI_MEDIC_API_KEY="your-key"
export CI_MEDIC_BASE_URL="https://openrouter.ai/api/v1"   # provider endpoint
export CI_MEDIC_MODEL="your-model"                         # provider's model id
```

You choose the model; ci-medic doesn't lock you to one. With no model specified, it tries a priority chain and falls through on rate-limit or no-credit, recording which it used.

---

## Private mode (local model)

ci-medic's code is open source (Apache-2.0) — on GitHub you reference the public action, and you're free to fork or vendor it. What "private" controls is your **data**: where your logs go.

Point ci-medic at a local model server and **no log content ever leaves your network**:

```bash
export CI_MEDIC_BASE_URL="http://localhost:11434/v1"   # Ollama (or llama.cpp's llama-server)
export CI_MEDIC_MODEL="your-local-model"
# set no cloud key
```

The distillation and secret-redaction steps always run locally regardless of provider; only the distilled, redacted window is ever sent to a model, and with a local model, even that stays on your machine.

---

## Privacy & security

Before any model call, ci-medic redacts known secret formats and runs an entropy filter for high-randomness strings in unknown formats. (See [docs/redaction.md](docs/redaction.md) for the exact patterns covered.) For zero egress, use a local model and set no cloud key.

---

## Advanced configuration

Optional `.ci-medic.yml` in your repo root (see `examples/.ci-medic.yml`):

```yaml
provider: openai-compat                       # or: anthropic
base_url: https://openrouter.ai/api/v1
char_budget: 12000
ignore_jobs: ["lint", "codeql"]               # skip these jobs
extra_signals: ["MY_CUSTOM_ERROR_TOKEN"]      # extra strings to treat as errors
```

Environment variables override the file.

---

## Roadmap

- [x] GitHub Actions and Jenkins (CLI-based) ship in v0.1. 

- [ ] **Jenkins plugin** (install from the Update Center, no agent setup), 

- [ ] **GitLab CI**

- [ ] **flaky-test memory** that tracks chronic flakes across runs

- [ ] **hardware/LAVA** log triage.

## License

Apache-2.0