#!/usr/bin/env node
/**
 * CLS measurement harness with per-element attribution.
 *
 * CLS is noisy: ad fill, font swap and iframe embeds vary run to run, so a
 * single number proves nothing. This runs the page N times and reports the
 * median plus the shift sources ranked by total contribution, which is what
 * actually tells you where to reserve space.
 *
 * It measures the same way Chrome's field metric does — sums layout-shift
 * entries that are NOT within 500ms of a user input — and keeps per-source
 * attribution from `entry.sources[].node`.
 *
 * Usage:
 *   node scripts/dev/measure_cls.mjs <url> [runs] [--json]
 *
 * Requires Playwright (already a devDependency for the CSP/mermaid guards).
 */

import { chromium } from 'playwright';

const url = process.argv[2];
const runs = Number(process.argv[3] || 5);
const asJson = process.argv.includes('--json');

if (!url) {
  console.error('usage: node scripts/dev/measure_cls.mjs <url> [runs] [--json]');
  process.exit(2);
}

const COLLECTOR = () => {
  window.__shifts = [];
  const describe = (node) => {
    if (!node || node.nodeType !== 1) return '(detached)';
    const el = /** @type {Element} */ (node);
    const id = el.id ? `#${el.id}` : '';
    const cls = typeof el.className === 'string' && el.className
      ? '.' + el.className.trim().split(/\s+/).slice(0, 3).join('.')
      : '';
    return `${el.tagName.toLowerCase()}${id}${cls}`;
  };
  new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (entry.hadRecentInput) continue;
      window.__shifts.push({
        value: entry.value,
        time: entry.startTime,
        sources: (entry.sources || []).map((s) => ({
          node: describe(s.node),
          from: s.previousRect ? `${Math.round(s.previousRect.width)}x${Math.round(s.previousRect.height)}@${Math.round(s.previousRect.y)}` : '',
          to: s.currentRect ? `${Math.round(s.currentRect.width)}x${Math.round(s.currentRect.height)}@${Math.round(s.currentRect.y)}` : '',
        })),
      });
    }
  }).observe({ type: 'layout-shift', buffered: true });
};

const browser = await chromium.launch();
const results = [];

for (let i = 0; i < runs; i += 1) {
  const context = await browser.newContext({ viewport: { width: 1512, height: 827 } });
  const page = await context.newPage();
  await page.addInitScript(COLLECTOR);
  await page.goto(url, { waitUntil: 'load', timeout: 60000 });
  // Scroll the whole page: shifts below the fold (ads, comments, footer)
  // only occur once those regions are reached and their embeds load.
  await page.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 600) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 90));
    }
    window.scrollTo(0, document.body.scrollHeight);
  });
  await page.waitForTimeout(9000);
  const shifts = await page.evaluate(() => window.__shifts || []);
  const total = shifts.reduce((a, s) => a + s.value, 0);
  results.push({ total, shifts });
  await context.close();
  if (!asJson) console.error(`  run ${i + 1}/${runs}: CLS=${total.toFixed(4)}`);
}

await browser.close();

const totals = results.map((r) => r.total).sort((a, b) => a - b);
const median = totals[Math.floor(totals.length / 2)];

// Rank sources by summed contribution across all runs.
const bySource = new Map();
for (const r of results) {
  for (const s of r.shifts) {
    const names = s.sources.length ? s.sources.map((x) => x.node) : ['(no attribution)'];
    for (const n of names) {
      const cur = bySource.get(n) || { total: 0, count: 0, sample: '' };
      cur.total += s.value / names.length;
      cur.count += 1;
      if (!cur.sample && s.sources.length) {
        const src = s.sources.find((x) => x.node === n);
        if (src) cur.sample = `${src.from} -> ${src.to}`;
      }
      bySource.set(n, cur);
    }
  }
}
const ranked = [...bySource.entries()]
  .map(([node, v]) => ({ node, perRun: v.total / runs, hits: v.count, sample: v.sample }))
  .sort((a, b) => b.perRun - a.perRun);

if (asJson) {
  console.log(JSON.stringify({ url, runs, median, totals, ranked }, null, 2));
} else {
  console.log('='.repeat(74));
  console.log(`URL: ${url}`);
  console.log(`runs=${runs}  CLS 중앙값=${median.toFixed(4)}  전체=[${totals.map((t) => t.toFixed(3)).join(', ')}]`);
  console.log(`목표: < 0.10  →  ${median < 0.1 ? 'PASS' : 'FAIL'}`);
  console.log('-'.repeat(74));
  console.log('기여도 상위 (run당 평균 CLS):');
  for (const r of ranked.slice(0, 12)) {
    console.log(`  ${r.perRun.toFixed(4)}  ${r.node.padEnd(44)} ${r.sample}`);
  }
}
