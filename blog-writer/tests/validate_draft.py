"""Final gate for a blog-writer draft. Usage:

    python3 tests/validate_draft.py <draft.md>

Checks, in order:
1. The draft has a level-1 title (first `# ` line).
2. No `[NEEDS SOURCE]` marker survived into the draft.
3. A `## Sources` section exists and holds at least one http(s) link with source text.
4. The anti-ai scanner reports zero HIGH hits on the draft. MEDIUM hits are reported
   as warnings (REVIEW can be legitimate human writing; judge by hand).

Exit code 0 = draft passes the gate.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCANNER_CANDIDATES = [
    Path(__file__).resolve().parent.parent.parent / "anti-ai" / "check_tells.py",
    Path("/home/user/anti-ai/check_tells.py"),
]


def find_scanner():
    env = os.environ.get("ANTI_AI_SCANNER")
    if env and Path(env).is_file():
        return Path(env)
    for c in SCANNER_CANDIDATES:
        if c.is_file():
            return c
    return None


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    draft = Path(sys.argv[1])
    if not draft.is_file():
        print("no such file: %s" % draft)
        sys.exit(2)
    text = draft.read_text(encoding="utf-8")
    problems = []
    warnings = []

    title = re.search(r"^# .+", text, re.MULTILINE)
    if not title:
        problems.append("no level-1 title (first `# ` line) found")

    if "[NEEDS SOURCE]" in text:
        problems.append("[NEEDS SOURCE] marker survived into the draft")

    sources = re.search(r"^## Sources\s*$", text, re.MULTILINE)
    if not sources:
        problems.append("no `## Sources` section")
    else:
        tail = text[sources.end():]
        links = re.findall(r"\[[^\]]+\]\(https?://[^)]+\)", tail)
        if not links:
            problems.append("Sources section holds no markdown links")

    scanner = find_scanner()
    if scanner is None:
        problems.append("anti-ai scanner not found (set ANTI_AI_SCANNER)")
    else:
        r = subprocess.run(
            [sys.executable, str(scanner), "--json", str(draft)],
            capture_output=True, text=True,
        )
        hits = json.loads(r.stdout)["hits"]
        highs = [h for h in hits if h["severity"] == "high"]
        med = [h for h in hits if h["severity"] == "medium"]
        for h in highs:
            problems.append("HIGH: L%s %s (%s)" % (h.get("line"), h.get("id"), h.get("match")))
        for h in med:
            warnings.append("MEDIUM: L%s %s" % (h.get("line"), h.get("id")))

    for p in problems:
        print("FAIL " + p)
    for w in warnings:
        print("WARN " + w)
    if problems:
        print("VERDICT: FAIL (%d problem%s)" % (len(problems), "" if len(problems) == 1 else "s"))
        sys.exit(1)
    print("VERDICT: PASS" + (" (%d medium hit%s, judge by hand)" % (len(warnings), "" if len(warnings) == 1 else "s") if warnings else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
