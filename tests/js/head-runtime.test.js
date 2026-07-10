// Regression tests for assets/js/head-runtime.js
//
// head-runtime.js is loaded on every page from `_includes/header.html`.
// It reads config attributes from a `<script id="head-runtime-script">`
// tag (defer-friendly: `document.currentScript` is null in defer mode)
// and lazy-loads Sentry/GA/AdSense/Kakao SDKs on first user interaction
// with a 10-12s idle safety-net.
//
// We don't assert against actual <script> tag injection (would require
// stubbing document.head.appendChild). Instead we verify:
//   - top-level idempotency guard (`__headRuntimeInitialized`)
//   - `applyTheme()` localStorage + system preference + skip-if-set
//   - `markBodyLoaded()` adds `body.loaded` class
//   - lazy loaders skip when their config attr is missing
//   - lazy loaders register the 5 interaction listeners
//     (pointermove/scroll/keydown/touchstart/click)

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/head-runtime.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

const INTERACTION_EVENTS = [
  'pointermove',
  'scroll',
  'keydown',
  'touchstart',
  'click',
];

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

// jsdom lacks IntersectionObserver. This local stub tracks constructed
// instances on `window.__ioInstances` so tests can manually `_trigger()`
// the observe callback without a real scroll/layout.
function stubIntersectionObserver() {
  window.__ioInstances = [];
  class StubIntersectionObserver {
    constructor(cb) {
      this._cb = cb;
      window.__ioInstances.push(this);
    }
    observe(_target) {}
    disconnect() {}
    _trigger(target, isIntersecting = true) {
      this._cb([{ isIntersecting, target }], this);
    }
  }
  window.IntersectionObserver = StubIntersectionObserver;
}

function restoreIO() {
  delete window.IntersectionObserver;
  delete window.__ioInstances;
}

function setupConfigScript({
  gaId = '',
  adsenseClient = '',
  kakaoAppKey = '',
  sentryDsn = '',
  sentryProductionHost = '',
  sentryAllowedHosts = '',
} = {}) {
  document.body.innerHTML =
    `<script id="head-runtime-script" ` +
    `data-ga-id="${gaId}" ` +
    `data-adsense-client="${adsenseClient}" ` +
    `data-kakao-app-key="${kakaoAppKey}" ` +
    `data-sentry-dsn="${sentryDsn}" ` +
    `data-sentry-production-host="${sentryProductionHost}" ` +
    `data-sentry-allowed-hosts="${sentryAllowedHosts}"></script>`;
}

