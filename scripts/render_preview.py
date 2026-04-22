#!/usr/bin/env python3
"""Render .docx -> .pdf (and optional PNG) for 1-page visual verification.

Requires LibreOffice (`soffice`). Optional: `pdftoppm` for PNG preview and
`pdfinfo` for page-count reporting.

Usage:
    render_preview.py INPUT.docx [--out-dir DIR] [--png]

Exit code 2 if the resulting PDF exceeds one page.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def which_or_fail(cmd: str) -> str:
    path = shutil.which(cmd)
    if not path:
        sys.exit(f"ERROR: '{cmd}' not found in PATH. Install LibreOffice (provides 'soffice').")
    return path


def docx_to_pdf(docx: Path, out_dir: Path) -> Path:
    which_or_fail("soffice")
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(docx)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    pdf = out_dir / (docx.stem + ".pdf")
    if not pdf.exists():
        sys.exit(f"ERROR: LibreOffice did not produce {pdf}")
    return pdf


def page_count(pdf: Path) -> int | None:
    if not shutil.which("pdfinfo"):
        return None
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.lower().startswith("pages:"):
            return int(line.split(":", 1)[1].strip())
    return None


def render_png(pdf: Path, out_dir: Path) -> Path | None:
    if not shutil.which("pdftoppm"):
        print("pdftoppm not available; skipping PNG preview.")
        return None
    stem = pdf.stem
    subprocess.run(
        ["pdftoppm", "-png", "-r", "120", str(pdf), str(out_dir / stem)],
        check=True,
    )
    # pdftoppm writes <stem>-1.png, <stem>-2.png, etc.
    png = next(out_dir.glob(f"{stem}-*.png"), None)
    return png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", type=Path)
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="Directory for generated PDF (default: docx's parent)")
    ap.add_argument("--png", action="store_true",
                    help="Also render first page as PNG preview")
    args = ap.parse_args()

    docx = args.docx.resolve()
    if not docx.exists():
        sys.exit(f"File not found: {docx}")
    out_dir = (args.out_dir or docx.parent).resolve()

    pdf = docx_to_pdf(docx, out_dir)
    pages = page_count(pdf)
    print(f"PDF: {pdf}  pages={pages if pages is not None else '?'}")
    if args.png:
        png = render_png(pdf, out_dir)
        if png:
            print(f"PNG: {png}")

    if pages is not None and pages > 1:
        print(f"WARNING: {pages} pages. One-page abstract constraint violated.")
        sys.exit(2)


if __name__ == "__main__":
    main()
