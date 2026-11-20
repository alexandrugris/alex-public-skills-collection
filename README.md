# alex-public-skills-collection

Portable, self-contained skills for AI-assisted writing, prose auditing, and personal brand styling. Each top-level folder holds one skill: a `SKILL.md` manifest, on-demand references, mechanical Python tools, and bidirectional tests.

Core linters, draft gates, the corrections database, and unit tests run offline with plain Python stdlib (no accounts, no telemetry). Optional PDF, screenshot, and PPTX rendering under `alexandru-style/brand/` uses Playwright, `python-pptx`, Poppler (`pdftoppm`), and LibreOffice (`soffice`).

## Skills at a glance

| Skill | Job | Mechanical gate |
|---|---|---|
| [anti-ai](./anti-ai/) | Multilingual (EN/RO/FR) prose linter (`patterns.json` + `check_tells.py`), measured house voice, human benchmarks, and a JSONL corrections database (`examples/`) | `python3 anti-ai/tests/run_tests.py` |
| [blog-writer](./blog-writer/) | Six-pass article pipeline: brief, multi-round deep research (10-15+ opened sources), developmental edit, copy edit in voice, fact-check loop, human review gate | `python3 blog-writer/tests/validate_draft.py <draft.md>` |
| [alexandru-style](./alexandru-style/) | AG Style v1.0 design system from alexandrugris.ro (`design-system.md`) plus the merged production toolkit in `brand/` (`tokens.css`, templates, render scripts) | `python3 alexandru-style/tests/check_styled.py <file>` |

## Architecture

Each skill follows the Agent Skills open specification: one thin `SKILL.md` manifest stays in context for routing, `references/` loads on demand, Python scripts handle deterministic checks, and `tests/` enforces controls in both directions (cases that must pass and cases that must fail).

```mermaid
flowchart TB
    U["User request"] --> AG["AGENTS.md routing"]
    AG -->|"De-AI / humanize / audit"| AA["anti-ai/<br/>SKILL.md · patterns.json · check_tells.py<br/>references/ · examples/corrections.jsonl"]
    AG -->|"Write / revise / fact-check article"| BW["blog-writer/<br/>SKILL.md · 4 pass references<br/>tests/validate_draft.py"]
    AG -->|"Style HTML, PDF, Marp, PPTX, table"| AS["alexandru-style/<br/>SKILL.md · design-system.md<br/>brand/tokens.css · render scripts"]

    BW <-->|"few-shot query + lint gate"| AA
    BW <-->|"medium constraints & overflow cuts"| AS
    AS -->|"lint kickers, ledes, captions"| AA
    AA --> GATE["bash run_all.sh<br/>9 controls + tests/ (24 unit tests)"]
    BW --> GATE
    AS --> GATE
```

## Execution flow: writing an article end to end

When a task spans content and presentation, all three skills work in one shared session context rather than as blind one-way steps: `alexandru-style` supplies medium constraints up front (paragraph cadence, kicker/lede shape, slide bullet caps), `blog-writer` runs multi-round research and drafting, `anti-ai` calibrates voice and blocks AI tells, and any layout overflow during rendering routes back to `blog-writer` Pass 2 without dropping sources.

```mermaid
flowchart LR
    B["1. Brief<br/>idea, reader, depth=deep,<br/>target medium, 1st-person vs external"] --> R["2. Deep Research loop (3-4 rounds)<br/>10-15+ opened sources: primary, blogs,<br/>Wikipedia leads, YouTube + 2-3 critiques"]
    R --> P1["3. Pass 1: Dev editor<br/>archetype + medium rules<br/>-> <structural_brief>"]
    P1 --> Q["4a. Few-shot retrieval<br/>examples.py query (top 3-5)<br/>from corrections.jsonl"]
    Q --> P2["4b. Pass 2: Copy editor<br/>prose in voice"]
    P2 -->|"<escalation> on bad outline"| P1
    P2 --> L["4c. anti-ai lint<br/>check_tells.py + sign-off"]
    L -->|"Any HIGH hit blocks"| P2
    L -->|"0 HIGH"| FC["5. Fact-check loop<br/>max 2 rounds"]
    FC -->|"Dead link / contradiction"| R
    FC -->|"Span wording fix"| P2
    FC -->|"0 blocking"| RG["6. Human review gate<br/>draft + sources + gaps"]
    RG -->|"Feedback routed by cause"| P1
    RG -->|"User edits prose"| DB["Log rewrite<br/>examples.py add"]
    RG -->|"Approved + styled output"| ST["7. alexandru-style<br/>HTML / A4 PDF / deck<br/>+ check_styled.py"]
    ST -->|"Overflow / cut copy"| P2
    ST -->|"New kickers / captions"| L
```

## How to write a blog article using these skills

