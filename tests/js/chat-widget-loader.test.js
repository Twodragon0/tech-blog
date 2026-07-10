// Regression tests for assets/js/chat-widget-loader.js
//
// chat-widget-loader.js is a tiny IIFE that lazy-loads the real
// chat-widget.js bundle (plus its DOMPurify dependency) only after the user
// clicks #chat-widget-toggle. It never actually fetches those scripts in
// jsdom, so the CDN load/error outcome is simulated by directly invoking the
// `.onload` / `.onerror` handlers the source assigns onto the injected
// <script> elements (jsdom does not perform real network fetches for
// dynamically-inserted <script src="...">, so dispatching synthetic 'load'
// events would not exercise this code either way -- calling the assigned
// handler function directly is the deterministic equivalent).
//
// document.currentScript is a read-only accessor inherited from
// Document.prototype; tests that need a custom data-chat-src stub it by
// defining an own property on the (shared) `document` object, then delete
// it again in afterEach so later tests see the real (null) value.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/chat-widget-loader.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

function buildFixture() {
  document.body.innerHTML = '<button id="chat-widget-toggle"></button>';
}

function purifyScriptEl() {
  return document.head.querySelector('script[src*="dompurify"]');
}

describe('chat-widget-loader.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    document.head.querySelectorAll('script').forEach((el) => el.remove());
  });

  afterEach(() => {
    document.body.innerHTML = '';
    document.head.querySelectorAll('script').forEach((el) => el.remove());
    delete document.currentScript;
  });

  it('does nothing (no throw, no injected scripts) when #chat-widget-toggle is missing', () => {
    document.body.innerHTML = '<div id="unrelated"></div>';
    expect(() => runScript()).not.toThrow();
    expect(document.head.querySelectorAll('script').length).toBe(0);
  });

  it('injects the DOMPurify CDN script with the correct src/integrity/crossOrigin on toggle click', () => {
    buildFixture();
    runScript();
    const toggle = document.getElementById('chat-widget-toggle');

    expect(purifyScriptEl()).toBeNull();
    toggle.click();

    const purify = purifyScriptEl();
    expect(purify).not.toBeNull();
    expect(purify.src).toBe(
      'https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.2.4/purify.min.js'
    );
    expect(purify.integrity).toBe(
      'sha384-eEu5CTj3qGvu9PdJuS+YlkNi7d2XxQROAFYOr59zgObtlcux1ae1Il3u7jvdCSWu'
    );
    expect(purify.crossOrigin).toBe('anonymous');
  });

  it('defaults the widget src to /assets/js/chat-widget.js when there is no data-chat-src script tag', () => {
    buildFixture();
    runScript();
    document.getElementById('chat-widget-toggle').click();

    purifyScriptEl().onload();

    const widgetScript = document.body.querySelector('script[src="/assets/js/chat-widget.js"]');
    expect(widgetScript).not.toBeNull();
  });

  it("reads the widget src from document.currentScript's data-chat-src attribute when present", () => {
    const fakeScript = document.createElement('script');
    fakeScript.setAttribute('data-chat-src', '/assets/js/custom-widget.js');
    Object.defineProperty(document, 'currentScript', {
      value: fakeScript,
      configurable: true,
    });

    buildFixture();
    runScript();
    document.getElementById('chat-widget-toggle').click();

    purifyScriptEl().onload();

    const widgetScript = document.body.querySelector('script[src="/assets/js/custom-widget.js"]');
    expect(widgetScript).not.toBeNull();
    expect(document.body.querySelector('script[src="/assets/js/chat-widget.js"]')).toBeNull();
  });

  it('does not inject a second DOMPurify script on a second click (once-guarded listener)', () => {
    buildFixture();
    runScript();
    const toggle = document.getElementById('chat-widget-toggle');

    toggle.click();
    expect(document.head.querySelectorAll('script').length).toBe(1);

    toggle.click(); // listener was registered with { once: true } -> no-op
    expect(document.head.querySelectorAll('script').length).toBe(1);
  });

  it('appends the chat-widget script to <body> with defer=true after DOMPurify loads successfully', () => {
    buildFixture();
    runScript();
    document.getElementById('chat-widget-toggle').click();

    purifyScriptEl().onload();

    const widgetScript = document.body.querySelector('script[src="/assets/js/chat-widget.js"]');
    expect(widgetScript).not.toBeNull();
    expect(widgetScript.defer).toBe(true);
  });

  it("clicks the toggle again once the DOMPurify-success chat-widget script's onload fires", () => {
    buildFixture();
    const toggle = document.getElementById('chat-widget-toggle');
    const clickSpy = vi.fn();
    toggle.addEventListener('click', clickSpy); // independent listener, not once-guarded

    runScript();
    toggle.click();
    expect(clickSpy).toHaveBeenCalledTimes(1);

    purifyScriptEl().onload();
    const widgetScript = document.body.querySelector('script[src="/assets/js/chat-widget.js"]');
    widgetScript.onload();

    expect(clickSpy).toHaveBeenCalledTimes(2);
  });

  it('falls back to appending the chat-widget script directly to <body> when the DOMPurify CDN script errors', () => {
    buildFixture();
    runScript();
    document.getElementById('chat-widget-toggle').click();

    expect(document.body.querySelector('script[src="/assets/js/chat-widget.js"]')).toBeNull();
    purifyScriptEl().onerror();

    const widgetScript = document.body.querySelector('script[src="/assets/js/chat-widget.js"]');
    expect(widgetScript).not.toBeNull();
    expect(widgetScript.defer).toBe(true);
  });

  it("clicks the toggle again once the DOMPurify-failure fallback script's onload fires", () => {
    buildFixture();
    const toggle = document.getElementById('chat-widget-toggle');
    const clickSpy = vi.fn();
    toggle.addEventListener('click', clickSpy);

    runScript();
    toggle.click();
    expect(clickSpy).toHaveBeenCalledTimes(1);

    purifyScriptEl().onerror();
    const widgetScript = document.body.querySelector('script[src="/assets/js/chat-widget.js"]');
    widgetScript.onload();

    expect(clickSpy).toHaveBeenCalledTimes(2);
  });
});
