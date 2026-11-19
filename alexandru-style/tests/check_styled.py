"""Static checker for a deliverable styled with AG Style v1.0.

Usage:
    python3 tests/check_styled.py <page|deck|draft>.<html|md>

For .html it enforces the mechanical parts of the quality bar: paper ground,
burgundy accent, Georgia display type, Inter uppercase labels, weight-400 headings,
1px solid hairlines, no gradient type, no text shadows, no emoji, no white
backgrounds, no centred body copy.
For .md (a Marp deck) it enforces the deck recipe from SKILL.md.

Exit code 0 = the deliverable passes.
"""

import re
import sys
from pathlib import Path

PAPER = r"#fbfaf7"
BURGUNDY = r"#8d2829"
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2190-\u21FF\u2700-\u27BF]"
)


def has(text, pattern):
    return re.search(pattern, text, re.IGNORECASE) is not None


def check_html(text):
    problems = []

    if not has(text, r"--paper:\s*" + PAPER) and not has(
        text, r"background(?:-color)?\s*:\s*[^;}]*" + PAPER
    ):
        problems.append("no paper ground " + PAPER + " (as --paper or background)")

    if not has(text, BURGUNDY):
        problems.append("no burgundy " + BURGUNDY + " anywhere (rules or accents)")

    if not has(text, r"font-family:\s*[^;}]*georgia"):
        problems.append("no Georgia in the display font stack")

    if not (has(text, r"font-family:\s*[^;}]*inter") and has(
        text, r"text-transform:\s*uppercase"
    )):
        problems.append("no uppercase Inter label pair (Inter + text-transform: uppercase)")

    for m in re.finditer(r"(h[1-6])[^{}]*\{([^}]*)\}", text):
        if re.search(r"font-weight:\s*(?:bold|[6-9]00)", m.group(2)):
            problems.append(m.group(1) + " rule uses a heavy font-weight (bar: 400)")

    if re.search(r"border[^;}]*dashed", text) or re.search(r"border[^;}]*double", text):
        problems.append("dashed or double border (hairlines are 1px solid)")

    if re.search(r"background-clip:\s*text", text, re.IGNORECASE) or re.search(
        r"-webkit-background-clip:\s*text", text
    ):
        problems.append("gradient type (background-clip: text)")

    if re.search(r"text-shadow\s*:\s*(?!none)", text):
        problems.append("text shadow on type")

    if re.search(r"background(?:-color)?\s*:\s*[^;}]*#fff(?:fff|f)?\b", text) or re.search(
        r"background(?:-color)?\s*:\s*white\b", text
    ):
        problems.append("white surface background (paper is " + PAPER + ", never white)")

    if re.search(r"(?:body|main|article)[^{}]*\{[^}]*text-align:\s*center", text):
        problems.append("centred body copy (body copy is left-aligned, ragged right)")

    em = EMOJI.findall(text)
    if em:
        problems.append("emoji found: " + " ".join(sorted(set(em))))
    return problems


def check_marp(text):
    problems = []
    if not has(text, r"size:\s*16:9"):
        problems.append("no 16:9 size directive")
    if not has(text, r"paginate:\s*true"):
        problems.append("no paginate directive")
    if not has(text, r"background(?:-color)?:\s*" + PAPER):
        problems.append("section background is not paper " + PAPER)
    if not has(text, r"georgia"):
        problems.append("no Georgia in the section font-family")
    if not has(text, BURGUNDY):
        problems.append("no burgundy " + BURGUNDY + " spine or accent")
    em = EMOJI.findall(text)
    if em:
        problems.append("emoji found: " + " ".join(sorted(set(em))))
    return problems


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    p = Path(sys.argv[1])
    if not p.is_file():
        print("no such file: %s" % p)
        sys.exit(2)
    text = p.read_text(encoding="utf-8")
    if p.suffix == ".html":
        problems = check_html(text)
    elif p.suffix == ".md":
        problems = check_marp(text)
    else:
        print("unsupported type: %s (expected .html or .md)" % p.suffix)
        sys.exit(2)
    for pr in problems:
        print("FAIL " + pr)
    if problems:
        print("VERDICT: FAIL (%d finding%s)" % (len(problems), "" if len(problems) == 1 else "s"))
        sys.exit(1)
    print("VERDICT: PASS")


if __name__ == "__main__":
    main()
