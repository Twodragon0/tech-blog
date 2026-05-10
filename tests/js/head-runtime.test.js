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
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/head-runtime.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

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
    addEventListenerSpy.mockRestore();
    window.matchMedia = originalMatchMedia;
    document.documentElement.removeAttribute('data-theme');
    document.body.classList.remove('loaded');
    document.body.innerHTML = '';
    localStorage.clear();
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
});
