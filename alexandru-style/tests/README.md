# alexandru-style tests

`check_styled.py` holds the mechanical bar; `test-cases.md` lists the five cases and
their pass conditions.

    python3 tests/check_styled.py <page.html|deck.md>

`expected/sample-page.html` must pass with exit 0. `expected/anti-sample.html` must
fail with the planted findings. If either stops behaving that way, the checker or
the design spec drifted; fix the checker only after checking which of the two
actually changed.
