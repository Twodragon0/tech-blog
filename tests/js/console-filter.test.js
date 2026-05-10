// Regression tests for assets/js/console-filter.js
//
// Goal: prove the console-filter (a) exposes window.initConsoleFilter,
// (b) is double-init guarded, (c) silences known noise patterns, and
// (d) enhances mapped error messages while passing through unrelated
// messages untouched.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/console-filter.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

describe('console-filter.js', () => {
  let originalError;
  let originalWarn;
  let originalLog;
  let originalFetch;
  let originalXHR;
  let originalOnError;

  beforeEach(() => {
    originalError = console.error;
    originalWarn = console.warn;
    originalLog = console.log;
    originalFetch = window.fetch;
    originalXHR = window.XMLHttpRequest;
    originalOnError = window.onerror;
    delete window._consoleFilterInitialized;
    delete window.initConsoleFilter;
    // jsdom default hostname is '' (not localhost/127.0.0.1), so the IIFE's
    // isDevelopment check evaluates to false — equivalent to production mode.
  });

  afterEach(() => {
    console.error = originalError;
    console.warn = originalWarn;
    console.log = originalLog;
    window.fetch = originalFetch;
    window.XMLHttpRequest = originalXHR;
    window.onerror = originalOnError;
    delete window._consoleFilterInitialized;
    delete window.initConsoleFilter;
  });

  it('exposes window.initConsoleFilter as a callable function', () => {
    runScript();
    expect(typeof window.initConsoleFilter).toBe('function');
    // Should not have actually initialized yet — only on call.
    expect(window._consoleFilterInitialized).toBeUndefined();
  });

  it('is double-init guarded (calling initConsoleFilter twice is safe)', () => {
    runScript();
    window.initConsoleFilter();
    expect(window._consoleFilterInitialized).toBe(true);
    const errorAfterFirst = console.error;
    window.initConsoleFilter(); // second call is a no-op
    expect(console.error).toBe(errorAfterFirst);
  });

  it('filters known noise patterns from console.error', () => {
    runScript();
    const captured = vi.fn();
    console.error = captured;
    window.initConsoleFilter();

    // Filtered (matches /runtime\.lastError/i)
    console.error('Unchecked runtime.lastError: chrome extension noise');
    // Filtered (matches /giscus\.app.*404/i)
    console.error('Failed to load resource: giscus.app/api/discussions 404');
    // Filtered (matches /favicon.*404/i)
    console.error('GET /favicon.png 404 (Not Found)');

    // The original underlying console.error should NOT have been called for any of these.
    expect(captured).not.toHaveBeenCalled();
  });

  it('passes through unrelated error messages to the original console.error', () => {
    runScript();
    const captured = vi.fn();
    console.error = captured;
    window.initConsoleFilter();
    // Genuine app error — should be enhanced or passed through, NOT silently dropped.
    console.error('TypeError: Cannot read properties of undefined (reading "foo")');
    expect(captured).toHaveBeenCalled();
  });

  it('intercepts fetch() to firebaseapp.com and resolves with a 200', async () => {
    runScript();
    window.initConsoleFilter();

    const resp = await window.fetch('https://example.firebaseapp.com/dynamic-link');
    expect(resp.status).toBe(200);
  });

  it('intercepts fetch() to app.goo.gl and resolves with a 200', async () => {
    runScript();
    window.initConsoleFilter();

    const resp = await window.fetch('https://app.goo.gl/abc123');
    expect(resp.status).toBe(200);
  });

  it('window.onerror returns true (handled) for filtered noise sources', () => {
    runScript();
    window.initConsoleFilter();

    // /runtime\.lastError/i pattern.
    const handled = window.onerror(
      'Unchecked runtime.lastError occurred',
      'chrome-extension://abc/script.js',
      1, 1, new Error('extension')
    );
    expect(handled).toBe(true);
  });
});
