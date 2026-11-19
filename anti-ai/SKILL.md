---
name: anti-ai
description: Detect and remove AI tells from English (and Romanian/French) prose: metaphors without literal meaning, weight verbs, self-certified honesty, empty emotional adjectives, crime-novel register, lists disguised as prose, hedge clusters, filler openers, inflated vocabulary, complex words with simple equivalents, closing morals. Use when writing or revising prose that must read as human, or when asked to humanize, de-AI, or audit a draft.
---

# anti-ai

Full rule set, portable for other AIs: `references/anti-ai-prompt.md` (and the short
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

## Audit (fast)

    python3 check_tells.py <file-or-dir> [--json] [--cat chat,inflated] [--severity high]

Regression gate (trilingual trap corpus, one CSV per language):

    python3 check_tells.py --fixtures tests/fixtures-en.csv tests/fixtures-ro.csv tests/fixtures-fr.csv

Requirement: every MUST-FAIL row fires its pattern, every MUST-PASS row fires nothing.

Verdicts: FAIL (any HIGH hit), REVIEW (MEDIUM hits present), PASS otherwise.
Exemptions are reported: quoted text, and literal context (a word is allowed when the
sentence is about the physical thing).

## Write

Apply the rules while drafting, not after. Then run the scanner and fix what it reports.
House rhythm: a sentence built as an enumeration (2+ items, or a semicolon series) may
run long, the clause stays 12-22 words, and it must not become every sentence.
Keep facts, numbers and quotations unchanged.
FAIL = heavy tells, almost surely AI-drafted. REVIEW can be good human writing: read
the benchmarks file before you cut a flagged sentence.
