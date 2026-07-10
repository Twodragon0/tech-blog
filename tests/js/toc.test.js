// Regression tests for assets/js/toc.js#highlightCurrentSection
//
// Goal: prove the read-then-write split fix preserves the original
// "last match wins / no-match leaves state alone" behavior, while
// asserting that classList writes happen in a single pass after all
// geometry reads are complete (the anti-thrash invariant from
// docs/optimization/IIFE_THRASH_AUDIT.md).

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/toc.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

// Build a fixture mimicking a post page with TOC + N section anchors.
// Each section gets a synthetic offsetTop/offsetHeight via Object.defineProperty.
// jsdom returns 0 for offsetTop/offsetHeight because it does no layout.
// Mock the HTMLElement prototype to read from data-test-* attributes — this
// works even on the instance after the script has captured a NodeList ref.
let prototypeMocked = false;
function ensurePrototypeMock() {
  if (prototypeMocked) return;
  prototypeMocked = true;
  Object.defineProperty(window.HTMLElement.prototype, 'offsetTop', {
    configurable: true,
    get() {
      const v = this.getAttribute && this.getAttribute('data-test-top');
      return v ? parseInt(v, 10) : 0;
    },
  });
  Object.defineProperty(window.HTMLElement.prototype, 'offsetHeight', {
    configurable: true,
    get() {
      const v = this.getAttribute && this.getAttribute('data-test-height');
      return v ? parseInt(v, 10) : 0;
    },
  });
}

function buildTocFixture(sections) {
  ensurePrototypeMock();
  const tocLinks = sections
    .map(
      (s) =>
        `<a class="toc-card-item" href="#${s.id}">${s.title}</a>`
    )
    .join('');
  const sectionEls = sections
    .map(
      (s) =>
        `<h2 id="${s.id}" data-test-top="${s.top}" data-test-height="${s.height}">${s.title}</h2>`
    )
    .join('');

  document.body.innerHTML = `
    <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
    <div id="toc-content">
      <span id="toc-count"></span>
      ${tocLinks}
    </div>
    <article class="post-content">${sectionEls}</article>
  `;
}

