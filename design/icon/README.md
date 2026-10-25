# Coverly Shelf icon: Boxed

The Coverly Shelf mark is a variant of the Coverly ROMs mark
([Lean-To](https://github.com/MAECLY/coverly-roms/tree/main/design/icon)):
the same 300 x 400 cover leans 12° on the same shelf rule, but the empty slot
next to it is now a **closed box with depth**. Coverly ROMs fills the gap on
your SD card; Coverly Shelf puts the game in its box on a web page.

Every icon the landing ships (`site/favicon.ico`, `site/assets/favicon.svg`,
`site/assets/mark*.svg`, `site/assets/icon-*.png`,
`site/assets/apple-touch-icon.png`) is generated from this folder by
`make icons` (`scripts/site/icons.mjs`, headless Chrome). Edit the SVGs here,
then regenerate; never edit the outputs by hand.

## Files

| File | What it is |
|---|---|
| `app.svg` | 1024 canvas, 824 px Buckram squircle (rx 185.4), paper cover and box, Manila shelf. Source of `icon-192/512.png` and the Open Graph cards |
| `maskable.svg` | Full-bleed Buckram square, glyph at 70% inside the safe zone. Source of `icon-maskable-512.png` and `apple-touch-icon.png` |
| `favicon.svg` | Full-bleed tile with heavier seams (40) and a thicker shelf so it holds at 16-48 px; dark-scheme palette. Source of `favicon.ico` |
| `mark.svg` | Glyph only in Buckram `#0E5E6F`, transparent, seams cut out with a mask |
| `mark-dark.svg` | Glyph only in Buckram dark `#5DB6C4` |
| `app-mono.svg` | Glyph only, one ink (`#000`), for single-colour use |

## Geometry (1024 glyph space, before the 0.8 scale in `app.svg`)

- Cover: identical to Lean-To (300 x 400, rx 48, rotated 12° about its
  bottom-right corner).
- Box front: 302 x 404, rx 50, where Lean-To's slot stood (x 540, y 299),
  filled instead of hollow.
- Box depth: a 64 unit offset up and to the right, drawn behind the front.
- Seams: a 28 unit Buckram stroke (painted under the fill) separates the
  front from the depth and the cover from the box, so the layers stay flat
  and opaque, with no shadows or gradients.
- Shelf: 740 x 56, rx 28, Manila, wider than Lean-To's to carry the deeper box.

## Don'ts

The Lean-To rules apply: no gradients, gloss or shadows; tile always Buckram;
Manila only on the shelf; never combine it with controllers, cartridges,
console logos or letterforms.
