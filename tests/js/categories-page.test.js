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
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';
import { stubIntersectionObserver, stubFetch } from './_fixtures.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/categories-page.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

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

/**
 * Evaluate the IIFE and capture the exact `hashchange` listener it registers
 * on `window`, rather than relying on `window.dispatchEvent`. `window` is
 * shared across tests in this file, and every `runScript()` call adds its
 * own closured listener that never gets removed — dispatching a real
 * `hashchange` event would also re-invoke every listener left over from
 * earlier tests (each with its own independent `dataPromise`), producing
 * extra, unrelated fetch calls. Capturing and invoking only the current
 * script's handler isolates the test the same way `observer._trigger()`
 * already isolates IntersectionObserver callbacks in this file.
 */
function runScriptAndCaptureHashHandler() {
  const originalAdd = window.addEventListener.bind(window);
  let handler = null;
  window.addEventListener = (type, cb, opts) => {
    if (type === 'hashchange' && handler === null) handler = cb;
    return originalAdd(type, cb, opts);
  };
  try {
    runScript();
  } finally {
    window.addEventListener = originalAdd;
  }
  return handler;
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

  // =========================================================================
  // Hash navigation (loadFromHash) — untested by the base suite: initial-load
  // hash targeting, invalid targets, and hashchange after the page has loaded.
  // =========================================================================

  it('loads the section matching location.hash on initial page load', async () => {
    buildCategoriesFixture(['security', 'cloud']);
    window.location.hash = '#security';
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    await flushMicrotasks();

    const section = document.querySelector('.category-section[data-category="security"]');
    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(section.querySelectorAll('article.post-card').length).toBeGreaterThan(0);
  });

  it('does not fetch when location.hash points to a nonexistent element', () => {
    buildCategoriesFixture(['security']);
    window.location.hash = '#does-not-exist';
    window.fetch = stubFetch(MOCK_DATA);

    expect(() => runScript()).not.toThrow();
    expect(window.fetch).not.toHaveBeenCalled();
  });

  it('does not fetch when location.hash targets an element that is not a category-section', () => {
    buildCategoriesFixture(['security']);
    document.body.insertAdjacentHTML('beforeend', '<div id="not-a-section"></div>');
    window.location.hash = '#not-a-section';
    window.fetch = stubFetch(MOCK_DATA);

    runScript();

    expect(window.fetch).not.toHaveBeenCalled();
  });

  it('loads the target section when a hashchange event fires after the page has loaded', async () => {
    buildCategoriesFixture(['security', 'cloud']);
    window.fetch = stubFetch(MOCK_DATA);
    const hashHandler = runScriptAndCaptureHashHandler();

    // No hash on initial load — nothing fetched yet.
    expect(window.fetch).not.toHaveBeenCalled();

    window.location.hash = '#cloud';
    hashHandler();
    await flushMicrotasks();

    const cloudSection = document.querySelector('.category-section[data-category="cloud"]');
    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(cloudSection.querySelectorAll('article.post-card').length).toBeGreaterThan(0);
  });

  // =========================================================================
  // Combined state: hash-triggered load vs. scroll (IntersectionObserver)
  // triggered load on the SAME section — the second signal must be a no-op
  // regardless of which one fired first (ensureLoaded's own data-loaded
  // guard, distinct from the dataPromise-level guard tested above with two
  // different sections).
  // =========================================================================

  it('ignores a later intersection trigger on a section already loaded via hash navigation', async () => {
    buildCategoriesFixture(['security']);
    window.location.hash = '#security';
    window.fetch = stubFetch(MOCK_DATA);
    runScript();
    await flushMicrotasks();

    const section = document.querySelector('.category-section[data-category="security"]');
    expect(window.fetch).toHaveBeenCalledTimes(1);
    const cardCountAfterHash = section.querySelectorAll('article.post-card').length;
    expect(cardCountAfterHash).toBeGreaterThan(0);

    // Scroll now brings the same, already-loaded section into view.
    observer._trigger(section);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(section.querySelectorAll('article.post-card').length).toBe(cardCountAfterHash);
  });

  it('ignores a later hashchange targeting a section already loaded via intersection', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch(MOCK_DATA);
    const hashHandler = runScriptAndCaptureHashHandler();

    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    const cardCountAfterIntersection = section.querySelectorAll('article.post-card').length;
    expect(cardCountAfterIntersection).toBeGreaterThan(0);

    // Hash navigation now points at the same, already-loaded section.
    window.location.hash = '#security';
    hashHandler();
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(section.querySelectorAll('article.post-card').length).toBe(cardCountAfterIntersection);
  });

  it('does not re-render a section on a repeat intersection trigger (existing DOM survives untouched)', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    // Mutate the rendered list — if renderSection ran again this would be wiped.
    const listEl = section.querySelector('.posts-list');
    const marker = document.createElement('div');
    marker.className = 'test-marker';
    listEl.appendChild(marker);

    observer._trigger(section);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(section.querySelector('.test-marker')).not.toBeNull();
  });

  // =========================================================================
  // category-grid click preload combined with a later intersection — the
  // preload and the lazy-render share the same dataPromise regardless of
  // which trigger path initiated the fetch.
  // =========================================================================

  it('reuses the category-grid click preload fetch when the section later intersects', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const topGrid = document.querySelector('.categories-page .category-grid');
    topGrid.dispatchEvent(new Event('click', { bubbles: true }));
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    const section = document.querySelector('.category-section[data-category="security"]');
    // Preload alone does not render — only ensureLoaded (via intersection/hash) does.
    expect(section.getAttribute('data-loaded')).not.toBe('1');

    observer._trigger(section);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(section.querySelectorAll('article.post-card').length).toBeGreaterThan(0);
  });

  // =========================================================================
  // Missing-data guards: the category key is absent from the fetched JSON,
  // or present but without a `posts` array. Both must render gracefully
  // without throwing.
  // =========================================================================

  it('leaves the section unrendered when its category key is absent from the fetched data', async () => {
    buildCategoriesFixture(['finops']);
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const section = document.querySelector('.category-section[data-category="finops"]');
    await expect(
      (async () => {
        observer._trigger(section);
        await flushMicrotasks();
      })()
    ).resolves.not.toThrow();

    expect(section.getAttribute('data-loaded')).not.toBe('1');
    expect(section.querySelectorAll('article.post-card').length).toBe(0);
    expect(section.querySelector('.posts-list').hasAttribute('aria-busy')).toBe(true);
  });

  it('renders an empty (but loaded) list when the category has no posts array', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({ security: {} });
    runScript();

    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    expect(section.getAttribute('data-loaded')).toBe('1');
    expect(section.querySelector('.posts-list').hasAttribute('aria-busy')).toBe(false);
    expect(section.querySelectorAll('article.post-card').length).toBe(0);
  });

  // =========================================================================
  // HTTP-error (resolved-but-not-ok) response — distinct from the network-
  // rejection path already covered — combined with retry-on-next-interaction
  // semantics described in the file's own header comment.
  // =========================================================================

  it('resets dataPromise on a non-ok HTTP response so a later interaction retries and succeeds', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch(null, { ok: false });
    runScript();

    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(section.querySelectorAll('article.post-card').length).toBe(0);
    expect(section.getAttribute('data-loaded')).not.toBe('1');

    // Network recovers; the guard must not have latched a permanent failure.
    window.fetch = stubFetch(MOCK_DATA);
    observer._trigger(section);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(section.querySelectorAll('article.post-card').length).toBeGreaterThan(0);
  });

  // =========================================================================
  // buildPictureHtml branch coverage: avif/webp presence, card-variant
  // presence, and the svg->_og.png src rewrite — none of the MOCK_DATA posts
  // above set `img`, so these branches were entirely unexercised.
  // =========================================================================

  it('renders card+full-size avif/webp sources and rewrites svg src to _og.png when all image flags are true', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({
      security: {
        posts: [{
          u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security',
          img: '/assets/images/cover.svg', ip: true, ia: true, ica: true, iw: true, icw: true,
        }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    const img = section.querySelector('img');
    expect(img.getAttribute('src')).toBe('/assets/images/cover_og.png');
    const avifSource = section.querySelector('source[type="image/avif"]');
    const webpSource = section.querySelector('source[type="image/webp"]');
    expect(avifSource.getAttribute('srcset')).toMatch(/525w/);
    expect(webpSource.getAttribute('srcset')).toMatch(/525w/);
  });

  it('renders single-source avif/webp without card variants and leaves a non-svg src untouched', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({
      security: {
        posts: [{
          u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security',
          img: '/assets/images/cover.png', ip: true, ia: true, ica: false, iw: true, icw: false,
        }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    const img = section.querySelector('img');
    expect(img.getAttribute('src')).toBe('/assets/images/cover.png');
    const avifSource = section.querySelector('source[type="image/avif"]');
    const webpSource = section.querySelector('source[type="image/webp"]');
    expect(avifSource.getAttribute('srcset')).not.toMatch(/525w/);
    expect(webpSource.getAttribute('srcset')).not.toMatch(/525w/);
  });

  it('omits avif/webp sources and skips the svg->png rewrite when ip/ia/iw are all false', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({
      security: {
        posts: [{
          u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security',
          img: '/assets/images/cover.svg', ip: false, ia: false, iw: false,
        }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    const img = section.querySelector('img');
    expect(img.getAttribute('src')).toBe('/assets/images/cover.svg');
    expect(section.querySelector('source')).toBeNull();
  });

  it('omits the picture element entirely when the post has no img field', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({
      security: {
        posts: [{ u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security' }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    expect(section.querySelector('.post-card-image')).toBeNull();
  });

  // =========================================================================
  // buildExcerptHtml branch coverage: dash-separated summary/highlights with
  // and without truncation, plain excerpts with and without truncation.
  // Also exercises the no-category-badge and no-tags branches on the same
  // post to avoid a proliferation of near-duplicate fixtures.
  // =========================================================================

  it('renders a dash-separated excerpt without truncation and omits badge/tags when absent', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({
      security: {
        posts: [{
          u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: '',
          ex: 'Short summary - short highlight',
        }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    expect(section.querySelector('.excerpt-summary').textContent).toBe('Short summary');
    expect(section.querySelector('.excerpt-highlights').textContent).toBe('short highlight');
    expect(section.querySelector('.category-badge')).toBeNull();
    expect(section.querySelector('.post-card-tags')).toBeNull();
  });

  it('truncates an overlong dash-separated summary and highlights', async () => {
    buildCategoriesFixture(['security']);
    const longSummary = 'S'.repeat(50);
    const longHighlights = 'H'.repeat(90);
    window.fetch = stubFetch({
      security: {
        posts: [{
          u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security',
          ex: longSummary + ' - ' + longHighlights,
        }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    expect(section.querySelector('.excerpt-summary').textContent).toBe('S'.repeat(40) + '…');
    expect(section.querySelector('.excerpt-highlights').textContent).toBe('H'.repeat(80) + '…');
  });

  it('renders a plain (non-dash) excerpt as-is when under the length limit', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({
      security: {
        posts: [{
          u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security',
          ex: 'A plain excerpt with no dash separator',
        }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    const p = section.querySelector('p.post-card-excerpt');
    expect(p.textContent).toBe('A plain excerpt with no dash separator');
  });

  it('truncates an overlong plain (non-dash) excerpt', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({
      security: {
        posts: [{
          u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security',
          ex: 'P'.repeat(150),
        }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    const p = section.querySelector('p.post-card-excerpt');
    expect(p.textContent).toBe('P'.repeat(120) + '…');
  });

  // =========================================================================
  // Tag "+N more" badge branch: only rendered when `tn` exceeds the number
  // of tags actually included in the payload.
  // =========================================================================

  it('does not render a "+more" tag badge when tn equals the tags length', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({
      security: {
        posts: [{
          u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security',
          tags: ['a', 'b'], tn: 2,
        }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    expect(section.querySelector('.tag--more')).toBeNull();
  });

  it('renders a "+N more" tag badge when tn exceeds the included tags length', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch({
      security: {
        posts: [{
          u: '/posts/a', t: 'Post A', d: '2026-01-01', x: '2026-01-01', c: 'security',
          tags: ['a'], tn: 5,
        }],
      },
    });
    runScript();
    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section);
    await flushMicrotasks();

    expect(section.querySelector('.tag--more').textContent).toBe('+4');
  });

  // =========================================================================
  // ensureLoaded / preload-listener / IntersectionObserver edge branches
  // =========================================================================

  it('does not fetch when a hash-targeted category-section lacks a data-category attribute', () => {
    buildCategoriesFixture(['security']);
    document.body.insertAdjacentHTML(
      'beforeend',
      '<section class="category-section" id="no-key"><div class="posts-list"></div></section>'
    );
    window.location.hash = '#no-key';
    window.fetch = stubFetch(MOCK_DATA);

    runScript();

    expect(window.fetch).not.toHaveBeenCalled();
  });

  it('does not attach a preload click listener when no .category-grid element exists', () => {
    document.body.innerHTML =
      '<section class="category-section" data-category="security" id="security">' +
      '<div class="posts-list"></div></section>';
    window.fetch = stubFetch(MOCK_DATA);

    expect(() => runScript()).not.toThrow();
    expect(window.fetch).not.toHaveBeenCalled();
  });

  it('does not load the section when the intersection entry reports isIntersecting=false', async () => {
    buildCategoriesFixture(['security']);
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const section = document.querySelector('.category-section[data-category="security"]');
    observer._trigger(section, false);
    await flushMicrotasks();

    expect(window.fetch).not.toHaveBeenCalled();
  });

  it('falls back to requestIdleCallback to eagerly load all sections when IntersectionObserver is unsupported', async () => {
    buildCategoriesFixture(['security', 'cloud']);
    delete window.IntersectionObserver;
    window.requestIdleCallback = vi.fn((cb) => cb());
    window.fetch = stubFetch(MOCK_DATA);

    runScript();
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    const sec = document.querySelector('.category-section[data-category="security"]');
    const cloud = document.querySelector('.category-section[data-category="cloud"]');
    expect(sec.querySelectorAll('article.post-card').length).toBeGreaterThan(0);
    expect(cloud.querySelectorAll('article.post-card').length).toBeGreaterThan(0);

    delete window.requestIdleCallback;
  });

  it('falls back to setTimeout to eagerly load sections when requestIdleCallback is also unavailable', async () => {
    buildCategoriesFixture(['security']);
    delete window.IntersectionObserver;
    delete window.requestIdleCallback;
    window.fetch = stubFetch(MOCK_DATA);

    vi.useFakeTimers();
    runScript();
    vi.advanceTimersByTime(1000);
    vi.useRealTimers();
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    const section = document.querySelector('.category-section[data-category="security"]');
    expect(section.querySelectorAll('article.post-card').length).toBeGreaterThan(0);
  });
});
