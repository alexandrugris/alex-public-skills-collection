"""Structural-heuristic regression cases (the CSV fixtures only exercise phrase
patterns, because run_fixtures() calls scan(); these cover the heuristics).

Run: python3 tests/test_heuristics.py   -> exit 0 = all asserts hold.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_tells as ct  # noqa: E402

# The pre-fix snapshot paragraph: mirrored author summaries interleaved with
# answer sentences (19 / 11 / 23 / 10 words) - must fire the mirrored heuristic.
V1 = (
    "Gianpiero Petriglieri asks what a company does to people whose sense of who they are is still being formed. "
    "His answer: leadership happens where meaning, belonging and direction get made. "
    "Manfred Kets de Vries asks what happens when leaders and followers slide into old patterns: the leader gets adored, leaned on and feared. "
    "Both sides usually cannot see the pattern they are in."
)

# The fixed paragraph: varied shapes and lengths, no mirrored template - must stay clean.
V2 = (
    "Gianpiero Petriglieri starts from the person, not the org chart. "
    "He asks what a company does to people whose sense of who they are is still being formed, and his answer is that leadership happens where meaning, belonging and direction get made. "
    "Manfred Kets de Vries looks at the bond between leader and follower: when the two fall into old patterns, the leader adored, leaned on and feared, neither side usually sees the pattern they are in."
)

# Adjacent long pair (18-30 words each, both name-start) - must fire parallel_pair_long.
PAIR = (
    "Gianpiero Petriglieri asks what a company does to people whose sense of self is still being formed in the role. "
    "Manfred Kets de Vries asks what happens when leaders and followers fall into old patterns of control and fear."
)


def note_ids(text):
    notes = (
        ct.structural_heuristics(text, "x")
        + ct.parallel_list_notes(text, "x")
        + ct.mirrored_summary_notes(text, "x")
        + ct.house_style_notes(text, "x")
    )
    return {n["id"] for n in notes}


failures = []
if "list.mirrored_summaries" not in note_ids(V1):
    failures.append("V1 mirrored paragraph not caught: %s" % sorted(note_ids(V1)))
if "list.mirrored_summaries" in note_ids(V2):
    failures.append("V2 clean paragraph false-fired")
if "list.parallel_pair_long" not in note_ids(PAIR):
    failures.append("adjacent name pair not caught")
if "list.parallel_pair_long" in note_ids(V2):
    failures.append("V2 false-fired parallel_pair_long")

if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("heuristics: 4/4 cases in declared direction")
