---
name: |
  alexandru-style
description: |
  Load this skill whenever Alexandru asks to create, restyle, or export a styled deliverable: documents, reports, PDFs, slide decks, presentations, HTML pages, mini apps, dashboards, or tables. It applies his personal design system (AG Style v1.0: Georgia serif display, uppercase Inter labels, IBM Plex Mono code, paper and burgundy palette from alexandrugris.ro) instead of generic defaults. Also load when he says "my style", "my design system", "the usual style", or mentions the alexandrugris.ro look.
---

# Alexandru's Style System (AG Style v1.0)

Apply Alexandru Gris's personal design system to any styled artifact he asks for: documents, PDFs, slide decks, HTML pages, mini apps, dashboards, tables. The tokens in `design-system.md` (this directory) are the source of truth — the AG Style Guide v1.0 (4 pages, 2026), distilled from alexandrugris.ro and alexandrugris.github.io. Do not fetch the sites at runtime.

## Workflow

1. Read `design-system.md` for the exact colors, typography, motifs, space, per-medium rules, voice, and anti-patterns.
2. Apply it as the default style unless Alexandru explicitly asks for something else.
3. Use the format-specific recipes below.
4. If Alexandru says the site style has changed, update `design-system.md` here and the corresponding entry in the `branding-personnel` Knowledge topic in the same pass.

## Format recipes

**Marp slides canvas.** Start with `<!-- theme: default -->`, `<!-- size: 16:9 -->` and `<!-- paginate: true -->`, then a global `<!-- style: | ... -->` comment defining `section { background: #fbfaf7; color: #30332f; font-family: Georgia, "Times New Roman", serif; }`, weight-400 headings with negative letter-spacing, the deck's burgundy spine (top rule per the guide; the reference HTML presenter deck uses a left-edge bar instead), and helper classes (`.kicker`, `.note`, `.section-head`, `.principle`, `.article`, `.swatch`, `.cvlink`) using the sans stack `Inter, ui-sans-serif, system-ui, sans-serif` in uppercase with 0.08-0.13em tracking. Reuse the class skeletons from `design-system.md`. Deck rules: one idea per slide (if a slide has two headlines, cut one), body never below 14pt, meta never below 10pt, never more than 6 bullets, 8-10 slides per talk. Charts: gridlines in `--rule`, axis labels in Inter 9pt, one burgundy series.

**HTML page or mini app.** Inline CSS with the custom properties block from `design-system.md` (`--paper`, `--ink`, `--burgundy`, etc.). Self-contained only: Georgia is web-safe, Inter falls back to the system sans stack, mono falls back to `ui-monospace, "SF Mono", Menlo, Consolas, monospace`; no CDN fonts or external assets.

**Standalone presenter deck (HTML).** Fixed 1280x720 stage centered and scaled to the viewport with a CSS transform; slides cross-fade via an `.active` class; arrow keys, space, and swipe navigate; `F` toggles fullscreen; a thin burgundy progress bar sits at the top and a muted counter bottom right; the deck's spine is a full-height burgundy bar on the left edge (as in the reference deck); include print CSS (one slide per page) so browser print yields a styled PDF. This exact pattern is proven to render in the HTML canvas.

**PDF / document.** Author the content as a styled HTML document with this system, then export or print to PDF. A4, Paper ground `#FBFAF7` — never white — 22mm side margins, 166mm measure. Kicker → display title → lede → hairline → meta line (author · role · date · length). Body 10.5pt / 1.58, full measure, no column splits. Running footer: name left, page number right, Inter 7.4pt uppercase. Headings never orphan; figures keep their caption on the same page. Never deliver a text-only PPTX as the final styled artifact; the PPTX export strips custom styling, so offer the HTML presenter route instead.

**Markdown document canvas.** Markdown limits styling: carry over the structure and voice instead. Kicker lines in the form "FROM THE TRENCHES · TOPIC · DATE" above the title, quiet uppercase section notes, middle-dot separators, weight on prose, and the "From the trenches" register in drafting.

**Tables and spreadsheets.** Paper-warm header band, ink text, 1px hairline row rules, burgundy reserved for accents and key figures. No default theme blues.

## Brand toolkit (full assets)

For production work, use the complete brand toolkit in `brand/` (merged from
github.com/alexandrugris/ag-personal-brand): `brand/references/tokens.css` is the
single source of truth for palette, type and components; `brand/references/style-spec.md`
is the full written spec; `brand/templates/` hold working web and A4 document HTML;
`brand/scripts/` render PDFs, page PNGs and the reference deck; `brand/samples/`
records the original reference gallery. `design-system.md` (next to this file) remains
the compact distilled spec; run from `brand/` root so the relative paths resolve.

## Quality bar

- Light paper backgrounds always; never dark themes unless requested (code blocks use the dark inset).
- Headings weight 400, never heavy bold; express hierarchy through size and tracking. Uppercase is always Inter — a serif in caps reads as a mistake.
- Burgundy appears once per visual block: kickers, rules, and accents, never large fills. No gradients on type, no shadows on text, no emoji, no decorative rules above 3px. Shadows only on the hero copy card over a full-bleed image.
- Hairlines are 1px solid, never dashed, never doubled. Body copy left-aligned, ragged right — never centred.
- Copy voice: "From the trenches", declarative not promotional, middle-dot separators in labels, no exclamation marks.
- Every deliverable must look unmistakably like alexandrugris.ro, not like a template.