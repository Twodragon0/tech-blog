// Regression tests for assets/js/post-page.js
//
// post-page.js loads on every post via `_includes/footer.html`. It owns
// (a) heading-id generation on `.post-content` so kramdown-style anchors
// work, (b) reading-time estimation in `#reading-time` (hybrid Korean
// 500 chars/min + English 200 words/min), (c) external-link hardening
// with target="_blank" + rel="noopener noreferrer", (d) reading-progress
// bar, (e) Giscus mount observer, (f) image lightbox.
//
// Most behavior runs via `scheduleIdleWork()` which falls back to
// `setTimeout(callback, 0)` in jsdom. We use `vi.useFakeTimers()` +
// `vi.runOnlyPendingTimers()` to flush the deferred passes synchronously.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/post-page.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function runScript(handlerSink) {
  const origAdd = document.addEventListener.bind(document);
  document.addEventListener = (evt, handler, opts) => {
    handlerSink.push({ evt, handler, opts });
    return origAdd(evt, handler, opts);
  };
  try {
    // eslint-disable-next-line no-new-func
    new Function('window', 'document', SCRIPT_SOURCE)(window, document);
    vi.runOnlyPendingTimers();
  } finally {
    document.addEventListener = origAdd;
  }
}

describe('post-page.js', () => {
  let documentHandlers;

  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = '';
    documentHandlers = [];
  });

  afterEach(() => {
    for (const r of documentHandlers) {
      document.removeEventListener(r.evt, r.handler, r.opts);
    }
    vi.useRealTimers();
    document.body.innerHTML = '';
  });

  // =========================================================================
  // generateHeadingIds — kramdown-compatible auto-id + heading-anchor link
  // =========================================================================

  it('heading IDs: adds slug ID to .post-content h2/h3 missing one', () => {
    document.body.innerHTML =
      '<article class="post-article">' +
      '<div class="post-content">' +
      '<h2>Hello World</h2>' +
      '<h3>Section Two</h3>' +
      '</div></article>';
    runScript(documentHandlers);

    const h2 = document.querySelector('h2');
    const h3 = document.querySelector('h3');
    expect(h2.id).toBe('hello-world');
    expect(h3.id).toBe('section-two');
  });

  it('heading IDs: preserves existing id (no overwrite)', () => {
    document.body.innerHTML =
      '<div class="post-content"><h2 id="custom-anchor">Hello</h2></div>';
    runScript(documentHandlers);
    expect(document.querySelector('h2').id).toBe('custom-anchor');
  });

  it('heading IDs: injects .heading-anchor with href="#id" inside the heading', () => {
    document.body.innerHTML =
      '<div class="post-content"><h2>안녕 세계</h2></div>';
    runScript(documentHandlers);

    const h2 = document.querySelector('h2');
    const anchor = h2.querySelector('a.heading-anchor');
    expect(anchor).not.toBeNull();
    // The anchor href encodes the (Korean-preserving) generated id.
    expect(anchor.getAttribute('href')).toBe('#' + h2.id);
    // ARIA label exists for screen readers.
    expect(anchor.getAttribute('aria-label')).toMatch(/Permalink/);
  });

  it('heading IDs: does nothing when .post-content is missing', () => {
    document.body.innerHTML = '<h2>Outside</h2>';
    expect(() => runScript(documentHandlers)).not.toThrow();
    expect(document.querySelector('h2').id).toBe('');
  });

  // =========================================================================
  // initReadingTime — hybrid Korean + English calculation
  // =========================================================================

  it('reading-time: hybrid Korean 500 chars/min + English 200 words/min populates #reading-time', () => {
    // 1000 Korean chars (= 2 min) + 400 English words (= 2 min) → ceil(4) = 4 min
    const koreanText = '가'.repeat(1000);
    const englishText = ('word '.repeat(400)).trim();
    document.body.innerHTML =
      '<div class="post-content"><p>' +
      koreanText +
      '</p><p>' +
      englishText +
      '</p></div>' +
      '<span id="reading-time"></span>';
    runScript(documentHandlers);

    const text = document.getElementById('reading-time').textContent;
    expect(text).toMatch(/^\d+ min read$/);
    // 1000/500 + 400/200 = 2 + 2 = 4
    expect(text).toBe('4 min read');
  });

  it('reading-time: minimum is 1 min even for empty content', () => {
    document.body.innerHTML =
      '<div class="post-content"></div><span id="reading-time"></span>';
    runScript(documentHandlers);
    expect(document.getElementById('reading-time').textContent).toBe('1 min read');
  });

  // =========================================================================
  // enhanceExternalLinks — security hardening for outbound links
  // =========================================================================

  it('external links: external https URL gets target=_blank + rel="noopener noreferrer"', () => {
    document.body.innerHTML =
      '<div class="post-content">' +
      '<a id="ext" href="https://external.example.com/x">External</a>' +
      '</div>' +
      '<span id="reading-time"></span>'; // initReadingTime needs to run for enhanceExternalLinks
    runScript(documentHandlers);

    const link = document.getElementById('ext');
    expect(link.getAttribute('target')).toBe('_blank');
    expect(link.getAttribute('rel')).toBe('noopener noreferrer');
    expect(link.classList.contains('external-link-processed')).toBe(true);
  });

  it('external links: skips fragment (#anchor) / mailto / tel / same-host links', () => {
    document.body.innerHTML =
      '<div class="post-content">' +
      '<a id="frag" href="#section">Anchor</a>' +
      '<a id="mail" href="mailto:foo@bar.com">Email</a>' +
      '<a id="tel" href="tel:+82-10-0000">Phone</a>' +
      `<a id="same" href="${window.location.origin}/posts/x">Same host</a>` +
      '</div>' +
      '<span id="reading-time"></span>';
    runScript(documentHandlers);

    for (const id of ['frag', 'mail', 'tel', 'same']) {
      const a = document.getElementById(id);
      expect(a.getAttribute('target'), `#${id} should have no target`).toBeNull();
      expect(a.classList.contains('external-link-processed')).toBe(false);
    }
  });
});
