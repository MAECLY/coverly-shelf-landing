# Coverly Shelf landing

[![Stars](https://img.shields.io/github/stars/MAECLY/coverly-shelf-landing?style=flat-square)](https://github.com/MAECLY/coverly-shelf-landing/stargazers) [![Views](https://hits.sh/github.com/MAECLY/coverly-shelf-landing.svg?label=views&style=flat-square)](https://hits.sh/github.com/MAECLY/coverly-shelf-landing/) [![Last commit](https://img.shields.io/github/last-commit/MAECLY/coverly-shelf-landing?style=flat-square)](https://github.com/MAECLY/coverly-shelf-landing/commits/main)

[Español](README.es.md)

The website of [Coverly Shelf](https://github.com/MAECLY/coverly-shelf), live at
**https://coverly-shelf.maecly.com**: a static, bilingual page (Spanish at `/`,
English at `/en/`) with no framework, no dependencies and no trackers. The
extension itself, its releases and its issues live in
[MAECLY/coverly-shelf](https://github.com/MAECLY/coverly-shelf).

Coverly Shelf is a purely cosmetic browser extension that adds box art in a
CSS 3D box and a screenshot gallery to 3DS title pages on hShop, and a
thumbnail to every row of its lists. It is part
of the Coverly family, next to [Coverly ROMs](https://coverly-roms.maecly.com),
and shares its design tokens and fonts.

## Run it locally

You need `python3` and `node` (24 or newer); there is nothing to install.

```bash
make site                  # build, then serve on http://localhost:8080
make site SITE_PORT=8111   # another port
make check                 # every gate, as the Vercel build runs it
make help                  # all targets
```

`make check` runs the token staleness and contrast check and
`scripts/site/check_site.py` (required files, internal links and fragments,
Spanish/English parity, head tags and CSP, no third-party code or trackers,
size budgets, empty and hidden metric slots), then `scripts/site/metrics.test.mjs`.

## How it deploys

Vercel Git integration: every push to `main` deploys production, pull requests
get previews. `vercel.json` runs `scripts/site/vercel_build.sh`, which runs the
checks and copies `site/` into `target/site`, the folder Vercel serves. It
then reads the public reach from the GitHub API (`fetch_metrics.py`: the
downloads of every release asset and the stars of `MAECLY/coverly-shelf`)
and writes it into the hero and next to the footer's source link
(`apply_metrics.py`, "4 downloads" / "4 descargas"), only for a number that is
known and above zero; an API error or a 0 shows nothing and never fails the
build. The page itself still talks to no other server. The
domain `coverly-shelf.maecly.com` is a DNS-only CNAME in the `maecly.com`
Cloudflare zone pointing at Vercel.

## Layout

| Path | What |
|---|---|
| `site/index.html`, `site/en/index.html` | The two pages, written by hand; keep them in step (the parity gate checks it) |
| `site/assets/site.css` | All layout; colours and type come from `tokens.css` |
| `site/assets/shelf.js` | The screenshot lightbox and the turnable CSS box |
| `site/assets/theme.js` | Light/dark/system mode and the reduced-motion gate |
| `site/assets/shots/` | Real screenshots of the extension, as WebP (see its README) |
| `design/icon/` | The Boxed icon, source of every icon (`make icons`) |
| `design/tokens.json` | Coverly family tokens (`make tokens`, `make sync-tokens`) |

## License

[AGPL-3.0](LICENSE), like the extension. Fonts are under the SIL Open Font
License 1.1; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
