// Regression tests for assets/js/giscus-init.js
//
// Goal: prove the giscus comments bootstrap (a) bails cleanly when the
// container is missing, (b) toggles reaction-card ARIA + localStorage
// state correctly (single-active invariant), (c) updates comments-count
// when giscus posts a discussion message, (d) ignores foreign-origin
// postMessages, and (e) wires up the retry button.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/giscus-init.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

function buildGiscusFixture() {
  document.body.innerHTML = `
    <div id="giscus-container"
         data-repo="x/y" data-repo-id="r1"
         data-category="General" data-category-id="c1"
         data-mapping="pathname" data-strict="0"
         data-reactions-enabled="1" data-emit-metadata="1"
         data-input-position="top" data-lang="ko"></div>
    <span id="giscus-loading">Loading…</span>
    <span id="comments-count" style="display:none">0</span>
    <div id="giscus-error" class="hidden">
      <span class="giscus-error-text"></span>
      <button id="giscus-retry-btn" type="button">Retry</button>
    </div>
    <button class="reaction-card" data-reaction="thumbsUp" type="button" aria-pressed="false">
      <span id="reaction-thumbsUp">0</span>
    </button>
    <button class="reaction-card" data-reaction="heart" type="button" aria-pressed="false">
      <span id="reaction-heart">0</span>
    </button>
  `;
}

describe('giscus-init.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    try {
      window.localStorage.clear();
    } catch (_e) {
      // ignore
    }
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('bails cleanly when #giscus-container is missing', () => {
    expect(() => runScript()).not.toThrow();
  });

  it('toggles a reaction card on click (single-active invariant + ARIA + localStorage)', () => {
    buildGiscusFixture();
    runScript();

    const thumbs = document.querySelector('.reaction-card[data-reaction="thumbsUp"]');
    const heart = document.querySelector('.reaction-card[data-reaction="heart"]');

    thumbs.click();
    expect(thumbs.classList.contains('active')).toBe(true);
    expect(thumbs.getAttribute('aria-pressed')).toBe('true');
    expect(window.localStorage.getItem('reaction-thumbsUp')).toBe('active');

    // Single-active invariant: clicking heart deactivates thumbs.
    heart.click();
    expect(heart.classList.contains('active')).toBe(true);
    expect(thumbs.classList.contains('active')).toBe(false);
    expect(thumbs.getAttribute('aria-pressed')).toBe('false');
    expect(window.localStorage.getItem('reaction-thumbsUp')).toBeNull();
    expect(window.localStorage.getItem('reaction-heart')).toBe('active');

    // Click again to deactivate.
    heart.click();
    expect(heart.classList.contains('active')).toBe(false);
    expect(window.localStorage.getItem('reaction-heart')).toBeNull();
  });

  it('updates #comments-count from a giscus postMessage', () => {
    buildGiscusFixture();
    runScript();

    // Simulate a giscus discussion update message.
    window.dispatchEvent(
      new MessageEvent('message', {
        origin: 'https://giscus.app',
        data: {
          giscus: {
            discussion: { totalCommentCount: 7, reactions: {} },
          },
        },
      })
    );

    const counter = document.getElementById('comments-count');
    expect(counter.textContent).toBe('7');
    expect(counter.style.display).toBe('inline-flex');
    expect(counter.getAttribute('aria-label')).toBe('댓글 7개');
  });

  it('ignores postMessages from foreign origins (security boundary)', () => {
    buildGiscusFixture();
    runScript();

    window.dispatchEvent(
      new MessageEvent('message', {
        origin: 'https://evil.example.com',
        data: { giscus: { discussion: { totalCommentCount: 999 } } },
      })
    );

    const counter = document.getElementById('comments-count');
    expect(counter.textContent).toBe('0');
  });

  it('restores active reaction state from localStorage on init', () => {
    window.localStorage.setItem('reaction-heart', 'active');
    buildGiscusFixture();
    runScript();

    const heart = document.querySelector('.reaction-card[data-reaction="heart"]');
    expect(heart.classList.contains('active')).toBe(true);
    expect(heart.getAttribute('aria-pressed')).toBe('true');
  });

  it('keyboard activation (Enter/Space) on a reaction card triggers click handler', () => {
    buildGiscusFixture();
    runScript();

    const thumbs = document.querySelector('.reaction-card[data-reaction="thumbsUp"]');
    const clickSpy = vi.spyOn(thumbs, 'click');

    const evt = new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true });
    thumbs.dispatchEvent(evt);
    expect(clickSpy).toHaveBeenCalled();
    clickSpy.mockRestore();
  });
});
