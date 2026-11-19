# blog-writer test cases

Five cases cover the pipeline end to end. Cases 1 to 3 have machine-checkable
acceptance; run `python3 tests/validate_draft.py <draft.md>` on the produced draft.
Cases 4 and 5 are judged from the pipeline trace, not from one file.

## Setup for every case

Run from a live session with this skill loaded, the anti-ai sibling skill present,
and web search available for the research pass. Fixture inputs live under
`tests/input/`.

## TC1 write from scratch

Request: "Write a 900 to 1,200 word how-to article for my blog: how I moved my home
server to immutable Linux. First-person experience, but find and link real sources
for every external claim."

Pass when:
- The workflow confirms the brief first (topic, angle, reader, length, format, language).
- Every external claim in the draft carries an inline link to a real source.
- First-person observations do not carry citations.
- validate_draft.py exits 0 on the final draft.
- The review gate presents source list, findings and open gaps, and waits for approval.

## TC2 seed paragraph laced with tells (uses tests/input/seed-tell-paragraph.md)

Request: "Turn this fragment into a drafted section. Keep the engineer quote as a
quotation." The seed fires at least four HIGH hits on its own; a draft built by
copying it must fail the gate.

Pass when:
- The final section keeps the meaning and the quotation verbatim, with attribution.
- Seed phrases other than the quotation are rewritten, not preserved.
- validate_draft.py exits 0 on the rewritten section.

## TC3 planted defects (uses tests/input/draft-with-planted-fabrication.md)

Request: "Fact-check this draft before publication."

Pass when:
- The invented statistic (the "4 GB per day" line) is flagged as unverifiable.
- The fabricated citation (the "Nordlake Analytics" report) is flagged as not found.
- The broken link is flagged.
- No invented replacement source is offered for a claim that could not be verified:
  the fix is to delete or recast the claim.
- The gate blocks publication while a blocking finding is open.

## TC4 escalation to Pass 1

Request (to the copy editor only, skipping the developmental pass): "Draft this
argument: observability made our team faster. Here are three bullet points of
ideas." The material cannot support the argument structure.

Pass when:
- Pass 2 emits an `<escalation>` instead of forcing a draft.
- The pipeline routes it back to Pass 1, not to publication.

## TC5 handoff to alexandru-style

Request, after TC1 is approved: "Make this a styled page for the site."

Pass when:
- blog-writer hands presentation to the alexandru-style skill instead of styling
  by itself.
- The produced page passes the alexandru-style tests (see that skill's tests folder).
- Content edits, if any, go through the blog-writer pipeline, not the style pass.
