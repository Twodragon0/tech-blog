// Regression tests for assets/js/sentry-init.js
//
// sentry-init.js is a standalone IIFE that:
//   1. Reads data-sentry-dsn from document.currentScript.
//   2. Bails immediately if dsn is empty.
//   3. When window.Sentry is defined, calls Sentry.init() with dsn,
//      environment (derived from hostname), allowUrls (regex array from
//      data-allowed-hosts), and sampleRate (0 when not production).
//   4. typeof Sentry is a bare identifier check — so Sentry must be on the
//      real global (window.Sentry) for the script to detect it.
//
// We evaluate the IIFE with new Function(src)(). Hostname is controlled by
// deleting window.location and assigning a plain object — the standard jsdom
// workaround for the non-configurable window.location.hostname property.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/sentry-init.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

/**
 * Override window.location with a plain stub.
 * jsdom does not allow Object.defineProperty on window.location.hostname,
 * but allows replacing window.location altogether via delete + assignment.
 */
function setHostname(hostname) {
  delete window.location;
  window.location = {
    hostname,
    href: `https://${hostname}/`,
    origin: `https://${hostname}`,
    pathname: '/',
    hash: '',
  };
}

/**
 * Inject a <script> element with given attrs and override document.currentScript
 * to return it for the duration of the IIFE evaluation.
 */
function runScriptWithAttrs(attrs = {}) {
  const el = document.createElement('script');
  Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
  document.body.appendChild(el);

  const descriptor = Object.getOwnPropertyDescriptor(Document.prototype, 'currentScript');
  Object.defineProperty(document, 'currentScript', {
    get: () => el,
    configurable: true,
  });
  try {
    // eslint-disable-next-line no-new-func
    new Function(SCRIPT_SOURCE)();
  } finally {
    if (descriptor) {
      Object.defineProperty(document, 'currentScript', descriptor);
    } else {
      delete document.currentScript;
    }
  }
}

/**
 * Spy on window.addEventListener and bucket registered handlers by event type,
 * so tests can invoke the 'error' / 'unhandledrejection' / 'load' handlers
 * directly with hand-crafted event objects instead of relying on jsdom's
 * (incomplete) ErrorEvent/PromiseRejectionEvent constructors.
 */
function captureListeners() {
  const listeners = {};
  const spy = vi.spyOn(window, 'addEventListener').mockImplementation((type, handler) => {
    (listeners[type] = listeners[type] || []).push(handler);
  });
  return {
    listeners,
    restore: () => spy.mockRestore(),
  };
}

