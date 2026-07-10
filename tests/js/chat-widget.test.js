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

  // formatMessage() markdown branches — driven through the assistant reply
  // path (DOMPurify present, sanitize = identity) so the real code path from
  // fetch -> addMessage -> formatMessage -> innerHTML is exercised.
  describe('formatMessage markdown rendering', () => {
    async function renderAssistantReply(text) {
      buildChatFixture();
      runScript(registered);
      const { form, input, messages } = elements();
      window.DOMPurify = { sanitize: (html) => html };
      window.fetch = vi.fn(() =>
        Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ response: text }) })
      );
      input.value = 'question text';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flush();
      return messages.querySelector('.chat-message-assistant .chat-message-content');
    }

    it('renders heading, hr and strikethrough', async () => {
      const el = await renderAssistantReply('# Title\n\n---\n\n~~strike~~');
      expect(el.innerHTML).toContain('<h1>Title</h1>');
      expect(el.innerHTML).toContain('<hr>');
      expect(el.innerHTML).toContain('<del>strike</del>');
    });

    it('wraps consecutive unordered and ordered list items', async () => {
      const el = await renderAssistantReply('- item1\n- item2\n\n1. first\n2. second');
      expect(el.innerHTML).toContain('<ul>');
      expect(el.innerHTML).toContain('<li>item1</li>');
      expect(el.innerHTML).toContain('<li>item2</li>');
      expect(el.innerHTML).toContain('</ul>');
      expect(el.innerHTML).toContain('<ol>');
      expect(el.innerHTML).toContain('<li>first</li>');
      expect(el.innerHTML).toContain('</ol>');
    });

    it('renders a markdown table as chat-table markup', async () => {
      const el = await renderAssistantReply('| A | B |\n|---|---|\n| 1 | 2 |');
      expect(el.innerHTML).toContain('chat-table-wrap');
      expect(el.innerHTML).toContain('<th>A</th>');
      expect(el.innerHTML).toContain('<td>1</td>');
    });

    it('blocks a link with a disallowed protocol (ftp)', async () => {
      const el = await renderAssistantReply('[f](ftp://host.example.com/x)');
      expect(el.innerHTML).not.toContain('<a ');
      expect(el.textContent).toContain('f');
    });

    it('blocks a link to a dangerous absolute host (127.0.0.1)', async () => {
      const el = await renderAssistantReply('[l](http://127.0.0.1/admin)');
      expect(el.innerHTML).not.toContain('<a ');
    });

    it('resolves a relative link then blocks it via the dangerous-host check', async () => {
      // window.location.hostname in the jsdom test environment is 'localhost',
      // which is in the dangerousHosts blocklist, so the relative-path
      // resolution branch is exercised but the link still renders as text.
      const el = await renderAssistantReply('[docs](/docs)');
      expect(el.innerHTML).not.toContain('<a ');
      expect(el.textContent).toContain('docs');
    });

    it('falls back to text when the URL is unparseable', async () => {
      const el = await renderAssistantReply('[bad](http://)');
      expect(el.innerHTML).not.toContain('<a ');
      expect(el.textContent).toContain('bad');
    });
  });

  describe('sendMessage status/error branches', () => {
    async function submitWithFetch(fetchImpl) {
      buildChatFixture();
      runScript(registered);
      const { form, input, messages } = elements();
      window.fetch = fetchImpl;
      input.value = 'question text';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flush();
      return messages;
    }

    it('shows the 403 rejection message', async () => {
      const messages = await submitWithFetch(
        vi.fn(() => Promise.resolve({ ok: false, status: 403, json: () => Promise.resolve({}) }))
      );
      expect(messages.textContent).toContain('요청이 거부되었습니다');
    });

    it('shows the default 503 message when errorData.error is absent', async () => {
      const messages = await submitWithFetch(
        vi.fn(() => Promise.resolve({ ok: false, status: 503, json: () => Promise.resolve({}) }))
      );
      expect(messages.textContent).toContain('일시적으로 사용할 수 없습니다');
    });

    it('combines timeoutData.error and suggestion on a 504 response', async () => {
      const messages = await submitWithFetch(
        vi.fn(() =>
          Promise.resolve({
            ok: false,
            status: 504,
            json: () =>
              Promise.resolve({
                error: '응답 생성에 시간이 오래 걸리고 있습니다 (custom)',
                suggestion: '질문을 짧게 해주세요',
              }),
          })
        )
      );
      expect(messages.textContent).toContain('응답 생성에 시간이 오래 걸리고 있습니다 (custom)');
      expect(messages.textContent).toContain('질문을 짧게 해주세요');
    });

    it('shows a custom message on a 400 response', async () => {
      const messages = await submitWithFetch(
        vi.fn(() =>
          Promise.resolve({ ok: false, status: 400, json: () => Promise.resolve({ error: '잘못된 요청입니다' }) })
        )
      );
      expect(messages.textContent).toContain('잘못된 요청입니다');
    });

    it('shows the generic server-error message for an unhandled status code', async () => {
      const messages = await submitWithFetch(
        vi.fn(() => Promise.resolve({ ok: false, status: 418, json: () => Promise.resolve({}) }))
      );
      expect(messages.textContent).toContain('서버 오류 (418)');
    });

    it('shows the timeout message when fetch rejects with an AbortError', async () => {
      const err = new Error('aborted');
      err.name = 'AbortError';
      const messages = await submitWithFetch(vi.fn(() => Promise.reject(err)));
      expect(messages.textContent).toContain('응답 생성에 시간이 오래 걸리고 있습니다');
      expect(messages.querySelector('.chat-retry-button')).toBeNull();
    });

    it('shows a generic error and no retry button when the response shape is invalid', async () => {
      const messages = await submitWithFetch(
        vi.fn(() => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) }))
      );
      expect(messages.textContent).toContain('응답 형식이 올바르지 않습니다');
      expect(messages.querySelector('.chat-retry-button')).toBeNull();
    });

    it('ignores a second submit while the first request is still in flight', async () => {
      buildChatFixture();
      runScript(registered);
      const { form, input } = elements();

      let resolveFetch;
      window.fetch = vi.fn(
        () =>
          new Promise((resolve) => {
            resolveFetch = resolve;
          })
      );

      input.value = 'first message long enough';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));

      // Second submit while isLoading is true should be a no-op (sendMessage
      // returns immediately, guarded by `if (isLoading) return;`).
      input.value = 'second message long enough';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));

      expect(window.fetch).toHaveBeenCalledTimes(1);

      resolveFetch({ ok: true, status: 200, json: () => Promise.resolve({ response: 'ok', usage: { promptTokens: 1 } }) });
      await flush();
      expect(window.fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('toggleChat mobile viewport', () => {
    let originalWidth;
    beforeEach(() => {
      originalWidth = window.innerWidth;
    });
    afterEach(() => {
      Object.defineProperty(window, 'innerWidth', { value: originalWidth, configurable: true });
    });

    it('locks body scroll when opening on a narrow viewport', () => {
      Object.defineProperty(window, 'innerWidth', { value: 500, configurable: true });
      buildChatFixture();
      runScript(registered);
      const { toggle } = elements();

      toggle.click();

      expect(document.body.style.overflow).toBe('hidden');
    });

    it('restores body scroll after closing on a narrow viewport', () => {
      Object.defineProperty(window, 'innerWidth', { value: 500, configurable: true });
      buildChatFixture();
      runScript(registered);
      const { toggle } = elements();

      vi.useFakeTimers();
      try {
        toggle.click(); // open (narrow viewport -> body scroll locked)
        toggle.click(); // close (schedules preventBodyScroll(false) after 300ms)
        vi.advanceTimersByTime(300);
        expect(document.body.style.overflow).toBe('');
      } finally {
        vi.useRealTimers();
      }
    });
  });

  describe('getPageContext', () => {
    it('includes post title, tags and excerpt from the page in the request body', async () => {
      document.body.innerHTML = `
        <h1 class="post-title">My Great Post</h1>
        <div class="post-tags"><span class="tag">security</span><span class="tag">devops</span></div>
        <meta name="description" content="A helpful excerpt about the post.">
        <div id="deepseek-chat-widget">
          <button id="chat-widget-toggle" aria-expanded="false"></button>
          <div id="chat-widget-window">
            <button id="chat-widget-close">Close</button>
            <div id="chat-widget-messages"></div>
            <form id="chat-widget-form">
              <input id="chat-widget-input" type="text" />
              <button id="chat-widget-send" type="submit"></button>
            </form>
          </div>
        </div>
      `;
      runScript(registered);
      const { form, input } = elements();

      window.fetch = vi.fn(() =>
        Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ response: 'ok' }) })
      );

      input.value = 'context question';
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flush();

      const body = JSON.parse(window.fetch.mock.calls[0][1].body);
      expect(body.pageContext.title).toBe('My Great Post');
      expect(body.pageContext.tags).toEqual(['security', 'devops']);
      expect(body.pageContext.excerpt).toBe('A helpful excerpt about the post.');
    });
  });
});
