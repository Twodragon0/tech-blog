# Style & Layout Cost Audit — Homepage 1,052 ms

**Date**: 2026-04-30
**Branch**: `perf/style-layout-analysis`
**PageSpeed Insights signal**: Style & Layout 1,052 ms · Script Eval 1,374 ms · Rendering 450 ms (homepage)
**Method**: Static analysis of compiled CSS, Liquid templates, and homepage JavaScript. **No Chrome trace was captured** — savings figures are best-effort estimates.

---

## 1. Summary — Dominant Contributors (Ranked)

| # | Contributor | Where | Why It Hurts | Confidence |
|---|-------------|-------|--------------|------------|
| 1 | Synchronous DOM-write loop in `home-posts-filter.js` toggles `display` on every `.post-card` then queries the layout for tab counts | `assets/js/home-posts-filter.js:74-122` | 30 cards × 2 writes = 60 style invalidations; subsequent `.tab-count` insertion forces a second layout pass. Containment-free `.posts-list` means each toggle re-flows the whole grid. | High — code path runs unconditionally on first paint |
| 2 | `.post-card` and `.posts-list` have **no CSS containment** | `_sass/_components.scss:154-159` (`.posts-list`), `_sass/_components.scss:161-166` (`.post-card`) | The 30-card grid is the largest visible structure on the homepage. Without `contain: layout style;`, every JS-driven `display` toggle on a card invalidates the whole grid's layout. | High |
| 3 | Substring/suffix attribute selectors fired on every render of post pages: 27 `[src*=…]` / `[src$=".svg"]` / `[class*=…]` matchers | `_sass/_post.scss:48,209,905` and 24 more (`_sass/_base.scss:174,228` etc. for 3rd-party Google selectors) | Browsers test these against every matching element on every style recalc. With 30 `<img>` and 60 `<source>` on the homepage and ~50 images on a digest post, this multiplies style work. | Medium — magnitude depends on browser optimization |

These three are the primary suspects behind the 1,052 ms. Item 1 is a guaranteed forced reflow during first paint; items 2-3 amplify the cost of every recalc round.

---

## 2. Concrete Code References

### 2.1 Forced reflow on homepage first paint

**File**: `assets/js/home-posts-filter.js`

```javascript
// Lines 79-85: hides ALL cards then shows the first 12.
// This is two synchronous style writes per card; with 30 cards
// that's 60 writes that each invalidate sibling layout.
allCards.forEach(function (card) {
  card.style.display = 'none';
});

filtered.slice(0, showCount).forEach(function (card) {
  card.style.display = '';
});
```

Then at lines 111-122, the script appends `<span class="tab-count">…</span>` to each of the 7 tabs **after** the writes above, which forces an additional layout flush per tab insertion. The combined effect on a cold render is observable as Style & Layout cost — the script runs `defer`, but it still executes before `DOMContentLoaded` and before the user can interact.

### 2.2 Missing `contain` on the homepage post grid

**File**: `_sass/_components.scss`

```scss
// Line 154 — the homepage grid (3 columns, 30+ cards). No contain.
.posts-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

// Line 161 — each card; no contain.
.post-card {
  display: block;
  text-decoration: none;
  color: inherit;
  height: 100%;
}
```

Compare with `_sass/_post.scss` which has 22 separate `contain:` declarations on smaller post-internal containers — the homepage's largest visible structure was never updated.

### 2.3 Heavy attribute regex selectors

**File**: `_sass/_post.scss`

```scss
// Line 48
.post-article .post-content img[src*="section-"] { … }

// Line 209
.post-header .post-image img[src$=".svg"] { … }

// Line 905
.post-content img[src$=".svg"] { … }

// Line 781-783 — :has() inside attribute filter, table edition
.post-content .table-wrapper:has(table.table-fit)::before,
.post-content .table-wrapper:has(table.table-fit)::after { display: none; }
```

