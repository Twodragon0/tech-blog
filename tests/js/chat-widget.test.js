// Regression tests for assets/js/chat-widget.js
//
// chat-widget.js is an IIFE that reads its DOM elements once at load time
// (getElementById) and exits early if #deepseek-chat-widget /
// #chat-widget-toggle / #chat-widget-window are missing. All the
// interesting logic (message formatting/escaping, XSS-safe link/URL
// validation, sendMessage error handling, focus trap) lives in closures
// that are only reachable through the DOM surface the script wires up
// (button clicks, form submit, keydown). We drive those exactly like a
// user/browser would, following the same eval-and-query pattern as
// tests/js/toc.test.js and tests/js/share-actions.test.js.
//
// Two jsdom gaps are patched per-test:
//   - Element.prototype.scrollTo is undefined in jsdom 29; chat-widget.js
//     calls chatMessages.scrollTo(...) on every addMessage(), so it must
//     be stubbed or the script throws.
//   - window.requestAnimationFrame defaults to a slow real timer; we flush
//     it synchronously (same trick as toc.test.js) so toggleChat()'s
//     rAF-deferred classList writes are observable immediately.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/chat-widget.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

// The script attaches one listener directly to `document` (keydown, for
// Escape-to-close + focus trap). Track it so afterEach can remove it —
// otherwise handlers accumulate across tests since `document` persists
// even after `document.body.innerHTML` is reset.
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

function buildChatFixture({ withSuggestions = false } = {}) {
  document.body.innerHTML = `
    <div id="deepseek-chat-widget">
      <button id="chat-widget-toggle" aria-expanded="false"></button>
      <div id="chat-widget-window">
        <button id="chat-widget-close">Close</button>
        <div id="chat-widget-messages"></div>
        ${withSuggestions ? '<div id="chat-suggestions"><button class="chat-suggestion-btn">Suggested question</button></div>' : ''}
        <form id="chat-widget-form">
          <input id="chat-widget-input" type="text" />
          <button id="chat-widget-send" type="submit"></button>
        </form>
      </div>
    </div>
  `;
}

function elements() {
  return {
    toggle: document.getElementById('chat-widget-toggle'),
    win: document.getElementById('chat-widget-window'),
    close: document.getElementById('chat-widget-close'),
    messages: document.getElementById('chat-widget-messages'),
    form: document.getElementById('chat-widget-form'),
    input: document.getElementById('chat-widget-input'),
    send: document.getElementById('chat-widget-send'),
  };
}

async function flush() {
  // Let pending fetch/json microtasks settle without relying on fake timers
  // (the non-streaming sendMessage path is a plain async/await chain).
  await new Promise((r) => setTimeout(r, 0));
  await new Promise((r) => setTimeout(r, 0));
}

