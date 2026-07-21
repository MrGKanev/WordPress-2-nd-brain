#!/usr/bin/env python3
"""Fail when a local Markdown link points to a missing file.

External URLs are deliberately skipped: their availability is volatile and should
be checked separately from the deterministic repository validation.
"""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]+)?\)")


def is_local_target(target):
    return not target.startswith(("http://", "https://", "mailto:", "/"))


def main():
    errors = []

    for source in ROOT.rglob("*.md"):
        if "book" in source.parts:
            continue

        for target in LINK_RE.findall(source.read_text(encoding="utf-8")):
            if not is_local_target(target):
                continue

            destination = (source.parent / target).resolve()
            if not destination.is_file():
                errors.append(
                    "{} -> {}".format(source.relative_to(ROOT), target)
                )

    if errors:
        print("Broken local Markdown links:", file=sys.stderr)
        for error in errors:
            print("- {}".format(error), file=sys.stderr)
        return 1

    print("All local Markdown links resolve exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
