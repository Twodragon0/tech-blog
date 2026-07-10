// Regression tests for assets/js/subscribe-float.js
//
// Goal: prove the feedback-button IIFE (a) no-ops safely when
// #custom-feedback-btn is missing from the DOM, (b) wires a click
// handler that opens the GitHub issues URL in a new tab when the
// button exists, (c) does not fire window.open before the button is
// clicked, and (d) re-running the script (double "init") attaches an
// additional listener rather than guarding against re-registration —
// documenting the script's actual (unguarded) behavior.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/subscribe-float.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

const EXPECTED_URL = 'https://github.com/Twodragon0/tech-blog/issues/new';

describe('subscribe-float.js', () => {
  let originalOpen;

  beforeEach(() => {
    originalOpen = window.open;
    document.body.innerHTML = '';
  });

  afterEach(() => {
    window.open = originalOpen;
    document.body.innerHTML = '';
  });

  it('does not throw and does not touch window.open when #custom-feedback-btn is missing', () => {
    window.open = vi.fn();
    expect(() => runScript()).not.toThrow();
    expect(window.open).not.toHaveBeenCalled();
  });

  it('attaches a click listener that opens the GitHub issues URL in a new tab', () => {
    const btn = document.createElement('button');
    btn.id = 'custom-feedback-btn';
    document.body.appendChild(btn);
    window.open = vi.fn();

    runScript();
    expect(window.open).not.toHaveBeenCalled();

    btn.click();
    expect(window.open).toHaveBeenCalledTimes(1);
    expect(window.open).toHaveBeenCalledWith(EXPECTED_URL, '_blank');
  });

  it('ignores clicks on unrelated elements (no listener leakage)', () => {
    const btn = document.createElement('button');
    btn.id = 'custom-feedback-btn';
    document.body.appendChild(btn);

    const other = document.createElement('button');
    other.id = 'some-other-btn';
    document.body.appendChild(other);

    window.open = vi.fn();
    runScript();

    other.click();
    expect(window.open).not.toHaveBeenCalled();
  });

  it('running the script twice attaches two listeners (no double-init guard)', () => {
    const btn = document.createElement('button');
    btn.id = 'custom-feedback-btn';
    document.body.appendChild(btn);
    window.open = vi.fn();

    runScript();
    runScript();

    btn.click();
    expect(window.open).toHaveBeenCalledTimes(2);
    expect(window.open).toHaveBeenNthCalledWith(1, EXPECTED_URL, '_blank');
    expect(window.open).toHaveBeenNthCalledWith(2, EXPECTED_URL, '_blank');
  });

  it('re-runs safely against a fresh DOM with no button present after removal', () => {
    const btn = document.createElement('button');
    btn.id = 'custom-feedback-btn';
    document.body.appendChild(btn);
    runScript();

    // Simulate a re-run after the button was removed from the DOM
    // (e.g. a partial re-render) — the second run must not throw.
    btn.remove();
    window.open = vi.fn();
    expect(() => runScript()).not.toThrow();
    expect(window.open).not.toHaveBeenCalled();
  });
});
