// Regression tests for assets/js/main-search.js
//
// Goal: prove the search bootstrap (a) bails cleanly when no #search-input
// exists, (b) injects its scoped enhanced-styles tag exactly once, (c)
// fetches /search.json on init, (d) defers Fuse.js loading until first
// focus (cost optimization), and (e) clears results when the query falls
// below the 2-char minimum.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/main-search.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

function buildSearchFixture() {
  document.body.innerHTML = `
    <div class="search-container">
      <input id="search-input" type="search" />
      <div id="search-results" style="display:none"></div>
    </div>
  `;
}

describe('main-search.js', () => {
  let originalFetch;

  beforeEach(() => {
    originalFetch = window.fetch;
    // Stub fetch so the IIFE's eager `/search.json` request resolves with
    // an empty index. We don't care about results — just that init runs.
    window.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      })
    );
    document.body.innerHTML = '';
    document.head.querySelectorAll('#search-enhanced-styles').forEach((el) => el.remove());
  });

  afterEach(() => {
    window.fetch = originalFetch;
    document.body.innerHTML = '';
    document.head.querySelectorAll('#search-enhanced-styles').forEach((el) => el.remove());
  });

  it('bails cleanly when #search-input is missing', () => {
    expect(() => runScript()).not.toThrow();
    expect(document.getElementById('search-enhanced-styles')).toBeNull();
  });

  it('injects #search-enhanced-styles exactly once when search input exists', () => {
    buildSearchFixture();
    runScript();
    expect(document.querySelectorAll('#search-enhanced-styles')).toHaveLength(1);
  });

  it('eagerly fetches /search.json on init', () => {
    buildSearchFixture();
    runScript();
    const calls = window.fetch.mock.calls.map((c) => c[0]);
    expect(calls.some((url) => String(url).includes('/search.json'))).toBe(true);
  });

  it('hides results panel when query length < 2 (debounced no-op)', async () => {
    buildSearchFixture();
    runScript();

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    // Pre-fill some HTML to verify it gets cleared.
    results.innerHTML = '<a class="search-result-item">stale</a>';
    results.style.display = 'block';

    input.value = 'a';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    expect(results.textContent).toBe('');
    expect(results.style.display).toBe('none');
  });

  it('defers Fuse.js CDN loading until the search input is focused', () => {
    buildSearchFixture();
    runScript();

    // No CDN script should be appended on init.
    const before = document.querySelectorAll('script[src*="fuse"]').length;
    expect(before).toBe(0);

    document.getElementById('search-input').dispatchEvent(new Event('focus'));
    const after = document.querySelectorAll('script[src*="fuse"]').length;
    expect(after).toBe(1);
  });

  it('Escape key on the search input hides the results panel', async () => {
    buildSearchFixture();
    runScript();

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    // Seed at least one result item so the keydown handler reaches the
    // Escape branch (the early-return only fires when zero items).
    results.innerHTML = '<a class="search-result-item" href="#">x</a>';
    results.style.display = 'block';

    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    expect(results.style.display).toBe('none');
  });
});
