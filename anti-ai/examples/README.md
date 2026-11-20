# Corrections database (`examples/corrections.jsonl`)

This folder holds real AI-drafted passages alongside the author's rewrites and reasons.
The goal is simple: the skill learns from edits without bloating `SKILL.md` with hundreds
of lines of prose.

## Why JSONL

One JSON object per line keeps diffs clean, avoids merge conflicts, works in text-only
connectors, and runs with plain Python stdlib.

Schema fields per line:

- `id`: unique key (`ex-YYYY-MM-DD-NNN`)
- `date`: ISO date (`YYYY-MM-DD`)
- `lang`: `en`, `ro`, or `fr`
- `context`: `essay`, `headline`, `transition`, `scene`, `ending`, `memo`
- `bad`: the rejected AI sentence or paragraph
- `good`: the author's rewrite (must pass `check_tells.py` with 0 HIGH hits)
- `why`: one concrete reason the draft failed
- `rules`: list of rule IDs from `references/anti-ai-prompt.md`
- `pattern_ids`: scanner IDs that fired on `bad` (empty list if the scanner missed it)
- `tags`: topic and failure-mode keywords for retrieval
- `scanner_caught`: boolean, set automatically by `scripts/examples.py add`
- `status`: `logged`, `promoted_fixture`, `promoted_pattern`, or `few_shot_only`

## Closed learning loop

1. **Retrieve before drafting or revising (few-shot calibration):**
   `python3 scripts/examples.py query --lang en --topic "leadership silence" --limit 5`
   Pulls only the 5 closest past rewrites into the current turn.
2. **Capture after a human edit:**
   `python3 scripts/examples.py add --lang en --bad "..." --good "..." --why "..." --rules 1,1b --tags metaphor`
   Runs `check_tells.py` on both strings and rejects any `good` rewrite that triggers a HIGH tell.
3. **Mine scanner blind spots:**
   `python3 scripts/examples.py gaps`
   Groups every `scanner_caught: false` entry by tag so recurring taste misses graduate into new rules or patterns.
4. **Promote caught entries to fixtures:**
   `python3 scripts/examples.py promote-fixtures --dry-run`
5. **Validate in CI:**
   `python3 scripts/examples.py validate`
