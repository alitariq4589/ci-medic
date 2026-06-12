import os
import httpx

API = "https://api.github.com"

def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def fetch_failed_logs(ignore_jobs: list[str] | None = None) -> dict[str, str]:
    """Return {job_name: log_text} for every failed job in the current run."""
    ignore = set(ignore_jobs or [])
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]          # "owner/name"
    run_id = os.environ["GITHUB_RUN_ID"]
    self_job = os.environ.get("GITHUB_JOB", "")

    with httpx.Client(headers=_headers(token), timeout=60,
                      follow_redirects=True) as client:
        r = client.get(f"{API}/repos/{repo}/actions/runs/{run_id}/jobs")
        r.raise_for_status()
        jobs = r.json().get("jobs", [])

        out: dict[str, str] = {}
        for job in jobs:
            name = job["name"]
            if job.get("conclusion") != "failure":
                continue
            if name == self_job or name in ignore:
                continue
            log = client.get(
                f"{API}/repos/{repo}/actions/jobs/{job['id']}/logs"
            )
            if log.status_code == 200:
                out[name] = log.text
        return out