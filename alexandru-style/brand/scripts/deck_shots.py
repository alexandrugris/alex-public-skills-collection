#!/usr/bin/env python3
"""Render a PPTX to per-slide PNGs.

PPTX -> PDF (soffice) -> PNG (pdftoppm). Conversion happens in a temp directory
so it never overwrites a PDF you already built with the same stem.

Usage:
    python3 deck_shots.py <deck.pptx> <out-dir> [--dpi 110] [--pdf]
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

from fonts import font_environment


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("outdir")
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--pdf", action="store_true", help="also keep the converted PDF")
    args = ap.parse_args()

    src = pathlib.Path(args.pptx).resolve()
    outdir = pathlib.Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    for tool in ("soffice", "pdftoppm"):
        if not shutil.which(tool):
            print(f"missing required tool: {tool}", file=sys.stderr)
            return 1

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", str(src), "--outdir", tmp],
            check=True, capture_output=True, timeout=300, env=font_environment(),
        )
        pdf = pathlib.Path(tmp) / (src.stem + ".pdf")
        if not pdf.exists():
            print("soffice produced no PDF", file=sys.stderr)
            return 1
        if args.pdf:
            shutil.copy(pdf, outdir / pdf.name)
        for old in outdir.glob(f"{src.stem}-*.png"):
            old.unlink()
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(args.dpi), str(pdf), str(outdir / src.stem)],
            check=True,
        )

    for p in sorted(outdir.glob(f"{src.stem}-*.png")):
        print(f"png  -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())