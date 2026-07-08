// Regression tests for assets/js/google-translate.js
//
// google-translate.js is a language-toggle widget: a top-level IIFE reads
// `document.readyState` once at eval time and, either immediately (via
// setTimeout(fn, 100)) or after 'DOMContentLoaded', wires up:
//   - a dropdown toggle (#lang-toggle/#lang-dropdown) with click-outside-
//     to-close and dblclick-to-reset-to-system-language behavior,
//   - changeLang(lang), which sets/deletes the `googtrans` cookie and
//     schedules a reload,
//   - DOM cleanup helpers (cleanupFontTags/restoreLangStructure/
//     hideGoogleTranslateBanner/addAttributesToTranslateSelect) that also
//     re-run on every MutationObserver-observed change to document.body.
// None of these are exported; everything lives inside the IIFE closure and
// is only reachable through the DOM/timer surface it wires up itself, so we
// eval the script fresh per test (same `new Function('window','document',
// SOURCE)` technique as tests/js/chat-widget.test.js) and drive it via real
// events plus `vi.useFakeTimers()` to cross the internal 100ms setTimeout
// gate that every init path in this script goes through.
//
// jsdom reports `document.readyState === 'complete'` by default (verified
// empirically), so the script always takes the "already loaded" branch:
// `setTimeout(initLangToggle + friends, 100)`.
//
// `location` is patched via delete+reassign (the documented jsdom
// workaround for the non-configurable window.location.hostname property),
// matching tests/js/categories-page.test.js and tests/js/sentry-init.test.js.
// A `document.addEventListener('click', ...)` (outside-click-closes) is
// registered once initLangToggle() runs; since `document` persists across
// tests in this file we capture and remove it in afterEach, matching
// tests/js/chat-widget.test.js's `registered` sink pattern.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/google-translate.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function setLocation({ protocol = 'https:', hostname = 'example.com', href = 'https://example.com/', pathname = '/' } = {}) {
  delete window.location;
  window.location = { protocol, hostname, href, pathname, hash: '', origin: `${protocol}//${hostname}`, reload: vi.fn() };
}