describe('head-runtime.js', () => {
  let addEventListenerSpy;
  let originalMatchMedia;

  beforeEach(() => {
    // Reset idempotency guard + load-init flags between tests so each
    // runScript() call exercises a fresh init path.
    delete window.__headRuntimeInitialized;
    delete window.__gaLoadInitiated;
    delete window.__adsenseLoadInitiated;
    delete window.__kakaoLoadInitiated;
    delete window.__sentryLoadInitiated;
    delete window.__fontTier2Loaded;
    document.documentElement.removeAttribute('data-theme');
    document.body.classList.remove('loaded');
    document.body.innerHTML = '';
    localStorage.clear();
    // jsdom 29 does not implement window.matchMedia. The script's
    // applyTheme() throws if matchMedia is undefined and falls back to
    // 'light' via its catch block, masking the localStorage path. Provide
    // a sane default that returns matches=false unless a test overrides it.
    originalMatchMedia = window.matchMedia;
    window.matchMedia = vi.fn(() => ({ matches: false }));
    addEventListenerSpy = vi.spyOn(window, 'addEventListener');
  });

  afterEach(() => {
    // Interaction/load listeners registered by lazy loaders during this test
    // are never self-removed unless their loadOnce() actually fired. Without
    // this cleanup, stale closures (bound to this test's config) leak onto
    // `window` and misfire in later tests once beforeEach resets the guard
    // flags (e.g. __sentryLoadInitiated), corrupting document.head with
    // duplicate scripts built from stale config.
    addEventListenerSpy.mock.calls.forEach(([type, handler, options]) => {
      try {
        window.removeEventListener(type, handler, options);
      } catch (_e) { /* ignore */ }
    });
    addEventListenerSpy.mockRestore();
    window.matchMedia = originalMatchMedia;
    document.documentElement.removeAttribute('data-theme');
    document.body.classList.remove('loaded');
    document.body.innerHTML = '';
    // Lazy loaders append <script>/<style> elements to document.head; clear
    // them so later tests' querySelector() calls don't match stale nodes.
    document.head.innerHTML = '';
    localStorage.clear();
    delete window.IntersectionObserver;
    delete window.__ioInstances;
    delete window.Kakao;
    delete window.dataLayer;
  });

  // =========================================================================
  // Top-level idempotency
  // =========================================================================

  it('top-level guard: second runScript() is a no-op', () => {
    setupConfigScript();
    runScript();
    expect(window.__headRuntimeInitialized).toBe(true);
    const callsAfterFirst = addEventListenerSpy.mock.calls.length;

    // Second invocation should bail immediately on the __headRuntimeInitialized check.
    runScript();
    expect(addEventListenerSpy.mock.calls.length).toBe(callsAfterFirst);
  });

  // =========================================================================
  // applyTheme()
  // =========================================================================

  it('applyTheme: reads localStorage theme and sets data-theme', () => {
    setupConfigScript();
    localStorage.setItem('theme', 'dark');
    runScript();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('applyTheme: falls back to system preference when localStorage is empty', () => {
    setupConfigScript();
    // Override the beforeEach stub to simulate prefers-color-scheme: dark.
    window.matchMedia = vi.fn(() => ({
      matches: true,
      media: '(prefers-color-scheme: dark)',
    }));
    runScript();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('applyTheme: skips when data-theme already set (inline init won the race)', () => {
    setupConfigScript();
    document.documentElement.setAttribute('data-theme', 'preset-by-inline');
    localStorage.setItem('theme', 'dark');
    runScript();
    // Pre-existing value preserved — applyTheme bailed.
    expect(document.documentElement.getAttribute('data-theme')).toBe('preset-by-inline');
  });

  // =========================================================================
  // markBodyLoaded() — synchronous when document.body already exists
  // =========================================================================

  it('markBodyLoaded: adds body.loaded synchronously when body is present', () => {
    setupConfigScript();
    runScript();
    expect(document.body.classList.contains('loaded')).toBe(true);
  });

  // =========================================================================
  // Lazy loader skip-when-config-missing contract
  // =========================================================================

  it('loadGoogleAnalytics: skips registering interaction listeners when data-ga-id is empty', () => {
    setupConfigScript({ gaId: '' });
    runScript();

    // Filter just the interaction-event listener calls.
    const interactionCalls = addEventListenerSpy.mock.calls.filter((c) =>
      INTERACTION_EVENTS.includes(c[0]),
    );
    // Without GA, Sentry, Kakao all unconfigured, no interaction listeners.
    expect(interactionCalls).toHaveLength(0);
  });

  it('loadGoogleAnalytics: registers all 5 interaction events when data-ga-id is set', () => {
    setupConfigScript({ gaId: 'G-TEST123' });
    runScript();

    const eventTypes = addEventListenerSpy.mock.calls
      .map((c) => c[0])
      .filter((e) => INTERACTION_EVENTS.includes(e));
    // Each of the 5 events should be registered exactly once for the GA loader.
    INTERACTION_EVENTS.forEach((ev) => {
      expect(eventTypes).toContain(ev);
    });
  });

  it('loadSentry: skips when data-sentry-dsn is empty', () => {
    // Set ONLY GA so we can isolate Sentry's contribution to listener count.
    setupConfigScript({ gaId: 'G-TEST123', sentryDsn: '' });
    runScript();
    const gaOnlyCount = addEventListenerSpy.mock.calls.filter((c) =>
      INTERACTION_EVENTS.includes(c[0]),
    ).length;

    // Now also enable Sentry — listener count should rise (5 more for Sentry).
    delete window.__headRuntimeInitialized;
    delete window.__gaLoadInitiated;
    delete window.__sentryLoadInitiated;
    addEventListenerSpy.mockClear();
    setupConfigScript({ gaId: 'G-TEST123', sentryDsn: 'https://abc@sentry.io/1' });
    runScript();
    const gaPlusSentryCount = addEventListenerSpy.mock.calls.filter((c) =>
      INTERACTION_EVENTS.includes(c[0]),
    ).length;

    // Each lazy loader registers its own 5 interaction listeners (separate
    // closures), so adding Sentry adds exactly 5.
    expect(gaPlusSentryCount).toBe(gaOnlyCount + INTERACTION_EVENTS.length);
  });

  // =========================================================================
  // Init-flag guards on lazy loaders
  // =========================================================================

  it('loadGoogleAnalytics: pre-existing __gaLoadInitiated suppresses listener registration', () => {
    setupConfigScript({ gaId: 'G-TEST123' });
    window.__gaLoadInitiated = true; // simulate earlier load
    runScript();
    const interactionCalls = addEventListenerSpy.mock.calls.filter((c) =>
      INTERACTION_EVENTS.includes(c[0]),
    );
    // GA bails early on __gaLoadInitiated check, so no listeners.
    expect(interactionCalls).toHaveLength(0);
  });

  // =========================================================================
  // applyTheme() — catch branch + 'system' saved-value branch
  // =========================================================================

  it('applyTheme: localStorage.getItem throwing falls back to light via catch', () => {
    setupConfigScript();
    const getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('storage disabled');
    });
    runScript();
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    getItemSpy.mockRestore();
  });

  it("applyTheme: saved === 'system' falls back to system preference (light)", () => {
    setupConfigScript();
    localStorage.setItem('theme', 'system');
    runScript();
    // beforeEach stub returns matches: false -> light
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });

  // =========================================================================
  // bindCssFallback()
  // =========================================================================

  it('bindCssFallback: no-op when #main-stylesheet link is absent', () => {
    setupConfigScript();
    runScript();
    // No error thrown, and no fallback <style> injected since onerror never wired.
    expect(document.head.querySelector('style')).toBeNull();
  });

  it('bindCssFallback: injects fallback style and removes link on link error', () => {
    document.body.innerHTML =
      '<script id="head-runtime-script"></script>' +
      '<link id="main-stylesheet" rel="stylesheet" href="/broken.css">';
    runScript();
    const link = document.getElementById('main-stylesheet');
    expect(link.onerror).toBeTypeOf('function');
    link.onerror();
    expect(document.head.querySelector('style')).toBeTruthy();
    expect(document.getElementById('main-stylesheet')).toBeNull();
  });

  // =========================================================================
  // registerServiceWorker()
  // =========================================================================

  it('registerServiceWorker: no-op when serviceWorker is not in navigator', () => {
    const originalDescriptor = Object.getOwnPropertyDescriptor(window.navigator, 'serviceWorker');
    expect('serviceWorker' in navigator).toBe(false);
    setupConfigScript();
    runScript();
    const loadCalls = addEventListenerSpy.mock.calls.filter((c) => c[0] === 'load');
    expect(loadCalls).toHaveLength(0);
    if (originalDescriptor) {
      Object.defineProperty(window.navigator, 'serviceWorker', originalDescriptor);
    }
  });

  it('registerServiceWorker: registers on load event and posts SKIP_WAITING when controller present', async () => {
    const postMessage = vi.fn();
    const registration = { addEventListener: vi.fn(), installing: null };
    const register = vi.fn(() => Promise.resolve(registration));
    Object.defineProperty(window.navigator, 'serviceWorker', {
      value: { register, controller: { postMessage } },
      configurable: true,
    });
    setupConfigScript();
    runScript();
    const loadCall = addEventListenerSpy.mock.calls.find((c) => c[0] === 'load');
    expect(loadCall).toBeTruthy();
    loadCall[1](); // invoke register()
    expect(register).toHaveBeenCalledWith('/sw.js');
    expect(postMessage).toHaveBeenCalledWith({ type: 'SKIP_WAITING' });
    await Promise.resolve();
    await Promise.resolve();
    expect(registration.addEventListener).toHaveBeenCalledWith('updatefound', expect.any(Function));
    delete window.navigator.serviceWorker;
  });

  it('registerServiceWorker: updatefound with activated newWorker + controller logs debug on localhost', async () => {
    const newWorker = { addEventListener: vi.fn(), state: 'activated' };
    const registration = { addEventListener: vi.fn(), installing: newWorker };
    const register = vi.fn(() => Promise.resolve(registration));
    Object.defineProperty(window.navigator, 'serviceWorker', {
      value: { register, controller: { postMessage: vi.fn() } },
      configurable: true,
    });
    const debugSpy = vi.spyOn(console, 'debug').mockImplementation(() => {});
    setupConfigScript();
    runScript();
    const loadCall = addEventListenerSpy.mock.calls.find((c) => c[0] === 'load');
    loadCall[1]();
    await Promise.resolve();
    await Promise.resolve();
    const updatefoundCb = registration.addEventListener.mock.calls.find((c) => c[0] === 'updatefound')[1];
    updatefoundCb();
    expect(newWorker.addEventListener).toHaveBeenCalledWith('statechange', expect.any(Function));
    const statechangeCb = newWorker.addEventListener.mock.calls.find((c) => c[0] === 'statechange')[1];
    statechangeCb();
    expect(debugSpy).toHaveBeenCalled();
    debugSpy.mockRestore();
    delete window.navigator.serviceWorker;
  });

  it('registerServiceWorker: updatefound with no installing worker bails without statechange', async () => {
    const registration = { addEventListener: vi.fn(), installing: null };
    const register = vi.fn(() => Promise.resolve(registration));
    Object.defineProperty(window.navigator, 'serviceWorker', {
      value: { register, controller: null },
      configurable: true,
    });
    setupConfigScript();
    runScript();
    const loadCall = addEventListenerSpy.mock.calls.find((c) => c[0] === 'load');
    loadCall[1]();
    await Promise.resolve();
    await Promise.resolve();
    const updatefoundCb = registration.addEventListener.mock.calls.find((c) => c[0] === 'updatefound')[1];
    // Should not throw even though installing is null.
    expect(() => updatefoundCb()).not.toThrow();
    delete window.navigator.serviceWorker;
  });

  // =========================================================================
  // initConsoleFilter() — requestIdleCallback absent + retry-until-found
  // =========================================================================

  it('initConsoleFilter: calls window.initConsoleFilter immediately once available (setTimeout path)', () => {
    vi.useFakeTimers();
    delete window.initConsoleFilter;
    const filterFn = vi.fn();
    setupConfigScript();
    runScript();
    // No requestIdleCallback in jsdom -> setTimeout(initFilter, 100) scheduled.
    window.initConsoleFilter = filterFn;
    vi.advanceTimersByTime(100);
    expect(filterFn).toHaveBeenCalled();
    vi.useRealTimers();
    delete window.initConsoleFilter;
  });

  it('initConsoleFilter: retries via setTimeout while window.initConsoleFilter stays undefined', () => {
    vi.useFakeTimers();
    delete window.initConsoleFilter;
    setupConfigScript();
    runScript();
    // First scheduled attempt (100ms) finds nothing -> reschedules itself at 50ms.
    vi.advanceTimersByTime(100);
    expect(window.initConsoleFilter).toBeUndefined();
    const filterFn = vi.fn();
    window.initConsoleFilter = filterFn;
    vi.advanceTimersByTime(50);
    expect(filterFn).toHaveBeenCalled();
    vi.useRealTimers();
    delete window.initConsoleFilter;
  });

  // =========================================================================
  // loadGoogleAnalytics() — interaction fires load() + onload gtag calls
  // =========================================================================

  it('loadGoogleAnalytics: click interaction loads script and onload pushes gtag calls', () => {
    delete window.dataLayer;
    setupConfigScript({ gaId: 'G-ABC' });
    runScript();
    window.dispatchEvent(new Event('click'));
    const script = document.head.querySelector('script[src*="googletagmanager"]');
    expect(script).toBeTruthy();
    script.onload();
    expect(Array.isArray(window.dataLayer)).toBe(true);
    expect(window.dataLayer.length).toBeGreaterThan(0);
    delete window.dataLayer;
  });

  it('loadGoogleAnalytics: second interaction event after fired is a no-op (loadOnce guard)', () => {
    setupConfigScript({ gaId: 'G-ABC' });
    runScript();
    window.dispatchEvent(new Event('click'));
    const scriptsAfterFirst = document.head.querySelectorAll('script[src*="googletagmanager"]').length;
    window.dispatchEvent(new Event('scroll'));
    const scriptsAfterSecond = document.head.querySelectorAll('script[src*="googletagmanager"]').length;
    expect(scriptsAfterSecond).toBe(scriptsAfterFirst);
  });

  // =========================================================================
  // loadKakaoSdk() — interaction fires load() + onload Kakao.init branches
  // =========================================================================

  it('loadKakaoSdk: interaction loads script and onload calls Kakao.init when not initialized', () => {
    setupConfigScript({ kakaoAppKey: 'kakao-key' });
    runScript();
    window.dispatchEvent(new Event('touchstart'));
    const script = document.head.querySelector('script[src*="kakao_js_sdk"]');
    expect(script).toBeTruthy();
    window.Kakao = { isInitialized: vi.fn(() => false), init: vi.fn() };
    script.onload();
    expect(window.Kakao.init).toHaveBeenCalledWith('kakao-key');
    delete window.Kakao;
  });

  it('loadKakaoSdk: onload skips init when Kakao already initialized', () => {
    setupConfigScript({ kakaoAppKey: 'kakao-key' });
    runScript();
    window.dispatchEvent(new Event('touchstart'));
    const script = document.head.querySelector('script[src*="kakao_js_sdk"]');
    window.Kakao = { isInitialized: vi.fn(() => true), init: vi.fn() };
    script.onload();
    expect(window.Kakao.init).not.toHaveBeenCalled();
    delete window.Kakao;
  });

  it('loadKakaoSdk: onload swallows errors thrown by Kakao.isInitialized', () => {
    setupConfigScript({ kakaoAppKey: 'kakao-key' });
    runScript();
    window.dispatchEvent(new Event('touchstart'));
    const script = document.head.querySelector('script[src*="kakao_js_sdk"]');
    window.Kakao = {
      isInitialized: vi.fn(() => {
        throw new Error('boom');
      }),
      init: vi.fn(),
    };
    expect(() => script.onload()).not.toThrow();
    delete window.Kakao;
  });

  // =========================================================================
  // loadSentry() — interaction fires load() + bundle onload chains init script
  // =========================================================================

  it('loadSentry: interaction loads bundle then chains sentry-init script on bundle onload', () => {
    setupConfigScript({
      sentryDsn: 'https://abc@sentry.io/1',
      sentryProductionHost: 'tech.example.com',
      sentryAllowedHosts: 'example.com',
    });
    runScript();
    window.dispatchEvent(new Event('keydown'));
    const bundleScript = document.head.querySelector('script[src*="browser.sentry-cdn.com"]');
    expect(bundleScript).toBeTruthy();
    bundleScript.onload();
    const initScript = document.head.querySelector('script[src="/assets/js/sentry-init.js"]');
    expect(initScript).toBeTruthy();
    expect(initScript.dataset.sentryDsn).toBe('https://abc@sentry.io/1');
    expect(initScript.dataset.productionHost).toBe('tech.example.com');
    expect(initScript.dataset.allowedHosts).toBe('example.com');
  });

  // =========================================================================
  // loadAdsense() — IntersectionObserver present/absent + onload/onerror
  // =========================================================================

  it('loadAdsense: with slot present, IntersectionObserver installs and load() fires on intersect', () => {
    stubIntersectionObserver();
    document.body.innerHTML =
      '<script id="head-runtime-script" data-adsense-client="ca-pub-123"></script>' +
      '<ins class="adsbygoogle"></ins>';
    runScript();
    const slot = document.querySelector('.adsbygoogle');
    const io = [...window.__ioInstances][0];
    io._trigger(slot);
    const script = document.head.querySelector('script[src*="googlesyndication"]');
    expect(script).toBeTruthy();
    script.onload();
    expect(window._adsenseLoaded).toBe(true);
    restoreIO();
  });

  it('loadAdsense: onerror hides existing .adsbygoogle slots', () => {
    stubIntersectionObserver();
    document.body.innerHTML =
      '<script id="head-runtime-script" data-adsense-client="ca-pub-123"></script>' +
      '<ins class="adsbygoogle"></ins>';
    runScript();
    const slot = document.querySelector('.adsbygoogle');
    const io = [...window.__ioInstances][0];
    io._trigger(slot);
    const script = document.head.querySelector('script[src*="googlesyndication"]');
    script.onerror();
    expect(slot.style.display).toBe('none');
    expect(window._adsenseLoaded).toBe(false);
    restoreIO();
  });

  it('loadAdsense: no slot yet in DOM watches via MutationObserver until it appears', () => {
    stubIntersectionObserver();
    setupConfigScript({ adsenseClient: 'ca-pub-123' });
    runScript();
    expect(document.querySelector('script[src*="googlesyndication"]')).toBeNull();
    const ins = document.createElement('ins');
    ins.className = 'adsbygoogle';
    document.body.appendChild(ins);
    // Flush MutationObserver microtask queue.
    return Promise.resolve().then(() => {
      const io = [...window.__ioInstances][0];
      expect(io).toBeTruthy();
      io._trigger(ins);
      expect(document.head.querySelector('script[src*="googlesyndication"]')).toBeTruthy();
      restoreIO();
    });
  });

  it('loadAdsense: no IntersectionObserver falls back to load event listener', () => {
    const originalIO = window.IntersectionObserver;
    delete window.IntersectionObserver;
    setupConfigScript({ adsenseClient: 'ca-pub-123' });
    runScript();
    const loadCall = addEventListenerSpy.mock.calls.find((c) => c[0] === 'load');
    expect(loadCall).toBeTruthy();
    loadCall[1]();
    expect(document.head.querySelector('script[src*="googlesyndication"]')).toBeTruthy();
    window.IntersectionObserver = originalIO;
  });

  // =========================================================================
  // loadFontTier2()
  // =========================================================================

  it('loadFontTier2: __fontTier2Loaded guard prevents duplicate scheduling', () => {
    window.__fontTier2Loaded = true;
    const addEventListenerLoadCallsBefore = addEventListenerSpy.mock.calls.filter(
      (c) => c[0] === 'load',
    ).length;
    setupConfigScript();
    runScript();
    const addEventListenerLoadCallsAfter = addEventListenerSpy.mock.calls.filter(
      (c) => c[0] === 'load',
    ).length;
    // Guard returns before scheduling anything new for font tier2.
    expect(addEventListenerLoadCallsAfter).toBe(addEventListenerLoadCallsBefore);
  });

  it('loadFontTier2: schedules via window load event when document.readyState is not complete', () => {
    delete window.__fontTier2Loaded;
    Object.defineProperty(document, 'readyState', { value: 'loading', configurable: true });
    setupConfigScript();
    runScript();
    const loadCall = addEventListenerSpy.mock.calls.find((c) => c[0] === 'load');
    expect(loadCall).toBeTruthy();
    expect(() => loadCall[1]()).not.toThrow();
    Object.defineProperty(document, 'readyState', { value: 'complete', configurable: true });
  });
});
