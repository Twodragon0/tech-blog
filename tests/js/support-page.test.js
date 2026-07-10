// Regression tests for assets/js/support-page.js
//
// support-page.js is a standalone IIFE that:
//   1. Bails immediately when no `.newsletter-form` element is present in
//      the DOM (no listeners attached, no success/error nodes injected).
//   2. Injects `.success-message` / `.error-message` nodes into the form.
//   3. On submit: if the email input is empty or fails HTML5 email
//      validation, prevents submission, shows the error message (auto-hides
//      after 5s), and returns false.
//   4. On submit with a valid email: opens a named popup window, toggles a
//      `loading` class + disables the submit button for 1s, then polls
//      (setInterval, 100ms) the popup's `closed` state to show the success
//      message and clear the input once the popup closes — with a 3s
//      failsafe that clears the poll interval regardless.
//   5. Clears both messages when the email input regains focus.
//   6. Wires an optional `#buyme-coffee-btn` to preventDefault + alert().
//
// We evaluate the IIFE with new Function() after each test builds its own
// DOM fixture, matching the pattern used by the other tests in this suite.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/support-page.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

/** Build a newsletter-form fixture with an email input + submit button. */
function buildNewsletterFixture() {
  document.body.innerHTML = `
    <form class="newsletter-form" action="https://buttondown.com/api/emails/embed-subscribe/twodragon" target="popupwindow">
      <input type="email" name="email" />
      <button type="submit">Subscribe</button>
    </form>
  `;
}

/** Dispatch a cancelable submit event on the form and return the event. */
function submitForm(form) {
  const event = new Event('submit', { bubbles: true, cancelable: true });
  form.dispatchEvent(event);
  return event;
}