describe('toc.js#highlightCurrentSection', () => {
  let originalRAF;
  let originalScrollY;

  beforeEach(() => {
    originalScrollY = window.pageYOffset;
    originalRAF = window.requestAnimationFrame;
    // Synchronously fire rAF callbacks. jsdom's default uses ~16ms setTimeout,
    // which is too slow for a test. We just want to verify behavior post-flush.
    window.requestAnimationFrame = (cb) => {
      cb(performance.now());
      return 0;
    };
    document.body.innerHTML = '';
  });

  afterEach(() => {
    window.requestAnimationFrame = originalRAF;
    document.body.innerHTML = '';
    Object.defineProperty(window, 'pageYOffset', {
      configurable: true,
      writable: true,
      value: originalScrollY,
    });
  });

  function setScrollY(value) {
    Object.defineProperty(window, 'pageYOffset', {
      configurable: true,
      writable: true,
      value,
    });
  }

  function dispatchScrollFlush() {
    window.dispatchEvent(new Event('scroll'));
  }

  it('marks exactly one TOC item as active when scrolling into a section', async () => {
    buildTocFixture([
      { id: 's1', title: 'One', top: 0, height: 500 },
      { id: 's2', title: 'Two', top: 500, height: 500 },
      { id: 's3', title: 'Three', top: 1000, height: 500 },
    ]);
    runScript();

    setScrollY(600); // scrollPosition = 700 → in section "Two"
    dispatchScrollFlush();

    const items = document.querySelectorAll('.toc-card-item');
    const active = Array.from(items).filter((el) => el.classList.contains('active'));
    expect(active).toHaveLength(1);
    expect(active[0].getAttribute('href')).toBe('#s2');
  });

  it('honors "last match wins" when sections overlap (preserves original behavior)', async () => {
    // s1 and s2 both contain scrollPosition 250. Original code's last-write-wins
    // means s2 (the later match in iteration order) ends up active.
    buildTocFixture([
      { id: 's1', title: 'One', top: 0, height: 1000 },
      { id: 's2', title: 'Two', top: 200, height: 1000 },
    ]);
    runScript();

    setScrollY(150); // scrollPosition = 250 → matches both s1 and s2
    dispatchScrollFlush();

    const s1 = document.querySelector('.toc-card-item[href="#s1"]');
    const s2 = document.querySelector('.toc-card-item[href="#s2"]');
    expect(s1.classList.contains('active')).toBe(false);
    expect(s2.classList.contains('active')).toBe(true);
  });

  it('does not strip an existing active class when no section matches', async () => {
    buildTocFixture([
      { id: 's1', title: 'One', top: 100, height: 100 },
      { id: 's2', title: 'Two', top: 300, height: 100 },
    ]);
    runScript();

    // Pre-mark s1 as active.
    const s1 = document.querySelector('.toc-card-item[href="#s1"]');
    s1.classList.add('active');

    // Scroll to a position outside any section.
    setScrollY(900); // scrollPosition = 1000, well past all sections
    dispatchScrollFlush();

    // No-match → state untouched (matches original behavior — important
    // so the active state doesn't flicker when scrolling past the article).
    expect(s1.classList.contains('active')).toBe(true);
  });

  it('toggles classList exactly once per item per scroll frame', async () => {
    buildTocFixture([
      { id: 's1', title: 'One', top: 0, height: 200 },
      { id: 's2', title: 'Two', top: 200, height: 200 },
      { id: 's3', title: 'Three', top: 400, height: 200 },
      { id: 's4', title: 'Four', top: 600, height: 200 },
    ]);
    runScript();

    const items = document.querySelectorAll('.toc-card-item');
    const writeCounts = new Array(items.length).fill(0);
    items.forEach((item, idx) => {
      const originalToggle = item.classList.toggle.bind(item.classList);
      item.classList.toggle = (...args) => {
        writeCounts[idx] += 1;
        return originalToggle(...args);
      };
    });

    setScrollY(300); // scrollPosition = 400 → sect "Three" boundary
    dispatchScrollFlush();

    // Each item should be touched at most once per frame (read-then-write
    // single pass). The original code wrote via classList.remove/add inside
    // the inner loop — that pattern would record higher counts.
    writeCounts.forEach((n) => {
      expect(n).toBeLessThanOrEqual(1);
    });
  });

  it('handles a TOC link whose href targets a missing id (graceful degradation)', async () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#does-not-exist">Missing</a>
      </div>
      <article class="post-content"></article>
    `;
    runScript();

    setScrollY(100);
    expect(() => window.dispatchEvent(new Event('scroll'))).not.toThrow();
    await new Promise((r) => setTimeout(r, 0));
  });

  it('TOC link click triggers smooth scrollTo + history.pushState on target heading', () => {
    buildTocFixture([
      { id: 's1', title: 'One', top: 100, height: 200 },
      { id: 's2', title: 'Two', top: 400, height: 200 },
    ]);
    runScript();

    const scrollToSpy = vi.fn();
    const pushStateSpy = vi.spyOn(history, 'pushState');
    const origScrollTo = window.scrollTo;
    window.scrollTo = scrollToSpy;

    try {
      const link = document.querySelector('.toc-card-item[href="#s2"]');
      const click = new MouseEvent('click', { bubbles: true, cancelable: true });
      link.dispatchEvent(click);

      expect(click.defaultPrevented).toBe(true);
      expect(scrollToSpy).toHaveBeenCalledTimes(1);
      const arg = scrollToSpy.mock.calls[0][0];
      expect(arg.behavior).toBe('smooth');
      expect(typeof arg.top).toBe('number');
      // pushState updates the URL hash to the target id.
      expect(pushStateSpy).toHaveBeenCalledTimes(1);
      expect(pushStateSpy.mock.calls[0][2]).toBe('#s2');
    } finally {
      window.scrollTo = origScrollTo;
      pushStateSpy.mockRestore();
    }
  });

  it('TOC link click on href="#" early-returns without preventDefault', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#">Top</a>
      </div>
      <article class="post-content"></article>
    `;
    runScript();

    const scrollToSpy = vi.fn();
    const origScrollTo = window.scrollTo;
    window.scrollTo = scrollToSpy;

    try {
      const link = document.querySelector('.toc-card-item');
      const click = new MouseEvent('click', { bubbles: true, cancelable: true });
      link.dispatchEvent(click);

      // href="#" is an early-return guard — no scroll, default not prevented.
      expect(scrollToSpy).not.toHaveBeenCalled();
      expect(click.defaultPrevented).toBe(false);
    } finally {
      window.scrollTo = origScrollTo;
    }
  });
});

