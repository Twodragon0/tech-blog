// Regression tests for assets/js/performance-monitor.js
//
// performance-monitor.js loads from `_includes/performance-monitor.html`
// on every page (production only). It registers PerformanceObservers
// for Long Task / LCP / FID / CLS / Resource and flushes a Long-Task
// count to `Sentry.metrics.distribution` on `beforeunload`.
//
// We run the script against a synthetic `window` whose `location.hostname`
// matches the production canonical so the localhost early-exit doesn't
// trip. The PerformanceObserver constructor is stubbed (jsdom 29 lacks
// it) and we capture the `entryTypes` arg of each `observe()` call so
// we can assert the full set of observers landed.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/performance-monitor.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

// Test harness:
// - The script does `if ('PerformanceObserver' in window) ... new PerformanceObserver(cb)`
//   and `if (typeof Sentry !== 'undefined') ...`. Both symbols are read
//   from the GLOBAL scope when evaluated inside `new Function(...)`, not
//   from the `window` parameter, so we stub them on globalThis.
// - The script also reads `window.location.hostname` and registers
//   listeners via `window.addEventListener`. Those go through the fake
//   `window` arg we hand to `new Function`.

function setupPerformanceObserverStub() {
  const observed = [];
  class StubPerformanceObserver {
    constructor(cb) {
      this._cb = cb;
      observed.push(this);
    }
    observe(opts) {
      this.entryTypes = (opts && opts.entryTypes) || [];
    }
    disconnect() {}
  }
  // The script does BOTH `'PerformanceObserver' in window` (against the
  // param) AND `new PerformanceObserver(...)` (resolved from the global
  // scope chain). We need the symbol in both places.
  vi.stubGlobal('PerformanceObserver', StubPerformanceObserver);
  return { observed, ctor: StubPerformanceObserver };
}

function buildFakeWindow({
  hostname = 'tech.2twodragon.com',
  PerformanceObserver = undefined,
} = {}) {
  const listeners = [];
  const fake = {
    addEventListener: vi.fn((evt, handler, opts) => {
      listeners.push({ evt, handler, opts });
    }),
    location: { hostname, pathname: '/posts/foo/' },
  };
  if (PerformanceObserver) {
    fake.PerformanceObserver = PerformanceObserver;
  }
  return { fake, listeners };
}

function runScript(fakeWindow) {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(fakeWindow, document);
}

