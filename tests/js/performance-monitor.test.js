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
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/performance-monitor.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

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
});
