// Regression tests for assets/js/console-filter.js
//
// Goal: prove the console-filter (a) exposes window.initConsoleFilter,
// (b) is double-init guarded, (c) silences known noise patterns, and
// (d) enhances mapped error messages while passing through unrelated
// messages untouched.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/console-filter.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

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
    // Note: jsdom's default test URL is http://localhost/, so the IIFE's
    // isDevelopment check evaluates to true by default. Tests that need real
    // production behavior override window.location explicitly (see the
    // "production mode" describe block below).
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

  it('window.onerror delegates to a pre-existing handler for non-noise errors', () => {
    const previous = vi.fn(() => 'previous-result');
    window.onerror = previous;
    runScript();
    window.initConsoleFilter();

    const result = window.onerror('Real bug happened', 'app.js', 10, 2, new Error('bug'));
    expect(previous).toHaveBeenCalledWith('Real bug happened', 'app.js', 10, 2, expect.any(Error));
    expect(result).toBe('previous-result');
  });

  it('window.onerror returns false for non-noise errors with no previous handler', () => {
    window.onerror = null;
    runScript();
    window.initConsoleFilter();

    const result = window.onerror('Real bug happened', 'app.js', 10, 2, new Error('bug'));
    expect(result).toBe(false);
  });

  describe('default env (jsdom default URL is http://localhost/ -> isDevelopment=true)', () => {
    it('safeLog uses console.log passthrough (isDevelopment branch) for non-noise logs', () => {
      runScript();
      const capturedLog = vi.fn();
      console.log = capturedLog;
      window.initConsoleFilter();

      console.log('plain development debug line');
      expect(capturedLog).toHaveBeenCalledWith('plain development debug line');
    });

    it('console.warn wrapper filters known noise patterns', () => {
      runScript();
      const capturedWarn = vi.fn();
      console.warn = capturedWarn;
      window.initConsoleFilter();

      console.warn('Unchecked runtime.lastError: extension noise');
      expect(capturedWarn).not.toHaveBeenCalled();
    });

    it('console.warn wrapper passes through unrelated warnings', () => {
      runScript();
      const capturedWarn = vi.fn();
      console.warn = capturedWarn;
      window.initConsoleFilter();

      console.warn('Deprecated API usage warning');
      expect(capturedWarn).toHaveBeenCalledWith('Deprecated API usage warning');
    });
  });

  describe('production mode (non-localhost hostname, isDevelopment=false)', () => {
    let originalLocation;

    beforeEach(() => {
      originalLocation = window.location;
      Object.defineProperty(window, 'location', {
        value: { hostname: 'example.com', search: '', href: 'https://example.com/' },
        writable: true,
        configurable: true,
      });
    });

    afterEach(() => {
      Object.defineProperty(window, 'location', {
        value: originalLocation,
        writable: true,
        configurable: true,
      });
    });

    it('console.log filters noise args but keeps unrelated args in production', () => {
      runScript();
      const capturedLog = vi.fn();
      console.log = capturedLog;
      window.initConsoleFilter();

      console.log('Unchecked runtime.lastError noise', 'real app message');
      expect(capturedLog).toHaveBeenCalledWith('real app message');
    });

    it('console.log emits nothing when every argument is noise in production', () => {
      runScript();
      const capturedLog = vi.fn();
      console.log = capturedLog;
      window.initConsoleFilter();

      console.log('Unchecked runtime.lastError noise');
      expect(capturedLog).not.toHaveBeenCalled();
    });

    it('does not print the dev init banner in production mode', () => {
      runScript();
      const capturedLog = vi.fn();
      console.log = capturedLog;
      window.initConsoleFilter();

      expect(capturedLog).not.toHaveBeenCalled();
    });
  });

  describe('non-string argument handling in safeLog', () => {
    it('passes through falsy non-string args untouched (e.g. 0)', () => {
      runScript();
      const captured = vi.fn();
      console.error = captured;
      window.initConsoleFilter();

      console.error(0);
      expect(captured).toHaveBeenCalledWith(0);
    });

    it('filters Error objects whose .message matches a noise pattern', () => {
      runScript();
      const captured = vi.fn();
      console.error = captured;
      window.initConsoleFilter();

      console.error(new Error('Unchecked runtime.lastError from extension'));
      expect(captured).not.toHaveBeenCalled();
    });

    it('filters objects using .toString() when no .message is present', () => {
      runScript();
      const captured = vi.fn();
      console.error = captured;
      window.initConsoleFilter();

      console.error({ toString: () => 'giscus.app 404 discussion missing' });
      expect(captured).not.toHaveBeenCalled();
    });

    it('passes through a non-matching Error object using .message', () => {
      runScript();
      const captured = vi.fn();
      console.error = captured;
      window.initConsoleFilter();

      const err = new Error('genuine application failure');
      console.error(err);
      expect(captured).toHaveBeenCalledWith(err);
    });
  });

  describe('window "error" event listener (resource errors)', () => {
    it('suppresses a filtered resource error on an <img> element', () => {
      runScript();
      window.initConsoleFilter();

      const img = document.createElement('img');
      document.body.appendChild(img);
      Object.defineProperty(img, 'currentSrc', {
        value: 'https://giscus.app/api/discussions?x=404',
        configurable: true,
      });

      const evt = new Event('error', { cancelable: true });
      const notPrevented = img.dispatchEvent(evt);
      expect(notPrevented).toBe(false); // dispatchEvent returns false when preventDefault() was called

      document.body.removeChild(img);
    });

    it('does not suppress a non-matching resource error on a <script> element', () => {
      runScript();
      window.initConsoleFilter();

      const script = document.createElement('script');
      script.src = 'https://example.com/app.js';
      document.body.appendChild(script);

      const evt = new Event('error', { cancelable: true });
      const notPrevented = script.dispatchEvent(evt);
      expect(notPrevented).toBe(true);

      document.body.removeChild(script);
    });

    it('ignores error events on elements with no src/href', () => {
      runScript();
      window.initConsoleFilter();

      const iframe = document.createElement('iframe');
      document.body.appendChild(iframe);

      const evt = new Event('error', { cancelable: true });
      expect(() => iframe.dispatchEvent(evt)).not.toThrow();

      document.body.removeChild(iframe);
    });

    it('ignores error events on unrelated tag types (e.g. <div>)', () => {
      runScript();
      window.initConsoleFilter();

      const div = document.createElement('div');
      document.body.appendChild(div);

      const evt = new Event('error', { cancelable: true });
      const notPrevented = div.dispatchEvent(evt);
      expect(notPrevented).toBe(true);

      document.body.removeChild(div);
    });

    it('ignores error events with no target', () => {
      runScript();
      window.initConsoleFilter();

      const evt = new Event('error', { cancelable: true });
      expect(() => window.dispatchEvent(evt)).not.toThrow();
    });
  });

  describe('unhandledrejection listener', () => {
    it('prevents default for a noise-matching Error reason (object branch)', () => {
      runScript();
      window.initConsoleFilter();

      const evt = new Event('unhandledrejection', { cancelable: true });
      evt.reason = new Error('Unchecked runtime.lastError: extension noise');
      const notPrevented = window.dispatchEvent(evt);
      expect(notPrevented).toBe(false);
    });

    it('prevents default for a noise-matching string reason (non-object branch)', () => {
      runScript();
      window.initConsoleFilter();

      const evt = new Event('unhandledrejection', { cancelable: true });
      evt.reason = 'giscus.app/api/discussions 404 not found';
      const notPrevented = window.dispatchEvent(evt);
      expect(notPrevented).toBe(false);
    });

    it('does not prevent default for a non-noise rejection reason', () => {
      runScript();
      window.initConsoleFilter();

      const evt = new Event('unhandledrejection', { cancelable: true });
      evt.reason = new Error('genuine unhandled rejection');
      const notPrevented = window.dispatchEvent(evt);
      expect(notPrevented).toBe(true);
    });
  });

  describe('fetch() wrapper', () => {
    it('quietly resolves 200 for Vercel speed-insights 429 rate limiting', async () => {
      window.fetch = vi.fn(() => Promise.resolve({ status: 429, statusText: 'Too Many Requests' }));
      runScript();
      window.initConsoleFilter();

      const resp = await window.fetch('https://example.com/_vercel/speed-insights/vitals');
      expect(resp.status).toBe(200);
    });

    it('passes through a non-429 speed-insights response unchanged', async () => {
      window.fetch = vi.fn(() => Promise.resolve({ status: 200, statusText: 'OK' }));
      runScript();
      window.initConsoleFilter();

      const resp = await window.fetch('https://example.com/_vercel/speed-insights/vitals');
      expect(resp.status).toBe(200);
      expect(resp.statusText).toBe('OK');
    });

    it('resolves 200 when the speed-insights request itself rejects', async () => {
      window.fetch = vi.fn(() => Promise.reject(new Error('network down')));
      runScript();
      window.initConsoleFilter();

      const resp = await window.fetch('https://example.com/_vercel/speed-insights/vitals');
      expect(resp.status).toBe(200);
    });

    it('resolves 200 for a generic fetch rejection matching a noise pattern', async () => {
      const err = new Error('Failed to load resource: net::ERR_NAME_NOT_RESOLVED');
      window.fetch = vi.fn(() => Promise.reject(err));
      runScript();
      window.initConsoleFilter();

      const resp = await window.fetch('https://e.dlx.addthis.com/track');
      expect(resp.status).toBe(200);
    });

    it('resolves 200 for a giscus 404 rejection (status-based branch)', async () => {
      const err = new Error('request failed');
      err.status = 404;
      window.fetch = vi.fn(() => Promise.reject(err));
      runScript();
      window.initConsoleFilter();

      const resp = await window.fetch('https://giscus.app/widget');
      expect(resp.status).toBe(200);
    });

    it('resolves 200 for an AdSense 400/403 rejection (status-based branch)', async () => {
      const err = new Error('request failed');
      err.status = 403;
      window.fetch = vi.fn(() => Promise.reject(err));
      runScript();
      window.initConsoleFilter();

      const resp = await window.fetch('https://pagead2.googlesyndication.com/pagead/ads');
      expect(resp.status).toBe(200);
    });

    it('rethrows a genuine fetch error unrelated to any known noise source', async () => {
      const err = new Error('DNS resolution failed');
      window.fetch = vi.fn(() => Promise.reject(err));
      runScript();
      window.initConsoleFilter();

      await expect(window.fetch('https://api.example.com/data')).rejects.toBe(err);
    });

    it('accepts a Request-like object (args[0].url) instead of a string URL', async () => {
      window.fetch = vi.fn(() => Promise.resolve({ status: 200, statusText: 'OK' }));
      runScript();
      window.initConsoleFilter();

      const resp = await window.fetch({ url: 'https://api.example.com/data' });
      expect(resp.status).toBe(200);
    });
  });

  describe('XMLHttpRequest wrapper', () => {
    class FakeXHR {
      constructor() {
        this.readyState = 0;
        this.status = 0;
        this.statusText = '';
        this.responseText = '';
        this.onerror = null;
      }
      open(method, url, ...rest) {
        this._openedWith = [method, url, ...rest];
      }
    }

    beforeEach(() => {
      window.XMLHttpRequest = FakeXHR;
    });

    it('quietly short-circuits Firebase Dynamic Links requests', () => {
      runScript();
      window.initConsoleFilter();

      const xhr = new window.XMLHttpRequest();
      xhr.open('GET', 'https://sub.firebaseapp.com/dynamic-link');

      expect(xhr.readyState).toBe(4);
      expect(xhr.status).toBe(200);
      expect(xhr.responseText).toBe('');
      expect(xhr._openedWith).toBeUndefined(); // originalOpen never invoked
    });

    it('quietly short-circuits app.goo.gl requests', () => {
      runScript();
      window.initConsoleFilter();

      const xhr = new window.XMLHttpRequest();
      xhr.open('GET', 'https://app.goo.gl/abc123');

      expect(xhr.readyState).toBe(4);
      expect(xhr.status).toBe(200);
    });

    it('wraps onerror for giscus URLs and normalizes a 404 to a quiet 200', () => {
      runScript();
      window.initConsoleFilter();

      const xhr = new window.XMLHttpRequest();
      xhr.open('GET', 'https://giscus.app/api/discussions');
      xhr.status = 404;
      xhr.onerror();

      expect(xhr.readyState).toBe(4);
      expect(xhr.status).toBe(200);
    });

    it('delegates to a pre-existing onerror for giscus URLs on a non-404 status', () => {
      runScript();
      window.initConsoleFilter();

      const xhr = new window.XMLHttpRequest();
      const previousOnError = vi.fn();
      xhr.onerror = previousOnError;
      xhr.open('GET', 'https://giscus.app/api/discussions');
      xhr.status = 500;
      xhr.onerror();

      expect(previousOnError).toHaveBeenCalled();
      expect(xhr.status).toBe(500); // not normalized
    });

    it('wraps onerror for AdSense URLs and normalizes 400/403 to a quiet 200', () => {
      runScript();
      window.initConsoleFilter();

      const xhr = new window.XMLHttpRequest();
      xhr.open('GET', 'https://pagead2.googlesyndication.com/pagead/ads');
      xhr.status = 400;
      xhr.onerror();

      expect(xhr.readyState).toBe(4);
      expect(xhr.status).toBe(200);
    });

    it('delegates to a pre-existing onerror for AdSense URLs on a non-400/403 status', () => {
      runScript();
      window.initConsoleFilter();

      const xhr = new window.XMLHttpRequest();
      const previousOnError = vi.fn();
      xhr.onerror = previousOnError;
      xhr.open('GET', 'https://googlesyndication.com/pagead/ads');
      xhr.status = 500;
      xhr.onerror();

      expect(previousOnError).toHaveBeenCalled();
      expect(xhr.status).toBe(500);
    });

    it('passes through unrelated URLs to the original open() with extra args intact', () => {
      runScript();
      window.initConsoleFilter();

      const xhr = new window.XMLHttpRequest();
      xhr.open('GET', 'https://api.example.com/data', true, 'user', 'pass');

      expect(xhr._openedWith).toEqual(['GET', 'https://api.example.com/data', true, 'user', 'pass']);
    });
  });
});
