// Regression tests for assets/js/categories-page.js
//
// categories-page.js is a standalone IIFE that:
//   1. Bails immediately when no `section.category-section[data-category]`
//      elements are present in the DOM.
//   2. On IntersectionObserver callback (scroll into view), fetches
//      /categories-data.json exactly once (lazy-load guard via `dataPromise`).
//   3. Populates each section's `.posts-list` with rendered `.post-card`
//      article elements from the JSON.
//   4. On fetch failure resets `dataPromise` to null (retry semantics) and
//      leaves the section empty — no throw.
//
// We evaluate the IIFE with new Function() after each test sets up its own
// DOM fixture, matching the pattern used by the other tests in this suite.
// `location` is patched via delete+reassign (the jsdom workaround for the
// non-configurable window.location.hostname).

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { stubIntersectionObserver, stubFetch } from './_fixtures.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/categories-page.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

// Minimal mock JSON payload that categories-page.js expects.
// Top-level keys are category slugs; values have a `posts` array.
const MOCK_DATA = {
  security: {
    posts: [
      { u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security', tags: ['sec'] },
    ],
  },
  cloud: {
    posts: [
      { u: '/posts/b', t: 'Post B', d: '2026-01-02', x: '2026-01-02', c: 'cloud', tags: [] },
    ],
  },
};

/** Drain enough microtask ticks for nested promise chains to settle. */
async function flushMicrotasks(n = 8) {
  for (let i = 0; i < n; i++) {
    await Promise.resolve();
  }
}

/**
 * Build a categories-page-like DOM fixture with the given category slugs.
 * Each section contains an empty `.posts-list` aria-busy="true" div.
 */
function buildCategoriesFixture(slugs = ['security', 'cloud']) {
  const sectionsHtml = slugs
    .map(
      (slug) =>
        `<section class="category-section" data-category="${slug}" id="${slug}">
           <div class="posts-list" aria-busy="true"></div>
         </section>`
    )
    .join('\n');

  document.body.innerHTML = `
    <div class="categories-page">
      <div class="category-grid"></div>
      ${sectionsHtml}
    </div>
  `;
}

/** Evaluate the IIFE. The script reads window.location.pathname internally. */
function runScript() {
  // eslint-disable-next-line no-new-func
  new Function(SCRIPT_SOURCE)();
}

describe('categories-page.js', () => {
  let restoreIO;
  // The IntersectionObserver instance created by the script.
  let observer;

  beforeEach(() => {
    // Set location so baseUrl derivation yields '' (empty baseurl).
    delete window.location;
    window.location = {
      hostname: 'localhost',
      href: 'http://localhost/categories/',
      pathname: '/categories/',
      hash: '',
      origin: 'http://localhost',
    };

    restoreIO = stubIntersectionObserver();

    // Wrap the stub to capture the instance the script creates.
    const StubIO = window.IntersectionObserver;
    window.IntersectionObserver = class extends StubIO {
      constructor(cb, opts) {
        super(cb, opts);
        observer = this;
      }
    };

    localStorage.clear();
    document.body.innerHTML = '';
    delete window.fetch;
  });

  afterEach(() => {
    restoreIO();
    delete window.fetch;
    // Restore a default location.
    delete window.location;
    window.location = { hostname: 'localhost', href: 'http://localhost/', pathname: '/', hash: '', origin: 'http://localhost' };
    localStorage.clear();
    document.body.innerHTML = '';
  });

  // =========================================================================
  // Early-bail: no category sections
  // =========================================================================

  it('bails when no .category-section[data-category] elements are present', () => {
    document.body.innerHTML = '<div class="categories-page"></div>';
    window.fetch = stubFetch(MOCK_DATA);
    runScript();
    expect(window.fetch).not.toHaveBeenCalled();
  });

  // =========================================================================
  // Fetch on first intersection
  // =========================================================================

  it('fetches /categories-data.json exactly once on first intersection', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);

    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(window.fetch.mock.calls[0][0]).toMatch(/categories-data\.json/);
  });

  // =========================================================================
  // DOM populated with post cards after intersection
  // =========================================================================

  it('populates the section with .post-card articles after intersection', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);

    await flushMicrotasks();

    const cards = section.querySelectorAll('article.post-card');
    expect(cards.length).toBeGreaterThan(0);
  });

  // =========================================================================
  // One-time load guard: subsequent intersections don't re-fetch
  // =========================================================================

  it('does not re-fetch on subsequent intersections (dataPromise guard)', async () => {
    buildCategoriesFixture(['security', 'cloud']);
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const sec = document.querySelector('.category-section[data-category="security"]');
    const cloud = document.querySelector('.category-section[data-category="cloud"]');

    // First intersection fetches data.
    observer._trigger(sec);
    await flushMicrotasks();
    const callsAfterFirst = window.fetch.mock.calls.length;

    // Second section intersection reuses the existing resolved dataPromise.
    observer._trigger(cloud);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(callsAfterFirst);
  });

  // =========================================================================
  // Graceful degradation on fetch failure
  // =========================================================================

  it('leaves section empty and does not throw when fetch rejects', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch(null, { throws: true });
    runScript();

    const section = document.querySelector('.category-section[data-category="security"]');

    await expect(
      (async () => {
        observer._trigger(section);
        await flushMicrotasks();
      })()
    ).resolves.not.toThrow();

    const cards = section.querySelectorAll('article.post-card');
    expect(cards.length).toBe(0);
  });
});
