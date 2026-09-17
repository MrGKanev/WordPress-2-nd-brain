#!/usr/bin/env python3
"""Inject the cover, print CSS and generated TOC into mdBook's print.html."""

from pathlib import Path
import re
import shutil

from generate_toc_html import extract_h1_ids, generate_html, normalize, parse_summary


ROOT = Path(__file__).resolve().parents[1]
PRINT = ROOT / "book" / "print.html"


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit(f"Expected exactly one {label} marker in {PRINT}")
    return text.replace(old, new, 1)


def main():
    shutil.copy2(ROOT / "theme" / "pdf.css", ROOT / "book" / "pdf.css")

    html = PRINT.read_text(encoding="utf-8")
    html = replace_once(
        html,
        "</head>",
        '<link rel="stylesheet" href="pdf.css"></head>',
        "closing head",
    )
    html = replace_once(
        html,
        "<main>",
        '<main><div class="pdf-cover"><img src="cover.png" alt=""></div>',
        "main",
    )

    entries = parse_summary(ROOT / "SUMMARY.md")
    ids = extract_h1_ids(PRINT)
    unmatched = [title for _, title in entries if normalize(title) not in ids]
    if unmatched:
        raise SystemExit("Missing print anchors: " + ", ".join(unmatched))

    pattern = re.compile(
        r'<h1 id="wordpress-second-brain">.*?'
        r'<div style="break-before: page; page-break-before: always;"></div>',
        re.DOTALL,
    )
    html, replacements = pattern.subn(generate_html(entries, ids), html, count=1)
    if replacements != 1:
        raise SystemExit("Could not replace the introduction with the PDF TOC")

    PRINT.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