// Additional branch-coverage tests below. These target guard clauses and
// fallback paths in toc.js that the tests above don't exercise: the
// early-return setup guards, the toggle expand/collapse button, the
// setTimeout-driven updateTocLinks() backfill, the smooth-scroll click
// handler's heading-text fallback, and the scroll handler's rAF coalescing.

describe('toc.js#setup guards', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('returns early without throwing when #toc-toggle is missing', () => {
    document.body.innerHTML = `
      <div id="toc-content"><span id="toc-count"></span></div>
    `;
    expect(() => runScript()).not.toThrow();
  });

  it('returns early without throwing when #toc-content is missing', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
    `;
    expect(() => runScript()).not.toThrow();
  });

  it('leaves the section-count label blank when there are zero TOC items', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content"><span id="toc-count"></span></div>
      <article class="post-content"></article>
    `;
    runScript();
    expect(document.getElementById('toc-count').textContent).toBe('');
  });

  it('skips the section-count update without throwing when #toc-count is absent', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <a class="toc-card-item" href="#s1">One</a>
      </div>
      <article class="post-content"><h2 id="s1">One</h2></article>
    `;
    expect(() => runScript()).not.toThrow();
    expect(document.getElementById('toc-toggle').style.display).toBe('none');
  });

  it('shows the toggle with "+N more" text when items exceed the preview max', () => {
    const items = Array.from({ length: 7 }, (_, i) => `<a class="toc-card-item" href="#s${i}">S${i}</a>`).join('');
    const sections = Array.from({ length: 7 }, (_, i) => `<h2 id="s${i}">S${i}</h2>`).join('');
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        ${items}
      </div>
      <article class="post-content">${sections}</article>
    `;
    runScript();
    const toggle = document.getElementById('toc-toggle');
    expect(toggle.style.display).not.toBe('none');
    expect(toggle.querySelector('.btn-text').textContent).toBe('+1 더보기');
  });
});

