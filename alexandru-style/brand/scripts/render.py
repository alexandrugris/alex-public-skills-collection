#!/usr/bin/env python3
"""Render an AG-style HTML file to PDF and page images.

Usage:
    python3 render.py <input.html> <output.pdf> [--png-dir DIR] [--no-footer]

Resolves the `TOKENS_PATH` placeholder in the HTML by inlining the canonical
stylesheet, so the rendered file is self-contained and prints identically
anywhere.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess

from fonts import font_css

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = ROOT / "references" / "tokens.css"

FOOTER = """
<div style="width:166mm;margin:0 auto;border-top:1px solid #D8D4CA;padding-top:7px;
            font-family:Inter,Helvetica,Arial,sans-serif;font-size:7.4px;
            letter-spacing:.14em;text-transform:uppercase;color:#85857C;
            display:flex;justify-content:space-between;align-items:center;">
  <span>From The Trenches — Alexandru Gris</span>
  <span style="color:#8D2829;"><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>
"""


def inline_tokens(html: str) -> str:
    """Replace the stylesheet link (or TOKENS_PATH placeholder) with inline CSS."""
    css = font_css() + "\n" + TOKENS.read_text(encoding="utf-8")
    block = f"<style>\n{css}\n</style>"

    html = html.replace("TOKENS_PATH", TOKENS.as_uri())
    html = re.sub(
        r'<link[^>]+href="[^"]*tokens\.css"[^>]*>',
        block,
        html,
    )
    # A file:// link may still be present if the template used a relative path.
    html = re.sub(
        r'<link[^>]+href="(?!\w+:)[^"]*tokens\.css"[^>]*>',
        block,
        html,
    )
    return html


def _find_chromium() -> str | None:
    """Locate a Chromium binary; the Playwright cache may sit outside $HOME."""
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        found = shutil.which(name)
        if found:
            return found
    return None


def to_pdf(src: pathlib.Path, out: pathlib.Path, footer: bool) -> None:
    from playwright.sync_api import sync_playwright

    html = inline_tokens(src.read_text(encoding="utf-8"))
    exe = _find_chromium()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=exe,
            args=["--font-render-hinting=none", "--force-color-profile=srgb"],
        )
        page = browser.new_page()
        page.emulate_media(media="print")
        page.set_content(html, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        has_print_footer = page.locator("body.doc--flow, .page-footer").count() > 0
        browser_footer = footer and not has_print_footer
        page.pdf(
            path=str(out),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=browser_footer,
            header_template="<div></div>",
            footer_template=FOOTER if browser_footer else "<div></div>",
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        browser.close()


def to_png(pdf: pathlib.Path, outdir: pathlib.Path, dpi: int = 130) -> list[pathlib.Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob(f"{pdf.stem}*.png"):
        old.unlink()
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(outdir / pdf.stem)],
        check=True,
    )
    return sorted(outdir.glob(f"{pdf.stem}*.png"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("pdf")
    ap.add_argument("--png-dir")
    ap.add_argument("--no-footer", action="store_true", help="Disable the renderer footer for custom HTML")
    ap.add_argument("--dpi", type=int, default=130)
    args = ap.parse_args()

    src = pathlib.Path(args.html).resolve()
    out = pathlib.Path(args.pdf).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if not shutil.which("pdftoppm") and args.png_dir:
        print("pdftoppm missing", file=sys.stderr)

    to_pdf(src, out, footer=not args.no_footer)
    print(f"pdf  -> {out}")

    if args.png_dir:
        pngs = to_png(out, pathlib.Path(args.png_dir).resolve(), dpi=args.dpi)
        for p in pngs:
            print(f"png  -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