describe('support-page.js', () => {
  let originalOpen;
  let originalAlert;

  beforeEach(() => {
    originalOpen = window.open;
    originalAlert = window.alert;
    document.body.innerHTML = '';
  });

  afterEach(() => {
    window.open = originalOpen;
    window.alert = originalAlert;
    document.body.innerHTML = '';
    vi.useRealTimers();
  });

  // =========================================================================
  // Early-bail: no newsletter form
  // =========================================================================

  it('bails when no .newsletter-form element is present', () => {
    document.body.innerHTML = '<div class="support-page"></div>';
    expect(() => runScript()).not.toThrow();
    expect(document.querySelector('.success-message')).toBeNull();
    expect(document.querySelector('.error-message')).toBeNull();
  });

  // =========================================================================
  // Message nodes injected into the form
  // =========================================================================

  it('injects .success-message and .error-message nodes into the form', () => {
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const success = form.querySelector('.success-message');
    const error = form.querySelector('.error-message');

    expect(success).not.toBeNull();
    expect(error).not.toBeNull();
    expect(success.textContent).toMatch(/구독이 완료/);
    expect(error.textContent).toMatch(/오류가 발생/);
  });

  // =========================================================================
  // Submit with empty email
  // =========================================================================

  it('prevents submission and shows the error message when email is empty', () => {
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const errorMsg = form.querySelector('.error-message');
    const successMsg = form.querySelector('.success-message');

    const event = submitForm(form);

    expect(event.defaultPrevented).toBe(true);
    expect(errorMsg.style.display).toBe('block');
    expect(successMsg.style.display).toBe('none');
  });

  it('auto-hides the error message 5s after an invalid submission', () => {
    vi.useFakeTimers();
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const errorMsg = form.querySelector('.error-message');

    submitForm(form);
    expect(errorMsg.style.display).toBe('block');

    vi.advanceTimersByTime(5000);
    expect(errorMsg.style.display).toBe('none');
  });

  // =========================================================================
  // Submit with a malformed (non-empty) email
  // =========================================================================

  it('prevents submission when the email fails HTML5 validation', () => {
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const emailInput = form.querySelector('input[type="email"]');
    emailInput.value = 'not-an-email';
    const errorMsg = form.querySelector('.error-message');

    const event = submitForm(form);

    expect(emailInput.validity.valid).toBe(false);
    expect(event.defaultPrevented).toBe(true);
    expect(errorMsg.style.display).toBe('block');
  });

  // =========================================================================
  // Submit with a valid email — popup + loading state
  // =========================================================================

  it('opens the buttondown popup and does not preventDefault on a valid email', () => {
    window.open = vi.fn(() => ({ closed: false }));
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const emailInput = form.querySelector('input[type="email"]');
    emailInput.value = 'reader@example.com';

    const event = submitForm(form);

    expect(event.defaultPrevented).toBe(false);
    expect(window.open).toHaveBeenCalledWith('https://buttondown.com/twodragon', 'popupwindow');
  });

  it('toggles the loading class and disables the submit button while pending', () => {
    window.open = vi.fn(() => ({ closed: false }));
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const emailInput = form.querySelector('input[type="email"]');
    const submitButton = form.querySelector('button[type="submit"]');
    emailInput.value = 'reader@example.com';

    submitForm(form);

    expect(form.classList.contains('loading')).toBe(true);
    expect(submitButton.disabled).toBe(true);
  });

  it('re-enables the submit button and clears the loading class after 1s', () => {
    vi.useFakeTimers();
    window.open = vi.fn(() => ({ closed: false }));
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const emailInput = form.querySelector('input[type="email"]');
    const submitButton = form.querySelector('button[type="submit"]');
    emailInput.value = 'reader@example.com';

    submitForm(form);
    expect(form.classList.contains('loading')).toBe(true);

    vi.advanceTimersByTime(1000);

    expect(form.classList.contains('loading')).toBe(false);
    expect(submitButton.disabled).toBe(false);
  });

  it('shows the success message and clears the email once the popup reports closed:false', () => {
    vi.useFakeTimers();
    window.open = vi.fn(() => ({ closed: false }));
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const emailInput = form.querySelector('input[type="email"]');
    const successMsg = form.querySelector('.success-message');
    emailInput.value = 'reader@example.com';

    submitForm(form);
    // Advance past the 1s pre-poll delay, then one 100ms poll tick.
    vi.advanceTimersByTime(1100);

    expect(successMsg.style.display).toBe('block');
    expect(emailInput.value).toBe('');
  });

  it('clears the poll interval without crashing when window.open("", popupwindow) throws', () => {
    vi.useFakeTimers();
    let callCount = 0;
    window.open = vi.fn(() => {
      callCount += 1;
      if (callCount === 1) {
        return { closed: false }; // initial popup-open call
      }
      throw new Error('SecurityError: cross-origin window access blocked');
    });
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const emailInput = form.querySelector('input[type="email"]');
    const successMsg = form.querySelector('.success-message');
    emailInput.value = 'reader@example.com';

    submitForm(form);

    expect(() => vi.advanceTimersByTime(1100)).not.toThrow();
    // The catch branch clears the poll interval and never flips success on.
    expect(successMsg.style.display).not.toBe('block');
  });

  it('clears the poll interval via the 3s failsafe when the popup never reports closed', () => {
    vi.useFakeTimers();
    window.open = vi.fn(() => ({ closed: true }));
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const emailInput = form.querySelector('input[type="email"]');
    const successMsg = form.querySelector('.success-message');
    emailInput.value = 'reader@example.com';

    submitForm(form);
    // 1s pre-poll delay + 3s failsafe should fully drain without throwing,
    // and success should never trigger because closed is never false.
    expect(() => vi.advanceTimersByTime(4100)).not.toThrow();
    expect(successMsg.style.display).not.toBe('block');
  });

  // =========================================================================
  // Focus on email input clears both messages
  // =========================================================================

  it('hides both messages when the email input regains focus', () => {
    buildNewsletterFixture();
    runScript();

    const form = document.querySelector('.newsletter-form');
    const emailInput = form.querySelector('input[type="email"]');
    const successMsg = form.querySelector('.success-message');
    const errorMsg = form.querySelector('.error-message');

    successMsg.style.display = 'block';
    errorMsg.style.display = 'block';

    emailInput.dispatchEvent(new Event('focus'));

    expect(successMsg.style.display).toBe('none');
    expect(errorMsg.style.display).toBe('none');
  });

  // =========================================================================
  // Buy Me a Coffee button
  // =========================================================================

  it('prevents default and alerts when #buyme-coffee-btn is clicked', () => {
    buildNewsletterFixture();
    const btn = document.createElement('button');
    btn.id = 'buyme-coffee-btn';
    document.body.appendChild(btn);
    window.alert = vi.fn();

    runScript();

    const event = new MouseEvent('click', { bubbles: true, cancelable: true });
    btn.dispatchEvent(event);

    expect(event.defaultPrevented).toBe(true);
    expect(window.alert).toHaveBeenCalledWith(
      expect.stringMatching(/Buy Me a Coffee/)
    );
  });

  it('does not attach a click handler when #buyme-coffee-btn is absent', () => {
    buildNewsletterFixture();
    window.alert = vi.fn();

    expect(() => runScript()).not.toThrow();
    expect(document.getElementById('buyme-coffee-btn')).toBeNull();
  });
});
