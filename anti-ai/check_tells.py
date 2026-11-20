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
import unicodedata
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
LIST_PATH = os.path.join(BASE, "patterns.json")
if not os.path.exists(LIST_PATH):
    LIST_PATH = os.path.join(os.path.dirname(BASE), "references", "patterns.json")
EXT = {".md", ".txt", ".html", ".json", ".rst", ".org", ".csv"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".openclaw", ".backups"}
SEV_RANK = {"low": 0, "medium": 1, "high": 2}
WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F\u1E00-\u1EFF']+")


def _fold(text):
    """Strip diacritics (NFKD) and lowercase so RO/FR exemptions match reliably."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn").lower()


def _blank_preserve_lines(match):
    return "".join("\n" if ch == "\n" else " " for ch in match.group(0))


_FRONTMATTER_RE = re.compile(r"\A---\r?\n.*?\r?\n---(?:\r?\n|\Z)", re.S)
_FENCE_RE = re.compile(r"(?m)^([ \t]{0,3}(?:`{3,}|~{3,}))[^\n]*\n.*?\n[ \t]{0,3}\1[ \t]*$", re.S)
_URL_RE = re.compile(r"https?://[^\s)\]>\"']+")


def mask_non_prose(text):
    """Blank Markdown YAML frontmatter, fenced code blocks, and URLs while preserving line numbers."""
    text = _FRONTMATTER_RE.sub(_blank_preserve_lines, text)
    text = _FENCE_RE.sub(_blank_preserve_lines, text)
    text = _URL_RE.sub(_blank_preserve_lines, text)
    return text


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
    # RO / FR person nouns (matched after diacritic folding)
    "prieten", "prietena", "prietene", "om", "omul", "femeie", "femeia",
    "barbat", "barbatul", "coleg", "colega", "angajat", "angajatul",
    "profesor", "client", "clientul", "partener", "adversar", "autor",
    "autorul", "scriitor", "jucator", "vecin", "vecinul", "strain", "straina",
    "mama", "tata", "copil",
    "ami", "amie", "homme", "femme", "collegue", "partenaire",
    "auteur", "voisin", "inconnu", "lecteur", "locuteur", "dirigeant",
)
_PERSON_RE = re.compile(
    r"\b(?:" + "|".join(sorted({_fold(w) for w in PERSON_NOUNS})) + r")\b"
)
EXEMPT_CATS = {"honesty"}


def person_follows(before, after):
    """True if the match refers to a person (Unicode/diacritic safe).
    'honest broker' / 'his honest assessment' / 'un collègue honnête' -> allowed;
    'the honest answer is' / 'to be honest' -> not."""
    head = " ".join(_fold(w) for w in WORD_RE.findall(after)[:2])
    tail = " ".join(_fold(w) for w in WORD_RE.findall(before)[-2:])
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


def _keep_hit(hit, cats=None, min_sev=None):
    if cats and hit.get("cat") not in cats:
        return False
    if min_sev and SEV_RANK.get(hit.get("severity"), 0) < SEV_RANK.get(min_sev, 0):
        return False
    return True


def _lang_allowed(item_lang, target_lang):
    if not target_lang or target_lang == "all":
        return True
    il = (item_lang or "any").lower()
    if il == "any":
        return True
    return il == target_lang.lower()


EXEMPT_LOG = []


def scan(text, data, cats=None, min_sev=None, lang=None):
    hits = []
    del EXEMPT_LOG[:]
    spans = quote_spans(text)
    for item in data["phrases"]:
        if not _lang_allowed(item.get("lang"), lang):
            continue
        if not _keep_hit(item, cats, min_sev):
            continue
        for match in item["re"].finditer(text):
            if in_quotes(match.start(), spans):
                EXEMPT_LOG.append({"id": item["id"], "why": "quoted",
                                   "match": match.group(0)[:60]})
                continue
            before = text[max(0, match.start() - 45):match.start()]
            after = text[match.end():match.end() + 80]
            if item["cat"] in EXEMPT_CATS and person_follows(before, after):
                EXEMPT_LOG.append({"id": item["id"], "why": "person",
                                   "match": match.group(0)[:60]})
                continue
            markers = item.get("literal")
            if markers:
                b_raw = text[max(0, match.start() - 40):match.start()]
                a_raw = text[match.end():match.end() + 40]
                b_raw = re.split(r"[.!?:;\n]", b_raw)[-1]
                a_raw = re.split(r"[.!?:;\n]", a_raw)[0]
                w_before = " ".join(_fold(w) for w in WORD_RE.findall(b_raw)[-3:])
                w_after = " ".join(_fold(w) for w in WORD_RE.findall(a_raw)[:3])
                near = w_before + " " + w_after
                if any(re.search(r"\b" + re.escape(_fold(mk)) + r"\b", near) for mk in markers):
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
                    "after": after,
                    "before": before,
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


def mirrored_summary_notes(text, path):
    """Two or more sentences in one paragraph that open with a name-like
    'First Last' token plus a question verb = mirrored author summaries,
    even when they are not adjacent (e.g. 19 / 11 / 23 / 10 word shapes)."""
    notes = []
    for para in re.split(r"\n\s*\n", text):
        sents = _prose_sentences(para)
        hits = [
            s for s in sents
            if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+", s)
            and re.search(r"\b(?:asks?|asked|wonders?|examines?)\b", s)
        ]
        if len(hits) >= 2:
            notes.append({
                "id": "list.mirrored_summaries",
                "cat": "list",
                "severity": "medium",
                "label": "%d propozitii-sablon 'First Last asks...' in acelasi paragraf" % len(hits),
                "fix": "Sparge sablonul: organizeaza paragraful in jurul a ce explica fiecare in scena, variaza lungimea si forma.",
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


def run_fixtures(paths, data, as_json=False):
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
            row_lang = (row.get("lang") or "").strip().lower()
            target_lang = row_lang if row_lang in ("en", "ro", "fr") else None
            text = row.get("text") or ""
            hits = scan(text, data, lang=target_lang)
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
    verdict = "PASS" if (must_fail and must_pass and fire_rate >= 90 and clean_rate == 100) else "FAIL"
    if as_json:
        print(json.dumps({
            "must_fail": must_fail,
            "fired": fired,
            "must_pass": must_pass,
            "clean": clean,
            "fire_rate": round(fire_rate, 2),
            "clean_rate": round(clean_rate, 2),
            "problems": problems,
            "verdict": verdict,
        }, ensure_ascii=False, indent=2))
    else:
        print("fixtures: MUST-FAIL fired %d/%d (%.0f%%) | MUST-PASS clean %d/%d (%.0f%%)"
              % (fired, must_fail, fire_rate, clean, must_pass, clean_rate))
        for p in problems:
            print("  " + p)
        print("VERDICT: %s" % verdict)
    return verdict


def compute_verdict(by_sev):
    if by_sev.get("high", 0):
        return "FAIL"
    if by_sev.get("medium", 0):
        return "REVIEW"
    return "PASS"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--cat", help="comma separated categories")
    ap.add_argument("--severity", choices=["low", "medium", "high"])
    ap.add_argument("--lang", choices=["all", "en", "ro", "fr"], default="all",
                    help="scope language-specific rules (default: all)")
    ap.add_argument("--density", action="store_true", help="hits per 1000 words")
    ap.add_argument("--fail-on", choices=["high", "medium"],
                    help="exit 1 if verdict reaches this severity")
    ap.add_argument("--fixtures", nargs="+", help="trap corpus CSVs (lang,expect,exid,text)")
    args = ap.parse_args()

    data = load_list()

    if args.fixtures:
        verdict = run_fixtures(args.fixtures, data, as_json=args.json)
        sys.exit(0 if verdict == "PASS" else 1)
    if not args.paths:
        ap.error("give files/directories, or --fixtures <csv> [...]")

    cats = set(args.cat.split(",")) if args.cat else None

    all_hits = []
    total_words = 0
    exempt_count = 0
    person_exempt_count = 0
    for path in iter_files(args.paths):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                raw_text = fh.read()
        except OSError as exc:
            print("cannot read %s: %s" % (path, exc), file=sys.stderr)
            continue
        text = mask_non_prose(raw_text) if path.lower().endswith(".md") else raw_text
        total_words += len(WORD_RE.findall(text))
        for hit in scan(text, data, cats, args.severity, lang=args.lang):
            hit["file"] = path
            all_hits.append(hit)
        for ex in EXEMPT_LOG:
            if ex.get("why") == "person":
                person_exempt_count += 1
            else:
                exempt_count += 1
        extra = (
            structural_heuristics(text, path)
            + parallel_list_notes(text, path)
            + mirrored_summary_notes(text, path)
            + house_style_notes(text, path)
        )
        for note in extra:
            if args.lang in ("ro", "fr") and note["id"] in ("house.word_len", "house.long_words"):
                continue
            if not _keep_hit(note, cats, args.severity):
                continue
            note["file"] = path
            all_hits.append(note)

    by_cat = Counter(h["cat"] for h in all_hits)
    by_sev = Counter(h["severity"] for h in all_hits)
    verdict = compute_verdict(by_sev)

    if args.json:
        print(
            json.dumps(
                {
                    "hits": all_hits,
                    "by_category": dict(by_cat),
                    "by_severity": dict(by_sev),
                    "words": total_words,
                    "exempt": exempt_count + person_exempt_count,
                    "verdict": verdict,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif not all_hits:
        print("CLEAN — nicio expresie din listă găsită.")
        print("VERDICT: PASS")
    else:
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
        if person_exempt_count:
            print("allowed (referinta la o persoana): %d" % person_exempt_count)
        if exempt_count:
            print("allowed (citat sau literal): %d" % exempt_count)
        if args.density and total_words:
            print("density: %.2f hits / 1000 words (%d words)" % (1000.0 * len(all_hits) / total_words, total_words))
        print("VERDICT: %s" % verdict)

    if args.fail_on == "high" and verdict == "FAIL":
        sys.exit(1)
    if args.fail_on == "medium" and verdict in ("FAIL", "REVIEW"):
        sys.exit(1)


if __name__ == "__main__":
    main()