describe('sentry-init.js', () => {
  let sentryInit;
  let sentryCaptureException;

  beforeEach(() => {
    sentryInit = vi.fn();
    sentryCaptureException = vi.fn();
    // Sentry must be on the real global so `typeof Sentry === 'undefined'` works.
    window.Sentry = { init: sentryInit, captureException: sentryCaptureException };

    // Default: production host.
    setHostname('tech.2twodragon.com');
    localStorage.clear();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    delete window.Sentry;
    // Restore a real location so other tests aren't affected.
    delete window.location;
    window.location = { hostname: 'localhost', href: 'http://localhost/', pathname: '/', hash: '', origin: 'http://localhost' };
    localStorage.clear();
    document.body.innerHTML = '';
  });

  // =========================================================================
  // Early-bail: window.Sentry undefined
  // =========================================================================

  it('bails when window.Sentry is undefined — Sentry.init is never called', () => {
    delete window.Sentry;
    runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
    expect(sentryInit).not.toHaveBeenCalled();
  });

  // =========================================================================
  // Early-bail: empty dsn
  // =========================================================================

  it('bails when data-sentry-dsn is empty — Sentry.init is never called', () => {
    runScriptWithAttrs({ 'data-sentry-dsn': '' });
    expect(sentryInit).not.toHaveBeenCalled();
  });

  // =========================================================================
  // Sentry.init called with correct dsn
  // =========================================================================

  it('calls Sentry.init with the dsn read from data-sentry-dsn', () => {
    const dsn = 'https://testkey@o0.ingest.sentry.io/123456';
    runScriptWithAttrs({ 'data-sentry-dsn': dsn });
    expect(sentryInit).toHaveBeenCalledTimes(1);
    expect(sentryInit.mock.calls[0][0].dsn).toBe(dsn);
  });

  // =========================================================================
  // allowUrls built from data-allowed-hosts
  // =========================================================================

  it('builds allowUrls regex array from data-allowed-hosts CSV', () => {
    runScriptWithAttrs({
      'data-sentry-dsn': 'https://abc@sentry.io/1',
      'data-allowed-hosts': 'tech.2twodragon.com,twodragon0.github.io',
    });
    expect(sentryInit).toHaveBeenCalledTimes(1);
    const { allowUrls } = sentryInit.mock.calls[0][0];
    expect(Array.isArray(allowUrls)).toBe(true);
    expect(allowUrls.length).toBe(2);
    expect(allowUrls[0]).toBeInstanceOf(RegExp);
    expect(allowUrls[0].test('https://tech.2twodragon.com/some/path')).toBe(true);
    expect(allowUrls[1].test('https://twodragon0.github.io/tech-blog/')).toBe(true);
  });

  // =========================================================================
  // localhost → development environment
  // =========================================================================

  it('sets environment to "development" on localhost', () => {
    setHostname('localhost');
    runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
    expect(sentryInit).toHaveBeenCalledTimes(1);
    expect(sentryInit.mock.calls[0][0].environment).toBe('development');
  });

  // =========================================================================
  // production host → production environment
  // =========================================================================

  it('sets environment to "production" on the production host', () => {
    // hostname is already 'tech.2twodragon.com' from beforeEach.
    runScriptWithAttrs({
      'data-sentry-dsn': 'https://abc@sentry.io/1',
      'data-allowed-hosts': 'tech.2twodragon.com',
    });
    expect(sentryInit).toHaveBeenCalledTimes(1);
    expect(sentryInit.mock.calls[0][0].environment).toBe('production');
  });

  // =========================================================================
  // sampleRate is 0 on non-production hosts
  // =========================================================================

  it('passes sampleRate 0 on non-production, non-backup host (preview env)', () => {
    setHostname('my-branch.vercel.app');
    runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
    expect(sentryInit).toHaveBeenCalledTimes(1);
    // getDynamicSampleRate() returns 0 when !isProduction.
    expect(sentryInit.mock.calls[0][0].sampleRate).toBe(0);
  });

  it('sets environment to "preview" on non-production, non-backup, non-dev host', () => {
    setHostname('my-branch.vercel.app');
    runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
    expect(sentryInit.mock.calls[0][0].environment).toBe('preview');
  });

  it('sets environment to "backup" on the GitHub Pages backup host', () => {
    setHostname('twodragon0.github.io');
    runScriptWithAttrs({
      'data-sentry-dsn': 'https://abc@sentry.io/1',
      'data-allowed-hosts': 'twodragon0.github.io',
    });
    expect(sentryInit.mock.calls[0][0].environment).toBe('backup');
  });

  // =========================================================================
  // release() branches
  // =========================================================================

  describe('release string', () => {
    it('uses VERCEL_GIT_COMMIT_SHA when present, truncated to 7 chars', () => {
      window.VERCEL_GIT_COMMIT_SHA = 'abcdef0123456789';
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      expect(sentryInit.mock.calls[0][0].release).toBe('tech-blog@abcdef0');
      delete window.VERCEL_GIT_COMMIT_SHA;
    });

    it('falls back to a date-based release on production without VERCEL_GIT_COMMIT_SHA', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      expect(sentryInit.mock.calls[0][0].release).toMatch(/^tech-blog@\d{8}$/);
    });

    it('is undefined on non-production without VERCEL_GIT_COMMIT_SHA', () => {
      setHostname('my-branch.vercel.app');
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      expect(sentryInit.mock.calls[0][0].release).toBeUndefined();
    });
  });

  // =========================================================================
  // getDynamicSampleRate() thresholds (production only)
  // =========================================================================

  describe('dynamic sample rate thresholds', () => {
    function seedMonthlyCount(count) {
      localStorage.setItem('se_ts', String(Date.now()));
      localStorage.setItem('se_month', String(count));
    }

    it('returns 0.3 when monthly count exceeds 90% of the limit', () => {
      seedMonthlyCount(4600); // > 4500 (90% of 5000)
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      expect(sentryInit.mock.calls[0][0].sampleRate).toBe(0.3);
    });

    it('returns 0.5 when monthly count exceeds 80% but not 90%', () => {
      seedMonthlyCount(4100); // > 4000, <= 4500
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      expect(sentryInit.mock.calls[0][0].sampleRate).toBe(0.5);
    });

    it('returns 0.75 when monthly count exceeds 60% but not 80%', () => {
      seedMonthlyCount(3100); // > 3000, <= 4000
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      expect(sentryInit.mock.calls[0][0].sampleRate).toBe(0.75);
    });

    it('returns 1 when monthly count is at or below 60%', () => {
      seedMonthlyCount(100);
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      expect(sentryInit.mock.calls[0][0].sampleRate).toBe(1);
    });
  });

  // =========================================================================
  // getMonthlyCount() reset / catch branches
  // =========================================================================

  describe('monthly count storage edge cases', () => {
    it('resets the counter when the stored timestamp is older than 30 days', () => {
      const oldTs = Date.now() - (31 * 24 * 60 * 60 * 1000);
      localStorage.setItem('se_ts', String(oldTs));
      localStorage.setItem('se_month', '4999');
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      // count reset to 0 -> falls in the <=60% bucket -> sampleRate 1.
      expect(sentryInit.mock.calls[0][0].sampleRate).toBe(1);
      expect(localStorage.getItem('se_month')).toBe('0');
    });

    it('falls back to count 0 when localStorage.getItem throws', () => {
      const spy = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
        throw new Error('storage disabled');
      });
      expect(() =>
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' })
      ).not.toThrow();
      expect(sentryInit.mock.calls[0][0].sampleRate).toBe(1);
      spy.mockRestore();
    });
  });

  // =========================================================================
  // beforeSend() — host / environment gating
  // =========================================================================

  describe('beforeSend host and environment gating', () => {
    it('returns null when the current host is not in the allowed-hosts list', () => {
      runScriptWithAttrs({
        'data-sentry-dsn': 'https://abc@sentry.io/1',
        'data-allowed-hosts': 'some-other-host.com',
      });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      expect(beforeSend({ message: 'hi' }, {})).toBeNull();
    });

    it('returns null on an allowed host that is neither production nor backup', () => {
      setHostname('my-branch.vercel.app');
      runScriptWithAttrs({
        'data-sentry-dsn': 'https://abc@sentry.io/1',
        'data-allowed-hosts': 'my-branch.vercel.app',
      });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      expect(beforeSend({ message: 'hi' }, {})).toBeNull();
    });

    it('proceeds (does not early-return null) on the backup host', () => {
      setHostname('twodragon0.github.io');
      runScriptWithAttrs({
        'data-sentry-dsn': 'https://abc@sentry.io/1',
        'data-allowed-hosts': 'twodragon0.github.io',
      });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = { message: 'plain event' };
      expect(beforeSend(event, {})).toBe(event);
    });
  });

  // =========================================================================
  // beforeSend() — noise filtering
  // =========================================================================

  describe('beforeSend noise filtering', () => {
    it('drops events whose hint.originalException.message matches a noise pattern', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const hint = { originalException: { message: 'ResizeObserver loop limit exceeded' } };
      expect(beforeSend({ message: 'unrelated' }, hint)).toBeNull();
    });

    it('drops events whose event.message matches a noise pattern', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      expect(beforeSend({ message: 'Script error.' }, {})).toBeNull();
    });

    it('drops events whose message is exactly "unknown error"', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      expect(beforeSend({ message: 'Unknown Error' }, {})).toBeNull();
    });

    it('does not drop non-noise events with a real message', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = { message: 'TypeError: something broke' };
      expect(beforeSend(event, {})).toBe(event);
    });
  });

  // =========================================================================
  // beforeSend() — exception stacktrace "hasOurCode" branches
  // =========================================================================

  describe('beforeSend exception frame filtering', () => {
    it('keeps events when a frame filename starts with /assets/js/', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        exception: {
          values: [
            {
              value: 'boom',
              stacktrace: { frames: [{ filename: '/assets/js/main.js' }] },
            },
          ],
        },
      };
      expect(beforeSend(event, {})).toBe(event);
    });

    it('keeps events when a frame URL hostname is in the allowed hosts list', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        exception: {
          values: [
            {
              value: 'boom',
              stacktrace: {
                frames: [{ filename: 'https://tech.2twodragon.com/assets/js/vendor.js' }],
              },
            },
          ],
        },
      };
      expect(beforeSend(event, {})).toBe(event);
    });

    it('treats an unparsable frame filename as not-our-code (catch branch)', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        exception: {
          values: [
            {
              // no exc.value -> combined with hasOurCode=false -> dropped.
              stacktrace: { frames: [{ filename: 'http://[::1' }] },
            },
          ],
        },
      };
      expect(beforeSend(event, {})).toBeNull();
    });

    it('drops events with no matching frame and no exc.value', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        exception: {
          values: [{ stacktrace: { frames: [{ filename: 'https://third-party.com/lib.js' }] } }],
        },
      };
      expect(beforeSend(event, {})).toBeNull();
    });

    it('drops events with no matching frame and a noise exc.value', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        exception: {
          values: [
            {
              value: 'network error',
              stacktrace: { frames: [{ filename: 'https://third-party.com/lib.js' }] },
            },
          ],
        },
      };
      expect(beforeSend(event, {})).toBeNull();
    });

    it('keeps events with no matching frame but a real exc.value', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        exception: {
          values: [
            {
              value: 'ReferenceError: x is not defined',
              stacktrace: { frames: [{ filename: 'https://third-party.com/lib.js' }] },
            },
          ],
        },
      };
      expect(beforeSend(event, {})).toBe(event);
    });

    it('skips frames without a filename when checking hasOurCode', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        exception: {
          values: [
            {
              value: 'ReferenceError: x is not defined',
              stacktrace: { frames: [{}, { filename: '/assets/js/app.js' }] },
            },
          ],
        },
      };
      expect(beforeSend(event, {})).toBe(event);
    });

    it('treats a missing stacktrace as no matching frame (short-circuit)', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = { exception: { values: [{ value: 'boom, no stacktrace' }] } };
      expect(beforeSend(event, {})).toBe(event);
    });
  });

  // =========================================================================
  // beforeSend() — throttling (isThrottled)
  // =========================================================================

  describe('beforeSend throttling', () => {
    it('does not throttle the first occurrence of a fingerprint', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = { message: 'repeat-me' };
      expect(beforeSend(event, {})).toBe(event);
    });

    it('resets the throttle window once an hour has elapsed', () => {
      vi.useFakeTimers();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const { beforeSend } = sentryInit.mock.calls[0][0];
        const event = { message: 'stale-window' };
        expect(beforeSend(event, {})).toBe(event);
        vi.advanceTimersByTime(3600001);
        expect(beforeSend(event, {})).toBe(event);
      } finally {
        vi.useRealTimers();
      }
    });

    it('throttles after more than 8 occurrences when Math.random() > 0.3', () => {
      const randomSpy = vi.spyOn(Math, 'random').mockReturnValue(0.9);
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const { beforeSend } = sentryInit.mock.calls[0][0];
        const event = { fingerprint: ['same-key'] };
        let lastResult;
        for (let i = 0; i < 10; i += 1) {
          lastResult = beforeSend({ ...event }, {});
        }
        expect(lastResult).toBeNull();
      } finally {
        randomSpy.mockRestore();
      }
    });

    it('does not throttle after more than 8 occurrences when Math.random() <= 0.3', () => {
      const randomSpy = vi.spyOn(Math, 'random').mockReturnValue(0.1);
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const { beforeSend } = sentryInit.mock.calls[0][0];
        let lastResult;
        for (let i = 0; i < 10; i += 1) {
          lastResult = beforeSend({ fingerprint: ['another-key'] }, {});
        }
        expect(lastResult).not.toBeNull();
      } finally {
        randomSpy.mockRestore();
      }
    });

    it('derives the throttle key from event.message when fingerprint is absent', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      expect(beforeSend({ message: 'keyed-by-message' }, {})).toEqual({
        message: 'keyed-by-message',
      });
    });

    it('derives the throttle key as "unknown" when both fingerprint and message are absent', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      expect(beforeSend({}, {})).toEqual({});
    });
  });

  // =========================================================================
  // beforeSend() — request URL / cookie scrubbing
  // =========================================================================

  describe('beforeSend request scrubbing', () => {
    it('removes sensitive query params and cookies from event.request', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        message: 'req-scrub',
        request: {
          url: 'https://tech.2twodragon.com/page?token=abc&keep=1&password=xyz',
          cookies: { session: 'abc' },
        },
      };
      const result = beforeSend(event, {});
      expect(result.request.url).toBe('https://tech.2twodragon.com/page?keep=1');
      expect(result.request.cookies).toBeUndefined();
    });

    it('leaves the URL unchanged when it cannot be parsed (catch branch)', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        message: 'bad-url',
        request: { url: '::not a valid url::', cookies: { a: '1' } },
      };
      const result = beforeSend(event, {});
      expect(result.request.url).toBe('::not a valid url::');
      expect(result.request.cookies).toBeUndefined();
    });

    it('skips the request-scrubbing block entirely when event.request is absent', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = { message: 'no-request' };
      expect(beforeSend(event, {})).toBe(event);
    });
  });

  // =========================================================================
  // beforeSend() — stack-frame path masking and var redaction
  // =========================================================================

  describe('beforeSend frame masking and redaction', () => {
    it('masks /Users/<name> and /home/<name> in frame filenames', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        message: 'path-mask',
        exception: {
          values: [
            {
              stacktrace: {
                frames: [
                  { filename: '/Users/alice/project/app.js' },
                  { filename: '/home/bob/project/app.js' },
                ],
              },
            },
          ],
        },
      };
      const result = beforeSend(event, {});
      expect(result.exception.values[0].stacktrace.frames[0].filename).toBe(
        '/Users/***/project/app.js'
      );
      expect(result.exception.values[0].stacktrace.frames[1].filename).toBe(
        '/home/***/project/app.js'
      );
    });

    it('redacts frame.vars entries whose key name looks sensitive', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        message: 'var-redact-key',
        exception: {
          values: [
            {
              stacktrace: {
                frames: [
                  {
                    filename: '/assets/js/app.js',
                    // `count: 0` has a non-sensitive key name (so the `||`
                    // evaluates its 2nd operand) and a falsy value, exercising
                    // the `frame.vars[variableName] || ''` fallback branch.
                    vars: { password: 'hunter2', count: 0, safe: 'ok' },
                  },
                ],
              },
            },
          ],
        },
      };
      const result = beforeSend(event, {});
      const vars = result.exception.values[0].stacktrace.frames[0].vars;
      expect(vars.password).toBe('***REDACTED***');
      expect(vars.count).toBe(0);
      expect(vars.safe).toBe('ok');
    });

    it('redacts frame.vars entries whose value content looks sensitive', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        message: 'var-redact-value',
        exception: {
          values: [
            {
              stacktrace: {
                frames: [{ filename: '/assets/js/app.js', vars: { note: 'contains a token value' } }],
              },
            },
          ],
        },
      };
      const result = beforeSend(event, {});
      expect(result.exception.values[0].stacktrace.frames[0].vars.note).toBe('***REDACTED***');
    });

    it('skips exception entries without a stacktrace or frames', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = { message: 'no-stack', exception: { values: [{ value: 'boom' }] } };
      expect(beforeSend(event, {})).toBe(event);
    });

    it('leaves frames without filename or vars untouched', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const event = {
        message: 'bare-frame',
        // exc.value truthy + non-noise keeps the event past the hasOurCode gate
        // even though the (only) frame has neither filename nor vars.
        exception: { values: [{ value: 'ReferenceError: y', stacktrace: { frames: [{}] } }] },
      };
      expect(beforeSend(event, {})).toBe(event);
    });
  });

  // =========================================================================
  // beforeSend() — breadcrumb slicing
  // =========================================================================

  describe('beforeSend breadcrumb slicing', () => {
    it('slices breadcrumbs down to the last 8 when there are more than 8', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const breadcrumbs = Array.from({ length: 12 }, (_, i) => ({ message: `crumb-${i}` }));
      const result = beforeSend({ message: 'many-crumbs', breadcrumbs }, {});
      expect(result.breadcrumbs).toHaveLength(8);
      expect(result.breadcrumbs[0].message).toBe('crumb-4');
    });

    it('leaves breadcrumbs untouched when there are 8 or fewer', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeSend } = sentryInit.mock.calls[0][0];
      const breadcrumbs = Array.from({ length: 3 }, (_, i) => ({ message: `crumb-${i}` }));
      const result = beforeSend({ message: 'few-crumbs', breadcrumbs }, {});
      expect(result.breadcrumbs).toHaveLength(3);
    });
  });

  // =========================================================================
  // beforeSend() — dev monthly-limit console.warn branch
  // =========================================================================

  it('warns via console.warn when in dev and the monthly count exceeds 80% of the limit', () => {
    // Force isProduction AND isDev true simultaneously by pointing both the
    // actual hostname and data-production-host at localhost (the only way
    // both conditions overlap, since isDev is hostname-derived too).
    setHostname('localhost');
    localStorage.setItem('se_ts', String(Date.now()));
    localStorage.setItem('se_month', '4100'); // > 80% of 5000
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    runScriptWithAttrs({
      'data-sentry-dsn': 'https://abc@sentry.io/1',
      'data-production-host': 'localhost',
      'data-allowed-hosts': 'localhost',
    });
    const { beforeSend } = sentryInit.mock.calls[0][0];
    beforeSend({ message: 'dev-warn' }, {});
    expect(warnSpy).toHaveBeenCalledWith(
      '[Sentry] Monthly event limit warning:',
      expect.any(Number),
      '/',
      5000
    );
    warnSpy.mockRestore();
  });

  it('does not crash beforeSend when incrementMonthly()s localStorage.setItem throws', () => {
    runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
    const { beforeSend } = sentryInit.mock.calls[0][0];
    const setSpy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('quota exceeded');
    });
    let result;
    expect(() => {
      result = beforeSend({ message: 'increment-throws' }, {});
    }).not.toThrow();
    expect(result).toEqual({ message: 'increment-throws' });
    setSpy.mockRestore();
  });

  // =========================================================================
  // beforeBreadcrumb()
  // =========================================================================

  describe('beforeBreadcrumb', () => {
    it('drops breadcrumbs when the host/environment gate fails', () => {
      setHostname('my-branch.vercel.app');
      runScriptWithAttrs({
        'data-sentry-dsn': 'https://abc@sentry.io/1',
        'data-allowed-hosts': 'my-branch.vercel.app',
      });
      const { beforeBreadcrumb } = sentryInit.mock.calls[0][0];
      expect(beforeBreadcrumb({ category: 'xhr' })).toBeNull();
    });

    it('drops console.log breadcrumbs', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeBreadcrumb } = sentryInit.mock.calls[0][0];
      expect(beforeBreadcrumb({ category: 'console', level: 'log' })).toBeNull();
    });

    it('keeps console breadcrumbs that are not level "log"', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeBreadcrumb } = sentryInit.mock.calls[0][0];
      const crumb = { category: 'console', level: 'warn', message: 'ok' };
      expect(beforeBreadcrumb(crumb)).toBe(crumb);
    });

    it('drops breadcrumbs whose message looks sensitive', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeBreadcrumb } = sentryInit.mock.calls[0][0];
      expect(beforeBreadcrumb({ category: 'xhr', message: 'Authorization: Bearer xyz' })).toBeNull();
    });

    it('keeps breadcrumbs with a non-sensitive message', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeBreadcrumb } = sentryInit.mock.calls[0][0];
      const crumb = { category: 'ui.click', message: 'button clicked' };
      expect(beforeBreadcrumb(crumb)).toBe(crumb);
    });

    it('keeps breadcrumbs with no message at all', () => {
      runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
      const { beforeBreadcrumb } = sentryInit.mock.calls[0][0];
      const crumb = { category: 'navigation' };
      expect(beforeBreadcrumb(crumb)).toBe(crumb);
    });
  });

  // =========================================================================
  // window 'error' listener
  // =========================================================================

  describe('window error listener', () => {
    it('does not capture when not in production', () => {
      setHostname('my-branch.vercel.app');
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({
          'data-sentry-dsn': 'https://abc@sentry.io/1',
          'data-allowed-hosts': 'my-branch.vercel.app',
        });
        const [errorHandler] = listeners.error;
        errorHandler({ message: 'boom' });
        expect(sentryCaptureException).not.toHaveBeenCalled();
      } finally {
        restore();
      }
    });

    it('does not capture when Sentry has been removed from the global', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [errorHandler] = listeners.error;
        delete window.Sentry;
        expect(() => errorHandler({ message: 'boom' })).not.toThrow();
        expect(sentryCaptureException).not.toHaveBeenCalled();
      } finally {
        restore();
      }
    });

    it('skips errors already captured (__sentry_captured__)', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [errorHandler] = listeners.error;
        errorHandler({ error: { __sentry_captured__: true } });
        expect(sentryCaptureException).not.toHaveBeenCalled();
      } finally {
        restore();
      }
    });

    it('captures a fresh error and tags it as global_error', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [errorHandler] = listeners.error;
        const err = new Error('boom');
        errorHandler({ error: err, filename: 'app.js', lineno: 10, colno: 5 });
        expect(sentryCaptureException).toHaveBeenCalledTimes(1);
        expect(sentryCaptureException.mock.calls[0][0]).toBe(err);
        expect(sentryCaptureException.mock.calls[0][1]).toMatchObject({
          tags: { errorType: 'global_error', handled: false },
          extra: { filename: 'app.js', lineno: 10, colno: 5 },
        });
      } finally {
        restore();
      }
    });

    it('builds a new Error from event.message when event.error is absent', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [errorHandler] = listeners.error;
        errorHandler({ message: 'plain message error' });
        expect(sentryCaptureException).toHaveBeenCalledTimes(1);
        expect(sentryCaptureException.mock.calls[0][0].message).toBe('plain message error');
      } finally {
        restore();
      }
    });

    it('defaults to "Unknown error" and unknown/0 extras when nothing is provided', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [errorHandler] = listeners.error;
        errorHandler({});
        expect(sentryCaptureException).toHaveBeenCalledTimes(1);
        expect(sentryCaptureException.mock.calls[0][0].message).toBe('Unknown error');
        expect(sentryCaptureException.mock.calls[0][1].extra).toEqual({
          filename: 'unknown',
          lineno: 0,
          colno: 0,
        });
      } finally {
        restore();
      }
    });
  });

  // =========================================================================
  // window 'unhandledrejection' listener
  // =========================================================================

  describe('window unhandledrejection listener', () => {
    it('does not capture when not in production', () => {
      setHostname('my-branch.vercel.app');
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({
          'data-sentry-dsn': 'https://abc@sentry.io/1',
          'data-allowed-hosts': 'my-branch.vercel.app',
        });
        const [handler] = listeners.unhandledrejection;
        handler({ reason: new Error('nope') });
        expect(sentryCaptureException).not.toHaveBeenCalled();
      } finally {
        restore();
      }
    });

    it('does not capture when Sentry has been removed from the global', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [handler] = listeners.unhandledrejection;
        delete window.Sentry;
        expect(() => handler({ reason: new Error('nope') })).not.toThrow();
        expect(sentryCaptureException).not.toHaveBeenCalled();
      } finally {
        restore();
      }
    });

    it('skips rejections already captured (__sentry_captured__)', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [handler] = listeners.unhandledrejection;
        handler({ reason: { __sentry_captured__: true } });
        expect(sentryCaptureException).not.toHaveBeenCalled();
      } finally {
        restore();
      }
    });

    it('skips rejections whose default was prevented', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [handler] = listeners.unhandledrejection;
        handler({ reason: new Error('nope'), defaultPrevented: true });
        expect(sentryCaptureException).not.toHaveBeenCalled();
      } finally {
        restore();
      }
    });

    it('captures an Error reason directly, tagged as unhandled_promise_rejection', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [handler] = listeners.unhandledrejection;
        const reason = new Error('rejected');
        handler({ reason });
        expect(sentryCaptureException).toHaveBeenCalledTimes(1);
        expect(sentryCaptureException.mock.calls[0][0]).toBe(reason);
        expect(sentryCaptureException.mock.calls[0][1]).toMatchObject({
          tags: { errorType: 'unhandled_promise_rejection', handled: false },
        });
      } finally {
        restore();
      }
    });

    it('wraps a non-Error reason in a new Error via String()', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [handler] = listeners.unhandledrejection;
        handler({ reason: 'plain string reason' });
        expect(sentryCaptureException).toHaveBeenCalledTimes(1);
        expect(sentryCaptureException.mock.calls[0][0].message).toBe('plain string reason');
      } finally {
        restore();
      }
    });

    it('defaults the message when reason is falsy', () => {
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [handler] = listeners.unhandledrejection;
        handler({ reason: undefined });
        expect(sentryCaptureException).toHaveBeenCalledTimes(1);
        expect(sentryCaptureException.mock.calls[0][0].message).toBe('Unhandled Promise Rejection');
      } finally {
        restore();
      }
    });
  });

  // =========================================================================
  // Top-level: deferred init via 'load' listener when Sentry loads late
  // =========================================================================

  describe('deferred initialization via load event', () => {
    it('registers a load listener and initializes once Sentry becomes available', () => {
      delete window.Sentry;
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        expect(sentryInit).not.toHaveBeenCalled();
        window.Sentry = { init: sentryInit, captureException: sentryCaptureException };
        const [loadHandler] = listeners.load;
        loadHandler();
        expect(sentryInit).toHaveBeenCalledTimes(1);
      } finally {
        restore();
      }
    });

    it('does nothing on load if Sentry is still unavailable', () => {
      delete window.Sentry;
      const { listeners, restore } = captureListeners();
      try {
        runScriptWithAttrs({ 'data-sentry-dsn': 'https://abc@sentry.io/1' });
        const [loadHandler] = listeners.load;
        loadHandler();
        expect(sentryInit).not.toHaveBeenCalled();
      } finally {
        restore();
      }
    });
  });
});
