#!/usr/bin/env node
/**
 * Render the Open Graph cards, site/assets/og.png (es) and og-en.png (en),
 * 1200 x 630. Modelled on the Coverly ROMs landing's cards: the Boxed app
 * icon (design/icon/app.svg) on the left; on the right the wordmark
 * (COVERLY plus the Manila "Shelf" tag), the headline, one line of copy and
 * the shelf rule with the host. Light palette from design/tokens.json.
 *
 * The brand font ships only as woff2, so the card is HTML screenshotted with
 * headless Chrome (scripts/site/chrome.mjs). Run: make og
 */
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { screenshot } from './chrome.mjs';

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const W = 1200;
const H = 630;

const COPY = {
  es: {
    out: 'og.png',
    h1: 'Cada juego en la estantería, con su portada.',
    p: 'Portada en caja 3D y galería de capturas para las fichas de 3DS en hShop. Solo cosmética.',
  },
  en: {
    out: 'og-en.png',
    h1: 'Every game on the shelf gets its cover.',
    p: 'Box art in a 3D case and a screenshot gallery for 3DS title pages on hShop. Purely cosmetic.',
  },
};

const C = {
  bg: '#F2F3EF',
  text: '#1B1E1B',
  muted: '#535A52',
  border: '#D3D7CF',
  primary: '#0E5E6F',
  manila: '#E6C171',
  manilaFg: '#2A2111',
};

const icon = readFileSync(join(REPO, 'design', 'icon', 'app.svg'), 'utf8')
  .replace(/<title>[^<]*<\/title>\n?/, '')
  .replace('<svg ', '<svg class="icon" aria-hidden="true" ');
const font = readFileSync(join(REPO, 'site', 'assets', 'fonts', 'archivo-variable.woff2')).toString('base64');
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function page(lang) {
  const t = COPY[lang];
  return `<!DOCTYPE html>
<html lang="${lang}">
<head>
<meta charset="utf-8">
<style>
@font-face { font-family: 'Archivo Display'; font-weight: 600 800; font-stretch: 75% 112%; font-display: block;
  src: url(data:font/woff2;base64,${font}) format('woff2'); }
* { box-sizing: border-box; margin: 0; }
html, body { width: ${W}px; height: ${H}px; overflow: hidden; background: ${C.bg}; }
body { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; color: ${C.text}; }
.card { position: relative; width: ${W}px; height: ${H}px; }
.icon { position: absolute; left: 36px; top: 74px; width: 440px; height: 440px; }
.copy { position: absolute; left: 520px; right: 72px; top: 104px; }
.wordmark { display: flex; align-items: center; gap: 14px; font: 800 52px/1 'Archivo Display'; letter-spacing: -0.01em; }
.tag { font: 800 30px/1 'Archivo Display'; background: ${C.manila}; color: ${C.manilaFg}; border-radius: 5px; padding: 7px 0.3em 6px; }
h1 { margin-top: 48px; font: 800 64px/1.02 'Archivo Display'; letter-spacing: -0.01em; }
p { margin-top: 24px; font-size: 25px; line-height: 1.4; color: ${C.muted}; }
.shelf { position: absolute; left: 72px; right: 72px; bottom: 64px; height: 1px; background: ${C.border}; }
.shelf::before { content: ''; position: absolute; left: 0; top: -1px; width: 96px; height: 3px; background: ${C.primary}; }
.host { position: absolute; right: 72px; bottom: 30px; font: 500 20px/1 ui-monospace, 'SF Mono', Menlo, monospace; color: ${C.muted}; }
h1, .wordmark, .tag { font-stretch: 75%; }
</style>
</head>
<body>
<div class="card">
${icon}
<div class="copy">
<div class="wordmark"><span>COVERLY</span><span class="tag">Shelf</span></div>
<h1>${esc(t.h1)}</h1>
<p>${esc(t.p)}</p>
</div>
<div class="shelf"></div>
<span class="host">coverly-shelf.maecly.com</span>
</div>
</body>
</html>
`;
}

for (const lang of Object.keys(COPY)) {
  const out = join(REPO, 'site', 'assets', COPY[lang].out);
  screenshot(page(lang), out, W, H);
  const png = readFileSync(out);
  const [w, h] = [png.readUInt32BE(16), png.readUInt32BE(20)];
  if (w !== W || h !== H) throw new Error(`${lang}: expected ${W}x${H}, got ${w}x${h}`);
  console.log('  wrote', out.slice(REPO.length + 1));
}
