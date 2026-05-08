# IIFE Layout-Thrash Audit

Follow-up to [PR #335](https://github.com/Twodragon0/tech-blog/pull/335) which fixed the same anti-pattern in `assets/js/home-posts-filter.js` (rAF-batched reads + single-pass writes).

**Date**: 2026-05-02
**Scope**: every `assets/js/*.js` script except already-refactored `home-posts-filter.js` and the dead-code `chat-widget*.js` (loaded only inside an iframe).
**Pattern hunted**: sequential geometry reads (`offsetWidth`, `offsetHeight`, `getBoundingClientRect`, `clientWidth`, `scrollHeight`, `getComputedStyle`, `innerWidth`, `offsetTop`, `offsetLeft`) interleaved with style writes (`element.style.X = ...`, `classList.add/remove/toggle`, `setAttribute`) inside a hot path (scroll, resize, input).

## Executive summary

| Severity | Count | Action |
|---|---|---|
| **P1** (fix this PR) | 1 | `toc.js#highlightCurrentSection` — read+write interleaved in `forEach` loop on every scroll frame |
| **P2** (review later) | 0 | none |
| **P3** (intentional / one-shot) | 4 | `archive-filter.js:78` (intentional reflow trigger), `main-core.js#anchorClick`, `toc.js#anchorClick`, `main-post.js#checkScrollable` |
| **No-fix** | 4 | `archive-filter.js#updateProgress`, `post-page.js#readingProgress`, `ad-optimizer.js#observer`, `main-search.js`, `chat-widget.js` (already correct or out of scope) |

The P1 fix is shipped in this same PR.

## Methodology

```
grep -rn 'offsetWidth\|offsetHeight\|getBoundingClientRect\|clientWidth\|clientHeight\|\
scrollHeight\|scrollWidth\|getComputedStyle\|innerWidth\|innerHeight\|offsetTop\|offsetLeft' \
assets/js/*.js
```

Each match was classified by:

1. **Frequency**: scroll/resize/input handlers = HIGH; click/init = LOW
2. **DOM-element count touched**: more elements = bigger reflow blast radius
3. **Pattern**: read-then-write batching = OK; read-write-read-write loop = THRASH

## Detailed findings

### P1 — `assets/js/toc.js#highlightCurrentSection` (FIXED in this PR)

**Hot path**: invoked from a scroll listener wrapped in `requestAnimationFrame` (lines 113–123). Runs every paint frame during scroll. On a typical post page, `tocItems` is 5–15 entries.

**Original shape** (lines 125–157):

```js
function highlightCurrentSection() {
  const scrollPosition = window.pageYOffset + 100;

  tocItems.forEach(item => {
    // ...resolve `section` from item href...

    if (section) {
      const sectionTop = section.offsetTop;        // READ (forces layout)
      const sectionBottom = sectionTop + section.offsetHeight; // READ

      if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
        tocItems.forEach(i => i.classList.remove('active')); // WRITE (invalidates layout)
        item.classList.add('active');                        // WRITE
      }
    }
  });
}
```

**Why this thrashes**: inside the outer `forEach`, every iteration's `section.offsetTop`/`offsetHeight` read happens after the *previous* iteration's `classList.remove/add` write may have invalidated layout. Even though `.active` only changes color/border in the current stylesheet, the browser still has to flush the pending style invalidations on the next geometry read. With 10 TOC items, that's potentially 10 forced synchronous layouts per scroll frame.

**Fix shape** (split into two passes):

```js
function highlightCurrentSection() {
  const scrollPosition = window.pageYOffset + 100;
  let activeIndex = -1;

  // PASS 1 (read-only): find which item is current.
  tocItems.forEach((item, idx) => {
    // ...resolve section...
    if (!section) return;
    const sectionTop = section.offsetTop;
    const sectionBottom = sectionTop + section.offsetHeight;
    if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
      activeIndex = idx; // last match wins (matches original behavior)
    }
  });

  // PASS 2 (write-only): toggle classList exactly once per item — but only
  // when something actually matched (preserves original "no-match = leave
  // existing state alone" behavior).
  if (activeIndex !== -1) {
    tocItems.forEach((item, idx) => {
      item.classList.toggle('active', idx === activeIndex);
    });
  }
}
```

**Behavioral preservation**:

- Original: highlight the *last* matching section if any match (later matches overwrite earlier matches via the inner `forEach(... remove)` + `add`). New code reproduces this: `activeIndex` keeps the last match.
- Original: if no match, no class changes (the inner loop never fires). New code preserves this: the PASS 2 loop is gated on `activeIndex !== -1`.

**Expected impact**: forced-synchronous-layouts during scroll drop from O(tocItems) → 0. On a 10-section post page, that's ~10 fewer reflows per paint frame. The Lighthouse "Avoid forced reflows" diagnostic should drop the toc.js attribution.

### P3 — Intentional reflow / one-shot (no action)

#### `archive-filter.js:78` — `void item.offsetWidth`

```js
item.classList.remove('is-filtering-in');
void item.offsetWidth;            // intentional — restart CSS animation
item.classList.add('is-filtering-in');
```

This is the canonical hack to restart a CSS animation. The forced reflow is *required* for the animation reset. Leave alone.

#### `main-core.js#anchorClick`, `toc.js#anchorClick`

Single read of `.site-header.offsetHeight` + single read of `.getBoundingClientRect()` only fires on `click`. Not a hot path. No batching needed.

#### `main-post.js#checkScrollable`

Debounced via `setTimeout(_, 100)` initial + `setTimeout(_, 200)` on resize. Runs at most a handful of times per page. Single read pair → single write. No batching needed.

### No-fix — already correct

#### `archive-filter.js#updateProgress`

```js
function updateProgress() {
  // 4 reads in a row...
  var rect = archivePage.getBoundingClientRect();
  var pageHeight = archivePage.offsetHeight;
  var viewportH = window.innerHeight;
  var scrolled = window.pageYOffset - rect.top - window.pageYOffset;
  // ...then one write at the end.
  progressBar.style.width = pct + '%';
}
```

All reads complete before the single write. Correct read-then-write pattern. No fix.

#### `post-page.js#readingProgress`

```js
requestAnimationFrame(function() {
  var article = document.querySelector('.post-article');
  var progressBar = document.getElementById('reading-progress');
  if (article && progressBar) {
    var articleTop = article.offsetTop;       // READ
    var articleHeight = article.offsetHeight; // READ
    var windowHeight = window.innerHeight;    // READ
    var scrollY = window.scrollY;             // READ
    // ...one write.
    progressBar.style.width = progress + '%';
  }
});
```

Same shape as `archive-filter.js#updateProgress`. Correct.

#### `ad-optimizer.js`

`offsetHeight` read only inside a `MutationObserver` callback waiting for an iframe to render — not a hot path, runs once per ad slot.

#### `main-search.js`

`window.innerWidth <= 768` check is a single property read for a mobile-vs-desktop branch. No layout-sensitive reads, no thrash.

#### `chat-widget.js`

Loaded only inside the chat-widget iframe (rendered on user-toggle). Out of scope for the main thread perf gate.

## Verification

This audit was generated from a static read of `assets/js/*.js` at HEAD. Re-run periodically (suggested: after any commit touching `assets/js/*.js` that adds an event listener or a `forEach` loop).

Quick re-run command:

```bash
grep -rn 'offsetWidth\|offsetHeight\|getBoundingClientRect\|clientWidth\|\
scrollHeight\|getComputedStyle\|offsetTop' assets/js/*.js
```

For each new match, classify by frequency × element-count × pattern, mirroring the table above.

## Related

- [PR #335](https://github.com/Twodragon0/tech-blog/pull/335) — the original `home-posts-filter.js` fix this audit follows up on
- [`docs/optimization/STYLE_LAYOUT_ANALYSIS.md`](./STYLE_LAYOUT_ANALYSIS.md) — original Style & Layout 1052 ms breakdown that motivated the PR-#335 work
- [`docs/optimization/LIGHTHOUSE_PERF_GATE.md`](./LIGHTHOUSE_PERF_GATE.md) — the LCP regression gate that protects these gains
