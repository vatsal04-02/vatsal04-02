#!/usr/bin/env bash
# Run this ONCE locally after downloading JetBrainsMono-Regular.ttf and
# JetBrainsMono-Bold.ttf (SIL OFL license) into the project root.
#
# Produces the subset .woff2 files that scripts/svg_common.py inlines as
# base64 @font-face blocks. Skip a step here and that graphic just falls
# back to the visitor's system monospace/sans font -- nothing breaks, it
# just won't be pixel-identical across OSes.
#
# Requires: pip install fonttools brotli
set -euo pipefail

SRC_REGULAR="${1:-JetBrainsMono-Regular.ttf}"
SRC_BOLD="${2:-JetBrainsMono-Bold.ttf}"
OUT_DIR="../fonts"

mkdir -p "$OUT_DIR"

echo "1/3 ramp subset (13 characters, for the portrait + year grid)..."
pyftsubset "$SRC_REGULAR" \
  --text=' .`:-=+*cs#%@' \
  --flavor=woff2 --layout-features='' --no-hinting \
  -o "$OUT_DIR/ramp.woff2"

echo "2/3 headings subset (only the letters actually used in section titles)..."
# Adjust --text to match the exact heading words in your README.
pyftsubset "$SRC_REGULAR" \
  --text='abcdefghijklmnopqrstuvwxyz -–—·' \
  --flavor=woff2 --layout-features='' --no-hinting \
  -o "$OUT_DIR/headings.woff2"

echo "3/3 basic latin, two weights (numbers + labels in the data graphics)..."
pyftsubset "$SRC_REGULAR" \
  --unicodes='U+0020-007E,U+2013,U+2014,U+00B7,U+2026' \
  --flavor=woff2 --layout-features='' --no-hinting \
  -o "$OUT_DIR/basic-latin.woff2"

echo "done. sizes:"
ls -la "$OUT_DIR"/*.woff2

echo
echo "Don't forget: copy the JetBrains Mono OFL LICENSE.txt into $OUT_DIR/ too."
