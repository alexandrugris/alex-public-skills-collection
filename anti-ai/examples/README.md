# Corrections and Voice Databases (`examples/`)

This folder holds two JSONL files managed by `scripts/examples.py`:
- `corrections.jsonl`: real AI-drafted passages alongside the author's rewrites and reasons (`BAD -> GOOD -> WHY`).
- `voice_samples.jsonl`: 981 selected, deduplicated human passages across six topics (`leadership`, `fiction`, `management`, `engineering`, `product`, `life`) and five structural roles (`observation`, `scene`, `question_hook`, `tradeoff`, `colon_pivot`), verified at 0 HIGH hits.

The goal is simple: the skill calibrates both what to avoid (`corrections.jsonl`) and what authentic human cadence looks like (`voice_samples.jsonl`) without bloating `SKILL.md`.

## Why JSONL

One JSON object per line keeps diffs clean, avoids merge conflicts, works in text-only
connectors, and runs with plain Python stdlib.

Schema fields in `corrections.jsonl`:

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

Schema fields in `voice_samples.jsonl`:

- `id`: unique key (`vs-NNNN`)
- `lang`: `en`, `ro`, or `fr`
- `topics`: non-empty list of topic tags (`leadership`, `fiction`, `management`, `engineering`, `product`, `life`)
- `role`: `observation`, `scene`, `question_hook`, `tradeoff`, or `colon_pivot`
- `words`: word count
- `med_hits`: count of MEDIUM notes (0 HIGH required for every entry)
- `text`: verbatim human passage used as a cadence and rhythm reference

## Closed learning loop

1. **Retrieve before drafting or revising (dual few-shot calibration):**
   `python3 scripts/examples.py query --lang en --topic "leadership silence" --limit 10`
   Pulls up to 10 `BAD -> GOOD` rewrites plus 6 topic-matched positive voice samples (including 1 scene snippet for opening texture; pass `--voice-samples 0` to omit voice samples).
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
   Verifies schema and asserts 0 HIGH hits across every `good` rewrite in `corrections.jsonl` and every passage in `voice_samples.jsonl`.
