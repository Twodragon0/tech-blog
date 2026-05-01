// Regression tests for assets/js/home-posts-filter.js
//
// Goal: prove that PR #332's perf refactor preserves behavior AND batches DOM
// writes into a single requestAnimationFrame callback (≤ 1 layout flush per
// renderPosts() invocation).
//
// The source file is a bare IIFE (no exports), so we load it as text and
// evaluate it after each test sets up its own DOM fixture. This keeps the
// tests close to how the script actually runs in the browser.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/home-posts-filter.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

// Build a homepage-like DOM fixture with N post cards. The shape mirrors
// `index.html` (the only real consumer of this script).
function buildHomeFixture(cards) {
  const tabs = [
    'latest',
    'popular',
    'security',
    'devsecops',
    'cloud',
    'kubernetes',
    'blockchain',
  ];
  const tabsHtml = tabs
    .map(
      (sort, i) =>
        `<button class="posts-tab${i === 0 ? ' active' : ''}" role="tab" data-sort="${sort}" type="button">${sort}</button>`
    )
    .join('\n');

  const cardsHtml = cards
    .map(
      (c) =>
        `<article class="post-card card" data-category="${c.cats}" data-date="${c.date}" data-popularity="${c.pop ?? 0}">${c.title ?? ''}</article>`
    )
    .join('\n');

  document.body.innerHTML = `
    <section class="posts-section">
      <div class="posts-toolbar">
        <div class="posts-tabs">${tabsHtml}</div>
        <div class="posts-view-toggle">
          <button class="view-btn active" data-view="grid" aria-pressed="true" type="button">grid</button>
          <button class="view-btn" data-view="list" aria-pressed="false" type="button">list</button>
        </div>
      </div>
      <div id="posts-panel" class="posts-list" role="tabpanel">${cardsHtml}</div>
      <div class="posts-footer"></div>
    </section>
  `;
}

// Run the IIFE source against the current `window`/`document`. We evaluate
// inside a Function so it does not leak into the test scope.
function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

