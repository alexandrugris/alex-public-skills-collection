#!/usr/bin/env python3
"""Build the AG-style sample deck (16:9 PPTX).

Every slide is drawn from primitives — no template, no placeholders — so the
palette, type scale and motifs stay identical to the web and document
mediums. Run:

    python3 build_deck.py [output.pptx]
"""
from __future__ import annotations

import pathlib
import re
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

# ---------------------------------------------------------------- tokens ----
_CSS = (pathlib.Path(__file__).resolve().parent.parent / "references/tokens.css").read_text()
def color(name):
    match = re.search(r"--" + name + r"\s*:\s*#([0-9A-Fa-f]{6})", _CSS)
    if not match:
        raise ValueError(f"Missing CSS token: {name}")
    return RGBColor.from_string(match.group(1))
PAPER       = color("paper")
PAPER_WARM  = color("paper-warm")
PAPER_ALT   = color("paper-alt")
INK         = color("ink")
INK_DEEP    = color("ink-deep")
INK_SOFT    = color("ink-soft")
MUTED       = color("muted")
MUTED_LIGHT = color("muted-light")
MUTED_FAINT = color("muted-faint")
RULE        = color("rule")
RULE_STRONG = color("rule-strong")
BURGUNDY    = color("burgundy")
GREEN       = color("green")

SERIF = "Georgia"
SANS  = "Inter"

SW, SH = 13.333, 7.5          # slide size, inches
L, R   = 0.95, 0.95           # outer margins
CW     = SW - L - R           # content width


# --------------------------------------------------------------- helpers ----
def set_spacing(run, pts: float) -> None:
    """Letter-spacing (not exposed by python-pptx)."""
    run.font._rPr.set("spc", str(int(pts * 100)))


def _flat(sh):
    """Drop the theme style reference: no inherited shadow, line or fill."""
    st = sh._element.find(qn("p:style"))
    if st is not None:
        sh._element.remove(st)
    sh.shadow.inherit = False
    return sh


def rect(slide, x, y, w, h, color):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    return _flat(sh)


def hline(slide, x, y, w, color=RULE, pt=0.75):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Pt(pt))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    return _flat(sh)


def vline(slide, x, y, h, color=BURGUNDY, pt=3.0):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Pt(pt), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    return _flat(sh)


