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

echo "==> Preparing print.html for PDF"
PRINT="$ROOT/book/print.html"
cp "$ROOT/images/book-cover-template.png" "$ROOT/book/cover.png"
cp "$ROOT/theme/pdf.css" "$ROOT/book/pdf.css"

# Inject pdf.css into <head>
sed -i '' 's|</head>|<link rel="stylesheet" href="pdf.css"></head>|' "$PRINT"

# Inject cover image after <main>
sed -i '' 's|<main>|<main><div style="page-break-after:always;margin:-15mm;padding:0;overflow:hidden"><img src="cover.png" style="width:210mm;height:297mm;object-fit:cover;display:block" /></div>|' "$PRINT"

# Generate TOC HTML from SUMMARY.md + real anchor IDs from print.html
TOC_HTML="$ROOT/book/.toc-inject.html"
python3 "$ROOT/scripts/generate_toc_html.py" "$ROOT/SUMMARY.md" "$PRINT" "$TOC_HTML"

# Replace README section with TOC in print.html
python3 -c "
import re, sys
with open('$PRINT', 'r') as f:
    html = f.read()
pattern = r'<h1 id=\"wordpress-second-brain\">.*?<div style=\"break-before: page; page-break-before: always;\"></div>'
with open('$TOC_HTML', 'r') as f:
    toc = f.read()
result = re.sub(pattern, toc, html, count=1, flags=re.DOTALL)
if result == html:
    print('WARNING: README section not found, TOC not injected', file=sys.stderr)
with open('$PRINT', 'w') as f:
    f.write(result)
"
rm "$TOC_HTML"

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
