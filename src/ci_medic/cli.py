import argparse
import os
from re import sub
import sys

from ci_medic import config as cfg_mod
from ci_medic.preprocess.ansi import strip
from ci_medic.preprocess.normalize import normalize
from ci_medic.preprocess.dedupe import dedupe
from ci_medic.preprocess.redact import redact
from ci_medic.preprocess.windows import extract_windows
from ci_medic.preprocess.fingerprint import fingerprint
from ci_medic.report.render import render_plain
from ci_medic.report.render import render_plain

def _distill(raw: str, budget: int):
    text = redact(normalize(strip(raw)))
    lines = dedupe(text.splitlines())
    windows = extract_windows(lines, budget=budget)
    distilled = "\n\n---\n\n".join(w.text for w in windows)
    fp = fingerprint([w.text for w in windows])
    return distilled, fp

def _provider_factory(cfg):
    def make(model):
        if cfg.provider == "anthropic":
            from ci_medic.llm.anthropic import Anthropic
            return Anthropic(model=model)
        from ci_medic.llm.openai_compat import OpenAICompat
        return OpenAICompat(base_url=cfg.base_url or None, model=model)
    return make

def _has_key() -> bool:
    return bool(os.environ.get("CI_MEDIC_API_KEY"))

def cmd_analyze(args):
    cfg = cfg_mod.load()
    raw = open(args.file, encoding="utf-8", errors="replace").read()
    distilled, fp = _distill(raw, cfg.char_budget)
    if not args.json:
        print("=== DISTILLED EVIDENCE ===\n")
        print(distilled)
        print(f"\nfingerprint: {fp}")
    if args.no_llm or not _has_key():
        return
    from ci_medic.llm.prompt import triage
    verdict = triage(_provider_factory(cfg), cfg.models, distilled)
    verdict.fingerprint = fp
    if args.json:
        print(verdict.model_dump_json())
        return
    print("\n=== VERDICT ===")
    print(verdict.model_dump_json(indent=2))

def cmd_github(args):
    from ci_medic.fetch_github import fetch_failed_logs
    from ci_medic.report.comment import post_comment
    from ci_medic.report.summary import write_summary
    from ci_medic.report.render import render

    cfg = cfg_mod.load()
    logs = fetch_failed_logs(cfg.ignore_jobs)
    if not logs:
        print("ci-medic: no failed jobs found.")
        return

    provider = _provider_factory(cfg) if _has_key() else None
    blocks = []
    for job, raw in logs.items():
        distilled, fp = _distill(raw, cfg.char_budget)
        if provider:
            from ci_medic.llm.prompt import triage
            v = triage(provider, cfg.models, distilled)
            v.fingerprint = fp
            blocks.append(render(job, v))
        else:
            blocks.append(
                f"## ci-medic: `{job}` (no LLM configured)\n\n"
                f"```\n{distilled[:3000]}\n```\n`fingerprint: {fp}`"
            )
    body = "\n\n".join(blocks)
    post_comment(body)
    write_summary(body)
    print("ci-medic: posted.")

def cmd_jenkins(args):
    cfg = cfg_mod.load()
    raw = open(args.file, encoding="utf-8", errors="replace").read()
    distilled, fp = _distill(raw, cfg.char_budget)

    if args.no_llm or not _has_key():
        # no LLM: emit distilled evidence so Groovy can still set a description
        print(f"ci-medic ({fp}): no LLM configured\n{distilled[:1500]}")
        return

    from ci_medic.llm.prompt import triage
    from ci_medic.report.render import render_plain
    verdict = triage(_provider_factory(cfg), cfg.models, distilled)
    verdict.fingerprint = fp

    if args.json:
        print(verdict.model_dump_json())
    else:
        # human-readable, single block — Groovy captures this for the description
        print(render_plain(args.job or "build", verdict))

def main():
    p = argparse.ArgumentParser(prog="ci-medic")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze")
    a.add_argument("--file", required=True)
    a.add_argument("--no-llm", action="store_true")
    a.add_argument("--json", action="store_true",
                   help="print only the verdict JSON")
    a.set_defaults(func=cmd_analyze)

    g = sub.add_parser("github")
    g.set_defaults(func=cmd_github)

    j = sub.add_parser("jenkins")
    j.add_argument("--file", required=True,
                   help="path to the captured console log")
    j.add_argument("--job", default="",
                   help="optional job/build label for the verdict header")
    j.add_argument("--no-llm", action="store_true")
    j.add_argument("--json", action="store_true")
    j.set_defaults(func=cmd_jenkins)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    sys.exit(main())