// Regression tests for assets/js/error-handler.js
//
// Pattern follows tests/js/ad-optimizer.test.js (PR #337). The script is
// an IIFE that registers three `window.addEventListener` listeners
// ('error', 'unhandledrejection', 'error' for resource failures) and
// rate-limits forwarded errors to a Sentry transport at 10/minute.
//
// The script early-exits on `localhost`/`127.0.0.1` hosts, so we run it
// against a synthetic `window` whose `location.hostname` matches the
// production canonical (`tech.2twodragon.com`). This lets us spy on the
// listener registration calls and on `Sentry.captureException` directly,
// without needing to dispatch real DOM events.

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/error-handler.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function buildFakeWindow({ hostname = 'tech.2twodragon.com', sentry = null } = {}) {
  const listeners = []; // captured (event, handler, useCapture)
  const fake = {
    addEventListener: vi.fn((evt, handler, capture) => {
      listeners.push({ evt, handler, capture });
    }),
    location: {
      hostname,
      href: `https://${hostname}/posts/foo/`,
    },
    Sentry: sentry,
  };
  return { fake, listeners };
}

function runScript(fakeWindow) {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(fakeWindow, document);
}

describe('error-handler.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('bails on localhost (no listeners registered)', () => {
    const { fake } = buildFakeWindow({ hostname: 'localhost' });
    runScript(fake);
    expect(fake.addEventListener).not.toHaveBeenCalled();
  });

  it('bails on 127.0.0.1 (no listeners registered)', () => {
    const { fake } = buildFakeWindow({ hostname: '127.0.0.1' });
    runScript(fake);
    expect(fake.addEventListener).not.toHaveBeenCalled();
  });

  it('registers error + unhandledrejection + resource-error listeners on production host', () => {
    const { fake, listeners } = buildFakeWindow();
    runScript(fake);
    const events = listeners.map((l) => l.evt).sort();
    // Two 'error' listeners (one for runtime errors, one for resource-load
    // failures) + one 'unhandledrejection'.
    expect(events).toEqual(['error', 'error', 'unhandledrejection']);
    // All listeners use the capture phase (per the script's third arg).
    expect(listeners.every((l) => l.capture === true)).toBe(true);
  });

  it('forwards a runtime error to Sentry.captureException', () => {
    const captureException = vi.fn();
    const { fake, listeners } = buildFakeWindow({ sentry: { captureException } });
    // Override hostname to match the script's prod-only Sentry gate.
    fake.location.hostname = 'tech.2twodragon.com';
    runScript(fake);
    const errorListener = listeners.find((l) => l.evt === 'error').handler;
    errorListener({
      message: 'boom',
      filename: 'https://tech.2twodragon.com/assets/js/foo.js',
      error: new Error('boom'),
      lineno: 12,
      colno: 4,
    });
    expect(captureException).toHaveBeenCalledTimes(1);
    expect(captureException.mock.calls[0][0].message).toBe('boom');
  });

  it('rate-limits at 10 errors/minute (11th call is dropped)', () => {
    const captureException = vi.fn();
    const { fake, listeners } = buildFakeWindow({ sentry: { captureException } });
    runScript(fake);
    const errorListener = listeners.find((l) => l.evt === 'error').handler;
    for (let i = 0; i < 12; i++) {
      errorListener({
        message: `boom-${i}`,
        filename: 'https://tech.2twodragon.com/assets/js/foo.js',
        error: new Error(`boom-${i}`),
      });
    }
    // First 10 forwarded, 11th + 12th dropped (memory protection).
    expect(captureException).toHaveBeenCalledTimes(10);
  });

  it('ignores errors from external (cross-origin) scripts', () => {
    const captureException = vi.fn();
    const { fake, listeners } = buildFakeWindow({ sentry: { captureException } });
    runScript(fake);
    const errorListener = listeners.find((l) => l.evt === 'error').handler;
    errorListener({
      message: 'External script error',
      filename: 'https://cdn.example.com/third-party.js', // different host
      error: new Error('external'),
    });
    expect(captureException).not.toHaveBeenCalled();
  });

  it('marks captured errors with __sentry_captured__ to avoid double-send', () => {
    const captureException = vi.fn();
    const { fake, listeners } = buildFakeWindow({ sentry: { captureException } });
    runScript(fake);
    const errorListener = listeners.find((l) => l.evt === 'error').handler;
    const err = new Error('first-time');
    errorListener({
      message: 'first-time',
      filename: 'https://tech.2twodragon.com/foo.js',
      error: err,
    });
    expect(err.__sentry_captured__).toBe(true);
    // Re-dispatching the SAME Error instance should not double-send.
    errorListener({
      message: 'first-time',
      filename: 'https://tech.2twodragon.com/foo.js',
      error: err,
    });
    expect(captureException).toHaveBeenCalledTimes(1);
  });

  it('handles unhandled promise rejections via the unhandledrejection listener', () => {
    const captureException = vi.fn();
    const { fake, listeners } = buildFakeWindow({ sentry: { captureException } });
    runScript(fake);
    const rejectionListener = listeners.find(
      (l) => l.evt === 'unhandledrejection',
    ).handler;
    rejectionListener({
      reason: new Error('async-boom'),
      promise: Promise.resolve(),
      defaultPrevented: false,
    });
    expect(captureException).toHaveBeenCalledTimes(1);
    expect(captureException.mock.calls[0][0].message).toBe('async-boom');
  });

  it('skips reporting when the rejection event was defaultPrevented', () => {
    const captureException = vi.fn();
    const { fake, listeners } = buildFakeWindow({ sentry: { captureException } });
    runScript(fake);
    const rejectionListener = listeners.find(
      (l) => l.evt === 'unhandledrejection',
    ).handler;
    rejectionListener({
      reason: new Error('handled-elsewhere'),
      defaultPrevented: true,
    });
    expect(captureException).not.toHaveBeenCalled();
  });
});
