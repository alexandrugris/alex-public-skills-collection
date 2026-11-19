# Reference samples

These are the original files recovered from the [shared task](https://share.mcode.io/share/QpS1NFOUNzw86kqPPwt-6g), not newly generated approximations. `manifest.json` records SHA-256 checksums and sizes. Retrieved November 17, 2026. Content is illustrative reference copy, not verified biography or real measurements.

Start with the [overview](original/overview.png), then inspect the medium you need:

| Medium | Editable/source | Reference output | Previews |
|---|---|---|---|
| Style guide | [Written specification](../references/style-spec.md) | [Original 4-page PDF](original/AG-Style-Guide.pdf) | [Colour and type](original/AG-Style-Guide-2.png) |
| Document | [Original HTML](original/sample-document.html) | [Original 3-page PDF](original/sample-document.pdf) | [Page 1](original/sample-document-1.png), [Page 2](original/sample-document-2.png), [Page 3](original/sample-document-3.png) |
| Slides | [Original PPTX](original/sample-deck.pptx) | [Original 9-slide PDF](original/sample-deck.pdf) | [Title](original/slide-1.png), [Principles](original/slide-3.png), [Writing](original/slide-4.png), [Chart](original/slide-5.png), [Quote](original/slide-6.png), [Close](original/slide-9.png) |
| Web | [Original HTML](original/sample-page.html) | [Full-page reference](original/page-full.png) | Same full-page image |

![Original reference overview](original/overview.png)

Use the maintained templates and scripts for new work; leave `original/` untouched. The original HTML depends on local fonts and the page refers to a photograph absent from the archive. It is preserved for provenance, not presented as a standalone working demo.

Read [validation results and known differences](validation.md). Run:

```sh
python scripts/check.py
python scripts/verify_samples.py
```

## Regenerated with bundled fonts

[Document PDF](regenerated/document.pdf) · [PPTX](regenerated/deck.pptx) ·
[Slides PDF](regenerated/slides/deck.pdf) · [Web preview](regenerated/page.png).
Page and slide PNGs are in `regenerated/document/` and `regenerated/slides/`.
These show the maintained toolkit with bundled fonts; they do not replace
the original references. The web preview intentionally exposes the missing
hero image rather than substituting an unrelated photograph.

[Original toolkit ZIP](original/ag-trenches-style-kit.zip) is preserved too.
