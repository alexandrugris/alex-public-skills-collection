# alex-public-skills-collection

The public home for my portable, self-contained skills for AI-assisted work. Each folder
is one skill: a manifest (`SKILL.md`), its reference files, and any code it needs.
Everything runs offline with plain Python. No accounts, no telemetry.

## Skills

| Skill | What it does |
|---|---|
| [anti-ai](./anti-ai/) | A regex linter that detects AI tells in prose: 442 patterns (EN/RO/FR), house-style calibration, and benchmarks from real human corpora |
| [blog-writer](./blog-writer/) | Multi-pass article pipeline: brief, sourced research, developmental edit, copy edit in the author's voice, fact-check loop, review gate. Lints its own drafts with anti-ai |
| [alexandru-style](./alexandru-style/) | AG Style v1.0: the design system distilled from alexandrugris.ro. Compact spec (`design-system.md`) plus the full brand toolkit under `brand/`: canonical tokens.css, style spec, working HTML templates, render/deck scripts and the reference sample gallery |

## Layout

    <skill-name>/
      SKILL.md          manifest: description, audit and writing instructions
      README.md         usage and background
      <code + data>     whatever the skill needs to run

## Using a skill

With an AI assistant that supports skills (e.g. Vibe), copy or install the skill folder.
Standalone use, for the `anti-ai` linter:

    python3 anti-ai/check_tells.py <file-or-dir> [--json] [--severity high]

Verdicts: `FAIL` (at least one HIGH AI tell), `REVIEW` (MEDIUM hits: can be good human
writing, judge by hand), `PASS`. The full calibration story behind those verdicts is in
[anti-ai/references/human-benchmarks.md](./anti-ai/references/human-benchmarks.md).

The brand toolkit in [alexandru-style/brand/](./alexandru-style/brand/) migrated from its
own repository (ag-personal-brand) on 2026-11-19. See
[alexandru-style/brand/TRANSFER-NOTES.md](./alexandru-style/brand/TRANSFER-NOTES.md) for
what crosses over as text and where the open-font binaries come from.

## License

MIT, see [LICENSE](./LICENSE). It covers the whole collection. Bundled font licenses
(SIL OFL 1.1) stay with their font family names.
