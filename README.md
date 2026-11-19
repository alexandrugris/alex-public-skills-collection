# alex-public-skills-collection

The public home for my portable, self-contained skills for AI-assisted work. Each folder
is one skill: a manifest (`SKILL.md`), its reference files, and any code it needs.
Everything runs offline with plain Python. No accounts, no telemetry.

## Skills

| Skill | What it does |
|---|---|
| [anti-ai](./anti-ai/) | A regex linter that detects AI tells in prose: 442 patterns (EN/RO/FR), house-style calibration, and benchmarks from real human corpora |

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

## License

MIT, see [LICENSE](./LICENSE). It covers the whole collection.
