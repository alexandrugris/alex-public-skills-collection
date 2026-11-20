# AG Style — "From The Trenches"

Visual system distilled from `alexandrugris.ro` (current, editorial) and
`alexandrugris.github.io` (older, paper-like Jekyll blog). Both sites share the
same spine: warm paper, dark warm ink, one burgundy accent, a serif for voice
and a sans for metadata, hairline rules, and generous space. This document
states the rules so any text, deck, document, or page can be produced in the
same language.

Canonical tokens live in `references/tokens.css`. Templates live in
`templates/`. Build helpers live in `scripts/`.

---

## 1. The idea in one line

**Quiet editorial polish.** The system never competes with the content. It
frames it: warm paper, one confident accent, strong typographic hierarchy,
restrained motion, no decoration that isn't information.

Three failure modes to avoid:

1. **Loud.** No gradients on type, no drop shadows on text, no color floods
   except photography scrims, no emoji, no decorative rules more than 3px.
2. **Generic.** No default Bootstrap grey, no generic blue links, no centered
   everything. The burgundy and the hairline carry the identity.
3. **Crowded.** Whitespace is the design. If a slide feels full, delete content
   rather than shrinking type.

---

## 2. Palette

| Token | Hex | Role |
|---|---|---|
| `--paper` | `#FBFAF7` | page ground. Warm off-white, never pure `#fff` |
| `--paper-warm` | `#F2EEE4` | alternating band (principles, callouts) |
| `--paper-deep` | `#EFEBE2` | footer band |
| `--paper-alt` | `#F7F4ED` | secondary section / figure ground |
| `--ink` | `#30332F` | body text — warm dark grey-green, never `#000` |
| `--ink-deep` | `#292B28` | display headings |
| `--ink-soft` | `#53574F` | lede paragraphs |
| `--muted` | `#686B64` | secondary text, card body |
| `--muted-light` | `#85857C` | section notes, meta labels |
| `--muted-faint` | `#A7A095` | index numerals (`01`, `02`) |
| `--rule` | `#D8D4CA` | hairline rule |
| `--rule-strong` | `#BBB7AE` | emphasised hairline (featured card tops) |
| `--burgundy` | `#8D2829` | **primary accent.** Kickers, numerals, card top-borders, links on hover |
| `--burgundy-deep` | `#6E0F0F` | visited link state |
| `--green` | `#415649` | secondary accent — signature block, quiet labels |
| `--green-deep` | `#1E2720` | scrim over photography |
| `--amber` | `#D69F65` | **focus ring only.** Never decorative |
| `--code-bg` / `--code-fg` | `#2B2B2B` / `#A9B7C6` | code blocks, dark inset |

Rules:

- Burgundy appears **once per visual block**. Repeated rules across a principle grid are intentional; avoid competing
  emphasis within each block.
- Green never competes with burgundy. It is a background/support color.
- Accent fills (burgundy background, white text on burgundy) are reserved for
  one element per page — the kicker band, the CV/download block, the close.
- Check text contrast against the actual surface, including `--paper-warm`.

---

## 3. Typography

### Families

| Role | Stack |
|---|---|
| Serif — voice, headings, long-form | `Georgia, "Gelasio", "Times New Roman", serif` |
| Sans — labels, metadata, captions, card body | `Inter, ui-sans-serif, system-ui, sans-serif` |
| Mono — code | `"IBM Plex Mono", Menlo, Consolas, monospace` |

`Gelasio` is metric-compatible with Georgia — use it as the drop-in when
Georgia is unavailable and the layout must not shift.

### The division of labour

**Serif carries the voice.** Headings, ledes, body copy, pull quotes, table
values in narrative sections, list items.

**Inter carries the metadata.** Kicker lines, section notes, dates, categories,
card descriptions, page furniture, chart labels. Metadata labels are uppercase, letterspaced and small. Card descriptions
and principle explanations use sentence-case sans text.

### Web scale

| Element | Size | Line height | Tracking | Family |
|---|---|---|---|---|
| Display | `clamp(46px, 6vw, 69px)` | `0.98` | `-0.055em` | serif |
| Masthead / domain | `clamp(27px, 3vw, 34px)` | `1` | `-0.02em` | serif, burgundy |
| H2 / section | `31px` | `1.15` | `-0.025em` | serif |
| H3 / card title | `23px` | `1.1` | `-0.015em` | serif |
| Lede | `18px` | `1.57` | — | serif |
| Body | `16px` | `1.62` | — | serif |
| Card body | `13px` | `1.55` | — | sans |
| Meta label | `11px` | — | `0.10em` | sans, uppercase |
| Micro label | `10px` | — | `0.08em` | sans, uppercase |

