# GITHUB_REPOSITORY, GITHUB_RUN_ID, GITHUB_TOKEN (passed as input), GITHUB_JOB
# 1. GET /repos/{repo}/actions/runs/{run_id}/jobs   -> jobs[]
#    keep: conclusion == "failure" and name != own job name
# 2. GET /repos/{repo}/actions/jobs/{job_id}/logs   -> 302 redirect to plain text
#    httpx.get(..., follow_redirects=True)
# 3. return {job_name: log_text}