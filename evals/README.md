# Skill Evals (Tiers 3 & 4)

Tiers 1 and 2 run offline on every commit via `bash run_all.sh` (spec validation, data
integrity, checker unit tests, fixtures, and corrections DB validation). This folder holds
the LLM-in-the-loop eval assets for Tiers 3 and 4.

## Tier 3: Trigger & routing evals (`triggers.csv`)

34 prompts across all four skills, multi-skill chains (`blog-writer+alexandru-style`,
`blog-writer+source-verifier`), and 10 negative controls (`should_trigger=false`). Run these prompts against your target
model/harness (Vibe, Claude Code, Codex, Antigravity) whenever you edit a `SKILL.md`
`description` field. Target: >= 95% trigger recall on positive prompts and <= 5% false
triggers on negative controls.

## Tier 4: Behavioral A/B evals (`cases.json` + `graders.py`)

Run each case in `cases.json` twice:
1. **Baseline run** (no skills loaded) -> save output to `baseline.md` or `baseline.html`.
2. **Skill run** (target skill loaded) -> save output to `skilled.md` or `skilled.html`.

Grade both artifacts deterministically first:

    python3 evals/graders.py --case blog-writer-tc2-seed --artifact skilled.md --json

Then score the remaining binary rubric items in `cases.json` by hand or with a pinned
judge model emitting strict JSON (`{"pass": true|false, "evidence": "..."}`).