def text(slide, x, y, w, h, blocks, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """blocks: list of dicts {text, font, size, color, bold, italic, spacing,
    line_spacing, space_before, space_after, caps}."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    for i, b in enumerate(blocks):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if b.get("line_spacing"):
            p.line_spacing = b["line_spacing"]
        if b.get("space_before"):
            p.space_before = Pt(b["space_before"])
        if b.get("space_after"):
            p.space_after = Pt(b["space_after"])
        run = p.add_run()
        run.text = b["text"].upper() if b.get("caps") else b["text"]
        f = run.font
        f.name = b.get("font", SERIF)
        f.size = Pt(b.get("size", 14))
        f.bold = b.get("bold", False)
        f.italic = b.get("italic", False)
        f.color.rgb = b.get("color", INK)
        if b.get("spacing"):
            set_spacing(run, b["spacing"])
    return box


def base_slide(prs, ground=PAPER, spine=True):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = ground
    if spine:
        rect(s, 0, 0, SW, 0.055, BURGUNDY)
    return s


def head(slide, kicker, title, note=None):
    """Standard content-slide header: kicker, serif title, hairline."""
    text(slide, L, 0.62, CW, 0.3,
         [{"text": kicker, "font": SANS, "size": 11, "color": BURGUNDY,
           "bold": True, "spacing": 1.4, "caps": True}])
    text(slide, L, 0.95, CW * 0.75, 0.7,
         [{"text": title, "font": SERIF, "size": 31, "color": INK_DEEP,
           "line_spacing": 1.0}])
    if note:
        text(slide, L + CW * 0.62, 1.06, CW * 0.38, 0.3,
             [{"text": note, "font": SANS, "size": 11, "color": MUTED_LIGHT,
               "spacing": 1.0, "caps": True}], align=PP_ALIGN.RIGHT)
    hline(slide, L, 1.72, CW)


def foot(slide, n):
    text(slide, L, 6.88, CW * 0.6, 0.3,
         [{"text": "From The Trenches — Alexandru Gris", "font": SANS, "size": 9,
           "color": MUTED_LIGHT, "spacing": 1.3, "caps": True}])
    text(slide, L + CW * 0.6, 6.88, CW * 0.4, 0.3,
         [{"text": str(n), "font": SANS, "size": 9, "color": BURGUNDY,
           "spacing": 1.3}], align=PP_ALIGN.RIGHT)


# ----------------------------------------------------------------- build ----
def build(path: pathlib.Path) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)

    # ---------------------------------------------------------- 1. title ---
    s = base_slide(prs, spine=False)
    rect(s, 0, 0, 0.28, SH, BURGUNDY)
    text(s, 1.35, 1.45, 9.0, 0.3,
         [{"text": "From The Trenches · Since 2008", "font": SANS, "size": 12,
           "color": BURGUNDY, "bold": True, "spacing": 1.8, "caps": True}])
    text(s, 1.35, 2.0, 10.2, 2.4,
         [{"text": "Technology, teams,\nand the long view.", "font": SERIF,
           "size": 58, "color": INK_DEEP, "line_spacing": 0.98}])
    hline(s, 1.35, 4.62, 4.2, RULE_STRONG)
    text(s, 1.35, 4.92, 8.6, 1.0,
         [{"text": "I build technology and lead teams. I write to understand — from "
                   "software, data, and organizations to judgment, progress, and the "
                   "human questions underneath.",
           "font": SERIF, "size": 17, "color": INK_SOFT, "line_spacing": 1.45}])
    text(s, 1.35, 6.35, 8.0, 0.4,
         [{"text": "Alexandru Gris · Engineering Leader · Munich", "font": SANS,
           "size": 11, "color": GREEN, "spacing": 1.5, "caps": True}])

    # ------------------------------------------------------- 2. manifesto ---
    s = base_slide(prs)
    text(s, L, 1.45, 10.6, 3.9,
         [{"text": "This is where I keep the ideas that survive the work: technical "
                   "experiments, leadership lessons, unfinished questions, and the "
                   "occasional reflection on being human.",
           "font": SERIF, "size": 37, "color": INK_DEEP, "line_spacing": 1.14}])
    hline(s, L, 5.42, 3.2, BURGUNDY, 2.0)
    text(s, L, 5.74, 9.0, 0.9,
         [{"text": "Engineering leadership, technical writing and creative work — "
                   "built and published as separate sites, from the same trunk.",
           "font": SANS, "size": 13, "color": MUTED, "line_spacing": 1.5}])
    foot(s, 2)

    # ------------------------------------------------------ 3. principles ---
    s = base_slide(prs)
    head(s, "Ideas I try to work by", "Principles", "Management · 2025")
    items = [
        ("01", "Disagree — and then commit.",
         "Open disagreement is the cheapest quality control there is. Once the call is made, the team moves as one."),
        ("02", "Authority is not an argument.",
         "Seniority decides who is accountable, not who is right. Bring evidence and expect it weighed the same way."),
        ("03", "Move fast, focused, and deep.",
         "Speed without focus is churn. Speed with depth compounds: the team gets faster at what it already knows."),
        ("04", "Measure learning and process.",
         "Output metrics reward the wrong behaviour. Measure how the team learns and how the work flows."),
    ]
    gap, n = 0.34, 4
    colw = (CW - gap * (n - 1)) / n
    for i, (num, title, desc) in enumerate(items):
        x = L + i * (colw + gap)
        hline(s, x, 2.45, colw, BURGUNDY, 2.0)
        text(s, x, 2.65, colw, 0.3,
             [{"text": num, "font": SANS, "size": 12, "color": MUTED_FAINT, "spacing": 0.6}])
        text(s, x, 3.02, colw, 1.1,
             [{"text": title, "font": SERIF, "size": 20, "color": INK_DEEP, "line_spacing": 1.12}])
        text(s, x, 4.35, colw, 1.6,
             [{"text": desc, "font": SANS, "size": 11.5, "color": MUTED, "line_spacing": 1.5}])
    foot(s, 3)

    # -------------------------------------------------------- 4. writings ---
    s = base_slide(prs)
    head(s, "Selected work", "Writings", "Creative · Management · Technical")
    works = [
        (True,  "Creative Writing · 2024–2026", "Media Projects",
         "The history, the diptych, and the three illustrated works — each built and published as its own site."),
        (False, "Management · 2025", "Some Leadership Principles",
         "Open disagreement, intellectual curiosity, depth of understanding, and honest learning."),
        (False, "Technical writing · 2022", "Timeseries Analysis with PyTorch",
         "A practical experiment in forecasting, written to learn by building."),
    ]
    gap = 0.5
    widths = [3.85, 3.29, 3.29]
    x = L
    for (feat, meta, title, desc), w in zip(works, widths):
        hline(s, x, 2.15, w, BURGUNDY if feat else RULE_STRONG, 3.0 if feat else 0.75)
        text(s, x, 2.42, w, 0.3,
             [{"text": meta, "font": SANS, "size": 10, "color": BURGUNDY,
               "bold": True, "spacing": 1.1, "caps": True}])
        text(s, x, 2.82, w, 1.0,
             [{"text": title, "font": SERIF, "size": 24, "color": INK_DEEP, "line_spacing": 1.08}])
        text(s, x, 4.05, w, 1.4,
             [{"text": desc, "font": SANS, "size": 12, "color": MUTED, "line_spacing": 1.55}])
        text(s, x, 5.5, w, 0.3,
             [{"text": "Open", "font": SANS, "size": 10, "color": MUTED_LIGHT,
               "bold": True, "spacing": 1.4, "caps": True}])
        x += w + gap
    foot(s, 4)

    # ----------------------------------------------------------- 5. chart ---
    s = base_slide(prs)
    head(s, "Observation", "Where the time goes", "Illustrative")
    rows = [("Feature work", 42, False), ("Review & rework", 21, False),
            ("Maintenance & ops", 17, False), ("Meetings & status", 12, False),
            ("Learning & exploration", 8, True)]
    bar_x, bar_max, scale = 4.15, 7.0, 7.0 / 50.0
    y0, step = 2.55, 0.78
    for i, (label, val, accent) in enumerate(rows):
        y = y0 + i * step
        text(s, L, y - 0.05, 3.0, 0.35,
             [{"text": label, "font": SERIF, "size": 15, "color": INK_DEEP}])
        rect(s, bar_x, y - 0.02, val * scale, 0.22, BURGUNDY if accent else MUTED_FAINT)
        text(s, bar_x + bar_max + 0.25, y - 0.03, 1.0, 0.35,
             [{"text": f"{val}%", "font": SANS, "size": 12,
               "color": BURGUNDY if accent else MUTED}])
    hline(s, bar_x, y0 + 4 * step + 0.36, bar_max)
    text(s, bar_x, y0 + 4 * step + 0.46, 1.0, 0.3,
         [{"text": "0%", "font": SANS, "size": 9, "color": MUTED_LIGHT, "spacing": 0.6}])
    text(s, bar_x + bar_max - 1.0, y0 + 4 * step + 0.46, 1.0, 0.3,
         [{"text": "50%", "font": SANS, "size": 9, "color": MUTED_LIGHT, "spacing": 0.6}],
         align=PP_ALIGN.RIGHT)
    text(s, L, 6.28, 8.6, 0.4,
         [{"text": "The bottom of the distribution is the slice that keeps a team "
                   "from merely repeating itself.",
           "font": SANS, "size": 12.5, "color": MUTED}])
    foot(s, 5)

    # ----------------------------------------------------------- 6. quote ---
    s = base_slide(prs, ground=PAPER_WARM)
    vline(s, L, 2.22, 1.62, BURGUNDY, 4.0)
    text(s, L + 0.45, 2.12, 10.4, 2.6,
         [{"text": "The work that matters is the work that is still true in two years.",
           "font": SERIF, "size": 40, "color": INK_DEEP, "italic": True, "line_spacing": 1.12}])
    text(s, L + 0.45, 5.15, 8.0, 0.4,
         [{"text": "Notes from a review · 2024", "font": SANS, "size": 11,
           "color": MUTED_LIGHT, "spacing": 1.3, "caps": True}])
    foot(s, 6)

    # ---------------------------------------------------- 7. disagreement ---
    s = base_slide(prs)
    head(s, "Practice", "Disagree — and then commit", "Culture")
    text(s, L, 2.35, 4.3, 2.4,
         [{"text": "Most teams do not fail from too little disagreement. They fail from "
                   "disagreement that leaks — into hallways, into status meetings, into "
                   "late-night pull requests nobody wanted to write.",
           "font": SERIF, "size": 15, "color": INK_SOFT, "line_spacing": 1.55}])
    text(s, L, 4.6, 4.3, 1.2,
         [{"text": "The fix is not more harmony. It is a container for the argument.",
           "font": SERIF, "size": 15, "color": INK_DEEP, "italic": True, "line_spacing": 1.5}])
    pts = [("01", "Separate the person from the position",
            "Say what the evidence is, and say what would change your mind."),
           ("02", "Argue about the work, not the rank",
            "Authority decides who is accountable, not who is correct."),
           ("03", "Commit in public, once",
            "Reopen the decision when new evidence appears — not because someone lost.")]
    x, y0 = 6.0, 2.35
    for num, title, desc in pts:
        hline(s, x, y0, 5.7, RULE)
        text(s, x, y0 + 0.2, 0.8, 0.3,
             [{"text": num, "font": SANS, "size": 11, "color": MUTED_FAINT, "spacing": 0.6}])
        text(s, x + 0.95, y0 + 0.15, 4.7, 0.4,
             [{"text": title, "font": SERIF, "size": 18, "color": INK_DEEP}])
        text(s, x + 0.95, y0 + 0.6, 4.7, 0.9,
             [{"text": desc, "font": SANS, "size": 12, "color": MUTED, "line_spacing": 1.5}])
        y0 += 1.42
    foot(s, 7)

    # ---------------------------------------------------------- 8. signal ---
    s = base_slide(prs)
    head(s, "Method", "Measure learning, not output", "Signals")
    cols = [3.3, 4.1, 4.0]
    xs = [L, L + cols[0], L + cols[0] + cols[1]]
    hdr = ["Signal", "What it tells you", "What it does not tell you"]
    for x, w, t in zip(xs, cols, hdr):
        text(s, x, 2.2, w - 0.3, 0.3,
             [{"text": t, "font": SANS, "size": 10, "color": MUTED_LIGHT,
               "bold": True, "spacing": 1.1, "caps": True}])
    hline(s, L, 2.55, CW, RULE_STRONG)
    rows = [("Deployment frequency", "How fast changes land", "Whether the changes were right"),
            ("Review turnaround", "Where the queue actually sits", "That review quality is good"),
            ("Defect escape rate", "Where quality leaks out", "That the system is well designed"),
            ("Learning hours", "Whether the team is still growing", "That growth happened")]
    for i, row in enumerate(rows):
        y = 2.75 + i * 0.78
        for x, w, t in zip(xs, cols, row):
            bold = (x == L)
            text(s, x, y, w - 0.3, 0.5,
                 [{"text": t, "font": SANS, "size": 13, "bold": bold,
                   "color": INK_DEEP if bold else MUTED, "line_spacing": 1.4}])
        hline(s, L, y + 0.56, CW)
    text(s, L, 6.05, 9.5, 0.4,
         [{"text": "A metric you cannot act on is decoration. A metric you act on weekly is culture.",
           "font": SERIF, "size": 16, "color": INK_SOFT, "italic": True}])
    foot(s, 8)

    # ----------------------------------------------------------- 9. close ---
    s = base_slide(prs, spine=False)
    rect(s, 0, 0, 0.28, SH, BURGUNDY)
    text(s, 1.35, 2.35, 9.5, 1.2,
         [{"text": "From The Trenches", "font": SERIF, "size": 48, "color": INK_DEEP,
           "line_spacing": 1.0}])
    hline(s, 1.35, 3.85, 3.4, BURGUNDY, 2.0)
    text(s, 1.35, 4.2, 9.0, 1.2,
         [{"text": "Ideas that survive the work. Technical experiments, leadership "
                   "lessons, unfinished questions — and the occasional reflection on "
                   "being human.",
           "font": SERIF, "size": 16, "color": INK_SOFT, "line_spacing": 1.5}])
    text(s, 1.35, 5.7, 9.0, 0.4,
         [{"text": "alexandrugris.ro   ·   github.com/alexandrugris   ·   LinkedIn",
           "font": SANS, "size": 12, "color": GREEN, "spacing": 1.0, "caps": True}])
    text(s, 1.35, 6.45, 9.0, 0.4,
         [{"text": "Munich · Morning", "font": SANS, "size": 10, "color": MUTED_LIGHT,
           "spacing": 1.4, "caps": True}])

    prs.save(str(path))
    print(f"deck -> {path}  ({len(prs.slides._sldIdLst)} slides)")


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "sample-deck.pptx")
    build(out)