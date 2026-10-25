#!/usr/bin/env bash
# Builds the landing for Vercel (vercel.json -> buildCommand): check the
# tokens and site/, then copy site/ into target/site, the folder Vercel
# serves. Markdown notes under site/ (like assets/shots/README.md) stay out.
# Then the public reach (fetch_metrics.py, apply_metrics.py, as in the
# Coverly ROMs landing): the downloads of every release asset and the GitHub
# stars, baked in only when known and above zero. An unknown number (API
# error, rate limit) leaves its slot hidden and never fails the build.
# GITHUB_TOKEN, when the Vercel project defines it, only raises the rate limit.
set -euo pipefail

REPO="MAECLY/coverly-shelf"
OUT="target/site"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

node scripts/brand/build_tokens.mjs --check
python3 -I scripts/site/check_site.py

rm -rf "$OUT"
mkdir -p "$OUT"
cp -R site/. "$OUT/"
find "$OUT" -name '*.md' -delete
python3 -I scripts/site/fetch_metrics.py --repo "$REPO" --out "$TMP/metrics.json"
python3 -I scripts/site/apply_metrics.py --metrics-json "$TMP/metrics.json" --out "$OUT"
echo "Built $OUT"