1. **Confirm the Brief (Step 1).** Give the agent a topic, reader, target length, language, research depth (`deep` by default, or `standard` / `quick`), and target medium (Markdown, flowing A4 HTML/PDF, or Marp deck). Separate your own first-person experience (no external link needed) from external claims (primary source required).
2. **Run the Deep Research Loop (Step 2).** Before any outlining, the agent runs 3-4 bounded rounds across primary papers/docs, practitioner blogs, Wikipedia (used only as a map to follow its primary citations), and YouTube talks/interviews (with transcript inspection and timestamped URLs). Default `deep` mode opens **10-15+ distinct URLs** and **2-3+ counter-arguments**, logging everything in `<research_brief>` and tagging unresolved items `[NEEDS SOURCE]`.
3. **Review `<structural_brief>` from Pass 1 (Step 3).** Pass 1 chooses an archetype (Trenches story, Argument essay, Diataxis how-to, or Explanation) while respecting the target medium's layout rules from `alexandru-style/design-system.md`.
4. **Calibrate, Draft, and Lint in Pass 2 (Step 4).**
   - **4a (`examples.py query`):** Right before writing prose, Pass 2 queries `anti-ai/examples/corrections.jsonl` for the top 3-5 past human rewrites matching the topic and language. That loads your concrete taste (~220 tokens) without bloating `SKILL.md`.
   - **4b–4c (Draft + `check_tells.py`):** Pass 2 writes the draft, runs `anti-ai/check_tells.py` and `blog-writer/tests/validate_draft.py`, fixes every HIGH hit, and checks headings, literal word sense, and endings by hand.
5. **Run the Fact-Check Loop (Step 5, max 2 rounds).** Every external claim and URL faces read-only verification. Unverifiable claims leave the draft or get recast; the pipeline never invents a replacement link.
6. **Approve at the Review Gate, then Style (Steps 6–7).** Nothing ships before your sign-off. When `alexandru-style` renders the HTML/A4 PDF/deck, any new UI copy (kickers, ledes, captions) goes through `anti-ai`, any overflow cuts route back to Pass 2, and `alexandru-style/tests/check_styled.py` verifies the output.

## Worked example: Gianpiero Petriglieri on leadership

Below is an end-to-end run in pipeline order for the prompt: *"Write a short blog piece on Gianpiero Petriglieri's leadership ideas (holding and identity workspaces), lint it, validate it, and style it as a flowing A4 HTML page."*

### Step 1 & Step 2: Brief + Research brief (opened sources)

The Brief sets `language: en`, `target_medium: a4-html`, and `depth: standard` (a compact section rather than a 2,000-word essay). The Research pass searches and opens primary sources and counter-views to build `<research_brief>`:

```text
<research_brief>
depth: standard
sources_opened_count: 5
claims:
  - claim: In a crisis, people already want to act and need "holding" (naming emotions, giving context and reality) before a lofty vision.
    stance: support
    source_type: primary
    url: https://hbsp.harvard.edu/product/H05KQR-PDF-ENG
    date: 2020-04-22
  - claim: Organizations act as "identity workspaces" (with Jennifer Petriglieri) that shape who people become; "nomadic professionals" gain mobility yet struggle to win trust.
    stance: support
    source_type: primary
    url: https://thinkers50.com/blog/new-leadership/
    date: 2016
counter_arguments:
  - claim: Leaders who lean on outside peer communities or "holding" without clear execution targets risk seeming detached from local accountability.
    url: https://thinkers50.com/blog/new-leadership/
    why_it_matters: Prevents treating holding as soft therapy rather than clear reality-testing.
gaps: []
</research_brief>
```

*(For a full-length `deep` article, Step 2 expands to 10-15+ opened URLs across HBR, INSEAD working papers, practitioner blogs, Wikipedia leads, YouTube talks with timestamps, and 2-3 independent critiques.)*

### Step 3 & Step 4a: Pass 1 outline -> Retrieve past rewrites (`examples.py query`)

After Pass 1 delivers `<structural_brief>` (Trenches/Explanation hybrid with A4 kicker, lede, and 3 short sections), Pass 2 runs `examples.py query` **before writing prose**:

```sh
python3 anti-ai/scripts/examples.py query --lang en --topic "leadership holding petriglieri" --limit 3
```

Actual output retrieved from `anti-ai/examples/corrections.jsonl` (~220 tokens):

