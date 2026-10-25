#!/usr/bin/env python3
"""Read the product's public reach from the GitHub API, for the build.

Used by scripts/site/vercel_build.sh, then scripts/site/apply_metrics.py
fills the page with what it found. Two numbers, both public:

  downloads  the sum of download_count over every asset of every release
             (GET /repos/<repo>/releases?per_page=100, every page)
  stars      stargazers_count (GET /repos/<repo>)

A metric the API does not answer cleanly (an error, a rate limit, a value
that is not a whole number, more pages than PAGES) is left out of the JSON,
so the page shows nothing for it: never a guess and never a 0. That is why
this never fails the build. GITHUB_TOKEN, when set, only raises the rate
limit. Standard-library Python, no install step.

  fetch_metrics.py --repo OWNER/NAME --out metrics.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

API = "https://api.github.com/repos/"
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PER_PAGE = 100
# 1,000 releases: far more than any of these products will publish; past
# that the sum would be partial, so it is dropped instead.
PAGES = 10


class MetricError(Exception):
    pass


def get(url: str) -> object:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "maecly-landing-build"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return json.load(res)
    except Exception as e:  # noqa: BLE001 (any failure means "unknown")
        raise MetricError(f"{url}: {e}") from None


def whole(n: object) -> bool:
    return isinstance(n, int) and not isinstance(n, bool) and n >= 0


def downloads(repo: str) -> int:
    total = 0
    for page in range(1, PAGES + 1):
        releases = get(f"{API}{repo}/releases?per_page={PER_PAGE}&page={page}")
        if not isinstance(releases, list):
            raise MetricError("the releases answer is not a list")
        for rel in releases:
            for asset in (rel.get("assets") or []) if isinstance(rel, dict) else [None]:
                n = asset.get("download_count") if isinstance(asset, dict) else None
                if not whole(n):
                    raise MetricError(f"download_count {n!r} is not a whole number")
                total += n
        if len(releases) < PER_PAGE:
            return total
    raise MetricError(f"more than {PAGES * PER_PAGE} releases")


def stars(repo: str) -> int:
    info = get(f"{API}{repo}")
    n = info.get("stargazers_count") if isinstance(info, dict) else None
    if not whole(n):
        raise MetricError(f"stargazers_count {n!r} is not a whole number")
    return n


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    p.add_argument("--repo", required=True)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args(argv)
    if not REPO.match(a.repo):
        p.error(f"not an OWNER/NAME repository: {a.repo!r}")
    found: dict[str, int] = {}
    for name, read in (("downloads", downloads), ("stars", stars)):
        try:
            found[name] = read(a.repo)
        except MetricError as e:
            print(f"fetch_metrics: {name} unknown, so not shown: {e}", file=sys.stderr)
    a.out.write_text(json.dumps(found) + "\n", encoding="utf-8")
    print(f"fetch_metrics: {a.repo} {json.dumps(found)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
