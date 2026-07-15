#!/usr/bin/env node
// Mermaid CSP-render regression guard.
//
// Proves that every mermaid diagram in the corpus still renders under the
// ENFORCING Content-Security-Policy defined in vercel.json — which no longer
// grants 'unsafe-eval' to script-src (commit d018fe06). If a future mermaid or
// dependency bump reintroduces an eval/wasm-eval dependency, the render breaks
// and this gate fails CI.
//
// Usage:
//   node scripts/tests/check_mermaid_csp_render.mjs [--verbose] [--live]
//
//   --verbose  Per-post detail (rendered roles, violations, console errors).
//   --live     Render live production URLs (https://tech.2twodragon.com/...)
//              instead of the committed default, the local _site build.
//
// Exit 0 = all mermaid posts rendered cleanly under the no-eval policy.
// Exit 1 = one or more posts failed (count mismatch, eval CSP violation, or
//          a mermaid syntax-error diagram), or a setup error.

import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, '..', '..');
const POSTS_DIR = path.join(REPO_ROOT, '_posts');
const SITE_DIR = path.join(REPO_ROOT, '_site');
const VERCEL_JSON = path.join(REPO_ROOT, 'vercel.json');
const LIVE_ORIGIN = 'https://tech.2twodragon.com';

const RENDER_TIMEOUT_MS = 15000;

const args = process.argv.slice(2);
const VERBOSE = args.includes('--verbose');
const LIVE = args.includes('--live');

function fail(msg) {
  console.error(`\n✗ ${msg}`);
  process.exit(1);
}

// --- 1. Discover mermaid posts + declared diagram types ---------------------

// Map a mermaid diagram's declared type to the aria-roledescription mermaid
// stamps on the rendered <svg>.
function typeToRole(declared) {
  if (declared === 'sequenceDiagram') return 'sequence';
  if (declared === 'flowchart' || declared === 'graph') return 'flowchart-v2';
  return null; // unknown type — counted toward total, not per-role
}

function scanPostForMermaid(filePath) {
  const text = fs.readFileSync(filePath, 'utf8');
  const lines = text.split('\n');
  const diagrams = [];
  let inBlock = false;
  let pendingType = null; // true while waiting for first non-empty line in a block
  for (const raw of lines) {
    const line = raw.trim();
    if (!inBlock) {
      if (line === '```mermaid' || line === '~~~mermaid') {
        inBlock = true;
        pendingType = true;
      }
    } else if (line === '```' || line === '~~~') {
      inBlock = false;
    } else if (pendingType && line.length > 0) {
      const declared = line.split(/\s+/)[0];
      diagrams.push({ declared, role: typeToRole(declared) });
      pendingType = false;
    }
  }
  return diagrams;
}

function slugFromFilename(name) {
  // 2026-07-13-Tech_Security_...md -> Tech_Security_...
  return name.replace(/^\d{4}-\d{2}-\d{2}-/, '').replace(/\.md$/, '');
}

function discoverPosts() {
  const files = fs
    .readdirSync(POSTS_DIR)
    .filter((f) => f.endsWith('.md'))
    .sort();
  const posts = [];
  for (const f of files) {
    const diagrams = scanPostForMermaid(path.join(POSTS_DIR, f));
    if (diagrams.length > 0) {
      posts.push({ file: f, slug: slugFromFilename(f), diagrams });
    }
  }
  return posts;
}

// --- 2. Map each post to its built HTML (slug-robust, UTC-shift-safe) --------

function findBuiltHtml(slug) {
  const postsRoot = path.join(SITE_DIR, 'posts');
  if (!fs.existsSync(postsRoot)) {
    fail(`_site/posts not found — build the site first (JEKYLL_ENV=production ./build.sh). Looked in ${postsRoot}`);
  }
  // Collect EVERY <slug>/index.html under _site/posts. A post can match more
  // than once: the canonical permalink /posts/YYYY/MM/DD/<slug>/ AND any
  // jekyll-redirect-from meta-refresh stubs (e.g. the month-only
  // /posts/YYYY/MM/<slug>/). The stubs contain no body, so we must select the
  // canonical page — the match whose date path is exactly YYYY/MM/DD.
  const matches = [];
  const stack = [postsRoot];
  while (stack.length) {
    const dir = stack.pop();
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const full = path.join(dir, entry.name);
      if (entry.name === slug && fs.existsSync(path.join(full, 'index.html'))) {
        const datePath = path.relative(postsRoot, dir).split(path.sep).join('/');
        matches.push({ index: path.join(full, 'index.html'), datePath });
      }
      stack.push(full);
    }
  }
  // Canonical permalink = 3-segment numeric date (UTC-shift-safe: the day may
  // differ from the filename date, but it is always present).
  const canonical = matches.filter((m) => /^\d{4}\/\d{2}\/\d{2}$/.test(m.datePath));
  if (canonical.length === 1) return canonical[0].index;
  if (canonical.length > 1) {
    fail(`Ambiguous canonical build for slug "${slug}": ${canonical.map((m) => m.datePath).join(', ')}`);
  }
  return null;
}

