# Noto Sans KR Self-Host Runbook

Operational guide for the self-hosted, two-tier Noto Sans KR woff2 subset that ships with this site (landed in PR #323).

## 1. Overview

The site self-hosts Noto Sans KR as two woff2 tiers per weight (400, 700) instead of fetching from Google Fonts. The motivation is twofold:

- PageSpeed flagged 45 KiB of unused CSS rules from the Google Fonts dynamic stylesheet on every page load.
- Removing the Google Fonts network dependency eliminates third-party DNS, TLS, and request waterfall before first paint, plus the GDPR/privacy exposure of font fetches to `fonts.googleapis.com` and `fonts.gstatic.com`.

The tradeoff with self-hosting Noto Sans KR is the full Hangul Syllables block (U+AC00–U+D7A3, 11,172 glyphs) compressing to ~545 KB per weight in woff2 — too heavy to preload eagerly. The two-tier strategy resolves this:

- **Tier 1 (eager, preloaded)**: Latin Basic + Latin-1 Supplement + Hangul Jamo + CJK punctuation + the top-N most-frequent Hangul syllables from the corpus. Targets ≤230 KB per weight. Preloaded via `<link rel="preload">` so first paint has the font ready.
- **Tier 2 (lazy, idle-loaded)**: The remaining Hangul codepoints. Targets ≤550 KB per weight. Loaded via the FontFace API inside `requestIdleCallback` after first paint. Browsers transparently fall back to tier-2 when a glyph isn't in tier-1.

Coverage analysis from PR #323: the corpus has 730,895 total Hangul characters across 155 posts and only 952 unique syllables. Tier-1 includes all 952, so **top-N covers 100.00% of every Hangul character ever published**. Tier-2 exists to handle rare syllables a future post might introduce — those render after a brief font-swap once tier-2 resolves.

## 2. File Layout

| Source / generator                                  | Generated artifact                                  | Consumer                                             |
|-----------------------------------------------------|------------------------------------------------------|------------------------------------------------------|
| `scripts/build/generate_noto_2tier_subset.py`       | `assets/fonts/noto-sans-kr-400-tier1.woff2`         | `_includes/font-face.html` `@font-face` + `<link rel="preload">` |
| `scripts/build/generate_noto_2tier_subset.py`       | `assets/fonts/noto-sans-kr-400-tier2.woff2`         | `assets/js/head-runtime.js#loadFontTier2()` via FontFace API |
| `scripts/build/generate_noto_2tier_subset.py`       | `assets/fonts/noto-sans-kr-700-tier1.woff2`         | `_includes/font-face.html` `@font-face`             |
| `scripts/build/generate_noto_2tier_subset.py`       | `assets/fonts/noto-sans-kr-700-tier2.woff2`         | `assets/js/head-runtime.js#loadFontTier2()`          |
| `scripts/build/noto_subset_top1k.txt`               | source-of-truth for tier-1 Hangul syllable list     | the generator's `--text-file=` for tier-1 subsetting |

Current sizes (drift detection baseline as of PR #323):

| File                                | Size     |
|-------------------------------------|----------|
| `noto-sans-kr-400-tier1.woff2`      | 199.3 KB |
| `noto-sans-kr-400-tier2.woff2`      | 478.1 KB |
| `noto-sans-kr-700-tier1.woff2`      | 203.3 KB |
| `noto-sans-kr-700-tier2.woff2`      | 493.8 KB |

Cache headers for `/assets/fonts/*.woff2` are set in `vercel.json:184-198` to `Cache-Control: public, max-age=31536000, immutable` so each woff2 is fetched at most once per browser indefinitely.

## 3. Regenerate

Reproducible regeneration:

```bash
cd /Users/yong/Desktop/personal/tech-blog
source .venv/bin/activate          # ensures fonttools[woff] is on PATH
python3 scripts/build/generate_noto_2tier_subset.py
git diff --stat assets/fonts/      # verify expected files changed
ls -lh assets/fonts/noto-sans-kr-*.woff2
```

For deterministic CI reproducibility, pin the Noto upstream source:

```bash
NOTO_VF_URL='https://github.com/notofonts/noto-cjk/raw/<commit-sha>/.../NotoSansKR-VF.ttf' \
  python3 scripts/build/generate_noto_2tier_subset.py
```

When to regenerate:

- A new post introduces Hangul syllables not in `scripts/build/noto_subset_top1k.txt`. The corpus already has 100% coverage, so this is rare — only meaningful for novel content (new Korean technical terms, transliterated proper nouns, etc.).
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

- Tier-1 ≤ 230 KB per weight (preload budget — exceeding this hurts LCP)
- Tier-2 ≤ 550 KB per weight (lazy budget — exceeding hurts perceived font-swap cost)

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

Tier-2 woff2 didn't load. Diagnose in browser DevTools:

1. Network tab → filter `noto-sans-kr-tier2`. Both 400 and 700 should show 200 OK with `Content-Type: font/woff2`.
2. If 404: verify the path in `assets/js/head-runtime.js#loadFontTier2()` matches the file name in `assets/fonts/`.
3. If blocked by CSP: confirm `vercel.json` has `font-src 'self'` (no `https://fonts.gstatic.com` needed since we self-host).
4. If FontFace API throws: check console for `Failed to load FontFace` errors — possibly a corrupted woff2 file. Regenerate (section 3).

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

## 8. Related References

- PR #323 — feature implementation (`12bd01d6`)
- `scripts/build/generate_noto_2tier_subset.py` — generator source
- `scripts/build/noto_subset_top1k.txt:1` — checked-in syllable list (952 entries)
- `_includes/font-face.html:1` — eager tier-1 `@font-face` + preload tag
- `_includes/head.html` — integration point (just after the `theme-init` script)
- `assets/js/head-runtime.js#loadFontTier2` — lazy tier-2 loader
- `vercel.json:34` — CSP without Google Fonts hosts; `vercel.json:184-198` — woff2 cache headers
