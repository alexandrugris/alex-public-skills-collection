"""anti-ai full test run: trilingual trap-corpus gate, heuristics, examples DB, and doc self-scan.

Run from anywhere:
    python3 tests/run_tests.py
Exit code 0 = everything passed.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCANNER = ROOT / "check_tells.py"
EXAMPLES_CLI = ROOT / "scripts" / "examples.py"
LANGS = ("en", "ro", "fr")


def scanner(args):
    return subprocess.run(
        [sys.executable, str(SCANNER)] + args, capture_output=True, text=True
    )


def gate():
    """Every MUST-FAIL row fires, every MUST-PASS row stays clean (exact counts)."""
    csvs = [str(ROOT / "tests" / ("fixtures-%s.csv" % lang)) for lang in LANGS]
    r = scanner(["--fixtures"] + csvs + ["--json"])
    if not r.stdout.strip():
        print(r.stderr.strip())
        return False
    res = json.loads(r.stdout)
    fired, must_fail = res["fired"], res["must_fail"]
    clean, must_pass = res["clean"], res["must_pass"]
    print(
        "fixtures: MUST-FAIL fired %d/%d (%.1f%%) | MUST-PASS clean %d/%d (%.1f%%)"
        % (fired, must_fail, res["fire_rate"], clean, must_pass, res["clean_rate"])
    )
    for prob in res["problems"]:
        print("  " + prob)
    ok = (
        r.returncode == 0
        and must_fail > 0
        and must_pass > 0
        and fired == must_fail
        and clean == must_pass
    )
    if not ok:
        print("gate: exact 100% MUST-FAIL and MUST-PASS requirement not met")
    return ok


def self_scan():
    """The skill's own docs carry 0 active HIGH/MEDIUM hits (LOW house notes are fine)."""
    md_files = sorted(str(p) for p in ROOT.rglob("*.md"))
    r = scanner(["--json", "--severity", "medium"] + md_files)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        return False
    hits = json.loads(r.stdout)["hits"]
    bad = [h for h in hits if h["severity"] in ("high", "medium")]
    for h in bad:
        print("self-scan %s: %s L%s %s" % (h["severity"].upper(), h["file"], h.get("line"), h["id"]))
    print("self-scan: %d docs scanned, %d active HIGH/MEDIUM hits" % (len(md_files), len(bad)))
    return not bad


def heuristics():
    """Structural heuristics (mirrored summaries, long parallel pairs) behave."""
    r = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "test_heuristics.py")],
        capture_output=True, text=True,
    )
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip())
        return False
    return True


def examples_gate():
    """Corrections database passes schema and zero-HIGH checks."""
    r = subprocess.run(
        [sys.executable, str(EXAMPLES_CLI), "validate"],
        capture_output=True, text=True,
    )
    print(r.stdout.strip())
    if r.returncode != 0:
        if r.stderr.strip():
            print(r.stderr.strip())
        return False
    return True


def main():
    results = [
        ("fixtures gate", gate()),
        ("heuristics gate", heuristics()),
        ("examples gate", examples_gate()),
        ("doc self-scan", self_scan()),
    ]
    print("")
    ok = True
    for name, passed in results:
        print("%-15s %s" % (name, "PASS" if passed else "FAIL"))
        ok = ok and passed
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
