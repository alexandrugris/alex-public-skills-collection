#!/usr/bin/env python3
"""Scanner for the anti-AI phrase list.

Reads patterns.json (same directory) and reports every occurrence of a known
AI tell in the given files/directories, with line numbers, severity and fix.

Usage:
    python3 check_tells.py <file-or-dir> [...] [--json] [--cat chat,inflated]
                           [--severity high] [--density]
    python3 check_tells.py --fixtures tests/fixtures-ro.csv tests/fixtures-fr.csv

The --fixtures mode scores trap sentences (CSV: lang,expect,exid,text). expect=FAIL
must fire pattern exid; expect=PASS must fire nothing. Only the regex blocklist runs;
the heuristics (structure/list/house) are excluded, they need longer texts.
Gate: >=90% of MUST-FAIL fire, 100% of MUST-PASS stay clean.

Exit code is always 0. The VERDICT line states the result.
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
LIST_PATH = os.path.join(BASE, "patterns.json")
if not os.path.exists(LIST_PATH):
    LIST_PATH = os.path.join(os.path.dirname(BASE), "references", "patterns.json")
EXT = {".md", ".txt", ".html", ".json", ".rst", ".org", ".csv"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".openclaw", ".backups"}


def load_list():
    with open(LIST_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    for item in data["phrases"]:
        item["re"] = re.compile(item["regex"], re.I)
    return data


def iter_files(paths):
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for name in files:
                    if os.path.splitext(name)[1].lower() in EXT:
                        yield os.path.join(root, name)
        elif os.path.isfile(path):
            yield path
        else:
            print("missing: %s" % path, file=sys.stderr)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


PERSON_NOUNS = (
    "person", "people", "guy", "lady", "man", "woman", "kid", "child",
    "friend", "partner", "colleague", "coworker", "co-worker", "broker",
    "worker", "employee", "employer", "teacher", "student", "leader", "boss",
    "author", "writer", "journalist", "editor", "politician", "founder",
    "co-founder", "cofounder", "ceo", "engineer", "designer", "consultant",
    "analyst", "reader", "player", "athlete", "coach", "doctor", "nurse",
    "scientist", "researcher", "critic", "historian", "artist", "musician",
    "actor", "director", "activist", "lawyer", "accountant", "marketer",
    "operator", "seller", "buyer", "supplier", "contractor", "intern",
    "apprentice", "volunteer", "neighbour", "neighbor", "stranger",
    "everyone", "someone", "anyone", "he", "she", "they", "him", "her",
    "them", "his", "hers", "their", "our", "us", "we",
    # RO / FR person nouns (same exemption logic)
    "prieten", "prietene", "om", "omul", "femeie", "femeia", "barbat", "coleg",
    "colega", "angajat", "angajatul", "profesor", "client", "clientul",
    "partener", "adversar", "autor", "autorul", "scriitor", "jucator",
    "vecin", "vecinul", "straina", "autorul", "mama", "tata", "copil",
    "ami", "amie", "homme", "femme", "collegue", "collègue", "partenaire",
    "auteur", "voisin", "inconnu", "lecteur", "locuteur", "dirigeant",
)
_PERSON_RE = re.compile(r"\b(?:" + "|".join(PERSON_NOUNS) + r")\b", re.I)
EXEMPT_CATS = {"honesty"}


def person_follows(before, after):
    """True if the match refers to a person.
    'honest broker' / 'his honest assessment' / 'her honest assessment' -> allowed;
    'the honest answer is' / 'to be honest' -> not."""
    head = " ".join(re.findall(r"[A-Za-z']+", after)[:2]).lower()
    tail = " ".join(re.findall(r"[A-Za-z']+", before)[-2:]).lower()
    return bool(_PERSON_RE.search(head) or _PERSON_RE.search(tail))


QUOTE_PATS = [
    re.compile(r'"[^"]{0,600}"', re.S),
    re.compile(r"\u201c[^\u201d]{0,600}\u201d", re.S),
    re.compile(r"\u2018[^\u2019]{0,600}\u2019", re.S),
]


def quote_spans(text):
    spans = []
    for pat in QUOTE_PATS:
        for m in pat.finditer(text):
            spans.append((m.start(), m.end()))
    return spans


def in_quotes(pos, spans):
    return any(a <= pos < b for a, b in spans)


EXEMPT_LOG = []


def scan(text, data, cats=None, min_sev=None):
    sev_rank = {"low": 0, "medium": 1, "high": 2}
    hits = []
    del EXEMPT_LOG[:]
    spans = quote_spans(text)
    for item in data["phrases"]:
        if cats and item["cat"] not in cats:
            continue
        if min_sev and sev_rank.get(item["severity"], 0) < sev_rank.get(min_sev, 0):
            continue
        for match in item["re"].finditer(text):
            if in_quotes(match.start(), spans):
                EXEMPT_LOG.append({"id": item["id"], "why": "quoted",
                                   "match": match.group(0)[:60]})
                continue
            markers = item.get("literal")
            if markers:
                b_raw = text[max(0, match.start() - 40):match.start()]
                a_raw = text[match.end():match.end() + 40]
                b_raw = re.split(r"[.!?:;\n]", b_raw)[-1]
                a_raw = re.split(r"[.!?:;\n]", a_raw)[0]
                w_before = " ".join(re.findall(r"[A-Za-z']+", b_raw)[-3:]).lower()
                w_after = " ".join(re.findall(r"[A-Za-z']+", a_raw)[:3]).lower()
                near = w_before + " " + w_after
                if any(re.search(r"\b" + re.escape(mk) + r"\b", near) for mk in markers):
                    EXEMPT_LOG.append({"id": item["id"], "why": "literal",
                                       "match": match.group(0)[:60]})
                    continue
            hits.append(
                {
                    "id": item["id"],
                    "cat": item["cat"],
                    "severity": item["severity"],
                    "label": item["label"],
                    "fix": item["fix"],
                    "line": line_of(text, match.start()),
                    "match": match.group(0)[:120],
                    "after": text[match.end():match.end() + 80],
                    "before": text[max(0, match.start() - 45):match.start()],
                }
            )
    return hits


def structural_heuristics(text, path):
    """Things the regex list cannot see: rhythm, header load, list lockstep."""
    notes = []
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    em = text.count(" - ") + text.count(" — ")
    if len(paragraphs) >= 4 and em / max(len(paragraphs), 1) >= 2:
        notes.append(
            {
                "id": "struct.em_dash_density",
            "cat": "structure",
                "severity": "medium",
                "label": "em-dash density %.1f/paragraph" % (em / len(paragraphs)),
                "fix": "Variaza ritmul: propozitie scurta dupa una lunga.",
                "line": 1,
            }
        )
    heads = re.findall(r"^#{1,6}\s+\S.*$", text, re.M)
    if len(heads) >= 8:
        notes.append(
            {
                "id": "struct.header_load",
            "cat": "structure",
                "severity": "low",
                "label": "%d headings" % len(heads),
                "fix": "Documente lungi cu multe headings par scrise de model.",
                "line": 1,
            }
        )
    bullets = re.findall(r"^\s*[-*]\s+(\w+)", text, re.M)
    if bullets:
        firsts = Counter(b.lower() for b in bullets)
        for word, n in firsts.items():
            if n >= 3 and word.endswith("ing"):
                notes.append(
                    {
                        "id": "struct.gerund_list",
            "cat": "structure",
                        "severity": "medium",
                        "label": "%d bullets start with '%s...'" % (n, word),
                        "fix": "Un bullet substantiv, unul verb, unul propozitie.",
                        "line": 1,
                    }
                )
                break
    words = len(re.findall(r"[A-Za-zÀ-ÿ]+", text))
    if words:
        lens = [len(s.split()) for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if len(lens) >= 12:
            band = sum(1 for l in lens if 12 <= l <= 20) / len(lens)
            if band >= 0.6:
                notes.append(
                    {
                        "id": "struct.metronome",
            "cat": "structure",
                        "severity": "medium",
                        "label": "%.0f%% sentences in 12-20 words" % (band * 100),
                        "fix": "Metronom: lungime constanta.",
                        "line": 1,
                    }
                )
    return notes


def _prose_sentences(text):
    t = re.sub(r"(?m)^\s*(?:[-*+]\s+|\d+[.)]\s+)", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]


def parallel_list_notes(text, path):
    """Three consecutive prose sentences with the same shape = a list hiding in prose."""
    sents = _prose_sentences(text)
    notes = []
    for i in range(len(sents) - 2):
        trio = sents[i:i + 3]
        lens = [len(s.split()) for s in trio]
        if max(lens) - min(lens) > 2:
            continue
        if not all(5 <= l <= 18 for l in lens):
            continue
        if not all(re.match(r"^(?:[A-Z][\w'-]*|The [A-Z][\w'-]*|Each [a-z]+|One [a-z]+)", s) for s in trio):
            continue
        if any(re.search(r"\b(?:and|but|or|while|whereas|though)\b", s.lower()) for s in trio):
            continue
        notes.append({
            "id": "list.parallel_prose",
            "cat": "list",
            "severity": "medium",
            "label": "lista mascata in proza: 3 propozitii paralele",
            "fix": "Daca sunt elemente de lista, fa-i bullet points. Daca sunt o idee, uneste-le intr-o propozitie.",
            "line": 1,
        })
        break
    # long parallel pairs (the "X asks... / Y asks..." shape): 18-30 words each,
    # similar length, both starting with a name-like "First Last" token
    for i in range(len(sents) - 1):
        pair = sents[i:i + 2]
        lens = [len(s.split()) for s in pair]
        if not all(18 <= l <= 30 for l in lens):
            continue
        if abs(lens[0] - lens[1]) > 4:
            continue
        if not all(re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+", s) for s in pair):
            continue
        notes.append({
            "id": "list.parallel_pair_long",
            "cat": "list",
            "severity": "medium",
            "label": "2 propozitii paralele lungi (tip 'X asks / Y asks')",
            "fix": "Sparge paralelismul: variaza lungimea si forma, nu pastra ambele cadre identice.",
            "line": 1,
        })
        break
    return notes


def house_style_notes(text, path):
    notes = []
    em = text.count(chr(8212)) + len(re.findall(r" - ", text))
    words = max(len(re.findall(r"[A-Za-zÀ-ÿ]+", text)), 1)
    if em >= 2 or 1000.0 * em / words > 1.0:
        notes.append({
            "id": "house.em_dash",
            "cat": "house",
            "severity": "low",
            "label": "%d em-dash (casa ta: 0)" % em,
            "fix": "Foloseste colon sau doua propozitii.",
            "line": 1,
        })
    def _sent_offsets(flat):
        """Yield (start_offset, sentence) pairs, skipping bullet/heading lines."""
        prev = 0
        offs = []
        for m in re.finditer(r"(?<=[.!?])\s+", flat):
            seg = flat[prev:m.start()]
            if seg.strip() and not seg.lstrip().startswith(("-", "*", "#")):
                offs.append((prev, seg.strip()))
            prev = m.end()
        seg = flat[prev:]
        if seg.strip() and not seg.lstrip().startswith(("-", "*", "#")):
            offs.append((prev, seg.strip()))
        return offs

    flat = re.sub(r"(?m)^\s*(?:[-*+]|\d+[.)])\s+", " ", text)
    offs = _sent_offsets(flat)

    def _is_enum(s):
        return s.count(",") >= 2 or (";" in s and re.search(r";[^.;!?]*\b(?:and|or)\b", s))

    def _max_clause(s):
        return max(len(c.split()) for c in re.split(r"[,;]", s))

    lens = [len(s.split()) for _, s in offs]
    if lens:
        mean = sum(lens) / float(len(lens))
        if mean > 32 or mean < 8:
            notes.append({
                "id": "house.sentence_len",
            "cat": "house",
                "severity": "low",
                "label": "medie %.1f cuvinte (casa ta: 8-32; enumaratiile pot creste)" % mean,
                "fix": "Variaza ritmul: propozitie scurta dupa una lunga.",
                "line": 1,
            })
        over = [(off, s) for off, s in offs
                if (len(s.split()) > 50 if _is_enum(s) else len(s.split()) > 35)
                or (_is_enum(s) and _max_clause(s) > 22)]
        if over:
            n_over = len(over)
            line = flat.count("\n", 0, over[0][0]) + 1
            notes.append({
                "id": "house.long_sentence",
            "cat": "house",
                "severity": "low",
                "label": "%d propozitii peste limita (enum <=50 cu propozitii de <=22, rest <=35)" % n_over,
                "fix": "Taie in doua. Enumaratia lunga e ok doar daca fiecare element e scurt.",
                "line": line,
            })
    words = re.findall(r"[A-Za-z\u00c0-\u00ff]+", text)
    if len(words) >= 40:
        avg = sum(len(w) for w in words) / float(len(words))
        long_share = sum(1 for w in words if len(w) >= 10) / float(len(words))
        if avg > 4.9:
            notes.append({
                "id": "house.word_len",
                "cat": "house",
                "severity": "low",
                "label": "medie %.1f litere/cuvant (simplu: sub 4.8)" % avg,
                "fix": "Cuvinte mai scurte. Vezi categoria complex pentru inlocuiri.",
                "line": 1,
            })
        if long_share > 0.12:
            notes.append({
                "id": "house.long_words",
                "cat": "house",
                "severity": "low",
                "label": "%.0f%% din cuvinte au 10+ litere" % (long_share * 100),
                "fix": "Simplifica: inlocuieste cu echivalentul scurt.",
                "line": 1,
            })
    return notes


def run_fixtures(paths, data):
    must_fail = must_pass = fired = clean = 0
    problems = []
    for path in paths:
        try:
            with open(path, encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
        except OSError as exc:
            print("cannot read %s: %s" % (path, exc), file=sys.stderr)
            continue
        for row in rows:
            expect = (row.get("expect") or "").strip().upper()
            exid = (row.get("exid") or "").strip()
            text = row.get("text") or ""
            hits = scan(text, data)
            ids = sorted({h["id"] for h in hits})
            if expect == "FAIL":
                must_fail += 1
                if exid.endswith("."):
                    matched = any(i.startswith(exid) for i in ids)
                elif exid:
                    matched = exid in ids
                else:
                    matched = bool(ids)
                if matched:
                    fired += 1
                else:
                    problems.append("%s NOT-FIRED %s: %r -> %s" % (path, exid, text[:70], ids))
            elif expect == "PASS":
                must_pass += 1
                if not ids:
                    clean += 1
                else:
                    problems.append("%s GHOST %s: %r" % (path, ",".join(ids), text[:70]))
    fire_rate = 100.0 * fired / max(must_fail, 1)
    clean_rate = 100.0 * clean / max(must_pass, 1)
    print("fixtures: MUST-FAIL fired %d/%d (%.0f%%) | MUST-PASS clean %d/%d (%.0f%%)"
          % (fired, must_fail, fire_rate, clean, must_pass, clean_rate))
    for p in problems:
        print("  " + p)
    verdict = "PASS" if (must_fail and must_pass and fire_rate >= 90 and clean_rate == 100) else "FAIL"
    print("VERDICT: %s" % verdict)
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--cat", help="comma separated categories")
    ap.add_argument("--severity", choices=["low", "medium", "high"])
    ap.add_argument("--density", action="store_true", help="hits per 1000 words")
    ap.add_argument("--fixtures", nargs="+", help="trap corpus CSVs (lang,expect,exid,text)")
    args = ap.parse_args()

    data = load_list()

    if args.fixtures:
        run_fixtures(args.fixtures, data)
        return
    if not args.paths:
        ap.error("give files/directories, or --fixtures <csv> [...]")

    cats = set(args.cat.split(",")) if args.cat else None

    all_hits = []
    total_words = 0
    exempt_count = 0
    for path in iter_files(args.paths):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            print("cannot read %s: %s" % (path, exc), file=sys.stderr)
            continue
        total_words += len(re.findall(r"[A-Za-zÀ-ÿ]+", text))
        for hit in scan(text, data, cats, args.severity):
            hit["file"] = path
            all_hits.append(hit)
        for ex in EXEMPT_LOG:
            exempt_count += 1
        for note in structural_heuristics(text, path):
            note["file"] = path
            all_hits.append(note)
        for note in parallel_list_notes(text, path) + house_style_notes(text, path):
            note["file"] = path
            all_hits.append(note)

    allowed = [
        h for h in all_hits
        if h.get("cat") in EXEMPT_CATS
        and person_follows(h.get("before", ""), h.get("after", ""))
    ]
    all_hits = [
        h for h in all_hits
        if not (h["cat"] in EXEMPT_CATS
                and person_follows(h.get("before", ""), h.get("after", "")))
    ]

    by_cat = Counter(h["cat"] for h in all_hits)
    by_sev = Counter(h["severity"] for h in all_hits)

    if args.json:
        print(
            json.dumps(
                {
                    "hits": all_hits,
                    "by_category": dict(by_cat),
                    "by_severity": dict(by_sev),
                    "words": total_words,
                    "exempt": exempt_count,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if not all_hits:
        print("CLEAN — nicio expresie din listă găsită.")
        print("VERDICT: PASS")
        return

    grouped = defaultdict(list)
    for hit in all_hits:
        grouped[hit["file"]].append(hit)

    for path, hits in grouped.items():
        print("\n=== %s (%d) ===" % (path, len(hits)))
        for hit in sorted(hits, key=lambda h: (h["line"], h["id"])):
            print(
                "  L%-5d %-7s %-9s %-22s %s"
                % (
                    hit["line"],
                    hit["severity"],
                    hit["cat"],
                    hit.get("match", "")[:22],
                    hit["label"],
                )
            )
            if hit.get("fix"):
                print("           fix: %s" % hit["fix"])

    print("\n--- totals ---")
    print("by category: %s" % dict(by_cat))
    print("by severity: %s" % dict(by_sev))
    if allowed:
        print("allowed (referinta la o persoana): %d" % len(allowed))
    if exempt_count:
        print("allowed (citat sau literal): %d" % exempt_count)
    if args.density and total_words:
        print("density: %.2f hits / 1000 words (%d words)" % (1000.0 * len(all_hits) / total_words, total_words))
    hi = by_sev.get("high", 0)
    print("VERDICT: %s" % ("FAIL" if hi else ("REVIEW" if all_hits else "PASS")))


if __name__ == "__main__":
    main()