`scripts/dev/analyze_css_complexity.py` reports **27** attribute-regex selectors and **3** `:has()` selectors in `_site/assets/css/post-page.css`. These do not run on the homepage (post-page.css isn't loaded there), so they explain heavy Style & Layout cost on **post pages**, not the index. The homepage is held back by items 1-2.

### 2.4 nth-child clusters inside post tables

**File**: `_sass/_post.scss:787-792`

Six `:nth-child(2)` / `:nth-child(3)` / `:nth-child(4)` selectors on `table.table-risk-scorecard`, plus `_sass/_post.scss:649` and `_sass/_post.scss:465` for `tbody tr:nth-child(even)` zebra striping. Each one re-evaluates row indices on every reflow.

### 2.5 Forced reflow in archive-page filter (informational, not homepage)

**File**: `assets/js/archive-filter.js:78`

```javascript
// Force reflow to restart animation
void item.offsetWidth;
```

This is intentional and isolated to the archive page; the comment makes the intent explicit. Not a homepage issue but worth noting in future passes.

### 2.6 DOM size

| Page | Total elements | Max nesting | Top 3 tags |
|------|----------------|-------------|------------|
| `_site/index.html` | **872** | 12 | `<span>` × 175, `<div>` × 161, `<a>` × 62 |
| `_site/posts/2026/04/29/.../index.html` (digest) | **1,381** | 13 | `<span>` × 162, `<div>` × 142, `<strong>` × 117 |

Neither page exceeds PageSpeed's 1,500-node "excessive" threshold, but the digest post is close. The homepage's 872 nodes are reasonable; **DOM size is not the bottleneck**, the JS-driven reflow is.

---

## 3. Recommended Fixes — Effort × Impact

| Priority | Fix | Effort | Expected Impact | Risk |
|----------|-----|--------|------------------|------|
| **P0** | Add `contain: layout style;` to `.post-card` (and consider `.posts-list`) | 1 line | Eliminates layout-cascade across grid when JS toggles `display`. Estimate **−80 to −150 ms** Style & Layout on cold render. | Very low. Card layout is self-contained — fixed aspect-ratio image, no overflowing children. |
| **P1** | Refactor `home-posts-filter.js renderPosts()` to batch DOM writes inside a `requestAnimationFrame` and to compute tab counts **once** (not inside a per-tab loop) | 30 min | Removes the dual write pass and the redundant `getFilteredCards(sort)` per tab. Estimate **−100 to −200 ms** Style & Layout + similar Script Eval drop. | Low. Same observable behavior, only render order changes. Add a smoke test (cards visible on first paint). |
| **P1** | Hide all cards beyond index 12 server-side (Liquid `{% if forloop.index > 12 %}…hidden`) so JS doesn't have to flip `display` on the 12 already-visible cards | 15 min | Cuts the initial paint write count in half. Estimate **−40 to −80 ms**. | Low. SSR-friendly; no-JS users still see the first 12. |
| **P2** | Replace `[src$=".svg"]` / `[src*="section-"]` selectors in `_sass/_post.scss` with deterministic class hooks (`.is-section-image`, `.is-svg-image`) added at Liquid render time | 1 hr (markup + Liquid changes) | Removes 27 substring matchers from post-page.css. Estimate **−50 to −120 ms** on post page Style & Layout. | Medium. Requires touching include templates and verifying every image path still gets the right class. |
| **P2** | Add `contain: layout style;` to `.toc-container`, `.toc-grid`, `.news-card`, `.news-grid` | 4 lines | Containment hardening for non-homepage pages. Estimate **−20 to −60 ms** per affected page. | Very low. |
| **P3** | Move zebra striping (`tbody tr:nth-child(even)`) behind a `.zebra-striped` class on the table; only the few tables that actually need stripes pay the cost | 30 min | Removes 3 broad nth-child rules from the global path. Marginal Style recalc cost reduction (5-15 ms). | Low. Need to add `.zebra-striped` to each instance via Markdown attribute lists. |
| **P3** | Strip the universal `*` selector descendant rules in `_sass/_base.scss:174` (`[class*="VIpgJd"]`) and consolidate Google Translate CLS rules into a single class hook injected by `google-translate.js` | 1 hr | Drops two `*`-with-descendant matches and 5 attribute-substring selectors. Cost is dominated by the homepage's main.css (38 KB), so impact is small but cumulative with P0/P1. | Medium — Google's translate widget injects its own class names; the substring matcher exists because we don't control them. Risk of regression if their classes change. |

---

## 4. Estimated Savings Summary

| Bundle of fixes | Style & Layout savings (estimate) | Script Eval savings (estimate) | Total estimate |
|-----------------|-----------------------------------|--------------------------------|----------------|
| P0 only (this PR) | **80–150 ms** | 0 ms | 80–150 ms |
| P0 + P1 (next PR) | 200–350 ms | 80–150 ms | 280–500 ms |
| P0 + P1 + P2 (post-page focus) | 280–500 ms (homepage) plus 70–180 ms on post pages | 80–150 ms | 350–650 ms total per page class |

**Caveat**: All numbers are derived from CSS rule counts and write-count math, not from a Chrome trace. Lighthouse is sensitive to selector depth × DOM size; the savings could land anywhere in these bands depending on browser optimizations.

---

## 5. Out-of-Scope (Needs Browser Tracing to Confirm)

These items look suspicious during static analysis but require runtime profiling to triage correctly. Defer until a Chrome DevTools `Performance` trace is captured.

- **GA / gtag.js forced reflow** (133–143 ms in PSI). The site loads GA via `defer` and lazy-init; PSI's flag is on Google's side. Mitigations would target `consent-init` interaction, not our CSS.
- **`getComputedStyle` from third-party widgets** (Sentry, Cloudflare beacon). All loaded `defer` so they shouldn't be in the critical path, but they could still pile on during first paint. A trace will tell.
- **Subscribe-float, share-actions, giscus init**. These all `defer` and only attach listeners; static analysis shows no layout reads. A trace is needed if the homepage Style & Layout doesn't drop after P0/P1.
- **`@font-face` swap-in cost**. Self-hosted Noto woff2 is in place; the swap is `swap`. Shouldn't be a layout issue, but can show up as Style cost in older Chromium.
- **Google Translate widget CLS reservations** in `_sass/_base.scss:174-242`. The `[class*="VIpgJd"]` selector is unfortunate but exists because Google's class names are unstable. Replacing it is a P3 hardening exercise, not a quick win.

---

## 6. Validation Run

```text
$ python3 scripts/dev/analyze_css_complexity.py
# CSS Complexity Report — `_site/assets/css/main.css`
- Rules: 284
- Selectors (post-split): 319
- Longest selector (56 chars): `.posts-list--list-view .post-card:hover .post-card-inner`
- Longest descendant chain: 3 compound parts
- Average specificity (a, b, c): (0.01, 1.33, 0.20)
- :has() selectors: 1
- Attribute regex (substring/prefix/suffix): 5
- :nth-* selectors: 0

$ python3 scripts/dev/analyze_css_complexity.py --input _site/assets/css/post-page.css
- Rules: 731
- Selectors (post-split): 897
- :has() selectors: 3
- Attribute regex (substring/prefix/suffix): 27
- :nth-* selectors: 11

$ python3 scripts/dev/count_dom_nodes.py _site/index.html _site/posts/2026/04/29/.../index.html
- _site/index.html: 872 elements, max depth 12
- _site/posts/2026/04/29/.../index.html: 1,381 elements, max depth 13
```

---

## 7. References

- Chrome DevTools — [Avoid large, complex layouts and layout thrashing](https://developer.chrome.com/docs/lighthouse/performance/uses-text-compression/)
- CSS Containment Module Level 1 — [`contain` property](https://developer.mozilla.org/docs/Web/CSS/contain)
- Vladimir Agafonkin — [The cost of CSS selectors](https://csswizardry.com/2014/01/optimising-css-selectors-for-css-stats/)
- Lighthouse audits — [DOM size](https://web.dev/dom-size-and-interactivity/)
- This repo — `_sass/_post.scss:133` (existing `contain` patterns to mirror)
