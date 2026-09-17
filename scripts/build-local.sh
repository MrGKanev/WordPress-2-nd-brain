#!/usr/bin/env bash
# Build the book locally (HTML + PDF)
# Usage: ./scripts/build-local.sh [version]
# Example: ./scripts/build-local.sh v1.0.0
# If no version is given, uses the latest git tag or "dev"

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

EXPECTED_MDBOOK="$(tr -d '[:space:]' < "$ROOT/.mdbook-version")"
if [[ "$(mdbook --version 2>/dev/null || true)" != "mdbook v$EXPECTED_MDBOOK" ]]; then
  echo "Error: mdbook v$EXPECTED_MDBOOK is required" >&2
  exit 1
fi

# Resolve version: argument > git tag > "dev"
VERSION="${1:-$(git describe --tags --abbrev=0 2>/dev/null || echo "dev")}"
echo "==> Version: $VERSION"

echo "==> Stamping version into cover SVG"
SVG_SRC="$ROOT/images/book-cover-template.svg"
BUILD_TMP="$(mktemp -d)"
trap 'rm -r "$BUILD_TMP"' EXIT
SVG_TMP="$BUILD_TMP/cover.svg"
python3 - "$SVG_SRC" "$SVG_TMP" "$VERSION" <<'PY'
from pathlib import Path
import sys

source, output = map(Path, sys.argv[1:3])
version = sys.argv[3]
text = source.read_text(encoding="utf-8")
marker = "v 4.2026"
if text.count(marker) != 1:
    raise SystemExit(f"Expected exactly one {marker!r} cover marker")
output.write_text(text.replace(marker, version), encoding="utf-8")
PY

echo "==> Building HTML with mdbook $EXPECTED_MDBOOK"
mdbook build

echo "==> Converting cover SVG → PNG"
npx --yes @resvg/resvg-js-cli@2.6.2-beta.1 "$SVG_TMP" "$ROOT/book/cover.png"

echo "==> Preparing print.html for PDF"
python3 "$ROOT/scripts/prepare_pdf.py"
python3 "$ROOT/scripts/check_markdown_links.py" --html "$ROOT/book"

echo "==> Generating PDF with Chrome"
if [[ -z "${CHROME_BIN:-}" ]]; then
  for candidate in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "$(command -v google-chrome 2>/dev/null || true)" \
    "$(command -v chromium 2>/dev/null || true)" \
    "$(command -v chromium-browser 2>/dev/null || true)"; do
    if [[ -x "$candidate" ]]; then CHROME_BIN="$candidate"; break; fi
  done
fi
if [[ ! -x "${CHROME_BIN:-}" ]]; then
  echo "Error: Chrome/Chromium not found; set CHROME_BIN" >&2
  exit 1
fi
"$CHROME_BIN" \
  --headless \
  --disable-gpu \
  --no-pdf-header-footer \
  --print-to-pdf="$ROOT/book.pdf" \
  "file://$ROOT/book/print.html"

echo ""
echo "Done! ($VERSION)"
echo "  HTML: $ROOT/book/"
echo "  PDF:  $ROOT/book.pdf"
