# alexandru-style test cases

The machine-checkable bar lives in `check_styled.py`; the cases below run the skill
by hand and say exactly what to accept. Positive and negative controls sit in
`expected/`: a sample page that passes the checker and an anti-sample that must
fail it. The input for TC1 lives in `input/plain-notes.md`.

## TC1 A4 document from plain notes (input/plain-notes.md)

Request: "Make this a styled A4 document."

Pass when:
- The page or PDF passes `check_styled.py`.
- A4 and margins hold: 22mm sides, 166mm measure, paper ground, not white.
- The structure follows the document recipe: kicker, display title, lede, hairline,
  meta line (author, role, date), body 10.5pt / 1.58.

## TC2 Marp deck on a chosen topic

Request: "Make a six-slide Marp deck about this."

Pass when:
- The deck markdown passes `check_styled.py` (16:9, paper background, Georgia,
  paginate, burgundy accent, no emoji).
- Deck rules hold: one idea per slide, body at 14pt or larger, six bullets at most.

## TC3 HTML mini app or dashboard

Request: "Build a small dashboard page with this data."

Pass when:
- The page passes `check_styled.py`.
- The build is self-contained: inline CSS, no CDN fonts, no external assets.
- Burgundy marks accents and key figures only; tables carry the paper-warm header
  band with 1px hairline row rules.

## TC4 markdown canvas (structure without CSS)

Request: "Open a markdown canvas with these notes, in my style."

Pass when:
- Kicker line above the title in the "FROM THE TRENCHES · TOPIC · DATE"
  form, quiet uppercase section notes, middle-dot separators, register kept.
- No styling tokens leaked where markdown cannot carry them.

## TC5 negative control (expected must fail)

Run `check_styled.py expected/anti-sample.html` and confirm it fails with the
planted findings: white ground, heavy display type, gradient headline, text shadow,
dashed and doubled rules, centred copy, emoji. A checker that passes the anti-sample
is broken. Conversely `check_styled.py expected/sample-page.html` must pass clean.
