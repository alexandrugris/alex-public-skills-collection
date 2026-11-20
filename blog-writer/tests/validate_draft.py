"""Final gate for a blog-writer draft. Usage:

    python3 tests/validate_draft.py <draft.md> [--json] [--verify-urls]

Checks, in order:
1. The draft has a level-1 title (first `# ` line).
2. No `[NEEDS SOURCE]` marker survived into the draft.
3. No banned generic section headings (`Introduction`, `Conclusion`, `Key takeaways`, `What is ...?`).
4. No placeholder or reserved invalid URLs (`.invalid`, `example.com/org/net`, `localhost`).
5. A `## Sources` section exists and holds at least one http(s) markdown link, and every
   inline body URL appears in `## Sources`.
6. Optional `--verify-urls`: live HTTP reachability check on all cited URLs.
7. The anti-ai scanner reports zero HIGH hits on the draft. MEDIUM hits are reported
   as warnings (REVIEW can be legitimate human writing; judge by hand).

Exit code 0 = draft passes the gate.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

SCANNER_CANDIDATES = [
    Path(__file__).resolve().parent.parent.parent / "anti-ai" / "check_tells.py",
]

BANNED_HEADING_RE = re.compile(
    r"^#{2,6}\s+(?:Introduction|Conclusion|Key takeaways?|What is .+\?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net", "localhost", "127.0.0.1"}


def find_scanner():
    env = os.environ.get("ANTI_AI_SCANNER")
    if env and Path(env).is_file():
        return Path(env)
    for candidate in SCANNER_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def is_placeholder_url(url):
    host = (urlparse(url).hostname or "").lower()
    return host.endswith(".invalid") or host in PLACEHOLDER_HOSTS


def verify_url_live(url, timeout=8):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "blog-writer-validator/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except urllib.error.HTTPError as exc:
        if exc.code == 405:
            try:
                req_get = urllib.request.Request(url, method="GET", headers={"User-Agent": "blog-writer-validator/1.0"})
                with urllib.request.urlopen(req_get, timeout=timeout) as resp:
                    return 200 <= resp.status < 400
            except Exception:
                return False
        return False
    except Exception:
        return False


def validate_text(text, draft_path, verify_urls=False):
    problems = []
    warnings = []

    if not re.search(r"^# .+", text, re.MULTILINE):
        problems.append("no level-1 title (first `# ` line) found")

    if "[NEEDS SOURCE]" in text:
        problems.append("[NEEDS SOURCE] marker survived into the draft")

    for m in BANNED_HEADING_RE.finditer(text):
        problems.append("banned generic heading: %s" % m.group(0).strip())

    all_urls = [u.rstrip(".,;:") for u in URL_RE.findall(text)]
    for u in sorted(set(all_urls)):
        if is_placeholder_url(u):
            problems.append("placeholder or invalid URL: %s" % u)

    sources = re.search(r"^## Sources\s*$", text, re.MULTILINE)
    source_urls = set()
    body_text = text
    if not sources:
        problems.append("no `## Sources` section")
    else:
        body_text = text[:sources.start()]
        tail = text[sources.end():]
        links = MD_LINK_RE.findall(tail)
        source_urls = {u.rstrip(".,;:") for u in links}
        if not source_urls:
            problems.append("Sources section holds no markdown links")

        inline_urls = {u.rstrip(".,;:") for u in MD_LINK_RE.findall(body_text)}
        missing_in_sources = sorted(inline_urls - source_urls)
        for u in missing_in_sources:
            problems.append("inline body URL missing from `## Sources`: %s" % u)
        if not inline_urls and source_urls:
            warnings.append("no inline markdown links in body (only in `## Sources`)")

    if verify_urls:
        for u in sorted(set(all_urls)):
            if is_placeholder_url(u):
                continue
            if not verify_url_live(u):
                problems.append("unreachable URL: %s" % u)

    scanner = find_scanner()
    if scanner is None:
        problems.append("anti-ai scanner not found (set ANTI_AI_SCANNER)")
    else:
        r = subprocess.run(
            [sys.executable, str(scanner), "--json", str(draft_path)],
            capture_output=True, text=True,
        )
        if r.returncode != 0 or not r.stdout.strip():
            problems.append("anti-ai scanner failed: %s" % (r.stderr.strip() or "empty output"))
        else:
            hits = json.loads(r.stdout)["hits"]
            for h in hits:
                if h["severity"] == "high":
                    problems.append("HIGH: L%s %s (%s)" % (h.get("line"), h.get("id"), h.get("match")))
                elif h["severity"] == "medium":
                    warnings.append("MEDIUM: L%s %s" % (h.get("line"), h.get("id")))

    return problems, warnings


def main():
    ap = argparse.ArgumentParser(description="Final gate for a blog-writer draft.")
    ap.add_argument("draft", help="path to draft markdown file")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--verify-urls", action="store_true", help="perform live HTTP check on cited URLs")
    args = ap.parse_args()

    draft = Path(args.draft)
    if not draft.is_file():
        print("no such file: %s" % draft)
        sys.exit(2)

    text = draft.read_text(encoding="utf-8")
    problems, warnings = validate_text(text, draft, verify_urls=args.verify_urls)
    verdict = "FAIL" if problems else "PASS"

    if args.json:
        print(json.dumps({
            "file": str(draft),
            "verdict": verdict,
            "problems": problems,
            "warnings": warnings,
        }, ensure_ascii=False, indent=2))
        sys.exit(1 if problems else 0)

    for p in problems:
        print("FAIL " + p)
    for w in warnings:
        print("WARN " + w)
    if problems:
        print("VERDICT: FAIL (%d problem%s)" % (len(problems), "" if len(problems) == 1 else "s"))
        sys.exit(1)
    suffix = " (%d warning%s, judge by hand)" % (len(warnings), "" if len(warnings) == 1 else "s") if warnings else ""
    print("VERDICT: PASS" + suffix)
    sys.exit(0)


if __name__ == "__main__":
    main()
