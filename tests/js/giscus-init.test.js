// Regression tests for assets/js/giscus-init.js
//
// Goal: prove the giscus comments bootstrap (a) bails cleanly when the
// container is missing, (b) toggles reaction-card ARIA + localStorage
// state correctly (single-active invariant), (c) updates comments-count
// when giscus posts a discussion message, (d) ignores foreign-origin
// postMessages, and (e) wires up the retry button.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';
import { stubIntersectionObserver } from './_fixtures.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/giscus-init.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

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

// Installs a capturing IntersectionObserver stub, runs the script, and
// immediately fires an intersecting entry so loadGiscus() appends the
// giscus <script> synchronously (avoids waiting on the 8s watchdog).
function runScriptAndTriggerIntersection() {
  const restore = stubIntersectionObserver();
  const Stub = window.IntersectionObserver;
  let created;
  window.IntersectionObserver = class extends Stub {
    constructor(cb, opts) {
      super(cb, opts);
      created = this;
    }
  };
  runScript();
  created._trigger(document.getElementById('giscus-container'), true);
  return restore;
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
    vi.useRealTimers();
    vi.restoreAllMocks();
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

  it('IntersectionObserver present: intersecting entry loads giscus and disconnects', () => {
    const restore = stubIntersectionObserver();
    const Stub = window.IntersectionObserver;
    let created;
    window.IntersectionObserver = class extends Stub {
      constructor(cb, opts) {
        super(cb, opts);
        created = this;
      }
    };
    buildGiscusFixture();
    runScript();

    expect(document.querySelector('#giscus-container script')).toBeNull();
    const container = document.getElementById('giscus-container');
    created._trigger(container, true);

    expect(document.querySelector('#giscus-container script')).not.toBeNull();
    expect(created._observed.size).toBe(0);

    restore();
  });

  it('IntersectionObserver absent: falls back to setTimeout(1000) load', () => {
    const original = window.IntersectionObserver;
    delete window.IntersectionObserver;
    vi.useFakeTimers();
    buildGiscusFixture();
    runScript();

    expect(document.querySelector('#giscus-container script')).toBeNull();
    vi.advanceTimersByTime(1000);
    expect(document.querySelector('#giscus-container script')).not.toBeNull();

    window.IntersectionObserver = original;
  });

  it('8s watchdog loads giscus when still not loaded and page visible', () => {
    const restoreIO = stubIntersectionObserver();
    Object.defineProperty(document, 'visibilityState', { value: 'visible', configurable: true });
    vi.useFakeTimers();
    buildGiscusFixture();
    runScript();

    expect(document.querySelector('#giscus-container script')).toBeNull();
    vi.advanceTimersByTime(8000);
    expect(document.querySelector('#giscus-container script')).not.toBeNull();

    restoreIO();
  });

  it('8s watchdog skips loading when page is hidden', () => {
    const restoreIO = stubIntersectionObserver();
    Object.defineProperty(document, 'visibilityState', { value: 'hidden', configurable: true });
    vi.useFakeTimers();
    buildGiscusFixture();
    runScript();

    vi.advanceTimersByTime(8000);
    expect(document.querySelector('#giscus-container script')).toBeNull();

    restoreIO();
    Object.defineProperty(document, 'visibilityState', { value: 'visible', configurable: true });
  });

  it('12s watchdog hides the loading indicator', () => {
    const restoreIO = stubIntersectionObserver();
    vi.useFakeTimers();
    buildGiscusFixture();
    runScript();

    const loadingEl = document.getElementById('giscus-loading');
    expect(loadingEl.classList.contains('hidden')).toBe(false);
    vi.advanceTimersByTime(12000);
    expect(loadingEl.classList.contains('hidden')).toBe(true);
    expect(loadingEl.style.display).toBe('none');

    restoreIO();
  });

  it('script onerror hides loading, shows error message, and resets giscusLoaded', () => {
    buildGiscusFixture();
    const restoreIO = runScriptAndTriggerIntersection();

    const script = document.querySelector('#giscus-container script');
    expect(script).not.toBeNull();
    script.onerror();

    const loadingEl = document.getElementById('giscus-loading');
    const errorEl = document.getElementById('giscus-error');
    expect(loadingEl.classList.contains('hidden')).toBe(true);
    expect(errorEl.classList.contains('hidden')).toBe(false);
    expect(errorEl.querySelector('.giscus-error-text').textContent).toBe(
      '댓글 위젯을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.'
    );

    restoreIO();
  });

  it('message type "ready" hides loading and error without touching comment count', () => {
    const restoreIO = stubIntersectionObserver();
    buildGiscusFixture();
    runScript();

    const errorEl = document.getElementById('giscus-error');
    errorEl.classList.remove('hidden');
    const loadingEl = document.getElementById('giscus-loading');
    loadingEl.classList.remove('hidden');

    window.dispatchEvent(
      new MessageEvent('message', {
        origin: 'https://giscus.app',
        data: { giscus: { type: 'ready' } },
      })
    );

    expect(loadingEl.classList.contains('hidden')).toBe(true);
    expect(errorEl.classList.contains('hidden')).toBe(true);

    restoreIO();
  });

  it('message type "error" shows the empty-state text on first failure, retryFailed after a retry', () => {
    const restoreIO = stubIntersectionObserver();
    buildGiscusFixture();
    runScript();

    const errorEl = document.getElementById('giscus-error');
    const retryBtn = document.getElementById('giscus-retry-btn');

    window.dispatchEvent(
      new MessageEvent('message', {
        origin: 'https://giscus.app',
        data: { giscus: { type: 'error' } },
      })
    );
    expect(errorEl.querySelector('.giscus-error-text').textContent).toBe(
      '아직 댓글이 없습니다. 첫 댓글을 남겨보세요.'
    );

    retryBtn.click();
    window.dispatchEvent(
      new MessageEvent('message', {
        origin: 'https://giscus.app',
        data: { giscus: { type: 'error' } },
      })
    );
    expect(errorEl.querySelector('.giscus-error-text').textContent).toBe(
      '댓글을 가져오지 못했습니다. 다시 시도해주세요.'
    );

    restoreIO();
  });

  it('message with discussion.reactions updates reaction counts and labels', () => {
    const restoreIO = stubIntersectionObserver();
    buildGiscusFixture();
    runScript();

    window.dispatchEvent(
      new MessageEvent('message', {
        origin: 'https://giscus.app',
        data: {
          giscus: {
            discussion: {
              totalCommentCount: 3,
              reactions: { THUMBS_UP: 5, HEART: undefined },
            },
          },
        },
      })
    );

    const thumbsEl = document.getElementById('reaction-thumbsUp');
    expect(thumbsEl.textContent).toBe('5');
    expect(thumbsEl.getAttribute('aria-label')).toBe('유용해요 5개');

    restoreIO();
  });

  it('message event without a giscus payload is a no-op', () => {
    const restoreIO = stubIntersectionObserver();
    buildGiscusFixture();
    runScript();

    expect(() =>
      window.dispatchEvent(
        new MessageEvent('message', { origin: 'https://giscus.app', data: {} })
      )
    ).not.toThrow();

    restoreIO();
  });

  it('themeChanged event posts the new theme to the giscus iframe when present', () => {
    const restoreIO = stubIntersectionObserver();
    buildGiscusFixture();
    runScript();

    const iframe = document.createElement('iframe');
    iframe.src = 'https://giscus.app/widget';
    document.getElementById('giscus-container').appendChild(iframe);
    iframe.contentWindow.postMessage = vi.fn();

    document.dispatchEvent(new CustomEvent('themeChanged', { detail: 'light' }));

    expect(iframe.contentWindow.postMessage).toHaveBeenCalledWith(
      { giscus: { setConfig: { theme: 'light' } } },
      'https://giscus.app'
    );
    expect(document.getElementById('giscus-error').getAttribute('data-theme-variant')).toBe('light');

    restoreIO();
  });

  it('themeChanged event with no iframe present only updates error theme (no throw)', () => {
    const restoreIO = stubIntersectionObserver();
    buildGiscusFixture();
    runScript();

    expect(() =>
      document.dispatchEvent(new CustomEvent('themeChanged', { detail: 'dark' }))
    ).not.toThrow();
    expect(document.getElementById('giscus-error').getAttribute('data-theme-variant')).toBe('dark');

    restoreIO();
  });

  it('retry button click reloads giscus (forceReload cleans up old script/iframe)', () => {
    buildGiscusFixture();
    const restoreIO = runScriptAndTriggerIntersection();

    const firstScript = document.querySelector('#giscus-container script');
    expect(firstScript).not.toBeNull();

    const retryBtn = document.getElementById('giscus-retry-btn');
    retryBtn.click();

    const scripts = document.querySelectorAll('#giscus-container script[src*="giscus.app/client.js"]');
    expect(scripts.length).toBe(1);
    expect(scripts[0]).not.toBe(firstScript);

    restoreIO();
  });

  it('locale=en renders English copy for retry + error text', () => {
    document.documentElement.setAttribute('lang', 'en');
    buildGiscusFixture();
    const restoreIO = runScriptAndTriggerIntersection();

    const script = document.querySelector('#giscus-container script');
    script.onerror();

    expect(document.getElementById('giscus-error').querySelector('.giscus-error-text').textContent).toBe(
      'Failed to load the comments widget. Please try again.'
    );
    expect(document.getElementById('giscus-retry-btn').textContent).toBe('Retry');

    document.documentElement.removeAttribute('lang');
    restoreIO();
  });

  it('locale=ja renders Japanese copy for the error message', () => {
    document.documentElement.setAttribute('lang', 'ja');
    buildGiscusFixture();
    const restoreIO = runScriptAndTriggerIntersection();

    const script = document.querySelector('#giscus-container script');
    script.onerror();

    expect(document.getElementById('giscus-error').querySelector('.giscus-error-text').textContent).toBe(
      'コメントウィジェットを読み込めませんでした。しばらくして再試行してください。'
    );

    document.documentElement.removeAttribute('lang');
    restoreIO();
  });

  it('getTheme reflects light preference from localStorage on the injected script', () => {
    window.localStorage.setItem('theme', 'light');
    buildGiscusFixture();
    const restoreIO = runScriptAndTriggerIntersection();

    const script = document.querySelector('#giscus-container script');
    expect(script.getAttribute('data-theme')).toBe('light');

    restoreIO();
  });

  it('missing optional elements (loading/error/retry) do not throw during error flow', () => {
    document.body.innerHTML = `
      <div id="giscus-container" data-repo="x/y" data-repo-id="r1"
           data-category="General" data-category-id="c1"></div>
    `;
    const restoreIO = runScriptAndTriggerIntersection();

    const script = document.querySelector('#giscus-container script');
    expect(() => script.onerror()).not.toThrow();

    restoreIO();
  });

  it('clicking a reaction card with an active giscus iframe schedules scrollIntoView', () => {
    const restoreIO = stubIntersectionObserver();
    vi.useFakeTimers();
    buildGiscusFixture();
    runScript();

    const iframe = document.createElement('iframe');
    iframe.scrollIntoView = vi.fn();
    document.getElementById('giscus-container').appendChild(iframe);

    const thumbs = document.querySelector('.reaction-card[data-reaction="thumbsUp"]');
    thumbs.click();
    vi.advanceTimersByTime(100);

    expect(iframe.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth', block: 'center' });

    restoreIO();
  });
});
