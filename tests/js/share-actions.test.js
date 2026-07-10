// Regression tests for assets/js/share-actions.js
//
// The script is a delegated click handler on `document` that reads
// `data-share-action="kakao|copy"` attributes off the clicked element
// (via `closest()`) and dispatches to the global `shareKakao()` /
// `copyToClipboard()` functions defined elsewhere on the page. This
// CSP-safe pattern replaces inline `onclick` attributes.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/share-actions.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

// share-actions.js attaches a delegated `click` listener directly to
// `document`. Across vitest tests `document` is shared, so we track the
// handler at registration time and remove it in afterEach to prevent
// listener accumulation that would inflate spy call counts on later
// tests.
function runScript(handlerSink) {
  const origAdd = document.addEventListener.bind(document);
  document.addEventListener = (evt, handler, opts) => {
    handlerSink.push({ evt, handler, opts });
    return origAdd(evt, handler, opts);
  };
  try {
    // eslint-disable-next-line no-new-func
    new Function('window', 'document', SCRIPT_SOURCE)(window, document);
  } finally {
    document.addEventListener = origAdd;
  }
}

describe('share-actions.js', () => {
  let shareKakao;
  let copyToClipboard;
  let registered;

  beforeEach(() => {
    document.body.innerHTML = '';
    shareKakao = vi.fn();
    copyToClipboard = vi.fn();
    // The script reads these as global function names. In the IIFE the
    // `typeof shareKakao === 'function'` check resolves against the
    // outer scope, which in jsdom maps to window.* — set both to be
    // explicit.
    window.shareKakao = shareKakao;
    window.copyToClipboard = copyToClipboard;
    registered = [];
    runScript(registered);
  });

  afterEach(() => {
    for (const r of registered) {
      document.removeEventListener(r.evt, r.handler, r.opts);
    }
    delete window.shareKakao;
    delete window.copyToClipboard;
    document.body.innerHTML = '';
  });

  it('dispatches data-share-action="kakao" to shareKakao with url+title+desc', () => {
    document.body.innerHTML =
      '<button data-share-action="kakao" ' +
      'data-share-url="https://example.com/post" ' +
      'data-share-title="My Title" ' +
      'data-share-desc="My description"></button>';
    document.querySelector('[data-share-action]').click();
    expect(shareKakao).toHaveBeenCalledTimes(1);
    expect(shareKakao).toHaveBeenCalledWith(
      'https://example.com/post',
      'My Title',
      'My description',
    );
    expect(copyToClipboard).not.toHaveBeenCalled();
  });

  it('dispatches data-share-action="copy" to copyToClipboard with the URL', () => {
    document.body.innerHTML =
      '<button data-share-action="copy" data-share-url="https://example.com/post"></button>';
    document.querySelector('[data-share-action]').click();
    expect(copyToClipboard).toHaveBeenCalledTimes(1);
    expect(copyToClipboard).toHaveBeenCalledWith('https://example.com/post');
    expect(shareKakao).not.toHaveBeenCalled();
  });

  it('ignores clicks on elements without data-share-action ancestors', () => {
    document.body.innerHTML = '<button id="other">unrelated button</button>';
    document.querySelector('#other').click();
    expect(shareKakao).not.toHaveBeenCalled();
    expect(copyToClipboard).not.toHaveBeenCalled();
  });

  it('uses closest() to find the share button even when the click is on a child element', () => {
    document.body.innerHTML =
      '<button data-share-action="copy" data-share-url="https://example.com/x">' +
      '<span class="icon">📋</span>' +
      '</button>';
    document.querySelector('span.icon').click();
    expect(copyToClipboard).toHaveBeenCalledWith('https://example.com/x');
  });

  it('passes empty strings when url/title/desc attributes are missing', () => {
    document.body.innerHTML = '<button data-share-action="kakao"></button>';
    document.querySelector('[data-share-action]').click();
    expect(shareKakao).toHaveBeenCalledWith('', '', '');
  });

  it('does not throw when the global handler is missing', () => {
    // Simulate page without copyToClipboard defined.
    delete window.copyToClipboard;
    document.body.innerHTML =
      '<button data-share-action="copy" data-share-url="https://example.com/y"></button>';
    expect(() => {
      document.querySelector('[data-share-action]').click();
    }).not.toThrow();
  });
});
