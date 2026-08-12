// CSP violation gate for the INTERACTION path.
//
// Why this exists
// ---------------
// `vercel.json` ships a Content-Security-Policy-Report-Only that drops
// 'unsafe-inline' from script-src and allows only the two first-party inline-script
// hashes. It is the preview of "Path B" — removing 'unsafe-inline' from the enforcing
// policy. The question Path B turns on is: does anything actually violate it?
//
// Measured 2026-08-12 with headless Chrome on production: **zero** violations on page
// load, on both the homepage and a post. But that measurement only covers what runs
// before load. `assets/js/head-runtime.js` defers GA / AdSense / Kakao / Sentry behind
// the first user interaction (pointermove, scroll, keydown, touchstart, click) with an
// idle safety-net, and `assets/js/google-translate.js` only initialises the Translate
// widget on demand. Those are exactly the scripts most likely to inject inline code,
// and a page-load-only check cannot see them.
//
// This gate closes that gap: it loads the page, fires the real interaction events,
// waits for the deferred third parties to load and execute, and asserts that the
// Report-Only policy recorded no violations. Violations are collected structurally via
// the `securitypolicyviolation` DOM event (the same approach as
// check_mermaid_csp_render.mjs), not by scraping console text — report-only violations
// fire that event too, and the event carries the directive and blocked URI.
//
// Each URL is driven twice, in 'interaction' and 'translated' mode — see checkUrl().
// The second pass exists because Google Translate rewrites the whole document, and the
// gate previously never reached that state.
//
// Usage
//   node scripts/tests/check_csp_interaction_violations.mjs [--url <url>] [--verbose]
//
// Exit 0 = no violations attributable to first-party code.
// Exit 1 = at least one violation survived; the report names the directive and URI.
// Exit 2 = the run could not be performed (navigation failed, no policy present) —
//          deliberately NOT exit 0, because "we could not check" must never read as
//          "nothing was wrong".

import { chromium } from 'playwright';
import fs from 'node:fs';

const DEFAULT_URLS = [
  'https://tech.2twodragon.com/',
  'https://tech.2twodragon.com/posts/2026/08/11/Tech_Security_Weekly_Digest_AI_Ransomware_Go_AWS/',
];

// head-runtime.js binds these five, capture+passive, to trigger its lazy loaders.
const INTERACTION_EVENTS = ['pointermove', 'scroll', 'keydown', 'touchstart', 'click'];

const NAV_TIMEOUT_MS = 45_000;
// head-runtime.js also has a 10-12s idle safety net; give the deferred scripts room to
// load and execute after the interaction fires.
const SETTLE_MS = 12_000;

const argv = process.argv.slice(2);
const verbose = argv.includes('--verbose');
const urlFlag = argv.indexOf('--url');
const urls = urlFlag !== -1 ? [argv[urlFlag + 1]] : DEFAULT_URLS;
// Coverage is reported always, but only ENFORCED on request: a third-party CDN being
// unreachable from a CI runner would otherwise produce a red run every time, which is
// the muted-noise failure mode this repo has been repairing all week.
const requireCoverage = argv.includes('--require-coverage');
const baselineFlag = argv.indexOf('--baseline');
const baselinePath = baselineFlag !== -1 ? argv[baselineFlag + 1] : null;

/**
 * Grandfathered violations, keyed as `effectiveDirective|blockedURI`.
 *
 * The Google Translate path violates the Report-Only policy today: clicking
 * #lang-toggle creates about:blank frames whose inline script trips
 * script-src-elem. Verified 2026-08-12 WITHOUT any Playwright injection — a
 * console-only observation reproduces it, so it is the site's behaviour, not the
 * instrument's. Wiring this gate as blocking without a baseline would make CI red on
 * every PR for a pre-existing condition, which is the muted-noise failure mode this
 * repo spent the week removing. New violations still fail.
 */
