#!/usr/bin/env node
/**
 * Measures the `__gaPending` loss path for `web_vitals` events.
 *
 * Why this exists: vitals flush on page hide via `window.__track`
 * (assets/js/performance-monitor.js), but GA itself is lazy-loaded on the
 * first interaction with a 10-12s idle fallback (assets/js/head-runtime.js).
 * When a page hides before `gtag('config')` has run, `__track` parks the
 * event in `window.__gaPending` and it dies with the page. That silently
 * removes exactly the sessions we most want to see: readers who left because
 * the page was slow.
 *
 * This quantifies two distinct loss windows:
 *   A. never-loaded  — no interaction, page hidden before the idle fallback
 *   B. in-flight     — interaction happened, but gtag onload had not fired
 *                      when the page hid
 * and measures the width of window B (interaction -> `__gaReady`).
 *
 * NOTE: a third and larger loss path exists that this harness does NOT model,
 * because it survives here — gtag batches events behind a ~5000ms timer, so a
 * reader who closes the tab or navigates away within 5s of the hide loses the
 * events even when `__gaReady` was true. This harness keeps the page alive, so
 * it always clears that timer. See notes/ga4-web-vitals-delivery-loss.md.
 *
 * Requests to google-analytics collect endpoints are ABORTED at the network
 * layer and only recorded. The harness must never inject synthetic web_vitals
 * into the production property.
 *
 * Usage:
 *   node scripts/dev/measure_ga_pending_loss.mjs [url] [--json] [--runs N]
 */

import { chromium } from 'playwright';

const args = process.argv.slice(2);
const asJson = args.includes('--json');
const runsIdx = args.indexOf('--runs');
const RUNS = runsIdx >= 0 ? Number(args[runsIdx + 1]) : 3;
const url = args.find((a) => !a.startsWith('--') && a !== String(RUNS))
  || 'https://tech.2twodragon.com/';

const GTAG_RE = /googletagmanager\.com\/gtag\/js/;
const COLLECT_RE = /google-analytics\.com\/(g\/)?collect|analytics\.google\.com\/g\/collect/;

/**
 * Opens a page with GA collect blocked-but-recorded, runs `body`, then forces
 * a hide and reports what would have been sent.
 */
async function trial(browser, body) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();

  const collected = [];
  const gtagTimings = [];

  // Capture via CDP, not page.route(): gtag sends these with
  // navigator.sendBeacon, which page.route() does not surface. Counting from
  // the route handler reports a flat 0 and reads as total data loss.
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Network.enable');
  cdp.on('Network.requestWillBeSent', (e) => {
    const u = e.request.url;
    if (GTAG_RE.test(u)) { gtagTimings.push({ requestedAt: Date.now() }); return; }
    if (!COLLECT_RE.test(u)) return;
    const target = `${u}\n${e.request.postData || ''}`;
    // en=<event name>; gtag batches with en= repeated per event.
    for (const m of target.matchAll(/(?:^|[?&\n])en=([^&\s]+)/g)) collected.push(m[1]);
  });
  // Record but never deliver — no synthetic events in the real property.
  await page.route(COLLECT_RE, (route) => route.abort());

  const t0 = Date.now();
  await page.goto(url, { waitUntil: 'domcontentloaded' });

  const result = await body(page, t0);

  // Force the hide path the same way Chrome does: performance-monitor reads
  // document.visibilityState inside the visibilitychange handler.
  const atHide = await page.evaluate(() => {
    const before = {
      gaReady: !!window.__gaReady,
      gaLoadInitiated: !!window.__gaLoadInitiated,
      pending: (window.__gaPending || []).map((e) => e.name),
    };
    Object.defineProperty(document, 'visibilityState', {
      configurable: true,
      get: () => 'hidden',
    });
    document.dispatchEvent(new Event('visibilitychange'));
    return before;
  });

  // Read the buffer straight away: if gtag finishes loading during the long
  // wait below, its onload replays and drains __gaPending, hiding the loss.
  await page.waitForTimeout(150);
  const strandedAtHide = await page.evaluate(() =>
    (window.__gaPending || []).map((e) => e.name)
  );

  // gtag batches events behind a ~5000ms timer (measured: 5003-5005ms, n=4),
  // so anything shorter than that reports 0 sent and reads as data loss when
  // it is only impatience. 6500ms clears the timer with margin.
  await page.waitForTimeout(6500);

  await ctx.close();
  return {
    ...result,
    gaReadyAtHide: atHide.gaReady,
    gaLoadInitiated: atHide.gaLoadInitiated,
    pendingBeforeHide: atHide.pending,
    strandedAfterHide: strandedAtHide,
    vitalsSent: collected.filter((e) => e === 'web_vitals').length,
    allEventsSent: collected,
    gtagRequested: gtagTimings.length > 0,
  };
}

/** Scenario A: reader never interacts and leaves after `waitMs`. */
function noInteraction(waitMs) {
  return async (page) => {
    await page.waitForTimeout(waitMs);
    return { scenario: `no-interaction@${waitMs}ms` };
  };
}

/** Scenario B: reader interacts, then leaves `hideAfterMs` later. */
function interactThenHide(hideAfterMs) {
  return async (page) => {
    await page.waitForTimeout(600);
    await page.mouse.move(200, 300);
    await page.mouse.move(240, 340); // pointermove -> loadOnce()
    await page.mouse.click(240, 340); // generates an INP interaction
    await page.waitForTimeout(hideAfterMs);
    return { scenario: `interact-then-hide@+${hideAfterMs}ms` };
  };
}

