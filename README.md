# Coverly Shelf landing

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
size budgets).

## How it deploys

Vercel Git integration: every push to `main` deploys production, pull requests
get previews. `vercel.json` runs `scripts/site/vercel_build.sh`, which runs the
checks and copies `site/` into `target/site`, the folder Vercel serves. The
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
