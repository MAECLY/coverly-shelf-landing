#!/usr/bin/env bash
# Builds the landing for Vercel (vercel.json -> buildCommand): check the
# tokens and site/, then copy site/ into target/site, the folder Vercel
# serves. Markdown notes under site/ (like assets/shots/README.md) stay out.
set -euo pipefail

OUT="target/site"

node scripts/brand/build_tokens.mjs --check
python3 -I scripts/site/check_site.py

rm -rf "$OUT"
mkdir -p "$OUT"
cp -R site/. "$OUT/"
find "$OUT" -name '*.md' -delete
echo "Built $OUT"
