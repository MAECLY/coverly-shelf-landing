/**
 * Screenshot an HTML string with headless Chrome or Chromium, for the icon
 * and Open Graph renders. The browser is found through $CHROME, then the
 * usual install paths and PATH names. Zero dependencies.
 */
import { execFileSync } from 'node:child_process';
import { existsSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const CANDIDATES = [
  process.env.CHROME,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
].filter(Boolean);

export function findChrome() {
  const hit = CANDIDATES.find((p) => existsSync(p));
  if (!hit) throw new Error('No Chrome/Chromium found: set $CHROME.');
  return hit;
}

/** Render `html` at width x height CSS px into `out` (PNG). */
export function screenshot(html, out, width, height, { transparent = false } = {}) {
  const dir = mkdtempSync(join(tmpdir(), 'shelf-render-'));
  try {
    const page = join(dir, 'page.html');
    writeFileSync(page, html);
    execFileSync(findChrome(), [
      '--headless=new',
      '--disable-gpu',
      '--hide-scrollbars',
      '--force-device-scale-factor=1',
      '--force-color-profile=srgb',
      '--no-first-run',
      '--no-default-browser-check',
      '--virtual-time-budget=3000',
      `--user-data-dir=${join(dir, 'profile')}`,
      ...(transparent ? ['--default-background-color=00000000'] : []),
      `--window-size=${width},${height}`,
      `--screenshot=${out}`,
      pathToFileURL(page).href,
    ], { stdio: 'ignore' });
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}
