# Screenshot slot

Real screenshots of the extension on an hShop title page go here, as WebP
(`<name>-light.webp`, `<name>-dark.webp`, 2x, plus `@1x` variants), for
example `title-light.webp` and `gallery-dark.webp`.

When they exist, replace the `.stage-body` and `.strip` blocks inside
`<figure class="stage">` in `site/index.html` and `site/en/index.html`
(marked `SHOTS SLOT`) with a `<picture>` that uses them, with `width`,
`height`, `alt` and `loading="lazy"` below the fold.

Crop or blur any third-party box art that is not essential, and credit the
image sources (GameTDB, Libretro) in the caption. This folder is not
published with any images until then.