### Rules

- **Serif headings are never bold.** Weight 400 only. Size and tracking do the
  work. The single exception is an inline emphasis inside a paragraph.
- Display tracking is negative and tight — `-0.055em` at the display size,
  easing to `-0.02em` as size drops. Sans labels are positive and open —
  `0.10em` to `0.13em`.
- Uppercase is **always** Inter, **never** serif. A serif in caps reads as a
  mistake in this system.
- Measure: `68ch` max for long-form; `51ch` for ledes; `740px` for document
  body; `800px` for blog archives.
- No text below `10px` on screen, `6.8pt` in print.

### Line-height ladder

Display `0.98` · H2 `1.15` · H3 `1.1` · lede `1.57` · body `1.62` · card `1.55`
· meta `1.4`.

---

## 4. Space & structure

- Web shell: `1180px` max, side padding `7%`.
- Section padding: `58px` top, `64px` bottom (web) — asymmetric, bottom heavier.
- Grid gaps: `28px` (4-col), `36px` (3-col), `52px` (2-col asymmetric).
- 4-col grid for principle sets; `1.16 / 1 / 1` for featured writing (the
  featured item is wider and carries a `3px` burgundy top rule); `.8 / 1.2` for
  About blocks (label column, body column).
- Document: A4, margins `20mm` top / `22mm` sides / `18mm` bottom.
- Slides: 16:9, `13.333in × 7.5in`, outer margin `0.95in`, content grid 12
  columns with `0.22in` gutters.

---

## 5. Signature motifs

These are the recognisable moves. Use them consistently.

1. **Hairline rules.** `1px solid var(--rule)` separates sections, table rows,
   list items. They are quiet, never dashed, never doubled.
2. **Accent top-borders.** A `2px` burgundy line tops a principle card; a
   `3px` line marks the featured item. This is the system's signature mark.
3. **Index numerals.** `01`, `02` in Inter 11px, `--muted-faint`, above the
   title. Two digits, zero-padded, always.
4. **Letterspaced micro-labels.** `CREATIVE WRITING · 2024–2026` in Inter 10px
   uppercase, burgundy. Replaces bullets, icons, and badges.
5. **Left-ruled pull quotes.** `4px` solid `--rule` (or burgundy for emphasis),
   italic serif, `--muted` colour.
6. **Invisible-until-hover underline.** Links carry `text-decoration-color:
   transparent` and reveal the underline on hover with a `4px` offset. Links are
   unremarkable until you look for them.
7. **Soft panel shadow.** `0 18px 46px rgba(28,36,29,.2)` — used **once**, on
   the hero copy card floating over photography. Nothing else gets a shadow.
8. **Photography scrim.** A `90deg` gradient from `rgba(21,31,25,.47)` to
   transparent sits over full-bleed images so type stays readable.
9. **Circular portrait**, `62px`, next to the name block.
10. **Folded edge**: the domain name at the top is the brand; keep it as the
    masthead rather than a logo image.

---

## 6. Voice (text)

Applies to long-form texts, deck copy, document prose.

- **Declarative, not promotional.** State what happened and what it taught.
  No superlatives, no "thrilled to announce", no "unlock/leverage/synergy".
- **Short declarative sentences for the claim; long ones for the nuance.**
  Mix both in a paragraph.
- **Concrete nouns over abstractions.** "Two teams, three countries, one
  incident review" beats "cross-functional collaboration".
- **Prefer the past tense for experience, present for principles.**
- **British-leaning, European plain English.** Avoid US corporate register.
- **Words to reach for:** depth, judgment, measure, disagreement, long view,
  from the trenches, trade-offs, evidence, practice.
- **Words to avoid:** leverage, synergy, innovative, robust solution,
  best-in-class, journey, unlock, empower, cutting-edge.
- Numbers are specific: `14%`, `three incidents`, `two weeks`.

---

## 7. Per-medium rules

### 7.1 Web page (`templates/page.html`)

- Masthead: domain in serif burgundy, centered; nav in Inter uppercase 11px.
- Hero: full-bleed image, left-aligned copy card in `--paper` with the soft
  shadow, kicker → display → lede → signature block.
- Sections alternate `--paper` / `--paper-warm` / `--paper-alt`, separated by
  hairlines.
- Footer band in `--paper-deep`, Inter 11px.
- Focus ring `--amber` 3px with 4px offset. Skip link present.
- Max width 1180px; collapse to 1 column under 760px.

