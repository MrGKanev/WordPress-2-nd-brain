#!/usr/bin/env python3
"""Fail when a local Markdown or rendered HTML link is broken.

External URLs are deliberately skipped: their availability is volatile and should
be checked separately from the deterministic repository validation.
"""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]+)?\)")


def is_local_target(target):
    return not target.startswith(("http://", "https://", "mailto:", "/"))


class HTMLPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])


def markdown_errors():
    errors = []

    for source in ROOT.rglob("*"):
        if not source.is_file() or source.suffix.lower() != ".md":
            continue
        if "book" in source.parts:
            continue

        for target in LINK_RE.findall(source.read_text(encoding="utf-8")):
            if not is_local_target(target):
                continue

            destination = (source.parent / target).resolve()
            if not destination.is_file() and not (
                destination.is_dir() and (destination / "README.md").is_file()
            ):
                errors.append("{} -> {}".format(source.relative_to(ROOT), target))

    return errors


def editorial_errors():
    errors = []
    for source in (ROOT / "chapters").rglob("*.md"):
        text = source.read_text(encoding="utf-8")
        if "> Last reviewed:" not in text and "> Review status: Unverified" not in text:
            errors.append(f"{source.relative_to(ROOT)} -> missing review status")
    return errors


def html_errors(book):
    pages = {}
    for source in book.rglob("*.html"):
        page = HTMLPage()
        page.feed(source.read_text(encoding="utf-8"))
        pages[source.resolve()] = page

    errors = []
    for source, page in pages.items():
        for href in page.links:
            parts = urlsplit(href)
            if parts.scheme or parts.netloc or href.startswith(("mailto:", "javascript:")):
                continue
            target = (source.parent / unquote(parts.path)).resolve() if parts.path else source
            if target.is_dir():
                target /= "index.html"
            if not target.exists():
                errors.append("{} -> {}".format(source.relative_to(book), href))
            elif parts.fragment and target.suffix == ".html":
                target_page = pages.get(target)
                if target_page and unquote(parts.fragment) not in target_page.ids:
                    errors.append("{} -> {} (missing anchor)".format(source.relative_to(book), href))

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, help="also validate a built mdBook directory")
    args = parser.parse_args()

    errors = markdown_errors() + editorial_errors()
    if args.html:
        book = args.html.resolve()
        if not book.is_dir():
            parser.error("--html must point to a built mdBook directory")
        errors.extend(html_errors(book))

    if errors:
        print("Broken local links:", file=sys.stderr)
        for error in errors:
            print("- {}".format(error), file=sys.stderr)
        return 1

    print("All local links resolve exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
