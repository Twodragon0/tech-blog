// Regression tests for assets/js/mermaid-init.js
//
// mermaid-init.js is an IIFE loaded on every post page. It (a) bails
// immediately when the page has no mermaid code blocks, (b) otherwise
// lazy-loads mermaid.js from a CDN with SRI, (c) on load: initializes
// mermaid with a theme derived from `data-theme` + Safari-specific
// flowchart options, converts `.language-mermaid` / `pre code.mermaid`
// blocks into `.mermaid-container` (toolbar + `.mermaid` div, preserving
// the original source in `data-mermaid-source`), and wires up fullscreen
// buttons after `mermaid.run()` resolves, (d) enhances generic alt text
// on static mermaid `<img>`s using the nearest heading, and (e) re-renders
// via a MutationObserver when `data-theme` changes and mermaid is loaded.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/mermaid-init.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8');

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

function getInjectedScript() {
  return document.head.querySelector('script[src*="mermaid.min.js"]');
}

function flushMicrotasks() {
  return new Promise((r) => setTimeout(r, 0));
}

function makeMermaidMock({ runResult = 'resolve' } = {}) {
  return {
    initialize: vi.fn(),
    run: vi.fn(() =>
      runResult === 'resolve' ? Promise.resolve() : Promise.reject(new Error('render boom'))
    ),
  };
}

