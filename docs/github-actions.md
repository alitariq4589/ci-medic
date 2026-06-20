# ci-medic on GitHub Actions

A full walkthrough of installing and using ci-medic in a GitHub Actions workflow.

## What you get

When a workflow fails, ci-medic adds a job that reads the failed jobs' logs, distills and redacts them, asks a model for a verdict, and posts a **sticky comment** on the pull request which gets updated in place on every re-run and is never duplicated.

![ci-medic on github actions](assets/ci-medic-github-actions.png)

## Setup

Add a triage job to your workflow. It runs only when an upstream job fails:

```yaml
# .github/workflows/ci.yml
  triage:
    if: failure()
    needs: [build, test]          # list the jobs you want triaged
    runs-on: ubuntu-latest
    permissions:
      actions: read               # required: read the failed job logs
      pull-requests: write        # required: post the sticky comment
    steps:
      - uses: alitariq4589/ci-medic@v0.1.0
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          api-key: ${{ secrets.CI_MEDIC_API_KEY }}   # optional
```

### The two required permissions

`actions: read` lets ci-medic download the failed job logs through the GitHub API. `pull-requests: write` lets it post the comment. Without these the job fails with a 403.

### The API key is optional

`api-key` is the key for your model provider (see the main README's *Model providers*). Store it as a repository secret named `CI_MEDIC_API_KEY`:

`Settings -> Secrets and variables -> Actions -> New repository secret`

Without a key, ci-medic still runs but it posts the extracted error window with no AI verdict, so you get the right lines without the classification.

## What the verdict contains

Each failed job gets: a **category** (code / flake / infra / dependency / config), a **confidence**, a one-paragraph **root cause**, a **suggested fix**, whether a **retry** is worth trying, and a collapsible **evidence** block with the exact log lines with secrets already redacted.

![Fake Secret Leaked](assets/fake-secret-leak.png)

## Re-runs update the same comment

ci-medic marks its comment with a hidden tag, so subsequent runs edit that comment rather than adding new ones. Your PR stays clean no matter how many times CI runs.