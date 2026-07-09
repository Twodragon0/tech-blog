// Regression tests for assets/js/adsense-init.js
//
// Goal: prove adsense-init (a) exposes window.__adsenseSlotInitializer and is
// double-init guarded, (b) only pushes new/un-marked .adsbygoogle slots and
// marks them data-ads-initialized, (c) treats a missing/incomplete
// window.adsbygoogle as "not ready" and no-ops safely, (d) tolerates
// individual adsbygoogle.push() failures without breaking the remaining
// slots, (e) reacts to the 'adsense:ready' event and the deferred 300ms
// initialization on 'load', and (f) the fallback guard hides ad slots (CLS
// cleanup) only when AdSense never becomes ready within AD_LOAD_TIMEOUT.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/adsense-init.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

describe('adsense-init.js', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = '';
    delete window.__adsenseSlotInitializer;
    delete window.adsbygoogle;
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
    document.body.innerHTML = '';
    delete window.__adsenseSlotInitializer;
    delete window.adsbygoogle;
  });

  it('exposes window.__adsenseSlotInitializer as a callable function', () => {
    runScript();
    expect(typeof window.__adsenseSlotInitializer).toBe('function');
  });

  it('double-init guard: does not re-register listeners when already initialized', () => {
    const sentinel = () => {};
    window.__adsenseSlotInitializer = sentinel;
    const addSpy = vi.spyOn(window, 'addEventListener');

    runScript();

    // Early return means the identity is untouched and no new listeners added.
    expect(window.__adsenseSlotInitializer).toBe(sentinel);
    expect(addSpy).not.toHaveBeenCalled();
    addSpy.mockRestore();
  });

  it('on first init, registers "adsense:ready" and "load" listeners on window', () => {
    const addSpy = vi.spyOn(window, 'addEventListener');

    runScript();

    expect(addSpy).toHaveBeenCalledWith('adsense:ready', expect.any(Function));
    expect(addSpy).toHaveBeenCalledWith('load', expect.any(Function), { once: true });
    addSpy.mockRestore();
  });

  it('does nothing when window.adsbygoogle is undefined (no push, no attribute)', () => {
    document.body.innerHTML = '<ins class="adsbygoogle"></ins>';
    runScript();

    window.__adsenseSlotInitializer();

    expect(document.querySelector('ins.adsbygoogle').hasAttribute('data-ads-initialized')).toBe(
      false
    );
  });

  it('does nothing when adsbygoogle exists but has no push function', () => {
    document.body.innerHTML = '<ins class="adsbygoogle"></ins>';
    window.adsbygoogle = {};
    runScript();

    window.__adsenseSlotInitializer();

    expect(document.querySelector('ins.adsbygoogle').hasAttribute('data-ads-initialized')).toBe(
      false
    );
  });

  it('pushes for each un-initialized slot and marks it data-ads-initialized="1"', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle"></ins><ins class="adsbygoogle"></ins>';
    const push = vi.fn();
    window.adsbygoogle = { push };
    runScript();

    window.__adsenseSlotInitializer();

    expect(push).toHaveBeenCalledTimes(2);
    document.querySelectorAll('ins.adsbygoogle').forEach((slot) => {
      expect(slot.getAttribute('data-ads-initialized')).toBe('1');
    });
  });

  it('skips slots that already have data-ads-initialized set', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle" data-ads-initialized="1"></ins>' +
      '<ins class="adsbygoogle"></ins>';
    const push = vi.fn();
    window.adsbygoogle = { push };
    runScript();

    window.__adsenseSlotInitializer();

    expect(push).toHaveBeenCalledTimes(1);
  });

  it('catches a push() error on one slot and still initializes the remaining slots', () => {
    document.body.innerHTML =
      '<ins class="adsbygoogle"></ins><ins class="adsbygoogle"></ins>';
    const push = vi
      .fn()
      .mockImplementationOnce(() => {
        throw new Error('adsbygoogle push failed');
      })
      .mockImplementationOnce(() => {});
    window.adsbygoogle = { push };
    runScript();

    expect(() => window.__adsenseSlotInitializer()).not.toThrow();

    const slots = document.querySelectorAll('ins.adsbygoogle');
    // First slot's push threw, so setAttribute for it never ran.
    expect(slots[0].hasAttribute('data-ads-initialized')).toBe(false);
    // Second slot's push succeeded and was marked.
    expect(slots[1].getAttribute('data-ads-initialized')).toBe('1');
  });

  it('dispatching "adsense:ready" triggers initializeAdsenseSlots', () => {
    document.body.innerHTML = '<ins class="adsbygoogle"></ins>';
    const push = vi.fn();
    window.adsbygoogle = { push };
    runScript();

    window.dispatchEvent(new Event('adsense:ready'));

    expect(push).toHaveBeenCalledTimes(1);
    expect(document.querySelector('ins.adsbygoogle').getAttribute('data-ads-initialized')).toBe(
      '1'
    );
  });

  it('on window load, calls initializeAdsenseSlots after a 300ms delay', () => {
    document.body.innerHTML = '<ins class="adsbygoogle"></ins>';
    const push = vi.fn();
    window.adsbygoogle = { push };
    runScript();

    window.dispatchEvent(new Event('load'));
    expect(push).not.toHaveBeenCalled();

    vi.advanceTimersByTime(300);

    expect(push).toHaveBeenCalledTimes(1);
  });

  it('fallback guard hides ad slots if adsbygoogle never becomes ready within the timeout', () => {
    document.body.innerHTML = '<ins class="adsbygoogle"></ins>';
    // window.adsbygoogle intentionally left undefined (never becomes ready).
    runScript();

    window.dispatchEvent(new Event('load'));
    vi.advanceTimersByTime(5000); // AD_LOAD_TIMEOUT

    const slot = document.querySelector('ins.adsbygoogle');
    expect(slot.style.display).toBe('none');
    expect(slot.style.minHeight).toBe('0px');
    expect(slot.getAttribute('data-ad-load-failed')).toBe('true');
  });

  it('fallback guard does not hide ad slots if adsbygoogle becomes ready before the timeout', () => {
    document.body.innerHTML = '<ins class="adsbygoogle"></ins>';
    runScript();

    window.dispatchEvent(new Event('load'));
    // First check-interval tick (200ms): still not ready.
    vi.advanceTimersByTime(200);

    // AdSense becomes ready before the 5000ms fallback fires.
    window.adsbygoogle = { push: vi.fn() };

    // Second check-interval tick (400ms total): detects ready, clears both timers.
    vi.advanceTimersByTime(200);
    // Advance well past the original 5000ms fallback mark to prove it never fires.
    vi.advanceTimersByTime(4700);

    const slot = document.querySelector('ins.adsbygoogle');
    expect(slot.style.display).not.toBe('none');
    expect(slot.hasAttribute('data-ad-load-failed')).toBe(false);
  });
});
