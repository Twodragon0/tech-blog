// Regression tests for assets/js/footer-runtime.js
//
// Goal: prove the footer runtime (a) is double-init guarded via
// window.__footerRuntimeInitialized, (b) lazy-loads main-search.js on first
// focus of #search-input (once, idempotent), (c) falls back to loading the
// search script after a 3s timer when the tab stays visible and focus never
// fired, (d) bails out of analytics injection on localhost/127.0.0.1, and
// (e) injects the Vercel analytics script (and, when sampled, speed-insights)
// on non-local hosts.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/footer-runtime.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

function searchScripts() {
  return Array.from(document.querySelectorAll('script[src*="main-search.js"]'));
}

function analyticsScripts() {
  return Array.from(document.querySelectorAll('script[src*="va.vercel-scripts.com/v1/script.js"]'));
}

function speedInsightsScripts() {
  return Array.from(document.querySelectorAll('script[src*="speed-insights/script.js"]'));
}

function setHostname(hostname) {
  Object.defineProperty(window, 'location', {
    value: { hostname, href: 'https://' + hostname + '/' },
    writable: true,
    configurable: true,
  });
}

describe('footer-runtime.js', () => {
  let originalLocation;

  beforeEach(() => {
    originalLocation = window.location;
    document.head.innerHTML = '';
    document.body.innerHTML = '';
    delete window.__footerRuntimeInitialized;
    // jsdom's default hostname is 'localhost', which is equivalent to the
    // production-analytics-disabled branch. Tests that need the analytics
    // branch explicitly override hostname via setHostname().
  });

  afterEach(() => {
    Object.defineProperty(window, 'location', {
      value: originalLocation,
      writable: true,
      configurable: true,
    });
    document.head.innerHTML = '';
    document.body.innerHTML = '';
    delete window.__footerRuntimeInitialized;
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('sets window.__footerRuntimeInitialized after running', () => {
    expect(() => runScript()).not.toThrow();
    expect(window.__footerRuntimeInitialized).toBe(true);
  });

  it('is double-init guarded: a second run does not attach a second focus listener', () => {
    document.body.innerHTML = '<input id="search-input" type="text" />';
    const addEventListenerSpy = vi.spyOn(HTMLElement.prototype, 'addEventListener');

    runScript();
    const callsAfterFirstRun = addEventListenerSpy.mock.calls.length;

    runScript(); // guard should make this a no-op
    expect(addEventListenerSpy.mock.calls.length).toBe(callsAfterFirstRun);
  });

  it('bails cleanly when #search-input is missing (no throw, no script injected)', () => {
    expect(() => runScript()).not.toThrow();
    expect(searchScripts()).toHaveLength(0);
  });

  it('lazy-loads main-search.js on first focus of #search-input', () => {
    document.body.innerHTML = '<input id="search-input" type="text" />';
    runScript();

    expect(searchScripts()).toHaveLength(0);
    document.getElementById('search-input').dispatchEvent(new Event('focus'));

    const injected = searchScripts();
    expect(injected).toHaveLength(1);
    expect(injected[0].defer).toBe(true);
    expect(injected[0].src).toContain('/assets/js/main-search.js');
  });

  it('does not double-load main-search.js when focused twice (listener is { once: true })', () => {
    document.body.innerHTML = '<input id="search-input" type="text" />';
    runScript();

    const input = document.getElementById('search-input');
    input.dispatchEvent(new Event('focus'));
    input.dispatchEvent(new Event('focus'));
    expect(searchScripts()).toHaveLength(1);
  });

  it('falls back to loading main-search.js ~3s later when the tab is visible and focus never fired', () => {
    document.body.innerHTML = '<input id="search-input" type="text" />';
    Object.defineProperty(document, 'visibilityState', {
      value: 'visible',
      configurable: true,
    });

    vi.useFakeTimers();
    runScript();
    expect(searchScripts()).toHaveLength(0);

    vi.advanceTimersByTime(3000);
    // requestIdleCallback is undefined in jsdom, so the fallback schedules a
    // second setTimeout(loadSearchScript, 0) — flush it too.
    vi.runOnlyPendingTimers();

    expect(searchScripts()).toHaveLength(1);
  });

  it('does not run the fallback timer load when the tab is hidden', () => {
    document.body.innerHTML = '<input id="search-input" type="text" />';
    Object.defineProperty(document, 'visibilityState', {
      value: 'hidden',
      configurable: true,
    });

    vi.useFakeTimers();
    runScript();
    vi.advanceTimersByTime(3000);
    vi.runOnlyPendingTimers();

    expect(searchScripts()).toHaveLength(0);
  });

  it('does not double-load via the fallback timer if focus already loaded the script', () => {
    document.body.innerHTML = '<input id="search-input" type="text" />';
    Object.defineProperty(document, 'visibilityState', {
      value: 'visible',
      configurable: true,
    });

    vi.useFakeTimers();
    runScript();
    document.getElementById('search-input').dispatchEvent(new Event('focus'));
    expect(searchScripts()).toHaveLength(1);

    vi.advanceTimersByTime(3000);
    vi.runOnlyPendingTimers();
    expect(searchScripts()).toHaveLength(1);
  });

  it('does not inject the analytics script on localhost', () => {
    setHostname('localhost');
    runScript();
    expect(analyticsScripts()).toHaveLength(0);
    expect(speedInsightsScripts()).toHaveLength(0);
  });

  it('does not inject the analytics script on 127.0.0.1', () => {
    setHostname('127.0.0.1');
    runScript();
    expect(analyticsScripts()).toHaveLength(0);
    expect(speedInsightsScripts()).toHaveLength(0);
  });

  it('injects the Vercel analytics script on a non-local host', () => {
    setHostname('tech.2twodragon.com');
    vi.spyOn(Math, 'random').mockReturnValue(0.9); // >= 0.1 => not sampled for speed-insights

    runScript();

    const injected = analyticsScripts();
    expect(injected).toHaveLength(1);
    expect(injected[0].defer).toBe(true);
    expect(injected[0].src).toBe('https://va.vercel-scripts.com/v1/script.js');
    expect(injected[0].parentElement).toBe(document.head);
    expect(speedInsightsScripts()).toHaveLength(0);
  });

  it('injects the speed-insights script when the 10% sample roll succeeds', () => {
    setHostname('tech.2twodragon.com');
    vi.spyOn(Math, 'random').mockReturnValue(0.05); // < 0.1 => sampled

    runScript();

    const injected = speedInsightsScripts();
    expect(injected).toHaveLength(1);
    expect(injected[0].defer).toBe(true);
    expect(injected[0].src).toBe('https://va.vercel-scripts.com/v1/speed-insights/script.js');
    expect(analyticsScripts()).toHaveLength(1);
  });

  it('does not inject speed-insights when the sample roll fails (boundary at 0.1)', () => {
    setHostname('tech.2twodragon.com');
    vi.spyOn(Math, 'random').mockReturnValue(0.1); // not < 0.1 => not sampled

    runScript();

    expect(speedInsightsScripts()).toHaveLength(0);
    expect(analyticsScripts()).toHaveLength(1);
  });
});
