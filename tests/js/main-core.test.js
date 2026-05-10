// Regression tests for assets/js/main-core.js
//
// main-core.js loads on every page from `_includes/footer.html`. It owns
// (a) `window.TechBlog.{scheduleIdleWork,yieldToMain,runInChunks}` shared
// utilities, (b) the mobile menu toggle + outside-click close,
// (c) smooth scroll for `a[href^="#"]` anchors, and (d) the
// `window.shareKakao` / `window.copyToClipboard` global helpers.
//
// Most behavior is wrapped in `scheduleIdleWork(...)` which delegates to
// `requestIdleCallback` (absent in jsdom 29) → falls through to
// `setTimeout(callback, 1)`. We use `vi.useFakeTimers()` +
// `vi.runOnlyPendingTimers()` to flush these synchronously inside each
// test (same pattern as ad-optimizer.test.js fix in PR #337 / f0638ae6).

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/main-core.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

// Track listeners attached to `document` so we can remove them after each
// test — they outlive document.body.innerHTML resets and would otherwise
// double-fire on later tests.
function runScript(handlerSink) {
  // Track addEventListener calls during BOTH module-eval AND the
  // scheduleIdleWork() callbacks that fire under vi.runOnlyPendingTimers().
  // The image-error capture listener is registered inside an idle callback,
  // so restoring the proxy too early would let it leak across tests.
  const origAdd = document.addEventListener.bind(document);
  document.addEventListener = (evt, handler, opts) => {
    handlerSink.push({ evt, handler, opts });
    return origAdd(evt, handler, opts);
  };
  try {
    // eslint-disable-next-line no-new-func
    new Function('window', 'document', SCRIPT_SOURCE)(window, document);
    vi.runOnlyPendingTimers();
  } finally {
    document.addEventListener = origAdd;
  }
}

