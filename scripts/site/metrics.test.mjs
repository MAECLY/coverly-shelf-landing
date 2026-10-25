// Tests for the public reach baked in at build time:
// scripts/site/apply_metrics.py on a copy of site/, as vercel_build.sh runs
// it. Node's own runner, no dependencies: `node --test scripts/site/`.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const ROOT = new URL('../../', import.meta.url).pathname;
const PYTHON = process.env.PYTHON || 'python3';
const APPLY = join(ROOT, 'scripts/site/apply_metrics.py');

// Both landing pages after apply_metrics.py with `metrics`.
function built(metrics) {
  const dir = mkdtempSync(join(tmpdir(), 'cs-metrics-'));
  const out = join(dir, 'site');
  cpSync(join(ROOT, 'site'), out, { recursive: true });
  writeFileSync(join(dir, 'm.json'), JSON.stringify(metrics));
  execFileSync(PYTHON, ['-I', APPLY, '--metrics-json', join(dir, 'm.json'), '--out', out], { stdio: 'pipe' });
  const pages = {
    es: readFileSync(join(out, 'index.html'), 'utf8'),
    en: readFileSync(join(out, 'en/index.html'), 'utf8'),
  };
  rmSync(dir, { recursive: true });
  return pages;
}

// The data-metric elements of a page: { name: { text, hidden } }.
function slots(html) {
  const out = {};
  for (const m of html.matchAll(/<(\w+)\b([^>]*)\sdata-metric="(\w+)"([^>]*)>(.*?)<\/\1>/g)) {
    out[m[3]] = { text: m[5], hidden: /\shidden\b/.test(m[4]) };
  }
  return out;
}
const empty = { text: '', hidden: true };

test('site/ ships every slot empty and hidden', () => {
  for (const rel of ['site/index.html', 'site/en/index.html']) {
    assert.deepEqual(slots(readFileSync(join(ROOT, rel), 'utf8')), { downloads: empty, stars: empty }, rel);
  }
});

test('known numbers above zero are written, localized', () => {
  const { es, en } = built({ downloads: 1234567, stars: 1 });
  assert.deepEqual(slots(es), {
    downloads: { text: '1.234.567 descargas', hidden: false },
    stars: { text: '1 estrella', hidden: false },
  });
  assert.deepEqual(slots(en), {
    downloads: { text: '1,234,567 downloads', hidden: false },
    stars: { text: '1 star', hidden: false },
  });
  const small = built({ downloads: 1234, stars: 2 });
  assert.equal(slots(small.es).downloads.text, '1.234 descargas', 'es groups four digits too');
  assert.equal(slots(small.en).stars.text, '2 stars');
  assert.equal(slots(built({ downloads: 1 }).en).downloads.text, '1 download');
});

test('zero, missing (API failure) or not a whole number stays empty and hidden', () => {
  for (const metrics of [{}, { downloads: 0, stars: 0 }, { downloads: -3, stars: '5' }, { downloads: 2.5, stars: true }]) {
    const { es, en } = built(metrics);
    assert.deepEqual(slots(es), { downloads: empty, stars: empty }, JSON.stringify(metrics));
    assert.deepEqual(slots(en), { downloads: empty, stars: empty }, JSON.stringify(metrics));
  }
  const some = built({ downloads: 4 });
  assert.deepEqual(slots(some.es), { downloads: { text: '4 descargas', hidden: false }, stars: empty });
});

test('a slot it cannot read fails the build', () => {
  const dir = mkdtempSync(join(tmpdir(), 'cs-metrics-bad-'));
  writeFileSync(join(dir, 'm.json'), '{"downloads": 5}');
  for (const html of [
    '<html lang="es"><p data-metric="views" hidden></p></html>',
    '<html lang="es"><p data-metric="downloads" hidden>12</p></html>',
    '<html lang="es"><p data-metric="downloads"></p></html>',
    '<html><p data-metric="downloads" hidden></p></html>',
  ]) {
    writeFileSync(join(dir, 'index.html'), html);
    const run = spawnSync(PYTHON, ['-I', APPLY, '--metrics-json', join(dir, 'm.json'), '--out', dir], { encoding: 'utf8' });
    assert.equal(run.status, 1, html);
  }
  rmSync(dir, { recursive: true });
});
