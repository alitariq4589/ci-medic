# ci-medic

**AI triage for failed CI runs.** When your pipeline goes red, ci-medic reads the logs, finds the *actual* error in the noise, and posts a verdict — **code** bug, **flake**, **infra** problem, **dependency**, or **config** — right where you already look: a PR comment on GitHub, a build description on Jenkins.

Vendor-agnostic. Self-hostable. Secrets are redacted *before* any model sees them, and with a local model your logs never leave your network at all.

> ci-medic isn't "explain this error" behind a button you have to click. It runs automatically on failure, finds the real error across thousands of noisy lines, redacts secrets, and works on CI systems that hosted assistants can't touch — including self-hosted Jenkins.

---

## Supported CI platforms

| Platform | Status | Output target |
|---|---|---|
| GitHub Actions | ✅ v0.1 | Sticky PR comment + job summary |
| Jenkins | ✅ v0.1 | Build description |
| GitLab CI | ⬜ planned (v0.3) | MR note |
| Bitbucket Pipelines | ⬜ planned | — |

Anything not listed can still use the **CLI** (below) against a log file today.

---

## GitHub Actions

Add a triage job that runs only when something fails:

```yaml
# .github/workflows/ci.yml
  triage:
    if: failure()
    needs: [build, test]          # the jobs you want triaged
    runs-on: ubuntu-latest
    permissions:
      actions: read               # read the failed job logs
      pull-requests: write        # post the sticky comment
    steps:
      - uses: alitariq4589/ci-medic@v0.1.0
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          api-key: ${{ secrets.OPENROUTER_KEY }}   # optional; see "Models"
```

`github-token` uses the built-in `GITHUB_TOKEN` — no setup. Without `api-key`, ci-medic still posts the extracted error window, just without the AI verdict. The comment is **sticky**: re-runs update the same comment instead of spamming the PR.

---

## Jenkins

Jenkins needs ci-medic available on the agent and a small block in your pipeline. No Jenkins API token and no script-approval is required — ci-medic reads a log file the pipeline writes, so it stays inside the Groovy sandbox.

**1. Make ci-medic available on the agent.** Bake it into your Jenkins image:

```dockerfile
FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update && apt-get install -y python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --break-system-packages INSTALL_LINE
USER jenkins
```

Provide your model key as an environment variable when you run the controller (or set it as a Jenkins credential and inject it into the stage):

```bash
docker run -d --name jenkins -p 8080:8080 \
  -e CI_MEDIC_API_KEY="$CI_MEDIC_API_KEY" \
  your-jenkins-image
```

**2. Add the triage block to your `Jenkinsfile`.** Tee the build output to a file, then run ci-medic against it on failure and write the verdict to the build description:

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh '''#!/bin/bash
          set -o pipefail
          {
            ./your-build-and-test-commands-here
          } 2>&1 | tee ci-medic-console.log
        '''
      }
    }
  }
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
}
```

`set -o pipefail` (with the `#!/bin/bash` shebang) ensures the stage still fails when your command fails — `tee` would otherwise mask the exit code. The verdict appears at the top of the failed build's page.

---

## CLI / local use

Run ci-medic directly on any log file — no CI, no GitHub. Good for trying it out, for unsupported CI systems, or for a fully offline setup.

```bash
pip install INSTALL_LINE

# Distill only — no key needed, nothing leaves your machine:
ci-medic analyze --file path/to/failed.log --no-llm

# Full triage with an AI verdict:
export CI_MEDIC_API_KEY="your-key"
export CI_MEDIC_BASE_URL="https://openrouter.ai/api/v1"
ci-medic analyze --file path/to/failed.log
```

PULL_SH_BLOCK

---

## Self-hosting / fully local (zero egress)

ci-medic talks to any OpenAI-compatible endpoint, so you can keep logs entirely inside your network by pointing it at a local model server:

```bash
export CI_MEDIC_BASE_URL="http://localhost:11434/v1"   # Ollama
# or llama.cpp's llama-server, or any OpenAI-compatible server
export CI_MEDIC_MODEL="your-local-model"
ci-medic analyze --file failed.log
```

With a local model and no cloud key set, nothing about your logs ever leaves the machine. The distillation and redaction steps run locally regardless of which model you choose.

---

## Models

ci-medic uses any OpenAI-compatible API (OpenRouter, OpenAI, a local server) or the Anthropic API directly. Configure via environment or `.ci-medic.yml`.

When a key is set and no model is specified, ci-medic tries a priority chain and falls through on failure (rate-limit, no-credit), recording which models were tried:

```
1. anthropic/claude-3.5-haiku            (reliable default)
2. openai/gpt-4o-mini                     (reliable backup)
3. openai/gpt-oss-120b:free               (strong free)
4. qwen/qwen3-next-80b-a3b-instruct:free  (free)
5. meta-llama/llama-3.3-70b-instruct:free (free fallback)
```

> **Note:** free-tier models are rate-limited and shared; for reliable results, use a key with credit so the primary model answers first. Logs are distilled to a small window before the model sees them, so a typical analysis costs a fraction of a cent.

---

## Configuration

Optional `.ci-medic.yml` in your repo root (see `examples/.ci-medic.yml`):

```yaml
provider: openai-compat                       # or: anthropic
model: anthropic/claude-3.5-haiku
base_url: https://openrouter.ai/api/v1
char_budget: 12000
ignore_jobs: ["lint", "codeql"]               # skip these jobs
extra_signals: ["MY_CUSTOM_ERROR_TOKEN"]      # extra strings to treat as errors
```

Environment variables (`CI_MEDIC_API_KEY`, `CI_MEDIC_BASE_URL`, `CI_MEDIC_MODEL`) override the file.

---

## How it works

1. **Trigger** on failure (Action job, Jenkins `post { failure }`, or manual CLI).
2. **Collect** the failed logs (GitHub API on Actions; a tee'd file on Jenkins).
3. **Distill, deterministically:** strip ANSI and timestamps, collapse repeated lines, **redact secrets**, and extract the highest-signal error windows — reducing thousands of lines to a small budget.
4. **Verdict:** send only that distilled evidence to a model for a structured result (category, confidence, root cause, suggested fix, evidence).
5. **Post** it where you'll see it.

Only the distilled, redacted window is ever sent to a model — never your raw logs.

---

## Privacy & security

Before any model call, ci-medic redacts known secret formats (AWS keys, GitHub tokens, JWTs, private keys, bearer tokens, credentials-in-URLs) **and** runs an entropy filter that catches high-randomness strings even in unknown formats. For zero egress, point it at a local model and set no cloud key.

---

## Roadmap

v0.1 ships GitHub Actions and Jenkins. Next: GitLab CI (v0.3), flaky-test memory that tracks chronic flakes across runs (v0.4), and hardware/LAVA log triage (v0.5).

## License

Apache-2.0