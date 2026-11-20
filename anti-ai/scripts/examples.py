#!/usr/bin/env python3
"""Manage the anti-ai corrections database (examples/corrections.jsonl).

Stores real AI-drafted passages alongside why they failed and how the author
rephrased them, so skills learn from lived edits via progressive retrieval
instead of dumping every example into the prompt.

Usage:
    python3 scripts/examples.py add --lang en --bad "..." --good "..." --why "..." --rules 1,1b --tags metaphor
    python3 scripts/examples.py query --lang en --topic "leadership silence" --limit 5
    python3 scripts/examples.py gaps
    python3 scripts/examples.py validate
    python3 scripts/examples.py promote-fixtures [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "examples" / "corrections.jsonl"
TESTS_DIR = ROOT / "tests"

sys.path.insert(0, str(ROOT))
import check_tells as ct  # noqa: E402

VALID_LANGS = {"en", "ro", "fr"}
VALID_STATUSES = {"logged", "promoted_fixture", "promoted_pattern", "few_shot_only"}
REQUIRED_FIELDS = ("id", "date", "lang", "bad", "good", "why")
TOKEN_RE = re.compile(r"[A-Za-z\u00C0-\u024F0-9]+")


def tokenize(text: str) -> list[str]:
    return [ct._fold(t) for t in TOKEN_RE.findall(text) if len(t) > 2]


def load_entries(path: Path = DB_PATH) -> list[dict]:
    if not path.is_file():
        return []
    entries = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
        entries.append(obj)
    return entries


def scan_text(text: str, data: dict, lang: str) -> list[dict]:
    hits = ct.scan(text, data, lang=lang)
    hits += ct.structural_heuristics(text, "<inline>")
    hits += ct.parallel_list_notes(text, "<inline>")
    hits += ct.mirrored_summary_notes(text, "<inline>")
    return hits


def next_id(entries: list[dict], today: str) -> str:
    prefix = f"ex-{today}-"
    seq = 1
    for entry in entries:
        eid = entry.get("id", "")
        if eid.startswith(prefix):
            try:
                seq = max(seq, int(eid.split("-")[-1]) + 1)
            except ValueError:
                pass
    return f"{prefix}{seq:03d}"


def cmd_add(args: argparse.Namespace) -> int:
    data = ct.load_list()
    entries = load_entries(Path(args.db))
    bad_hits = scan_text(args.bad, data, args.lang)
    good_hits = scan_text(args.good, data, args.lang)
    good_high = [h for h in good_hits if h["severity"] == "high"]

    if good_high and not args.force:
        ids = ", ".join(sorted({h["id"] for h in good_high}))
        print(f"REJECTED: good rewrite triggers HIGH tell(s): {ids}", file=sys.stderr)
        print("Fix the rewrite or pass --force if intentional.", file=sys.stderr)
        return 1

    today = args.date or dt.date.today().isoformat()
    pattern_ids = sorted({h["id"] for h in bad_hits})
    entry = {
        "id": args.id or next_id(entries, today),
        "date": today,
        "lang": args.lang,
        "context": args.context,
        "bad": args.bad.strip(),
        "good": args.good.strip(),
        "why": args.why.strip(),
        "rules": [r.strip() for r in args.rules.split(",") if r.strip()],
        "pattern_ids": pattern_ids,
        "tags": [t.strip().lower() for t in args.tags.split(",") if t.strip()],
        "scanner_caught": bool(pattern_ids),
        "status": args.status,
    }
    db = Path(args.db)
    db.parent.mkdir(parents=True, exist_ok=True)
    with db.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"ADDED {entry['id']} (scanner_caught={entry['scanner_caught']}, patterns={pattern_ids})")
    return 0


def score_entry(entry: dict, q_tokens: Counter, wanted_tags: set[str], wanted_rule: str | None) -> tuple[float, float]:
    match_score = 0.0
    etags = {t.lower() for t in entry.get("tags", [])}
    match_score += 3.0 * len(etags & wanted_tags)
    if wanted_rule and wanted_rule in entry.get("rules", []):
        match_score += 4.0
    if q_tokens:
        match_score += 2.0 * len(etags & set(q_tokens.keys()))
        doc_tokens = Counter(tokenize(" ".join([
            entry.get("bad", ""),
            entry.get("good", ""),
            entry.get("why", ""),
            " ".join(entry.get("tags", [])),
            entry.get("context", ""),
        ])))
        overlap = sum(min(c, doc_tokens[tok]) for tok, c in q_tokens.items())
        norm = math.sqrt(sum(doc_tokens.values()) or 1.0)
        match_score += (overlap / norm) * 2.5
    # Slightly favor examples where the regex scanner is blind (higher few-shot value)
    tiebreak = 0.35 if not entry.get("scanner_caught", False) else 0.0
    return match_score, tiebreak


def cmd_query(args: argparse.Namespace) -> int:
    entries = load_entries(Path(args.db))
    if args.lang and args.lang != "all":
        entries = [e for e in entries if e.get("lang") == args.lang]
    if args.only_uncaught:
        entries = [e for e in entries if not e.get("scanner_caught", False)]

    wanted_tags = {t.strip().lower() for t in (args.tags or "").split(",") if t.strip()}
    q_tokens = Counter(tokenize(args.topic or ""))

    scored = [
        (score_entry(e, q_tokens, wanted_tags, args.rule), e)
        for e in entries
    ]
    scored.sort(key=lambda pair: (pair[0][0] + pair[0][1], pair[1].get("date", "")), reverse=True)

    if wanted_tags or q_tokens or args.rule:
        matched = [e for (ms, _), e in scored if ms > 0.0]
        selected = matched[: args.limit]
        if len(selected) < args.limit:
            # Backfill with diverse general structural/taste constructs (uncaught first)
            seen_ids = {e["id"] for e in selected}
            seen_rules = {r for e in selected for r in e.get("rules", [])}
            rest = [e for _, e in scored if e["id"] not in seen_ids]
            # Prefer entries that cover new rules and uncaught taste patterns
            rest.sort(
                key=lambda e: (
                    not e.get("scanner_caught", False),
                    bool(set(e.get("rules", [])) - seen_rules),
                    e.get("date", ""),
                ),
                reverse=True,
            )
            for e in rest:
                if len(selected) >= args.limit:
                    break
                selected.append(e)
                seen_rules.update(e.get("rules", []))
    else:
        selected = [e for _, e in scored][: args.limit]

    if args.format == "json":
        print(json.dumps(selected, ensure_ascii=False, indent=2))
        return 0

    for e in selected:
        rules = ",".join(e.get("rules", [])) or "-"
        tags = ",".join(e.get("tags", [])) or "-"
        print(f"[{e['id']} | {e['lang']} | rules:{rules} | tags:{tags}]")
        print(f"  BAD : {e['bad']}")
        print(f"  GOOD: {e['good']}")
        print(f"  WHY : {e['why']}")
    return 0


def cmd_gaps(args: argparse.Namespace) -> int:
    entries = load_entries(Path(args.db))
    if args.lang and args.lang != "all":
        entries = [e for e in entries if e.get("lang") == args.lang]
    uncaught = [e for e in entries if not e.get("scanner_caught", False)]
    by_tag: dict[str, list[dict]] = defaultdict(list)
    for e in uncaught:
        for tag in e.get("tags") or ["untagged"]:
            by_tag[tag].append(e)

    if args.json:
        print(json.dumps({
            "total_entries": len(entries),
            "uncaught_count": len(uncaught),
            "by_tag": {k: [x["id"] for x in v] for k, v in sorted(by_tag.items())},
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"Scanner blind spots: {len(uncaught)}/{len(entries)} entries not caught by check_tells.py")
    for tag, items in sorted(by_tag.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print(f"\n  [{tag}] ({len(items)})")
        for item in items:
            print(f"    - {item['id']} ({item['lang']}): {item['bad'][:80]}")
    return 0


def cmd_promote_fixtures(args: argparse.Namespace) -> int:
    entries = load_entries(Path(args.db))
    existing: dict[str, set[str]] = defaultdict(set)
    for lang in VALID_LANGS:
        fp = TESTS_DIR / f"fixtures-{lang}.csv"
        if fp.is_file():
            with fp.open(encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    existing[lang].add((row.get("text") or "").strip())

    candidates = []
    for e in entries:
        pids = [p for p in e.get("pattern_ids", []) if not p.startswith(("struct.", "list.", "house."))]
        if not pids:
            continue
        lang = e["lang"]
        if e["bad"] not in existing[lang]:
            candidates.append((lang, "FAIL", pids[0], e["bad"]))
        if e["good"] not in existing[lang]:
            candidates.append((lang, "PASS", "", e["good"]))

    if not candidates:
        print("No new fixture candidates to promote.")
        return 0

    for row in candidates:
        print(f"{row[0]},{row[1]},{row[2]},{json.dumps(row[3], ensure_ascii=False)}")
    if not args.dry_run:
        for lang in VALID_LANGS:
            lang_rows = [r for r in candidates if r[0] == lang]
            if not lang_rows:
                continue
            fp = TESTS_DIR / f"fixtures-{lang}.csv"
            with fp.open("a", encoding="utf-8", newline="") as fh:
                w = csv.writer(fh)
                for row in lang_rows:
                    w.writerow(row)
            print(f"Appended {len(lang_rows)} rows to {fp}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    data = ct.load_list()
    entries = load_entries(Path(args.db))
    problems = []
    seen_ids = set()

    if not entries:
        problems.append("corrections database is empty")

    for idx, e in enumerate(entries, 1):
        eid = e.get("id", f"<row {idx}>")
        for field in REQUIRED_FIELDS:
            if not isinstance(e.get(field), str) or not e[field].strip():
                problems.append(f"{eid}: missing or empty field '{field}'")
        if eid in seen_ids:
            problems.append(f"{eid}: duplicate id")
        seen_ids.add(eid)

        lang = e.get("lang", "")
        if lang not in VALID_LANGS:
            problems.append(f"{eid}: invalid lang '{lang}'")
        status = e.get("status", "logged")
        if status not in VALID_STATUSES:
            problems.append(f"{eid}: invalid status '{status}'")

        if lang in VALID_LANGS and e.get("good"):
            good_hits = [h for h in scan_text(e["good"], data, lang) if h["severity"] == "high"]
            if good_hits:
                hit_ids = ",".join(sorted({h["id"] for h in good_hits}))
                problems.append(f"{eid}: good rewrite triggers HIGH tell(s): {hit_ids}")

    if problems:
        for p in problems:
            print("FAIL " + p)
        print(f"VERDICT: FAIL ({len(problems)} problem(s))")
        return 1
    print(f"examples: {len(entries)} entries valid, 0 HIGH tells in good rewrites")
    print("VERDICT: PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Manage anti-ai corrections database")
    ap.add_argument("--db", default=str(DB_PATH), help="path to corrections.jsonl")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="log a new bad -> good rewrite")
    p_add.add_argument("--lang", choices=sorted(VALID_LANGS), required=True)
    p_add.add_argument("--bad", required=True)
    p_add.add_argument("--good", required=True)
    p_add.add_argument("--why", required=True)
    p_add.add_argument("--rules", default="", help="comma-separated rule numbers")
    p_add.add_argument("--tags", default="", help="comma-separated tags")
    p_add.add_argument("--context", default="essay")
    p_add.add_argument("--status", choices=sorted(VALID_STATUSES), default="logged")
    p_add.add_argument("--date", default=None)
    p_add.add_argument("--id", default=None)
    p_add.add_argument("--force", action="store_true")
    p_add.set_defaults(func=cmd_add)

    p_q = sub.add_parser("query", help="retrieve top-K relevant past rewrites")
    p_q.add_argument("--lang", choices=["all", "en", "ro", "fr"], default="all")
    p_q.add_argument("--tags", default="")
    p_q.add_argument("--rule", default=None)
    p_q.add_argument("--topic", default="")
    p_q.add_argument("--limit", type=int, default=10)
    p_q.add_argument("--only-uncaught", action="store_true")
    p_q.add_argument("--format", choices=["compact", "json"], default="compact")
    p_q.set_defaults(func=cmd_query)

    p_g = sub.add_parser("gaps", help="show examples the regex scanner missed")
    p_g.add_argument("--lang", choices=["all", "en", "ro", "fr"], default="all")
    p_g.add_argument("--json", action="store_true")
    p_g.set_defaults(func=cmd_gaps)

    p_p = sub.add_parser("promote-fixtures", help="export caught entries to fixtures-*.csv")
    p_p.add_argument("--dry-run", action="store_true")
    p_p.set_defaults(func=cmd_promote_fixtures)

    p_v = sub.add_parser("validate", help="validate schema and verify all good rewrites stay clean")
    p_v.set_defaults(func=cmd_validate)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
