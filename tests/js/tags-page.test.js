// Regression tests for assets/js/tags-page.js
//
// tags-page.js is a standalone IIFE that:
//   1. Bails immediately when `#tag-search` or `.tag-cloud` is missing.
//   2. Restores persisted sort order (`tags-sort`) and multi-select tag
//      filter (`tags-selected`) from localStorage on load.
//   3. Handles multi-select tag clicks in the cloud (toggle select/deselect,
//      dim non-matching sections, update the "N개 선택됨" badge).
//   4. Debounces (200ms) a search box that filters both the tag cloud and
//      the `.tag-section` list, showing an empty-state when nothing matches.
//   5. Supports keyboard shortcuts ("/" focuses search, Escape clears it).
//   6. Re-sorts the tag cloud (alpha w/ letter dividers vs. count desc) on
//      sort-button click, persisting the choice.
//   7. Lazily loads `/tags-data.json` on first tag-cloud click or when a
//      `.tag-section` scrolls into view (IntersectionObserver), rendering
//      escaped post lists + related-tag pills exactly once per section.
//   8. Supports hash-based navigation (`/tags/#slug`) that eagerly loads
//      the target section before scrolling.
//
// We evaluate the IIFE with new Function('window','document', SOURCE) after
// each test sets up its own DOM fixture, matching the pattern used by the
// other tests in this suite (see home-posts-filter.test.js / categories-page.test.js).

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { stubIntersectionObserver, stubFetch } from './_fixtures.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/tags-page.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

// Mock /tags-data.json payload keyed by tag slug.
const MOCK_DATA = {
  aws: {
    related: ['Kubernetes', 'Docker'],
    posts: [
      { u: '/posts/a', t: 'Post <A>', d: '2026-01-01', x: '2026-01-01', c: 'cloud' },
      { u: '/posts/b', t: 'Post B', d: '2026-01-02', x: '2026-01-02', c: '' },
    ],
  },
  docker: {
    related: [],
    posts: [{ u: '/posts/c', t: 'Post C', d: '2026-01-03', x: '2026-01-03', c: 'devops' }],
  },
  kubernetes: {
    related: [],
    posts: [],
  },
};

const DEFAULT_TAGS = [
  { slug: 'kubernetes', name: 'kubernetes', count: 5, letter: 'K' },
  { slug: 'aws', name: 'aws', count: 10, letter: 'A' },
  { slug: 'docker', name: 'docker', count: 3, letter: 'D' },
];

/** Drain enough microtask ticks for nested promise chains to settle. */
async function flushMicrotasks(n = 8) {
  for (let i = 0; i < n; i++) {
    await Promise.resolve();
  }
}

