---
name: alexandru-style
description: |
  Load this skill whenever Alexandru asks to create, restyle, or export a styled deliverable: documents, reports, PDFs, slide decks, presentations, HTML pages, mini apps, dashboards, or tables. It applies his personal design system (AG Style v1.0: Georgia serif display, uppercase Inter labels, IBM Plex Mono code, paper and burgundy palette from alexandrugris.ro) instead of generic defaults. Also load when he says "my style", "my design system", "the usual style", or mentions the alexandrugris.ro look. Do not load for unstyled code debugging, prose-only de-AI passes, or raw data scripts.
---

# Alexandru's Style System (AG Style v1.0)

Apply Alexandru Gris's personal design system to any styled artifact: documents, PDFs, slide decks, HTML pages, mini apps, dashboards, or tables. Canonical CSS tokens live in `brand/references/tokens.css`, with a compact working summary in `design-system.md` (distilled from alexandrugris.ro and alexandrugris.github.io). Do not fetch the sites at runtime.

## Workflow

1. Read `design-system.md` for the exact colors, typography, motifs, space, per-medium rules, and anti-patterns. For production PDF/HTML/PPTX rendering, also consult `brand/references/production-workflow.md` and `brand/references/style-spec.md`.
2. Apply AG Style as the default visual treatment unless the user explicitly asks for another brand or theme. Preserve supplied wording on visual-only restyling tasks.
3. Use the format-specific recipe below.
4. Run `python3 tests/check_styled.py <deliverable>` on HTML pages and Marp decks before delivery; inspect rendered page PNGs for PDFs and slide decks.
5. If the site style changes, update `brand/references/tokens.css` first (single source of truth), then sync `design-system.md` in the same commit.

## Format recipes

**Marp slides canvas.** Start with `<!-- theme: default -->`, `<!-- size: 16:9 -->`, and `<!-- paginate: true -->`, then a global `<!-- style: | ... -->` block defining `section { background: #fbfaf7; color: #30332f; font-family: Georgia, "Times New Roman", serif; }`, weight-400 headings with negative letter-spacing, the burgundy spine (top rule per the guide; the HTML presenter deck uses a left-edge bar), and helper classes (`.kicker`, `.note`, `.section-head`, `.principle`, `.article`) using `Inter, ui-sans-serif, system-ui, sans-serif` in uppercase with `0.08-0.13em` tracking. Reuse the class skeletons from `design-system.md`. Deck rules: one idea per slide, body never below 14pt, meta never below 10pt, at most 6 bullets per slide, 8-10 slides per talk. Charts: gridlines in `--rule`, axis labels in Inter 9pt, one burgundy series.

**HTML page or mini app.** Inline CSS using the exact custom properties from `brand/references/tokens.css` (`--paper`, `--ink`, `--ink-deep`, `--burgundy`, etc.), or start from `brand/templates/page.html`. Self-contained only: Georgia is web-safe, Inter falls back to the system sans stack, mono falls back to `ui-monospace, "SF Mono", Menlo, Consolas, monospace`; no CDN fonts or external assets.

**Standalone presenter deck (HTML).** Fixed 1280x720 stage centered and scaled to the viewport with CSS transform; slides cross-fade via `.active`; arrow keys, space, and swipe navigate; `F` toggles fullscreen; thin burgundy progress bar at the top and muted counter bottom right; full-height burgundy spine bar on the left edge; print CSS (one slide per page) so browser print yields a styled PDF.

**PDF / document.** Start from [the flowing A4 article template](brand/templates/article.html) (or `brand/templates/document.html` for fixed page counts) and follow [the print recipe](brand/references/style-spec.md#72-document--pdf). Put the author directly below the title, with publication date if supplied. Add a role or reading time only if requested. Render with `python3 alexandru-style/brand/scripts/render.py INPUT.html OUTPUT.pdf --png-dir PREVIEWS` from the repo root, and inspect every rendered page PNG before delivery.

**PPTX deck.** Copy `brand/scripts/build_deck.py` for working edits (it pulls its palette directly from `brand/references/tokens.css`), generate the `.pptx`, and render slide previews with `brand/scripts/deck_shots.py`.

**Markdown document canvas.** Markdown limits styling: carry over structure and voice instead. Kicker lines in the form `FROM THE TRENCHES · TOPIC · DATE` above the title, quiet uppercase section notes, middle-dot separators, and no leaked CSS tokens.

**Tables and spreadsheets.** Paper-warm header band (`#F2EEE4`), ink text (`#30332F`), 1px hairline row rules (`#D8D4CA`), burgundy reserved for accents and key figures. No default theme blues.

## Tests

`tests/test-cases.md` holds the five cases with pass conditions; `python3 tests/check_styled.py <file>` is the static bar for HTML and Marp deliverables.

## Brand toolkit (`brand/`)

`brand/` holds the full production toolkit merged from `ag-personal-brand`:
- `brand/references/tokens.css`: single source of truth for CSS variables, typography, components, and `@page` print rules.
- `brand/references/style-spec.md` & `brand/references/production-workflow.md`: full visual spec and rendering workflow.
- `brand/templates/`: web (`page.html`), flowing A4 article (`article.html`), and fixed-page document (`document.html`).
- `brand/scripts/`: PDF/PNG/PPTX renderers and verification scripts.
- `brand/samples/` & `brand/binaries-archive/`: original reference gallery and byte-verified snapshot archive.

## Quality bar

- Light paper backgrounds always (`#FBFAF7`); never dark themes unless requested (code blocks use `--code-bg: #2B2B2B`).
- Headings weight 400, never bold; express hierarchy through size and tracking. Uppercase is always Inter — never a serif in all-caps.
- Burgundy (`#8D2829`) appears once per visual block: kickers, rules, and accents, never large fills. No gradients on type, no text shadows, no emoji, no decorative rules above 3px. Shadows only on the hero copy card over a full-bleed image.
- Hairlines are 1px solid (`#D8D4CA`), never dashed, never doubled. Body copy left-aligned, ragged right — never centered.
- For prose voice rules, defer to the `anti-ai` skill (`../anti-ai/references/anti-ai-short.md`); keep copy declarative, middle-dot labels, and zero exclamation marks.
