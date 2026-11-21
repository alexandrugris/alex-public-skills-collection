# Source Verifier Test Cases

1. **Clean verified draft (`expected/clean-verified.md`)**: `python3 scripts/audit_sources.py tests/expected/clean-verified.md` exits 0 (`VERDICT: PASS`) and extracts multi-word quotes outside the opening scene into `quotes_to_verify`.
2. **Planted bibliographic defects (`input/bad-citations.md`)**: `python3 scripts/audit_sources.py tests/input/bad-citations.md` exits 1 (`VERDICT: FAIL`) and flags all four planted defects: secondary podcast URL cited as a study, inline/source year mismatch (1990 vs. 1989), dual-year conflation (`1991/2001`), and missing author surname (`IJOA (2026)`).
3. **Surgical fix passes guardrails**: Fixing a misquoted span and updating `## Sources` passes `scripts/guardrails.py check` (`diff <= 15%`, `shrink <= 10%`, headings and opening scene preserved).
4. **Collapse blocked by guardrails**: Deleting a section heading, altering the opening paragraph, shrinking body word count >10%, or rewriting >15% of body tokens causes `scripts/guardrails.py check` to exit 1 (`VERDICT: FAIL`).
5. **Bounded 2-loop adversarial dialogue**: A fresh read-only subagent audits Loop 1, the Custodian applies surgical fixes or primary-evidence rebuttals, Loop 2 checks only the delta, and execution halts unconditionally after Loop 2.
