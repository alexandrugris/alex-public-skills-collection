---
name: anti-ai
description: Detect and remove AI tells from English, Romanian, and French prose (dead metaphors, weight verbs, self-certified honesty, empty emotional adjectives, crime-novel register, lists disguised as prose, hedge clusters, filler openers, inflated or Latinate vocabulary, passive voice, closing morals). Load when writing, revising, humanizing, de-AI-ing, or auditing prose that must read as human. Do not load for pure code debugging, data transformation, or visual-only styling.
---

# anti-ai

Full rule set, portable for other models: `references/anti-ai-prompt.md` (and the short
version `references/anti-ai-short.md`).
Per-language annexes for the spoken-register rule: `references/lang-ro.md` and
`references/lang-fr.md` (equivalent tables, bad-to-good pairs, recalibration recipe).
Blocklist (canonical, versioned): `patterns.json`, next to the scanner.
House rules, calibrated on Alexandru's own blog voice (use as a template, then calibrate
your own): `references/house-style.md`.
Voice profile (Alex, measured on alexandrugris.ro and on 90 posts spanning 2008-2025):
`references/alex-style.md`.
Calibration benchmarks (human corpora; third-party sources anonymized):
`references/human-benchmarks.md`.
Corrections database (real bad-to-good rewrites for progressive few-shot retrieval):
`examples/corrections.jsonl`, managed by `scripts/examples.py` (see `examples/README.md`).

## Audit (fast)

Paths below treat `<SKILL_DIR>` as the folder holding this `SKILL.md`, while `<file-or-dir>` accepts any path on disk:

    python3 "<SKILL_DIR>/check_tells.py" <file-or-dir> [--json] [--cat chat,inflated] [--severity high] [--lang en|ro|fr]

Regression gate (trilingual trap corpus, one CSV per language):

    python3 "<SKILL_DIR>/check_tells.py" --fixtures "<SKILL_DIR>/tests/fixtures-en.csv" "<SKILL_DIR>/tests/fixtures-ro.csv" "<SKILL_DIR>/tests/fixtures-fr.csv"

Requirement: every MUST-FAIL row fires its pattern, every MUST-PASS row fires nothing. Full run (fixtures, heuristics, corrections DB, and self-scan of these docs):
`python3 "<SKILL_DIR>/tests/run_tests.py"`.

Verdicts: FAIL (any HIGH hit), REVIEW (MEDIUM hits present, zero HIGH), PASS otherwise (including LOW-only hits).
The scanner reports exemptions: quoted text, literal physical context, and honesty words referring to a person. For Markdown files, it masks YAML frontmatter, fenced code blocks, and URLs before scanning prose.
Guardrail: during prose tasks, if a rule fires on your draft, fix the text and never edit `check_tells.py` or `patterns.json`.

## Write and learn from edits

1. **Retrieve relevant past rewrites before drafting or revising** (top 10: topic matches plus general structural/taste constructs):
   `python3 "<SKILL_DIR>/scripts/examples.py" query --lang en --topic "<topic or tags>" --limit 10`
   French and Romanian queries fill unused slots with examples labeled `en`. Apply their editorial principles and write naturally in the requested language; do not copy or literally translate their wording.
2. **Apply the rules while drafting, then scan and fix what the scanner reports.**
   House rhythm: a sentence built as an enumeration (2+ items, or a semicolon series) may run long, the clause stays 12-22 words, and it must not become every sentence.
   Keep facts, numbers, and quotations unchanged.
   FAIL = heavy tells, almost surely AI-drafted. REVIEW can be good human writing: read `references/human-benchmarks.md` before you cut a flagged sentence.
3. **Capture new human rewrites into the database.** When the user rewrites a sentence or explains why a draft sounds machine-written, offer to log it:
   `python3 "<SKILL_DIR>/scripts/examples.py" add --lang <en|ro|fr> --bad "..." --good "..." --why "..." --rules <ids> --tags <tags>`
   Periodically run `python3 "<SKILL_DIR>/scripts/examples.py" gaps` to turn recurring uncaught misses into new rules or patterns.
