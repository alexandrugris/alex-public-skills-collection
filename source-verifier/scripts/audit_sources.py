#!/usr/bin/env python3
"""Deterministic source, citation, DOI, and quotation pre-auditor.

Runs offline by default using Python stdlib only. Pass --online to resolve
doi.org links against the Crossref API when outbound HTTPS is permitted.

Exit codes:
  0 = PASS (zero mechanical blocking issues)
  1 = FAIL (one or more mechanical blocking issues)
  2 = usage / I/O error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://(?:[^()\s]+|\([^()\s]*\))+)\)")
SOURCES_HDR_RE = re.compile(r"(?m)^##\s+Sources\s*$")
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
DUAL_YEAR_RE = re.compile(r"\((19\d{2}|20\d{2})\s*/\s*(19\d{2}|20\d{2})\)")
ACRONYM_AUTHOR_RE = re.compile(r"^([A-Z]{2,8})\s*\((19\d{2}|20\d{2})\)")
DOI_URL_RE = re.compile(r"^https?://(?:dx\.)?doi\.org/(.+)$", re.I)
VALID_DOI_RE = re.compile(r"^10\.\d{4,9}/[^\s\"<>]+$")
QUOTE_RE = re.compile(
    r'"([^"\n]{2,300})"'
    r'|“([^”\n]{2,300})”'
    r'|„([^”"“\n]{2,300})[”"“]'
    r'|«\s*([^»\n]{2,300}?)\s*»'
)
WORD_RE = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*", re.UNICODE)
STUDY_LABEL_RE = re.compile(r"\b(study|paper|article|research|monograph|working paper)\b", re.I)
FENCE_RE = re.compile(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n.*?\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)

PLACEHOLDER_HOSTS = ("example.com", "example.org", "example.net", ".invalid", "localhost")
SECONDARY_WRAPPER_HOSTS = (
    "asqblog.com",
    "medium.com",
    "substack.com",
    "wikipedia.org",
    "youtube.com",
    "youtu.be",
    "podcasts.apple.com",
    "open.spotify.com",
)
INSTITUTIONAL_AUTHORS = {
    "ACM", "AMA", "APA", "BIS", "CDC", "CERN", "CISA", "ECB", "EPA", "ESA",
    "EU", "FDA", "FED", "IEEE", "IETF", "ILO", "IMF", "ISO", "NASA", "NATO",
    "NIST", "NSA", "OECD", "OWASP", "UN", "UNESCO", "UNICEF", "W3C", "WEF",
    "WHO", "WTO",
}


def _blank_preserve_lines(match: re.Match) -> str:
    return "".join("\n" if ch == "\n" else " " for ch in match.group(0))


def mask_code(text: str) -> str:
    """Blank fenced and inline code blocks while keeping 1-indexed line numbers intact."""
    masked = FENCE_RE.sub(_blank_preserve_lines, text)
    return INLINE_CODE_RE.sub(_blank_preserve_lines, masked)


def strip_frontmatter(text: str) -> tuple[str, int]:
    """Strip leading YAML frontmatter, returning (remaining_text, skipped_line_count)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text, 0
    prefix = m.group(0)
    return text[m.end() :], prefix.count("\n")


def normalize_url(url: str) -> str:
    """Normalize equivalent URLs (http/https, dx.doi.org/doi.org, trailing slash) for matching."""
    raw = url.strip().rstrip(".,;:")
    parts = urllib.parse.urlsplit(raw)
    scheme = "https" if parts.scheme.lower() in ("http", "https") else parts.scheme.lower()
    netloc = parts.netloc.lower()
    if netloc == "dx.doi.org":
        netloc = "doi.org"
    path = parts.path.rstrip("/") if parts.path and parts.path != "/" else parts.path
    return urllib.parse.urlunsplit((scheme, netloc, path, parts.query, parts.fragment))


