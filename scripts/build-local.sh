#!/usr/bin/env bash
# Build the book locally (HTML + PDF)
# Usage: ./scripts/build-local.sh [version]
# Example: ./scripts/build-local.sh v1.0.0
# If no version is given, uses the latest git tag or "dev"

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Stop mdbook serve if running (it overwrites print.html)
pkill -f "mdbook serve" 2>/dev/null && echo "==> Stopped mdbook serve" || true

# Resolve version: argument > git tag > "dev"
VERSION="${1:-$(git describe --tags --abbrev=0 2>/dev/null || echo "dev")}"
echo "==> Version: $VERSION"

echo "==> Stamping version into cover SVG"
SVG_SRC="$ROOT/images/book-cover-template.svg"
SVG_TMP="$ROOT/images/.cover-build.svg"
sed "s|v 4.2026|$VERSION|" "$SVG_SRC" > "$SVG_TMP"

echo "==> Converting cover SVG → PNG"
npx --yes @resvg/resvg-js-cli "$SVG_TMP" "$ROOT/images/book-cover-template.png"
rm "$SVG_TMP"

echo "==> Building HTML with mdbook"
mdbook build

echo "==> Injecting cover + print styles into print.html"
cp "$ROOT/images/book-cover-template.png" "$ROOT/book/cover.png"
cp "$ROOT/theme/pdf.css" "$ROOT/book/pdf.css"

# Inject cover image after <main> and pdf.css in <head>
sed -i '' 's|<main>|<main><div style="page-break-after:always;margin:-15mm;padding:0;overflow:hidden"><img src="cover.png" style="width:210mm;height:297mm;object-fit:cover;display:block" /></div>|' "$ROOT/book/print.html"
sed -i '' 's|</head>|<link rel="stylesheet" href="pdf.css"></head>|' "$ROOT/book/print.html"

echo "==> Generating PDF with Chrome"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless \
  --disable-gpu \
  --no-pdf-header-footer \
  --print-to-pdf="$ROOT/book.pdf" \
  "$ROOT/book/print.html"

echo ""
echo "Done! ($VERSION)"
echo "  HTML: $ROOT/book/"
echo "  PDF:  $ROOT/book.pdf"
