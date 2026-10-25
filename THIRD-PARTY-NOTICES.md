# Third-party notices

The Coverly Shelf landing (https://coverly-shelf.maecly.com) is licensed under
the GNU Affero General Public License v3.0 (see `LICENSE`), like the extension
in [MAECLY/coverly-shelf](https://github.com/MAECLY/coverly-shelf). The page
uses no third-party code. The 3D box and the screens in the feature cards are
drawn in CSS.

## Screenshots of the extension

`site/assets/shots/*.webp` are screenshots of the extension running on live
hShop title pages (https://hshop.erista.me/t/1814 and /t/18761). They show:

- box art from **GameTDB** (https://www.gametdb.com/);
- screenshots and title screens from **libretro-thumbnails**
  (https://thumbnails.libretro.com/);
- the hShop page itself.

They are shown to document what the extension does, are credited in the
caption on the page, and belong to their respective owners.

## Image sources the extension uses

The extension (not this page) loads images at runtime from:

- **GameTDB** (https://www.gametdb.com/), box covers, via `art.gametdb.com`.
- **libretro-thumbnails** (https://thumbnails.libretro.com/), screenshots and
  title screens, from the Libretro project.

Those images belong to their respective owners. Coverly Shelf is not
affiliated with hShop, GameTDB, Libretro or Nintendo.

## Coverly ROMs icon

`site/assets/coverly-roms.png` is the Coverly ROMs app icon, from
[MAECLY/coverly-roms](https://github.com/MAECLY/coverly-roms) (AGPL-3.0, same
author), used to link the sibling product.

## Fonts

The website self-hosts three typefaces (`site/assets/fonts/`), each licensed
under the SIL Open Font License 1.1:

- **Archivo**, Copyright 2020 The Archivo Project Authors
  (https://github.com/Omnibus-Type/Archivo). Licence: `OFL-Archivo.txt`.
- **Atkinson Hyperlegible Next**, Copyright 2020-2024 The Atkinson
  Hyperlegible Next Project Authors
  (https://github.com/googlefonts/atkinson-hyperlegible-next). Licence:
  `OFL-AtkinsonHyperlegibleNext.txt`.
- **Atkinson Hyperlegible Mono**, Copyright 2020-2024 The Atkinson
  Hyperlegible Mono Project Authors
  (https://github.com/googlefonts/atkinson-hyperlegible-next-mono). Licence:
  `OFL-AtkinsonHyperlegibleMono.txt`.

The shipped `.woff2` files are modified versions of the variable fonts from
the google/fonts repository: their axes are limited (Archivo wdth 75-112 and
wght 600-800, Atkinson Hyperlegible Next wght 400-700, Atkinson Hyperlegible
Mono wght 400-600), they are subset to Latin, Latin-1 Supplement and Latin
Extended-A, hinting is removed, and they are converted to WOFF2. They keep
their original family names, which the OFL allows because none of these
fonts declares a Reserved Font Name. Each licence file sits next to the font
files.
