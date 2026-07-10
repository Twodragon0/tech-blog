// Regression tests for assets/js/post-page.js
//
// post-page.js loads on every post via `_includes/footer.html`. It owns
// (a) heading-id generation on `.post-content` so kramdown-style anchors
// work, (b) reading-time estimation in `#reading-time` (hybrid Korean
// 500 chars/min + English 200 words/min), (c) external-link hardening
// with target="_blank" + rel="noopener noreferrer", (d) reading-progress
// bar, (e) Giscus mount observer, (f) image lightbox.
//
// Most behavior runs via `scheduleIdleWork()` which falls back to
// `setTimeout(callback, 0)` in jsdom. We use `vi.useFakeTimers()` +
// `vi.runOnlyPendingTimers()` to flush the deferred passes synchronously.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/post-page.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript(handlerSink) {
  const origAdd = document.addEventListener.bind(document);
  document.addEventListener = (evt, handler, opts) => {
    handlerSink.push({ evt, handler, opts });
    return origAdd(evt, handler, opts);
  };
  try {
    // eslint-disable-next-line no-new-func
    new Function('window', 'document', SCRIPT_SOURCE)(window, document);
    vi.runOnlyPendingTimers();
  } finally {
    document.addEventListener = origAdd;
  }
}

// The Giscus block registers `document.addEventListener('DOMContentLoaded', ...)`
// unconditionally (no readyState check), so in jsdom (readyState already
// 'complete' when the script runs) the event never fires on its own.
// Manually invoke the captured handler(s) to exercise that code path.
function fireDOMContentLoaded(handlerSink) {
  for (const r of handlerSink) {
    if (r.evt === 'DOMContentLoaded') r.handler();
  }
}

