# Design System · alexandrugris.ro — AG Style v1.0 (2026)

Source of truth for the alexandru-style skill: the AG Style Guide v1.0 (4 pages), distilled from the CSS of https://alexandrugris.ro and https://alexandrugris.github.io (GitHub: `alexandrugris/alexandrugris.ro`, inline styles in `index.html`). Do not fetch the sites at runtime.

"Quiet editorial polish. The system never competes with the content — it frames it." Everything below is a rule, not a suggestion.

## 1 · Colour — 18 tokens

The guide specifies 18 tokens; the custom properties below are the working set (including the derived shades `--heading`, `--heading-2`, `--note`, `--paper-alt` taken from the site CSS).

```css
:root {
  --paper: #fbfaf7;        /* main background — never pure #fff */
  --paper-warm: #f2eee4;   /* warm section bands */
  --paper-alt: #f7f4ed;    /* light alternating section bands */
  --paper-deep: #efebe2;   /* footer band */
  --ink: #30332f;          /* body text */
  --heading: #292b28;      /* h1 */
  --heading-2: #32352f;    /* h2 */
  --muted: #686b64;        /* secondary text */
  --note: #85857c;         /* section notes, meta captions */
  --number: #a7a095;       /* muted faint: principle/card numbers */
  --burgundy: #8d2829;     /* the one accent: kickers, rules, borders */
  --rule: #d8d4ca;         /* 1px hairlines */
  --rule-strong: #bbb7ae;  /* card top rules (non-first) */
  --green: #415649;        /* support colour, signature line */
  --green-deep: #1e2720;   /* dark inset for code blocks */
  --focus: #d69f65;        /* amber focus ring only, 3px, 4px offset */
}
```

- Burgundy appears **once per visual block**; four accents in one viewport is a failure, not a feature.
- Green is a support colour and never competes. Amber is the focus ring and nothing else.
- Body text contrast is always checked against *Paper*, never against *Paper warm*.
- Alternating sections use `--paper` / `--paper-warm` / `--paper-alt` separated by 1px `--rule` borders; the footer band is `--paper-deep`.

## 2 · Typography — two families + mono

- **Serif · voice:** `Georgia, "Times New Roman", serif` — headings, ledes, body, pull quotes.
- **Sans · metadata:** `Inter, ui-sans-serif, system-ui, sans-serif` — kickers, dates, labels, captions.
- **Mono · code:** `IBM Plex Mono` — code blocks and chips (on the web without CDN assets, fall back to `ui-monospace, "SF Mono", Menlo, Consolas, monospace`).

| Element | Size | Line | Tracking | Family | Specimen |
| --- | --- | --- | --- | --- | --- |
| Display | 46–69px | 0.98 | −0.055em | Serif | The long view |
| Masthead | 27–34px | 1 | −0.02em | Serif | alexandrugris.ro |
| Section H2 | 31px | 1.15 | −0.025em | Serif | Principles |
| Card H3 | 23px | 1.1 | −0.015em | Serif | Media Projects |
| Lede | 18px | 1.57 | — | Serif | Technology, teams, and the long view |
| Body | 16px | 1.62 | — | Serif | I write to understand |
| Card body | 13px | 1.55 | — | Sans | Built and published as its own site |
| Meta label | 11px | — | +0.10em | Sans | CREATIVE WRITING · 2026 |
| Micro label | 10px | — | +0.08em | Sans | NOTES FROM A REVIEW |

- Serif headings are **never bold** — weight 400, with size and tracking doing the work (per the site CSS; at render size Georgia 400 can look heavy, but never set 700).
- Uppercase is **always Inter**; a serif in caps reads as a mistake in this system.
- Measure: 68ch for long-form, 51ch for ledes, 166mm for documents.
- Kicker pattern: uppercase sans in burgundy with middle-dot separator, e.g. "FROM THE TRENCHES · SINCE 2008". Section head: serif h2 left, quiet uppercase note right.

## 3 · Signature motifs — the recognisable moves

1. **Hairline rules** — 1px solid, never dashed, never doubled. Separates sections, table rows, list items.
2. **Accent top-borders** — 2px burgundy tops a card; 3px marks the featured item. The system's signature mark.
3. **Index numerals** — two digits, zero-padded, Inter 11px, muted faint, above the title.
4. **Letterspaced labels** — replace bullets, icons, and badges with uppercase metadata (e.g. "MANAGEMENT · 2025").
5. **Left-ruled pull quotes** — 4px solid rule (burgundy for emphasis), italic serif in muted ink. The one block allowed to interrupt the measure.
6. **Invisible-until-hover underline** — links are unremarkable until hovered; the rule appears on hover, 4px below.
7. **Photography scrim** — a 90° gradient keeps type readable over a full-bleed image. One shadow, one scrim.

## 4 · Space & structure

