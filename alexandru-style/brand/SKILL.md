---
name: ag-trenches-style
description: >-
  Apply Alexandru Gris's personal brand as the default starting point for
  generated writing, documents, presentations and web pages. Use when creating
  work for Alexandru, when asked for AG Style or From The Trenches, or when
  adapting existing content to his brand. Adapt to explicit briefs and other
  required brands; preserve supplied words unless rewriting is requested.
---

# AG Style — "From The Trenches"

A four-surface visual system distilled from `alexandrugris.ro` (editorial,
current) and `alexandrugris.github.io` (paper-like blog, older). Both sites
share the spine: warm paper, warm ink, one burgundy accent, serif for voice and
sans for metadata, hairline rules, generous space.

Canonical assets:

| Path | Use |
|---|---|
| `references/tokens.css` | Single source of truth: palette, type scale, components, print rules |
| `references/style-spec.md` | Full written spec, per-medium rules, anti-patterns |
| `templates/page.html` | Working web page (masthead, hero, principles, writings, about, footer) |
| `templates/document.html` | Working A4 document (fixed-height pages, running footer, figure, table) |
| `scripts/render.py` | HTML → PDF (+ page PNGs), inlines `tokens.css` automatically |
| `scripts/shoot.py` | HTML → PNG screenshot (page or viewport) |
| `scripts/deck_shots.py` | PPTX → per-slide PNGs (via soffice + pdftoppm) |
| `scripts/build_deck.py` | Builds the reference 9-slide 16:9 deck from primitives |

## Default and adaptation policy

Read `references/brand-voice.md` for the writing baseline. This brand is the
starting point for work generated for Alexandru, not a rigid template.
Explicit user requests, audience needs, accessibility and required external
brands take precedence. A brief may use only selected elements of this system.
Do not force a visual treatment into plain text, code or structured data.
Preserve factual meaning and supplied wording during visual-only restyling.
Never claim this repository automatically configures every agent or account.

## Reference samples and verification

Read `samples/README.md` and inspect the relevant original PNGs before visual
work. `samples/original/` contains the untouched source guide, PDFs, PPTX,
HTML and reference images; `samples/validation.md` records known mismatches.
Run `python scripts/fonts.py` to verify bundled-font discovery on Linux.
The sample copy is illustrative, not evidence of the user's biography.

Run `python scripts/verify_samples.py` to verify source checksums, shared CSS
and the generated slide structure against the original PPTX. This is a
structural check, not pixel-level or semantic proof for new work. Render and
inspect new output separately. Use the bundled OFL fonts in `fonts/`; see `fonts/README.md`. HTML renderers
embed them; slide previews use project-local Fontconfig. Exact appearance
still depends on font version and rendering engine;
never claim visual equivalence when fallbacks or assets are missing.

## Inputs to collect

- **Medium**: web page, document/PDF, slides, or long-form text. Changes the
  layout rules; the palette and type system do not change.
- **Content**: what the piece says. Preserve supplied content for visual restyling. For new content, use the
  writing baseline and disclose material assumptions.
- **Length**: one page or many. Documents are fixed-height A4 pages — ask how
  many, or default to 3.
- Do not ask about colours, fonts or spacing. Those are decided.

## Procedure

1. **Read `references/style-spec.md` first** if the medium is new to you. It
   holds the rules; this file holds the workflow.

2. **Start from the canonical tokens.** Never hand-pick a colour, size or
   spacing value. Use `references/tokens.css` — it is the only place colours
   live. If you need a value that is not there, add it to `tokens.css` and
   reference it, so the system stays single-sourced.

3. **Pick the medium and use its template.**
   - Web → `templates/page.html`, keep `TOKENS_PATH` in the `<link>`;
     `scripts/render.py` inlines it.
   - Document → `templates/document.html`. Pages are fixed-height
     (`width:210mm; height:297mm; overflow:hidden`), so **content that
     overflows is silently clipped** — check the rendered PNGs every time and
     split or reflow content, never shrink narrative body type below 10.5pt.
     Preserve supplied wording unless editing is authorized.
   - Slides → `scripts/build_deck.py`. Edit the content lists inside `build()`
     in a working copy, keeping canonical source unchanged.
   - Long-form text → no template; apply the typography and voice rules in
     Markdown.

   Every document template must keep `class="doc"` on `<body>` — that class is
   what activates the print type scale in `tokens.css`. Without it the document
   silently renders at web scale.

