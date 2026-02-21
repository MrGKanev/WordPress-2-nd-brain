#!/usr/bin/env bash
# Build the book locally (HTML + PDF)
# Usage: ./scripts/build-local.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Converting cover SVG → PNG"
./images/convert-cover.sh

echo "==> Building HTML with mdbook"
mdbook build

echo "==> Injecting cover page into print.html"
cp "$ROOT/images/book-cover-template.png" "$ROOT/book/cover.png"
COVER_TAG='<div style="page-break-after:always;margin:-15mm;padding:0;overflow:hidden"><img src="cover.png" style="width:210mm;height:297mm;object-fit:cover;display:block" \/><\/div>'
sed -i '' "s|<main>|<main>${COVER_TAG}|" "$ROOT/book/print.html"

echo "==> Generating PDF with Chrome"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless \
  --disable-gpu \
  --no-pdf-header-footer \
  --print-to-pdf="$ROOT/book.pdf" \
  "$ROOT/book/print.html"

echo ""
echo "Done!"
echo "  HTML: $ROOT/book/"
echo "  PDF:  $ROOT/book.pdf"
