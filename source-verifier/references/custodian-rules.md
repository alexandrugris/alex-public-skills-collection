# Author / Custodian Response Rules

The Main Agent acts as Custodian of the essay's thesis, structure, and voice during the adversarial verification loop.

## Three typed moves per verifier ticket

For every `blocking` ticket in `<verification_ledger>`, execute exactly one move:

1. **`SURGICAL_FIX`**: Edit **only** the flagged span (the misquoted phrase, year, author name, link URL, or `## Sources` line). Leave surrounding sentences, transitions, and examples untouched.
2. **`DEQUOTE_PARAPHRASE`**: If a verbatim transcript or paywalled primary text cannot be confirmed character-for-character, remove the quotation marks and paraphrase the verified claim cleanly in plain voice. Never guess or reconstruct a quotation.
3. **`REBUT`**: If the Verifier erred (e.g., search-engine blind spot on a valid DOI or misread source passage), keep the text and return primary-source or Crossref API proof in `<custodian_response>`.

## Anti-collapse rules

- **Never panic-delete**: Do not delete an entire paragraph or argument because a citation was secondary or a quote drifted. Upgrade the link to the primary DOI/paper or switch to `DEQUOTE_PARAPHRASE`.
- **No academic footnote bloat**: Keep inline links clean and readable; put full bibliographic metadata (volume, issue, pages, publisher) in `## Sources`, not crammed into body prose.
- **Guardrail gate after every loop** (`<SKILL_DIR>` = `source-verifier` directory, `<SKILLS_DIR>` = its parent directory, `<revised.md>` = absolute path to the draft on disk):
  1. Run `python3 "<SKILL_DIR>/scripts/guardrails.py" check "<snapshot.json>" "<revised.md>"` (mandatory).
  2. If `guardrails.py` returns `FAIL` (dropped heading, altered opening paragraph, word-count drop `>10%`, or body token diff `>15%`), **roll back** and re-apply only the minimal span fixes.
  3. Run `python3 "<SKILL_DIR>/scripts/audit_sources.py" "<revised.md>" [--online]` to confirm zero mechanical blocking defects remain.
  4. **Optional sibling gates:** if `<SKILLS_DIR>/anti-ai/check_tells.py` exists, run `python3 "<SKILLS_DIR>/anti-ai/check_tells.py" "<revised.md>"` (must pass with 0 HIGH). If this audit was invoked from `blog-writer` (Step 5b) or targets a blog article and `<SKILLS_DIR>/blog-writer/tests/validate_draft.py` exists, run it too.
- **Stopping rule**:
  - If Loop 1 has `0 blocking` findings: done.
  - If Loop 1 had fixes or rebuttals: send **only** `<custodian_response>` + the revised draft to Loop 2 (delta-only check).
  - After Loop 2: stop unconditionally. Surface any remaining non-blocking notes or unresolved impasses directly to Alexandru at the human review gate.

## Response ledger format

```text
<custodian_response>
loop: 1 | 2
actions:
  - id: V1
    move: SURGICAL_FIX | DEQUOTE_PARAPHRASE | REBUT
    before: "..."
    after: "..."
    evidence: URL / DOI / Crossref record
guardrails: PASS (diff=X.X%, shrink=Y.Y%, headings=ok, opening=ok)
voice_gate: PASS (0 HIGH, 0 MEDIUM)
draft_gate: PASS
</custodian_response>
```
