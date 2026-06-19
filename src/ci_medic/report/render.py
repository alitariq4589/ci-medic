from ci_medic.schema import Verdict

_EMOJI = {"code": "🐛", "flake": "🎲", "infra": "🔧",
          "dependency": "📦", "config": "⚙️"}

def render(job_name: str, v: Verdict) -> str:
    lines = [
        f"## {_EMOJI.get(v.category,'')} ci-medic: `{v.category}` "
        f"({v.confidence:.0%}) — *{job_name}*",
        "",
        f"**Root cause:** {v.root_cause}",
        f"**Suggested fix:** {v.suggested_fix}",
        f"**Retry recommended:** {'yes' if v.retry_recommended else 'no'}",
        f"\n`fingerprint: {v.fingerprint}` · `model: {v.model}`",
    ]
    if v.evidence:
        ev = "\n".join(v.evidence[:8])
        lines += ["\n<details><summary>Evidence</summary>\n",
                  f"```\n{ev}\n```", "</details>"]
    return "\n".join(lines)

def render_plain(job_name: str, v) -> str:
    lines = [
        f"ci-medic: {v.category.upper()} ({v.confidence:.0%}) — {job_name}",
        f"Root cause: {v.root_cause}",
        f"Suggested fix: {v.suggested_fix}",
        f"Retry recommended: {'yes' if v.retry_recommended else 'no'}",
        f"fingerprint: {v.fingerprint} | model: {v.model}",
    ]
    if v.evidence:
        lines.append("Evidence:")
        lines += [f"  {e}" for e in v.evidence[:8]]
    return "\n".join(lines)