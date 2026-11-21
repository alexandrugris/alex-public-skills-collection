# alex-public-skills-collection: rules for coding agents

Four AI-facing skills live in this repository, each backed by tests and bidirectional controls. Load the skill that owns the task, then prove your work with the gates before calling it done.

## The four skills

- `anti-ai/` hunts AI tells with `anti-ai/check_tells.py`, `anti-ai/patterns.json`, `anti-ai/references/`, and the corrections database (`anti-ai/examples/corrections.jsonl`, queried via `anti-ai/scripts/examples.py`).
- `blog-writer/` runs a six-pass article pipeline gated by `blog-writer/tests/validate_draft.py`.
- `source-verifier/` runs an optional, context-isolated adversarial audit of quotations, DOIs, and concept fidelity (`source-verifier/scripts/audit_sources.py` + `source-verifier/scripts/guardrails.py`), keeping revisions surgical so essays do not collapse.
- `alexandru-style/` implements AG Style v1.0, with canonical CSS tokens in `alexandru-style/brand/references/tokens.css` and a static checker in `alexandru-style/tests/check_styled.py`.

## Load the right skill

Load `anti-ai/SKILL.md` for any hunt, de-AI, or humanize task, and for any edit to prose the user will publish. When the job is to write, revise, or fact-check an article, load `blog-writer/SKILL.md` instead; before final approval it asks whether to invoke `source-verifier/SKILL.md` for an exact quote, DOI, and concept audit. Load `source-verifier/SKILL.md` directly whenever the user asks to audit citations or quotes on any finished draft. Reach for `alexandru-style/SKILL.md` when a deliverable needs styling, and note that a task can span multiple skills: `blog-writer` runs first, optional `source-verifier` runs before approval, and the style pass comes last.

## Hard rules

- Never edit `anti-ai/check_tells.py` or `anti-ai/patterns.json` during prose tasks: if a trap fires on your text, fix the text, never the detector (only touch scanner code or patterns when the user explicitly requests a versioned scanner release).
- Keep every row under `anti-ai/tests/fixtures-*.csv` in its declared direction: MUST-FAIL rows keep firing, and MUST-PASS rows keep staying clean.
- Treat `*/tests/expected/` and `*/tests/input/` as controls, not as prose to improve.
- Keep strictly four `SKILL.md` manifests in this repository (one per top-level skill folder, with `name` matching the folder name) and never add nested `SKILL.md` files under subdirectories.

## Prove the work

After any change, run `bash run_all.sh` from the repo root. It runs every skill gate, control fixture, brand offline check, and the repo-wide `tests/` unit suite in one pass, and it self-scans `AGENTS.md`, `run_all.sh`, and `README.md` for HIGH or MEDIUM hits. Exit 0 means green.