// Convert a "YYYY-MM-DD HH:MM:SS +0900" front-matter date to its UTC calendar
// date, so --live can build the permalink even when a KST 00:00-08:59 post
// shifts to the previous UTC day.
function liveUrlForPost(filePath, slug) {
  const text = fs.readFileSync(filePath, 'utf8');
  const m = text.match(/^date:\s*(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})\s*([+-]\d{2})(\d{2})/m);
  if (!m) fail(`Cannot parse date front matter for --live URL of ${path.basename(filePath)}`);
  const [, y, mo, d, h, mi, s, offH, offM] = m;
  const offsetMin = parseInt(offH, 10) * 60 + Math.sign(parseInt(offH, 10)) * parseInt(offM, 10);
  const utcMs = Date.UTC(+y, +mo - 1, +d, +h, +mi, +s) - offsetMin * 60000;
  const dt = new Date(utcMs);
  const yyyy = dt.getUTCFullYear();
  const mm = String(dt.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(dt.getUTCDate()).padStart(2, '0');
  return `/posts/${yyyy}/${mm}/${dd}/${slug}/`;
}

// --- 3. Extract the ENFORCING CSP from vercel.json --------------------------

function extractEnforcingCsp() {
  const cfg = JSON.parse(fs.readFileSync(VERCEL_JSON, 'utf8'));
  for (const rule of cfg.headers || []) {
    for (const h of rule.headers || []) {
      if (h.key === 'Content-Security-Policy') return h.value;
    }
  }
  fail('No enforcing "Content-Security-Policy" header found in vercel.json (only Report-Only?).');
}

// --- 4. Local static server rooted at _site --------------------------------

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico': 'image/png',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
};

function startStaticServer() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let urlPath = decodeURIComponent((req.url || '/').split('?')[0]);
      const candidates = [];
      if (urlPath.endsWith('/')) candidates.push(path.join(SITE_DIR, urlPath, 'index.html'));
      else {
        candidates.push(path.join(SITE_DIR, urlPath));
        candidates.push(path.join(SITE_DIR, `${urlPath}.html`)); // cleanUrls
        candidates.push(path.join(SITE_DIR, urlPath, 'index.html'));
      }
      for (const filePath of candidates) {
        const resolved = path.resolve(filePath);
        if (!resolved.startsWith(SITE_DIR)) continue; // traversal guard
        if (fs.existsSync(resolved) && fs.statSync(resolved).isFile()) {
          res.writeHead(200, { 'Content-Type': MIME[path.extname(resolved)] || 'application/octet-stream' });
          res.end(fs.readFileSync(resolved));
          return;
        }
      }
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not found');
    });
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

// --- 5-7. Render one post + assert -----------------------------------------

async function renderPost(browser, pageUrl, enforcingCsp, expectedCount) {
  const context = await browser.newContext();
  const page = await context.newPage();

  const violations = [];
  const consoleErrors = [];

  await page.exposeFunction('__reportCspViolation', (v) => violations.push(v));
  await page.addInitScript(() => {
    document.addEventListener('securitypolicyviolation', (e) => {
      // eslint-disable-next-line no-undef
      window.__reportCspViolation({
        effectiveDirective: e.effectiveDirective,
        violatedDirective: e.violatedDirective,
        blockedURI: e.blockedURI,
      });
    });
  });
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  // Inject the enforcing CSP onto the main document, replacing whatever the
  // origin sent (local server sends none; prod sends its own + Report-Only).
  await page.route(pageUrl, async (route) => {
    const response = await route.fetch();
    const headers = { ...response.headers() };
    headers['content-security-policy'] = enforcingCsp;
    delete headers['content-security-policy-report-only'];
    await route.fulfill({ response, headers });
  });

  await page.goto(pageUrl, { waitUntil: 'load', timeout: RENDER_TIMEOUT_MS }).catch(() => {});

  await page
    .waitForFunction(
      (n) => document.querySelectorAll('svg[aria-roledescription]').length >= n,
      expectedCount,
      { timeout: RENDER_TIMEOUT_MS }
    )
    .catch(() => {});

  const rendered = await page.evaluate(() => {
    const svgs = Array.from(document.querySelectorAll('svg[aria-roledescription]'));
    const roles = svgs.map((s) => s.getAttribute('aria-roledescription'));
    const errorDiagram = Array.from(document.querySelectorAll('.mermaid, [id^="mermaid"]')).some((el) =>
      /syntax error/i.test(el.textContent || '')
    );
    return { roles, errorDiagram };
  });

  await context.close();
  return { rendered, violations, consoleErrors };
}

function evalViolations(violations) {
  return violations.filter((v) => {
    const dir = (v.effectiveDirective || v.violatedDirective || '').toLowerCase();
    const uri = (v.blockedURI || '').toLowerCase();
    return dir.includes('script-src') && (uri === 'eval' || uri.includes('eval') || uri.includes('wasm-eval'));
  });
}