function clearAllCookies() {
  document.cookie.split(';').forEach((c) => {
    const name = c.split('=')[0].trim();
    if (name) {
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/`;
    }
  });
}

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

function buildToggleFixture() {
  document.body.innerHTML = `
    <div class="lang-toggle-wrapper">
      <button id="lang-toggle" aria-expanded="false"><span id="current-lang">KO</span></button>
      <div id="lang-dropdown">
        <button class="lang-option" data-lang="en">EN</button>
        <button class="lang-option" data-lang="ja">JA</button>
        <button class="lang-option" data-lang="ko">KO</button>
      </div>
      <div id="lang-dropdown-overlay" aria-hidden="true"></div>
    </div>
  `;
}

/** Run the script and advance fake timers past the internal 100ms init gate. */
function runAndInit(handlerSink) {
  runScript(handlerSink);
  vi.advanceTimersByTime(100);
}

describe('google-translate.js', () => {
  let registered;
  let originalNavigatorLanguage;

  beforeEach(() => {
    vi.useFakeTimers();
    registered = [];
    document.body.innerHTML = '';
    // A prior test's loadTranslateScript() call may have appended a
    // `<script src=".../translate_a/element.js">` to <head>; that node is
    // never touched by resetting document.body, so it would otherwise leak
    // into later tests' `document.querySelector('script[src*=...]')` checks.
    document.head.innerHTML = '';
    localStorage.clear();
    sessionStorage.clear();
    clearAllCookies();
    setLocation();
    originalNavigatorLanguage = Object.getOwnPropertyDescriptor(window.navigator, 'language');
    Object.defineProperty(window.navigator, 'language', { value: 'ko-KR', configurable: true });
  });

  afterEach(() => {
    for (const r of registered) {
      document.removeEventListener(r.evt, r.handler, r.opts);
    }
    if (originalNavigatorLanguage) {
      Object.defineProperty(window.navigator, 'language', originalNavigatorLanguage);
    }
    document.body.innerHTML = '';
    localStorage.clear();
    sessionStorage.clear();
    clearAllCookies();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe('initLangToggle — dropdown open/close', () => {
    it('does not throw when #lang-toggle/#lang-dropdown are missing (early-return guard)', () => {
      document.body.innerHTML = '<div></div>';
      expect(() => runAndInit(registered)).not.toThrow();
    });

    it('opens the dropdown and flips aria-expanded + overlay state on toggle click', () => {
      buildToggleFixture();
      runAndInit(registered);

      const toggle = document.getElementById('lang-toggle');
      const dropdown = document.getElementById('lang-dropdown');
      const overlay = document.getElementById('lang-dropdown-overlay');

      toggle.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      expect(dropdown.classList.contains('active')).toBe(true);
      expect(toggle.getAttribute('aria-expanded')).toBe('true');
      expect(overlay.classList.contains('active')).toBe(true);
      expect(overlay.getAttribute('aria-hidden')).toBe('false');
    });

    it('closes the dropdown on a second toggle click', () => {
      buildToggleFixture();
      runAndInit(registered);
      const toggle = document.getElementById('lang-toggle');
      const dropdown = document.getElementById('lang-dropdown');

      toggle.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      toggle.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      expect(dropdown.classList.contains('active')).toBe(false);
      expect(toggle.getAttribute('aria-expanded')).toBe('false');
    });

    it('closes the dropdown when clicking outside it', () => {
      buildToggleFixture();
      runAndInit(registered);
      const toggle = document.getElementById('lang-toggle');
      const dropdown = document.getElementById('lang-dropdown');

      toggle.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      expect(dropdown.classList.contains('active')).toBe(true);

      document.body.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      expect(dropdown.classList.contains('active')).toBe(false);
      expect(toggle.getAttribute('aria-expanded')).toBe('false');
    });

    it('does not close the dropdown when the click target is inside it', () => {
      buildToggleFixture();
      runAndInit(registered);
      const toggle = document.getElementById('lang-toggle');
      const dropdown = document.getElementById('lang-dropdown');

      toggle.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      dropdown.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      expect(dropdown.classList.contains('active')).toBe(true);
    });
  });

  describe('dblclick — reset to system language', () => {
    it('reverts to the detected system language, clears session flags, and updates the label', () => {
      Object.defineProperty(window.navigator, 'language', { value: 'ja-JP', configurable: true });
      localStorage.setItem('preferredLang', 'en');
      sessionStorage.setItem('langApplied', 'true');
      buildToggleFixture();
      runAndInit(registered);

      const toggle = document.getElementById('lang-toggle');
      toggle.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));

      expect(localStorage.getItem('preferredLang')).toBe('system');
      expect(document.getElementById('current-lang').textContent).toBe('JA');
      // The handler clears 'langApplied' *before* calling changeLang('ja'),
      // but changeLang's own non-Korean branch immediately sets it back to
      // 'true' (no select present, so it takes the "set flags then reload"
      // path) — so the net observable end-state is 'true', not cleared.
      expect(sessionStorage.getItem('langApplied')).toBe('true');
    });

    it('schedules a reload after changing to a non-Korean system language (no goog-te-combo present)', () => {
      Object.defineProperty(window.navigator, 'language', { value: 'ja-JP', configurable: true });
      buildToggleFixture();
      runAndInit(registered);

      document.getElementById('lang-toggle').dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));
      vi.advanceTimersByTime(150);

      expect(window.location.reload).toHaveBeenCalledTimes(1);
      expect(document.cookie).toContain('googtrans=/ko/ja');
    });
  });

  describe('lang-option click — changeLang to a non-Korean language', () => {
    it('sets the googtrans cookie, updates the label, persists the preference, and reloads', () => {
      buildToggleFixture();
      runAndInit(registered);

      document.getElementById('lang-toggle').dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      const enOption = document.querySelector('.lang-option[data-lang="en"]');
      enOption.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      expect(document.getElementById('lang-dropdown').classList.contains('active')).toBe(false);
      expect(document.getElementById('current-lang').textContent).toBe('EN');
      expect(localStorage.getItem('preferredLang')).toBe('en');
      expect(document.cookie).toContain('googtrans=/ko/en');

      vi.advanceTimersByTime(150);
      expect(window.location.reload).toHaveBeenCalledTimes(1);
    });

    it('falls back to text-content language detection when data-lang is absent', () => {
      document.body.innerHTML = `
        <button id="lang-toggle" aria-expanded="false"><span id="current-lang">KO</span></button>
        <div id="lang-dropdown">
          <button class="lang-option">English</button>
        </div>
      `;
      runAndInit(registered);

      document.querySelector('.lang-option').dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      expect(localStorage.getItem('preferredLang')).toBe('en');
      expect(document.getElementById('current-lang').textContent).toBe('EN');
    });

    it('does nothing when a lang-option has neither data-lang nor recognizable text', () => {
      document.body.innerHTML = `
        <button id="lang-toggle" aria-expanded="false"><span id="current-lang">KO</span></button>
        <div id="lang-dropdown">
          <button class="lang-option">???</button>
        </div>
      `;
      runAndInit(registered);

      document.querySelector('.lang-option').dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      expect(localStorage.getItem('preferredLang')).toBeNull();
      expect(document.getElementById('current-lang').textContent).toBe('KO');
    });
  });

  describe('changeLang("ko") — revert-to-Korean branch', () => {
    it('deletes the googtrans cookie, resets body offset styles, and schedules a reload when the URL has no googtrans hash', () => {
      document.cookie = 'googtrans=/ko/en; path=/';
      // Match the system language to the pre-set cookie's language so
      // applySystemLanguage()'s own auto-correct branch (which fires an
      // independent changeLang('ko') during init when system-pref and
      // cookie-derived language disagree) stays quiet — otherwise it would
      // race the user's click and double the scheduled reload.
      Object.defineProperty(window.navigator, 'language', { value: 'en-US', configurable: true });
      buildToggleFixture();
      runAndInit(registered);

      document.getElementById('lang-toggle').dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      document
        .querySelector('.lang-option[data-lang="ko"]')
        .dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      expect(document.cookie).not.toContain('googtrans=');
      expect(document.body.style.top).toBe('0px');

      vi.advanceTimersByTime(200);
      expect(window.location.reload).toHaveBeenCalledTimes(1);
    });

    it('rewrites window.location.href instead of reloading when the URL carries a #googtrans(...) hash', () => {
      setLocation({ href: 'https://example.com/page#googtrans(ko|en)' });
      buildToggleFixture();
      runAndInit(registered);

      document.getElementById('lang-toggle').dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      document
        .querySelector('.lang-option[data-lang="ko"]')
        .dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      vi.advanceTimersByTime(200);

      expect(window.location.href).toBe('https://example.com/page');
      expect(window.location.reload).not.toHaveBeenCalled();
    });

    it('removes an existing Google Translate banner iframe when reverting to Korean', () => {
      buildToggleFixture();
      document.body.insertAdjacentHTML('beforeend', '<iframe class="goog-te-banner-frame"></iframe>');
      runAndInit(registered);

      document.getElementById('lang-toggle').dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      document
        .querySelector('.lang-option[data-lang="ko"]')
        .dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

      expect(document.querySelector('.goog-te-banner-frame')).toBeNull();
    });
  });

  describe('getCurrentLang / initial label rendering', () => {
    it('reflects the googtrans cookie language when no explicit preference is saved', () => {
      document.cookie = 'googtrans=/ko/ja; path=/';
      buildToggleFixture();
      runAndInit(registered);

      expect(document.getElementById('current-lang').textContent).toBe('JA');
    });

    it('prefers an explicit localStorage preference over the cookie-derived language', () => {
      document.cookie = 'googtrans=/ko/ja; path=/';
      localStorage.setItem('preferredLang', 'es');
      buildToggleFixture();
      runAndInit(registered);

      expect(document.getElementById('current-lang').textContent).toBe('ES');
    });

    it('defaults to Korean when there is no cookie at all', () => {
      buildToggleFixture();
      runAndInit(registered);

      expect(document.getElementById('current-lang').textContent).toBe('KO');
    });
  });

  describe('DOM cleanup helpers (run once on the 100ms init pass)', () => {
    it('cleanupFontTags unwraps Google-Translate-inserted <font> tags without losing their text', () => {
      document.body.innerHTML = `
        <div class="lang-toggle-wrapper">before<font>English</font>after</div>
      `;
      runAndInit(registered);

      const wrapper = document.querySelector('.lang-toggle-wrapper');
      expect(wrapper.querySelector('font')).toBeNull();
      expect(wrapper.textContent).toBe('beforeEnglishafter');
    });

    it('restoreLangStructure rebuilds missing lang-flag/lang-name spans from data-lang', () => {
      document.body.innerHTML = `
        <div id="lang-dropdown">
          <button class="lang-option" data-lang="en">garbled</button>
        </div>
      `;
      runAndInit(registered);

      const option = document.querySelector('.lang-option');
      expect(option.querySelector('.lang-flag')).not.toBeNull();
      expect(option.querySelector('.lang-name').textContent).toBe('English');
    });

    it('restoreLangStructure strips stray text nodes injected directly into #lang-dropdown', () => {
      document.body.innerHTML = `<div id="lang-dropdown">stray text<button class="lang-option" data-lang="en"><span class="lang-flag">x</span><span class="lang-name">English</span></button></div>`;
      runAndInit(registered);

      const dropdown = document.getElementById('lang-dropdown');
      const strayTextNodes = Array.from(dropdown.childNodes).filter(
        (n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim()
      );
      expect(strayTextNodes).toHaveLength(0);
    });

    it('addAttributesToTranslateSelect adds id/name/aria-label to a bare .goog-te-combo select', () => {
      document.body.innerHTML = '<select class="goog-te-combo"></select>';
      runAndInit(registered);

      const select = document.querySelector('.goog-te-combo');
      expect(select.id).toBe('google-translate-select');
      expect(select.name).toBe('google-translate-language');
      expect(select.getAttribute('aria-label')).toBe('번역 언어 선택');
    });

    it('addAttributesToTranslateSelect does not overwrite an existing id', () => {
      document.body.innerHTML = '<select class="goog-te-combo" id="custom-id"></select>';
      runAndInit(registered);

      expect(document.querySelector('.goog-te-combo').id).toBe('custom-id');
    });

    it('hideGoogleTranslateBanner force-hides banner/tooltip elements and resets body offset', () => {
      document.body.innerHTML = '<div class="goog-te-banner-frame"></div><div id="goog-gt-tt"></div>';
      document.body.style.top = '-40px';
      runAndInit(registered);

      const banner = document.querySelector('.goog-te-banner-frame');
      expect(banner.style.display).toBe('none');
      expect(banner.style.visibility).toBe('hidden');
      expect(document.body.style.top).toBe('0px');
      expect(document.body.style.position).toBe('static');
    });
  });

  describe('MutationObserver — reacts to dynamically inserted Google Translate DOM', () => {
    it('hides a VIpgJd-classed node inserted into the body after init', async () => {
      buildToggleFixture();
      runAndInit(registered);

      const injected = document.createElement('div');
      injected.className = 'VIpgJd-ZVi9od-xl07Ob-lTBxed';
      document.body.appendChild(injected);

      // MutationObserver callbacks run as a microtask queued independently
      // of the timer mocks; flush the microtask queue directly.
      await Promise.resolve();
      await Promise.resolve();

      expect(injected.style.display).toBe('none');
    });
  });

  describe('needsTranslate gating (bottom-of-IIFE script-load decision)', () => {
    it('does not append the Google Translate loader script when the system language is Korean and no preference is saved', () => {
      Object.defineProperty(window.navigator, 'language', { value: 'ko-KR', configurable: true });
      buildToggleFixture();
      runScript(registered);
      vi.advanceTimersByTime(500);

      expect(document.querySelector('script[src*="translate_a/element.js"]')).toBeNull();
    });

    it('appends the Google Translate loader script when the saved preference is a non-Korean language', () => {
      localStorage.setItem('preferredLang', 'en');
      buildToggleFixture();
      runScript(registered);
      vi.advanceTimersByTime(500);

      expect(document.querySelector('script[src*="translate_a/element.js"]')).not.toBeNull();
    });

    it('appends the loader script when the system language is non-Korean and no preference is saved', () => {
      Object.defineProperty(window.navigator, 'language', { value: 'en-US', configurable: true });
      buildToggleFixture();
      runScript(registered);
      vi.advanceTimersByTime(500);

      expect(document.querySelector('script[src*="translate_a/element.js"]')).not.toBeNull();
    });
  });
});
