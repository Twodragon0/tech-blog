// Shared fixture helpers for tests/js vitest suite.
//
// Provides three stubs that jsdom 29 lacks and that multiple test files need:
//   - stubIntersectionObserver() — installs window.IntersectionObserver with a
//     _trigger(target) helper to manually fire intersection callbacks in tests.
//   - stubFetch(json, opts) — returns a vi.fn() resolving to a fake Response.
//   - stubPerformanceObserver() — installs window.PerformanceObserver (ready for
//     performance-monitor.test.js in round 3 step 3; not yet used by this PR).
//
// Usage pattern:
//   import { stubIntersectionObserver, stubFetch } from './_fixtures.js';
//   beforeEach(() => { stubIntersectionObserver(); window.fetch = stubFetch({...}); });
//   afterEach(() => { delete window.IntersectionObserver; delete window.fetch; });

import { vi } from 'vitest';

/**
 * Installs a minimal IntersectionObserver stub on window.
 *
 * Each constructed instance exposes a `_trigger(target, isIntersecting = true)`
 * method so tests can manually fire the observer callback without real scroll.
 *
 * @returns {Function} restore — call in afterEach to remove the stub.
 */
export function stubIntersectionObserver() {
  const original = window.IntersectionObserver;

  class StubIntersectionObserver {
    constructor(cb, _opts) {
      this._cb = cb;
      this._observed = new Set();
    }
    observe(target) { this._observed.add(target); }
    unobserve(target) { this._observed.delete(target); }
    disconnect() { this._observed.clear(); }
    /** Manually fire the callback as if `target` scrolled into view. */
    _trigger(target, isIntersecting = true) {
      this._cb([{ isIntersecting, target }], this);
    }
  }

  window.IntersectionObserver = StubIntersectionObserver;
  return function restore() {
    if (original === undefined) {
      delete window.IntersectionObserver;
    } else {
      window.IntersectionObserver = original;
    }
  };
}

/**
 * Returns a vi.fn() that simulates window.fetch returning the given JSON.
 *
 * @param {*}       json             — The value returned by response.json().
 * @param {object}  [opts]
 * @param {boolean} [opts.ok=true]   — Whether response.ok is true.
 * @param {boolean} [opts.throws=false] — If true the fetch promise rejects.
 * @returns {import('vitest').MockInstance}
 */
export function stubFetch(json, { ok = true, throws = false } = {}) {
  if (throws) {
    return vi.fn(() => Promise.reject(new Error('Network error')));
  }
  return vi.fn(() =>
    Promise.resolve({
      ok,
      status: ok ? 200 : 500,
      json: () => Promise.resolve(json),
    })
  );
}

/**
 * Installs a minimal PerformanceObserver stub on window.
 *
 * Exposes `window.__perfObservers` so tests can flush metrics manually.
 * Includes a static `supportedEntryTypes` array matching common entry types.
 *
 * @returns {Function} restore — call in afterEach to remove the stub.
 */
export function stubPerformanceObserver() {
  const original = window.PerformanceObserver;
  const observers = [];

  class StubPerformanceObserver {
    constructor(cb) {
      this._cb = cb;
      observers.push(this);
    }
    observe(_opts) {}
    disconnect() {}
  }
  StubPerformanceObserver.supportedEntryTypes = [
    'largest-contentful-paint',
    'first-input',
    'layout-shift',
    'longtask',
  ];

  window.PerformanceObserver = StubPerformanceObserver;
  window.__perfObservers = observers;

  return function restore() {
    delete window.__perfObservers;
    if (original === undefined) {
      delete window.PerformanceObserver;
    } else {
      window.PerformanceObserver = original;
    }
  };
}
