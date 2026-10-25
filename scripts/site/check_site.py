#!/usr/bin/env python3
"""Check the Coverly Shelf landing before it ships. Standard library only.

  check_site.py [--site site]

Gates, in the spirit of the Coverly ROMs landing's checks:

  files    required files exist; vercel.json builds with this script and
           serves target/site
  links    every internal href/src resolves inside site/, every #fragment
           exists on its page
  parity   Spanish and English pages have the same structure (sections,
           headings, FAQ entries, install steps, images, links out)
  head     same CSP on every page, canonical/hreflang pairs, lang attribute,
           no inline style attributes or <style>, no inline scripts other
           than JSON-LD, no third-party scripts, styles or trackers, images
           sized and described
  budget   page, CSS, JS and image sizes
  motion   keyframes and transitions move only compositor or paint
           properties (no layout), and no keyframe that starts hidden
           keeps text hidden for more than a second

Exit status 1 when any gate fails; every failure is printed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
HOST = "coverly-shelf.maecly.com"
CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "font-src 'self'; connect-src 'self'; manifest-src 'self'; object-src 'none'; "
    "base-uri 'self'; form-action 'none'"
)
PAGES = {"es": "index.html", "en": "en/index.html"}
# Standalone pages: same CSP, link, inline-style and budget rules as the landing.
EXTRA = ["404.html", "privacy/index.html", "en/privacy/index.html"]
CANONICAL = {"es": f"https://{HOST}/", "en": f"https://{HOST}/en/"}
REQUIRED = [
    "index.html", "en/index.html", "404.html", "privacy/index.html", "en/privacy/index.html", "robots.txt", "sitemap.xml",
    "llms.txt", "site.webmanifest", "en/site.webmanifest", "favicon.ico",
    "assets/tokens.css", "assets/site.css", "assets/motion.css", "assets/theme.js", "assets/shelf.js",
    "assets/motion.js",
    "assets/favicon.svg", "assets/mark.svg", "assets/mark-dark.svg",
    "assets/icon-192.png", "assets/icon-512.png", "assets/icon-maskable-512.png",
    "assets/apple-touch-icon.png", "assets/og.png", "assets/og-en.png",
    "assets/fonts/archivo-variable.woff2",
    "assets/fonts/atkinson-hyperlegible-next-variable.woff2",
    "assets/fonts/atkinson-hyperlegible-mono-variable.woff2",
    "assets/fonts/OFL-Archivo.txt", "assets/fonts/OFL-AtkinsonHyperlegibleNext.txt",
    "assets/fonts/OFL-AtkinsonHyperlegibleMono.txt",
]
TRACKERS = re.compile(
    r"google-analytics|googletagmanager|gtag\(|plausible|umami|matomo|segment\.|"
    r"hotjar|clarity\.ms|facebook\.net|doubleclick|posthog|vercel-insights|va\.vercel",
    re.I,
)
# Raw bytes; the CSS box and screens are drawn in CSS, so the page is light.
BUDGET = {
    "page": 40_000,
    "css": 40_000,
    "js": 12_000,
    "png": 120_000,
    "svg": 8_000,
}

failures: list[str] = []


def fail(gate: str, msg: str) -> None:
    failures.append(f"[{gate}] {msg}")


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.ids: set[str] = set()
        self.scripts: list[tuple[dict[str, str], str]] = []
        self._script: dict[str, str] | None = None
        self._buf: list[str] = []
        self.has_style_tag = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        self.tags.append((tag, a))
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "script":
            self._script, self._buf = a, []
        if tag == "style":
            self.has_style_tag = True

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        if self._script is not None:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._script is not None:
            self.scripts.append((self._script, "".join(self._buf)))
            self._script = None

    def find(self, tag: str, **want: str) -> list[dict[str, str]]:
        return [a for t, a in self.tags if t == tag and all(a.get(k) == v for k, v in want.items())]


def parse(path: Path) -> Page:
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def check_files(site: Path) -> None:
    for rel in REQUIRED:
        if not (site / rel).is_file():
            fail("files", f"missing {rel}")
    try:
        vercel = json.loads((ROOT / "vercel.json").read_text())
    except (OSError, ValueError) as e:
        fail("files", f"vercel.json unreadable: {e}")
        return
    if vercel.get("outputDirectory") != "target/site":
        fail("files", "vercel.json outputDirectory must be target/site")
    if "vercel_build.sh" not in vercel.get("buildCommand", ""):
        fail("files", "vercel.json buildCommand must run scripts/site/vercel_build.sh")
    for f in ("site.webmanifest", "en/site.webmanifest"):
        try:
            json.loads((site / f).read_text())
        except (OSError, ValueError) as e:
            fail("files", f"{f}: {e}")


def resolve(site: Path, page_rel: str, ref: str) -> Path | None:
    parts = urlsplit(ref)
    if parts.scheme or parts.netloc or ref.startswith(("mailto:", "#")):
        return None
    base = (site / page_rel).parent
    path = parts.path
    target = (site / path.lstrip("/")) if path.startswith("/") else (base / path)
    target = target.resolve()
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def check_links(site: Path, pages: dict[str, Page]) -> None:
    for rel in [*PAGES.values(), *EXTRA]:
        page = pages.get(rel) or parse(site / rel)
        for tag, a in page.tags:
            for attr in ("href", "src"):
                ref = a.get(attr)
                if not ref or (tag == "a" and attr == "src"):
                    continue
                if ref.startswith("#"):
                    if ref[1:] and ref[1:] not in page.ids:
                        fail("links", f"{rel}: #{ref[1:]} has no target")
                    continue
                target = resolve(site, rel, ref)
                if target is None:
                    if ref.startswith("http://"):
                        fail("links", f"{rel}: insecure link {ref}")
                    continue
                if not target.is_file():
                    fail("links", f"{rel}: {ref} does not resolve")


def shape(page: Page) -> dict[str, int]:
    count = lambda pred: sum(1 for t, a in page.tags if pred(t, a))
    return {
        "section": count(lambda t, a: t == "section"),
        "h1": count(lambda t, a: t == "h1"),
        "h2": count(lambda t, a: t == "h2"),
        "h3": count(lambda t, a: t == "h3"),
        "details": count(lambda t, a: t == "details"),
        "li": count(lambda t, a: t == "li"),
        "img": count(lambda t, a: t == "img"),
        "button": count(lambda t, a: t == "button"),
        "external links": count(lambda t, a: t == "a" and a.get("href", "").startswith("https://")),
        "ids": len(page.ids),
    }


def check_parity(pages: dict[str, Page]) -> None:
    es, en = shape(pages[PAGES["es"]]), shape(pages[PAGES["en"]])
    for k in es:
        if es[k] != en[k]:
            fail("parity", f"{k}: es has {es[k]}, en has {en[k]}")
    ext = lambda p: sorted(a["href"] for t, a in p.tags if t == "a" and a.get("href", "").startswith("https://"))
    if ext(pages[PAGES["es"]]) != ext(pages[PAGES["en"]]):
        fail("parity", "es and en link to different external URLs")


def check_head(site: Path, pages: dict[str, Page]) -> None:
    for lang, rel in PAGES.items():
        page = pages[rel]
        html = page.find("html")
        if not html or html[0].get("lang") != lang:
            fail("head", f"{rel}: <html lang> must be {lang}")
        alts = {a.get("hreflang"): a.get("href") for a in page.find("link", rel="alternate")}
        if alts.get("es") != CANONICAL["es"] or alts.get("en") != CANONICAL["en"] or "x-default" not in alts:
            fail("head", f"{rel}: hreflang es/en/x-default incomplete")
        canon = page.find("link", rel="canonical")
        if not canon or canon[0].get("href") != CANONICAL[lang]:
            fail("head", f"{rel}: canonical must be {CANONICAL[lang]}")
        if not page.find("meta", property="og:image"):
            fail("head", f"{rel}: og:image missing")
    for rel in [*PAGES.values(), *EXTRA]:
        page = pages.get(rel) or parse(site / rel)
        text = (site / rel).read_text(encoding="utf-8")
        csp = page.find("meta", **{"http-equiv": "Content-Security-Policy"})
        if not csp or csp[0].get("content") != CSP:
            fail("head", f"{rel}: CSP missing or different from check_site.CSP")
        if page.has_style_tag or any("style" in a for _, a in page.tags):
            fail("head", f"{rel}: inline styles are blocked by the CSP")
        for attrs, body in page.scripts:
            src = attrs.get("src", "")
            if src:
                if urlsplit(src).netloc:
                    fail("head", f"{rel}: third-party script {src}")
            elif attrs.get("type") != "application/ld+json":
                fail("head", f"{rel}: inline script blocked by the CSP")
            else:
                try:
                    json.loads(body)
                except ValueError as e:
                    fail("head", f"{rel}: JSON-LD does not parse: {e}")
        for a in page.find("link", rel="stylesheet"):
            if urlsplit(a.get("href", "")).netloc:
                fail("head", f"{rel}: third-party stylesheet {a['href']}")
        if TRACKERS.search(text):
            fail("head", f"{rel}: looks like a tracker")
        for t, a in page.tags:
            if t == "img":
                for need in ("width", "height", "alt"):
                    if need not in a:
                        fail("head", f"{rel}: <img src={a.get('src')}> lacks {need}")
            if t == "a" and a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
                fail("head", f"{rel}: target=_blank without rel=noopener")


def check_budget(site: Path) -> None:
    for rel in [*PAGES.values(), *EXTRA]:
        size = (site / rel).stat().st_size
        if size > BUDGET["page"]:
            fail("budget", f"{rel}: {size} B > {BUDGET['page']} B")
    for f in site.rglob("*"):
        if not f.is_file():
            continue
        kind = {".css": "css", ".js": "js", ".png": "png", ".svg": "svg"}.get(f.suffix)
        if kind and f.stat().st_size > BUDGET[kind]:
            fail("budget", f"{f.relative_to(site)}: {f.stat().st_size} B > {BUDGET[kind]} B")
    for f in (site / "assets").rglob("*.js"):
        if TRACKERS.search(f.read_text(encoding="utf-8")):
            fail("budget", f"{f.relative_to(site)}: looks like a tracker")


# ── motion ─────────────────────────────────────────────────────────────

# What a keyframe or transition may move: compositor-friendly or paint-only
# properties. Anything that moves layout (sizes, offsets, margins) shifts
# the page, so it fails. The exceptions answer a click: the FAQ answer's
# height, and the lightbox's discrete display/overlay switch.
MOVES = {
    "transform", "opacity", "visibility", "clip-path", "stroke-dashoffset",
    "background-color", "outline-color", "color", "border-color", "box-shadow",
}
USER_LAYOUT = {
    ("::details-content", "block-size"), ("::details-content", "content-visibility"),
    (".lightbox", "display"), (".lightbox", "overlay"),
}
TEXT = re.compile(r"(^|[\s>+~])(h[1-6]|p|li|a|img|picture|figure|button|\.btn)$")
# Stagger indices (--n, --r) are assumed to reach this when delays are checked.
STAGGER = 3


def css_rules(css: str) -> list[tuple[list[str], str, str]]:
    """(enclosing at-rule preludes, selector, body) for every style rule."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out: list[tuple[list[str], str, str]] = []
    stack: list[str] = []
    buf = ""
    i = 0
    while i < len(css):
        ch = css[i]
        if ch == "{":
            prelude = buf.strip()
            buf = ""
            if prelude.startswith("@") and not prelude.startswith("@font-face"):
                stack.append(prelude)
            else:
                end = css.index("}", i)
                out.append((stack[:], prelude, css[i + 1:end]))
                i = end
        elif ch == "}":
            if stack:
                stack.pop()
            buf = ""
        else:
            buf += ch
        i += 1
    return out