def split_body_and_sources(text: str) -> tuple[str, str, int]:
    """Return (body_text, sources_text, sources_start_line_1indexed)."""
    m = SOURCES_HDR_RE.search(text)
    if not m:
        return text, "", -1
    body = text[: m.start()]
    sources = text[m.end() :]
    start_line = text[: m.start()].count("\n") + 1
    return body, sources, start_line


def find_opening_paragraph_lines(body: str) -> set[int]:
    """Return 1-indexed line numbers belonging to the opening narrative paragraph."""
    cleaned, offset = strip_frontmatter(body)
    lines = cleaned.splitlines()
    opening: set[int] = set()
    in_opening = False
    for idx, raw in enumerate(lines, start=offset + 1):
        s = raw.strip()
        if not s:
            if in_opening:
                break
            continue
        if s.startswith("#") or s == "---":
            if in_opening:
                break
            continue
        if not in_opening and s.startswith("*") and s.endswith("*") and len(s) > 2:
            continue
        in_opening = True
        opening.add(idx)
    return opening


def parse_sources(sources_text: str, start_line: int) -> list[dict]:
    entries = []
    if start_line < 0:
        return entries
    for offset, raw in enumerate(sources_text.splitlines(), start=1):
        line_no = start_line + offset
        s = raw.strip()
        if not s.startswith("- "):
            continue
        m = INLINE_LINK_RE.search(s)
        if not m:
            continue
        label, url = m.group(1).strip(), m.group(2).strip()
        doi_m = DOI_URL_RE.match(url)
        doi = doi_m.group(1) if doi_m else None
        years = YEAR_RE.findall(label)
        entries.append(
            {
                "line": line_no,
                "label": label,
                "url": url,
                "normalized_url": normalize_url(url),
                "doi": doi,
                "years": years,
            }
        )
    return entries


def parse_inline_links(body: str) -> list[dict]:
    links = []
    masked = mask_code(body)
    for line_no, raw in enumerate(masked.splitlines(), start=1):
        for m in INLINE_LINK_RE.finditer(raw):
            label, url = m.group(1).strip(), m.group(2).strip()
            after = raw[m.end() : m.end() + 45]
            paren_years = []
            pm = re.match(r"\s*\(([^)]{1,40})\)", after)
            if pm:
                paren_years = YEAR_RE.findall(pm.group(1))
            label_years = YEAR_RE.findall(label)
            links.append(
                {
                    "line": line_no,
                    "label": label,
                    "url": url,
                    "normalized_url": normalize_url(url),
                    "years": label_years or paren_years,
                }
            )
    return links


def extract_quotes(body: str) -> list[dict]:
    opening_lines = find_opening_paragraph_lines(body)
    cleaned, offset = strip_frontmatter(body)
    masked = mask_code(cleaned)
    quotes = []
    for line_no, raw in enumerate(masked.splitlines(), start=offset + 1):
        if raw.strip().startswith("#"):
            continue
        for m in QUOTE_RE.finditer(raw):
            q = next((g for g in m.groups() if g is not None), "").strip()
            words = WORD_RE.findall(q)
            quotes.append(
                {
                    "line": line_no,
                    "text": q,
                    "word_count": len(words),
                    "in_opening_scene": line_no in opening_lines,
                    "needs_verbatim_check": (len(words) >= 3 and line_no not in opening_lines),
                }
            )
    return quotes


def normalize_name(text: str) -> str:
    """Fold diacritics and curly apostrophes/dashes for Crossref author matching."""
    folded = unicodedata.normalize("NFKD", text)
    ascii_ish = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return ascii_ish.replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-").lower()


def extract_crossref_years(msg: dict) -> list[str]:
    """Collect valid publication years from Crossref print, online, and issued date fields."""
    years: list[str] = []
    for field in ("published-print", "published-online", "issued", "published"):
        parts = msg.get(field, {}).get("date-parts", [])
        if parts and parts[0] and parts[0][0]:
            y = str(parts[0][0])
            if y not in years:
                years.append(y)
    return years