/** Wait for real timers (search debounce is a real 200ms setTimeout). */
function wait(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

/**
 * Build a tags-page-like DOM fixture.
 *
 * @param {object}  [opts]
 * @param {Array}   [opts.tags] — [{ slug, name, count, letter }]
 * @param {boolean} [opts.withInput=true]
 * @param {boolean} [opts.withCloud=true]
 * @param {boolean} [opts.withSortBtns=true]
 * @param {boolean} [opts.withClearBtn=true]
 * @param {boolean} [opts.withFilterStatus=true]
 */
function buildTagsFixture({
  tags = DEFAULT_TAGS,
  withInput = true,
  withCloud = true,
  withSortBtns = true,
  withClearBtn = true,
  withFilterStatus = true,
} = {}) {
  const tagsHtml = tags
    .map(
      (t) =>
        `<a href="#${t.slug}" class="tag" data-tag="${t.slug}" data-tag-name="${t.name}" data-count="${t.count}" data-letter="${t.letter}">${t.name}</a>`
    )
    .join('\n');

  const letters = [...new Set(tags.map((t) => t.letter))];
  const dividersHtml = letters
    .map((l) => `<span class="tag-letter-divider" data-letter="${l}">${l}</span>`)
    .join('\n');

  const sectionsHtml = tags
    .map(
      (t) =>
        `<section class="tag-section" id="${t.slug}" data-section-tag="${t.slug}">
           <div class="tag-section-header">${t.name}</div>
         </section>`
    )
    .join('\n');

  document.body.innerHTML = `
    <div id="tags-top">
      ${withInput ? `<div><input id="tag-search" type="text" /><span class="search-kbd">/</span></div>` : ''}
      ${
        withCloud
          ? `<div class="tag-cloud sort-alpha">${dividersHtml}\n${tagsHtml}</div>`
          : ''
      }
      <div id="tags-search-empty" hidden aria-hidden="true"></div>
      ${
        withSortBtns
          ? `<div class="tags-sort-bar">
               <button class="tags-sort-btn active" data-sort="alpha" type="button">A-Z</button>
               <button class="tags-sort-btn" data-sort="count" type="button">Count</button>
             </div>`
          : ''
      }
      ${withClearBtn ? `<button id="tags-clear-btn" type="button">Clear</button>` : ''}
      ${
        withFilterStatus
          ? `<div id="tags-filter-status" hidden><span id="tags-selected-badge"></span></div>`
          : ''
      }
      ${sectionsHtml}
    </div>
  `;
}

/** Evaluate the IIFE against the current window/document. */
function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

/**
 * vitest reuses one jsdom `window`/`document` for every test in this file
 * (only `document.body.innerHTML` is reset between tests). The script under
 * test attaches several *document/window*-level listeners (hashchange,
 * keydown, delegated click for `.tag-related-pill`) on every runScript()
 * call, which would otherwise accumulate across tests and make a single
 * event fire N handlers instead of 1. This helper records every listener
 * added to `document`/`window` during a test and strips them all in
 * afterEach so each test starts from a clean listener slate.
 */
function trackGlobalListeners() {
  const originalDocAdd = document.addEventListener.bind(document);
  const originalWinAdd = window.addEventListener.bind(window);
  const added = [];

  document.addEventListener = (type, handler, opts) => {
    added.push([document, type, handler, opts]);
    return originalDocAdd(type, handler, opts);
  };
  window.addEventListener = (type, handler, opts) => {
    added.push([window, type, handler, opts]);
    return originalWinAdd(type, handler, opts);
  };

  return function restore() {
    added.forEach(([target, type, handler, opts]) => target.removeEventListener(type, handler, opts));
    document.addEventListener = originalDocAdd;
    window.addEventListener = originalWinAdd;
  };
}

/** Read the ordered list of tag slugs currently in the DOM's .tag-cloud. */
function cloudOrder() {
  return Array.from(document.querySelectorAll('.tag-cloud .tag[data-tag]')).map((t) =>
    t.getAttribute('data-tag')
  );
}

describe('tags-page.js', () => {
  let restoreIO;
  let restoreListeners;
  let originalScrollIntoView;
  // The IntersectionObserver instance the script creates internally, so
  // tests can fire `.tag-section` scroll-into-view without a real scroll.
  let observer;

  beforeEach(() => {
    delete window.location;
    window.location = {
      hostname: 'localhost',
      href: 'http://localhost/tags/',
      pathname: '/tags/',
      hash: '',
      origin: 'http://localhost',
    };

    restoreIO = stubIntersectionObserver();
    const StubIO = window.IntersectionObserver;
    window.IntersectionObserver = class extends StubIO {
      constructor(cb, opts) {
        super(cb, opts);
        observer = this;
      }
    };

    // jsdom lacks rAF; the script calls it bare (unprefixed) for fade-in
    // animation only — a synchronous stub keeps assertions deterministic.
    window.requestAnimationFrame = vi.fn((cb) => {
      cb();
      return 1;
    });

    originalScrollIntoView = Element.prototype.scrollIntoView;
    Element.prototype.scrollIntoView = vi.fn();

    restoreListeners = trackGlobalListeners();

    localStorage.clear();
    document.body.innerHTML = '';
    // Every test exercises the tag-cloud click listener (which eagerly calls
    // loadTagsData() via a `{ once: true }` handler), so a default fetch stub
    // must always be present — jsdom has no native `fetch`. Tests that care
    // about the response override `window.fetch` before calling runScript().
    window.fetch = stubFetch(null, { ok: false });
  });

  afterEach(() => {
    restoreListeners();
    restoreIO();
    delete window.fetch;
    delete window.requestAnimationFrame;
    Element.prototype.scrollIntoView = originalScrollIntoView;
    delete window.location;
    window.location = { hostname: 'localhost', href: 'http://localhost/', pathname: '/', hash: '', origin: 'http://localhost' };
    localStorage.clear();
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  // =========================================================================
  // Early-bail guards
  // =========================================================================

  it('bails when #tag-search is missing (clicking a tag does nothing)', () => {
    buildTagsFixture({ withInput: false });
    runScript();

    const tag = document.querySelector('.tag[data-tag="aws"]');
    tag.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(tag.classList.contains('tag--selected')).toBe(false);
  });

  it('bails when .tag-cloud is missing (no crash)', () => {
    expect(() => {
      buildTagsFixture({ withCloud: false });
      runScript();
    }).not.toThrow();
  });

  // =========================================================================
  // Restore persisted state: sort
  // =========================================================================

  it('applies default alpha sort with letter dividers on load', () => {
    buildTagsFixture();
    runScript();

    expect(cloudOrder()).toEqual(['aws', 'docker', 'kubernetes']);
    expect(document.querySelector('.tag-cloud').classList.contains('sort-alpha')).toBe(true);
    // Every letter divider present in the source tags should now be inside the cloud.
    const dividers = document.querySelectorAll('.tag-cloud .tag-letter-divider');
    expect(dividers.length).toBeGreaterThan(0);
  });

  it('restores count sort from localStorage and removes sort-alpha', () => {
    localStorage.setItem('tags-sort', JSON.stringify('count'));
    buildTagsFixture();
    runScript();

    expect(cloudOrder()).toEqual(['aws', 'kubernetes', 'docker']); // 10, 5, 3
    expect(document.querySelector('.tag-cloud').classList.contains('sort-alpha')).toBe(false);
    const activeBtn = document.querySelector('.tags-sort-btn.active');
    expect(activeBtn.getAttribute('data-sort')).toBe('count');
  });

  // =========================================================================
  // Restore persisted state: selected tags
  // =========================================================================

  it('restores selected tags from localStorage and applies the multi-filter', () => {
    localStorage.setItem('tags-selected', JSON.stringify(['docker']));
    buildTagsFixture();
    runScript();

    const dockerTag = document.querySelector('.tag[data-tag="docker"]');
    const awsTag = document.querySelector('.tag[data-tag="aws"]');
    expect(dockerTag.classList.contains('tag--selected')).toBe(true);
    expect(awsTag.classList.contains('tag--dimmed')).toBe(true);

    const dockerSection = document.getElementById('docker');
    expect(dockerSection.classList.contains('tag-section--dimmed')).toBe(false);

    const badge = document.getElementById('tags-selected-badge');
    expect(badge.textContent).toBe('1개 선택됨');
    expect(document.getElementById('tags-filter-status').hidden).toBe(false);
  });

  it('ignores a persisted tag slug that no longer exists in the DOM', () => {
    localStorage.setItem('tags-selected', JSON.stringify(['does-not-exist']));
    expect(() => {
      buildTagsFixture();
      runScript();
    }).not.toThrow();

    // Selection should remain empty since the slug was never found — no
    // filter should be applied.
    expect(document.getElementById('tags-filter-status').hidden).toBe(true);
  });

  // =========================================================================
  // Tag cloud: click to select / deselect
  // =========================================================================

  it('selects a tag on click: adds tag--selected, dims others, updates badge', () => {
    buildTagsFixture();
    runScript();

    const awsTag = document.querySelector('.tag[data-tag="aws"]');
    awsTag.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(awsTag.classList.contains('tag--selected')).toBe(true);
    expect(document.querySelector('.tag[data-tag="docker"]').classList.contains('tag--dimmed')).toBe(
      true
    );
    expect(document.getElementById('aws').classList.contains('tag-section--dimmed')).toBe(false);
    expect(document.getElementById('docker').classList.contains('tag-section--dimmed')).toBe(true);
    expect(document.getElementById('tags-selected-badge').textContent).toBe('1개 선택됨');
    expect(JSON.parse(localStorage.getItem('tags-selected'))).toEqual(['aws']);
  });

  it('deselects a tag on second click and resets all styling when selection becomes empty', () => {
    buildTagsFixture();
    runScript();

    const awsTag = document.querySelector('.tag[data-tag="aws"]');
    awsTag.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    awsTag.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(awsTag.classList.contains('tag--selected')).toBe(false);
    expect(awsTag.classList.contains('tag--dimmed')).toBe(false);
    expect(document.getElementById('docker').classList.contains('tag-section--dimmed')).toBe(false);
    expect(document.getElementById('tags-filter-status').hidden).toBe(true);
    expect(JSON.parse(localStorage.getItem('tags-selected'))).toEqual([]);
  });

  it('supports multi-select: two selected tags both stay un-dimmed, the rest are dimmed', () => {
    buildTagsFixture();
    runScript();

    document
      .querySelector('.tag[data-tag="aws"]')
      .dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    document
      .querySelector('.tag[data-tag="docker"]')
      .dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(document.getElementById('aws').classList.contains('tag-section--dimmed')).toBe(false);
    expect(document.getElementById('docker').classList.contains('tag-section--dimmed')).toBe(false);
    expect(document.getElementById('kubernetes').classList.contains('tag-section--dimmed')).toBe(
      true
    );
    expect(document.getElementById('tags-selected-badge').textContent).toBe('2개 선택됨');
  });

  it('clicking inside the cloud but outside a .tag[data-tag] element is a no-op', () => {
    buildTagsFixture();
    runScript();

    const cloud = document.querySelector('.tag-cloud');
    cloud.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(document.getElementById('tags-filter-status').hidden).toBe(true);
    expect(localStorage.getItem('tags-selected')).toBeNull();
  });

  it('scrolls the matching section into view when exactly one tag is newly selected', async () => {
    buildTagsFixture();
    runScript();

    const awsTag = document.querySelector('.tag[data-tag="aws"]');
    awsTag.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

    await wait(120); // scroll is scheduled via setTimeout(..., 80)

    expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
  });

  // =========================================================================
  // Clear button
  // =========================================================================

  it('clear button resets selection and un-dims everything', () => {
    buildTagsFixture();
    runScript();

    document
      .querySelector('.tag[data-tag="aws"]')
      .dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    document.getElementById('tags-clear-btn').click();

    expect(document.querySelector('.tag[data-tag="aws"]').classList.contains('tag--selected')).toBe(
      false
    );
    expect(document.getElementById('docker').classList.contains('tag-section--dimmed')).toBe(false);
    expect(document.getElementById('tags-filter-status').hidden).toBe(true);
    expect(JSON.parse(localStorage.getItem('tags-selected'))).toEqual([]);
  });

  // =========================================================================
  // Search filter (debounced)
  // =========================================================================

  it('filters the tag cloud and sections by search query after the debounce', async () => {
    buildTagsFixture();
    runScript();

    const input = document.getElementById('tag-search');
    input.value = 'doc';
    input.dispatchEvent(new Event('input'));

    await wait(250);

    expect(document.querySelector('.tag[data-tag="docker"]').style.display).toBe('');
    expect(document.querySelector('.tag[data-tag="aws"]').style.display).toBe('none');
    expect(document.getElementById('docker').style.display).toBe('');
    expect(document.getElementById('aws').style.display).toBe('none');
    expect(document.getElementById('aws').getAttribute('data-search-hidden')).toBe('1');
  });

  it('shows the empty-state when the query matches no tags, hides it once cleared', async () => {
    buildTagsFixture();
    runScript();

    const input = document.getElementById('tag-search');
    const emptyEl = document.getElementById('tags-search-empty');

    input.value = 'zzz-no-match';
    input.dispatchEvent(new Event('input'));
    await wait(250);

    expect(emptyEl.hidden).toBe(false);
    expect(emptyEl.getAttribute('aria-hidden')).toBe('false');

    input.value = '';
    input.dispatchEvent(new Event('input'));
    await wait(250);

    expect(emptyEl.hidden).toBe(true);
    expect(emptyEl.getAttribute('aria-hidden')).toBe('true');
    expect(document.querySelector('.tag[data-tag="aws"]').style.display).toBe('');
  });

  it('hides letter dividers whose entire letter group is filtered out', async () => {
    buildTagsFixture();
    runScript();

    const input = document.getElementById('tag-search');
    input.value = 'aws'; // only matches the "A" tag; "D" and "K" groups fully hidden
    input.dispatchEvent(new Event('input'));
    await wait(250);

    const dividerA = document.querySelector('.tag-cloud .tag-letter-divider[data-letter="A"]');
    const dividerD = document.querySelector('.tag-cloud .tag-letter-divider[data-letter="D"]');
    expect(dividerA.style.display).toBe('');
    expect(dividerD.style.display).toBe('none');
  });

  // =========================================================================
  // Combined interactions: multi-select + search
  // =========================================================================

  it('multi-select stays intact while a search filters the cloud, and clearing the search restores hidden selected tags', async () => {
    buildTagsFixture();
    runScript();

    const awsTag = document.querySelector('.tag[data-tag="aws"]');
    const dockerTag = document.querySelector('.tag[data-tag="docker"]');
    const kubernetesTag = document.querySelector('.tag[data-tag="kubernetes"]');

    awsTag.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    dockerTag.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(awsTag.classList.contains('tag--selected')).toBe(true);
    expect(dockerTag.classList.contains('tag--selected')).toBe(true);
    expect(document.getElementById('tags-selected-badge').textContent).toBe('2개 선택됨');

    const input = document.getElementById('tag-search');
    input.value = 'doc'; // matches only "docker"
    input.dispatchEvent(new Event('input'));
    await wait(250);

    // Selection state is untouched by search: both tags remain selected...
    expect(awsTag.classList.contains('tag--selected')).toBe(true);
    expect(dockerTag.classList.contains('tag--selected')).toBe(true);
    expect(document.getElementById('tags-selected-badge').textContent).toBe('2개 선택됨');
    // ...but search independently hides the non-matching selected tag ("aws")
    // while the matching selected tag ("docker") stays visible.
    expect(awsTag.style.display).toBe('none');
    expect(dockerTag.style.display).toBe('');
    expect(kubernetesTag.classList.contains('tag--dimmed')).toBe(true);
    expect(kubernetesTag.style.display).toBe('none');

    input.value = '';
    input.dispatchEvent(new Event('input'));
    await wait(250);

    // Clearing the search reveals the previously search-hidden selected tag,
    // and the selection itself (classes + badge + persisted pref) is unchanged.
    expect(awsTag.style.display).toBe('');
    expect(awsTag.classList.contains('tag--selected')).toBe(true);
    expect(dockerTag.classList.contains('tag--selected')).toBe(true);
    expect(document.getElementById('tags-selected-badge').textContent).toBe('2개 선택됨');
    expect(JSON.parse(localStorage.getItem('tags-selected'))).toEqual(['aws', 'docker']);
  });

  it('a search query that hides a selected tag keeps it selected (class + persisted pref) and reveals it again once cleared', async () => {
    buildTagsFixture();
    runScript();

    const awsTag = document.querySelector('.tag[data-tag="aws"]');
    awsTag.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    expect(awsTag.classList.contains('tag--selected')).toBe(true);

    const input = document.getElementById('tag-search');
    input.value = 'zzz-no-match'; // matches nothing, including the selected "aws" tag
    input.dispatchEvent(new Event('input'));
    await wait(250);

    expect(awsTag.style.display).toBe('none');
    expect(awsTag.classList.contains('tag--selected')).toBe(true); // still selected, just hidden
    expect(JSON.parse(localStorage.getItem('tags-selected'))).toEqual(['aws']); // pref untouched by search

    input.value = '';
    input.dispatchEvent(new Event('input'));
    await wait(250);

    expect(awsTag.style.display).toBe('');
    expect(awsTag.classList.contains('tag--selected')).toBe(true);
    expect(document.getElementById('tags-selected-badge').textContent).toBe('1개 선택됨');
  });

  // =========================================================================
  // Keyboard shortcuts
  // =========================================================================

  it('"/" focuses the search input when focus is elsewhere', () => {
    buildTagsFixture();
    runScript();

    const input = document.getElementById('tag-search');
    expect(document.activeElement).not.toBe(input);

    document.dispatchEvent(new KeyboardEvent('keydown', { key: '/', bubbles: true, cancelable: true }));

    expect(document.activeElement).toBe(input);
  });

  it('Escape clears and blurs the search input when it is focused', async () => {
    buildTagsFixture();
    runScript();

    const input = document.getElementById('tag-search');
    input.focus();
    input.value = 'docker';
    input.dispatchEvent(new Event('input'));
    await wait(250);

    input.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true })
    );

    expect(input.value).toBe('');
    await wait(250); // the re-dispatched 'input' event re-runs the debounced filter

    expect(document.querySelector('.tag[data-tag="aws"]').style.display).toBe('');
  });

  it('hides the keyboard hint on focus and re-shows it on blur only if the input is empty', () => {
    buildTagsFixture();
    runScript();

    const input = document.getElementById('tag-search');
    const hint = document.querySelector('.search-kbd');

    input.dispatchEvent(new Event('focus'));
    expect(hint.style.display).toBe('none');

    input.value = 'aws';
    input.dispatchEvent(new Event('blur'));
    expect(hint.style.display).toBe('none'); // stays hidden — input has a value

    input.value = '';
    input.dispatchEvent(new Event('blur'));
    expect(hint.style.display).toBe(''); // re-shown — input is empty
  });

  // =========================================================================
  // Sort buttons
  // =========================================================================

  it('clicking the count sort button re-sorts by count desc and persists the choice', () => {
    buildTagsFixture();
    runScript();

    const countBtn = document.querySelector('.tags-sort-btn[data-sort="count"]');
    countBtn.click();

    expect(cloudOrder()).toEqual(['aws', 'kubernetes', 'docker']);
    expect(countBtn.classList.contains('active')).toBe(true);
    expect(document.querySelector('.tags-sort-btn[data-sort="alpha"]').classList.contains('active')).toBe(
      false
    );
    expect(JSON.parse(localStorage.getItem('tags-sort'))).toBe('count');
    expect(document.querySelector('.tag-cloud').classList.contains('sort-alpha')).toBe(false);
  });

  it('switching count -> alpha re-sorts tags and restores the letter dividers', () => {
    // applySortToDom('count') detaches the divider elements from .tag-cloud
    // without reattaching them. Divider elements are now cached at module
    // scope on first read, so switching back to alpha re-appends the same
    // cached elements instead of losing them permanently.
    buildTagsFixture();
    runScript();
    const initialDividerCount = document.querySelectorAll('.tag-cloud .tag-letter-divider').length;
    expect(initialDividerCount).toBeGreaterThan(0);

    document.querySelector('.tags-sort-btn[data-sort="count"]').click();
    expect(document.querySelectorAll('.tag-cloud .tag-letter-divider').length).toBe(0);

    document.querySelector('.tags-sort-btn[data-sort="alpha"]').click();

    expect(cloudOrder()).toEqual(['aws', 'docker', 'kubernetes']);
    expect(document.querySelector('.tag-cloud').classList.contains('sort-alpha')).toBe(true);
    expect(document.querySelectorAll('.tag-cloud .tag-letter-divider').length).toBe(initialDividerCount);

    // Dividers must be correctly interleaved ahead of their letter group,
    // not just present anywhere in the DOM.
    const cloud = document.querySelector('.tag-cloud');
    const orderedTags = Array.from(cloud.children).map((el) =>
      el.classList.contains('tag-letter-divider')
        ? 'divider:' + el.getAttribute('data-letter')
        : el.getAttribute('data-tag')
    );
    expect(orderedTags).toEqual(['divider:A', 'aws', 'divider:D', 'docker', 'divider:K', 'kubernetes']);
  });

  it('active search survives a count->alpha round trip without stale divider visibility', async () => {
    // Regression test: updateLetterDividers() early-returns while sort-alpha
    // is not set (count sort), so changing the search *while* sorted by
    // count leaves the cached divider elements holding stale style.display
    // from the previous alpha-mode search. Switching back to alpha must
    // recompute divider visibility from the *current* search state instead
    // of replaying the stale cached value.
    buildTagsFixture();
    runScript();

    const input = document.getElementById('tag-search');
    const dividerA = document.querySelector('.tag-cloud .tag-letter-divider[data-letter="A"]');
    const dividerD = document.querySelector('.tag-cloud .tag-letter-divider[data-letter="D"]');
    const dividerK = document.querySelector('.tag-cloud .tag-letter-divider[data-letter="K"]');

    // Search for "aws": only the "A" letter group has a visible match.
    input.value = 'aws';
    input.dispatchEvent(new Event('input'));
    await wait(250);

    expect(dividerA.style.display).toBe('');
    expect(dividerD.style.display).toBe('none');
    expect(dividerK.style.display).toBe('none');

    // Switch to count sort — dividers are detached from the DOM entirely,
    // and sort-alpha is removed so updateLetterDividers() is inert while
    // this mode is active.
    document.querySelector('.tags-sort-btn[data-sort="count"]').click();

    // While still in count mode, change the search: now only "docker"
    // matches. Because sort-alpha isn't set, updateLetterDividers() (called
    // by the input handler) early-returns — the cached divider elements'
    // style.display is NOT updated to reflect this new search state yet.
    input.value = 'docker';
    input.dispatchEvent(new Event('input'));
    await wait(250);

    // Switch back to alpha sort.
    document.querySelector('.tags-sort-btn[data-sort="alpha"]').click();

    // The fix: applySortToDom's alpha branch calls updateLetterDividers()
    // itself, recomputing from the *current* tag visibility rather than
    // leaving the stale cached style.display in place.
    expect(dividerA.style.display).toBe('none'); // aws is now search-hidden
    expect(dividerD.style.display).toBe('');     // docker is now visible
    expect(dividerK.style.display).toBe('none'); // kubernetes still hidden
  });

  it('a count->alpha round trip with no active search leaves every divider visible', () => {
    buildTagsFixture();
    runScript();

    document.querySelector('.tags-sort-btn[data-sort="count"]').click();
    document.querySelector('.tags-sort-btn[data-sort="alpha"]').click();

    const dividers = document.querySelectorAll('.tag-cloud .tag-letter-divider');
    expect(dividers.length).toBeGreaterThan(0);
    dividers.forEach((div) => {
      expect(div.style.display).not.toBe('none');
    });
  });

  // =========================================================================
  // Combined interactions: multi-select + sort
  // =========================================================================

  it('multi-select classes and badge survive the DOM detach/re-append from toggling count -> alpha sort', () => {
    buildTagsFixture();
    runScript();

    document
      .querySelector('.tag[data-tag="aws"]')
      .dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    document
      .querySelector('.tag[data-tag="docker"]')
      .dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(document.getElementById('tags-selected-badge').textContent).toBe('2개 선택됨');

    document.querySelector('.tags-sort-btn[data-sort="count"]').click();

    // applySortToDom('count') removes every .tag element from .tag-cloud and
    // re-appends them in count order; selection state lives on the elements'
    // own classList (not re-derived from a data structure), so it must
    // survive the detach/re-append.
    let awsTag = document.querySelector('.tag[data-tag="aws"]');
    let dockerTag = document.querySelector('.tag[data-tag="docker"]');
    let kubernetesTag = document.querySelector('.tag[data-tag="kubernetes"]');
    expect(awsTag.classList.contains('tag--selected')).toBe(true);
    expect(dockerTag.classList.contains('tag--selected')).toBe(true);
    expect(kubernetesTag.classList.contains('tag--dimmed')).toBe(true);
    expect(document.getElementById('tags-selected-badge').textContent).toBe('2개 선택됨');

    document.querySelector('.tags-sort-btn[data-sort="alpha"]').click();

    awsTag = document.querySelector('.tag[data-tag="aws"]');
    dockerTag = document.querySelector('.tag[data-tag="docker"]');
    expect(awsTag.classList.contains('tag--selected')).toBe(true);
    expect(dockerTag.classList.contains('tag--selected')).toBe(true);
    expect(document.getElementById('tags-selected-badge').textContent).toBe('2개 선택됨');
    expect(JSON.parse(localStorage.getItem('tags-selected'))).toEqual(['aws', 'docker']);
  });

  // =========================================================================
  // Lazy-render: IntersectionObserver -> fetch -> renderSection
  // =========================================================================

  it('eagerly preloads /tags-data.json on the first tag-cloud click (once)', async () => {
    buildTagsFixture();
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    document
      .querySelector('.tag-cloud')
      .dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(window.fetch.mock.calls[0][0]).toMatch(/tags-data\.json/);
  });

  it('fetches /tags-data.json and renders a section when it scrolls into view', async () => {
    buildTagsFixture();
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const awsSection = document.getElementById('aws');
    observer._trigger(awsSection);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(awsSection.getAttribute('data-loaded')).toBe('1');
  });

  it('renders escaped post items and related-tag pills into a section exactly once', async () => {
    buildTagsFixture();
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const awsSection = document.getElementById('aws');
    observer._trigger(awsSection);
    await flushMicrotasks();

    // Section should now be rendered with escaped content and marked loaded.
    expect(awsSection.getAttribute('data-loaded')).toBe('1');
    expect(awsSection.innerHTML).toContain('&lt;A&gt;'); // XSS-safe escaping of "Post <A>"
    expect(awsSection.querySelectorAll('.tag-section-item').length).toBe(2);
    const pill = awsSection.querySelector('.tag-related-pill[data-related-tag="docker"]');
    expect(pill).not.toBeNull();

    // Clicking the rendered related pill scrolls to + ensures the "docker"
    // section is loaded, via the document-level delegated click listener.
    pill.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    await flushMicrotasks();

    expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
    expect(document.getElementById('docker').getAttribute('data-loaded')).toBe('1');
  });

  it('does not re-render or re-fetch a section that is already marked data-loaded', async () => {
    buildTagsFixture();
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const awsSection = document.getElementById('aws');
    awsSection.setAttribute('data-loaded', '1');
    const originalHtml = awsSection.innerHTML;

    observer._trigger(awsSection);
    await flushMicrotasks();

    expect(window.fetch).not.toHaveBeenCalled();
    expect(awsSection.innerHTML).toBe(originalHtml);
  });

  it('renders an empty post list without throwing when a tag has no posts', async () => {
    buildTagsFixture();
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    const kubernetesSection = document.getElementById('kubernetes');
    observer._trigger(kubernetesSection);
    await flushMicrotasks();

    expect(kubernetesSection.getAttribute('data-loaded')).toBe('1');
    expect(kubernetesSection.querySelectorAll('.tag-section-item').length).toBe(0);
    expect(kubernetesSection.querySelector('.tag-related')).toBeNull(); // no `related` entries
  });

  it('resets the data promise and does not throw when the fetch rejects', async () => {
    buildTagsFixture();
    window.fetch = stubFetch(null, { throws: true });
    runScript();

    await expect(
      (async () => {
        document.querySelector('.tag-cloud').dispatchEvent(
          new MouseEvent('click', { bubbles: true, cancelable: true })
        );
        await flushMicrotasks();
      })()
    ).resolves.not.toThrow();

    const awsSection = document.getElementById('aws');
    expect(awsSection.getAttribute('data-loaded')).toBeNull();
  });

  it('loadTagsData resolves null and resets its cached promise when the HTTP response is not ok', async () => {
    buildTagsFixture();
    window.fetch = stubFetch(null, { ok: false });
    runScript();

    const awsSection = document.getElementById('aws');
    observer._trigger(awsSection);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    // renderSection saw data === null (the !r.ok branch throws, is caught,
    // and resolves null) so the section is never marked loaded.
    expect(awsSection.getAttribute('data-loaded')).toBeNull();

    // The catch handler resets the cached promise to null, so a later
    // trigger (e.g. scrolling a second section into view) retries the fetch
    // instead of reusing the failed promise.
    const dockerSection = document.getElementById('docker');
    observer._trigger(dockerSection);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(2);
  });

  it('renderSection no-ops when the tags-data.json response has no entry for the section tag slug', async () => {
    buildTagsFixture();
    var dataWithoutDocker = { aws: MOCK_DATA.aws, kubernetes: MOCK_DATA.kubernetes }; // no "docker" key
    window.fetch = stubFetch(dataWithoutDocker);
    runScript();

    const dockerSection = document.getElementById('docker');
    observer._trigger(dockerSection);
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    // data[slug] is undefined, so renderSection's `if (!tagData) return;`
    // guard fires: the section is never marked loaded and stays un-rendered.
    expect(dockerSection.getAttribute('data-loaded')).toBeNull();
    expect(dockerSection.querySelector('.tag-section-list')).toBeNull();
  });

  it('renders zero list items without throwing when tagData.posts is not an array', async () => {
    buildTagsFixture();
    var malformedData = {
      aws: { related: ['Docker'], posts: null }, // posts missing/non-array
    };
    window.fetch = stubFetch(malformedData);
    runScript();

    const awsSection = document.getElementById('aws');
    observer._trigger(awsSection);
    await flushMicrotasks();

    // Array.isArray(tagData.posts) is false, so the post-list loop is
    // skipped entirely, but the section is still marked loaded and the
    // (unrelated) related-pills branch still renders normally.
    expect(awsSection.getAttribute('data-loaded')).toBe('1');
    expect(awsSection.querySelectorAll('.tag-section-item').length).toBe(0);
    expect(awsSection.querySelector('.tag-section-list')).not.toBeNull();
    expect(awsSection.querySelector('.tag-related-pill[data-related-tag="docker"]')).not.toBeNull();
  });

  it('ensureSectionLoaded no-ops for a section element that lacks data-section-tag', async () => {
    buildTagsFixture();
    const strayNode = document.createElement('section');
    strayNode.className = 'tag-section';
    strayNode.id = 'stray';
    strayNode.innerHTML = '<div class="tag-section-header">Stray</div>';
    document.getElementById('tags-top').appendChild(strayNode);

    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    observer._trigger(strayNode);
    await flushMicrotasks();

    // `var slug = section.getAttribute('data-section-tag'); if (!slug) return;`
    // fires before loadTagsData() is ever called.
    expect(window.fetch).not.toHaveBeenCalled();
    expect(strayNode.getAttribute('data-loaded')).toBeNull();
  });

  // =========================================================================
  // Hash navigation
  // =========================================================================

  it('eagerly loads the section matching location.hash on init', async () => {
    window.location.hash = '#aws';
    buildTagsFixture();
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    const awsSection = document.getElementById('aws');
    expect(awsSection.getAttribute('data-loaded')).toBe('1');
  });

  it('ignores location.hash pointing at a non tag-section element', async () => {
    window.location.hash = '#tags-top'; // exists in the fixture but is not a .tag-section
    buildTagsFixture();
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    await flushMicrotasks();

    expect(window.fetch).not.toHaveBeenCalled();
  });

  it('loads the newly-hashed section again on a hashchange event', async () => {
    buildTagsFixture();
    window.fetch = stubFetch(MOCK_DATA);
    runScript();

    await flushMicrotasks();
    expect(window.fetch).not.toHaveBeenCalled(); // no hash on init

    window.location.hash = '#docker';
    window.dispatchEvent(new Event('hashchange'));
    await flushMicrotasks();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    expect(document.getElementById('docker').getAttribute('data-loaded')).toBe('1');
  });
});