def decls(body: str) -> list[tuple[str, str]]:
    return [(k.strip().lower(), v.strip()) for k, _, v in
            (d.partition(":") for d in body.split(";")) if v.strip()]


def tokens(value: str) -> list[str]:
    """Split on spaces outside parentheses: calc(1ms + 2ms) stays whole."""
    out, depth, cur = [], 0, ""
    for ch in value:
        depth += (ch == "(") - (ch == ")")
        if ch.isspace() and depth == 0:
            if cur:
                out.append(cur)
            cur = ""
        else:
            cur += ch
    return out + ([cur] if cur else [])


def seconds(tok: str) -> float | None:
    """A time, or a calc() of times with var() read as STAGGER."""
    expr = re.sub(r"var\(--[\w-]+(,[^)]*)?\)", str(STAGGER), tok)
    if not re.search(r"\d(m?s)\b", expr):
        return None
    expr = re.sub(r"([\d.]+)ms\b", r"(\1/1000)", re.sub(r"^calc", "", expr))
    expr = re.sub(r"([\d.]+)s\b", r"(\1)", expr)
    if not re.fullmatch(r"[\d.+\-*/() ]+", expr):
        return None
    try:
        return float(eval(expr, {"__builtins__": {}}))  # digits and operators only
    except (SyntaxError, ZeroDivisionError):
        return None


