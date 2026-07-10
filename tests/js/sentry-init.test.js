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
});
