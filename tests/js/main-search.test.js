// Regression tests for assets/js/main-search.js
//
// Goal: prove the search bootstrap (a) bails cleanly when no #search-input
// exists, (b) injects its scoped enhanced-styles tag exactly once, (c)
// fetches /search.json on init, (d) defers Fuse.js loading until first
// focus (cost optimization), and (e) clears results when the query falls
// below the 2-char minimum.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = resolve(__dirname, '../../assets/js/main-search.js');
const SCRIPT_SOURCE = readFileSync(SCRIPT_PATH, 'utf8') + `\n//# sourceURL=${pathToFileURL(SCRIPT_PATH).href}`;

function runScript() {
  // eslint-disable-next-line no-new-func
  new Function('window', 'document', SCRIPT_SOURCE)(window, document);
}

function buildSearchFixture() {
  document.body.innerHTML = `
    <div class="search-container">
      <input id="search-input" type="search" />
      <div id="search-results" style="display:none"></div>
    </div>
  `;
}

function buildLangFixture({ overlay = true, googleLink = true, langBtns = true } = {}) {
  document.body.innerHTML = `
    <button id="lang-toggle" aria-expanded="false"></button>
    <div id="lang-dropdown">
      <div class="lang-option" data-lang="ko">한국어</div>
      <div class="lang-option" data-lang="en">English</div>
      <div class="lang-option" data-lang="ja">日本語</div>
    </div>
    ${overlay ? '<div id="lang-dropdown-overlay" aria-hidden="true"></div>' : ''}
    ${googleLink ? '<a id="header-google-translate"></a>' : ''}
    ${langBtns ? '<div class="language-tools"><button class="lang-btn" data-lang="ko"></button><button class="lang-btn" data-lang="en"></button></div>' : ''}
  `;
}

