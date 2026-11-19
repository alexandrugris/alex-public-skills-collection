# anti-ai

A regex-based linter that detects AI tells in prose: the phrases, structures and
registers that give machine-written text away. Built and calibrated against real
human corpora, not just against AI output.

## Why

The obvious AI tells are not grammar mistakes. They are habits: metaphors whose
dictionary sense does not survive in context, weight verbs, self-certified honesty,
empty emotional adjectives, crime-novel register, lists disguised as prose, hedge
clusters, inflated vocabulary, and a closing moral. A model draft trips several of
these in a thousand words; human writing trips almost none (see
`references/human-benchmarks.md`).

## Usage

    python3 check_tells.py <file-or-dir> [...] [--json] [--cat chat,inflated] [--severity high] [--density]

Verdicts:

- **FAIL** (exit report): at least one HIGH hit. Almost surely machine-drafted text, or
  prose with heavy tells. Fix before publishing.
- **REVIEW**: MEDIUM hits present. Can be perfectly good human writing: judge by hand.
- **PASS**: nothing above LOW.

Exemptions are reported, never silently dropped: quoted text, and literal context (a
word is allowed when the sentence is actually about the physical thing: a bridge that
carries the weight of three trucks is fine).

## The pattern file

`patterns.json` (442 patterns, versioned) is the canonical blocklist. Categories:
`metaphor` (words without literal meaning), `weight` (carries the weight of / anchors /
underpins / grants...), `inflated` (corporate inflation), `hedge`, `honesty`
(self-certified sincerity, allowed when describing a person), `vague` (empty emotional
adjectives), `structure` (shapes that self-confess: binaries, aphorisms, abstract
chains), `list` (bullet lists disguised as prose), `chat` (assistant residue),
`complex` (words with a simpler equivalent), `house` (see below) and `dramatic`.
Romanian and French tells are included (`lang: ro|fr`).

Labels and fix suggestions are in Romanian; the rules themselves are language-agnostic
and the code adapts to new patterns without changes.

## House rules

`house` is a different animal: not AI tells, but *your* personal rhythm, measured on
*your* clean writing (sentence length bands, em-dash budget, word length, metronome
detection). The shipped `references/house-style.md` is one real example, calibrated on
a personal blog corpus (90 posts, 2008-2025), including the two-era voice drift and the
hard confirmations (one true em-dash in 55,700 words; "term - description" lines are
list syntax, not pauses). Use it as a template: measure your own corpus, replace the
numbers.

## Calibration evidence

The FAIL/REVIEW split was validated in both directions:

| Corpus | Verdict |
|---|---|
| AI draft (~1k words) | FAIL, 3 HIGH |
| Human blog, recent era (10.5k words) | 9 REVIEW, 4 FAIL (0.4 HIGH/k) |
| Human internal memo (5.1k words) | REVIEW, 0 HIGH |
| Human unedited work doc (1.5k words) | REVIEW, 0 HIGH |

Unedited human text wins REVIEW, not PASS: single blocklist words at low density
(holistic, cutting edge, important) are noise; density and empty second clauses are the
tells. Read `references/human-benchmarks.md` before cutting anything a REVIEW verdict
flags.

## Portable rule set

- `references/anti-ai-prompt.md` - full rules, pasteable into any model prompt
- `references/anti-ai-short.md` - the short version

## Limitations

It is a linter, not a judge. Regexes overreach by design; exemptions cover quotes and
literal contexts, and REVIEW exists because the human call stays yours. In work-related
register (memos, design docs) the `complex` category fires as register noise: LOW, ignore.

## License

TBD by the author.