describe('post-page.js', () => {
  let documentHandlers;

  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = '';
    documentHandlers = [];
  });

  afterEach(() => {
    for (const r of documentHandlers) {
      document.removeEventListener(r.evt, r.handler, r.opts);
    }
    vi.useRealTimers();
    document.body.innerHTML = '';
  });

  // =========================================================================
  // generateHeadingIds — kramdown-compatible auto-id + heading-anchor link
  // =========================================================================

  it('heading IDs: adds slug ID to .post-content h2/h3 missing one', () => {
    document.body.innerHTML =
      '<article class="post-article">' +
      '<div class="post-content">' +
      '<h2>Hello World</h2>' +
      '<h3>Section Two</h3>' +
      '</div></article>';
    runScript(documentHandlers);

    const h2 = document.querySelector('h2');
    const h3 = document.querySelector('h3');
    expect(h2.id).toBe('hello-world');
    expect(h3.id).toBe('section-two');
  });

  it('heading IDs: preserves existing id (no overwrite)', () => {
    document.body.innerHTML =
      '<div class="post-content"><h2 id="custom-anchor">Hello</h2></div>';
    runScript(documentHandlers);
    expect(document.querySelector('h2').id).toBe('custom-anchor');
  });

  it('heading IDs: injects .heading-anchor with href="#id" inside the heading', () => {
    document.body.innerHTML =
      '<div class="post-content"><h2>안녕 세계</h2></div>';
    runScript(documentHandlers);

    const h2 = document.querySelector('h2');
    const anchor = h2.querySelector('a.heading-anchor');
    expect(anchor).not.toBeNull();
    // The anchor href encodes the (Korean-preserving) generated id.
    expect(anchor.getAttribute('href')).toBe('#' + h2.id);
    // ARIA label exists for screen readers.
    expect(anchor.getAttribute('aria-label')).toMatch(/Permalink/);
  });

  it('heading IDs: does nothing when .post-content is missing', () => {
    document.body.innerHTML = '<h2>Outside</h2>';
    expect(() => runScript(documentHandlers)).not.toThrow();
    expect(document.querySelector('h2').id).toBe('');
  });

  // =========================================================================
  // initReadingTime — hybrid Korean + English calculation
  // =========================================================================

  it('reading-time: hybrid Korean 500 chars/min + English 200 words/min populates #reading-time', () => {
    // 1000 Korean chars (= 2 min) + 400 English words (= 2 min) → ceil(4) = 4 min
    const koreanText = '가'.repeat(1000);
    const englishText = ('word '.repeat(400)).trim();
    document.body.innerHTML =
      '<div class="post-content"><p>' +
      koreanText +
      '</p><p>' +
      englishText +
      '</p></div>' +
      '<span id="reading-time"></span>';
    runScript(documentHandlers);

    const text = document.getElementById('reading-time').textContent;
    expect(text).toMatch(/^\d+ min read$/);
    // 1000/500 + 400/200 = 2 + 2 = 4
    expect(text).toBe('4 min read');
  });

  it('reading-time: minimum is 1 min even for empty content', () => {
    document.body.innerHTML =
      '<div class="post-content"></div><span id="reading-time"></span>';
    runScript(documentHandlers);
    expect(document.getElementById('reading-time').textContent).toBe('1 min read');
  });

  // =========================================================================
  // enhanceExternalLinks — security hardening for outbound links
  // =========================================================================

  it('external links: external https URL gets target=_blank + rel="noopener noreferrer"', () => {
    document.body.innerHTML =
      '<div class="post-content">' +
      '<a id="ext" href="https://external.example.com/x">External</a>' +
      '</div>' +
      '<span id="reading-time"></span>'; // initReadingTime needs to run for enhanceExternalLinks
    runScript(documentHandlers);

    const link = document.getElementById('ext');
    expect(link.getAttribute('target')).toBe('_blank');
    expect(link.getAttribute('rel')).toBe('noopener noreferrer');
    expect(link.classList.contains('external-link-processed')).toBe(true);
  });

  it('external links: skips fragment (#anchor) / mailto / tel / same-host links', () => {
    document.body.innerHTML =
      '<div class="post-content">' +
      '<a id="frag" href="#section">Anchor</a>' +
      '<a id="mail" href="mailto:foo@bar.com">Email</a>' +
      '<a id="tel" href="tel:+82-10-0000">Phone</a>' +
      `<a id="same" href="${window.location.origin}/posts/x">Same host</a>` +
      '</div>' +
      '<span id="reading-time"></span>';
    runScript(documentHandlers);

    for (const id of ['frag', 'mail', 'tel', 'same']) {
      const a = document.getElementById(id);
      expect(a.getAttribute('target'), `#${id} should have no target`).toBeNull();
      expect(a.classList.contains('external-link-processed')).toBe(false);
    }
  });

  it('external links: target=_blank internal link is processed but existing target/rel/aria-label/title are preserved', () => {
    document.body.innerHTML =
      '<div class="post-content">' +
      '<a id="nt" href="/internal" target="_blank" rel="preexisting" aria-label="keep" title="keep-title">Internal new tab</a>' +
      '</div>' +
      '<span id="reading-time"></span>';
    runScript(documentHandlers);
    const a = document.getElementById('nt');
    expect(a.getAttribute('rel')).toBe('preexisting');
    expect(a.getAttribute('aria-label')).toBe('keep');
    expect(a.getAttribute('title')).toBe('keep-title');
    expect(a.classList.contains('external-link-processed')).toBe(true);
  });

  it('external links: skips link with no href attribute and one already processed', () => {
    document.body.innerHTML =
      '<div class="post-content">' +
      '<a id="noHref">No href</a>' +
      '<a id="already" href="https://external.example.com/y" class="external-link-processed">Done</a>' +
      '</div>' +
      '<span id="reading-time"></span>';
    expect(() => runScript(documentHandlers)).not.toThrow();
    expect(document.getElementById('already').getAttribute('target')).toBeNull();
  });

  it('external links: does not throw when .post-content is missing entirely', () => {
    document.body.innerHTML = '<span id="reading-time"></span>';
    expect(() => runScript(documentHandlers)).not.toThrow();
  });

  // =========================================================================
  // generateId edge cases
  // =========================================================================

  it('heading IDs: symbol-only heading falls back to "heading", numeric-start gets prefixed', () => {
    document.body.innerHTML =
      '<div class="post-content"><h2>***</h2><h3>123 Title</h3></div>';
    runScript(documentHandlers);
    const [h2, h3] = document.querySelectorAll('.post-content h2, .post-content h3');
    expect(h2.id).toBe('heading');
    expect(h3.id).toBe('heading-123-title');
  });

  it('heading IDs: duplicate heading text gets a numeric suffix for uniqueness', () => {
    document.body.innerHTML =
      '<div class="post-content"><h2>Same</h2><h2>Same</h2></div>';
    runScript(documentHandlers);
    const headings = document.querySelectorAll('.post-content h2');
    expect(headings[0].id).toBe('same');
    expect(headings[1].id).toBe('same-1');
  });

  it('heading IDs: builds text from mixed text + inline element child nodes', () => {
    document.body.innerHTML =
      '<div class="post-content"><h2>Hello <code>World</code></h2></div>';
    runScript(documentHandlers);
    expect(document.querySelector('h2').id).toBe('hello-world');
  });

  it('heading IDs: falls back to heading.textContent when only a heading-anchor child exists, and skips re-inserting the anchor', () => {
    document.body.innerHTML =
      '<div class="post-content"><h2><a class="heading-anchor">X</a></h2></div>';
    runScript(documentHandlers);
    const h2 = document.querySelector('h2');
    expect(h2.id).toBe('x');
    expect(h2.querySelectorAll('.heading-anchor').length).toBe(1);
  });

  // =========================================================================
  // Reading progress bar (scroll, rAF-throttled)
  // =========================================================================

  it('reading progress: sets progressBar width on scroll when article + bar present', () => {
    const origRAF = window.requestAnimationFrame;
    window.requestAnimationFrame = (cb) => { cb(); return 0; };
    document.body.innerHTML =
      '<article class="post-article"><div class="post-content"></div></article>' +
      '<div id="reading-progress"></div>';
    runScript(documentHandlers);
    window.dispatchEvent(new Event('scroll'));
    const bar = document.getElementById('reading-progress');
    expect(bar.style.width).toMatch(/%$/);
    window.requestAnimationFrame = origRAF;
  });

  it('reading progress: scroll handler no-ops (no throw) when article/bar are missing', () => {
    const origRAF = window.requestAnimationFrame;
    window.requestAnimationFrame = (cb) => { cb(); return 0; };
    document.body.innerHTML = '<div class="post-content"></div>';
    runScript(documentHandlers);
    expect(() => window.dispatchEvent(new Event('scroll'))).not.toThrow();
    window.requestAnimationFrame = origRAF;
  });

  it('reading progress: ticking guard skips queuing a second rAF while one is pending', () => {
    let calls = 0;
    const origRAF = window.requestAnimationFrame;
    window.requestAnimationFrame = () => { calls++; return 0; };
    document.body.innerHTML =
      '<article class="post-article"><div class="post-content"></div></article>' +
      '<div id="reading-progress"></div>';
    runScript(documentHandlers);
    window.dispatchEvent(new Event('scroll'));
    window.dispatchEvent(new Event('scroll'));
    expect(calls).toBe(1);
    window.requestAnimationFrame = origRAF;
  });

  // =========================================================================
  // Giscus loading-state management
  // =========================================================================

  it('giscus: hides loading indicator when MutationObserver reports an iframe with contentDocument', () => {
    document.body.innerHTML =
      '<div id="giscus-container"></div><div id="giscus-loading"></div>';
    runScript(documentHandlers);
    fireDOMContentLoaded(documentHandlers);

    const container = document.getElementById('giscus-container');
    const loading = document.getElementById('giscus-loading');
    const iframe = document.createElement('iframe');
    Object.defineProperty(iframe, 'contentDocument', { value: {}, configurable: true });
    container.appendChild(iframe);
    // jsdom's MutationObserver fires callbacks via microtask; flush it.
    return Promise.resolve().then(() => {
      expect(loading.classList.contains('hidden')).toBe(true);
    });
  });

  it('giscus: auto-hides loading indicator after the 10s max-wait timeout', () => {
    document.body.innerHTML =
      '<div id="giscus-container"></div><div id="giscus-loading"></div>';
    runScript(documentHandlers);
    fireDOMContentLoaded(documentHandlers);
    vi.advanceTimersByTime(10000);
    expect(document.getElementById('giscus-loading').classList.contains('hidden')).toBe(true);
  });

  it('giscus: script load event hides loading indicator once an iframe appears', () => {
    document.body.innerHTML =
      '<div id="giscus-container"></div><div id="giscus-loading"></div>' +
      '<script src="https://giscus.app/client.js"></script>';
    runScript(documentHandlers);
    fireDOMContentLoaded(documentHandlers);
    const container = document.getElementById('giscus-container');
    container.appendChild(document.createElement('iframe'));
    const script = document.querySelector('script[src*="giscus.app"]');
    script.dispatchEvent(new Event('load'));
    vi.advanceTimersByTime(2000);
    expect(document.getElementById('giscus-loading').classList.contains('hidden')).toBe(true);
  });

  it('giscus: does nothing when container or loading element is missing', () => {
    document.body.innerHTML = '<div id="giscus-container"></div>';
    runScript(documentHandlers);
    expect(() => fireDOMContentLoaded(documentHandlers)).not.toThrow();
  });

  // =========================================================================
  // Image lightbox
  // =========================================================================

  function clickable(id, extra = '') {
    return `<img id="${id}" class="clickable-image" src="/assets/images/${id}.png" ${extra}>`;
  }

  it('lightbox: attachImageHandlers skips images already attached, wires click -> openLightbox on the rest', () => {
    document.body.innerHTML =
      clickable('a') + `<img id="b" class="clickable-image" data-lightbox-attached="true" src="/x.png">`;
    runScript(documentHandlers);
    const a = document.getElementById('a');
    const b = document.getElementById('b');
    expect(a.style.cursor).toBe('zoom-in');
    expect(b.style.cursor).toBe('');
    a.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    expect(document.getElementById('image-lightbox').classList.contains('active')).toBe(true);
  });

  it('lightbox: openLightbox uses data-full-src over src, decodes a Korean-encoded URI, and returns early with no src', () => {
    document.body.innerHTML =
      clickable('a', `data-full-src="${encodeURIComponent('/assets/images/한글.png')}"`) +
      `<img id="c" class="clickable-image">`;
    runScript(documentHandlers);
    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const lightboxImg = document.querySelector('.lightbox-image');
    // preload resolves async via Image mock in jsdom; just assert no throw and caption alt set.
    expect(document.getElementById('image-lightbox').classList.contains('active')).toBe(true);

    // no-src image: click should not throw and should not (re)activate a fresh open.
    document.getElementById('image-lightbox').classList.remove('active');
    expect(() =>
      document.getElementById('c').dispatchEvent(new MouseEvent('click', { bubbles: true }))
    ).not.toThrow();
    expect(document.getElementById('image-lightbox').classList.contains('active')).toBe(false);
  });

  it('lightbox: backdrop click closes only when the event target is the backdrop itself', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const lightbox = document.getElementById('image-lightbox');
    const backdrop = lightbox.querySelector('.lightbox-backdrop');
    const controls = lightbox.querySelector('.lightbox-controls');

    // Click bubbles up to lightboxContent's listener, but e.target is `controls`,
    // not lightboxContent/lightboxWrapper, so it must stay open.
    controls.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(lightbox.classList.contains('active')).toBe(true);

    backdrop.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(lightbox.classList.contains('active')).toBe(false);
  });

  it('lightbox: close button and lightboxContent self-click both close; wrapper click also closes', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    const lightbox = document.getElementById('image-lightbox');
    const content = lightbox.querySelector('.lightbox-content');
    const wrapper = lightbox.querySelector('.lightbox-image-wrapper');

    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    lightbox.querySelector('.lightbox-close').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(lightbox.classList.contains('active')).toBe(false);

    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    Object.defineProperty(content, 'target', { value: undefined });
    wrapper.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    // Wrapper click bubbles to lightboxContent listener; e.target === wrapper closes it.
    expect(lightbox.classList.contains('active')).toBe(false);
  });

  it('lightbox: closeLightbox timeout resets state only if still inactive after 350ms', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    const lightbox = document.getElementById('image-lightbox');
    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    lightbox.querySelector('.lightbox-close').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    vi.advanceTimersByTime(350);
    expect(lightbox.querySelector('.lightbox-image').getAttribute('src')).toBe('');
  });

  it('lightbox: zoom-in/out/reset buttons update transform; clamped zoom is a no-op past max', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const lightbox = document.getElementById('image-lightbox');
    const img = lightbox.querySelector('.lightbox-image');
    const zoomIn = lightbox.querySelector('.lightbox-zoom-in');
    const zoomOut = lightbox.querySelector('.lightbox-zoom-out');
    const reset = lightbox.querySelector('.lightbox-reset');

    for (let i = 0; i < 20; i++) {
      zoomIn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    }
    expect(img.classList.contains('zoomed')).toBe(true);
    // Past max (5), further zoom-in clicks are clamped no-ops (currentZoom === oldZoom branch).
    zoomIn.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    reset.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(img.classList.contains('zoomed')).toBe(false);

    for (let i = 0; i < 20; i++) {
      zoomOut.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    }
    expect(img.classList.contains('zoomed')).toBe(false);
  });

  it('lightbox: dblclick toggles between reset (when zoomed) and zoom-in (when not)', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const lightbox = document.getElementById('image-lightbox');
    const img = lightbox.querySelector('.lightbox-image');

    img.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
    expect(img.classList.contains('zoomed')).toBe(true);

    img.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
    expect(img.classList.contains('zoomed')).toBe(false);
  });

  it('lightbox: wheel zoom is ignored while inactive, applied while active (both scroll directions)', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    const lightbox = document.getElementById('image-lightbox');
    const wrapper = lightbox.querySelector('.lightbox-image-wrapper');
    const img = lightbox.querySelector('.lightbox-image');

    // Inactive: wheel should be a no-op (early return, no preventDefault side effect needed).
    expect(() =>
      wrapper.dispatchEvent(new WheelEvent('wheel', { deltaY: 100, cancelable: true }))
    ).not.toThrow();

    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    wrapper.dispatchEvent(new WheelEvent('wheel', { deltaY: -100, cancelable: true }));
    expect(img.style.transform).toContain('scale(1.15)');
    wrapper.dispatchEvent(new WheelEvent('wheel', { deltaY: 100, cancelable: true }));
    // Back near zoom 1 (floating point: 1.15 - 0.15 ~= 0.9999999999999999), no longer "zoomed".
    expect(img.classList.contains('zoomed')).toBe(false);
  });

  it('lightbox: mouse drag only engages past zoom>1, and mousemove/mouseup no-op without an active drag', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const lightbox = document.getElementById('image-lightbox');
    const img = lightbox.querySelector('.lightbox-image');
    const zoomIn = lightbox.querySelector('.lightbox-zoom-in');

    // At zoom 1: mousedown should not start a drag.
    img.dispatchEvent(new MouseEvent('mousedown', { clientX: 0, clientY: 0 }));
    document.dispatchEvent(new MouseEvent('mousemove', { clientX: 50, clientY: 50 }));
    expect(img.classList.contains('dragging')).toBe(false);

    zoomIn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    img.dispatchEvent(new MouseEvent('mousedown', { clientX: 0, clientY: 0 }));
    expect(img.classList.contains('dragging')).toBe(true);
    document.dispatchEvent(new MouseEvent('mousemove', { clientX: 30, clientY: 40 }));
    expect(img.style.transform).toContain('translate(');
    document.dispatchEvent(new MouseEvent('mouseup'));
    expect(img.classList.contains('dragging')).toBe(false);
  });

  it('lightbox: touchstart pinch (2 fingers) sets up zoom baseline; touchmove pinch scales; touchend settles', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const lightbox = document.getElementById('image-lightbox');
    const img = lightbox.querySelector('.lightbox-image');

    const twoTouch = (x1, x2) => ({
      touches: [{ clientX: x1, clientY: 0 }, { clientX: x2, clientY: 0 }],
    });
    img.dispatchEvent(new TouchEvent('touchstart', twoTouch(0, 10)));
    img.dispatchEvent(new TouchEvent('touchmove', twoTouch(0, 40)));
    expect(img.classList.contains('zoomed')).toBe(true);
    img.dispatchEvent(new TouchEvent('touchend', { touches: [] }));
  });

  it('lightbox: single-finger touch drags when zoomed, and touchend resets translate when zoom<=1', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const lightbox = document.getElementById('image-lightbox');
    const img = lightbox.querySelector('.lightbox-image');
    const zoomIn = lightbox.querySelector('.lightbox-zoom-in');
    zoomIn.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    img.dispatchEvent(new TouchEvent('touchstart', { touches: [{ clientX: 0, clientY: 0 }] }));
    img.dispatchEvent(new TouchEvent('touchmove', { touches: [{ clientX: 20, clientY: 10 }] }));
    expect(img.style.transform).toContain('translate(');

    // reset back to zoom 1 then touchend should zero out translate.
    lightbox.querySelector('.lightbox-reset').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    img.dispatchEvent(new TouchEvent('touchend', { touches: [] }));
  });

  it('lightbox: keydown is ignored while inactive; Escape/+/-/0 act while active; unmapped keys no-op', () => {
    document.body.innerHTML = clickable('a');
    runScript(documentHandlers);
    const lightbox = document.getElementById('image-lightbox');

    // Inactive: keydown should be ignored entirely.
    expect(() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))).not.toThrow();

    document.getElementById('a').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '+' }));
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '-' }));
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '0' }));
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab' })); // unmapped -> default no-op
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    expect(lightbox.classList.contains('active')).toBe(false);
  });
});
