# Screenshots

Real screenshots of the extension on live hShop title pages, taken by the
extension's end-to-end run (`bun run e2e` in
[MAECLY/coverly-shelf](https://github.com/MAECLY/coverly-shelf), saved in its
`docs/screenshots/`). They are cropped with `sips` and encoded with `cwebp`.

| File | Source | Crop | Used for |
|---|---|---|---|
| `title-{light,dark}.webp` (955 px) and `@1x` (560 px) | `title-1814-{light,dark}-1440.png` | the left card, 955 x 718 from (25, 121) | The hero image, by colour mode |
| `title-1814-{light,dark}.webp` and `-thumb` (400 px) | `title-1814-{light,dark}-1440.png` | top 1440 x 848 (above hShop's fixed footer) | Thumbnail 1 and its lightbox image |
| `lightbox.webp` and `-thumb` | `lightbox-1440.png` | top 1440 x 848 | Thumbnail 2 |
| `title-digital-18761.webp` and `-thumb` | `title-digital-18761-1440.png` | top 1440 x 848 | Thumbnail 3 |

Encoding: `cwebp -q 80 -m 6` (82 for the hero, 78 for thumbnails,
`-resize 560 0` / `-resize 400 0` for the smaller sizes).

The light and dark images are both in the page; CSS shows the one that
matches the page's colour mode (`.shot-light` / `.shot-dark` in
`site.css`), and the lightbox picks `data-full-light` in light mode.

The captures contain box art from GameTDB and screenshots from Libretro,
which belong to their owners and are credited in the caption under the
stage. This file is not published (`*.md` is left out of the build).