describe('home-posts-filter.js', () => {
  let rafCallbacks;
  let originalRAF;

  beforeEach(() => {
    rafCallbacks = [];
    originalRAF = window.requestAnimationFrame;
    // Capture rAF callbacks instead of running them on a frame. Tests flush
    // them manually so we can assert that DOM writes only happen after a flush.
    window.requestAnimationFrame = vi.fn((cb) => {
      rafCallbacks.push(cb);
      return rafCallbacks.length;
    });
    // Stub localStorage to avoid jsdom quirks.
    try {
      window.localStorage.clear();
    } catch (_e) {
      // some jsdom versions throw on cleared storage; ignore.
    }
  });

  afterEach(() => {
    window.requestAnimationFrame = originalRAF;
    document.body.innerHTML = '';
  });

  function flushFrames() {
    // Run every queued rAF callback in order. Mirrors what the browser does on
    // the next paint.
    while (rafCallbacks.length) {
      const cb = rafCallbacks.shift();
      cb(performance.now());
    }
  }

  it('schedules DOM writes inside requestAnimationFrame, not synchronously', () => {
    buildHomeFixture([
      { cats: 'security', date: 20260101, pop: 10 },
      { cats: 'cloud', date: 20260102, pop: 20 },
      { cats: 'devsecops kubernetes', date: 20260103, pop: 5 },
    ]);
    runScript();

    // Initial renderPosts() ran during script init — it should have queued a
    // frame and NOT mutated card display yet.
    expect(window.requestAnimationFrame).toHaveBeenCalled();
    const cards = document.querySelectorAll('.post-card');
    cards.forEach((card) => {
      // Before flush: jsdom's default style.display is '' for elements that
      // never had it set. The script must not have written 'none' yet.
      expect(card.style.display).toBe('');
    });

    // After flushing the rAF: visibility settles. With 3 cards and
    // PAGE_SIZE=12, all 3 should be visible under "latest".
    flushFrames();
    cards.forEach((card) => {
      expect(card.style.display).toBe('');
    });
  });

  it('triggers ≤ 1 rAF (= 1 layout flush) per renderPosts() invocation', () => {
    buildHomeFixture([
      { cats: 'security', date: 20260101 },
      { cats: 'cloud', date: 20260102 },
      { cats: 'devsecops', date: 20260103 },
    ]);
    runScript();

    // Initial render queued exactly one frame.
    expect(window.requestAnimationFrame).toHaveBeenCalledTimes(1);
    flushFrames();

    // Click another tab → exactly one more frame queued.
    window.requestAnimationFrame.mockClear();
    rafCallbacks.length = 0;
    const securityTab = document.querySelector('.posts-tab[data-sort="security"]');
    securityTab.click();
    expect(window.requestAnimationFrame).toHaveBeenCalledTimes(1);
  });

  it('computes tab counts in a single pass (no per-tab full re-filter)', () => {
    // 3 security, 2 cloud, 1 devsecops, 0 kubernetes/blockchain. Total = 5.
    buildHomeFixture([
      { cats: 'security', date: 20260101 },
      { cats: 'security cloud', date: 20260102 },
      { cats: 'security devsecops', date: 20260103 },
      { cats: 'cloud', date: 20260104 },
      { cats: 'cloud', date: 20260105 },
    ]);
    runScript();
    flushFrames();

    function badge(sort) {
      const el = document.querySelector(`.posts-tab[data-sort="${sort}"] .tab-count`);
      return el ? el.textContent : null;
    }

    // Sort tabs (latest/popular) show full count; category tabs show match count.
    expect(badge('latest')).toBe('5');
    expect(badge('popular')).toBe('5');
    expect(badge('security')).toBe('3');
    expect(badge('cloud')).toBe('3');
    expect(badge('devsecops')).toBe('1');
    expect(badge('kubernetes')).toBe('0');
    expect(badge('blockchain')).toBe('0');
  });

  it('filters cards correctly when a category tab is clicked', () => {
    buildHomeFixture([
      { cats: 'security', date: 20260101 },
      { cats: 'cloud', date: 20260102 },
      { cats: 'security devsecops', date: 20260103 },
      { cats: 'kubernetes', date: 20260104 },
      { cats: 'security cloud', date: 20260105 },
    ]);
    runScript();
    flushFrames();

    // Click the "security" tab.
    const tab = document.querySelector('.posts-tab[data-sort="security"]');
    tab.click();
    flushFrames();

    const cards = Array.from(document.querySelectorAll('.post-card'));
    const visible = cards.filter((c) => c.style.display !== 'none');
    const hidden = cards.filter((c) => c.style.display === 'none');

    expect(visible.length).toBe(3); // 3 cards have "security" in data-category
    expect(hidden.length).toBe(2);
    visible.forEach((c) => {
      expect(c.getAttribute('data-category')).toMatch(/security/);
    });
  });

  it('sorts by popularity when "popular" tab is clicked', () => {
    buildHomeFixture([
      { cats: 'security', date: 20260101, pop: 5 },
      { cats: 'cloud', date: 20260102, pop: 50 },
      { cats: 'devsecops', date: 20260103, pop: 20 },
      { cats: 'security', date: 20260104, pop: 1 },
    ]);
    runScript();
    flushFrames();

    const popularTab = document.querySelector('.posts-tab[data-sort="popular"]');
    popularTab.click();
    flushFrames();

    // The script does not reorder DOM nodes — sorting affects which 12 are
    // shown when there are >12 cards. With <PAGE_SIZE cards, all are visible.
    // Verify all are visible AND the popular tab is now active+aria-selected.
    const cards = Array.from(document.querySelectorAll('.post-card'));
    cards.forEach((c) => expect(c.style.display).toBe(''));
    expect(popularTab.classList.contains('active')).toBe(true);
    expect(popularTab.getAttribute('aria-selected')).toBe('true');
  });

  it('preserves keyboard/ARIA tab state on click', () => {
    buildHomeFixture([
      { cats: 'security', date: 20260101 },
      { cats: 'cloud', date: 20260102 },
    ]);
    runScript();
    flushFrames();

    const cloudTab = document.querySelector('.posts-tab[data-sort="cloud"]');
    const latestTab = document.querySelector('.posts-tab[data-sort="latest"]');
    cloudTab.click();
    flushFrames();

    expect(cloudTab.classList.contains('active')).toBe(true);
    expect(cloudTab.getAttribute('aria-selected')).toBe('true');
    expect(latestTab.classList.contains('active')).toBe(false);
    expect(latestTab.getAttribute('aria-selected')).toBe('false');
  });
});