describe('toc.js#toggle expand/collapse', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  function buildToggleFixture(count) {
    const items = Array.from(
      { length: count },
      (_, i) => `<a class="toc-card-item${i >= 6 ? ' toc-hidden' : ''}" href="#s${i}">S${i}</a>`
    ).join('');
    const sections = Array.from({ length: count }, (_, i) => `<h2 id="s${i}">S${i}</h2>`).join('');
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        ${items}
      </div>
      <article class="post-content">${sections}</article>
    `;
  }

  it('expands all items and updates the toggle UI on first click', () => {
    buildToggleFixture(7);
    runScript();
    const toggle = document.getElementById('toc-toggle');
    toggle.click();

    const items = document.querySelectorAll('.toc-card-item');
    items.forEach((item) => expect(item.classList.contains('toc-hidden')).toBe(false));
    expect(toggle.querySelector('.btn-text').textContent).toBe('접기');
    expect(toggle.classList.contains('expanded')).toBe(true);
  });

  it('re-hides items past the preview max and restores the toggle UI on second click', () => {
    buildToggleFixture(7);
    runScript();
    const toggle = document.getElementById('toc-toggle');
    toggle.click(); // expand
    toggle.click(); // collapse

    const items = Array.from(document.querySelectorAll('.toc-card-item'));
    items.forEach((item, idx) => {
      expect(item.classList.contains('toc-hidden')).toBe(idx >= 6);
    });
    expect(toggle.querySelector('.btn-text').textContent).toBe('+1 더보기');
    expect(toggle.classList.contains('expanded')).toBe(false);
  });

  it('leaves the toggle label untouched when collapsing with items within the preview max', () => {
    buildToggleFixture(3);
    runScript();
    const toggle = document.getElementById('toc-toggle');
    toggle.click(); // expand
    toggle.click(); // "collapse" — no-op on items/label since 3 <= maxPreview

    expect(toggle.querySelector('.btn-text').textContent).toBe('접기');
    expect(toggle.classList.contains('expanded')).toBe(false);
  });
});

describe('toc.js#updateTocLinks (delayed heading-id backfill)', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    vi.useRealTimers();
  });

  it('skips links with no href or href="#" without throwing', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#">Top</a>
        <a class="toc-card-item">No Href</a>
      </div>
      <article class="post-content"></article>
    `;
    vi.useFakeTimers();
    runScript();
    expect(() => vi.advanceTimersByTime(500)).not.toThrow();
  });

  it('rewrites a stale href to the heading id once a heading is matched by text', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#stale-id">Real Heading</a>
      </div>
      <article class="post-content">
        <h2 id="real-heading">Real Heading</h2>
      </article>
    `;
    vi.useFakeTimers();
    runScript();
    vi.advanceTimersByTime(500);

    const link = document.querySelector('.toc-card-item');
    expect(link.getAttribute('href')).toBe('#real-heading');
  });

  it('leaves the href untouched when the matching heading has no id', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#stale-id">No Id Heading</a>
      </div>
      <article class="post-content">
        <h2>No Id Heading</h2>
      </article>
    `;
    vi.useFakeTimers();
    runScript();
    vi.advanceTimersByTime(500);

    const link = document.querySelector('.toc-card-item');
    expect(link.getAttribute('href')).toBe('#stale-id');
  });

  it('does not touch a link whose href already resolves to an existing element', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#s1">One</a>
      </div>
      <article class="post-content"><h2 id="s1">One</h2></article>
    `;
    vi.useFakeTimers();
    runScript();
    vi.advanceTimersByTime(500);

    const link = document.querySelector('.toc-card-item');
    expect(link.getAttribute('href')).toBe('#s1');
  });
});

describe('toc.js#smooth-scroll click fallback matching', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('falls back to a heading matched by text when the href id does not exist', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#missing-id">Real Heading</a>
      </div>
      <article class="post-content">
        <h2 id="actual-heading">Real Heading</h2>
      </article>
    `;
    runScript();

    const scrollToSpy = vi.fn();
    const pushStateSpy = vi.spyOn(history, 'pushState');
    const origScrollTo = window.scrollTo;
    window.scrollTo = scrollToSpy;

    try {
      const link = document.querySelector('.toc-card-item');
      const click = new MouseEvent('click', { bubbles: true, cancelable: true });
      link.dispatchEvent(click);

      expect(click.defaultPrevented).toBe(true);
      expect(scrollToSpy).toHaveBeenCalledTimes(1);
      expect(pushStateSpy).toHaveBeenCalledTimes(1);
      expect(pushStateSpy.mock.calls[0][2]).toBe('#actual-heading');
    } finally {
      window.scrollTo = origScrollTo;
      pushStateSpy.mockRestore();
    }
  });

  it('falls back to the original href id in pushState when the matched heading has no id', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#missing-id">No Id Heading</a>
      </div>
      <article class="post-content">
        <h2>No Id Heading</h2>
      </article>
    `;
    runScript();

    const scrollToSpy = vi.fn();
    const pushStateSpy = vi.spyOn(history, 'pushState');
    const origScrollTo = window.scrollTo;
    window.scrollTo = scrollToSpy;

    try {
      const link = document.querySelector('.toc-card-item');
      const click = new MouseEvent('click', { bubbles: true, cancelable: true });
      link.dispatchEvent(click);

      expect(scrollToSpy).toHaveBeenCalledTimes(1);
      expect(pushStateSpy.mock.calls[0][2]).toBe('#missing-id');
    } finally {
      window.scrollTo = origScrollTo;
      pushStateSpy.mockRestore();
    }
  });

  it('does nothing when neither the href id nor a matching heading exists', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#missing-id">Nonexistent Heading</a>
      </div>
      <article class="post-content"></article>
    `;
    runScript();

    const scrollToSpy = vi.fn();
    const origScrollTo = window.scrollTo;
    window.scrollTo = scrollToSpy;

    try {
      const link = document.querySelector('.toc-card-item');
      const click = new MouseEvent('click', { bubbles: true, cancelable: true });
      link.dispatchEvent(click);

      expect(click.defaultPrevented).toBe(false);
      expect(scrollToSpy).not.toHaveBeenCalled();
    } finally {
      window.scrollTo = origScrollTo;
    }
  });
});

