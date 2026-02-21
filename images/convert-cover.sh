#!/usr/bin/env bash
# Convert book-cover-template.svg → book-cover-template.png
# Usage: ./images/convert-cover.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SVG="$SCRIPT_DIR/book-cover-template.svg"
PNG="$SCRIPT_DIR/book-cover-template.png"

if [ ! -f "$SVG" ]; then
  echo "Error: $SVG not found"
  exit 1
fi

npx --yes @resvg/resvg-js-cli "$SVG" "$PNG"
echo "Done: $PNG"
