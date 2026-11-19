# Transfer notes (merge into this collection)

Merged 2026-11-19 from github.com/alexandrugris/ag-personal-brand (the source
repo will be deleted; this copy is the surviving one).

## What transferred verbatim (text)

Skill manifest (`SKILL.md`), `AGENTS.md`, `README.md`, `requirements.txt`,
`references/` (tokens.css, style-spec.md, assets-manifest.json),
`templates/` (page.html, document.html), all eight scripts, `samples/`
text files (README, manifest.json, validation.md) and the two original
sample HTML files, plus the three SIL OFL font licenses.

## What could not transfer as binaries (and how it is preserved)

The GitHub connector writing to this repo only handles text: a binary file
pushed through it is UTF-8-inflated and corrupt (measured on a 48,223-byte
PNG: 71,444 bytes came back; the corrupt test file was deleted). Binary
writes are therefore impossible through this path.

So the complete source snapshot (79 files, 9.4 MB: all 17 TTF fonts, the
original reference gallery PDF/PPTX/PNGs/ZIP, the regenerated outputs, and
the text assets) is preserved in `binaries-archive/` as base64 text in 11
parts, byte-identical to the official GitHub tarball and verified by full
read-back. See `binaries-archive/README.md` for the one-command restore and
the SHA-256 anchor.

## Consequences for the verification scripts

- `scripts/check.py` passes as-is (text assets, templates, slide palette).
- `scripts/fonts.py` works but finds no bundled TTFs until they are
  restored from the archive (then offline embedding and slide conversion
  work as in the original repo).
- `scripts/verify_samples.py` and `scripts/audit_assets.py` expect the full
  original layout with binaries; run them after restoring, or expect them
  to fail on missing assets.

## After deleting the source repo

`samples/original` and `samples/regenerated` binaries exist nowhere else
in extractable form except this archive (the fonts are also on Google
Fonts). Restore once, commit the binaries at their proper paths, and this
archive can be dropped.