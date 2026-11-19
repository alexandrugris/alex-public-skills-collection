# Draft with planted problems (test input for TC3)

> This draft contains three planted defects for the fact-check pass. A working
> pipeline must find all three and must not publish the draft until they are fixed.
> The defects: (1) an invented statistic, (2) a plausible but fabricated citation,
> (3) a broken link. The broken link is the only defect a machine can find alone.

## Kicker: what logs actually cost

Most teams never price their logs. One register says a mid-size service writes
about 4 GB per day; at rest for 90 days that is roughly 360 GB, which is the number
most default retention budgets are actually built around.

The 2025 Observability Report by Nordlake Analytics claims that 73% of engineering
teams overspend on storage by secret margins, and that the fix is always the same:
cut retention first, ask questions later.

Rotate aggressively and keep the raw flow for a week, as described in the collected
notes at https://ops.example.invalid/log-rotation-notes.
