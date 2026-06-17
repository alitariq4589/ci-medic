import json, subprocess, pathlib

FIX = pathlib.Path("tests/fixtures")
labels = [json.loads(l) for l in (FIX / "labels.jsonl").read_text().splitlines() if l.strip()]

correct = 0
for entry in labels:
    res = subprocess.run(
        ["ci-medic", "analyze", "--file", str(FIX / entry["file"]), "--json"],
        capture_output=True, text=True)
    out = res.stdout + res.stderr
    try:
        verdict = json.loads(res.stdout.strip())
        got = verdict["category"]
    except (ValueError, KeyError):
        print(f"✗ {entry['file']:50} NO VERDICT (exit={res.returncode})")
        print("    stdout[:200]:", repr(res.stdout[:200]))
        print("    stderr[:300]:", repr(res.stderr[:300]))
        continue
    ok = got == entry["category"]
    correct += ok
    print(f"{'✓' if ok else '✗'} {entry['file']:50} want={entry['category']:11} got={got}")
print(f"\n{correct}/{len(labels)} correct")