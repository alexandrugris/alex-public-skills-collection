"""Static checker for a deliverable styled with AG Style v1.0.

Usage:
    python3 tests/check_styled.py <page|deck|draft>.<html|md> [--json]

For .html it resolves linked local stylesheets (including `tokens.css` and the
`TOKENS_PATH` placeholder) and enforces the mechanical parts of the quality bar:
paper ground, burgundy accent, Georgia display type, Inter uppercase labels,
weight-400 headings, 1px solid hairlines, no gradient type, no text shadows,
no emoji, no white backgrounds, no centred body copy, and no external CDN fonts.
For .md (a Marp deck) it enforces the deck recipe from SKILL.md.

Exit code 0 = the deliverable passes.
"""

import argparse
import json
import re
import sys
from pathlib import Path

PAPER = r"#fbfaf7"
BURGUNDY = r"#8d2829"
SKILL_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_TOKENS = SKILL_ROOT / "brand" / "references" / "tokens.css"

# True emoji blocks only (excludes U+2190-U+21FF typographic arrows like -> / <-).
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF\uFE0F]"
)
LINK_STYLESHEET_RE = re.compile(
    r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']|'
    r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']stylesheet["\']',
    re.IGNORECASE,
)


def has(text, pattern):
    return re.search(pattern, text, re.IGNORECASE) is not None


def load_effective_html(html_text, base_dir=None):
    """Return (html_text, combined_css) after resolving local stylesheet links."""
    css_parts = []
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", html_text, re.IGNORECASE | re.S):
        css_parts.append(m.group(1))
    for m in LINK_STYLESHEET_RE.finditer(html_text):
        href = (m.group(1) or m.group(2) or "").strip()
        if not href:
            continue
        if href == "TOKENS_PATH":
            if CANONICAL_TOKENS.is_file():
                css_parts.append(CANONICAL_TOKENS.read_text(encoding="utf-8"))
        elif not re.match(r"^(?:https?:)?//", href, re.IGNORECASE) and base_dir is not None:
            candidate = (base_dir / href).resolve()
            if candidate.is_file():
                css_parts.append(candidate.read_text(encoding="utf-8"))
    return html_text, "\n".join(css_parts)


def check_html(text, base_dir=None):
    problems = []
    html_text, css_text = load_effective_html(text, base_dir=base_dir)
    surface = css_text if css_text.strip() else html_text

    if not has(surface, r"--paper\s*:\s*" + PAPER) and not has(
        surface, r"background(?:-color)?\s*:\s*[^;}]*" + PAPER
    ):
        problems.append("no paper ground " + PAPER + " (as --paper or background)")

    if not has(surface, BURGUNDY):
        problems.append("no burgundy " + BURGUNDY + " anywhere (rules or accents)")

    if not has(surface, r"(?:font-family|--font-serif)\s*:\s*[^;}]*georgia"):
        problems.append("no Georgia in the display font stack")

    if not (has(surface, r"(?:font-family|--font-sans)\s*:\s*[^;}]*inter") and has(
        surface, r"text-transform\s*:\s*uppercase"
    )):
        problems.append("no uppercase Inter label pair (Inter + text-transform: uppercase)")

    for m in re.finditer(r"(h[1-6])[^{}]*\{([^}]*)\}", surface, re.IGNORECASE):
        if re.search(r"font-weight\s*:\s*(?:bold|[6-9]00)", m.group(2), re.IGNORECASE):
            problems.append(m.group(1).lower() + " rule uses a heavy font-weight (bar: 400)")

    if re.search(r"border[^;}]*\bdashed\b", surface, re.IGNORECASE) or re.search(
        r"border[^;}]*\bdouble\b", surface, re.IGNORECASE
    ):
        problems.append("dashed or double border (hairlines are 1px solid)")

    if re.search(r"(?:-webkit-)?background-clip\s*:\s*text", surface, re.IGNORECASE):
        problems.append("gradient type (background-clip: text)")

    if re.search(r"text-shadow\s*:\s*(?!none\b)", surface, re.IGNORECASE):
        problems.append("text shadow on type")

    if re.search(r"background(?:-color)?\s*:\s*[^;}]*#fff(?:fff|f)?\b", surface, re.IGNORECASE) or re.search(
        r"background(?:-color)?\s*:\s*white\b", surface, re.IGNORECASE
    ):
        problems.append("white surface background (paper is " + PAPER + ", never white)")

    if re.search(r"(?:body|main|article)[^{}]*\{[^}]*text-align\s*:\s*center", surface, re.IGNORECASE):
        problems.append("centred body copy (body copy is left-aligned, ragged right)")

    if re.search(r"fonts\.googleapis\.com|fonts\.gstatic\.com|cdn\.jsdelivr\.net", html_text, re.IGNORECASE):
        problems.append("external CDN font or asset dependency (deliverables must be self-contained)")

    em = EMOJI.findall(html_text)
    if em:
        problems.append("emoji found: " + " ".join(sorted(set(em))))
    return problems


def check_marp(text):
    problems = []
    if not has(text, r"size:\s*16:9"):
        problems.append("no 16:9 size directive")
    if not has(text, r"paginate:\s*true"):
        problems.append("no paginate directive")
    if not has(text, r"background(?:-color)?\s*:\s*" + PAPER):
        problems.append("section background is not paper " + PAPER)
    if has(text, r"background(?:-color)?\s*:\s*(?:#fff(?:fff)?\b|white\b)"):
        problems.append("white surface background (paper is " + PAPER + ", never white)")
    if not has(text, r"georgia"):
        problems.append("no Georgia in the section font-family")
    if not has(text, BURGUNDY):
        problems.append("no burgundy " + BURGUNDY + " spine or accent")
    # Check <= 6 bullets per slide
    slides = re.split(r"(?m)^\s*---\s*$", text)
    for idx, slide in enumerate(slides, 1):
        bullets = re.findall(r"(?m)^\s*[-*]\s+\S", slide)
        if len(bullets) > 6:
            problems.append("slide %d has %d bullets (max 6)" % (idx, len(bullets)))
    em = EMOJI.findall(text)
    if em:
        problems.append("emoji found: " + " ".join(sorted(set(em))))
    return problems


def main():
    ap = argparse.ArgumentParser(description="Static checker for AG Style v1.0 deliverables.")
    ap.add_argument("target", help="path to .html or Marp .md deliverable")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()

    p = Path(args.target)
    if not p.is_file():
        print("no such file: %s" % p)
        sys.exit(2)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".html":
        problems = check_html(text, base_dir=p.parent)
    elif p.suffix.lower() == ".md":
        problems = check_marp(text)
    else:
        print("unsupported type: %s (expected .html or .md)" % p.suffix)
        sys.exit(2)

    verdict = "FAIL" if problems else "PASS"
    if args.json:
        print(json.dumps({
            "file": str(p),
            "verdict": verdict,
            "problems": problems,
        }, ensure_ascii=False, indent=2))
        sys.exit(1 if problems else 0)

    for pr in problems:
        print("FAIL " + pr)
    if problems:
        print("VERDICT: FAIL (%d finding%s)" % (len(problems), "" if len(problems) == 1 else "s"))
        sys.exit(1)
    print("VERDICT: PASS")


if __name__ == "__main__":
    main()
