MARKER = '<!-- ci-medic -->'
# PR number: json.load(open(os.environ['GITHUB_EVENT_PATH']))['pull_request']['number']
#   (if key missing -> push event -> skip comment, summary only)
# GET  /repos/{repo}/issues/{pr}/comments  -> find c where MARKER in c['body']
# found    -> PATCH /repos/{repo}/issues/comments/{id}
# not found-> POST  /repos/{repo}/issues/{pr}/comments
# body: f"{MARKER}\n## ci-medic: {v.category} ({v.confidence:.0%})\n**Root cause:** ..."