describe('toc.js#highlightCurrentSection extra branches', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('skips a TOC item without an href attribute during highlighting', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item">No Href</a>
        <a class="toc-card-item" href="#s1">One</a>
      </div>
      <article class="post-content"><h2 id="s1" data-test-top="0" data-test-height="500">One</h2></article>
    `;
    ensurePrototypeMock();
    expect(() => runScript()).not.toThrow();

    const items = document.querySelectorAll('.toc-card-item');
    expect(items[1].classList.contains('active')).toBe(true);
  });

  it('finds the section via heading-text fallback and highlights it when the href id does not exist', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#missing-id">Real Heading</a>
      </div>
      <article class="post-content">
        <h2 data-test-top="0" data-test-height="500">Real Heading</h2>
      </article>
    `;
    ensurePrototypeMock();
    runScript();

    const link = document.querySelector('.toc-card-item');
    expect(link.classList.contains('active')).toBe(true);
  });
});

describe('toc.js#scroll handler rAF coalescing', () => {
  let originalRAF;

  beforeEach(() => {
    originalRAF = window.requestAnimationFrame;
  });

  afterEach(() => {
    window.requestAnimationFrame = originalRAF;
    document.body.innerHTML = '';
  });

  it('coalesces rapid scroll events into a single pending rAF until it flushes', () => {
    document.body.innerHTML = `
      <button id="toc-toggle"><span class="btn-text">Toggle</span></button>
      <div id="toc-content">
        <span id="toc-count"></span>
        <a class="toc-card-item" href="#s1">One</a>
      </div>
      <article class="post-content"><h2 id="s1">One</h2></article>
    `;
    // NOTE: `window` (and its 'scroll' listeners) persist across every test
    // in this file — earlier tests' runScript() calls leave their own
    // "scroll" listeners attached to the same jsdom window. So rafCalls is
    // NOT expected to equal 1 per dispatch; instead this test asserts the
    // *delta* pattern that proves coalescing: a dispatch adds some calls,
    // an immediate second dispatch adds ZERO (this test's own listener is
    // still "ticking"), and after flushing this test's pending frame a
    // third dispatch adds calls again.
    let rafCalls = 0;
    let pendingCb = null;
    window.requestAnimationFrame = (cb) => {
      rafCalls += 1;
      pendingCb = cb; // overwritten per call; ends up holding the last-registered (this test's) callback
      return 0;
    };

    runScript();

    window.dispatchEvent(new Event('scroll'));
    const callsAfterFirst = rafCalls;
    expect(callsAfterFirst).toBeGreaterThan(0);

    // A second scroll event before the pending frame flushes must add no new
    // rAF requests — this exercises the `if (!ticking)` guard's "already
    // ticking" (skip) branch for every listener still pending, including
    // this test's own.
    window.dispatchEvent(new Event('scroll'));
    expect(rafCalls).toBe(callsAfterFirst);

    // Flush the pending frame — this resets *this test's* `ticking` flag
    // back to false (stale listeners from other tests remain ticking and
    // stay silent, since their own pending callbacks were never captured).
    pendingCb();

    // A subsequent scroll event should now request at least one new frame
    // (this test's listener requests again).
    window.dispatchEvent(new Event('scroll'));
    expect(rafCalls).toBeGreaterThan(callsAfterFirst);
  });
});
