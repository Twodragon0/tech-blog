#!/usr/bin/env node
/**
 * Resource-hint usage gate (real browser, local build).
 *
 * `scripts/check_asset_hint_version.py` reads the templates and catches one
 * failure mode: a hint whose href omits the `?v=` its loader uses. That is a
 * static check and it cannot see the other half of the problem — whether the
 * hinted URL is ever requested at all, and whether the page ends up fetching
 * two URL variants of the same file. Only a browser knows that.
 *
 * This gate loads pages from the local `_site` build in Chromium and fails when
 * a same-origin preload/prefetch/modulepreload is either:
 *
 *   1. NEVER-FETCHED  — the hint downloads nothing the page uses, or
 *   2. SPLIT          — the same file is fetched under two different URLs
 *                       (the versionless/versioned split that cost ~14 KB per
 *                       post view until 2026-08-14).
 *
 * Determinism: every non-local request is aborted. Third-party behaviour
 * (AdSense fill, Sentry, giscus) varies run to run and would make this flaky,
 * and CI has no business shipping page loads to external services. That means
 * cross-origin preconnect/dns-prefetch hints are deliberately NOT judged here —
 * several of them (Translate, DeepSeek chat) are lazy on user interaction and
 * are *expected* to be unused on initial load, so "unused" is not a defect
 * signal for them.
 *
 * Usage:
 *   node scripts/tests/check_resource_hint_usage.mjs [--verbose]
 *
 * Requires a build first:  JEKYLL_ENV=production ./build.sh   (or jekyll build)
 */

import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const SITE_DIR = path.join(REPO_ROOT, '_site');
const VERBOSE = process.argv.includes('--verbose');

const HINT_RELS = new Set(['preload', 'prefetch', 'modulepreload']);

function fail(msg) {
  console.error(`[hint-usage] ${msg}`);
  process.exit(1);
}

if (!fs.existsSync(SITE_DIR)) {
  fail(`_site not found — build first (JEKYLL_ENV=production ./build.sh). Looked in ${SITE_DIR}`);
}

/** Pick representative pages: home plus the first post (layout: post carries the most hints). */
function pickPages() {
  const pages = ['/'];
  const postsRoot = path.join(SITE_DIR, 'posts');
  if (fs.existsSync(postsRoot)) {
    const stack = [postsRoot];
    const found = [];
    while (stack.length && found.length < 400) {
      const dir = stack.pop();
      for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, e.name);
        if (e.isDirectory()) stack.push(full);
        else if (e.name === 'index.html') found.push(full);
      }
    }
    found.sort();
    if (found.length) {
      pages.push('/' + path.relative(SITE_DIR, found[found.length - 1]).replace(/index\.html$/, '').split(path.sep).join('/'));
    }
  }
  return pages;
}

function startServer() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const urlPath = decodeURIComponent((req.url || '/').split('?')[0]);
      const candidates = [];
      if (urlPath.endsWith('/')) candidates.push(path.join(SITE_DIR, urlPath, 'index.html'));
      else {
        candidates.push(path.join(SITE_DIR, urlPath));
        candidates.push(path.join(SITE_DIR, `${urlPath}.html`));
        candidates.push(path.join(SITE_DIR, urlPath, 'index.html'));
      }
      for (const c of candidates) {
        const resolved = path.resolve(c);
        if (!resolved.startsWith(SITE_DIR)) continue; // traversal guard
        if (fs.existsSync(resolved) && fs.statSync(resolved).isFile()) {
          const ext = path.extname(resolved);
          const type = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
            '.woff2': 'font/woff2', '.json': 'application/json', '.svg': 'image/svg+xml' }[ext] || 'application/octet-stream';
          res.writeHead(200, { 'Content-Type': type });
          fs.createReadStream(resolved).pipe(res);
          return;
        }
      }
      res.writeHead(404).end('not found');
    });
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

const server = await startServer();
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch();
const problems = [];
let hintsChecked = 0;

for (const pagePath of pickPages()) {
  const context = await browser.newContext();
  const localRequests = [];
  // Abort everything that is not our local server: determinism over realism.
  await context.route('**/*', (route) => {
    const u = route.request().url();
    if (u.startsWith(base)) { localRequests.push(u.split('#')[0]); route.continue(); }
    else route.abort();
  });
  const page = await context.newPage();
  await page.goto(base + pagePath, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(2500);

  const hints = await page.evaluate((rels) =>
    Array.from(document.querySelectorAll('link[rel]'))
      .filter((l) => rels.includes(l.rel))
      .map((l) => ({ rel: l.rel, href: l.href, as: l.getAttribute('as') || '' })),
    [...HINT_RELS]
  );

  for (const h of hints) {
    const href = h.href.split('#')[0];
    if (!href.startsWith(base)) continue; // cross-origin: intentionally not judged
    hintsChecked += 1;
    const hits = localRequests.filter((u) => u === href).length;
    const bare = href.split('?')[0];
    const variants = [...new Set(localRequests.filter((u) => u.split('?')[0] === bare && u !== href))];
    const rel = href.slice(base.length);

    if (hits === 0) {
      problems.push(`${pagePath}: NEVER-FETCHED  rel="${h.rel}" ${rel} — the hint downloads nothing the page uses.`);
    } else if (variants.length) {
      problems.push(
        `${pagePath}: SPLIT  rel="${h.rel}" ${rel} is hinted, but the page also fetches ` +
        variants.map((v) => v.slice(base.length)).join(', ') +
        ` — separate cache entries, so the hinted copy is downloaded and never used.`
      );
    } else if (VERBOSE) {
      console.log(`[hint-usage] OK ${pagePath} ${h.rel} ${rel}`);
    }
  }
  await context.close();
}

await browser.close();
server.close();

if (problems.length) {
  console.error(`[hint-usage] FAIL — ${problems.length} problem(s):\n`);
  for (const p of problems) console.error(`  ${p}`);
  console.error(
    `\n  Fix by either deleting the hint (correct when the page already loads the\n` +
    `  asset — the preload scanner finds it anyway), or making the hint href\n` +
    `  byte-identical to the URL the loader requests.`
  );
  process.exit(1);
}

console.log(`[hint-usage] OK — ${hintsChecked} same-origin hint(s) checked across pages, 0 problems.`);
