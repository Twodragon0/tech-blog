// Regression tests for assets/js/main-post.js
//
// main-post.js is an IIFE that, at script-eval time, synchronously:
//   1. wraps every `.highlight` code block (and any stray `pre code` not
//      already inside one) with a language-labeled copy button, and
//   2. wraps every `.post-content table` in a scrollable `.table-wrapper`,
//      classifying risk/ops tables and their cells (level-high, P0, etc.)
//      based on the preceding heading text.
// A third block (Korean image-filename URL recovery, `fixImageUrls`) is
// deferred via `window.TechBlog.scheduleIdleWork(cb)`, which falls back to
// `setTimeout(cb, 1)` when `window.TechBlog` is absent. We set our own
// synchronous `scheduleIdleWork` stub before loading the script (same
// "define the global the closure reads" technique tests/js/share-actions
// and tests/js/main-core use for shareKakao/copyToClipboard) so the image
// URL logic is directly observable without fake timers.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/main-post.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

describe('main-post.js', () => {
  let originalClipboard;

  beforeEach(() => {
    document.body.innerHTML = '';
    delete window.TechBlog;
    // jsdom has no Clipboard API at all by default.
    originalClipboard = navigator.clipboard;
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: vi.fn(() => Promise.resolve()) },
    });
  });

  afterEach(() => {
    document.body.innerHTML = '';
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: originalClipboard,
    });
    vi.useRealTimers();
  });

  describe('code block copy button', () => {
    it('labels a python .highlight block and adds an accessible copy button', () => {
      document.body.innerHTML =
        '<div class="highlight python"><pre><code>print(1)</code></pre></div>';
      runScript();

      const highlight = document.querySelector('.highlight');
      expect(highlight.getAttribute('data-lang')).toBe('Python');
      expect(highlight.style.position).toBe('relative');

      const btn = highlight.querySelector('.copy-code-btn');
      expect(btn).not.toBeNull();
      expect(btn.getAttribute('aria-label')).toBe('Copy code to clipboard');
      expect(btn.querySelector('.copied')).toBeNull();
    });

    it('marks a mermaid .highlight block with the mermaid-specific classes', () => {
      document.body.innerHTML =
        '<div class="highlight mermaid"><pre><code class="language-mermaid">graph TD</code></pre></div>';
      runScript();

      const highlight = document.querySelector('.highlight');
      expect(highlight.getAttribute('data-lang')).toBe('Mermaid');
      expect(highlight.classList.contains('mermaid-block')).toBe(true);
      expect(highlight.querySelector('.copy-code-btn.mermaid-copy-btn')).not.toBeNull();
    });

    it('wraps a standalone `pre code` block (not inside .highlight) and labels its language', () => {
      document.body.innerHTML = '<pre><code class="language-bash">ls -la</code></pre>';
      runScript();

      const highlight = document.querySelector('.highlight');
      expect(highlight).not.toBeNull();
      expect(highlight.getAttribute('data-lang')).toBe('Bash');
      expect(highlight.contains(document.querySelector('pre'))).toBe(true);
      expect(highlight.querySelector('.copy-code-btn')).not.toBeNull();
    });

    it('copies the code text to the clipboard and shows/reverts the copied state', async () => {
      vi.useFakeTimers();
      document.body.innerHTML =
        '<div class="highlight python"><pre><code>print("hi")</code></pre></div>';
      runScript();

      const btn = document.querySelector('.copy-code-btn');
      const copyIcon = btn.querySelector('.copy-icon');
      const checkIcon = btn.querySelector('.check-icon');

      btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      // Flush the microtask queue for the awaited clipboard.writeText().
      await vi.waitFor(() => {
        expect(btn.classList.contains('copied')).toBe(true);
      });

      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('print("hi")');
      expect(copyIcon.style.display).toBe('none');
      expect(checkIcon.style.display).toBe('block');
      expect(btn.getAttribute('title')).toBe('Copied!');

      await vi.advanceTimersByTimeAsync(2000);

      expect(btn.classList.contains('copied')).toBe(false);
      expect(copyIcon.style.display).toBe('block');
      expect(checkIcon.style.display).toBe('none');
      expect(btn.getAttribute('title')).toBe('Copy');
    });
  });

  describe('table wrapper + risk/ops classification', () => {
    // REGRESSION GUARD (bug fixed): wrapTables() moves the table inside a
    // .table-wrapper div (insertBefore + appendChild) before classifying it,
    // so at classify time `table.previousElementSibling` is null. Previously
    // getTableContext() walked from the table and always returned '', making
    // table-risk-scorecard / table-ops-metrics / per-cell classes dead code.
    // Fix: getTableContext() now anchors on the wrapper (table.parentElement)
    // when the table is already inside .table-wrapper, so it finds the
    // preceding heading. This test asserts the classification IS applied.
    it('applies risk/ops classification to a wrapped table with a matching heading + cell content', () => {
      document.body.innerHTML = `
        <article class="post-content">
          <h2>보안 위험 스코어카드</h2>
          <table><thead><tr><th>Risk</th></tr></thead>
          <tbody><tr><td>HIGH</td><td>P0</td></tr></tbody></table>
        </article>
      `;
      runScript();

      const table = document.querySelector('table');
      const wrapper = table.parentElement;
      expect(wrapper.classList.contains('table-wrapper')).toBe(true);

      // Classification now runs correctly against the wrapper's preceding heading.
      expect(wrapper.classList.contains('table-wrapper-risk-scorecard')).toBe(true);
      expect(table.classList.contains('table-risk-scorecard')).toBe(true);
      const cells = table.querySelectorAll('td');
      expect(cells[0].classList.contains('level-high')).toBe(true);   // "HIGH"
      expect(cells[1].classList.contains('urgency-critical')).toBe(true); // "P0"
    });

    it('does not wrap a table with no preceding heading in a risk/ops class, but still wraps it', () => {
      document.body.innerHTML = `
        <article class="post-content">
          <p>intro text</p>
          <table><tbody><tr><td>plain</td></tr></tbody></table>
        </article>
      `;
      runScript();

      const table = document.querySelector('table');
      expect(table.parentElement.classList.contains('table-wrapper')).toBe(true);
      expect(table.classList.contains('table-risk-scorecard')).toBe(false);
      expect(table.classList.contains('table-ops-metrics')).toBe(false);
    });

    it('excludes tables with the chat-table class from wrapping', () => {
      document.body.innerHTML = `
        <article class="post-content">
          <table class="chat-table"><tbody><tr><td>x</td></tr></tbody></table>
        </article>
      `;
      runScript();

      const table = document.querySelector('table');
      expect(table.parentElement.classList.contains('table-wrapper')).toBe(false);
    });

    it('toggles is-scrolling on scroll and clears it after the debounce delay', async () => {
      vi.useFakeTimers();
      document.body.innerHTML = `
        <article class="post-content">
          <table><tbody><tr><td>x</td></tr></tbody></table>
        </article>
      `;
      runScript();

      const wrapper = document.querySelector('.table-wrapper');
      wrapper.dispatchEvent(new Event('scroll'));
      expect(wrapper.classList.contains('is-scrolling')).toBe(true);

      await vi.advanceTimersByTimeAsync(1500);
      expect(wrapper.classList.contains('is-scrolling')).toBe(false);
    });
  });

  describe('Korean image URL recovery (fixImageUrls / sanitizeImagePath)', () => {
    beforeEach(() => {
      // Force fixImageUrls() to run synchronously instead of via
      // setTimeout(cb, 1), so assertions don't need to await a real timer.
      window.TechBlog = { scheduleIdleWork: (cb) => cb() };
    });

    it('decodes a percent-encoded Korean filename into a direct /assets/images/ src', () => {
      const encoded = '/assets/images/' + encodeURIComponent('테스트.png');
      document.body.innerHTML = `<img class="post-image" src="${encoded}">`;
      runScript();

      const img = document.querySelector('img');
      expect(img.getAttribute('src')).toBe('/assets/images/테스트.png');
    });

    it('refuses to decode a Korean filename containing an embedded HTML tag', () => {
      const malicious = '/assets/images/' + encodeURIComponent('<script>가.png');
      document.body.innerHTML = `<img class="post-image" src="${malicious}">`;
      runScript();

      const img = document.querySelector('img');
      // sanitizeImagePath() rejects any decoded path containing `<...>` and
      // returns null, so fixImageUrls() must leave the original src alone.
      expect(img.getAttribute('src')).toBe(malicious);
    });

    it('refuses to promote a data-original-src that resolves outside /assets or /images', async () => {
      document.body.innerHTML =
        '<img class="post-image" src="/assets/images/plain.png" data-original-src="javascript:alert(1)">';
      runScript();

      const img = document.querySelector('img');
      const before = img.getAttribute('src');

      // retryCount reaches 2 (the data-original-src branch) only after two
      // error events.
      img.dispatchEvent(new Event('error'));
      img.dispatchEvent(new Event('error'));

      expect(img.getAttribute('src')).toBe(before);
    });

    it('marks a hero post image as loaded immediately when already complete', () => {
      document.body.innerHTML =
        '<div class="post-header"><div class="post-image"><img></div></div>';
      const img = document.querySelector('img');
      Object.defineProperty(img, 'complete', { value: true, configurable: true });
      Object.defineProperty(img, 'naturalHeight', { value: 200, configurable: true });

      runScript();

      expect(img.classList.contains('loaded')).toBe(true);
    });

    it('marks a hero post image as loaded once its load event fires', () => {
      document.body.innerHTML =
        '<div class="post-header"><div class="post-image"><img></div></div>';
      const img = document.querySelector('img');
      Object.defineProperty(img, 'complete', { value: false, configurable: true });

      runScript();
      expect(img.classList.contains('loaded')).toBe(false);

      img.dispatchEvent(new Event('load'));
      expect(img.classList.contains('loaded')).toBe(true);
    });
  });
});
