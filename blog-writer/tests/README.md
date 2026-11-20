# blog-writer tests

Test cases live in `test-cases.md`; inputs in `input/`. The machine-checkable part
of the gate is `validate_draft.py`:

    python3 tests/validate_draft.py <draft.md> [--json] [--verify-urls]

It fails the draft if it has no title, a surviving `[NEEDS SOURCE]` marker, a banned
generic heading, a placeholder or `.invalid` URL, a missing or empty `## Sources`
section, an inline link absent from `## Sources`, or any HIGH hit from the anti-ai
scanner. MEDIUM hits are printed as warnings: REVIEW can be legitimate human writing,
judge by hand.

The script finds the scanner automatically (sibling `../anti-ai/check_tells.py`, or the
path in `ANTI_AI_SCANNER`).
