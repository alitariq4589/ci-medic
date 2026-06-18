import os
import json
import httpx

API = "https://api.github.com"
MARKER = "<!-- ci-medic -->"

def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def _pr_number() -> int | None:
    """Get the PR number from the Actions event payload."""
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        event = json.load(f)
    pr = event.get("pull_request")
    if pr:
        return pr.get("number")
    # push events have no PR; nothing to comment on
    return None

def post_comment(body: str) -> None:
    """Post (or update) a sticky ci-medic comment on the current PR."""
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr = _pr_number()

    body = f"{MARKER}\n{body}"

    if pr is None:
        # not a PR (e.g. push event) — print instead of posting
        print("ci-medic: no PR context; comment body below:\n")
        print(body)
        return

    with httpx.Client(headers=_headers(token), timeout=60,
                      follow_redirects=True) as client:
        # find an existing ci-medic comment to update (sticky behavior)
        r = client.get(f"{API}/repos/{repo}/issues/{pr}/comments")
        r.raise_for_status()
        existing = next(
            (c for c in r.json() if MARKER in (c.get("body") or "")), None)

        if existing:
            client.patch(
                f"{API}/repos/{repo}/issues/comments/{existing['id']}",
                json={"body": body}).raise_for_status()
        else:
            client.post(
                f"{API}/repos/{repo}/issues/{pr}/comments",
                json={"body": body}).raise_for_status()