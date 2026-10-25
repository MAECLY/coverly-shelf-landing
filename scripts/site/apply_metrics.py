#!/usr/bin/env python3
"""Fill the public-reach slots of a built landing with known numbers.

Used by scripts/site/vercel_build.sh after scripts/site/fetch_metrics.py.
In site/, each slot is an empty, hidden element:

  <li data-metric="downloads" hidden></li>
  <span class="metric-stars" data-metric="stars" hidden></span>

For a metric known and above zero, this writes its label in the page's
language (<html lang>) and drops `hidden`: "1.234 descargas", "1,234
downloads", "1 estrella", "2 stars". A metric that is missing from the
JSON or is 0 leaves its slot empty and hidden, so the page never shows a
made-up or placeholder number. It fails on a slot it cannot read (unknown
metric, not empty, not hidden) or a page with no lang, so a typo cannot ship
silently.

  apply_metrics.py --metrics-json metrics.json --out target/site
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Singular and plural, by language.
WORDS = {
    "es": {"downloads": ("descarga", "descargas"), "stars": ("estrella", "estrellas")},
    "en": {"downloads": ("download", "downloads"), "stars": ("star", "stars")},
}
SEPARATOR = {"es": ".", "en": ","}
LANG = re.compile(r'<html\b[^>]*\slang="([a-z]{2})')
ANY = re.compile(r'<(\w+)\b[^>]*\sdata-metric="([^"]*)"[^>]*>')
SLOT = re.compile(r'(<(\w+)\b[^>]*?\sdata-metric="([a-z]+)"[^>]*?) hidden></\2>')


class MetricError(Exception):
    pass


def number(n: int, lang: str) -> str:
    """Thousands grouped for every size: es 1.234, en 1,234."""
    return f"{n:,}".replace(",", SEPARATOR[lang])


def label(name: str, n: int, lang: str) -> str:
    one, many = WORDS[lang][name]
    return f"{number(n, lang)} {one if n == 1 else many}"


def fill(text: str, metrics: dict[str, int], where: str) -> tuple[str, int]:
    slots = ANY.findall(text)
    if not slots:
        return text, 0
    m = LANG.search(text)
    if not m or m.group(1) not in WORDS:
        raise MetricError(f"{where}: no supported <html lang> for its metric slots")
    lang = m.group(1)
    good = SLOT.findall(text)
    if len(good) != len(slots):
        raise MetricError(f"{where}: every data-metric slot must be empty and end in ' hidden></tag>'")
    for _, _, name in good:
        if name not in WORDS[lang]:
            raise MetricError(f"{where}: unknown metric {name!r}")
    shown = 0

    def one(s: re.Match) -> str:
        nonlocal shown
        n = metrics.get(s.group(3))
        if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
            return s.group(0)
        shown += 1
        return f"{s.group(1)}>{label(s.group(3), n, lang)}</{s.group(2)}>"

    return SLOT.sub(one, text), shown


def apply(metrics: dict[str, int], out: Path) -> int:
    shown = 0
    for path in sorted(out.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        new, n = fill(text, metrics, path.relative_to(out).as_posix())
        shown += n
        if new != text:
            path.write_text(new, encoding="utf-8")
    return shown


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    p.add_argument("--metrics-json", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args(argv)
    try:
        metrics = json.loads(a.metrics_json.read_text(encoding="utf-8"))
        if not isinstance(metrics, dict):
            raise MetricError("the metrics JSON is not an object")
        if not a.out.is_dir():
            raise MetricError(f"{a.out} is not a folder")
        shown = apply(metrics, a.out)
    except (OSError, json.JSONDecodeError, MetricError) as e:
        print(f"apply_metrics: {e}", file=sys.stderr)
        return 1
    print(f"apply_metrics: {shown} slot(s) filled from {json.dumps(metrics)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