describe('performance-monitor.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('bails on localhost (no PerformanceObserver instances created)', () => {
    const { observed, ctor } = setupPerformanceObserverStub();
    const { fake } = buildFakeWindow({ hostname: 'localhost', PerformanceObserver: ctor });
    runScript(fake);
    expect(observed).toHaveLength(0);
    expect(fake.addEventListener).not.toHaveBeenCalled();
  });

  it('bails on 127.0.0.1 (no observers, no listeners)', () => {
    const { observed, ctor } = setupPerformanceObserverStub();
    const { fake, listeners } = buildFakeWindow({ hostname: '127.0.0.1', PerformanceObserver: ctor });
    runScript(fake);
    expect(observed).toHaveLength(0);
    expect(listeners).toHaveLength(0);
  });

  it('on production: registers observers for the 5 web-vitals entryTypes', () => {
    const { observed, ctor } = setupPerformanceObserverStub();
    const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
    runScript(fake);

    // Five PerformanceObserver instances: Long Task, LCP, FID, CLS, Resource.
    expect(observed.length).toBeGreaterThanOrEqual(5);

    const allTypes = observed.flatMap((o) => o.entryTypes || []);
    expect(allTypes).toEqual(
      expect.arrayContaining([
        'longtask',
        'largest-contentful-paint',
        'first-input',
        'layout-shift',
        'resource',
      ]),
    );
  });

  it('on production: registers a beforeunload listener that flushes Long-Task metric to Sentry', () => {
    const distribution = vi.fn();
    vi.stubGlobal('Sentry', { metrics: { distribution } });
    const { observed, ctor } = setupPerformanceObserverStub();
    const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
    runScript(fake);

    // Feed 3 long-task entries to the long-task observer.
    const longTaskObserver = observed.find((o) =>
      (o.entryTypes || []).includes('longtask'),
    );
    longTaskObserver._cb({
      getEntries: () => [{ duration: 60 }, { duration: 75 }, { duration: 90 }],
    });

    const beforeunload = listeners.find((l) => l.evt === 'beforeunload');
    expect(beforeunload).toBeDefined();
    beforeunload.handler();

    expect(distribution).toHaveBeenCalledTimes(1);
    expect(distribution.mock.calls[0][0]).toBe('longtask.count');
    expect(distribution.mock.calls[0][1]).toBe(3);
    expect(distribution.mock.calls[0][2]).toEqual(
      expect.objectContaining({
        unit: 'none',
        tags: expect.objectContaining({ page: '/posts/foo/' }),
      }),
    );
  });

  it('beforeunload no-op when Sentry.metrics is missing', () => {
    // Sentry exists but without the metrics namespace — must not throw.
    vi.stubGlobal('Sentry', { captureException: vi.fn() });
    const { observed, ctor } = setupPerformanceObserverStub();
    const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
    runScript(fake);

    const longTaskObserver = observed.find((o) =>
      (o.entryTypes || []).includes('longtask'),
    );
    longTaskObserver._cb({ getEntries: () => [{ duration: 60 }] });

    const beforeunload = listeners.find((l) => l.evt === 'beforeunload');
    expect(() => beforeunload.handler()).not.toThrow();
  });

  it('beforeunload no-op when longTaskCount stayed at 0 (no entries observed)', () => {
    const distribution = vi.fn();
    vi.stubGlobal('Sentry', { metrics: { distribution } });
    const { ctor } = setupPerformanceObserverStub();
    const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
    runScript(fake);
    // Never feed the long-task observer any entries.
    const beforeunload = listeners.find((l) => l.evt === 'beforeunload');
    beforeunload.handler();
    expect(distribution).not.toHaveBeenCalled();
  });

  it('beforeunload no-op when Sentry global is entirely undefined', () => {
    // Deliberately do NOT stub Sentry at all.
    const { observed, ctor } = setupPerformanceObserverStub();
    const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
    runScript(fake);
    const longTaskObserver = observed.find((o) =>
      (o.entryTypes || []).includes('longtask'),
    );
    longTaskObserver._cb({ getEntries: () => [{ duration: 60 }] });
    const beforeunload = listeners.find((l) => l.evt === 'beforeunload');
    expect(() => beforeunload.handler()).not.toThrow();
  });

  // ---------------------------------------------------------------------
  // Failing-observer helper: lets a specific `entryTypes` request throw
  // from `.observe()`, which is what drives each `catch (e) { ... }` block
  // in the source (LCP / FID / CLS / Resource all wrap `new
  // PerformanceObserver(...).observe(...)` in the same try).
  // ---------------------------------------------------------------------
  function setupObserverStubWithFailures(failEntryTypes = []) {
    const observed = [];
    class FailingPerformanceObserver {
      constructor(cb) {
        this._cb = cb;
        observed.push(this);
      }
      observe(opts) {
        const types = (opts && opts.entryTypes) || [];
        if (types.some((t) => failEntryTypes.includes(t))) {
          throw new Error('entry type not supported: ' + types.join(','));
        }
        this.entryTypes = types;
      }
      disconnect() {}
    }
    vi.stubGlobal('PerformanceObserver', FailingPerformanceObserver);
    return { observed, ctor: FailingPerformanceObserver };
  }

  function getObserverByType(observed, type) {
    return observed.find((o) => (o.entryTypes || []).includes(type));
  }

  describe('LCP observer callback branches', () => {
    it('no entries at all: lastEntry is undefined, no warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const lcp = getObserverByType(observed, 'largest-contentful-paint');
      expect(() => lcp._cb({ getEntries: () => [] })).not.toThrow();
      expect(warn).not.toHaveBeenCalled();
    });

    it('lastEntry present but missing renderTime: no warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const lcp = getObserverByType(observed, 'largest-contentful-paint');
      lcp._cb({ getEntries: () => [{ startTime: 100 }] });
      expect(warn).not.toHaveBeenCalled();
    });

    it('renderTime under the 4000ms threshold: no warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const lcp = getObserverByType(observed, 'largest-contentful-paint');
      lcp._cb({ getEntries: () => [{ renderTime: 2500 }] });
      expect(warn).not.toHaveBeenCalled();
    });

    it('renderTime over the 4000ms threshold: logs a slow-LCP warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const lcp = getObserverByType(observed, 'largest-contentful-paint');
      lcp._cb({ getEntries: () => [{ renderTime: 5200 }] });
      expect(warn).toHaveBeenCalledWith('[Performance] LCP is slow:', '5200ms');
    });

    it('LCP observer unsupported: catch reports to Sentry on the production host', () => {
      const captureException = vi.fn();
      vi.stubGlobal('Sentry', { captureException });
      const { ctor } = setupObserverStubWithFailures(['largest-contentful-paint']);
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
      expect(captureException).toHaveBeenCalledTimes(1);
      expect(captureException.mock.calls[0][1]).toEqual(
        expect.objectContaining({ tags: { errorType: 'performance_monitor_lcp' } }),
      );
    });

    it('LCP observer unsupported: does NOT report to Sentry off the production host', () => {
      const captureException = vi.fn();
      vi.stubGlobal('Sentry', { captureException });
      const { ctor } = setupObserverStubWithFailures(['largest-contentful-paint']);
      const { fake } = buildFakeWindow({ hostname: 'staging.example.com', PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
      expect(captureException).not.toHaveBeenCalled();
    });

    it('LCP observer unsupported: does NOT throw when Sentry is undefined', () => {
      const { ctor } = setupObserverStubWithFailures(['largest-contentful-paint']);
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
    });

    it('LCP observer unsupported: does NOT throw when Sentry lacks captureException', () => {
      vi.stubGlobal('Sentry', {});
      const { ctor } = setupObserverStubWithFailures(['largest-contentful-paint']);
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
    });
  });

  describe('FID observer callback branches', () => {
    it('processingStart - startTime under 800ms: no warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const fid = getObserverByType(observed, 'first-input');
      const entries = [{ startTime: 100, processingStart: 300 }];
      fid._cb({ getEntries: () => entries });
      expect(warn).not.toHaveBeenCalled();
    });

    it('processingStart - startTime over 800ms: logs a slow-FID warning per entry', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const fid = getObserverByType(observed, 'first-input');
      const entries = [
        { startTime: 0, processingStart: 900 }, // slow
        { startTime: 0, processingStart: 400 }, // fast
      ];
      fid._cb({ getEntries: () => entries });
      expect(warn).toHaveBeenCalledTimes(1);
      expect(warn).toHaveBeenCalledWith('[Performance] FID is slow:', '900ms');
    });

    it('FID observer unsupported: catch reports to Sentry on the production host', () => {
      const captureException = vi.fn();
      vi.stubGlobal('Sentry', { captureException });
      const { ctor } = setupObserverStubWithFailures(['first-input']);
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
      expect(captureException).toHaveBeenCalledTimes(1);
      expect(captureException.mock.calls[0][1]).toEqual(
        expect.objectContaining({ tags: { errorType: 'performance_monitor_fid' } }),
      );
    });

    it('FID observer unsupported: does NOT report to Sentry off the production host', () => {
      const captureException = vi.fn();
      vi.stubGlobal('Sentry', { captureException });
      const { ctor } = setupObserverStubWithFailures(['first-input']);
      const { fake } = buildFakeWindow({ hostname: 'staging.example.com', PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
      expect(captureException).not.toHaveBeenCalled();
    });
  });

  describe('CLS observer callback branches (analyzeCLSCause)', () => {
    it('entries with hadRecentInput=true are ignored entirely', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({ getEntries: () => [{ hadRecentInput: true, value: 5 }] });
      expect(warn).not.toHaveBeenCalled();
    });

    it('no sources on the entry: cause resolves to "unknown"', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [{ hadRecentInput: false, value: 0.2, startTime: 10 }],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'unknown',
      );
    });

    it('source with no .node: cause still resolves to "unknown"', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          { hadRecentInput: false, value: 0.2, sources: [{ node: null }] },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'unknown',
      );
    });

    it('IMG tagName source: attributes an "Image:" cause using src', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          {
            hadRecentInput: false,
            value: 0.2,
            sources: [{ node: { tagName: 'IMG', src: '/hero.png', className: '' } }],
          },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'Image: /hero.png',
      );
    });

    it('non-IMG element with className containing "img": still an Image cause via getAttribute fallback', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          {
            hadRecentInput: false,
            value: 0.2,
            sources: [
              {
                node: {
                  tagName: 'SPAN',
                  className: 'lazy-img',
                  getAttribute: (attr) => (attr === 'src' ? '/lazy.png' : null),
                },
              },
            ],
          },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'Image: /lazy.png',
      );
    });

    it('IFRAME tagName source: attributes an "Ad:" cause using src', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          {
            hadRecentInput: false,
            value: 0.2,
            sources: [{ node: { tagName: 'IFRAME', src: '/ads/slot1', className: '' } }],
          },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'Ad: /ads/slot1',
      );
    });

    it('non-IFRAME element with className "adsbygoogle": attributes an "Ad:" cause via className', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          {
            hadRecentInput: false,
            value: 0.2,
            sources: [{ node: { tagName: 'INS', className: 'adsbygoogle' } }],
          },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'Ad: adsbygoogle',
      );
    });

    it('DIV with className containing "card": attributes a "Card:" cause', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          {
            hadRecentInput: false,
            value: 0.2,
            sources: [{ node: { tagName: 'DIV', className: 'post-card' } }],
          },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'Card: post-card',
      );
    });

    it('SCRIPT tagName source: attributes a "Script insertion" cause', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          { hadRecentInput: false, value: 0.2, sources: [{ node: { tagName: 'SCRIPT' } }] },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'Script insertion',
      );
    });

    it('generic element source: falls back to tagName#id.class', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          {
            hadRecentInput: false,
            value: 0.2,
            sources: [{ node: { tagName: 'SECTION', id: 'hero', className: 'wrapper extra' } }],
          },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'SECTION#hero.wrapper',
      );
    });

    it('generic element with SVG-style className object (.baseVal): still classifies via baseVal string', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          {
            hadRecentInput: false,
            value: 0.2,
            sources: [{ node: { tagName: 'svg', className: { baseVal: 'ad-banner' } } }],
          },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'Ad: ad-banner',
      );
    });

    it('className object without baseVal falls back to toString()', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          {
            hadRecentInput: false,
            value: 0.2,
            sources: [
              {
                node: {
                  tagName: 'SECTION',
                  id: '',
                  className: { toString: () => 'wrap-only' },
                },
              },
            ],
          },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'SECTION.wrap-only',
      );
    });

    it('multiple sources join into one comma-separated cause string', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({
        getEntries: () => [
          {
            hadRecentInput: false,
            value: 0.2,
            sources: [
              { node: { tagName: 'IMG', src: '/a.png', className: '' } },
              { node: { tagName: 'SCRIPT' } },
            ],
          },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] CLS is high:',
        expect.any(String),
        '| Cause:',
        'Image: /a.png, Script insertion',
      );
    });

    it('clsValue under the 0.1 threshold: no warning at all', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({ getEntries: () => [{ hadRecentInput: false, value: 0.02 }] });
      expect(warn).not.toHaveBeenCalled();
    });

    it('cumulative clsValue exceeding 0.25 triggers a console.error on beforeunload', () => {
      vi.spyOn(console, 'warn').mockImplementation(() => {});
      const error = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({ getEntries: () => [{ hadRecentInput: false, value: 0.3 }] });
      const beforeunload = listeners.find(
        (l) => l.evt === 'beforeunload' && l !== undefined,
      );
      // Two beforeunload listeners are registered (long-task + CLS); fire both.
      listeners.filter((l) => l.evt === 'beforeunload').forEach((l) => l.handler());
      expect(error).toHaveBeenCalledWith('[Performance] CLS is very high:', '0.300000');
      expect(beforeunload).toBeDefined();
    });

    it('cumulative clsValue at/under 0.25 does NOT trigger console.error on beforeunload', () => {
      vi.spyOn(console, 'warn').mockImplementation(() => {});
      const error = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const cls = getObserverByType(observed, 'layout-shift');
      cls._cb({ getEntries: () => [{ hadRecentInput: false, value: 0.05 }] });
      listeners.filter((l) => l.evt === 'beforeunload').forEach((l) => l.handler());
      expect(error).not.toHaveBeenCalled();
    });

    it('CLS observer unsupported: catch reports to Sentry on the production host', () => {
      const captureException = vi.fn();
      vi.stubGlobal('Sentry', { captureException });
      const { ctor } = setupObserverStubWithFailures(['layout-shift']);
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
      expect(captureException).toHaveBeenCalledTimes(1);
      expect(captureException.mock.calls[0][1]).toEqual(
        expect.objectContaining({ tags: { errorType: 'performance_monitor_cls' } }),
      );
    });

    it('CLS observer unsupported: does NOT report to Sentry off the production host', () => {
      const captureException = vi.fn();
      vi.stubGlobal('Sentry', { captureException });
      const { ctor } = setupObserverStubWithFailures(['layout-shift']);
      const { fake } = buildFakeWindow({ hostname: 'staging.example.com', PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
      expect(captureException).not.toHaveBeenCalled();
    });
  });

  describe('Resource observer callback branches', () => {
    it('non-API resource over the 3000ms threshold: logs a slow-resource warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const resource = getObserverByType(observed, 'resource');
      resource._cb({
        getEntries: () => [
          { name: '/assets/big.js', duration: 4000, initiatorType: 'script' },
        ],
      });
      expect(warn).toHaveBeenCalledWith(
        '[Performance] Slow resource:',
        '/assets/big.js',
        '4000ms',
      );
    });

    it('non-API resource under the 3000ms threshold: no warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const resource = getObserverByType(observed, 'resource');
      resource._cb({
        getEntries: () => [
          { name: '/assets/small.js', duration: 100, initiatorType: 'script' },
        ],
      });
      expect(warn).not.toHaveBeenCalled();
    });

    it('API resource over the 8000ms threshold: no warning (API requests are silent)', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const resource = getObserverByType(observed, 'resource');
      resource._cb({
        getEntries: () => [
          { name: '/api/collect-news', duration: 9000, initiatorType: 'fetch' },
        ],
      });
      expect(warn).not.toHaveBeenCalled();
    });

    it('API resource under its 8000ms threshold: no warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const resource = getObserverByType(observed, 'resource');
      resource._cb({
        getEntries: () => [
          { name: '/api/tags', duration: 500, initiatorType: 'fetch' },
        ],
      });
      expect(warn).not.toHaveBeenCalled();
    });

    it('navigation-initiated entries are exempt even over threshold', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { observed, ctor } = setupPerformanceObserverStub();
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const resource = getObserverByType(observed, 'resource');
      resource._cb({
        getEntries: () => [
          { name: '/posts/foo/', duration: 5000, initiatorType: 'navigation' },
        ],
      });
      expect(warn).not.toHaveBeenCalled();
    });

    it('Resource observer unsupported: catch reports to Sentry on the production host', () => {
      const captureException = vi.fn();
      vi.stubGlobal('Sentry', { captureException });
      const { ctor } = setupObserverStubWithFailures(['resource']);
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
      expect(captureException).toHaveBeenCalledTimes(1);
      expect(captureException.mock.calls[0][1]).toEqual(
        expect.objectContaining({ tags: { errorType: 'performance_monitor_resource' } }),
      );
    });

    it('Resource observer unsupported: does NOT report to Sentry off the production host', () => {
      const captureException = vi.fn();
      vi.stubGlobal('Sentry', { captureException });
      const { ctor } = setupObserverStubWithFailures(['resource']);
      const { fake } = buildFakeWindow({ hostname: 'staging.example.com', PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
      expect(captureException).not.toHaveBeenCalled();
    });
  });

  describe('Long Task observer unsupported (outer try/catch, silently ignored)', () => {
    it('does not throw and web-vitals observers still register when longtask.observe() throws', () => {
      const { observed, ctor } = setupObserverStubWithFailures(['longtask']);
      const { fake } = buildFakeWindow({ PerformanceObserver: ctor });
      expect(() => runScript(fake)).not.toThrow();
      // LCP/FID/CLS/Resource observers should still have been constructed
      // even though the long-task observer's `.observe()` threw.
      const allTypes = observed.flatMap((o) => o.entryTypes || []);
      expect(allTypes).toEqual(
        expect.arrayContaining([
          'largest-contentful-paint',
          'first-input',
          'layout-shift',
          'resource',
        ]),
      );
    });
  });

  describe('Page load monitoring ("load" listener)', () => {
    it('no navigation entries available: nothing is logged', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      vi.spyOn(performance, 'getEntriesByType').mockReturnValue([]);
      const { ctor } = setupPerformanceObserverStub();
      const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const load = listeners.find((l) => l.evt === 'load');
      expect(() => load.handler()).not.toThrow();
      expect(warn).not.toHaveBeenCalled();
    });

    it('slow page load (>3000ms, <60000ms): logs a page-load warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      vi.spyOn(performance, 'getEntriesByType').mockReturnValue([
        { loadEventEnd: 4200, domContentLoadedEventEnd: 1000 },
      ]);
      const { ctor } = setupPerformanceObserverStub();
      const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const load = listeners.find((l) => l.evt === 'load');
      load.handler();
      expect(warn).toHaveBeenCalledWith('[Performance] Page load is slow:', '4200ms');
    });

    it('fast page load (<=3000ms): no page-load warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      vi.spyOn(performance, 'getEntriesByType').mockReturnValue([
        { loadEventEnd: 1200, domContentLoadedEventEnd: 800 },
      ]);
      const { ctor } = setupPerformanceObserverStub();
      const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const load = listeners.find((l) => l.evt === 'load');
      load.handler();
      expect(warn).not.toHaveBeenCalled();
    });

    it('bogus load time (>=60000ms) is ignored (guards against broken timers)', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      vi.spyOn(performance, 'getEntriesByType').mockReturnValue([
        { loadEventEnd: 70000, domContentLoadedEventEnd: 800 },
      ]);
      const { ctor } = setupPerformanceObserverStub();
      const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const load = listeners.find((l) => l.evt === 'load');
      load.handler();
      expect(warn).not.toHaveBeenCalled();
    });

    it('slow DOM ready (>5000ms, <60000ms): logs a dom-ready warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      vi.spyOn(performance, 'getEntriesByType').mockReturnValue([
        { loadEventEnd: 1000, domContentLoadedEventEnd: 6500 },
      ]);
      const { ctor } = setupPerformanceObserverStub();
      const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const load = listeners.find((l) => l.evt === 'load');
      load.handler();
      expect(warn).toHaveBeenCalledWith('[Performance] DOM ready is slow:', '6500ms');
    });

    it('fast DOM ready (<=5000ms): no dom-ready warning', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      vi.spyOn(performance, 'getEntriesByType').mockReturnValue([
        { loadEventEnd: 1000, domContentLoadedEventEnd: 2000 },
      ]);
      const { ctor } = setupPerformanceObserverStub();
      const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const load = listeners.find((l) => l.evt === 'load');
      load.handler();
      expect(warn).not.toHaveBeenCalled();
    });

    it('performance.getEntriesByType throwing is swallowed silently', () => {
      vi.spyOn(performance, 'getEntriesByType').mockImplementation(() => {
        throw new Error('boom');
      });
      const { ctor } = setupPerformanceObserverStub();
      const { fake, listeners } = buildFakeWindow({ PerformanceObserver: ctor });
      runScript(fake);
      const load = listeners.find((l) => l.evt === 'load');
      expect(() => load.handler()).not.toThrow();
    });
  });
});
