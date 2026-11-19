# Skill checked against the original samples

Checked November 17, 2026 against 19 original files (including the recovered toolkit ZIP) downloaded from the shared task. No independent agent evaluation was performed in this check.

## Results

- **Integrity:** all 19 original files (including the recovered toolkit ZIP) have recorded SHA-256 checksums; verification passes.
- **Palette and CSS:** canonical `references/tokens.css` occurs verbatim in both original HTML files. The maintained document extracts that stylesheet to the shared link and preserves its document-specific layout and `body.doc` activation.
- **Slides:** a fresh run of `build_deck.py` matches the original PPTX in all nine slide XML trees, including text, coordinates, fills, rules, declared fonts, sizes and spacing. Deck dimensions and shape ordering also match. This does not compare ZIP metadata or rendering-engine output.
- **Render smoke checks:** the maintained toolkit generated a three-page document PDF and PNGs, a full-page web PNG, a nine-slide PPTX and LibreOffice PDF/PNGs in this workspace. Document pages 1–2 and title/content slide previews were inspected during packaging; the original overview, original document page 2 and original web preview were inspected during this audit.
- **Visual result:** the editorial structure and palette are retained. Pixel equivalence is **not established**. Initial renders substituted Noto Serif/OpenAI Sans. This was fixed by bundling licensed Gelasio and Inter, embedding them in HTML, and configuring Linux slide conversion locally. Font discovery and `pdffonts` confirm Gelasio/Inter in the regenerated PDFs. The bundled fonts are current static instances; the originals used older versions, so pixel equivalence is still not claimed.
- **Web asset gap:** both source HTML and the working template refer to `assets/hero-city-park.webp`, absent from the shared archive. The original web screenshot contains the photograph; the regenerated preview has the plain fallback background. Supply a suitable authorized asset for new work or intentionally adapt the design. Do not claim full reproduction of the web sample.

## Corrections made to the skill/specification

1. Corrected the slide top spine from 0.75in to the actual 0.055in; slide side margin is 0.95in.
2. Clarified sentence-case sans descriptions versus uppercase metadata; repeated principle rules are intentional.
3. Document principle grids can have four columns, matching the sample. Clarified smaller supporting slide copy and 9pt footers.
4. Required inspection of original references and explicit disclosure of missing fonts/assets. Removed the guarantee that font substitution never changes layout.
5. Preserved original-copy wording during visual-only work, and directed agents to edit working copies rather than canonical deck source.
6. Recorded legacy sample exceptions: ink masthead, bold web article titles and serif principle numerals. The idealized specification differs in these details; originals remain unchanged.
7. Corrected the contrast advice: test against the actual background, not just paper.

## Repeatable check and limits

`python scripts/verify_samples.py` checks source integrity, original shared CSS and freshly generated PPTX XML/text/geometry. It intentionally fails on a changed baseline. Update references only after deliberate review, never regenerate expected originals from current code to make a failure pass.

This check is structural evidence, not a universal visual regression test or proof that new content fits. For each new deliverable, verify font availability, render at the intended size, inspect every page/slide for overflow and collisions, and compare with the relevant original previews. When a brief intentionally adapts the style, judge the intended brand elements rather than pixel identity.

## Bundled-font rerender

`fonts/` includes 17 font files, family OFL licenses and a source/hash manifest.
A second render of the document, web and slides used the bundled fonts.
Document page 2 and slide 3 were visually inspected after this change; all
three document pages and nine slides were rendered. The results are saved in
`samples/regenerated/`, separately from the untouched originals.
HTML/PDF carries embedded fonts; PPTX relies on installed fonts when opened
elsewhere, while the bundled Linux preview command uses local Fontconfig.
The missing hero photograph remains the known web difference.

## Complete Git asset audit

`python scripts/audit_assets.py` verifies 52 shipped assets against a complete
SHA-256/size inventory and `git ls-files`, rejects Git LFS placeholders, checks
all three font-family licenses, and checks local resource dependencies in
maintained HTML/CSS. The 52 assets comprise 19 original files, 17 font files
and 16 regenerated outputs.

The original toolkit ZIP is now preserved as well. The maintained web template
no longer requests the unavailable photograph; it uses an intentional solid
background. Archived original HTML is unchanged, including its historical
missing photograph reference. This is the sole known unavailable source asset;
it was never part of the shared toolkit and is not claimed to be in Git.
