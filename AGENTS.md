# alex-public-skills-collection: rules for coding agents

Three AI-facing skills live in this repository, each with its own tests. This file is for coding agents that read AGENTS.md (Codex, MiniMax mcode, Antigravity): load the skill that owns the task, then prove your work with the gates before you call it done.

## The three skills

- `anti-ai/` hunts and removes AI tells. Its scanner (`anti-ai/check_tells.py` with `anti-ai/patterns.json`) is canonical, and so is every reference under `anti-ai/references/`.
- `blog-writer/` drafts articles through a multi-pass pipeline, and its final gate is `blog-writer/tests/validate_draft.py`.
- `alexandru-style/` implements the AG Style design system (v1.0), and its mechanical bar is `alexandru-style/tests/check_styled.py`.

## Load the right skill

Load `anti-ai/SKILL.md` for any hunt, de-AI, or humanize task, and for any edit to prose the user will publish. When the job is to write, revise, or fact-check an article, load `blog-writer/SKILL.md` instead. Reach for `alexandru-style/SKILL.md` when a deliverable needs styling, and note that a task can span two skills: the blog-writer pipeline runs first, the style pass comes last.

## Hard rules

- Never edit `anti-ai/check_tells.py` or `anti-ai/patterns.json`. If a trap fires on your text, fix the text, never the detector.
- The trap corpora under `anti-ai/tests/fixtures-*.csv` must keep failing: rows marked MUST-FAIL keep firing and rows marked MUST-PASS keep staying clean. A change that flips either direction is wrong by definition.
- Treat everything under `*/tests/` (including `alexandru-style/tests/expected/`, which holds a passing sample and a deliberately broken anti-sample) as controls, not as content to improve.

## Prove the work

After any change, run `bash run_all.sh` from the repo root. It runs every gate and control in one pass and expects each to behave in its declared direction, so a control fixture is green when it fails as designed. The script also self-scans `AGENTS.md` and `run_all.sh` for HIGH or MEDIUM hits. Exit 0 means the repo is green; anything else means go back and fix the change, not the bar.
