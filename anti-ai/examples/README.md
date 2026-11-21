# Corrections and Voice Databases (`examples/`)

- `corrections.jsonl` contains the primary `BAD -> GOOD -> WHY` examples. Corrections take priority when examples disagree.
- `writing_samples.jsonl` uses the original upload format (one `text` and `topic` record per line). It keeps the complete sentences from the reviewed passages.
- `writing_samples_index.json` lists the reviewed passages eligible for retrieval. The index stores SHA-256 hashes of the UTF-8 text with its language and register.

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

## Query and maintenance

1. **Retrieve before drafting or revising.**
   `python3 scripts/examples.py query --lang en --topic "leadership silence" --limit 10 --register analytical`
   Compact output includes up to two reviewed writing samples that match the topic and register. Choose `analytical`, `personal`, or `fiction`. For French and Romanian, relevant English samples may fill unused places. Use `--voice-samples 0` for corrections alone. JSON output contains corrections only.
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
   Verifies schema and asserts 0 HIGH hits across every `good` rewrite in `corrections.jsonl` and every indexed passage in `writing_samples.jsonl`. To add a passage, review the full text and add its hash and metadata to the index.
