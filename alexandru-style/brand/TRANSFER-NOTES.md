# Transfer notes (merge into this collection)

Merged 2026-11-19 from github.com/alexandrugris/ag-personal-brand (the source
repo will be deleted; this copy is the surviving one).

Everything textual was transferred verbatim: skill manifest, spec, tokens,
templates, scripts, sample HTML, font licenses. What could not come along:

- `fonts/*.ttf` (17 binary font files). All are open fonts, downloadable from
  Google Fonts: Gelasio, Inter, IBM Plex Mono. Their SHA-256 hashes, sizes and
  upstream sources are recorded in `references/assets-manifest.json`.
- `samples/original/` binaries (PDFs, PPTX, PNGs, toolkit ZIP) and
  `samples/regenerated/` outputs. Their checksums are recorded in
  `samples/manifest.json`; the HTML sources are included here.

Consequences for the verification scripts, when run from this folder:
- `scripts/check.py` passes (text assets, templates, slide palette).
- `scripts/fonts.py` works but finds no bundled TTFs; download them into
  `fonts/` to enable offline embedding and slide conversion.
- `scripts/verify_samples.py` and `scripts/audit_assets.py` require the full
  original repo with binaries; on this text-only copy they will fail on the
  missing assets. That is expected.