```text
[ex-2026-11-19-012 | en | rules:1,2 | tags:abstraction,press-release,leadership,taste]
  BAD : Good leadership means balancing empathy with accountability across every level of the organization.
  GOOD: A manager has to hear what worries the team and still cut the project that loses money.
  WHY : Press-release abstraction ('balancing empathy with accountability') uses zero banned regex words yet says nothing concrete; name the exact conflicting actions.
[ex-2026-11-19-002 | en | rules:1,1b | tags:headline,metaphor,leadership]
  BAD : The restructuring that was right on paper still landed as a threat.
  GOOD: Silence at the all-hands was not agreement.
  WHY : Stock-pair headline mixing two clichés ('on paper' + 'landed as'); state the concrete scene event instead.
[ex-2026-11-19-001 | en | rules:1,1b | tags:metaphor,expansion,leadership]
  BAD : Care widens the room people have to think and act.
  GOOD: Care means people can decide, disagree and act without you in the room.
  WHY : Dead spatial metaphor ('widens the room'); deleting it leaves a gap, so expand into concrete actor behavior while keeping 'room' literal.
```

### Step 4b–4c: Outcome comparison (raw AI draft vs skills pipeline)

A typical unguided model draft on the same topic fails `anti-ai/check_tells.py` with **8 HIGH, 4 MEDIUM, and 4 LOW hits**:

```markdown
# Leadership in Crisis

In today's fast-paced world, it is important to note that leadership has undergone a pivotal shift. Gianpiero Petriglieri delves into the intricate tapestry of crisis management, arguing that holding carries the weight of organizational trust. Ultimately, leaders must leverage empathy to unlock human potential and foster a culture of resilience.
```

```text
$ python3 anti-ai/check_tells.py raw_ai_draft.md
by severity: {'high': 8, 'medium': 4, 'low': 4}
VERDICT: FAIL
```

Running the full `blog-writer` + `anti-ai` pipeline yields a sourced, human-register draft (first pass caught 2 MEDIUM hits on `"what happens next"` and `"on paper"`, which Pass 2 tightened before sign-off):

```markdown
FROM THE TRENCHES · LEADERSHIP · 2026-11-20

# During a crisis, people need clear ground before a vision.

When revenue drops and teams brace for cuts, a bright slide deck about next year misses the room. People already want to act; they lack a clear read on what the numbers mean for their job.

## Holding comes before vision.

Gianpiero Petriglieri, an organizational behavior professor at INSEAD who trained as a psychiatrist, calls that missing work "holding." In his April 2020 Harvard Business Review piece, [The Psychology Behind Effective Crisis Leadership](https://hbsp.harvard.edu/product/H05KQR-PDF-ENG), he argues that people in a crisis already want to act. A manager who holds names the pressure, states the facts on the table, and names the next step. That lets the team put its energy into real tasks rather than rumors.

## Workplaces shape who people become.

In a [Thinkers50 interview with Stuart Crainer](https://thinkers50.com/blog/new-leadership/), Petriglieri calls organizations "identity workspaces," a term he developed with Jennifer Petriglieri. Companies assign tasks, and they also shape how people see themselves at work. He also warns about "nomadic professionals": mobile managers who collect credentials across firms look qualified by resume alone, yet struggle to win trust from teams that stay put.

## What changes on Monday morning.

Before pitching a three-year roadmap to an anxious team, write down three facts: what changed, what stays intact, and who decides next. People remember how managers spoke when loss sat on the table.

## Sources

- [Gianpiero Petriglieri: The Psychology Behind Effective Crisis Leadership (Harvard Business Review, 2020)](https://hbsp.harvard.edu/product/H05KQR-PDF-ENG)
- [Thinkers50: The New Leadership, interview with Gianpiero Petriglieri](https://thinkers50.com/blog/new-leadership/)
```

### Step 5–7: Fact-check, style handoff, and gate verification

```text
$ python3 anti-ai/check_tells.py petriglieri_holding.md
by severity: {'low': 1}
VERDICT: PASS

$ python3 blog-writer/tests/validate_draft.py petriglieri_holding.md
VERDICT: PASS

$ python3 alexandru-style/tests/check_styled.py petriglieri_holding.html
VERDICT: PASS
```

Rendering the styled HTML to a print-ready A4 PDF with proofing PNGs takes one command:

```sh
python3 alexandru-style/brand/scripts/render.py petriglieri_holding.html petriglieri_holding.pdf --png-dir previews/
```

## How to improve the `anti-ai` database and other rules

The skills improve through a closed loop instead of bloating `SKILL.md` with endless prose rules.

```mermaid
flowchart LR
    E["User edits a draft<br/>or rejects AI phrasing"] --> ADD["1. Capture<br/>examples.py add<br/>(auto-scans bad + good)"]
    ADD --> DB["examples/corrections.jsonl<br/>(git-native JSONL)"]
    DB --> Q["2. Retrieve on future runs<br/>examples.py query (top 3-5)"]
    DB --> G["3. Audit blind spots<br/>examples.py gaps"]
    G -->|"Repeats 3+ times & regex-able"| PAT["4a. Graduate to patterns.json<br/>+ bump version + CSV fixtures"]
    G -->|"Pure semantic taste"| FS["4b. Keep as few_shot_only<br/>in corrections.jsonl"]
    DB -->|"Caught by existing pattern"| FIX["4c. promote-fixtures<br/>-> fixtures-{en,ro,fr}.csv"]
    PAT --> GATE["bash run_all.sh"]
    FIX --> GATE
```

