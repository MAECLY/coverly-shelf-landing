#!/usr/bin/env node
/**
 * Rasterise the Coverly Shelf icons from design/icon/*.svg into site/:
 *
 *   site/assets/favicon.svg            copy of design/icon/favicon.svg
 *   site/assets/mark.svg, mark-dark.svg copies of the marks
 *   site/assets/icon-192.png, icon-512.png       app.svg
 *   site/assets/icon-maskable-512.png            maskable.svg
 *   site/assets/apple-touch-icon.png (180)       maskable.svg (full bleed)
 *   site/favicon.ico (16, 32, 48 PNG layers)     favicon.svg
 *
 * Needs Chrome or Chromium (scripts/site/chrome.mjs). Run: make icons
 */
import { copyFileSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { screenshot } from './chrome.mjs';

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const ICON = join(REPO, 'design', 'icon');
const ASSETS = join(REPO, 'site', 'assets');

const svg = (name) => readFileSync(join(ICON, name), 'utf8');
const page = (markup, size, view = '0 0 1024 1024') =>
  `<!doctype html><html><head><style>html,body{margin:0;background:transparent;overflow:hidden}svg{display:block;width:${size}px;height:${size}px}</style></head><body>${
    markup.replace(/viewBox="[^"]*"/, `viewBox="${view}"`)
  }</body></html>`;

function render(name, size, out, view) {
  screenshot(page(svg(name), size, view), out, size, size, { transparent: true });
}

for (const f of ['favicon.svg', 'mark.svg', 'mark-dark.svg']) copyFileSync(join(ICON, f), join(ASSETS, f));
render('app.svg', 192, join(ASSETS, 'icon-192.png'));
render('app.svg', 512, join(ASSETS, 'icon-512.png'));
render('maskable.svg', 512, join(ASSETS, 'icon-maskable-512.png'));
// iOS rounds the corners itself: the full-bleed maskable drawing.
render('maskable.svg', 180, join(ASSETS, 'apple-touch-icon.png'));

// favicon.ico: PNG-compressed layers (Vista+ and every current browser).
const tmp = mkdtempSync(join(tmpdir(), 'shelf-ico-'));
try {
  const layers = [16, 32, 48].map((s) => {
    const p = join(tmp, `${s}.png`);
    // Render large and let Chrome downsample through the SVG viewport.
    render('favicon.svg', s, p);
    return [s, readFileSync(p)];
  });
  const head = Buffer.alloc(6 + 16 * layers.length);
  head.writeUInt16LE(0, 0);
  head.writeUInt16LE(1, 2);
  head.writeUInt16LE(layers.length, 4);
  let offset = head.length;
  layers.forEach(([s, png], i) => {
    const e = 6 + 16 * i;
    head.writeUInt8(s, e);
    head.writeUInt8(s, e + 1);
    head.writeUInt16LE(1, e + 4);
    head.writeUInt16LE(32, e + 6);
    head.writeUInt32LE(png.length, e + 8);
    head.writeUInt32LE(offset, e + 12);
    offset += png.length;
  });
  writeFileSync(join(REPO, 'site', 'favicon.ico'), Buffer.concat([head, ...layers.map((l) => l[1])]));
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
console.log('icons: wrote site/favicon.ico and site/assets/{favicon,mark,mark-dark}.svg, icon-*.png, apple-touch-icon.png');
