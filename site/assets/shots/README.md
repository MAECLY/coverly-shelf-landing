# Screenshots

Real screenshots of the extension on live hShop pages, taken by the
extension's end-to-end runs (`bun run e2e`, `bun run e2e:lists` and
`bun run e2e:options` in
[MAECLY/coverly-shelf](https://github.com/MAECLY/coverly-shelf), saved in its
`docs/screenshots/`). They are cropped with `sips` and encoded with `cwebp`.

hShop's download QR code carries a token and must never appear here. The
title-page captures hide it (the e2e run screenshots them with the QR hidden);
listing pages and the settings page have no QR. Look at every new image
before adding it.

| File | Source | Crop | Used for |
|---|---|---|---|
| `title-{light,dark}.webp` (955 px) and `@1x` (560 px) | `title-1814-{light,dark}-1440.png` | the left card, 955 x 718 from (25, 121) | The hero image, by colour mode |
| `title-1814-{light,dark}.webp` and `-thumb` (400 px) | `title-1814-{light,dark}-1440.png` | top 1440 x 848 (above hShop's fixed footer) | Thumbnail 1 and its lightbox image |
| `lightbox.webp` and `-thumb` | `lightbox-1440.png` | top 1440 x 848 | Thumbnail 2 |
| `title-digital-18761.webp` and `-thumb` | `title-digital-18761-1440.png` | top 1440 x 848 | Thumbnail 3 |
| `cover-zoom.webp` (640 px) | `cover-zoom-1440.png` | 816 x 728 from (312, 80): the box art viewer and a little of the dimmed page | Cover zoom, under "What it does" |
| `related-6881.webp` (760 px) | `related-6881-dark-1440.png` | none (the e2e run captures only the Related Content box) | Related Content, under "What it does" |
| `list-na-{light,dark}.webp` (1112 px) and `@1x` (560 px) | `list-na-{light,dark}-1440.png` | 1112 x 656 from (164, 120): the heading and the first three rows | The listing-page stage, by colour mode |
| `options-{light,dark}.webp` | `options-{light,dark}-1280.png` | 600 x 640 from (340, 30): the header and the Cache card, without the version line | The settings section, by colour mode |

Crops are given as width x height from (x, y). With `sips` that is
`sips -c <height> <width> --cropOffset <y> <x>`.

Encoding: `cwebp -q 80 -m 6` (82 for the hero, 78 for thumbnails and
`cover-zoom`, `-resize 560 0` / `-resize 400 0` / `-resize 640 0` /
`-resize 760 0` for the smaller sizes).

The light and dark images are both in the page; CSS shows the one that
matches the page's colour mode (`.shot-light` / `.shot-dark` in
`site.css`), and the lightbox picks `data-full-light` in light mode.
`cover-zoom` and `related-6881` exist only in dark (hShop's dark theme).

The captures contain box art from GameTDB and screenshots and box art from
Libretro, which belong to their owners and are credited in the captions next
to them. This file is not published (`*.md` is left out of the build).
