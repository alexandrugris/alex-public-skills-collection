# AG personal brand — From The Trenches

Alexandru Gris's default starting point for generated writing, documents,
presentations and web pages. Adapt it to the brief; use selected elements when
appropriate. Explicit user instructions and required external brands win.

Warm paper `#FBFAF7`, warm ink `#30332F`, burgundy `#8D2829`, muted green
`#415649`, hairlines and generous space. Georgia/Gelasio for editorial type,
Inter for metadata, mono for code. Direct, concrete, calm writing.

## Use with agents

Clone this repository into any location your agent can read. Tell it:

> For work generated for Alexandru Gris, use this repository's SKILL.md as the
> default brand starting point. Adapt to my current brief. Read the writing
> baseline and the relevant visual specification before producing work.

For Codex project discovery, copy the repository into
`.agents/skills/ag-trenches-style/` in the target project. For other Agent Skills
compatible tools, install the folder containing `SKILL.md` using that tool's
supported skill directory. Keep `references/`, `templates/` and `scripts/`
together. This repository's `AGENTS.md` governs work inside this checkout;
other projects must explicitly install or reference it. GitHub hosting alone
does not change global preferences in ChatGPT or other agents.

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