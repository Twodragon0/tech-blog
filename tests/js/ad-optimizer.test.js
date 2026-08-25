// Regression tests for assets/js/ad-optimizer.js
//
// Goal: prove the ad-optimizer (a) wraps every adsbygoogle slot in a
// .ad-container, (b) reserves NO height, (c) does not double-wrap an
// already-wrapped slot, and (d) applies CSS containment hints to the ad
// element itself.
//
// (b) inverted on 2026-08-14. Reserving 90/250/600px and then collapsing it
// is itself the layout shift: the :has() rules in _includes/head.html delete
// .ad-container the moment AdSense reports data-ad-status="unfilled", and the
// measured fill rate on this site is 0/4 and 0/3. Driving that transition on a
// local build measured CLS 0.0575 with the reservation and 0.0039 without
// (scripts/dev/measure_ad_collapse_cls.mjs). These assertions now guard
// against the reservation coming back.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/ad-optimizer.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript() {
  // ad-optimizer.js defers optimizeAds() through requestIdleCallback /
  // setTimeout(2000) to keep layout-mutating work off the LCP critical path
  // (see comment in init()). Fake timers let us flush that deferred pass
  // synchronously inside each test without changing production behavior.
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
  vi.runOnlyPendingTimers();
}

describe('ad-optimizer.js', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    vi.useRealTimers();
    document.body.innerHTML = '';
  });

  it('wraps a bare adsbygoogle slot in .ad-container and reserves no height', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle" data-ad-format="rectangle"></ins>';
    runScript();

    const ad = document.querySelector('ins.adsbygoogle');
    const container = ad.parentElement;
    expect(container.classList.contains('ad-container')).toBe(true);
    expect(container.style.minHeight).toBe('');
  });

  it('reserves no height for horizontal/banner ad formats', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle" data-ad-format="horizontal"></ins>';
    runScript();
    expect(document.querySelector('.ad-container').style.minHeight).toBe('');
  });

  it('reserves no height for vertical/sidebar ad formats', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle" data-ad-slot="sidebar-1"></ins>';
    runScript();
    expect(document.querySelector('.ad-container').style.minHeight).toBe('');
  });

  it('does not double-wrap an ad that is already inside .ad-container', () => {
    document.body.innerHTML =
      '<div class="ad-container" style="min-height: 250px"><ins class="adsbygoogle"></ins></div>';
    runScript();
    expect(document.querySelectorAll('.ad-container')).toHaveLength(1);
  });

  it('applies CSS containment hints (display + contain + width) to the ad element', () => {
    document.body.innerHTML = '<ins class="adsbygoogle"></ins>';
    runScript();
    const ad = document.querySelector('ins.adsbygoogle');
    expect(ad.style.display).toBe('block');
    expect(ad.style.contain).toBe('layout style');
    expect(ad.style.width).toBe('100%');
    expect(ad.style.minHeight).toBe('');
  });

  // 표 안 광고 제거 (2026-08-25). Auto ads(slotname=auto)는 본문 어디에나
  // 슬롯을 꽂아서 <table> 내부에 들어가는 일이 있고, 디제스트 포스트는 표가
  // 많다. 그러면 열 폭이 틀어지고 본문 표가 광고로 쪼개진다.
  it('removes an ad injected inside a table instead of wrapping it', () => {
    document.body.innerHTML =
      '<table><tbody><tr><td>' +
      '<ins class="adsbygoogle"></ins>' +
      '</td></tr></tbody></table>';
    runScript();

    expect(document.querySelector('ins.adsbygoogle')).toBeNull();
    expect(document.querySelectorAll('.ad-container')).toHaveLength(0);
    // 표 자체는 그대로 남아야 한다 — 광고만 걷어낸다.
    expect(document.querySelector('table')).not.toBeNull();
    expect(document.querySelector('td')).not.toBeNull();
  });

  it('removes a google-auto-placed slot nested deep inside a table', () => {
    document.body.innerHTML =
      '<table><tbody><tr><td><div class="wrap">' +
      '<div class="google-auto-placed"><ins class="adsbygoogle"></ins></div>' +
      '</div></td></tr></tbody></table>';
    runScript();

    expect(document.querySelector('.google-auto-placed')).toBeNull();
    expect(document.querySelectorAll('.ad-container')).toHaveLength(0);
    expect(document.querySelector('table')).not.toBeNull();
  });

  it('leaves ads OUTSIDE a table untouched even when a table is present', () => {
    document.body.innerHTML =
      '<table><tbody><tr><td>cell</td></tr></tbody></table>' +
      '<ins class="adsbygoogle"></ins>';
    runScript();

    const ad = document.querySelector('ins.adsbygoogle');
    expect(ad).not.toBeNull();
    expect(ad.parentElement.classList.contains('ad-container')).toBe(true);
    expect(document.querySelector('table')).not.toBeNull();
  });

  it('handles multiple ad slots on the same page', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle" data-ad-format="rectangle"></ins>' +
      '<ins class="adsbygoogle" data-ad-format="horizontal"></ins>' +
      '<ins class="adsbygoogle"></ins>';
    runScript();
    const containers = document.querySelectorAll('.ad-container');
    expect(containers).toHaveLength(3);
    const heights = Array.from(containers).map((c) => c.style.minHeight);
    expect(heights).toEqual(['', '', '']);
  });
});
