# AG Style Production Workflow (`brand/`)

Operational reference for rendering production deliverables (web pages, flowing or fixed A4 PDFs, and 16:9 PPTX decks) with the bundled brand toolkit. This file complements `../../SKILL.md` (the single skill manifest) and `references/style-spec.md`.

## Canonical assets

| Path (relative to `brand/`) | Use |
|---|---|
| `references/tokens.css` | Single source of truth: palette, type scale, components, print rules |
| `references/style-spec.md` | Full written spec, per-medium rules, anti-patterns |
| `templates/page.html` | Working web page (masthead, hero, principles, writings, about, footer) |
| `templates/article.html` | Flowing A4 article, byline, page-wide paper and running page numbers |
| `templates/document.html` | Fixed-page A4 sample for briefs with a specified page count |
| `scripts/render.py` | HTML -> PDF (+ page PNGs), inlines `tokens.css` and bundled fonts |
| `scripts/shoot.py` | HTML -> PNG screenshot (page or viewport) |
| `scripts/deck_shots.py` | PPTX -> per-slide PNGs (via `soffice` + `pdftoppm`) |
| `scripts/build_deck.py` | Builds the reference 9-slide 16:9 PPTX deck from `tokens.css` palette |

## Default and adaptation policy

This brand is the starting point for work created for Alexandru Gris, not a rigid cage.
Explicit user requests, audience needs, accessibility requirements, and external brand guidelines take precedence.
Do not force visual treatment into plain text, code, or raw data.
Preserve factual meaning and supplied wording during visual-only restyling.

## Rendering and visual inspection

Never deliver a rendered PDF or deck without inspecting its page images (`<SKILL_DIR>` = `alexandru-style` directory; inputs and outputs can live anywhere on disk):

```sh
python3 "<SKILL_DIR>/brand/scripts/render.py" doc.html out.pdf --png-dir shots/
python3 "<SKILL_DIR>/brand/scripts/shoot.py" page.html shots/page.png --full
python3 "<SKILL_DIR>/brand/scripts/deck_shots.py" deck.pptx shots/
```

Check every page image at reading size:
- Paper ground extends through all four margins (never pure `#ffffff`).
- Byline sits clearly under the display title; at most one divider per section transition.
- Figures, captions, tables, and Sources have clean spacing and no clipped text.
- Every diagram arrow clears adjacent text and unrelated boxes.

## Failure handling

- **Text overflows a fixed page:** cut copy, split into another page, or tighten a figure. Never drop body type below `10.5pt` and never rely on `overflow: hidden` to crop text.
- **Georgia missing on Linux:** `tokens.css` falls back to bundled `Gelasio` (read directly from `fonts/` or in-memory from `binaries-archive/` by `scripts/fonts.py`). Verify line wrapping; never modify system font settings.
- **Print footers:** `render.py` detects `.doc--flow` and `.page-footer` automatically. Pass `--no-footer` when custom HTML defines its own running footer.
- **Name collisions during PPTX conversion:** `soffice --convert-to pdf` overwrites `<stem>.pdf`; always run `scripts/deck_shots.py`, which converts in a temporary directory.
- **Optional rendering dependencies:** PDF/screenshot scripts require Playwright + Chromium (`pip install -r brand/requirements.txt && python -m playwright install chromium`) and Poppler (`pdftoppm`). Deck scripts require `python-pptx` and LibreOffice (`soffice`).

## Sample-specific exceptions

The original web masthead is ink, original sample article titles retain browser-bold serif, and principle numerals inherit serif from a broad span selector. Treat those as legacy sample artifacts; use explicit token classes (weight-400 serif headings, sans metadata/numerals) for all new work. The original hero photograph was never supplied, so `templates/page.html` uses an intentional plain background.