- Web shell: 1180px with 7% side padding. Sections pad 58px top and 64px bottom — asymmetric, bottom heavier. Grid gaps run 28px, 36px, and 52px.
- Documents: A4 with 22mm side margins. Slides: 16:9 with a 0.95in outer margin.
- Two grid shapes repeat across every medium: four equal columns for principle sets, and a 1.16 / 1 / 1 row for featured work — the wider column carries the 3px rule. About blocks use .8 / 1.2: a label column, then the body.
- Motion: transitions are 120ms and only ever change colour. Nothing slides, fades, or bounces — and `prefers-reduced-motion` turns off even the scroll.

## 5 · Per-medium rules

**Web page.** Masthead: domain in serif burgundy, centred; nav in Inter uppercase 11px. Hero: full-bleed image, copy card in Paper with the one permitted shadow. Sections alternate Paper / Paper warm / Paper alt, separated by hairlines. Footer band in Paper deep; focus ring amber 3px, 4px offset; skip link present. Collapse to one column under 760px.

**Document / PDF.** A4, Paper ground — never white. 22mm side margins. Kicker → display title → lede → hairline → meta line (author · role · date · length). Body 10.5pt / 1.58, full measure, no column splits. Running footer: name left, page number right, Inter 7.4pt uppercase. Headings never orphan; figures keep their caption on the same page.

**Slides.** 16:9, Paper ground. The deck has one full-bleed burgundy spine rule — a top rule per the guide; the reference presenter deck carries it as a left-edge bar on every slide. One idea per slide. Body never below 14pt; meta never below 10pt. Charts: gridlines in Rule, axis labels in Inter 9pt, one burgundy series. 8–10 slides for a talk; never more than 6 bullets.

**Long-form text.** Kicker, then H1 in sentence case, then a one-paragraph lede. Two to five sentences per paragraph; one idea per paragraph. Sentence-case headings, never Title Case. Inline code as a light chip; blocks in the dark inset. Close with a one-line colophon, not a summary paragraph.

## 6 · Guardrails & anti-patterns — never

**Three ways to get it wrong:** 01 LOUD — no gradients on type, no shadows on text, no colour floods except photography scrims, no emoji, no decorative rules above 3px. 02 GENERIC — no default greys, no blue links, no centred everything; burgundy and the hairline carry the identity. 03 CROWDED — whitespace is the design; if a slide feels full, delete content rather than shrinking type.

| Don't | Do |
| --- | --- |
| Pure #fff background | Paper — #FBFAF7 |
| Blue underlined links | Burgundy accent, underline revealed on hover only |
| Bold serif headings | Weight 400 with tight tracking |
| Serif in uppercase | Uppercase is Inter only |
| Accent on every element | One accent per visual block |
| Icons for categories | Letterspaced text labels |
| Shadows on cards | Shadow only on the hero copy card |
| Centre-aligned body copy | Left-aligned, ragged right |
| Rounded pill badges | Flat text labels |

## 7 · Voice

"From the trenches" (since 2008): build to understand, the long view, learning by doing. Declarative, not promotional — state what happened and what it taught. Concrete nouns over abstractions. Past tense for experience, present for principles. Reach for: depth, judgment, measure, disagreement, long view, trade-offs. Avoid: leverage, synergy, innovative, robust solution, journey, unlock. Quiet, direct sentences; middle-dot separators in labels; understated confidence, no exclamation marks.

## Reusable class skeletons (Marp `style` directive)

```
<!-- size: 16:9 -->
section { background:#fbfaf7; color:#30332f; font-family: Georgia, "Times New Roman", serif; padding:58px 76px; border-top:6px solid #8d2829; }
.kicker { font-family: Inter, ui-sans-serif, system-ui, sans-serif; color:#8d2829; font-size:13px; letter-spacing:.13em; text-transform:uppercase; }
.note   { font-family: Inter, ui-sans-serif, system-ui, sans-serif; color:#85857c; font-size:12px; letter-spacing:.08em; text-transform:uppercase; }
h1 { font-size:52px; font-weight:400; letter-spacing:-0.045em; line-height:1.02; color:#292b28; }
h2 { font-size:34px; font-weight:400; letter-spacing:-0.025em; color:#32352f; }
.principle { border-top:2px solid #8d2829; padding-top:14px; }
.principle b { font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:#a7a095; font-size:12px; }
.section-head { display:flex; justify-content:space-between; align-items:baseline; gap:20px; margin-bottom:30px; }
```

Reference implementations built with this system: the Marp deck and the self-contained HTML presenter deck created on 2026-11-13 (the presenter deck carries the burgundy spine as a left-edge bar), plus the AG Style Guide v1.0 PDF (4 pages, 2026), the sample documents, and the alexandrugris.ro page screenshots shipped alongside this guide.