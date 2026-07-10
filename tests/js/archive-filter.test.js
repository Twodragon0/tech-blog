// Regression tests for assets/js/archive-filter.js
//
// archive-filter.js is a standalone IIFE that:
//   1. Bails immediately when #archive-search is missing from the DOM.
//   2. Lazy-hydrates /archive-data.json into .archive-year > .archive-month
//      > .archive-list <li> rows (renderItem), then runs the initial filter
//      pass (applyFilters(false)) — skipping the pre-hydration pass so the
//      empty-state never flashes before real data loads.
//   3. Filters the hydrated items by category (filter buttons) and/or a
//      debounced search string (title/tag substring match), toggling
//      `is-hidden` on non-matching items and hiding month/year containers
//      that have no visible children.
//   4. Persists {filter, search} to localStorage and restores them on load.
//   5. Supports a reset button, tag-chip-click-to-search, and "/"-focus /
//      Escape-clear keyboard shortcuts.
//
// We evaluate the IIFE with new Function() after each test sets up its own
// DOM fixture, matching the pattern used by the other tests in this suite.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { stubFetch } from './_fixtures.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/archive-filter.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

/** Drain enough microtask ticks for nested promise chains to settle. */
async function flushMicrotasks(n = 8) {
  for (let i = 0; i < n; i++) {
    await Promise.resolve();
  }
}

/**
 * Build an archive-page-like DOM fixture: search input, filter buttons,
 * empty-state message with reset button, visible-count stat, and one
 * `.archive-year[data-year]` > `.archive-month[data-month]` > `.archive-list`
 * per entry in `years`. Each `.archive-list` starts empty with
 * aria-busy="true", matching the real Jekyll-rendered stub markup.
 */
function buildArchiveFixture({
  years = [{ year: '2026', months: ['01'] }],
  filters = ['all', 'security', 'cloud'],
  includeKbdHint = true,
} = {}) {
  const filterBtnsHtml = filters
    .map((f) => `<button class="archive-filter" data-filter="${f}" type="button">${f}</button>`)
    .join('\n');

  const yearsHtml = years
    .map(
      (y) => `
        <section class="archive-year" data-year="${y.year}">
          ${y.months
            .map(
              (m) => `
                <div class="archive-month" data-month="${m}">
                  <ul class="archive-list" aria-busy="true"></ul>
                </div>
              `
            )
            .join('\n')}
        </section>
      `
    )
    .join('\n');

  document.body.innerHTML = `
    <div class="archive-page">
      <div class="archive-toolbar">
        <input id="archive-search" type="text" />
        ${includeKbdHint ? '<span class="search-kbd">/</span>' : ''}
        <div class="archive-filters">${filterBtnsHtml}</div>
      </div>
      <div class="archive-stats">
        <span id="archive-visible-count" data-stat-number="0">0</span>
      </div>
      <div class="archive-empty" style="display:none">
        No results
        <button class="archive-empty-reset" type="button">Reset</button>
      </div>
      ${yearsHtml}
    </div>
  `;
}

/** Minimal post shape expected by renderItem() in archive-filter.js. */
function makePost(overrides = {}) {
  return {
    u: '/posts/default',
    t: 'Default Title',
    d: '2026-01-01',
    x: '2026-01-01T00:00:00Z',
    c: 'security',
    tags: [],
    ...overrides,
  };
}

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