/** Scenario C: how long is window B? interaction -> __gaReady. */
function measureReadyLatency() {
  return async (page) => {
    await page.waitForTimeout(600);
    const started = await page.evaluate(() => performance.now());
    await page.mouse.move(200, 300);
    await page.mouse.move(240, 340);
    let readyLatencyMs = null;
    try {
      await page.waitForFunction(() => window.__gaReady === true, null, {
        timeout: 20000,
      });
      readyLatencyMs = Math.round(
        (await page.evaluate(() => performance.now())) - started
      );
    } catch {
      readyLatencyMs = null; // never became ready within 20s
    }
    return { scenario: 'ready-latency', readyLatencyMs };
  };
}

/**
 * Path B: gtag loaded and ready, event reaches dataLayer — but the reader
 * leaves `gapMs` after the hide. gtag's ~5s batch timer has not fired, so the
 * queued events die with the page. This is the common exit (tab close, or an
 * internal link click, since the site is not an SPA).
 *
 * A control sendBeacon fires from the SAME visibilitychange handler. If the
 * control is captured while gtag's events are not, the capture path works
 * during teardown and the absence is real loss, not a measurement artifact.
 */
async function survival(browser, gapMs) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Network.enable');
  const ga = [];
  let control = 0;
  cdp.on('Network.requestWillBeSent', (e) => {
    const u = e.request.url;
    if (/__control_beacon__/.test(u)) { control++; return; }
    if (!COLLECT_RE.test(u)) return;
    const target = `${u}\n${e.request.postData || ''}`;
    for (const m of target.matchAll(/(?:^|[?&\n])en=([^&\s]+)/g)) ga.push(m[1]);
  });
  await page.route(/google-analytics\.com|analytics\.google\.com|__control_beacon__/, (r) =>
    r.abort()
  );

  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(600);
  await page.mouse.move(200, 300);
  await page.mouse.move(240, 340);
  await page.mouse.click(240, 340);
  await page.waitForFunction(() => window.__gaReady === true, null, { timeout: 20000 });
  await page.waitForTimeout(1500);
  ga.length = 0;

  await page.evaluate(() => {
    const fire = () => navigator.sendBeacon('/__control_beacon__?t=' + Date.now());
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') fire();
    });
    Object.defineProperty(document, 'visibilityState', {
      configurable: true,
      get: () => 'hidden',
    });
    document.dispatchEvent(new Event('visibilitychange'));
  });
  await page.waitForTimeout(gapMs);
  await page.goto('about:blank', { waitUntil: 'domcontentloaded' }).catch(() => {});
  await page.waitForTimeout(1500);

  const vitals = ga.filter((n) => n === 'web_vitals').length;
  await ctx.close();
  return { gapMs, vitals, control };
}

const PLAN = [
  ['A1', noInteraction(3000)],
  ['A2', noInteraction(8000)],
  ['A3', noInteraction(13000)],
  ['B1', interactThenHide(0)],
  ['B2', interactThenHide(200)],
  ['B3', interactThenHide(600)],
  ['B4', interactThenHide(2000)],
  ['C', measureReadyLatency()],
];

const browser = await chromium.launch();
const rows = [];

for (const [id, body] of PLAN) {
  for (let r = 0; r < RUNS; r++) {
    const out = await trial(browser, body);
    rows.push({ id, run: r + 1, ...out });
  }
}

// Path B — the larger loss. Always run: without it this harness only measures
// the smaller __gaPending path and the headline number is unreproducible.
const survivalRows = [];
for (const gap of [0, 500, 2000, 5000, 10000]) {
  survivalRows.push(await survival(browser, gap));
}

await browser.close();

if (asJson) {
  console.log(JSON.stringify({ url, runs: RUNS, rows, survival: survivalRows }, null, 2));
} else {
  console.log(`\nGA __gaPending loss — ${url} (${RUNS} runs each)\n`);
  console.log(
    'id  scenario                      gtagReq gaReady vitalsSent stranded'
  );
  console.log('-'.repeat(78));
  for (const r of rows) {
    console.log(
      [
        r.id.padEnd(3),
        String(r.scenario).padEnd(29),
        String(r.gtagRequested).padEnd(7),
        String(r.gaReadyAtHide).padEnd(7),
        String(r.vitalsSent).padEnd(10),
        r.strandedAfterHide.join(',') || '-',
      ].join(' ')
    );
  }
  const lat = rows
    .filter((r) => r.id === 'C')
    .map((r) => r.readyLatencyMs)
    .filter((v) => v != null);
  if (lat.length) {
    lat.sort((a, b) => a - b);
    console.log(
      `\nwindow B width (interaction -> __gaReady): ` +
        `min=${lat[0]}ms median=${lat[Math.floor(lat.length / 2)]}ms max=${lat[lat.length - 1]}ms`
    );
  }
  console.log('\nPath B — gtag ready, but reader leaves N ms after the hide:');
  console.log('  leave-gap   web_vitals on wire   control beacon');
  for (const s of survivalRows) {
    console.log(
      `  ${String(s.gapMs).padStart(6)}ms   ${String(s.vitals).padStart(13)}/3   ` +
        `${String(s.control).padStart(12)}`
    );
  }
  console.log(
    '  (control captured while web_vitals is not => real loss, not a\n' +
      '   capture artifact. gtag batches behind a ~5s timer.)'
  );

  console.log(
    '\nNote: collect requests were aborted at the network layer — nothing ' +
      'reached the production property.\n'
  );
}
