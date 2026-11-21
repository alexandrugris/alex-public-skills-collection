#!/usr/bin/env python3
"""Anti-collapse guardrails for adversarial verification loops.

Snapshots a draft's structural anchors before verification begins and checks
every revised draft against hard collapse limits:
  - Title preserved
  - All H2 section headings preserved
  - Opening narrative paragraph untouched
  - Body word-count shrinkage <= max_shrink_ratio (default 10%)
  - Body token diff ratio <= max_diff_ratio (default 15%)

Exit codes:
  0 = PASS (or snapshot written)
  1 = FAIL (collapse guardrail tripped)
  2 = usage / I/O error
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

SOURCES_HDR_RE = re.compile(r"(?m)^##\s+Sources\s*$")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


def extract_body(text: str) -> str:
    m = SOURCES_HDR_RE.search(text)
    return text[: m.start()] if m else text


def extract_anchors(text: str) -> dict:
    body = extract_body(text)
    lines = body.splitlines()

    title = ""
    h2_headings: list[str] = []
    opening_paragraph = ""

    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        if s.startswith("# ") and not title:
            title = s[2:].strip()
            continue
        if s.startswith("## "):
            h2_headings.append(s[3:].strip())
            continue
        if not opening_paragraph:
            if s.startswith("*") and s.endswith("*") and len(s) > 2:
                continue
            opening_paragraph = s

    # Strip URLs inside markdown links so fixing a DOI/URL does not penalize body token diff
    prose_without_urls = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    tokens = [w.lower() for w in WORD_RE.findall(prose_without_urls)]

    return {
        "title": title,
        "h2_headings": h2_headings,
        "opening_paragraph_sha256": hashlib.sha256(opening_paragraph.encode("utf-8")).hexdigest(),
        "opening_paragraph_preview": opening_paragraph[:120],
        "body_word_count": len(tokens),
        "body_tokens": tokens,
    }


def check_against_snapshot(
    snapshot: dict,
    revised_text: str,
    max_diff_ratio: float = 0.15,
    max_shrink_ratio: float = 0.10,
) -> dict:
    rev = extract_anchors(revised_text)
    violations: list[dict] = []

    if rev["title"] != snapshot["title"]:
        violations.append(
            {
                "rule": "title_changed",
                "detail": f"Title changed from {snapshot['title']!r} to {rev['title']!r}.",
            }
        )

    missing_headings = [h for h in snapshot["h2_headings"] if h not in rev["h2_headings"]]
    if missing_headings:
        violations.append(
            {
                "rule": "missing_headings",
                "detail": f"H2 heading(s) removed or altered: {missing_headings}",
            }
        )

    if rev["opening_paragraph_sha256"] != snapshot["opening_paragraph_sha256"]:
        violations.append(
            {
                "rule": "opening_scene_mutated",
                "detail": "Opening narrative paragraph was altered during source verification.",
            }
        )

    old_wc = max(snapshot["body_word_count"], 1)
    new_wc = rev["body_word_count"]
    shrink_ratio = max(0.0, (old_wc - new_wc) / old_wc)
    if shrink_ratio > max_shrink_ratio:
        violations.append(
            {
                "rule": "word_count_shrinkage",
                "detail": f"Body shrank by {shrink_ratio:.1%} ({old_wc} -> {new_wc} words; limit {max_shrink_ratio:.0%}).",
            }
        )

    sim = difflib.SequenceMatcher(None, snapshot["body_tokens"], rev["body_tokens"]).ratio()
    diff_ratio = 1.0 - sim
    if diff_ratio > max_diff_ratio:
        violations.append(
            {
                "rule": "diff_budget_exceeded",
                "detail": f"Body token diff is {diff_ratio:.1%} (limit {max_diff_ratio:.0%}); patch must stay surgical.",
            }
        )

    verdict = "FAIL" if violations else "PASS"
    return {
        "verdict": verdict,
        "violations": violations,
        "metrics": {
            "old_word_count": snapshot["body_word_count"],
            "new_word_count": new_wc,
            "shrink_ratio": round(shrink_ratio, 4),
            "diff_ratio": round(diff_ratio, 4),
            "max_shrink_ratio": max_shrink_ratio,
            "max_diff_ratio": max_diff_ratio,
            "headings_preserved": len(missing_headings) == 0,
            "opening_preserved": rev["opening_paragraph_sha256"] == snapshot["opening_paragraph_sha256"],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Anti-collapse anchor and diff-budget guardrails.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_snap = sub.add_parser("snapshot", help="Freeze anchor snapshot before verification loop")
    sp_snap.add_argument("draft", help="Path to Markdown draft")
    sp_snap.add_argument("-o", "--output", required=True, help="Path to write snapshot JSON")

    sp_chk = sub.add_parser("check", help="Check revised draft against frozen snapshot")
    sp_chk.add_argument("snapshot", help="Path to snapshot JSON")
    sp_chk.add_argument("revised", help="Path to revised Markdown draft")
    sp_chk.add_argument("--max-diff-ratio", type=float, default=0.15)
    sp_chk.add_argument("--max-shrink-ratio", type=float, default=0.10)
    sp_chk.add_argument("--json", action="store_true")

    args = ap.parse_args()

    if args.cmd == "snapshot":
        p = Path(args.draft)
        if not p.is_file():
            print(f"File not found: {p}", file=sys.stderr)
            return 2
        snap = extract_anchors(p.read_text(encoding="utf-8"))
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(snap, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"SNAPSHOT OK: {out} (words={snap['body_word_count']}, h2={len(snap['h2_headings'])})")
        return 0

    snap_path = Path(args.snapshot)
    rev_path = Path(args.revised)
    if not snap_path.is_file() or not rev_path.is_file():
        print("Snapshot or revised draft file not found.", file=sys.stderr)
        return 2

    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    res = check_against_snapshot(
        snap,
        rev_path.read_text(encoding="utf-8"),
        max_diff_ratio=args.max_diff_ratio,
        max_shrink_ratio=args.max_shrink_ratio,
    )
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        for v in res["violations"]:
            print(f"FAIL [{v['rule']}]: {v['detail']}")
        m = res["metrics"]
        print(
            f"VERDICT: {res['verdict']} "
            f"(diff={m['diff_ratio']:.1%}, shrink={m['shrink_ratio']:.1%}, "
            f"headings={'ok' if m['headings_preserved'] else 'BROKEN'}, "
            f"opening={'ok' if m['opening_preserved'] else 'MUTATED'})"
        )
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
