"""anti-ai full test run: trilingual trap-corpus gate + self-scan of the skill docs.

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
LANGS = ("en", "ro", "fr")


def scanner(args):
    return subprocess.run(
        [sys.executable, str(SCANNER)] + args, capture_output=True, text=True
    )


def gate():
    """Every MUST-FAIL row fires, every MUST-PASS row stays clean."""
    csvs = [str(ROOT / "tests" / ("fixtures-%s.csv" % lang)) for lang in LANGS]
    r = scanner(["--fixtures"] + csvs)
    out = r.stdout
    must_fail_ok = "MUST-FAIL fired" in out and "100%" in out.split("MUST-FAIL")[1].split("|")[0]
    must_pass_ok = "MUST-PASS clean" in out and "100%" in out.split("MUST-PASS")[1].split("|")[0]
    print(out.strip())
    if not must_fail_ok:
        print("gate: MUST-FAIL rows missing their patterns")
        return False
    if not must_pass_ok:
        print("gate: MUST-PASS rows firing false hits")
        return False
    return True


def self_scan():
    """The skill's own docs carry 0 active HIGH/MEDIUM hits (LOW house notes are fine)."""
    r = scanner(["--json", str(ROOT)])
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        return False
    hits = json.loads(r.stdout)["hits"]
    docs = sorted(
        {h["file"] for h in hits if Path(h["file"]).suffix == ".md"}
    )
    bad = [
        h
        for h in hits
        if Path(h["file"]).suffix == ".md" and h["severity"] in ("high", "medium")
    ]
    for h in bad:
        print("self-scan %s: %s %s" % (h["severity"].upper(), h["file"], h["id"]))
    print("self-scan: %d docs scanned, %d active HIGH/MEDIUM hits" % (len(docs), len(bad)))
    return not bad


def main():
    results = []
    results.append(("fixtures gate", gate()))
    results.append(("doc self-scan", self_scan()))
    print("")
    ok = True
    for name, passed in results:
        print("%-14s %s" % (name, "PASS" if passed else "FAIL"))
        ok = ok and passed
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