def query_crossref(doi: str, timeout: float = 8.0) -> tuple[dict | None, str | None]:
    """Query Crossref API for canonical DOI metadata. Returns (message_dict, error_code)."""
    encoded = urllib.parse.quote(doi, safe="/")
    url = f"https://api.crossref.org/works/{encoded}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "alex-public-skills-source-verifier/1.0 (mailto:noreply@example.org)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
            return payload.get("message"), None
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None, "dead_doi"
        return None, f"http_{exc.code}"
    except Exception:
        return None, "crossref_unreachable"


def audit_markdown(text: str, online: bool = False) -> dict:
    body, sources_text, sources_start = split_body_and_sources(text)
    sources = parse_sources(sources_text, sources_start)
    inline_links = parse_inline_links(body)
    quotes = extract_quotes(body)

    blocking: list[dict] = []
    warnings: list[dict] = []
    crossref_records: list[dict] = []

    sources_by_url = {s["normalized_url"]: s for s in sources}

    if inline_links and sources_start < 0:
        blocking.append(
            {
                "code": "BIB_MISMATCH",
                "rule": "missing_sources_section",
                "line": 1,
                "detail": "Draft contains inline URLs but no `## Sources` section.",
            }
        )

    # Check inline links
    for lnk in inline_links:
        url = lnk["url"]
        norm_url = lnk["normalized_url"]
        host = urllib.parse.urlparse(url).netloc.lower()
        if any(ph in host for ph in PLACEHOLDER_HOSTS) or "TODO" in url or "TBD" in url:
            blocking.append(
                {
                    "code": "BIB_MISMATCH",
                    "rule": "placeholder_url",
                    "line": lnk["line"],
                    "detail": f"Placeholder or invalid URL: {url}",
                }
            )
        if sources_start >= 0 and norm_url not in sources_by_url:
            blocking.append(
                {
                    "code": "BIB_MISMATCH",
                    "rule": "inline_url_missing_from_sources",
                    "line": lnk["line"],
                    "detail": f"Inline URL missing from `## Sources`: {url}",
                }
            )
        if STUDY_LABEL_RE.search(lnk["label"]) and any(w in host for w in SECONDARY_WRAPPER_HOSTS):
            blocking.append(
                {
                    "code": "BIB_MISMATCH",
                    "rule": "secondary_source_as_study",
                    "line": lnk["line"],
                    "detail": f"Inline label {lnk['label']!r} claims a study/paper but links to secondary/wrapper host {host} ({url}).",
                }
            )
        if norm_url in sources_by_url and lnk["years"]:
            src = sources_by_url[norm_url]
            if src["years"]:
                missing_years = [y for y in lnk["years"] if y not in src["years"]]
                if missing_years:
                    blocking.append(
                        {
                            "code": "BIB_MISMATCH",
                            "rule": "inline_source_year_mismatch",
                            "line": lnk["line"],
                            "detail": f"Inline year(s) {missing_years} for {url} do not match `## Sources` year(s) {src['years']}.",
                        }
                    )

    # Check ## Sources entries
    for src in sources:
        label = src["label"]
        url = src["url"]
        host = urllib.parse.urlparse(url).netloc.lower()
        if any(ph in host for ph in PLACEHOLDER_HOSTS):
            blocking.append(
                {
                    "code": "BIB_MISMATCH",
                    "rule": "placeholder_url",
                    "line": src["line"],
                    "detail": f"Placeholder URL in `## Sources`: {url}",
                }
            )
        if DUAL_YEAR_RE.search(label):
            blocking.append(
                {
                    "code": "BIB_MISMATCH",
                    "rule": "dual_year_conflation",
                    "line": src["line"],
                    "detail": f"Dual-year conflation in `## Sources` ({label!r}); cite the exact edition/publication year.",
                }
            )
        acr_m = ACRONYM_AUTHOR_RE.match(label)
        if acr_m and acr_m.group(1) not in INSTITUTIONAL_AUTHORS:
            blocking.append(
                {
                    "code": "BIB_MISMATCH",
                    "rule": "missing_author_in_sources",
                    "line": src["line"],
                    "detail": f"Entry begins with venue acronym instead of author surname: {label!r}.",
                }
            )
        if src["doi"] is not None:
            doi = src["doi"]
            if not VALID_DOI_RE.match(doi) or doi.endswith((".", ",", ";")):
                blocking.append(
                    {
                        "code": "BIB_MISMATCH",
                        "rule": "malformed_doi",
                        "line": src["line"],
                        "detail": f"Malformed DOI syntax: {doi!r}",
                    }
                )
            elif online:
                msg, err = query_crossref(doi)
                if err == "dead_doi":
                    blocking.append(
                        {
                            "code": "BIB_MISMATCH",
                            "rule": "dead_doi",
                            "line": src["line"],
                            "detail": f"Crossref returned 404 for DOI {doi}.",
                        }
                    )
                elif err:
                    warnings.append({"rule": err, "line": src["line"], "doi": doi})
                elif msg:
                    authors = [a.get("family", "") for a in msg.get("author", []) if a.get("family")]
                    cr_years = extract_crossref_years(msg)
                    title = (msg.get("title") or [""])[0]
                    container = (msg.get("container-title") or [""])[0]
                    crossref_records.append(
                        {
                            "line": src["line"],
                            "doi": doi,
                            "authors": authors,
                            "year": cr_years[0] if cr_years else None,
                            "years": cr_years,
                            "title": title,
                            "container": container,
                        }
                    )
                    if authors and normalize_name(authors[0]) not in normalize_name(label):
                        blocking.append(
                            {
                                "code": "BIB_MISMATCH",
                                "rule": "crossref_author_mismatch",
                                "line": src["line"],
                                "detail": f"Crossref lead author {authors[0]!r} not found in `## Sources` label {label!r}.",
                            }
                        )
                    if cr_years and src["years"] and not any(y in cr_years for y in src["years"]):
                        blocking.append(
                            {
                                "code": "BIB_MISMATCH",
                                "rule": "crossref_year_mismatch",
                                "line": src["line"],
                                "detail": f"Crossref year(s) {cr_years} do not match `## Sources` years {src['years']} for {doi}.",
                            }
                        )

    verdict = "FAIL" if blocking else "PASS"
    return {
        "verdict": verdict,
        "blocking": blocking,
        "warnings": warnings,
        "counts": {
            "inline_links": len(inline_links),
            "sources": len(sources),
            "quotes_total": len(quotes),
            "quotes_needing_verbatim_check": sum(1 for q in quotes if q["needs_verbatim_check"]),
            "blocking": len(blocking),
            "warnings": len(warnings),
        },
        "quotes_to_verify": [q for q in quotes if q["needs_verbatim_check"]],
        "sources": sources,
        "crossref_records": crossref_records,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-audit Markdown citations, DOIs, and quotes.")
    ap.add_argument("draft", help="Path to Markdown draft")
    ap.add_argument("--online", action="store_true", help="Verify doi.org entries against Crossref API")
    ap.add_argument("--json", action="store_true", help="Output JSON report")
    args = ap.parse_args()

    p = Path(args.draft)
    if not p.is_file():
        print(f"File not found: {p}", file=sys.stderr)
        return 2

    res = audit_markdown(p.read_text(encoding="utf-8"), online=args.online)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        for item in res["blocking"]:
            print(f"FAIL {item['code']} [{item['rule']}] L{item['line']}: {item['detail']}")
        for w in res["warnings"]:
            print(f"WARN [{w['rule']}] L{w['line']}: {w.get('doi', '')}")
        c = res["counts"]
        print(
            f"VERDICT: {res['verdict']} "
            f"(blocking={c['blocking']}, sources={c['sources']}, quotes_to_verify={c['quotes_needing_verbatim_check']})"
        )
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