### 7.2 Document / PDF

- Use `templates/article.html` for long-form work. Its named A4 page paints
  `--paper` across the sheet, including the margins, with a 166mm text measure.
  Use `templates/document.html` for fixed compositions.
- Open with a kicker and display title. Give the author's name its own byline
  directly below the title. Add the publication date when known and include a
  role or reading time only on request. Place the lede beneath the byline.
- Set narrative body at 10.5pt / 1.58 in a single column. Leave 1em between
  consecutive body paragraphs, with more space above section headings than below.
  Reserve hairlines for elements such as tables and a colophon. Set sources as
  a plain linked list below its heading, with space between links.
- The flowing template uses print margin boxes for the left-hand signature and
  right-hand page count. Keep headings with the next block, keep captions with
  their figures, and repeat the header when a long table breaks across pages.
- Route diagram arrows through the gaps between boxes. Put labels inside the
  node they describe or reserve clear space outside the arrow path. Use a table
  for independent checks that share the same input and result.

For notebooks and research reports, use generous vertical space on covers and
part openers. In a visual guide, give each main diagram its own block with the
caption close by and a clear gap before the next block.

### 7.3 Slides (`scripts/build_deck.py`)

- 16:9. Paper ground, never white. A full-width `0.055in` burgundy rule at the
  very top of content slides is the deck's spine.
- **Title slide**: kicker (burgundy) → display title (serif, 44–54pt) →
  thin rule → lede → signature block bottom-left.
- **One idea per slide.** If a slide has two headlines, cut one.
- Narrative body text should stay at least 14pt; supporting descriptions in
  the reference use smaller type. Metadata is typically 10–11pt, with 9pt
  footers and chart labels. Prefer larger type for projected presentations.
- 4-col principle grid mirrors the web grid: `2px` burgundy top rule, grey
  numeral, serif title.
- Charts: no chart junk. Gridlines in `--rule`, axis labels in Inter 9–10pt,
  one accent series in burgundy, everything else in `--muted-faint`.
- Quote slide: oversized serif italic, left-ruled in burgundy, nothing else.
- Close slide: no new content. Domain, links, one line.
- Numbers slide-wide: 8–10 slides for a talk; never more than 6 bullets.

### 7.4 Long-form text (Markdown / note)

- Kicker line, then H1 in sentence case, then a one-paragraph lede.
- Paragraphs: 2–5 sentences. One idea per paragraph.
- Pull quote for the sentence that carries the piece.
- Section headings in sentence case, never Title Case.
- Inline code as `.chip` (light), blocks in `.code` (dark inset).
- Tables for comparison, `.list-clean` for enumerations with hairline rows.
- Close with a one-line colophon, not a summary paragraph.

---

## 8. Anti-patterns

| Don't | Do |
|---|---|
| Pure `#fff` background | `--paper` `#FBFAF7` |
| Blue underlined links | burgundy accent, underline on hover only |
| Bold serif headings | weight 400, tight tracking |
| Serif in uppercase | uppercase is Inter only |
| Accent colour on every element | one accent per visual block |
| Icons for categories | letterspaced text labels |
| Drop shadows on cards | shadow only on the hero copy card |
| Centre-aligned body copy | left-aligned, ragged right |
| 3+ colours per page | paper, ink, burgundy, one hairline |
| Dashed or double rules | 1px solid hairline |
| Rounded pill badges | flat text labels |
| Centre everything | asymmetric grids, generous margins |

---

## 9. Quick reference

```css
--paper: #FBFAF7;   --ink: #30332F;    --burgundy: #8D2829;
--rule: #D8D4CA;    --green: #415649;  --muted: #686B64;

font-family: Georgia, "Gelasio", serif;        /* voice  */
font-family: Inter, ui-sans-serif, system-ui;    /* labels */

h1 { font-weight: 400; letter-spacing: -0.055em; line-height: .98; }
.meta { font-size: 11px; letter-spacing: .10em; text-transform: uppercase; }
.principle { border-top: 2px solid #8D2829; }
.quote { border-left: 4px solid #D8D4CA; font-style: italic; }
```

## 10. Evidence and legacy exceptions

See `samples/validation.md`. Original samples are preserved unchanged even
where they diverge from idealized rules: ink web masthead, bold article titles,
serif principle numerals and small slide supporting copy. New work should
follow the intended hierarchy unless faithful reproduction is requested.
Gelasio and Georgia are not guaranteed to wrap identically across engines.
