// Regression tests for assets/js/header-runtime.js (lang toggle bootstrap)
//
// Goal: prove the lang-toggle bootstrap (a) bails cleanly when the toggle is
// missing, (b) lazy-loads google-translate.js exactly once on first click,
// and (c) auto-loads when localStorage already shows a non-Korean preference.

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/header-runtime.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

function injectedScripts() {
  return Array.from(document.querySelectorAll('script[src*="google-translate.js"]'));
}

describe('header-runtime.js (lang toggle bootstrap)', () => {
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

  it('bails cleanly when #lang-toggle is missing', () => {
    expect(() => runScript()).not.toThrow();
    expect(injectedScripts()).toHaveLength(0);
  });

  it('attaches a one-shot click listener that loads google-translate.js', () => {
    document.body.innerHTML = '<button id="lang-toggle" type="button">Lang</button>';
    runScript();

    expect(injectedScripts()).toHaveLength(0);
    document.getElementById('lang-toggle').click();
    expect(injectedScripts()).toHaveLength(1);
    expect(injectedScripts()[0].defer).toBe(true);
  });

  it('does not double-load when clicked twice (idempotent)', () => {
    document.body.innerHTML = '<button id="lang-toggle" type="button">Lang</button>';
    runScript();

    const toggle = document.getElementById('lang-toggle');
    toggle.click();
    toggle.click();
    toggle.click();
    expect(injectedScripts()).toHaveLength(1);
  });

  it('auto-loads google-translate.js when localStorage preferredLang is non-ko', () => {
    document.body.innerHTML = '<button id="lang-toggle" type="button">Lang</button>';
    window.localStorage.setItem('preferredLang', 'en');
    runScript();
    expect(injectedScripts()).toHaveLength(1);
  });

  it('does NOT auto-load when localStorage preferredLang is "ko" or "system"', () => {
    document.body.innerHTML = '<button id="lang-toggle" type="button">Lang</button>';
    window.localStorage.setItem('preferredLang', 'ko');
    runScript();
    expect(injectedScripts()).toHaveLength(0);

    document.body.innerHTML = '<button id="lang-toggle" type="button">Lang</button>';
    window.localStorage.setItem('preferredLang', 'system');
    runScript();
    expect(injectedScripts()).toHaveLength(0);
  });

  it('reports the first toggle click through window.__track', () => {
    // The first click is the one google-translate.js structurally cannot see:
    // it is what triggers that script's download. If this stops firing, usage
    // data silently starts at the second click.
    document.body.innerHTML = '<button id="lang-toggle" type="button">Lang</button>';
    const calls = [];
    window.__track = (name, params) => calls.push([name, params]);
    runScript();

    expect(calls).toHaveLength(0);
    document.getElementById('lang-toggle').click();
    expect(calls).toEqual([['lang_toggle_open', { first_open: true }]]);

    // once:true — repeat clicks are counted by google-translate.js instead, so
    // counting them here too would double-report.
    document.getElementById('lang-toggle').click();
    expect(calls).toHaveLength(1);
    delete window.__track;
  });

  it('does not throw when window.__track is absent', () => {
    // head-runtime.js defines __track, but it is a separate script: a load
    // failure there must not take the lang toggle down with it.
    document.body.innerHTML = '<button id="lang-toggle" type="button">Lang</button>';
    delete window.__track;
    runScript();
    expect(() => document.getElementById('lang-toggle').click()).not.toThrow();
    expect(injectedScripts()).toHaveLength(1);
  });

  it('respects a custom data-translate-src override on the script tag', () => {
    // The IIFE reads `document.currentScript`, which is null when evaluated
    // via Function(). Instead, test the fallback default URL is honored.
    document.body.innerHTML = '<button id="lang-toggle" type="button">Lang</button>';
    runScript();
    document.getElementById('lang-toggle').click();
    const injected = injectedScripts();
    expect(injected).toHaveLength(1);
    expect(injected[0].src).toContain('/assets/js/google-translate.js');
  });
});