### Growing the `anti-ai` corrections database

1. **Log every real edit you make.** When you rewrite an AI sentence, record the `bad` text, your `good` rewrite, and `why`:

```sh
python3 anti-ai/scripts/examples.py add \
  --lang en \
  --bad "Good leadership means balancing empathy with accountability." \
  --good "A manager hears what worries the team and still cuts the project that loses money." \
  --why "Press-release abstraction with zero banned words; name the concrete conflicting actions." \
  --rules 1,2 \
  --tags abstraction,leadership,taste
```

`examples.py add` runs `check_tells.py` on both strings automatically. It records whether the scanner caught `bad` (`scanner_caught: true|false`) and rejects `good` if your rewrite triggers a HIGH tell.

2. **Mine scanner blind spots periodically:**

```sh
python3 anti-ai/scripts/examples.py gaps
```

Entries with `scanner_caught: false` group by tag. When the same pattern repeats across several drafts and has a reliable textual shape, add a versioned rule to `anti-ai/patterns.json` (plus a MUST-FAIL and MUST-PASS pair in `anti-ai/tests/fixtures-{en,ro,fr}.csv` and a concise note in `anti-ai/references/anti-ai-prompt.md`). Pure semantic taste (scene detail, press-release tone, poster morals) stays in `corrections.jsonl` with `status: "few_shot_only"` so `examples.py query` returns it on demand.

3. **Promote caught entries to permanent regression tests:**

```sh
python3 anti-ai/scripts/examples.py promote-fixtures --dry-run
```

### Updating `blog-writer` and `alexandru-style` rules

- **`blog-writer`:** When a failure repeats across drafts (for instance, a new banned heading shape or broken link pattern), add the prose instruction to the pass file that owns it (`research.md`, `developmental-editor.md`, `copy-editor.md`, or `fact-checker.md`), encode the mechanical part in `blog-writer/tests/validate_draft.py`, and add a unit test in `tests/test_checkers_unit.py`.
- **`alexandru-style`:** Edit `alexandru-style/brand/references/tokens.css` first (the single source of truth), mirror any color token change in `alexandru-style/design-system.md`, enforce new mechanical constraints in `alexandru-style/tests/check_styled.py`, and run `bash run_all.sh` (which verifies token sync, all three HTML templates, and the archive SHA-256).
- **Routing and end-to-end evals (`evals/`):** When you edit a `SKILL.md` `description` field, test routing against `evals/triggers.csv` (30 prompts including 10 negative controls). When you change workflow behavior, grade baseline vs skill-enabled outputs with `python3 evals/graders.py --case <id> --artifact <file>`.

## Repository layout & verification

```text
anti-ai/
  SKILL.md                     manifest: trigger description, audit & learning loop
  check_tells.py               multilingual scanner, heuristics, and fixture runner
  patterns.json                canonical versioned blocklist (EN/RO/FR)
  examples/corrections.jsonl   append-only human rewrites database
  scripts/examples.py          query, add, gaps, promote-fixtures, validate CLI
  references/                  portable prompts, house voice, benchmarks, RO/FR annexes
  tests/                       trilingual CSV fixtures, heuristics, and self-scan
blog-writer/
  SKILL.md                     six-pass pipeline manifest
  references/                  research (deep multi-round), developmental-editor, copy-editor, fact-checker
  tests/                       validate_draft.py + positive/negative draft controls
alexandru-style/
  SKILL.md                     AG Style v1.0 manifest
  design-system.md             compact spec synced to brand/references/tokens.css
  brand/                       canonical tokens.css, style-spec, templates, render scripts, archive
  tests/                       check_styled.py + sample/anti-sample controls
tests/                         repo-wide spec, schema, token-sync, and checker unit tests
evals/                         Tier 3 trigger prompts and Tier 4 behavioral graders
run_all.sh                     one-command offline gate (runs in CI on every push/PR)
```

Prove any change with one command:

```sh
bash run_all.sh
```

The brand toolkit in [alexandru-style/brand/](./alexandru-style/brand/) migrated from `ag-personal-brand` on 2026-11-19. Its binary snapshot (17 OFL fonts, reference PDFs, sample deck, and screenshots) lives in [alexandru-style/brand/binaries-archive/](./alexandru-style/brand/binaries-archive/), and `run_all.sh` verifies its SHA-256 automatically.

## License

MIT, see [LICENSE](./LICENSE). It covers the whole collection. Bundled font licenses (SIL OFL 1.1) stay with their font family names.
