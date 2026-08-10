# Noto Sans KR Self-Host Runbook

Operational guide for the self-hosted, two-tier Noto Sans KR woff2 subset that ships with this site (landed in PR #323).

## 1. Overview

The site self-hosts Noto Sans KR as two woff2 tiers per weight (400, 700) instead of fetching from Google Fonts. The motivation is twofold:

- PageSpeed flagged 45 KiB of unused CSS rules from the Google Fonts dynamic stylesheet on every page load.
- Removing the Google Fonts network dependency eliminates third-party DNS, TLS, and request waterfall before first paint, plus the GDPR/privacy exposure of font fetches to `fonts.googleapis.com` and `fonts.gstatic.com`.

The tradeoff with self-hosting Noto Sans KR is the full Hangul Syllables block (U+AC00–U+D7A3, 11,172 glyphs) compressing to ~545 KB per weight in woff2 — too heavy to preload eagerly. The two-tier strategy resolves this:

- **Tier 1 (eager, preloaded)**: Latin Basic + Latin-1 Supplement + Hangul Jamo + CJK punctuation + **every** Hangul syllable that appears anywhere in the corpus. Targets ≤230 KB per weight. Preloaded via `<link rel="preload">` so first paint has the font ready.
- **Tier 2 (on-demand safety net)**: The Hangul tail — syllables the corpus has never used. Targets ≤550 KB per weight. Declared in the generated `assets/css/font-tier2.css` with a `unicode-range` **disjoint from tier-1's actual glyph set**, attached after `load` by `head-runtime.js#loadFontTier2`. The browser fetches it only when a page renders a tail syllable, which for current content means never.

Coverage analysis (regenerated 2026-08-10): the corpus has 1,286,806 total Hangul characters across 260 posts plus templates, `_data`, and scripts, using 1,044 unique syllables. Tier-1 includes all 1,044 → **100.00% coverage of every Hangul character the site can render**. Full coverage costs only ~5 KB per weight over the old 952-syllable list, which is what makes the on-demand tier-2 practical.

> **History.** Until 2026-08-10 both tiers declared the same broad `unicode-range: U+AC00-D7A3` and `loadFontTier2()` called `FontFace#load()`, so **every first visit downloaded all four files — 1,426,514 B measured on production** — even though no page needed a tier-2 glyph. Measured after the split: 423,234 B of woff2 plus a 21 KB stylesheet (~2.5 KB brotli), i.e. **~980 KB less per first visit**. Verified with Lighthouse `network-requests` against a local build: a normal post fetches tier-1 only; a probe page carrying tail syllables in its `<h1>` fetches `noto-sans-kr-700-tier2.woff2` and nothing else (weight 400 stays untouched because the tail glyphs only appeared in bold).

The disjointness is the whole mechanism, so it is generated, never hand-written, and asserted by `scripts/tests/test_font_tier_split.py`. **Do not add a `<link rel="preload">` for tier-2 and do not call `FontFace#load()` on it** — either one restores the old waste.

**Expected Lighthouse noise:** `unused-css-rules` lists `font-tier2.css` as ~21 KB
of fully unused bytes, because on a page with no tail syllable none of its
`@font-face` rules match. That is the mechanism working, not a regression — the
audit was already failing on `pages-extra.css` / `chat-page.css`, and the metrics
are unaffected (measured desktop: FCP 0.5 s, LCP 1.3 s, TBT 0 ms, CLS 0, perf 97)
because the stylesheet is attached after `load`. Do not "fix" it by deleting the
file.

## 2. File Layout

| Source / generator                                  | Generated artifact                                  | Consumer                                             |
|-----------------------------------------------------|------------------------------------------------------|------------------------------------------------------|
| `scripts/build/generate_noto_2tier_subset.py`       | `assets/fonts/noto-sans-kr-400-tier1.woff2`         | `_includes/font-face.html` `@font-face` + `<link rel="preload">` |
| `scripts/build/generate_noto_2tier_subset.py`       | `assets/fonts/noto-sans-kr-400-tier2.woff2`         | `assets/css/font-tier2.css` `@font-face` (on-demand)  |
| `scripts/build/generate_noto_2tier_subset.py`       | `assets/fonts/noto-sans-kr-700-tier1.woff2`         | `_includes/font-face.html` `@font-face`             |
| `scripts/build/generate_noto_2tier_subset.py`       | `assets/fonts/noto-sans-kr-700-tier2.woff2`         | `assets/css/font-tier2.css` `@font-face` (on-demand)  |
| `scripts/build/generate_noto_2tier_subset.py`       | `assets/css/font-tier2.css` (tail `unicode-range`)  | `head-runtime.js#loadFontTier2()` attaches it after `load`, href from `head.html`'s `data-font-tier2-href` |
| `scripts/build/noto_subset_top1k.txt`               | source-of-truth for tier-1 Hangul syllable list     | the generator's tier-1 subset + the disjointness tests |

Current sizes (regenerated 2026-08-10, 1,044-syllable tier-1):

| File                                | Size     | Fetched when                          |
|-------------------------------------|----------|---------------------------------------|
| `noto-sans-kr-400-tier1.woff2`      | 204.7 KB | always (preload)                      |
| `noto-sans-kr-700-tier1.woff2`      | 208.2 KB | always (preload)                      |
| `noto-sans-kr-400-tier2.woff2`      | 474.2 KB | page renders a tail syllable in 400   |
| `noto-sans-kr-700-tier2.woff2`      | 490.3 KB | page renders a tail syllable in 700   |
| `assets/css/font-tier2.css`         | 20.8 KB (2.5 KB brotli) | always, after `load`    |

Cache headers for `/assets/fonts/*.woff2` are set in `vercel.json:184-198` to `Cache-Control: public, max-age=31536000, immutable` so each woff2 is fetched at most once per browser indefinitely.

## 3. Regenerate

### Automatic regeneration in CI/Vercel

`build.sh` automatically checks whether the woff2 files need to be regenerated before every Jekyll build. The check uses a stamp file (`.noto-subset.stamp`) to avoid redundant work.

**When regen runs** (any of these conditions triggers it):
- Any of the 4 woff2 files is missing from `assets/fonts/`
- `assets/css/font-tier2.css` is missing (a missing tail stylesheet silently disables tier-2 fallback)
- The stamp file (`.noto-subset.stamp`) does not exist
- `scripts/build/generate_noto_2tier_subset.py` is newer than the stamp
- `scripts/build/noto_subset_top1k.txt` is newer than the stamp

**When regen is skipped** (cache hit):
- All 4 woff2 files exist AND the stamp is newer than both input files — regen outputs ~0 s overhead

**Stamp-file invariants**:
- The stamp is written (via `touch "$STAMP"`) after a successful or attempted regeneration
- `.noto-subset.stamp` is listed in `.gitignore` — it is a local build artifact, never committed
- On a fresh Vercel/CI clone all 4 woff2 files are present in the repo (committed), so the stamp is absent but mtime of committed files equals checkout time — the stamp is created immediately and subsequent builds skip regen unless inputs change

**Graceful-failure path**: if `fonttools[woff]` installation fails or the upstream URL is unreachable, the regeneration step prints a warning but does NOT abort the build. The last-known-good woff2 files already in the repo are used. This prevents a temporary upstream outage from breaking production deploys.

**Cost**: ~10 s when regeneration is needed (font download + subsetting), ~0 s on cache hit.

`build.sh` also exports the pinned upstream URL so every invocation uses the same source:

```bash
export NOTO_VF_URL='https://raw.githubusercontent.com/notofonts/noto-cjk/f8d157532fbfaeda587e826d4cd5b21a49186f7c/Sans/Variable/TTF/Subset/NotoSansKR-VF.ttf'
```

To bump the pin: update the SHA in `build.sh`, regenerate locally, commit the new woff2 files, and push.

### Manual regeneration

```bash
cd /Users/yong/Desktop/personal/tech-blog
source .venv/bin/activate          # ensures fonttools[woff] is on PATH
python3 scripts/build/generate_noto_2tier_subset.py
git diff --stat assets/fonts/ assets/css/font-tier2.css
ls -lh assets/fonts/noto-sans-kr-*.woff2
python3 -m pytest scripts/tests/test_font_tier_split.py -q   # tail range must stay disjoint
```

The generator writes `assets/css/font-tier2.css` from the same codepoint set it
feeds the subsetter, so the woff2 files and the `unicode-range` cannot diverge
as long as you regenerate both together. `test_font_tier_split.py` fails if
they do (it re-renders the CSS and compares the woff2 cmaps).

For deterministic CI reproducibility, pin the Noto upstream source:

```bash
NOTO_VF_URL='https://raw.githubusercontent.com/notofonts/noto-cjk/<commit-sha>/Sans/Variable/TTF/Subset/NotoSansKR-VF.ttf' \
  python3 scripts/build/generate_noto_2tier_subset.py
```

When to regenerate:

- A new post introduces Hangul syllables not in `scripts/build/noto_subset_top1k.txt`. This is no longer urgent: an uncovered syllable now pulls tier-2 on demand and renders correctly. Regenerating just folds it into tier-1 so that page stops paying ~500 KB. `pytest scripts/tests/test_font_tier_split.py` emits a `UserWarning` listing uncovered syllables — deliberately a warning, not a failure, because cron publishes digests without regenerating fonts and a hard gate would turn that into a red `main`.
- Noto upstream releases a new version. Review `notofonts/noto-cjk` releases quarterly and bump the pinned commit SHA.
- Tier-1 size drifts above 230 KB per weight. Either trim the top-N syllable list or split tier-1 further.

## 4. Size Monitoring

Add this to a monthly checklist:

```bash
stat -f "%z %N" assets/fonts/noto-sans-kr-*.woff2 \
  | awk '{ kb=$1/1024; printf "%6.1fKB %s\n", kb, $2 }' \
  | sort
```

Acceptance thresholds (as of PR #323):

- Tier-1 ≤ 230 KB per weight (preload budget — exceeding this hurts LCP; asserted by `test_font_tier_split.py::test_tier1_preload_budget_holds`)
- Tier-2 ≤ 550 KB per weight (on-demand budget — exceeding hurts the font-swap cost on the rare pages that need it)

If a threshold is exceeded after regeneration:

1. Inspect `scripts/build/noto_subset_top1k.txt` for unexpected entries (e.g. stray non-Hangul codepoints).
2. Reduce top-N by lowering the frequency cutoff in the generator (default keeps every syllable that appears at least once).
3. Consider splitting tier-2 further into tier-2 + tier-3 if the rare-Hangul tail grows past 700 KB.

## 5. Rollback

### Soft rollback (preferred)

```bash
git revert -m 1 12bd01d6
```

This restores the Google Fonts `<link>` tag, the `wireGoogleFonts()` JS branch, and the Google Fonts hosts in CSP. The 4 woff2 files remain on disk but are no longer referenced. Vercel redeploys automatically.

### Hard rollback (manual)

```bash
git rm assets/fonts/noto-sans-kr-*.woff2
git rm _includes/font-face.html
git checkout main~1 -- _includes/head.html assets/js/head-runtime.js vercel.json
git commit -m "revert: roll back Noto Sans KR self-host"
```

After rollback, verify the build:

```bash
bundle exec jekyll build --quiet --destination _site
grep -c 'fonts.googleapis.com' _site/index.html   # should be >= 1
grep -c 'noto-sans-kr-tier1' _site/index.html     # should be 0
```

Manually re-add `https://fonts.googleapis.com` to CSP `style-src` and `https://fonts.gstatic.com` to CSP `font-src` in `vercel.json` if they were removed by the hard rollback.

## 6. Troubleshooting

### Korean text shows as boxes (tofu)

A tail syllable failed to resolve to tier-2. Note that tier-2 is now fetched
**only on demand**, so its absence from the Network tab is normal — the question
is whether it appears on a page that needs it.

1. Elements tab → confirm `<link id="font-tier2-stylesheet">` was appended to `<head>` after load. If not, check that `head.html` still emits `data-font-tier2-href` on `#head-runtime-script`.
2. Network tab → `font-tier2.css` should be 200 OK with `Content-Type: text/css`. A 404 means the build didn't generate it (section 3).
3. Network tab → filter `noto-sans-kr-tier2` **while viewing a page with a rare syllable**. If it never fires, the syllable is probably inside tier-1's range but missing from the tail `unicode-range` — run `pytest scripts/tests/test_font_tier_split.py`.
4. If blocked by CSP: confirm `vercel.json` has `font-src 'self'` and `style-src 'self'` (no `https://fonts.gstatic.com` needed since we self-host).

### FOUT (Flash of Unstyled Text)

Expected for ~50 ms while tier-1 woff2 loads. If the FOUT lasts longer:

- Verify `<link rel="preload" as="font" type="font/woff2" crossorigin href="/assets/fonts/noto-sans-kr-400-tier1.woff2">` is present in `_site/index.html`.
- Verify the `@font-face` declaration uses `font-display: swap` (allows fallback during fetch).
- Verify the woff2 file is served with `Cache-Control: immutable` so repeat visits don't re-fetch.

### Build fails with `pyftsubset: command not found`

```bash
source .venv/bin/activate
pip install 'fonttools[woff]'
which pyftsubset    # should resolve to .venv/bin/pyftsubset
```

### Generator can't fetch Noto from `notofonts/noto-cjk`

GitHub may rate-limit or the upstream may have moved. Override:

```bash
NOTO_VF_URL='https://github.com/notofonts/noto-cjk/raw/<commit-sha>/Sans/Variable/TTF/NotoSansKR-VF.ttf' \
  python3 scripts/build/generate_noto_2tier_subset.py
```

## 7. Decision Log

- **2026-05** — Chose two-tier eager + lazy because the all-or-nothing self-host attempt produced ~1.1 MB initial transfer (both weights × full Hangul block), unacceptable for first paint. Corpus analysis revealed 952 unique syllables → ~200 KB tier-1 with 100% real-content coverage, fitting the preload budget.
- **2026-05** — Rejected Korean Linguistic Society frequency tables for tier selection. Discarded because corpus-driven analysis is more accurate for THIS site (technical security vocabulary skews different than general Korean).
- **2026-05** — Rejected FontFace API only with no preload. Discarded because tier-1 must be available before first paint — preload is required.
- **2026-08-10** — Made tier-2 on-demand via a disjoint `unicode-range`, and expanded tier-1 to full corpus coverage (952 → 1,044 syllables, +5 KB/weight). The old design fetched all four files on every first visit (1,426,514 B measured) for glyphs no page rendered. Considered and rejected: **deleting tier-2 entirely** — the corpus had drifted to 85 uncovered syllables (`꽃`, `돈`, `듣`, `삶`, `옷`, `뜻` …), so "tier-1 covers 100%" had quietly stopped being true and dropping the safety net would have degraded live pages to the system font. Also rejected: enumerating tier-1's ~1k syllables as an inline `unicode-range` (~7.5 KB of blocking CSS per page view) — the tail descriptor goes in an externally cached stylesheet instead, off the critical path.

## 8. Related References

- PR #323 — feature implementation (`12bd01d6`)
- `scripts/build/generate_noto_2tier_subset.py` — generator source
- `scripts/build/noto_subset_top1k.txt:1` — checked-in syllable list (1,044 entries)
- `assets/css/font-tier2.css` — generated tail `@font-face` pair (do not hand-edit)
- `_includes/font-face.html:1` — eager tier-1 `@font-face` + preload tag
- `_includes/head.html` — integration point (just after the `theme-init` script); carries `data-font-tier2-href`
- `assets/js/head-runtime.js#loadFontTier2` — attaches the tail stylesheet after `load`
- `scripts/tests/test_font_tier_split.py` — disjointness / cmap / no-preload invariants
- `vercel.json:34` — CSP without Google Fonts hosts; `vercel.json:184-198` — woff2 cache headers

## 9. Why Not Git LFS?

**Short answer:** The four woff2 files (~1.34 MiB total) have been touched in only two commits across the project's entire history. LFS would add per-build bandwidth cost on Vercel (~5–10 s per build, ~400 MiB/month) and contributor friction (`git lfs install` required after clone), with negligible repo-size benefit at today's scale.

The full cost-benefit analysis — including clone time metrics, Vercel build budget, and GitHub LFS bandwidth projections — lives in [`docs/optimization/WOFF2_LFS_DECISION.md`](./WOFF2_LFS_DECISION.md). The recommendation is to stay in the main git pack and enforce the rule that woff2 files may only change when the generator or corpus also changes.

**The CI discipline that replaces LFS migration:**

Instead of LFS, a dedicated CI gate enforces the invariant that no woff2 can enter the history without a corresponding source change:

- **`.gitattributes`** marks `assets/fonts/*.woff2` as `binary` so git never attempts a text diff on font files and CRLF normalization is suppressed on Windows clones.
- **`.github/workflows/font-drift-gate.yml`** triggers on every PR that touches `assets/fonts/**`. If any `*.woff2` appears in the diff, at least one of the following must also appear:
  - `scripts/build/generate_noto_2tier_subset.py`
  - `scripts/build/noto_subset_top1k.txt`
- **`scripts/dev/check_font_drift.py`** implements the same logic as a pure-stdlib CLI so the gate can be verified locally without CI:
  ```bash
  python3 scripts/dev/check_font_drift.py \
      --changed-files 'assets/fonts/noto-sans-kr-400-tier1.woff2'
  # exit 1 — fonts changed without generator/corpus update
  ```
- **Override:** For intentional font swaps that don't change the generator (e.g. an upstream Noto upstream bump committed separately), a maintainer can apply the `font-drift-allowed` label to the PR to bypass the gate.

Revisit the LFS decision if any of the triggers in `WOFF2_LFS_DECISION.md §6` becomes true (≥5 woff2-touching commits in 90 days, total woff2 size >5 MiB, etc.). Next scheduled review: 2027-04-30.
