// Regression tests for assets/js/ad-optimizer.js
//
// Goal: prove the ad-optimizer (a) wraps every adsbygoogle slot in a
// .ad-container, (b) sets a CLS-preventing minHeight that matches the
// requested ad format, (c) does not double-wrap an already-wrapped slot,
// and (d) applies CSS containment hints to the ad element itself.

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/ad-optimizer.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

describe('ad-optimizer.js', () => {
  beforeEach(() => {
    // Default-ready DOM so optimizeAds() runs synchronously.
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('wraps a bare adsbygoogle slot in .ad-container with a default minHeight', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle" data-ad-format="rectangle"></ins>';
    runScript();

    const ad = document.querySelector('ins.adsbygoogle');
    const container = ad.parentElement;
    expect(container.classList.contains('ad-container')).toBe(true);
    expect(container.style.minHeight).toBe('250px');
  });

  it('sets minHeight=90px for horizontal/banner ad formats', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle" data-ad-format="horizontal"></ins>';
    runScript();
    expect(document.querySelector('.ad-container').style.minHeight).toBe('90px');
  });

  it('sets minHeight=600px for vertical/sidebar ad formats', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle" data-ad-slot="sidebar-1"></ins>';
    runScript();
    expect(document.querySelector('.ad-container').style.minHeight).toBe('600px');
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
    expect(ad.style.minHeight).toBe('250px');
  });

  it('handles multiple ad slots on the same page', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle" data-ad-format="rectangle"></ins>' +
      '<ins class="adsbygoogle" data-ad-format="horizontal"></ins>' +
      '<ins class="adsbygoogle"></ins>';
    runScript();
    const containers = document.querySelectorAll('.ad-container');
    expect(containers).toHaveLength(3);
    const heights = Array.from(containers).map((c) => c.style.minHeight).sort();
    expect(heights).toEqual(['250px', '250px', '90px'].sort());
  });
});