// --- Main -------------------------------------------------------------------

async function main() {
  const posts = discoverPosts();
  if (posts.length === 0) fail('No mermaid posts discovered in _posts/*.md — expected at least one fenced ```mermaid block.');

  const enforcingCsp = extractEnforcingCsp();
  if (!/script-src\b/.test(enforcingCsp)) fail('Enforcing CSP has no script-src directive — cannot evaluate eval policy.');
  const hasUnsafeEval = /script-src[^;]*'unsafe-eval'/.test(enforcingCsp);

  console.log(`Mermaid CSP-render guard  |  mode: ${LIVE ? 'LIVE (production)' : 'local _site'}  |  posts: ${posts.length}`);
  console.log(`Enforcing script-src grants 'unsafe-eval': ${hasUnsafeEval ? 'YES (policy relaxed)' : 'NO (eval blocked — guard is meaningful)'}`);
  console.log('');

  let server = null;
  let baseUrl = LIVE_ORIGIN;
  if (!LIVE) {
    server = await startStaticServer();
    const { port } = server.address();
    baseUrl = `http://127.0.0.1:${port}`;
  }

  const browser = await chromium.launch();
  const failures = [];

  for (const post of posts) {
    let urlPath;
    if (LIVE) {
      urlPath = liveUrlForPost(path.join(POSTS_DIR, post.file), post.slug);
    } else {
      const built = findBuiltHtml(post.slug);
      if (!built) {
        failures.push({ post, reasons: [`built HTML not found for slug "${post.slug}" under _site/posts/**`] });
        console.log(`✗ ${post.slug}  (built HTML missing)`);
        continue;
      }
      urlPath = '/' + path.relative(SITE_DIR, path.dirname(built)).split(path.sep).join('/') + '/';
    }
    const pageUrl = baseUrl + urlPath;

    const expectedCount = post.diagrams.length;
    const expectedRoles = post.diagrams.map((d) => d.role).filter(Boolean);

    let result;
    try {
      result = await renderPost(browser, pageUrl, enforcingCsp, expectedCount);
    } catch (err) {
      failures.push({ post, reasons: [`render threw: ${err.message}`] });
      console.log(`✗ ${post.slug}  (render error: ${err.message})`);
      continue;
    }

    const { rendered, violations } = result;
    const evals = evalViolations(violations);
    const reasons = [];

    // (a) rendered diagram count matches source count
    if (rendered.roles.length !== expectedCount) {
      reasons.push(`rendered ${rendered.roles.length} svg[aria-roledescription], expected ${expectedCount}`);
    }
    // per-type check for the known roles declared in source
    for (const role of new Set(expectedRoles)) {
      const want = expectedRoles.filter((r) => r === role).length;
      const got = rendered.roles.filter((r) => r === role).length;
      if (got < want) reasons.push(`role "${role}": rendered ${got}, expected ${want}`);
    }
    // (b) zero eval-related script-src CSP violations
    if (evals.length > 0) {
      reasons.push(`${evals.length} eval-related script-src CSP violation(s): ${evals.map((e) => e.blockedURI).join(', ')}`);
    }
    // (c) no mermaid error diagram
    if (rendered.errorDiagram) reasons.push('mermaid rendered a "Syntax error" diagram');

    const declaredSummary = post.diagrams.map((d) => d.declared).join(', ');
    if (reasons.length === 0) {
      console.log(`✓ ${post.slug}  (${expectedCount} diagram(s): ${declaredSummary})`);
      if (VERBOSE) {
        console.log(`    rendered roles: [${rendered.roles.join(', ')}]`);
        console.log(`    CSP violations: ${violations.length} (eval-related: ${evals.length})`);
        if (result.consoleErrors.length) console.log(`    console errors: ${result.consoleErrors.length}`);
      }
    } else {
      failures.push({ post, reasons });
      console.log(`✗ ${post.slug}  (${expectedCount} diagram(s): ${declaredSummary})`);
      for (const r of reasons) console.log(`    - ${r}`);
      if (VERBOSE) {
        console.log(`    rendered roles: [${rendered.roles.join(', ')}]`);
        console.log(`    all CSP violations: ${JSON.stringify(violations)}`);
        if (result.consoleErrors.length) console.log(`    console errors: ${result.consoleErrors.slice(0, 10).join(' | ')}`);
      }
    }
  }

  await browser.close();
  if (server) server.close();

  console.log('');
  if (failures.length > 0) {
    console.log(`FAIL: ${failures.length}/${posts.length} mermaid post(s) failed the no-eval CSP render gate.`);
    process.exit(1);
  }
  console.log(`PASS: all ${posts.length} mermaid post(s) rendered under the enforcing CSP with no eval dependency.`);
  process.exit(0);
}

main().catch((err) => fail(`Unexpected error: ${err.stack || err.message}`));