describe('mermaid-init.js', () => {
  let originalUserAgent;
  let originalWarn;

  beforeEach(() => {
    document.head.innerHTML = '';
    document.body.innerHTML = '';
    document.documentElement.removeAttribute('data-theme');
    delete window.mermaid;
    originalUserAgent = window.navigator.userAgent;
    originalWarn = console.warn;
  });

  afterEach(() => {
    document.head.innerHTML = '';
    document.body.innerHTML = '';
    document.documentElement.removeAttribute('data-theme');
    delete window.mermaid;
    Object.defineProperty(window.navigator, 'userAgent', {
      value: originalUserAgent,
      configurable: true,
    });
    console.warn = originalWarn;
  });

  // =========================================================================
  // Early bail-out (no mermaid diagrams on the page)
  // =========================================================================

  it('does nothing when the page has no mermaid code blocks', () => {
    document.body.innerHTML = '<p>Just a regular paragraph, no diagrams here.</p>';
    runScript();
    expect(getInjectedScript()).toBeNull();
  });

  // =========================================================================
  // Detection + script injection
  // =========================================================================

  it('injects the mermaid CDN script (with SRI) when a .language-mermaid block is present', () => {
    document.body.innerHTML = '<pre class="language-mermaid"><code>graph TD; A--&gt;B;</code></pre>';
    runScript();

    const script = getInjectedScript();
    expect(script).not.toBeNull();
    expect(script.src).toContain('https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js');
    expect(script.integrity).toMatch(/^sha384-/);
    expect(script.crossOrigin).toBe('anonymous');
  });

  it('also detects the alternate "pre code.mermaid" selector', () => {
    document.body.innerHTML = '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>';
    runScript();
    expect(getInjectedScript()).not.toBeNull();
  });

  // =========================================================================
  // onload: theme selection
  // =========================================================================

  it('onload: initializes mermaid with theme "default" when data-theme is absent', () => {
    document.body.innerHTML = '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>';
    const mermaidMock = makeMermaidMock();
    window.mermaid = mermaidMock;
    runScript();

    getInjectedScript().onload();

    expect(mermaidMock.initialize).toHaveBeenCalledWith(
      expect.objectContaining({ theme: 'default', securityLevel: 'strict' })
    );
  });

  it('onload: initializes mermaid with theme "dark" when data-theme="dark"', () => {
    document.documentElement.setAttribute('data-theme', 'dark');
    document.body.innerHTML = '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>';
    const mermaidMock = makeMermaidMock();
    window.mermaid = mermaidMock;
    runScript();

    getInjectedScript().onload();

    expect(mermaidMock.initialize).toHaveBeenCalledWith(
      expect.objectContaining({ theme: 'dark' })
    );
  });

  it('onload: disables flowchart htmlLabels on Safari (foreignObject rendering issue)', () => {
    Object.defineProperty(window.navigator, 'userAgent', {
      value:
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 ' +
        '(KHTML, like Gecko) Version/17.0 Safari/605.1.15',
      configurable: true,
    });
    document.body.innerHTML = '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>';
    const mermaidMock = makeMermaidMock();
    window.mermaid = mermaidMock;
    runScript();

    getInjectedScript().onload();

    expect(mermaidMock.initialize).toHaveBeenCalledWith(
      expect.objectContaining({ flowchart: expect.objectContaining({ htmlLabels: false }) })
    );
  });

  it('onload: keeps flowchart htmlLabels enabled on non-Safari browsers', () => {
    document.body.innerHTML = '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>';
    const mermaidMock = makeMermaidMock();
    window.mermaid = mermaidMock;
    runScript();

    getInjectedScript().onload();

    expect(mermaidMock.initialize).toHaveBeenCalledWith(
      expect.objectContaining({ flowchart: expect.objectContaining({ htmlLabels: true }) })
    );
  });

  // =========================================================================
  // onload: DOM conversion of code blocks -> .mermaid-container
  // =========================================================================

  it('onload: converts a mermaid code block into a container with toolbar + .mermaid div, preserving source', () => {
    document.body.innerHTML =
      '<pre><code class="mermaid">graph TD;\n  A --&gt; B;</code></pre>';
    window.mermaid = makeMermaidMock();
    runScript();

    getInjectedScript().onload();

    expect(document.querySelector('pre')).toBeNull(); // original <pre> replaced
    const container = document.querySelector('.mermaid-container');
    expect(container).not.toBeNull();
    expect(container.querySelector('.mermaid-toolbar .mermaid-fullscreen-btn')).not.toBeNull();

    const mermaidDiv = container.querySelector('.mermaid');
    expect(mermaidDiv).not.toBeNull();
    expect(mermaidDiv.getAttribute('data-mermaid-source')).toBe('graph TD;\n  A --> B;');
    expect(mermaidDiv.textContent).toBe('graph TD;\n  A --> B;');
  });

  it('onload: leaves a code block untouched when its content is empty/whitespace-only', () => {
    document.body.innerHTML = '<pre><code class="mermaid">   \n   </code></pre>';
    window.mermaid = makeMermaidMock();
    runScript();

    getInjectedScript().onload();

    // Empty block is skipped before container creation — original <pre> survives.
    expect(document.querySelector('pre')).not.toBeNull();
    expect(document.querySelector('.mermaid-container')).toBeNull();
  });

  // =========================================================================
  // onload: mermaid.run() success / failure paths
  // =========================================================================

  it('onload: after mermaid.run() resolves, fullscreen button click requests fullscreen on its container', async () => {
    document.body.innerHTML = '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>';
    window.mermaid = makeMermaidMock({ runResult: 'resolve' });
    runScript();

    getInjectedScript().onload();
    await flushMicrotasks();

    const container = document.querySelector('.mermaid-container');
    const requestFullscreen = vi.fn();
    container.requestFullscreen = requestFullscreen;

    container.querySelector('.mermaid-fullscreen-btn').click();
    expect(requestFullscreen).toHaveBeenCalledTimes(1);
  });

  it('onload: logs a non-critical warning (does not throw) when mermaid.run() rejects', async () => {
    document.body.innerHTML = '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>';
    window.mermaid = makeMermaidMock({ runResult: 'reject' });
    const warnSpy = vi.fn();
    console.warn = warnSpy;
    runScript();

    expect(() => getInjectedScript().onload()).not.toThrow();
    await flushMicrotasks();

    expect(warnSpy).toHaveBeenCalledWith(
      '[Mermaid] Rendering error (non-critical):',
      expect.any(Error)
    );
  });

  it('onload: catches initialize() errors so the page never breaks', () => {
    document.body.innerHTML = '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>';
    window.mermaid = {
      initialize: vi.fn(() => {
        throw new Error('bad config');
      }),
      run: vi.fn(() => Promise.resolve()),
    };
    const warnSpy = vi.fn();
    console.warn = warnSpy;
    runScript();

    expect(() => getInjectedScript().onload()).not.toThrow();
    expect(warnSpy).toHaveBeenCalledWith('[Mermaid] Initialization error:', expect.any(Error));
    // Conversion never ran because initialize() threw first.
    expect(document.querySelector('.mermaid-container')).toBeNull();
  });

  it('onerror: warns when the mermaid.js CDN script fails to load', () => {
    document.body.innerHTML = '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>';
    const warnSpy = vi.fn();
    console.warn = warnSpy;
    runScript();

    getInjectedScript().onerror();

    expect(warnSpy).toHaveBeenCalledWith('[Mermaid] Failed to load mermaid.js');
  });

  // =========================================================================
  // Static mermaid <img> alt-text enhancement
  // =========================================================================

  it('enhances a generic/missing alt on static mermaid images using the nearest preceding heading', () => {
    // Note: the whole script bails out on the top-level hasMermaid guard, so
    // alt-text enhancement only ever runs on pages that also have a live
    // mermaid code block elsewhere on the page.
    document.body.innerHTML =
      '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>' +
      '<h2>Deployment Flow</h2>' +
      '<img src="/assets/mermaid/deploy.svg" alt="Mermaid Diagram">';
    window.mermaid = makeMermaidMock();
    runScript();

    const img = document.querySelector('img');
    expect(img.alt).toBe('Deployment Flow diagram');
    expect(img.getAttribute('role')).toBe('img');
  });

  it('leaves a custom alt text untouched on static mermaid images (and does not set role)', () => {
    document.body.innerHTML =
      '<pre><code class="mermaid">graph TD; A--&gt;B;</code></pre>' +
      '<h2>Deployment Flow</h2>' +
      '<img src="/assets/mermaid/deploy.svg" alt="Custom author-provided description">';
    window.mermaid = makeMermaidMock();
    runScript();

    const img = document.querySelector('img');
    expect(img.alt).toBe('Custom author-provided description');
    expect(img.getAttribute('role')).toBeNull();
  });

  // =========================================================================
  // MutationObserver: re-render on data-theme change
  // =========================================================================

  it('re-initializes mermaid with the new theme and re-renders when data-theme changes (mermaid loaded)', async () => {
    document.body.innerHTML =
      '<div class="mermaid" data-processed="true" data-mermaid-source="graph TD; A--&gt;B;"></div>';
    const mermaidMock = makeMermaidMock();
    window.mermaid = mermaidMock;
    runScript();
    mermaidMock.initialize.mockClear();

    document.documentElement.setAttribute('data-theme', 'dark');
    await flushMicrotasks();

    expect(mermaidMock.initialize).toHaveBeenCalledWith(expect.objectContaining({ theme: 'dark' }));
    const el = document.querySelector('.mermaid');
    expect(el.hasAttribute('data-processed')).toBe(false);
    expect(el.textContent).toBe('graph TD; A-->B;');
    expect(mermaidMock.run).toHaveBeenCalled();
  });

  it('does nothing on data-theme change when mermaid has not loaded yet', async () => {
    document.body.innerHTML =
      '<div class="mermaid" data-processed="true" data-mermaid-source="graph TD; A--&gt;B;"></div>';
    runScript(); // no window.mermaid set

    expect(() => {
      document.documentElement.setAttribute('data-theme', 'dark');
    }).not.toThrow();
    await flushMicrotasks();

    // Guard `window.mermaid` was falsy — the processed marker is left alone.
    const el = document.querySelector('.mermaid');
    expect(el.hasAttribute('data-processed')).toBe(true);
  });
});
