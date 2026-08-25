#!/usr/bin/env node
/**
 * Per-element CLS attribution harness.
 *
 * Why this exists alongside measure_ad_collapse_cls.mjs
 * -----------------------------------------------------
 * That script answers one specific question — "is reserving ad height and then
 * collapsing it worse than not reserving?" — by driving that one transition and
 * reporting a single total. It cannot say WHICH element moved, so it cannot be
 * used to check a field report.
 *
 * The field report this was written for (2026-08-25, a reader's console on the
 * live 08-25 digest):
 *
 *   [Performance] CLS is high: 0.179668
 *   Cause: SECTION#comments.comments-section, NAV.post-navigation
 *
 * Those are first-party elements, so the reflex reading is "the comments block
 * is unreserved". But .giscus-wrapper already reserves min-height:400px, and the
 * same console showed AdSense slots at ady=19148 / ady=20938 — directly above
 * navigation and comments — all returning 400 (unfilled). A shift ATTRIBUTED to
 * an element is not the same as a shift CAUSED by it: everything below a
 * collapsing ad is reported as the source, because those are the nodes that
 * actually moved.
 *
 * So this harness reports, per layout-shift entry: the score, and the
 * `sources[]` element selectors with their before/after rects. That is what
 * distinguishes "comments grew" from "comments got pushed".
 *
 * Third-party handling
 * --------------------
 * `--allow <substr>` may be repeated to let specific third-party origins load.
 * Everything else is aborted. Default is first-party only, which means ads never
 * render and giscus never mounts — that run measures the FLOOR (what shifts with
 * no third party at all). Compare it against a run that allows giscus.app to
 * isolate the comments iframe's own contribution.
 *
 * Ads cannot be reproduced this way: Auto ads placement is server-decided and
 * stochastic, so an ad-collapse contribution measured locally would be fiction.
 * Use measure_ad_collapse_cls.mjs for that half, and read this one as
 * "first-party floor", not "total".
 *
 * Usage:
 *   JEKYLL_ENV=production bundle exec jekyll build -d _site
 *   node scripts/dev/measure_cls_attribution.mjs /posts/2026/08/25/Some_Slug/
 *   node scripts/dev/measure_cls_attribution.mjs /posts/... --allow giscus.app
 *   node scripts/dev/measure_cls_attribution.mjs /posts/... --scroll
 *
 * --scroll walks the page top-to-bottom before settling, because a shift below
 * the fold is only recorded once it is in (or near) the viewport.
 */

import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const argv = process.argv.slice(2);
const urlPath = argv.find((a) => a.startsWith('/'));
if (!urlPath) {
  console.error('usage: measure_cls_attribution.mjs /posts/YYYY/MM/DD/slug/ [--allow host] [--scroll]');
  process.exit(2);
}
const allow = argv.reduce((acc, a, i) => (a === '--allow' && argv[i + 1] ? acc.concat(argv[i + 1]) : acc), []);
const doScroll = argv.includes('--scroll');

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '_site');
if (!fs.existsSync(SITE)) {
  console.error(`No _site at ${SITE} — build first.`);
  process.exit(2);
}

const MIME = {
  '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  '.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.avif': 'image/avif',
};

const server = http.createServer((req, res) => {
  const u = decodeURIComponent((req.url || '/').split('?')[0]);
  const candidates = u.endsWith('/')
    ? [path.join(SITE, u, 'index.html')]
    : [path.join(SITE, u), path.join(SITE, u, 'index.html')];
  for (const c of candidates) {
    const r = path.resolve(c);
    if (!r.startsWith(SITE)) continue;
    if (fs.existsSync(r) && fs.statSync(r).isFile()) {
      res.writeHead(200, { 'Content-Type': MIME[path.extname(r)] || 'application/octet-stream' });
      return fs.createReadStream(r).pipe(res);
    }
  }
  res.writeHead(404).end('nf');
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1512, height: 827 } });
await ctx.route('**/*', (route) => {
  const url = route.request().url();
  if (url.startsWith(base)) return route.continue();
  if (allow.some((a) => url.includes(a))) return route.continue();
  return route.abort();
});
const page = await ctx.newPage();

// Record every shift with its sources. `sources` carries the nodes that MOVED,
// which is exactly the distinction the field report could not make.
await page.addInitScript(() => {
  window.__cls = 0;
  window.__entries = [];
  const describe = (node) => {
    if (!node || node.nodeType !== 1) return '(no node)';
    const id = node.id ? `#${node.id}` : '';
    const cls = node.className && typeof node.className === 'string'
      ? '.' + node.className.trim().split(/\s+/).slice(0, 3).join('.')
      : '';
    return `${node.tagName}${id}${cls}`;
  };
  new PerformanceObserver((list) => {
    for (const e of list.getEntries()) {
      if (e.hadRecentInput) continue;
      window.__cls += e.value;
      window.__entries.push({
        value: e.value,
        t: Math.round(e.startTime),
        sources: (e.sources || []).map((s) => ({
          el: describe(s.node),
          from: s.previousRect ? [Math.round(s.previousRect.y), Math.round(s.previousRect.height)] : null,
          to: s.currentRect ? [Math.round(s.currentRect.y), Math.round(s.currentRect.height)] : null,
        })),
      });
    }
  }).observe({ type: 'layout-shift', buffered: true });
});

await page.goto(base + urlPath, { waitUntil: 'load', timeout: 60000 });
await page.waitForTimeout(4000);

if (doScroll) {
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < h; y += 700) {
    await page.evaluate((yy) => window.scrollTo(0, yy), y);
    await page.waitForTimeout(220);
  }
  await page.waitForTimeout(2500);
}

const total = await page.evaluate(() => window.__cls);
const entries = await page.evaluate(() => window.__entries);

console.log(`\nURL      : ${urlPath}`);
console.log(`third-party allowed: ${allow.length ? allow.join(', ') : '(none — first-party floor)'}`);
console.log(`scrolled : ${doScroll}`);
console.log(`TOTAL CLS: ${total.toFixed(4)}   (${entries.length} shift entries)\n`);

// Aggregate by element so the headline answer is "what moved, and how much".
const byEl = new Map();
for (const e of entries) {
  for (const s of e.sources) {
    byEl.set(s.el, (byEl.get(s.el) || 0) + e.value / Math.max(1, e.sources.length));
  }
}
if (byEl.size) {
  console.log('per-element share (a source is a node that MOVED, not necessarily the cause):');
  [...byEl.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12)
    .forEach(([el, v]) => console.log(`  ${v.toFixed(4)}  ${el}`));
} else {
  console.log('no shift sources recorded.');
}

const top = entries.slice().sort((a, b) => b.value - a.value).slice(0, 6);
if (top.length) {
  console.log('\nlargest individual shifts:');
  for (const e of top) {
    console.log(`  ${e.value.toFixed(4)} @ ${e.t}ms`);
    for (const s of e.sources.slice(0, 4)) {
      console.log(`      ${s.el}  y/h ${JSON.stringify(s.from)} -> ${JSON.stringify(s.to)}`);
    }
  }
}
console.log('');

await browser.close();
server.close();