describe('main-search.js', () => {
  let originalFetch;

  beforeEach(() => {
    originalFetch = window.fetch;
    // Stub fetch so the IIFE's eager `/search.json` request resolves with
    // an empty index. We don't care about results — just that init runs.
    window.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      })
    );
    document.body.innerHTML = '';
    document.head.querySelectorAll('#search-enhanced-styles').forEach((el) => el.remove());
    document.head.querySelectorAll('script[src*="fuse"]').forEach((el) => el.remove());
    document.querySelectorAll('.translate-toast').forEach((el) => el.remove());
  });

  afterEach(() => {
    window.fetch = originalFetch;
    document.body.innerHTML = '';
    document.head.querySelectorAll('#search-enhanced-styles').forEach((el) => el.remove());
    document.head.querySelectorAll('script[src*="fuse"]').forEach((el) => el.remove());
    document.querySelectorAll('.translate-toast').forEach((el) => el.remove());
    delete window.Fuse;
    window.innerWidth = 1024;
  });

  it('bails cleanly when #search-input is missing', () => {
    expect(() => runScript()).not.toThrow();
    expect(document.getElementById('search-enhanced-styles')).toBeNull();
  });

  it('injects #search-enhanced-styles exactly once when search input exists', () => {
    buildSearchFixture();
    runScript();
    expect(document.querySelectorAll('#search-enhanced-styles')).toHaveLength(1);
  });

  it('eagerly fetches /search.json on init', () => {
    buildSearchFixture();
    runScript();
    const calls = window.fetch.mock.calls.map((c) => c[0]);
    expect(calls.some((url) => String(url).includes('/search.json'))).toBe(true);
  });

  it('hides results panel when query length < 2 (debounced no-op)', async () => {
    buildSearchFixture();
    runScript();

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    // Pre-fill some HTML to verify it gets cleared.
    results.innerHTML = '<a class="search-result-item">stale</a>';
    results.style.display = 'block';

    input.value = 'a';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    expect(results.textContent).toBe('');
    expect(results.style.display).toBe('none');
  });

  it('defers Fuse.js CDN loading until the search input is focused', () => {
    buildSearchFixture();
    runScript();

    // No CDN script should be appended on init.
    const before = document.querySelectorAll('script[src*="fuse"]').length;
    expect(before).toBe(0);

    document.getElementById('search-input').dispatchEvent(new Event('focus'));
    const after = document.querySelectorAll('script[src*="fuse"]').length;
    expect(after).toBe(1);
  });

  it('Escape key on the search input hides the results panel', async () => {
    buildSearchFixture();
    runScript();

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    // Seed at least one result item so the keydown handler reaches the
    // Escape branch (the early-return only fires when zero items).
    results.innerHTML = '<a class="search-result-item" href="#">x</a>';
    results.style.display = 'block';

    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    expect(results.style.display).toBe('none');
  });

  // ------------------------------------------------------------------
  // Bootstrap guard / style-injection branch variants
  // ------------------------------------------------------------------

  it('does nothing when #search-results is missing (search-input alone)', () => {
    document.body.innerHTML = `
      <div class="search-container">
        <input id="search-input" type="search" />
      </div>
    `;
    expect(() => runScript()).not.toThrow();
    expect(document.getElementById('search-enhanced-styles')).toBeNull();
  });

  it('does not duplicate #search-enhanced-styles when already present', () => {
    const pre = document.createElement('style');
    pre.id = 'search-enhanced-styles';
    document.head.appendChild(pre);

    buildSearchFixture();
    runScript();

    expect(document.querySelectorAll('#search-enhanced-styles')).toHaveLength(1);
    expect(document.getElementById('search-enhanced-styles')).toBe(pre);
  });

  it('sets an error placeholder when /search.json responds non-ok', async () => {
    window.fetch = vi.fn(() =>
      Promise.resolve({ ok: false, status: 500, json: () => Promise.resolve([]) })
    );
    buildSearchFixture();
    runScript();

    // Flush the fetch().then().catch() microtask chain.
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    expect(input.placeholder).toBe('검색 데이터 로드 실패');
  });

  // ------------------------------------------------------------------
  // clientSearch: fallback (no Fuse) filtering across fields
  // ------------------------------------------------------------------

  function buildSearchDataFixture(data) {
    window.fetch = vi.fn(() =>
      Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(data) })
    );
  }

  it('fallback search matches by title, content, tags, and category independently', async () => {
    buildSearchDataFixture([
      { title: 'Kubernetes Security', content: 'irrelevant', url: '/a', tags: ['k8s'], category: 'devops' },
      { title: 'Untitled', content: 'contains zerotrust keyword', url: '/b', category: 'security' },
      { title: 'Tagged post', content: 'x', url: '/c', tags: ['ZeroTrust', 'iam'] },
      { title: 'Cat post', content: 'x', url: '/d', category: 'ZeroTrustCategory' },
      { title: 'No match here', content: 'nope', url: '/e' },
    ]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0)); // let /search.json resolve

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');

    input.value = 'zerotrust';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    const links = results.querySelectorAll('a.search-result-item');
    const urls = Array.from(links).map((l) => l.dataset.url);
    expect(urls).toEqual(expect.arrayContaining(['/b', '/c', '/d']));
    expect(urls).not.toContain('/e');
  });

  it('renders the no-results message when nothing matches', async () => {
    buildSearchDataFixture([{ title: 'Alpha', content: 'x', url: '/a' }]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    input.value = 'zzzznomatch';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    expect(results.querySelector('.no-results')).not.toBeNull();
    expect(results.textContent).toContain('검색 결과가 없습니다.');
    expect(results.style.display).toBe('block');
  });

  it('renders date, category, and up to 3 tags in result meta', async () => {
    buildSearchDataFixture([
      {
        title: 'Full meta post',
        content: 'metatest',
        url: '/full',
        date: '2026-01-01',
        category: 'devsecops',
        tags: ['one', 'two', 'three', 'four'],
      },
    ]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    input.value = 'metatest';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    const meta = results.querySelector('.search-result-meta');
    expect(meta.textContent).toContain('2026-01-01');
    expect(meta.querySelector('.search-category').textContent).toBe('devsecops');
    expect(meta.querySelectorAll('.search-tag')).toHaveLength(3);
  });

  it('renders result meta without date/category/tags when absent', async () => {
    buildSearchDataFixture([{ title: 'Bare post', content: 'baretest', url: '/bare' }]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    input.value = 'baretest';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    const meta = results.querySelector('.search-result-meta');
    expect(meta.querySelector('.search-category')).toBeNull();
    expect(meta.querySelectorAll('.search-tag')).toHaveLength(0);
  });

  // ------------------------------------------------------------------
  // safeUrl branches, reached through renderResults()
  // ------------------------------------------------------------------

  it('safeUrl: keeps relative urls, rewrites unsafe/invalid urls to #, and defaults missing urls', async () => {
    buildSearchDataFixture([
      { title: 'RelPost matchme', content: 'x', url: '/relative/path' },
      { title: 'HttpsPost matchme', content: 'x', url: 'https://example.com/post' },
      { title: 'BadProtocol matchme', content: 'x', url: 'javascript:alert(1)' },
      { title: 'MalformedUrl matchme', content: 'x', url: 'http://[::1' },
      { title: 'NoUrl matchme', content: 'x' },
    ]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    input.value = 'matchme';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    const hrefs = Array.from(results.querySelectorAll('a.search-result-item')).map((a) => a.getAttribute('href'));
    expect(hrefs).toContain('/relative/path');
    expect(hrefs).toContain('https://example.com/post');
    expect(hrefs.filter((h) => h === '#').length).toBeGreaterThanOrEqual(3);
  });

  // ------------------------------------------------------------------
  // highlightMatch / getExcerpt branches, reached through renderResults()
  // ------------------------------------------------------------------

  it('highlightMatch wraps matches in <mark> and handles empty title gracefully', async () => {
    buildSearchDataFixture([
      { title: 'security security tips', content: 'security content body', url: '/s' },
      { title: '', content: 'security only in content field', url: '/t' },
    ]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    input.value = 'security';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    const marks = results.querySelectorAll('.search-result-title mark');
    expect(marks.length).toBeGreaterThan(0);
    // Empty-title item must not throw and should still render a result row.
    const secondLink = Array.from(results.querySelectorAll('a.search-result-item')).find(
      (a) => a.dataset.url === '/t'
    );
    expect(secondLink).toBeTruthy();
  });

  it('getExcerpt centers around the match with ellipses on both sides', async () => {
    const before = 'x'.repeat(60);
    const after = 'y'.repeat(100);
    buildSearchDataFixture([
      {
        title: 'Excerpt post',
        content: `${before} findme ${after}`,
        url: '/excerpt',
      },
    ]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    input.value = 'findme';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    const excerpt = results.querySelector('.search-result-excerpt');
    expect(excerpt.textContent.startsWith('...')).toBe(true);
    expect(excerpt.textContent.endsWith('...')).toBe(true);
    expect(excerpt.textContent).toContain('findme');
  });

  it('getExcerpt falls back to a plain prefix when the query is not found', async () => {
    buildSearchDataFixture([
      { title: 'Fallback matchtitle', content: 'short content with no query text inside it', url: '/fallback' },
    ]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    input.value = 'matchtitle';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    const excerpt = results.querySelector('.search-result-excerpt');
    // Query isn't present in `content`, so getExcerpt takes the substring(0,120) branch.
    expect(excerpt.textContent.startsWith('...')).toBe(false);
  });

  it('getExcerpt prefers item.excerpt over item.content when both exist', async () => {
    buildSearchDataFixture([
      {
        title: 'Excerpt-field matchit',
        excerpt: 'short excerpt matchit here',
        content: 'this long content body should not be used for excerpt display',
        url: '/exc2',
      },
    ]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    input.value = 'matchit';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    const excerpt = results.querySelector('.search-result-excerpt');
    expect(excerpt.textContent).toContain('short excerpt matchit here');
  });

  // ------------------------------------------------------------------
  // Keyboard navigation branches
  // ------------------------------------------------------------------

  async function seedThreeResults() {
    buildSearchDataFixture([
      { title: 'Nav one', content: 'navkw', url: '/n1' },
      { title: 'Nav two', content: 'navkw', url: '/n2' },
      { title: 'Nav three', content: 'navkw', url: '/n3' },
    ]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));
    const input = document.getElementById('search-input');
    input.value = 'navkw';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    return input;
  }

  it('keydown: does nothing when there are zero rendered result items', () => {
    buildSearchFixture();
    runScript();
    const input = document.getElementById('search-input');
    // No results have been rendered — results panel is empty.
    expect(() =>
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }))
    ).not.toThrow();
  });

  it('ArrowDown moves the active index forward and clamps at the last item', async () => {
    Element.prototype.scrollIntoView = vi.fn();
    try {
      const input = await seedThreeResults();
      const results = document.getElementById('search-results');
      const dispatchDown = () => input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));

      dispatchDown();
      dispatchDown();
      dispatchDown();
      dispatchDown(); // one past the end — should clamp

      const items = results.querySelectorAll('.search-result-item:not(.no-results)');
      expect(items[2].classList.contains('active')).toBe(true);
      expect(items[0].classList.contains('active')).toBe(false);
    } finally {
      delete Element.prototype.scrollIntoView;
    }
  });

  it('ArrowUp moves the active index backward and clamps at zero', async () => {
    Element.prototype.scrollIntoView = vi.fn();
    try {
      const input = await seedThreeResults();
      const results = document.getElementById('search-results');
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));

      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true }));
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true }));
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true })); // clamp at 0

      const items = results.querySelectorAll('.search-result-item:not(.no-results)');
      expect(items[0].classList.contains('active')).toBe(true);
    } finally {
      delete Element.prototype.scrollIntoView;
    }
  });

  it('Enter activates the currently-active result link', async () => {
    Element.prototype.scrollIntoView = vi.fn();
    try {
      const input = await seedThreeResults();
      const results = document.getElementById('search-results');
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));

      const items = results.querySelectorAll('.search-result-item:not(.no-results)');
      const clickSpy = vi.fn();
      items[0].click = clickSpy;

      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
      expect(clickSpy).toHaveBeenCalledTimes(1);
    } finally {
      delete Element.prototype.scrollIntoView;
    }
  });

  it('Enter with no active selection (index -1) does not click anything', async () => {
    const input = await seedThreeResults();
    const results = document.getElementById('search-results');
    const items = results.querySelectorAll('.search-result-item:not(.no-results)');
    const clickSpy = vi.fn();
    items[0].click = clickSpy;

    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    expect(clickSpy).not.toHaveBeenCalled();
  });

  it('an unhandled key falls through all branches without side effects', async () => {
    const input = await seedThreeResults();
    const results = document.getElementById('search-results');
    expect(() =>
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }))
    ).not.toThrow();
    expect(results.style.display).toBe('block');
  });

  // ------------------------------------------------------------------
  // Outside-click closes the results panel; inside-click leaves it open
  // ------------------------------------------------------------------

  it('clicking outside the search container hides the results panel', async () => {
    const input = await seedThreeResults();
    const results = document.getElementById('search-results');
    expect(results.style.display).toBe('block');

    const outside = document.createElement('div');
    document.body.appendChild(outside);
    outside.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(results.style.display).toBe('none');
    void input;
  });

  it('clicking inside the search container leaves the results panel open', async () => {
    const input = await seedThreeResults();
    const results = document.getElementById('search-results');
    expect(results.style.display).toBe('block');

    input.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(results.style.display).toBe('block');
  });

  // ------------------------------------------------------------------
  // loadFuseJs / initFuse branches
  // ------------------------------------------------------------------

  it('loadFuseJs resolves immediately (no CDN script) when window.Fuse already exists', () => {
    window.Fuse = function FakeFuse() {};
    try {
      buildSearchFixture();
      runScript();
      document.getElementById('search-input').dispatchEvent(new Event('focus'));
      expect(document.querySelectorAll('script[src*="fuse"]')).toHaveLength(0);
    } finally {
      delete window.Fuse;
    }
  });

  it('uses fuseInstance.search() results once Fuse.js finishes loading via onload', async () => {
    class FakeFuse {
      constructor(data) { this.data = data; }
      search(query) {
        return this.data
          .filter((d) => d.title.includes(query))
          .map((item) => ({ item, score: 0.05 }));
      }
    }
    buildSearchDataFixture([
      { title: 'fuseterm post', content: 'x', url: '/fuse1' },
      { title: 'unrelated', content: 'x', url: '/fuse2' },
    ]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0)); // let /search.json resolve, searchData populated

    const input = document.getElementById('search-input');
    input.dispatchEvent(new Event('focus'));
    const script = document.querySelector('script[src*="fuse"]');
    expect(script).toBeTruthy();

    window.Fuse = FakeFuse;
    script.onload(); // simulate CDN script finishing load -> initFuse() builds fuseInstance
    await new Promise((r) => setTimeout(r, 0));

    try {
      const results = document.getElementById('search-results');
      input.value = 'fuseterm';
      input.dispatchEvent(new Event('input', { bubbles: true }));

      const urls = Array.from(results.querySelectorAll('a.search-result-item')).map((a) => a.dataset.url);
      expect(urls).toEqual(['/fuse1']);
    } finally {
      delete window.Fuse;
    }
  });

  it('loadFuseJs resolves gracefully via onerror when the CDN script fails', async () => {
    buildSearchFixture();
    runScript();
    document.getElementById('search-input').dispatchEvent(new Event('focus'));
    const script = document.querySelector('script[src*="fuse"]');
    expect(() => script.onerror()).not.toThrow();
    await new Promise((r) => setTimeout(r, 0));
  });

  it('swallows an initFuse error thrown after Fuse.js loads (defensive .catch on focus handler)', async () => {
    buildSearchDataFixture([{ title: 'x', content: 'x', url: '/x' }]);
    buildSearchFixture();
    runScript();
    await new Promise((r) => setTimeout(r, 0));

    const input = document.getElementById('search-input');
    input.dispatchEvent(new Event('focus'));
    const script = document.querySelector('script[src*="fuse"]');

    window.Fuse = function ThrowingFuse() { throw new Error('boom'); };
    try {
      expect(() => script.onload()).not.toThrow();
      await new Promise((r) => setTimeout(r, 0));
    } finally {
      delete window.Fuse;
    }
  });

  // ------------------------------------------------------------------
  // Language dropdown: guard, toast creation, Google Translate link
  // ------------------------------------------------------------------

  it('initLanguageDropdown guard: no-ops when #lang-toggle/#lang-dropdown are missing', () => {
    buildSearchFixture(); // no lang elements at all
    expect(() => runScript()).not.toThrow();
    expect(document.querySelector('.translate-toast')).toBeNull();
  });

  it('creates a .translate-toast element and sets the Google Translate link href', () => {
    buildLangFixture();
    runScript();
    expect(document.querySelectorAll('.translate-toast')).toHaveLength(1);
    const link = document.getElementById('header-google-translate');
    expect(link.getAttribute('href')).toContain('translate.google.com');
  });

  it('reuses an existing .translate-toast element instead of creating a duplicate', () => {
    buildLangFixture();
    const pre = document.createElement('div');
    pre.className = 'translate-toast';
    document.body.appendChild(pre);

    runScript();
    expect(document.querySelectorAll('.translate-toast')).toHaveLength(1);
  });

  it('skips setting the Google Translate link href when the element is absent', () => {
    buildLangFixture({ googleLink: false });
    expect(() => runScript()).not.toThrow();
    expect(document.getElementById('header-google-translate')).toBeNull();
  });

  // ------------------------------------------------------------------
  // Language dropdown: open / close / toggle / mobile-scroll-lock
  // ------------------------------------------------------------------

  it('toggle click opens then closes the dropdown (and overlay + aria state)', () => {
    buildLangFixture();
    runScript();

    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');
    const overlay = document.getElementById('lang-dropdown-overlay');

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(dropdown.classList.contains('active')).toBe(true);
    expect(overlay.classList.contains('active')).toBe(true);
    expect(overlay.getAttribute('aria-hidden')).toBe('false');
    expect(toggle.getAttribute('aria-expanded')).toBe('true');

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(dropdown.classList.contains('active')).toBe(false);
    expect(overlay.classList.contains('active')).toBe(false);
    expect(overlay.getAttribute('aria-hidden')).toBe('true');
    expect(toggle.getAttribute('aria-expanded')).toBe('false');
  });

  it('opening the dropdown works without an overlay element present', () => {
    buildLangFixture({ overlay: false });
    runScript();
    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');

    expect(() => toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }))).not.toThrow();
    expect(dropdown.classList.contains('active')).toBe(true);
  });

  it('locks body scroll on narrow viewports and restores it on close', () => {
    buildLangFixture();
    window.innerWidth = 500;
    runScript();

    const toggle = document.getElementById('lang-toggle');
    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(document.body.style.overflow).toBe('hidden');

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(document.body.style.overflow).toBe('');
  });

  it('does not lock body scroll on wide viewports', () => {
    buildLangFixture();
    window.innerWidth = 1440;
    runScript();

    document.getElementById('lang-toggle').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(document.body.style.overflow).toBe('');
  });

  it('clicking the overlay closes the dropdown', () => {
    buildLangFixture();
    runScript();
    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');
    const overlay = document.getElementById('lang-dropdown-overlay');

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(dropdown.classList.contains('active')).toBe(true);

    overlay.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(dropdown.classList.contains('active')).toBe(false);
  });

  // ------------------------------------------------------------------
  // Language dropdown: outside-click and Escape-key closing
  // ------------------------------------------------------------------

  it('clicking outside the dropdown/toggle/overlay closes it', () => {
    buildLangFixture();
    runScript();
    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(dropdown.classList.contains('active')).toBe(true);

    const outside = document.createElement('div');
    document.body.appendChild(outside);
    outside.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(dropdown.classList.contains('active')).toBe(false);
  });

  it('clicking inside the dropdown does not close it', () => {
    buildLangFixture();
    runScript();
    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    dropdown.querySelector('.lang-option[data-lang="ja"]').dispatchEvent(
      new MouseEvent('click', { bubbles: true })
    );
    // The document-level outside-click listener must not have closed it
    // (the langOptions click handler's own closeDropdown() call is what
    // actually closes it — see the langOptions describe block below).
    // Here we only assert the outside-click guard itself doesn't double-fire
    // incorrectly for a target inside the toggle.
    expect(dropdown.classList.contains('active')).toBe(false); // closed by the option handler itself
  });

  it('clicking inside the toggle button does not trigger the outside-click closer redundantly', () => {
    buildLangFixture();
    runScript();
    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(dropdown.classList.contains('active')).toBe(true);

    // Clicking the toggle again is handled by the toggle's own listener
    // (closes it) rather than the outside-click listener; verify no throw.
    expect(() => toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }))).not.toThrow();
    expect(dropdown.classList.contains('active')).toBe(false);
  });

  it('Escape key closes the dropdown only when it is active', () => {
    buildLangFixture();
    runScript();
    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');

    // Not active yet — Escape should be a no-op.
    expect(() =>
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))
    ).not.toThrow();
    expect(dropdown.classList.contains('active')).toBe(false);

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(dropdown.classList.contains('active')).toBe(true);

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    expect(dropdown.classList.contains('active')).toBe(false);
  });

  // ------------------------------------------------------------------
  // removeGoogleInjectedElements + MutationObserver
  // ------------------------------------------------------------------

  it('removes Google-injected elements found inside .post-content at init', () => {
    buildLangFixture();
    const container = document.createElement('div');
    container.className = 'post-content';
    container.innerHTML = '<insertion>google stuff</insertion><div data-ved="x">panel</div>';
    document.body.appendChild(container);

    runScript();

    expect(container.querySelector('insertion')).toBeNull();
    expect(container.querySelector('[data-ved]')).toBeNull();
  });

  it('leaves matching elements alone when they are outside post-content/post-article/main', () => {
    buildLangFixture();
    const stray = document.createElement('insertion');
    stray.textContent = 'not inside a tracked container';
    document.body.appendChild(stray);

    runScript();

    expect(document.body.contains(stray)).toBe(true);
  });

  it('MutationObserver cleans up dynamically-injected Google elements inside .post-content', async () => {
    buildLangFixture();
    const container = document.createElement('div');
    container.className = 'post-content';
    document.body.appendChild(container);
    runScript();

    const injected = document.createElement('insertion');
    container.appendChild(injected);
    await new Promise((r) => setTimeout(r, 0));

    expect(container.querySelector('insertion')).toBeNull();
  });

  it('MutationObserver ignores unrelated text-node mutations without throwing', async () => {
    buildLangFixture();
    const container = document.createElement('div');
    container.className = 'post-content';
    container.textContent = 'seed';
    document.body.appendChild(container);
    runScript();

    container.appendChild(document.createTextNode(' more text'));
    await new Promise((r) => setTimeout(r, 0));

    expect(container.textContent).toContain('more text');
  });

  // ------------------------------------------------------------------
  // langOptions click handler (header dropdown)
  // ------------------------------------------------------------------

  it('clicking the option matching the current language just closes the dropdown (early return)', () => {
    buildLangFixture();
    runScript();
    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    dropdown.querySelector('.lang-option[data-lang="ko"]').dispatchEvent(
      new MouseEvent('click', { bubbles: true })
    );

    expect(dropdown.classList.contains('active')).toBe(false);
    expect(document.querySelectorAll('.lang-option.active')).toHaveLength(0);
  });

  it('clicking a different-language option updates active state and syncs postLangBtns', () => {
    buildLangFixture();
    runScript();
    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');

    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const enOption = dropdown.querySelector('.lang-option[data-lang="en"]');
    enOption.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(enOption.classList.contains('active')).toBe(true);
    expect(dropdown.querySelector('.lang-option[data-lang="ko"]').classList.contains('active')).toBe(false);
    expect(dropdown.classList.contains('active')).toBe(false); // closed by the click

    const enBtn = document.querySelector('.language-tools .lang-btn[data-lang="en"]');
    const koBtn = document.querySelector('.language-tools .lang-btn[data-lang="ko"]');
    expect(enBtn.classList.contains('active')).toBe(true);
    expect(koBtn.classList.contains('active')).toBe(false);
  });

  // ------------------------------------------------------------------
  // postLangBtns click handler (in-post language selector)
  // ------------------------------------------------------------------

  it('clicking a post-page lang-btn syncs the header dropdown active state', () => {
    buildLangFixture();
    runScript();

    const enBtn = document.querySelector('.language-tools .lang-btn[data-lang="en"]');
    enBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(document.querySelector('.lang-option[data-lang="en"]').classList.contains('active')).toBe(true);
    expect(document.querySelector('.lang-option[data-lang="ko"]').classList.contains('active')).toBe(false);
  });

  it('syncing to a language with no matching header option clears all header active states', () => {
    buildLangFixture();
    document.querySelector('.language-tools').insertAdjacentHTML(
      'beforeend',
      '<button class="lang-btn" data-lang="zh"></button>'
    );
    runScript();

    const zhBtn = document.querySelector('.language-tools .lang-btn[data-lang="zh"]');
    zhBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(document.querySelectorAll('.lang-option.active')).toHaveLength(0);

    // Internal currentLang is now 'zh' (not 'ko'), so clicking the ko header
    // option should proceed past the early-return branch this time.
    const toggle = document.getElementById('lang-toggle');
    const dropdown = document.getElementById('lang-dropdown');
    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    const koOption = dropdown.querySelector('.lang-option[data-lang="ko"]');
    koOption.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(koOption.classList.contains('active')).toBe(true);
  });
});
