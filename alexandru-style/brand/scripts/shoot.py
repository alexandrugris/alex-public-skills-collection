#!/usr/bin/env python3
"""Screenshot an AG-style HTML page to PNG.

Usage:
    python3 shoot.py <input.html> <output.png> [--width 1440] [--full]
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from render import inline_tokens, _find_chromium  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("png")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--scale", type=float, default=1.0)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    src = pathlib.Path(args.html).resolve()
    out = pathlib.Path(args.png).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    html = inline_tokens(src.read_text(encoding="utf-8"))
    tmp = src.with_name(src.stem + ".shoot.html")
    tmp.write_text(html, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=_find_chromium(),
            args=["--font-render-hinting=none", "--force-color-profile=srgb"],
        )
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale,
        )
        page.set_content(html, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(400)
        page.screenshot(path=str(out), full_page=args.full)
        browser.close()
    tmp.unlink(missing_ok=True)
    print(f"png  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())