describe('main-core.js', () => {
  let documentHandlers;

  let originalMatchMedia;
  let originalIO;

  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = '';
    delete window.TechBlog;
    delete window.shareKakao;
    delete window.copyToClipboard;
    delete window.Kakao;
    documentHandlers = [];
    // jsdom 29 doesn't implement window.matchMedia. main-core.js calls it
    // at module init for prefers-color-scheme detection.
    originalMatchMedia = window.matchMedia;
    window.matchMedia = vi.fn(() => ({
      matches: false,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
    }));
    // jsdom 29 also doesn't implement IntersectionObserver. The script
    // uses it inside two scheduleIdleWork() blocks (scroll animations +
    // lazy images). Provide a no-op constructor so module-eval doesn't
    // ReferenceError; behavior under test does not depend on its callbacks.
    originalIO = window.IntersectionObserver;
    window.IntersectionObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
  });

  afterEach(() => {
    for (const r of documentHandlers) {
      document.removeEventListener(r.evt, r.handler, r.opts);
    }
    vi.useRealTimers();
    document.body.innerHTML = '';
    delete window.TechBlog;
    delete window.shareKakao;
    delete window.copyToClipboard;
    delete window.Kakao;
    window.matchMedia = originalMatchMedia;
    window.IntersectionObserver = originalIO;
  });

  // =========================================================================
  // window.TechBlog utility surface
  // =========================================================================

  it('exposes TechBlog.{scheduleIdleWork,yieldToMain,runInChunks} globals', () => {
    runScript(documentHandlers);
    expect(window.TechBlog).toBeDefined();
    expect(typeof window.TechBlog.scheduleIdleWork).toBe('function');
    expect(typeof window.TechBlog.yieldToMain).toBe('function');
    expect(typeof window.TechBlog.runInChunks).toBe('function');
  });

  it('exposes window.shareKakao and window.copyToClipboard global helpers', () => {
    runScript(documentHandlers);
    expect(typeof window.shareKakao).toBe('function');
    expect(typeof window.copyToClipboard).toBe('function');
  });

  // =========================================================================
  // Mobile menu toggle
  // =========================================================================

  it('mobile menu toggle: click on #mobile-menu-btn flips .active + aria-expanded', () => {
    document.body.innerHTML =
      '<button id="mobile-menu-btn" aria-expanded="false">menu</button>' +
      '<nav id="mobile-nav"></nav>';
    runScript(documentHandlers);

    const btn = document.getElementById('mobile-menu-btn');
    const nav = document.getElementById('mobile-nav');

    btn.click();
    expect(nav.classList.contains('active')).toBe(true);
    expect(btn.getAttribute('aria-expanded')).toBe('true');

    btn.click();
    expect(nav.classList.contains('active')).toBe(false);
    expect(btn.getAttribute('aria-expanded')).toBe('false');
  });

  it('mobile menu: clicking outside the nav + button closes the menu', () => {
    document.body.innerHTML =
      '<button id="mobile-menu-btn" aria-expanded="false">menu</button>' +
      '<nav id="mobile-nav"></nav>' +
      '<main id="elsewhere"></main>';
    runScript(documentHandlers);

    const btn = document.getElementById('mobile-menu-btn');
    const nav = document.getElementById('mobile-nav');
    const elsewhere = document.getElementById('elsewhere');

    // Open via toggle.
    btn.click();
    expect(nav.classList.contains('active')).toBe(true);

    // Click outside both nodes — should close.
    elsewhere.click();
    expect(nav.classList.contains('active')).toBe(false);
    expect(btn.getAttribute('aria-expanded')).toBe('false');
  });

  // =========================================================================
  // Smooth scroll for a[href^="#"]
  // =========================================================================

  it('smooth-scroll: a[href="#section"] click → scrollTo({behavior:smooth}) + history.pushState', () => {
    document.body.innerHTML =
      '<a id="link" href="#target">jump</a>' +
      '<section id="target">target</section>';
    runScript(documentHandlers);

    const scrollToSpy = vi.fn();
    const origScrollTo = window.scrollTo;
    window.scrollTo = scrollToSpy;
    const pushSpy = vi.spyOn(history, 'pushState');

    try {
      const link = document.getElementById('link');
      const ev = new MouseEvent('click', { bubbles: true, cancelable: true });
      link.dispatchEvent(ev);

      expect(ev.defaultPrevented).toBe(true);
      expect(scrollToSpy).toHaveBeenCalledTimes(1);
      expect(scrollToSpy.mock.calls[0][0].behavior).toBe('smooth');
      expect(pushSpy).toHaveBeenCalledTimes(1);
      expect(pushSpy.mock.calls[0][2]).toBe('#target');
    } finally {
      window.scrollTo = origScrollTo;
      pushSpy.mockRestore();
    }
  });

  it('smooth-scroll: clicking #-anchor while menu is open also closes the menu', () => {
    document.body.innerHTML =
      '<button id="mobile-menu-btn" aria-expanded="true">menu</button>' +
      '<nav id="mobile-nav" class="active"></nav>' +
      '<a id="link" href="#target">jump</a>' +
      '<section id="target">target</section>';
    runScript(documentHandlers);

    const origScrollTo = window.scrollTo;
    window.scrollTo = vi.fn();

    try {
      document.getElementById('link').dispatchEvent(
        new MouseEvent('click', { bubbles: true, cancelable: true }),
      );
      const nav = document.getElementById('mobile-nav');
      const btn = document.getElementById('mobile-menu-btn');
      expect(nav.classList.contains('active')).toBe(false);
      expect(btn.getAttribute('aria-expanded')).toBe('false');
    } finally {
      window.scrollTo = origScrollTo;
    }
  });

  // =========================================================================
  // shareKakao() — Web Share API fallback path
  // =========================================================================

  it('shareKakao: falls back to navigator.share when Kakao SDK is uninitialized', () => {
    runScript(documentHandlers);

    const shareSpy = vi.fn(() => Promise.resolve());
    const origShare = navigator.share;
    Object.defineProperty(navigator, 'share', {
      configurable: true,
      writable: true,
      value: shareSpy,
    });

    try {
      window.shareKakao('https://example.com/x', 'Title', 'Description');
      expect(shareSpy).toHaveBeenCalledTimes(1);
      expect(shareSpy.mock.calls[0][0]).toEqual({
        title: 'Title',
        text: 'Description',
        url: 'https://example.com/x',
      });
    } finally {
      if (origShare === undefined) {
        delete navigator.share;
      } else {
        Object.defineProperty(navigator, 'share', {
          configurable: true,
          writable: true,
          value: origShare,
        });
      }
    }
  });

  // =========================================================================
  // copyToClipboard() — clipboard.writeText + toast injection
  // =========================================================================

  it('copyToClipboard: writes to navigator.clipboard then injects + auto-removes a toast', async () => {
    runScript(documentHandlers);

    const writeSpy = vi.fn(() => Promise.resolve());
    const origClipboard = navigator.clipboard;
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      writable: true,
      value: { writeText: writeSpy },
    });

    try {
      // window.copyToClipboard is async (uses await navigator.clipboard.writeText).
      // We need to flush microtasks AND the toast lifecycle timers.
      const promise = window.copyToClipboard('https://example.com/y');
      await promise;
      expect(writeSpy).toHaveBeenCalledWith('https://example.com/y');
      // Toast was appended to body.
      const toasts = Array.from(document.body.children).filter(
        (n) => n.textContent && n.textContent.includes('복사되었습니다'),
      );
      expect(toasts).toHaveLength(1);
    } finally {
      if (origClipboard === undefined) {
        delete navigator.clipboard;
      } else {
        Object.defineProperty(navigator, 'clipboard', {
          configurable: true,
          writable: true,
          value: origClipboard,
        });
      }
    }
  });

  // =========================================================================
  // Image fallback chain (CSP-compliant, no inline onerror)
  // =========================================================================

  it('image fallback chain: data-svg-src → data-fallback when img errors', () => {
    // Run the script first so its delegated `error` listener is in place,
    // THEN inject the image. Inserting before runScript triggers the
    // separate "image already failed before JS loaded" sync handler
    // (lines 424-437 of main-core.js), which would mutate the image
    // synchronously and confuse the assertions below.
    runScript(documentHandlers);

    document.body.innerHTML =
      '<img id="hero" src="https://example.com/orig.png" ' +
      'data-svg-src="https://example.com/orig.svg" ' +
      'data-fallback="https://example.com/orig.fallback.png">';
    const img = document.getElementById('hero');

    // First error → swap to data-svg-src.
    img.dispatchEvent(new Event('error'));
    expect(img.getAttribute('src')).toBe('https://example.com/orig.svg');
    expect(img.hasAttribute('data-svg-src')).toBe(false);

    // Second error → swap to data-fallback.
    img.dispatchEvent(new Event('error'));
    expect(img.getAttribute('src')).toBe('https://example.com/orig.fallback.png');
    expect(img.hasAttribute('data-fallback')).toBe(false);
  });
});