4. **For new or requested rewritten copy, use the AG voice** (see `references/style-spec.md` §6):
   declarative not promotional, concrete nouns over abstractions, past tense for
   experience and present for principles, sentence-case headings. Avoid
   leverage/synergy/robust/journey/unlock.

5. **Render and inspect.** Never ship a PDF or deck you have not looked at:
   ```bash
   python3 scripts/render.py doc.html out.pdf --png-dir shots/ --no-footer
   python3 scripts/shoot.py page.html shots/page.png --full
   python3 scripts/deck_shots.py deck.pptx shots/
   ```
   Check for: text colliding with the running footer, clipped text on a fixed
   page, an orphan heading, two accents in one visual block.

6. **Deliver the artefact plus its screenshots.** A style the user cannot see is
   not delivered — always include rendered images of at least the first page and
   one interior page or slide.

## Output contract

- A file deliverable (`.pdf`, `.pptx`, `.html`) in the requested medium, plus
  rendered PNGs of it.
- If the user asked for new content, the content is written in the AG voice and
  clearly original — do not paste text from the live sites.
- If the user asked to restyle *their* content, keep their words; change only
  structure and presentation.

## Failure handling

- **Text overflows a fixed page**: cut copy, split into another page, or reduce
  a figure. Never reduce body type below 10.5pt and never let `overflow:hidden`
  crop a sentence silently.
- **Georgia is usually not installed**: the CSS stack falls back to Gelasio,
  which is intended as a compatible substitute; verify line wrapping. Bundled Gelasio faces include a real bold. HTML rendering embeds them and
  slide conversion uses the project-local alias automatically. Do not change
  system or user font settings.
- **`--no-footer` for `render.py`**: document templates carry their own running
  footer with a hard-coded page number. Without the flag you get a second,
  duplicated footer.
- **Name collisions**: `soffice --convert-to pdf` writes `<stem>.pdf` and will
  overwrite a document PDF that shares the stem. Use `scripts/deck_shots.py`,
  which converts in a temp directory.
- **Chromium missing** for `render.py`/`shoot.py`: the scripts use a system Chromium or the normal Playwright installation.
  Run `python -m playwright install chromium` when needed. If unavailable,
  fall back to `soffice --headless --convert-to pdf` for decks and report that
  the PDF path was not used.
- **Georgia missing** on the target machine: the CSS stack falls back to
  Gelasio. Verify its actual availability before rendering rather than letting the page
  fall back to Times.
- **PPTX opened elsewhere without Gelasio/Inter**: Georgia and Inter are the
  declared fonts, so the file stays correct on any machine with them; render
  previews with the bundled script instead of trusting PowerPoint.
- Unsure which medium the user means: ask once, offering web / document /
  slides, and proceed on the reply.

## Examples

**Input** — "Turn this outline into a 3-page PDF in my style."
**Output** — `templates/document.html` filled with the outline, rendered via
`scripts/render.py` to a 3-page A4 PDF with `sample-document-1.png` …
`-3.png` attached.

**Input** — "Build me a deck about the principles."
**Output** — `scripts/build_deck.py` edited with the new content, producing a
9-slide 16:9 PPTX, then `scripts/deck_shots.py` for a PNG of every slide.

**Input** — "Make my homepage look like alexandrugris.ro."
**Output** — `templates/page.html` as the base: keep the masthead, hero with
the copy card, 4-column principle grid, 1.16/1/1 writings grid and the
`.8/1.2` about band; replace only the content.

## Sample-specific exceptions

The original web masthead is ink, article titles retain browser-bold serif,
and principle numerals inherit serif from the broad span selector. These are
legacy sample exceptions, not universal brand rules. For new work prefer the
explicit token classes (regular serif headings; sans metadata/numerals), while
faithful sample reproduction preserves the original. The original hero image
was not in the shared archive; use a supplied image or an intentional plain
background, and disclose that exact web reproduction is unavailable.

Run `python scripts/audit_assets.py` before distributing the skill; it verifies
all shipped asset hashes and Git tracking. The maintained web template uses an
intentional plain background, so it has no missing hero-image dependency.