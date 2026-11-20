# AG personal brand — From The Trenches

Alexandru Gris's default starting point for generated writing, documents,
presentations and web pages. Adapt it to the brief; use selected elements when
appropriate. Explicit user instructions and required external brands win.

Warm paper `#FBFAF7`, warm ink `#30332F`, burgundy `#8D2829`, muted green
`#415649`, hairlines and generous space. Georgia/Gelasio for editorial type,
Inter for metadata, mono for code. Direct, concrete, calm writing.

## Use with agents

This toolkit lives inside the `alexandru-style` skill (one level up). Use `../SKILL.md`
as the single skill manifest, `references/production-workflow.md` for rendering steps,
and `references/tokens.css` + `references/style-spec.md` for the visual contract. Keep
`references/`, `templates/`, `scripts/`, and `binaries-archive/` together.

To update all participating agents, pull the same repository revision in each
installation. Pin a commit for reproducible output; review changes before
updating. Keep credentials and private source documents out of this repository.

## Generate

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python scripts/check.py
mkdir -p build
python scripts/render.py templates/document.html build/document.pdf --no-footer --png-dir build/document-shots
python scripts/shoot.py templates/page.html build/page.png --full
python scripts/build_deck.py build/deck.pptx
python scripts/deck_shots.py build/deck.pptx build/deck-shots --pdf
```

PDF page images require Poppler (`pdftoppm`); slide previews also require
LibreOffice (`soffice`). Gelasio, Inter and IBM Plex Mono are bundled with their OFL licenses in
`fonts/`. HTML embeds them and Linux slide rendering uses a project-local
Fontconfig alias; no system installation is needed. PowerPoint users should
install the bundled fonts locally or use the rendered PDF. Font versions may
change layout, so
inspect rendered pages and slides for overflow before delivery.

The templates contain reference content. Copy them for real work; keep the
canonical originals. `references/tokens.css` controls the shared palette,
including the slide generator. Document-specific layouts stay in the template.

## Provenance

Recovered from the original toolkit attached to the
[shared MiniMax task](https://share.mcode.io/share/QpS1NFOUNzw86kqPPwt-6g),
created November 7, 2026 from alexandrugris.ro and alexandrugris.github.io.
Packaged November 17, 2026 with agent adoption guidance, a writing baseline,
shared palette loading, dependency declarations and validation. Original
layout assets were preserved; brand defaults remain adaptable.

## Reference gallery and validation

The [sample gallery](samples/README.md) includes the original style-guide PDF,
document PDF/HTML, slide PDF/PPTX, web HTML and twelve PNG reference images.
See [validation results](samples/validation.md) for sample comparisons, corrected
rules, font substitutions and the missing original hero-image dependency.

```sh
python scripts/verify_samples.py
```

For a complete offline Git asset audit, run `python scripts/audit_assets.py`.
The maintained web template intentionally uses a plain hero background; the
original photograph was never supplied. Original references remain untouched.