function loadBaseline() {
  if (!baselinePath) return new Set();
  try {
    const text = fs.readFileSync(baselinePath, 'utf8');
    return new Set(
      text
        .split('\n')
        .map((l) => l.replace(/#.*$/, '').trim())
        .filter(Boolean),
    );
  } catch {
    fail(`baseline file not readable: ${baselinePath}`);
    process.exit(2);
  }
}

function violationKey(v) {
  return `${v.effectiveDirective}|${v.blockedURI}`;
}

function fail(msg) {
  console.error(`\n✗ ${msg}`);
}

/**
 * Violations whose blockedURI points at a browser extension or at a scheme we do not
 * control are not ours. The user-reported console dump that started this work was
 * dominated by MetaMask (`chrome-extension://`) WebAssembly violations; adding
 * 'unsafe-eval' to satisfy an extension would weaken the policy for every visitor.
 */
function isFirstPartyConcern(v) {
  const uri = (v.blockedURI || '').toLowerCase();
  if (uri.startsWith('chrome-extension:') || uri.startsWith('moz-extension:')) return false;
  if (uri === 'about' || uri.startsWith('about:')) return false;
  return true;
}

/**
 * Drive the page in one of two modes.
 *
 * 'interaction' — load, fire the deferred-loader triggers, click #lang-toggle.
 * 'translated'  — additionally pre-set the `googtrans` cookie and `preferredLang`
 *                 that the site's own changeLang() writes, so the page loads
 *                 already translated and the gate sees the DOM Google Translate
 *                 actually produces.
 *
 * Why the second mode exists: driving `.goog-te-combo` (what this gate used to
 * attempt) never works headlessly — the dropdown widget renders inside
 * about:blank frames and the combo never appears in the main document, so
 * `translate-select` was permanently false and the translated page state was
 * never exercised. The cookie path is the same one a returning visitor hits, and
 * it does translate: verified 2026-08-12 on production, body Hangul 1061 -> 0
 * chars with 446 <font> marker elements injected.
 */
async function checkUrl(browser, url, mode = 'interaction') {
  const context = await browser.newContext();
  if (mode === 'translated') {
    await context.addCookies([
      { name: 'googtrans', value: '/ko/en', domain: `.${new URL(url).hostname}`, path: '/' },
    ]);
  }
  const page = await context.newPage();
  if (mode === 'translated') {
    await page.addInitScript(() => {
      try {
        localStorage.setItem('preferredLang', 'en');
      } catch (_e) {
        /* private mode — the cookie alone still drives the translation */
      }
    });
  }

  // Authoritative record of what the page fetched. Neither `document.scripts` nor
  // Resource Timing is reliable here: Google's translate_a/element.js removes its own
  // <script> node after running, and Resource Timing silently stops recording once the
  // 250-entry default buffer fills — which this page exceeds, so a late-loading script
  // vanishes from it. The CDP-level request log has neither problem.
  const requested = [];
  page.on('request', (r) => requested.push(r.url()));

  const violations = [];
  await page.exposeFunction('__reportCspViolation', (v) => violations.push(v));
  await page.addInitScript(() => {
    document.addEventListener('securitypolicyviolation', (e) => {
      // eslint-disable-next-line no-undef
      window.__reportCspViolation({
        effectiveDirective: e.effectiveDirective,
        violatedDirective: e.violatedDirective,
        blockedURI: e.blockedURI,
        disposition: e.disposition,
        sourceFile: e.sourceFile,
        lineNumber: e.lineNumber,
      });
    });
  });

  // Confirm a report-only policy is actually present. Without it this gate would pass
  // trivially — the same vacuous-green shape the 2026-08 CI audit kept finding.
  let sawReportOnly = false;
  page.on('response', (res) => {
    if (res.url() === url && res.headers()['content-security-policy-report-only']) {
      sawReportOnly = true;
    }
  });

  const response = await page
    .goto(url, { waitUntil: 'load', timeout: NAV_TIMEOUT_MS })
    .catch((e) => {
      fail(`navigation failed for ${url}: ${e.message}`);
      return null;
    });
  if (!response) {
    await context.close();
    return { url, ok: false, reason: 'navigation', violations };
  }

  // Fire the interaction the lazy loaders are waiting for. A real pointer move plus a
  // scroll covers pointermove/scroll; the rest are dispatched directly so a headless
  // run without a pointer device still trips them.
  await page.mouse.move(200, 200).catch(() => {});
  await page.mouse.wheel(0, 400).catch(() => {});
  await page.evaluate((events) => {
    for (const type of events) {
      window.dispatchEvent(new Event(type, { bubbles: true }));
    }
  }, INTERACTION_EVENTS);

  // AdSense loads only when a `.adsbygoogle` slot enters the viewport
  // (head-runtime.js installs an IntersectionObserver on it), so a shallow scroll
  // never reaches it. Bring the slot into view explicitly.
  const adSlotScrolled = await page
    .locator('.adsbygoogle')
    .first()
    .scrollIntoViewIfNeeded({ timeout: 5_000 })
    .then(() => true)
    .catch(() => false);

  // Translate: google-translate.js loads Google's element.js from a click on
  // #lang-toggle, then exposes `.goog-te-combo`. Clicking is the only way in — the
  // widget container is display:none until then. Changing the select is what actually
  // translates the page, which is the deepest interaction path we can drive headlessly.
  const langToggleClicked = await page
    .locator('#lang-toggle')
    .first()
    .click({ timeout: 5_000 })
    .then(() => true)
    .catch(() => false);

  await page.waitForTimeout(4_000);

  const translated = await page
    .evaluate(() => {
      const select = document.querySelector('.goog-te-combo');
      if (!select) return false;
      select.value = 'en';
      select.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    })
    .catch(() => false);

  await page.waitForTimeout(SETTLE_MS);

  // What actually loaded, so a green result is auditable rather than assumed.
  //
  // Sourced from the request log above, not from a DOM scan: element.js deletes its
  // own <script> node once it has run, so `document.scripts` reported translate=false
  // for a script that demonstrably loaded and executed (verified 2026-08-12 — the
  // element.js request fires and pulls in translate_http JS/CSS and translate-pa
  // supportedLanguages, while `script[src*="translate_a/element.js"]` is null). A gate
  // understating its own coverage is the failure mode this file exists to prevent.
  const has = (needle) => requested.some((s) => s.includes(needle));
  const inlineExecutable = await page.evaluate(
    () =>
      Array.from(document.scripts).filter(
        (s) => !s.src && s.type !== 'application/ld+json' && s.textContent.trim(),
      ).length,
  );
  const loaded = {
    gtm: has('googletagmanager'),
    adsense: has('googlesyndication'),
    sentry: has('sentry-cdn'),
    kakao: has('kakao'),
    translate: has('translate.google') || has('translate_a'),
    inlineExecutable,
  };

  // Which integrations the page is CONFIGURED for. Distinguishes "did not load
  // because it is not configured" (fine) from "configured but this gate failed to
  // trigger it" (a coverage gap that must not read as coverage).
  const configured = await page.evaluate(() => {
    const el = document.getElementById('head-runtime-script');
    const attr = (n) => Boolean(el && (el.getAttribute(n) || '').trim());
    return {
      gtm: attr('data-ga-id'),
      adsense: attr('data-adsense-client'),
      kakao: attr('data-kakao-app-key'),
      sentry: attr('data-sentry-dsn'),
      translate: Boolean(document.getElementById('lang-toggle')),
    };
  });

  // Did Google Translate actually rewrite the document? `translated-ltr` on <html>
  // and the <font> wrappers are Google's own markers. In 'translated' mode a false
  // here means the gate did not reach the translated state, so its green says
  // nothing about that code path.
  const translation = await page.evaluate(() => {
    const text = document.body.innerText || '';
    return {
      applied: document.documentElement.classList.contains('translated-ltr'),
      htmlLang: document.documentElement.lang,
      fontMarkers: document.querySelectorAll('font').length,
      hangulChars: (text.match(/[가-힣]/g) || []).length,
    };
  });

  await context.close();

  const baseline = loadBaseline();
  const mine = violations
    .filter(isFirstPartyConcern)
    .filter((v) => !baseline.has(violationKey(v)));
  const grandfathered = violations
    .filter(isFirstPartyConcern)
    .filter((v) => baseline.has(violationKey(v)));
  const uncovered = Object.keys(configured).filter((k) => configured[k] && !loaded[k]);
  return {
    url, mode, ok: true, sawReportOnly, translated, adSlotScrolled, langToggleClicked,
    loaded, configured, uncovered, translation, violations, mine, grandfathered,
  };
}

async function main() {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const results = [];
  for (const url of urls) {
    results.push(await checkUrl(browser, url, 'interaction'));
    results.push(await checkUrl(browser, url, 'translated'));
  }
  await browser.close();

  let exitCode = 0;
  for (const r of results) {
    if (!r.ok) {
      exitCode = 2;
      continue;
    }
    const path = `${new URL(r.url).pathname} [${r.mode}]`;
    console.log(`\n${path}`);
    console.log(`  report-only header present : ${r.sawReportOnly ? 'yes' : 'NO'}`);
    console.log(
      `  deferred third parties     : gtm=${r.loaded.gtm} adsense=${r.loaded.adsense} ` +
        `sentry=${r.loaded.sentry} kakao=${r.loaded.kakao} translate=${r.loaded.translate}`,
    );
    console.log(
      `  triggers fired             : ad-slot-scrolled=${r.adSlotScrolled} ` +
        `lang-toggle-clicked=${r.langToggleClicked} translate-select=${r.translated}`,
    );
    console.log(
      `  coverage                   : ${r.uncovered.length === 0 ? 'all configured integrations loaded' : 'NOT COVERED -> ' + r.uncovered.join(', ')}`,
    );
    console.log(
      `  translated DOM reached     : ${r.translation.applied} ` +
        `(html lang=${r.translation.htmlLang || '?'}, ${r.translation.fontMarkers} <font> markers, ` +
        `${r.translation.hangulChars} Hangul chars left)`,
    );
    console.log(`  executable inline scripts  : ${r.loaded.inlineExecutable}`);
    console.log(
      `  CSP violations             : ${r.violations.length} total, ` +
        `${r.grandfathered.length} grandfathered, ${r.mine.length} NEW first-party`,
    );

    if (!r.sawReportOnly) {
      fail(`${path}: no Content-Security-Policy-Report-Only header — this gate would pass vacuously`);
      exitCode = 2;
    }
    if (verbose || r.mine.length) {
      for (const v of r.violations) {
        const tag = isFirstPartyConcern(v) ? 'FIRST-PARTY' : 'extension/ignored';
        console.log(
          `    [${tag}] ${v.disposition} ${v.effectiveDirective} blocked=${v.blockedURI} ` +
            `at ${v.sourceFile || '?'}:${v.lineNumber ?? '?'}`,
        );
      }
    }
    if (r.uncovered.length) {
      const msg =
        `${path}: configured but never loaded: ${r.uncovered.join(', ')} — this run did ` +
        `NOT exercise those code paths, so a green result does not cover them.`;
      if (requireCoverage) {
        fail(msg);
        exitCode = Math.max(exitCode, 2);
      } else {
        console.log(`  ::warning:: ${msg}`);
      }
    }
    // A 'translated' run that never reached the translated DOM covers no more than the
    // 'interaction' run does. Say so rather than letting the extra pass imply coverage
    // it did not deliver.
    if (r.mode === 'translated' && !r.translation.applied) {
      const msg =
        `${path}: googtrans cookie was set but the document was never translated ` +
        `(html lang=${r.translation.htmlLang || '?'}, ${r.translation.fontMarkers} <font> markers) ` +
        `— this pass adds no coverage over the interaction pass.`;
      if (requireCoverage) {
        fail(msg);
        exitCode = Math.max(exitCode, 2);
      } else {
        console.log(`  ::warning:: ${msg}`);
      }
    }
    if (r.mine.length) {
      fail(
        `${path}: ${r.mine.length} first-party CSP violation(s). Removing 'unsafe-inline' ` +
          `from the enforcing policy would break these. Hash or externalise them first.`,
      );
      exitCode = 1;
    }
  }

  if (exitCode === 0) {
    console.log('\n✓ No first-party CSP violations on the interaction path.');
  }
  process.exit(exitCode);
}

main().catch((e) => {
  fail(`unexpected error: ${e.stack || e.message}`);
  process.exit(2);
});