describe('archive-filter.js', () => {
  let originalScrollIntoView;

  beforeEach(() => {
    document.body.innerHTML = '';
    try {
      window.localStorage.clear();
    } catch (_e) {
      // some jsdom versions throw on cleared storage; ignore.
    }
    delete window.fetch;
    // jsdom has no layout engine, so Element.prototype.scrollIntoView is
    // undefined. The tag-chip click handler calls it on the toolbar.
    originalScrollIntoView = Element.prototype.scrollIntoView;
    Element.prototype.scrollIntoView = vi.fn();
  });

  afterEach(() => {
    vi.useRealTimers();
    delete window.fetch;
    document.body.innerHTML = '';
    Element.prototype.scrollIntoView = originalScrollIntoView;
    try {
      window.localStorage.clear();
    } catch (_e) {
      // ignore
    }
  });

  // =========================================================================
  // Guard: no #archive-search
  // =========================================================================

  it('bails out and never calls fetch when #archive-search is missing', () => {
    document.body.innerHTML = '<div class="archive-page"></div>';
    window.fetch = stubFetch({});
    runScript();
    expect(window.fetch).not.toHaveBeenCalled();
  });

  // =========================================================================
  // Hydration
  // =========================================================================

  it('hydrates archive-data.json into the matching year/month .archive-list', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Post One', u: '/posts/one', c: 'security', tags: ['sec', 'cloud'] }),
          makePost({ t: 'Post Two', u: '/posts/two', c: 'cloud', tags: [] }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    const list = document.querySelector('.archive-month[data-month="01"] .archive-list');
    const rendered = list.querySelectorAll('.archive-item');
    expect(rendered.length).toBe(2);
    expect(list.hasAttribute('aria-busy')).toBe(false);
    expect(document.querySelector('.archive-year[data-year="2026"]').getAttribute('data-loaded')).toBe('1');
  });

  it('renders category badge, tag chips, and excerpt only when present on the post', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({
            t: 'Full Post',
            c: 'security',
            tags: ['zero-day', 'csp'],
            ex: 'An excerpt summary',
          }),
          makePost({ t: 'Bare Post', c: '', tags: [], ex: '' }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    const items = document.querySelectorAll('.archive-item');
    const full = items[0];
    const bare = items[1];

    expect(full.querySelector('.category-badge')).not.toBeNull();
    expect(full.querySelectorAll('.archive-tag-chip').length).toBe(2);
    expect(full.querySelector('.archive-item-excerpt')).not.toBeNull();

    expect(bare.querySelector('.category-badge')).toBeNull();
    expect(bare.querySelector('.archive-tag-chips')).toBeNull();
    expect(bare.querySelector('.archive-item-excerpt')).toBeNull();
  });

  it('escapes HTML in the rendered title to prevent XSS', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [makePost({ t: '<script>alert(1)</script>', u: '/posts/xss' })],
      },
    });
    runScript();
    await flushMicrotasks();

    const link = document.querySelector('.archive-item-title');
    // The raw tag must never appear as an actual element in the DOM.
    expect(document.querySelector('.archive-item script')).toBeNull();
    expect(link.textContent).toBe('<script>alert(1)</script>');
    expect(link.innerHTML).not.toContain('<script>');
  });

  it('updates the visible count to the number of hydrated items', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [makePost({ t: 'A' }), makePost({ t: 'B' }), makePost({ t: 'C' })],
      },
    });
    runScript();
    await flushMicrotasks();

    expect(document.getElementById('archive-visible-count').textContent).toBe('3');
  });

  it('leaves the list empty (aria-busy intact) and does not throw when the fetch rejects', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch(null, { throws: true });

    await expect(
      (async () => {
        runScript();
        await flushMicrotasks();
      })()
    ).resolves.not.toThrow();

    const list = document.querySelector('.archive-list');
    expect(list.querySelectorAll('.archive-item').length).toBe(0);
    expect(list.hasAttribute('aria-busy')).toBe(true);
  });

  // =========================================================================
  // Category filter buttons
  // =========================================================================

  it('filters items by category when a filter button is clicked', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Sec Post', c: 'security' }),
          makePost({ t: 'Cloud Post', c: 'cloud' }),
          makePost({ t: 'Sec Post 2', c: 'security' }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    document.querySelector('.archive-filter[data-filter="security"]').click();

    const items = Array.from(document.querySelectorAll('.archive-item'));
    const visible = items.filter((i) => !i.classList.contains('is-hidden'));
    const hidden = items.filter((i) => i.classList.contains('is-hidden'));

    expect(visible.length).toBe(2);
    expect(hidden.length).toBe(1);
    visible.forEach((i) => expect(i.getAttribute('data-categories')).toContain('security'));
    expect(document.getElementById('archive-visible-count').textContent).toBe('2');
  });

  it('marks the clicked filter button active and deactivates the others', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({ 2026: { '01': [makePost()] } });
    runScript();
    await flushMicrotasks();

    const allBtn = document.querySelector('.archive-filter[data-filter="all"]');
    const secBtn = document.querySelector('.archive-filter[data-filter="security"]');
    expect(allBtn.classList.contains('active')).toBe(true);

    secBtn.click();
    expect(secBtn.classList.contains('active')).toBe(true);
    expect(allBtn.classList.contains('active')).toBe(false);
  });

  // =========================================================================
  // Search input (debounced)
  // =========================================================================

  it('filters items by title substring after the search debounce fires', async () => {
    vi.useFakeTimers();
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [makePost({ t: 'Kubernetes Security Guide' }), makePost({ t: 'FinOps Basics' })],
      },
    });
    runScript();
    await flushMicrotasks();

    const searchInput = document.getElementById('archive-search');
    searchInput.value = 'kubernetes';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));

    // Not yet applied — debounce is 180ms.
    vi.advanceTimersByTime(100);
    let items = Array.from(document.querySelectorAll('.archive-item'));
    expect(items.filter((i) => i.classList.contains('is-hidden')).length).toBe(0);

    vi.advanceTimersByTime(100);
    items = Array.from(document.querySelectorAll('.archive-item'));
    const visible = items.filter((i) => !i.classList.contains('is-hidden'));
    expect(visible.length).toBe(1);
    expect(visible[0].getAttribute('data-title')).toContain('kubernetes');
  });

  it('filters items by tag substring match via search', async () => {
    vi.useFakeTimers();
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Post A', tags: ['zero-trust'] }),
          makePost({ t: 'Post B', tags: ['finops'] }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    const searchInput = document.getElementById('archive-search');
    searchInput.value = 'zero-trust';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    vi.advanceTimersByTime(200);

    const visible = Array.from(document.querySelectorAll('.archive-item')).filter(
      (i) => !i.classList.contains('is-hidden')
    );
    expect(visible.length).toBe(1);
    expect(visible[0].getAttribute('data-tags')).toContain('zero-trust');
  });

  // =========================================================================
  // Empty-state handling
  // =========================================================================

  it('shows the empty-state message when no items match the filter+search combo', async () => {
    vi.useFakeTimers();
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: { '01': [makePost({ t: 'Only Post', c: 'security' })] },
    });
    runScript();
    await flushMicrotasks();

    expect(document.querySelector('.archive-empty').style.display).toBe('none');

    const searchInput = document.getElementById('archive-search');
    searchInput.value = 'nonexistent-term';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    vi.advanceTimersByTime(200);

    expect(document.querySelector('.archive-empty').style.display).toBe('');
    expect(document.getElementById('archive-visible-count').textContent).toBe('0');
  });

  // =========================================================================
  // Month/year container visibility
  // =========================================================================

  it('hides a month container (and the year, if it was the only visible month) when all its items are filtered out', async () => {
    buildArchiveFixture({
      years: [{ year: '2026', months: ['01', '02'] }],
    });
    window.fetch = stubFetch({
      2026: {
        '01': [makePost({ t: 'Jan Post', c: 'security' })],
        '02': [makePost({ t: 'Feb Post', c: 'cloud' })],
      },
    });
    runScript();
    await flushMicrotasks();

    document.querySelector('.archive-filter[data-filter="security"]').click();

    const janMonth = document.querySelector('.archive-month[data-month="01"]');
    const febMonth = document.querySelector('.archive-month[data-month="02"]');
    expect(janMonth.style.display).toBe('');
    expect(febMonth.style.display).toBe('none');
    // The year still has a visible month (January), so it stays visible.
    expect(document.querySelector('.archive-year[data-year="2026"]').style.display).toBe('');
  });

  it('hides the year container entirely when every month under it has zero visible items', async () => {
    buildArchiveFixture({ years: [{ year: '2026', months: ['01'] }] });
    window.fetch = stubFetch({
      2026: { '01': [makePost({ t: 'Only Cloud Post', c: 'cloud' })] },
    });
    runScript();
    await flushMicrotasks();

    document.querySelector('.archive-filter[data-filter="security"]').click();

    expect(document.querySelector('.archive-month[data-month="01"]').style.display).toBe('none');
    expect(document.querySelector('.archive-year[data-year="2026"]').style.display).toBe('none');
  });

  // =========================================================================
  // Reset button
  // =========================================================================

  it('reset button clears the search, restores the "all" filter, and re-shows all items', async () => {
    vi.useFakeTimers();
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [makePost({ t: 'Sec Post', c: 'security' }), makePost({ t: 'Cloud Post', c: 'cloud' })],
      },
    });
    runScript();
    await flushMicrotasks();

    const searchInput = document.getElementById('archive-search');
    document.querySelector('.archive-filter[data-filter="security"]').click();
    searchInput.value = 'sec';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    vi.advanceTimersByTime(200);

    // Sanity check: filter+search combo narrowed results before reset.
    let hidden = Array.from(document.querySelectorAll('.archive-item')).filter((i) =>
      i.classList.contains('is-hidden')
    );
    expect(hidden.length).toBe(1);

    document.querySelector('.archive-empty-reset').click();

    expect(searchInput.value).toBe('');
    expect(window.localStorage.getItem('archive_search')).toBe('');
    expect(window.localStorage.getItem('archive_filter')).toBe('all');
    expect(document.querySelector('.archive-filter[data-filter="all"]').classList.contains('active')).toBe(true);
    hidden = Array.from(document.querySelectorAll('.archive-item')).filter((i) =>
      i.classList.contains('is-hidden')
    );
    expect(hidden.length).toBe(0);
  });

  // =========================================================================
  // Tag chip click-to-search
  // =========================================================================

  it('clicking a tag chip sets the search input to that tag and filters by it', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Post A', tags: ['zero-trust'] }),
          makePost({ t: 'Post B', tags: ['finops'] }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    const chip = document.querySelector('.archive-tag-chip[data-tag="zero-trust"]');
    chip.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(document.getElementById('archive-search').value).toBe('zero-trust');
    const visible = Array.from(document.querySelectorAll('.archive-item')).filter(
      (i) => !i.classList.contains('is-hidden')
    );
    expect(visible.length).toBe(1);
    expect(visible[0].getAttribute('data-tags')).toContain('zero-trust');
  });

  it('hides the keyboard hint when a tag chip is clicked', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: { '01': [makePost({ t: 'Post A', tags: ['zero-trust'] })] },
    });
    runScript();
    await flushMicrotasks();

    const kbdHint = document.querySelector('.search-kbd');
    const chip = document.querySelector('.archive-tag-chip[data-tag="zero-trust"]');
    chip.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(kbdHint.style.display).toBe('none');
  });

  // =========================================================================
  // localStorage persistence
  // =========================================================================

  it('persists the active filter and search string to localStorage after filtering', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({ 2026: { '01': [makePost({ c: 'security' })] } });
    runScript();
    await flushMicrotasks();

    document.querySelector('.archive-filter[data-filter="cloud"]').click();

    expect(window.localStorage.getItem('archive_filter')).toBe('cloud');
    expect(window.localStorage.getItem('archive_search')).toBe('');
  });

  it('restores a previously saved filter and search from localStorage on load', async () => {
    window.localStorage.setItem('archive_filter', 'cloud');
    window.localStorage.setItem('archive_search', 'zero-trust');
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Cloud Zero Trust', c: 'cloud', tags: ['zero-trust'] }),
          makePost({ t: 'Other Post', c: 'security', tags: [] }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    expect(document.getElementById('archive-search').value).toBe('zero-trust');
    expect(document.querySelector('.archive-filter[data-filter="cloud"]').classList.contains('active')).toBe(true);

    const visible = Array.from(document.querySelectorAll('.archive-item')).filter(
      (i) => !i.classList.contains('is-hidden')
    );
    expect(visible.length).toBe(1);
  });

  // =========================================================================
  // Keyboard shortcuts
  // =========================================================================

  it('focuses the search input when "/" is pressed outside of it', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({ 2026: { '01': [makePost()] } });
    runScript();
    await flushMicrotasks();

    document.body.focus();
    document.dispatchEvent(new window.KeyboardEvent('keydown', { key: '/', bubbles: true, cancelable: true }));

    expect(document.activeElement).toBe(document.getElementById('archive-search'));
  });

  it('clears the search input and re-applies filters when Escape is pressed while focused', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: { '01': [makePost({ t: 'Post A', c: 'security' })] },
    });
    runScript();
    await flushMicrotasks();

    const searchInput = document.getElementById('archive-search');
    searchInput.focus();
    searchInput.value = 'post';
    document.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }));

    expect(searchInput.value).toBe('');
    expect(window.localStorage.getItem('archive_search')).toBe('');
  });

  // =========================================================================
  // Keyboard hint (.search-kbd) visibility
  // =========================================================================

  it('hides the keyboard hint on focus and restores it on blur when the input is empty', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({ 2026: { '01': [makePost()] } });
    runScript();
    await flushMicrotasks();

    const searchInput = document.getElementById('archive-search');
    const kbdHint = document.querySelector('.search-kbd');

    searchInput.dispatchEvent(new window.Event('focus'));
    expect(kbdHint.style.display).toBe('none');

    searchInput.value = '';
    searchInput.dispatchEvent(new window.Event('blur'));
    expect(kbdHint.style.display).toBe('');
  });

  it('keeps the keyboard hint hidden on blur when the input still has a value', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({ 2026: { '01': [makePost()] } });
    runScript();
    await flushMicrotasks();

    const searchInput = document.getElementById('archive-search');
    const kbdHint = document.querySelector('.search-kbd');

    // Focus hides the hint first (matches real usage: focus, type, blur).
    searchInput.dispatchEvent(new window.Event('focus'));
    expect(kbdHint.style.display).toBe('none');

    searchInput.value = 'still typing';
    searchInput.dispatchEvent(new window.Event('blur'));

    // Blur only restores the hint when the input is empty — a non-empty
    // value must leave it hidden.
    expect(kbdHint.style.display).toBe('none');
  });

  // =========================================================================
  // Combined filter + search interaction states
  //
  // The single-feature tests above exercise the category filter and the
  // debounced search independently. applyFilters() ANDs them together
  // (`matchFilter && matchSearch`), so these tests target the interaction
  // states a per-feature test can't reach: both axes active at once,
  // changing one axis while the other holds, and state restored from
  // localStorage feeding into a later user action.
  // =========================================================================

  it('applies category filter AND search together — only items matching both survive', async () => {
    vi.useFakeTimers();
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Zero Trust Guide', c: 'security' }),
          makePost({ t: 'FinOps Basics', c: 'security' }),
          makePost({ t: 'Zero Trust Cloud', c: 'cloud' }),
          makePost({ t: 'Random Post', c: 'cloud' }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    document.querySelector('.archive-filter[data-filter="security"]').click();

    const searchInput = document.getElementById('archive-search');
    searchInput.value = 'zero';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    vi.advanceTimersByTime(200);

    const items = Array.from(document.querySelectorAll('.archive-item'));
    const visible = items.filter((i) => !i.classList.contains('is-hidden'));

    // "FinOps Basics" matches the filter but not the search; "Zero Trust
    // Cloud" matches the search but not the filter. Neither is enough alone.
    expect(visible.length).toBe(1);
    expect(visible[0].getAttribute('data-title')).toBe('zero trust guide');
    expect(document.getElementById('archive-visible-count').textContent).toBe('1');
  });

  it('clearing the search while a category filter is active keeps the filter applied', async () => {
    vi.useFakeTimers();
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Zero Trust Guide', c: 'security' }),
          makePost({ t: 'FinOps Basics', c: 'security' }),
          makePost({ t: 'Zero Trust Cloud', c: 'cloud' }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    document.querySelector('.archive-filter[data-filter="security"]').click();
    const searchInput = document.getElementById('archive-search');
    searchInput.value = 'zero';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    vi.advanceTimersByTime(200);

    // Clear the search box — the category filter must remain in effect.
    searchInput.value = '';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    vi.advanceTimersByTime(200);

    const items = Array.from(document.querySelectorAll('.archive-item'));
    const visible = items.filter((i) => !i.classList.contains('is-hidden'));

    expect(visible.length).toBe(2);
    visible.forEach((i) => expect(i.getAttribute('data-categories')).toContain('security'));
    expect(
      document.querySelector('.archive-filter[data-filter="security"]').classList.contains('active')
    ).toBe(true);
  });

  it('switching the category filter while a search is active keeps the search applied', async () => {
    vi.useFakeTimers();
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Zero Trust Guide', c: 'security' }),
          makePost({ t: 'Zero Trust Cloud', c: 'cloud' }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    document.querySelector('.archive-filter[data-filter="security"]').click();
    const searchInput = document.getElementById('archive-search');
    searchInput.value = 'zero';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    vi.advanceTimersByTime(200);

    // Switching category buttons must not clear the in-flight search term —
    // the click handler only touches currentFilter, never currentSearch.
    document.querySelector('.archive-filter[data-filter="cloud"]').click();

    expect(searchInput.value).toBe('zero');
    const items = Array.from(document.querySelectorAll('.archive-item'));
    const visible = items.filter((i) => !i.classList.contains('is-hidden'));
    expect(visible.length).toBe(1);
    expect(visible[0].getAttribute('data-categories')).toContain('cloud');
  });

  it('hides both month containers and shows the empty-state when a filter+search combo matches nothing', async () => {
    vi.useFakeTimers();
    buildArchiveFixture({ years: [{ year: '2026', months: ['01', '02'] }] });
    window.fetch = stubFetch({
      2026: {
        '01': [makePost({ t: 'Alpha Post', c: 'security' })],
        '02': [makePost({ t: 'Beta Post', c: 'cloud' })],
      },
    });
    runScript();
    await flushMicrotasks();

    document.querySelector('.archive-filter[data-filter="security"]').click();
    const searchInput = document.getElementById('archive-search');
    searchInput.value = 'nonexistent-term';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    vi.advanceTimersByTime(200);

    // Jan's post fails the search; Feb's post fails the filter — combined,
    // every month (and the year) collapses, distinct from the single-axis
    // month/year-hide tests above.
    expect(document.querySelector('.archive-month[data-month="01"]').style.display).toBe('none');
    expect(document.querySelector('.archive-month[data-month="02"]').style.display).toBe('none');
    expect(document.querySelector('.archive-year[data-year="2026"]').style.display).toBe('none');
    expect(document.querySelector('.archive-empty').style.display).toBe('');
    expect(document.getElementById('archive-visible-count').textContent).toBe('0');
  });

  it('restores a saved filter+search combo from localStorage on init, then applies a further filter change on top of it', async () => {
    window.localStorage.setItem('archive_filter', 'cloud');
    window.localStorage.setItem('archive_search', 'alpha');
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Alpha One', c: 'cloud' }),
          makePost({ t: 'Beta Two', c: 'cloud' }),
          makePost({ t: 'Alpha Three', c: 'security' }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    // Restored combo: cloud + "alpha" → only "Alpha One" matches both.
    let visible = Array.from(document.querySelectorAll('.archive-item')).filter(
      (i) => !i.classList.contains('is-hidden')
    );
    expect(visible.length).toBe(1);
    expect(visible[0].getAttribute('data-title')).toBe('alpha one');

    // User interaction layered on top of the restored state: switch to
    // "all". The restored search term must remain in effect.
    document.querySelector('.archive-filter[data-filter="all"]').click();

    visible = Array.from(document.querySelectorAll('.archive-item')).filter(
      (i) => !i.classList.contains('is-hidden')
    );
    expect(visible.length).toBe(2);
    expect(document.getElementById('archive-search').value).toBe('alpha');
    expect(window.localStorage.getItem('archive_filter')).toBe('all');
    expect(window.localStorage.getItem('archive_search')).toBe('alpha');
  });

  it('tag-chip click narrows within an already-active category filter', async () => {
    buildArchiveFixture();
    window.fetch = stubFetch({
      2026: {
        '01': [
          makePost({ t: 'Cloud Zero Trust', c: 'cloud', tags: ['zero-trust'] }),
          makePost({ t: 'Security Zero Trust', c: 'security', tags: ['zero-trust'] }),
          makePost({ t: 'Cloud Other', c: 'cloud', tags: ['other-tag'] }),
        ],
      },
    });
    runScript();
    await flushMicrotasks();

    document.querySelector('.archive-filter[data-filter="cloud"]').click();

    const chip = document.querySelector(
      '.archive-item[data-categories="cloud"] .archive-tag-chip[data-tag="zero-trust"]'
    );
    chip.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true }));

    const items = Array.from(document.querySelectorAll('.archive-item'));
    const visible = items.filter((i) => !i.classList.contains('is-hidden'));

    // "Security Zero Trust" matches the chip-driven search but not the
    // still-active "cloud" filter; "Cloud Other" matches the filter but not
    // the search. Only the item matching both survives.
    expect(visible.length).toBe(1);
    expect(visible[0].getAttribute('data-title')).toBe('cloud zero trust');
    expect(
      document.querySelector('.archive-filter[data-filter="cloud"]').classList.contains('active')
    ).toBe(true);
  });
});