def check_motion(site: Path) -> None:
    rules: list[tuple[list[str], str, str]] = []
    for rel in ("assets/site.css", "assets/motion.css"):
        rules += css_rules((site / rel).read_text(encoding="utf-8").replace('"', "'"))
    hiding: set[str] = set()
    for stack, sel, body in rules:
        frame = [p for p in stack if p.startswith("@keyframes")]
        if frame:
            for prop, _ in decls(body):
                if prop not in MOVES:
                    fail("motion", f"{frame[-1]} animates {prop} (layout)")
            if any(s.strip() in ("from", "0%") for s in sel.split(",")) and any(
                    (p, v) in (("opacity", "0"), ("visibility", "hidden")) for p, v in decls(body)):
                hiding.add(frame[-1].split()[1])
            continue
        for prop, val in decls(body):
            if prop in ("transition", "transition-property") and not val.startswith("none"):
                for part in val.split(","):
                    name = part.split()[0] if part.split() else ""
                    if name not in MOVES and not any(s in sel and p == name for s, p in USER_LAYOUT):
                        fail("motion", f"{sel}: transition on {name} (layout)")
    for stack, sel, body in rules:
        if any(p.startswith("@keyframes") for p in stack):
            continue
        d = dict(decls(body))
        for part in d.get("animation", d.get("animation-name", "")).split(","):
            toks = tokens(part)
            name = next((t for t in toks if t in hiding), None)
            if not name:
                continue
            texty = [s.strip() for s in sel.split(",")
                     if TEXT.search(re.sub(r":[\w-]+(\([^)]*\))?", "", s.strip()))]
            if not texty:
                continue
            times = [t for t in (seconds(x) for x in toks) if t is not None]
            delay = seconds(d["animation-delay"]) if "animation-delay" in d else \
                (times[1] if len(times) > 1 else 0.0)
            if delay and delay > 1:
                fail("motion", f"{texty[0]}: {name} hides text for {delay:g}s before it shows")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--site", default=str(ROOT / "site"))
    args = ap.parse_args()
    site = Path(args.site).resolve()
    pages = {rel: parse(site / rel) for rel in PAGES.values()}
    check_files(site)
    check_links(site, pages)
    check_parity(pages)
    check_head(site, pages)
    check_budget(site)
    check_motion(site)
    if failures:
        print("\n".join(failures))
        print(f"\n{len(failures)} check(s) failed.")
        return 1
    print("site: files, links, parity, head, budget and motion checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