describe('chat-widget.js', () => {
  let registered;
  let originalRAF;
  let originalScrollTo;

  beforeEach(() => {
    localStorage.clear();
    document.body.innerHTML = '';
    registered = [];
    originalRAF = window.requestAnimationFrame;
    window.requestAnimationFrame = (cb) => {
      cb(performance.now());
      return 0;
    };
    // jsdom 29 has no scroll implementation at all.
    originalScrollTo = Element.prototype.scrollTo;
    Element.prototype.scrollTo = vi.fn();
    delete window.DOMPurify;
    window.fetch = vi.fn(() => Promise.reject(new Error('fetch not mocked for this test')));
  });

  afterEach(() => {
    for (const r of registered) {
      document.removeEventListener(r.evt, r.handler, r.opts);
    }
    window.requestAnimationFrame = originalRAF;
    // toggleChat() schedules a real `setTimeout(scrollToBottom, 100)` that can
    // fire AFTER this afterEach when enough wall-clock elapses across the full
    // suite. jsdom has no scrollTo, so restoring the original `undefined` made
    // that stray call throw an uncaught "scrollTo is not a function" — all
    // assertions still passed, but the vitest process exited 1 intermittently.
    // Restore a no-op polyfill instead so the late timer is harmless (real
    // timers are kept because other tests flush promises via setTimeout(r, 0)).
    Element.prototype.scrollTo =
      typeof originalScrollTo === 'function' ? originalScrollTo : () => {};
    delete window.DOMPurify;
    delete window.fetch;
    document.body.innerHTML = '';
  });

  describe('toggleChat', () => {
    it('opens the window and flips aria attributes on toggle click', () => {
      buildChatFixture();
      runScript(registered);
      const { toggle, win } = elements();

      toggle.click();

      expect(win.hasAttribute('hidden')).toBe(false);
      expect(win.getAttribute('aria-hidden')).toBe('false');
      expect(win.classList.contains('chat-widget-window-open')).toBe(true);
      expect(win.classList.contains('chat-widget-user-opened')).toBe(true);
      expect(toggle.getAttribute('aria-expanded')).toBe('true');
    });

    it('closes the window on close-button click', () => {
      buildChatFixture();
      runScript(registered);
      const { toggle, close, win } = elements();

      toggle.click(); // open
      close.click(); // close

      expect(win.hasAttribute('hidden')).toBe(true);
      expect(win.getAttribute('aria-hidden')).toBe('true');
      expect(win.classList.contains('chat-widget-window-open')).toBe(false);
      expect(win.classList.contains('chat-widget-user-opened')).toBe(false);
    });

    it('closes on Escape key when open', () => {
      buildChatFixture();
      runScript(registered);
      const { toggle, win } = elements();

      toggle.click();
      expect(win.hasAttribute('hidden')).toBe(false);

      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));

      expect(win.hasAttribute('hidden')).toBe(true);
    });

    it('closes when the click target is the window backdrop itself', () => {
      buildChatFixture();
      runScript(registered);
      const { toggle, win } = elements();

      toggle.click();
      win.dispatchEvent(new MouseEvent('click', { bubbles: true }));

      expect(win.hasAttribute('hidden')).toBe(true);
    });

    it('does not close when the click target is a child of the window', () => {
      buildChatFixture();
      runScript(registered);
      const { toggle, win, messages } = elements();

      toggle.click();
      messages.dispatchEvent(new MouseEvent('click', { bubbles: true }));

      expect(win.hasAttribute('hidden')).toBe(false);
    });
  });

  describe('handleSubmit validation', () => {
    it('rejects a message shorter than 2 characters without calling fetch', () => {
      buildChatFixture();
      runScript(registered);
      const { form, input, messages } = elements();

      input.value = 'a';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));

      expect(window.fetch).not.toHaveBeenCalled();
      expect(messages.textContent).toContain('최소 2자 이상');
    });

    it('rejects a message longer than maxMessageLength without calling fetch', () => {
      buildChatFixture();
      runScript(registered);
      const { form, input, messages } = elements();

      input.value = 'a'.repeat(2001);
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));

      expect(window.fetch).not.toHaveBeenCalled();
      expect(messages.textContent).toContain('너무 깁니다');
    });
  });

  describe('sendMessage (non-streaming fallback)', () => {
    // supportsStreaming() calls Response.prototype.body on the bare
    // prototype (no receiver), which throws "Illegal invocation" under
    // Node's fetch polyfill and is caught internally -> always resolves to
    // the non-streaming path in this test environment. Verified empirically
    // (see PR notes) rather than assumed.

    it('disables input/send while loading, then re-enables after completion', async () => {
      buildChatFixture();
      runScript(registered);
      const { form, input, send } = elements();

      let resolveFetch;
      window.fetch = vi.fn(
        () =>
          new Promise((resolve) => {
            resolveFetch = resolve;
          })
      );

      input.value = 'hello there';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));

      expect(input.disabled).toBe(true);
      expect(send.disabled).toBe(true);

      resolveFetch({ ok: true, status: 200, json: () => Promise.resolve({ response: 'hi' }) });
      await flush();

      expect(input.disabled).toBe(false);
      expect(send.disabled).toBe(false);
    });

    it('posts message/sessionId/pageContext and clears the input on submit', async () => {
      buildChatFixture();
      runScript(registered);
      const { form, input } = elements();

      localStorage.setItem('chatSessionId', 'existing-session');
      // Re-run so initSession() picks up the pre-seeded id.
      buildChatFixture();
      runScript(registered);
      const els = elements();

      window.fetch = vi.fn(() =>
        Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ response: 'hi' }) })
      );

      els.input.value = 'hello agent';
      els.form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));

      expect(els.input.value).toBe('');
      await flush();

      expect(window.fetch).toHaveBeenCalledTimes(1);
      const [url, opts] = window.fetch.mock.calls[0];
      expect(url).toBe('/api/chat');
      expect(opts.method).toBe('POST');
      const body = JSON.parse(opts.body);
      expect(body.message).toBe('hello agent');
      expect(body.sessionId).toBe('existing-session');
      expect(body.pageContext).toEqual(expect.objectContaining({ title: expect.any(String) }));
    });

    it('renders the assistant reply as plain text when DOMPurify is unavailable', async () => {
      buildChatFixture();
      runScript(registered);
      const { form, input, messages } = elements();

      window.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ response: 'Plain reply text' }),
        })
      );

      input.value = 'question';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flush();

      const assistantEl = messages.querySelector('.chat-message-assistant .chat-message-content');
      expect(assistantEl.textContent).toBe('Plain reply text');
      // Fallback path strips tags entirely -> no element children.
      expect(assistantEl.innerHTML).not.toContain('<p>');
    });

    it('renders markdown (bold/inline-code/external link) through formatMessage when DOMPurify is present', async () => {
      buildChatFixture();
      runScript(registered);
      const { form, input, messages } = elements();

      window.DOMPurify = { sanitize: (html) => html };
      window.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({ response: '**Bold** and `code` and [link](https://example.com)' }),
        })
      );

      input.value = 'format this';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flush();

      const assistantEl = messages.querySelector('.chat-message-assistant .chat-message-content');
      expect(assistantEl.innerHTML).toContain('<strong>Bold</strong>');
      expect(assistantEl.innerHTML).toContain('<code class="inline-code">code</code>');
      expect(assistantEl.innerHTML).toContain('href="https://example.com/"');
      expect(assistantEl.innerHTML).toContain('chat-link-external');
    });

    it('blocks a javascript: URL in a markdown link and renders text only', async () => {
      buildChatFixture();
      runScript(registered);
      const { form, input, messages } = elements();

      window.DOMPurify = { sanitize: (html) => html };
      window.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({ response: '[click me](javascript:alert(1))' }),
        })
      );

      input.value = 'try xss';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flush();

      const assistantEl = messages.querySelector('.chat-message-assistant .chat-message-content');
      expect(assistantEl.innerHTML).not.toContain('<a ');
      expect(assistantEl.innerHTML).not.toContain('javascript:');
      expect(assistantEl.textContent).toContain('click me');
    });

    it('persists a server-issued sessionId to localStorage', async () => {
      buildChatFixture();
      runScript(registered);
      const { form, input } = elements();

      window.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ response: 'hi', sessionId: 'server-session-42' }),
        })
      );

      input.value = 'hello';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flush();

      expect(localStorage.getItem('chatSessionId')).toBe('server-session-42');
    });

    it('shows the retryAfter countdown message on a 429 response', async () => {
      buildChatFixture();
      runScript(registered);
      const { form, input, messages } = elements();

      window.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 429,
          json: () => Promise.resolve({ retryAfter: 42 }),
        })
      );

      input.value = 'too fast';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flush();

      expect(messages.textContent).toContain('42초 후 다시 시도해주세요');
    });

    it('appends a working retry button on a network failure and re-sends on click', async () => {
      buildChatFixture();
      runScript(registered);
      const { form, input, messages } = elements();

      window.fetch = vi.fn(() => Promise.reject(new Error('failed to fetch')));

      input.value = 'network please fail';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flush();

      const retryBtn = messages.querySelector('.chat-retry-button');
      expect(retryBtn).not.toBeNull();
      expect(window.fetch).toHaveBeenCalledTimes(1);

      window.fetch = vi.fn(() =>
        Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ response: 'ok now' }) })
      );
      retryBtn.click();
      await flush();

      expect(messages.querySelector('.chat-retry-button')).toBeNull();
      expect(window.fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('suggestion buttons', () => {
    it('hides the suggestions panel and submits the suggestion text on click', async () => {
      buildChatFixture({ withSuggestions: true });
      runScript(registered);
      const suggestionsContainer = document.getElementById('chat-suggestions');
      const btn = suggestionsContainer.querySelector('.chat-suggestion-btn');
      const { input } = elements();

      window.fetch = vi.fn(() =>
        Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ response: 'ok' }) })
      );

      btn.click();

      // handleSubmit() runs synchronously up to the first await, clearing
      // the input immediately after reading its value — so by the time we
      // can observe it, the value is already '' again. Assert the cleared
      // end-state plus the submitted body to prove the suggestion text
      // actually made it into the request.
      expect(suggestionsContainer.style.display).toBe('none');
      expect(input.value).toBe('');
      await flush();
      expect(window.fetch).toHaveBeenCalledTimes(1);
      const body = JSON.parse(window.fetch.mock.calls[0][1].body);
      expect(body.message).toBe('Suggested question');
    });
  });

  describe('focus trap', () => {
    it('wraps Tab from the last focusable element to the first when open', () => {
      buildChatFixture();
      runScript(registered);
      const { toggle, close, send } = elements();

      toggle.click(); // open
      send.focus();
      expect(document.activeElement).toBe(send);

      const evt = new KeyboardEvent('keydown', { key: 'Tab', bubbles: true, cancelable: true });
      document.dispatchEvent(evt);

      expect(document.activeElement).toBe(close);
      expect(evt.defaultPrevented).toBe(true);
    });

    it('wraps Shift+Tab from the first focusable element to the last when open', () => {
      buildChatFixture();
      runScript(registered);
      const { toggle, close, send } = elements();

      toggle.click(); // open
      close.focus();
      expect(document.activeElement).toBe(close);

      const evt = new KeyboardEvent('keydown', {
        key: 'Tab',
        shiftKey: true,
        bubbles: true,
        cancelable: true,
      });
      document.dispatchEvent(evt);

      expect(document.activeElement).toBe(send);
      expect(evt.defaultPrevented).toBe(true);
    });
  });
});
