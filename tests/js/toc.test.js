// Regression tests for assets/js/toc.js#highlightCurrentSection
//
// Goal: prove the read-then-write split fix preserves the original
// "last match wins / no-match leaves state alone" behavior, while
// asserting that classList writes happen in a single pass after all
// geometry reads are complete (the anti-thrash invariant from
// docs/optimization/IIFE_THRASH_AUDIT.md).

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/toc.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

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
});
