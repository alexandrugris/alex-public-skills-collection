# Bundled fonts

Gelasio (Georgia-compatible serif substitute), Inter, and IBM Plex Mono are
bundled under the SIL Open Font License 1.1. Georgia itself is proprietary and
is not redistributed. Keep each family's `*-OFL.txt` when copying these files.

Gelasio and Inter include static regular, medium, semibold and bold faces, plus
their italics. These were instantiated using fontTools 4.61.1 from Google Fonts
variable upstream files on November 17, 2026 (wght 400/500/600/700; Inter opsz 14).
IBM Plex Mono Regular is an unmodified upstream static font. `manifest.json`
records upstream URLs, source hashes, output hashes and axis coordinates.
The baseline original samples used older static fonts; the current bundled
versions may have subtle metric differences and are not claimed pixel-identical.

HTML rendering embeds these fonts directly as data URLs, including a local
Georgia-family alias to Gelasio. PDF and PNG output therefore work offline.
`inline_tokens()` returns the CSS with embedded fonts for standalone HTML.

For Linux slide conversion, `deck_shots.py` automatically supplies a private
Fontconfig configuration that finds these fonts and aliases Georgia to Gelasio.
The configuration and cache live under ignored `build/fonts/`; no home-directory
or system settings are modified. Verify discovery with `python scripts/fonts.py`.

PowerPoint does not embed these TTF files in the generated PPTX. On another
computer, install the bundled TTF files using that operating system's normal
font installer and use Gelasio when Georgia is absent, or view the rendered PDF.
For native web delivery, copy the fonts with their licenses and use @font-face,
or export self-contained HTML through `inline_tokens()`.
