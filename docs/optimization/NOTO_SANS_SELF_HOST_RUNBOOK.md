# Noto Sans KR Self-Host Runbook

Operational guide for the self-hosted Noto Sans KR woff2 subset that ships with this site (self-host landed in PR #323 as a 2-tier layout; collapsed to a single tier 2026-08-07).

## 1. Overview

The site self-hosts Noto Sans KR as one woff2 subset per weight (400, 700) instead of fetching from Google Fonts. The motivation is twofold:

- PageSpeed flagged 45 KiB of unused CSS rules from the Google Fonts dynamic stylesheet on every page load.
- Removing the Google Fonts network dependency eliminates third-party DNS, TLS, and request waterfall before first paint, plus the GDPR/privacy exposure of font fetches to `fonts.googleapis.com` and `fonts.gstatic.com`.

The tradeoff with self-hosting Noto Sans KR is the full Hangul Syllables block (U+AC00–U+D7A3, 11,172 glyphs) compressing to ~545 KB per weight in woff2 — too heavy to preload eagerly. The subset resolves this by covering only what Korean text actually needs:

- Latin Basic + Latin-1 Supplement + Latin Extended-A + Hangul Jamo + CJK punctuation + halfwidth/fullwidth + arrows/geometry/symbols
- **KS X 1001 Hangul (2,350 syllables) ∪ every syllable observed in `_posts/*.md`**

Measured 2026-08-07: the corpus has 1,250,662 Hangul characters across 258 posts and **1,035 distinct syllables — all 1,035 inside KS X 1001**, so the union is exactly the 2,350-syllable KS X 1001 set today. The subset therefore covers 100% of every Hangul character ever published, with ~1,315 syllables of headroom for novel content.

Both faces are preloaded via `<link rel="preload">` so first paint has the font ready. There is no runtime font loading.

### Why the 2-tier layout was retired (2026-08-07)

The previous layout eager-loaded a ~200 KB "tier-1" face (top-1000 corpus syllables) and lazy-loaded a ~490 KB "tier-2" face with the remaining ~10,200 syllables — 1,374.6 KB across four files. Two structural defects made it a net loss:

1. **The tiers were disjoint, not overlapping.** tier-1 carried 952 Hangul glyphs while its CSS `unicode-range` claimed all 11,172 of U+AC00–D7A3 (tier-1 ∩ tier-2 Hangul = 0). Chrome does **not** walk the CSS fallback stack for a code point that is inside a declared range but missing from the face — it goes straight to OS system fallback. The same-family fallback tier-2 was supposed to provide never worked.
2. **The "lazy" load was not lazy.** `head-runtime.js` waited for `window.load` then `requestIdleCallback`, but on a warm load `window.load` fires before FCP so the idle callback ran immediately (84 ms observed, versus FCP at 261 ms). Worse, `FontFace.load()` fetches at Chrome priority `VeryHigh` — **above** the tier-1 preload's `High`. 972 KB of rare glyphs covering 0.0194% of body text competed with first paint.

The single face sits between the two sizes and removes both defects. Total woff2 transfer: **1,374.6 KB → 562.8 KB (−59%)**.

The `unicode-range` in `_includes/font-face.html` still declares the whole `U+AC00-D7A3` block. That is deliberate: narrowing it to the real 2,350-code-point coverage would add 10–12 KB of raw ranges to the inline `<style>`, and per defect (1) it would not change fallback behaviour for the ~8,800 unused syllables. Narrowing is tracked as a separate decision, not a bug.

## 2. File Layout

| Source / generator                            | Generated artifact                                | Consumer                                                         |
|-----------------------------------------------|---------------------------------------------------|------------------------------------------------------------------|
| `scripts/build/generate_noto_subset.py`       | `assets/fonts/noto-sans-kr-400-ksx1001.woff2`     | `_includes/font-face.html` `@font-face` + `<link rel="preload">`  |
| `scripts/build/generate_noto_subset.py`       | `assets/fonts/noto-sans-kr-700-ksx1001.woff2`     | `_includes/font-face.html` `@font-face` + `<link rel="preload">`  |
| `scripts/build/generate_noto_subset.py`       | `scripts/build/noto_subset_hangul.txt`            | font-drift-gate source of truth (2,350 entries)                  |

Current sizes (drift detection baseline as of 2026-08-07, fontTools 4.62.1):

| File                                  | Size     | Coverage                     |
|---------------------------------------|----------|------------------------------|
| `noto-sans-kr-400-ksx1001.woff2`      | 278.4 KB | 3,230 code points / 5,487 glyphs |
| `noto-sans-kr-700-ksx1001.woff2`      | 284.4 KB | 3,230 code points / 5,487 glyphs |
| **total**                             | 562.9 KB |                              |

Code-point count is lower than the 3,694 the generator requests because the upstream VF has no glyph for some of them (parts of `U+FF00-FFEF` and `U+2600-26FF`). The corpus and the full KS X 1001 set are covered — that is what the gate asserts. Sizes vary by up to ~0.1% between runs; see §3.

### Filenames must change when the bytes change

Cache headers for `/assets/fonts/*.woff2` are set in `vercel.json:176-190` to `Cache-Control: public, max-age=31536000, immutable`, and the filenames carry **no content hash**. Rewriting bytes under a name a returning visitor already cached pins them to a stale face for up to a year — and a stale face plus new CSS is how the 2-tier retirement would have shipped a broken combination (cached 952-glyph tier-1 + CSS with no tier-2). The `ksx1001` stem encodes the Hangul coverage basis: **any change to the coverage set must also change the filename stem** (`FONT_STEM` in the generator).

## 3. Regenerate

### Automatic regeneration in CI/Vercel

`build.sh` automatically checks whether the woff2 files need to be regenerated before every Jekyll build. The check uses a stamp file (`.noto-subset.stamp`) to avoid redundant work.

**When regen runs** (any of these conditions triggers it):
- Either woff2 file is missing from `assets/fonts/`
- The stamp file (`.noto-subset.stamp`) does not exist
- `scripts/build/generate_noto_subset.py` is newer than the stamp
- `scripts/build/noto_subset_hangul.txt` is newer than the stamp

**When regen is skipped** (cache hit):
- Both woff2 files exist AND the stamp is newer than both input files — regen outputs ~0 s overhead

**Stamp-file invariants**:
- The stamp is written (via `touch "$STAMP"`) after a successful or attempted regeneration
- `.noto-subset.stamp` is listed in `.gitignore` — it is a local build artifact, never committed
- On a fresh Vercel/CI clone both woff2 files are present in the repo (committed), so the stamp is absent but mtime of committed files equals checkout time — the stamp is created immediately and subsequent builds skip regen unless inputs change

**Graceful-failure path**: if `fonttools[woff]` installation fails or the upstream URL is unreachable, the regeneration step prints a warning but does NOT abort the build. The last-known-good woff2 files already in the repo are used. This prevents a temporary upstream outage from breaking production deploys.

**Cost**: ~20 s when regeneration is needed (font download + subsetting), ~0 s on cache hit.

`build.sh` also exports the pinned upstream URL so every invocation uses the same source:

```bash
export NOTO_VF_URL='https://raw.githubusercontent.com/notofonts/noto-cjk/f8d157532fbfaeda587e826d4cd5b21a49186f7c/Sans/Variable/TTF/Subset/NotoSansKR-VF.ttf'
```

To bump the pin: update the SHA in `build.sh`, regenerate locally, commit the new woff2 files, and push.

### Manual regeneration

Always pass the same pinned URL `build.sh` uses, otherwise you build from upstream `main` and produce different bytes than production:

```bash
cd /Users/yong/Desktop/personal/tech-blog
source .venv/bin/activate          # ensures fonttools[woff] is on PATH
export NOTO_VF_URL="$(grep -o "https://[^']*" build.sh | head -1)"
python3 scripts/build/generate_noto_subset.py
git diff --stat assets/fonts/      # verify expected files changed
python3 -m pytest scripts/tests/test_font_glyph_coverage.py -q
```

When to regenerate:

- **A new post introduces a Hangul syllable outside the coverage set.** `scripts/tests/test_font_glyph_coverage.py` fails CI in that case with the exact syllable(s) named. Since cron auto-publishes digests, this gate is the early warning. The generator's coverage set is `KS X 1001 ∪ corpus`, so re-running it picks up the new syllable automatically — but you must also bump `FONT_STEM` (see §2) because the bytes change under cache-immutable headers.
- Noto upstream releases a new version. Review `notofonts/noto-cjk` releases quarterly and bump the pinned commit SHA.
- Per-weight size drifts above 320 KB (the generator's `--max-kb` soft cap).

### The generator is not byte-reproducible

Re-running with an unchanged corpus, unchanged pinned upstream font, same fontTools, and even `PYTHONHASHSEED=0` yields woff2 that differ in bytes and in size by up to ~0.1% (measured 284,892 / 284,984 / 285,036 / 285,120 B for weight 400 across four runs — glyph count 5,487 and cmap 3,230 code points identical every time). brotli itself is deterministic, so the variance is inside fontTools' subsetting or woff2 transform.

Consequences:

- **Never gate on byte equality** against the committed files. `scripts/tests/test_font_glyph_coverage.py` is the authority; it asserts coverage, not bytes.
- Vercel's cold-deploy regen therefore serves bytes that differ slightly from the committed ones. Harmless (same coverage, same metrics), and regen never commits back so git history stays clean.
- Separately, rebuilding against upstream `main` instead of the pinned SHA also changes bytes. Always export `NOTO_VF_URL` from `build.sh` as shown above.

## 4. Size Monitoring

Add this to a monthly checklist:

```bash
stat -f "%z %N" assets/fonts/noto-sans-kr-*.woff2 \
  | awk '{ kb=$1/1024; printf "%6.1fKB %s\n", kb, $2 }' \
  | sort
```

Acceptance thresholds (as of 2026-08-07):

- ≤ 320 KB per weight (preload budget — exceeding this hurts LCP)
- ≤ 600 KB total across both weights

If a threshold is exceeded after regeneration:

1. Inspect `scripts/build/noto_subset_hangul.txt` for unexpected entries (e.g. stray non-Hangul codepoints).
2. Check whether new posts pulled in a large number of syllables outside KS X 1001 — if so, decide whether they are real content or mojibake.
3. Consider the variable-font route (one VF file serving both weights) before re-introducing tiering — tiering failed for the reasons in §1.

## 5. Rollback

### Soft rollback (preferred)

```bash
git revert -m 1 12bd01d6
```

This restores the Google Fonts `<link>` tag, the `wireGoogleFonts()` JS branch, and the Google Fonts hosts in CSP. The woff2 files remain on disk but are no longer referenced. Vercel redeploys automatically.

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
grep -c 'fonts.googleapis.com' _site/index.html    # should be >= 1
grep -c 'noto-sans-kr-400-ksx1001' _site/index.html # should be 0
```

Manually re-add `https://fonts.googleapis.com` to CSP `style-src` and `https://fonts.gstatic.com` to CSP `font-src` in `vercel.json` if they were removed by the hard rollback.

## 6. Troubleshooting

### Korean text shows as boxes (tofu) or in the wrong typeface

The syllable is outside the subset, so Chrome fell through to OS system fallback — silently, with no console warning and no network error.

1. Run the gate: `python3 -m pytest scripts/tests/test_font_glyph_coverage.py -q`. It names the missing syllable(s).
2. If the gate passes, the woff2 failed to load. Network tab → filter `noto-sans-kr`. Both 400 and 700 should show 200 OK with `Content-Type: font/woff2`.
3. If 404: verify the paths in `_includes/font-face.html` match the file names in `assets/fonts/`. A `FONT_STEM` bump without an include update produces exactly this.
4. If blocked by CSP: confirm `vercel.json` has `font-src 'self'` (no `https://fonts.gstatic.com` needed since we self-host).

### FOUT (Flash of Unstyled Text)

Expected for ~50 ms while the woff2 loads. If the FOUT lasts longer:

- Verify `<link rel="preload" as="font" type="font/woff2" crossorigin href="/assets/fonts/noto-sans-kr-400-ksx1001.woff2">` is present in `_site/index.html`.
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
  python3 scripts/build/generate_noto_subset.py
```

## 7. Decision Log

- **2026-05** — Chose two-tier eager + lazy because the all-or-nothing self-host attempt produced ~1.1 MB initial transfer (both weights × full Hangul block), unacceptable for first paint. Corpus analysis revealed 952 unique syllables → ~200 KB tier-1 with 100% real-content coverage, fitting the preload budget.
- **2026-05** — Rejected Korean Linguistic Society frequency tables for tier selection. Discarded because corpus-driven analysis is more accurate for THIS site (technical security vocabulary skews different than general Korean).
- **2026-05** — Rejected FontFace API only with no preload. Discarded because tier-1 must be available before first paint — preload is required.
- **2026-08-07** — Collapsed to a single tier. tier-2 was 972 KB (71% of all font bytes) covering 0.0194% of body-text syllable instances, and it did not even function as a same-family fallback because the tiers were disjoint while tier-1's `unicode-range` over-claimed. Coverage basis switched from "top-N corpus frequency" to "KS X 1001 ∪ corpus" so the set no longer shrinks/grows with post churn. 1,374.6 KB → 562.8 KB.
- **2026-08-07** — Rejected narrowing `unicode-range` to real coverage. It adds 10–12 KB of raw ranges to the inline `<style>` and changes nothing behaviourally at 2,350-syllable coverage, because Chrome skips the CSS fallback stack for in-range-but-missing glyphs. Revisit only if coverage drops far below KS X 1001.
- **2026-08-07** — Deferred the variable-font route (one VF file serving both weights). Separate PR.

## 8. Related References

- PR #323 — self-host feature implementation (`12bd01d6`)
- `scripts/build/generate_noto_subset.py` — generator source
- `scripts/build/noto_subset_hangul.txt:1` — checked-in coverage list (2,350 entries)
- `_includes/font-face.html:1` — `@font-face` + preload tags
- `_includes/head.html` — integration point (just after the `theme-init` script)
- `scripts/tests/test_font_glyph_coverage.py` — blocking Hangul coverage gate
- `vercel.json:34` — CSP without Google Fonts hosts; `vercel.json:176-190` — woff2 cache headers

## 9. Why Not Git LFS?

**Short answer:** The woff2 files (~550 KiB total since 2026-08-07, 1.34 MiB before) have been touched in only a handful of commits across the project's entire history. LFS would add per-build bandwidth cost on Vercel (~5–10 s per build, ~400 MiB/month) and contributor friction (`git lfs install` required after clone), with negligible repo-size benefit at today's scale.

The full cost-benefit analysis — including clone time metrics, Vercel build budget, and GitHub LFS bandwidth projections — lives in [`docs/optimization/WOFF2_LFS_DECISION.md`](./WOFF2_LFS_DECISION.md). The recommendation is to stay in the main git pack and enforce the rule that woff2 files may only change when the generator or coverage list also changes.

**The CI discipline that replaces LFS migration:**

Instead of LFS, a dedicated CI gate enforces the invariant that no woff2 can enter the history without a corresponding source change:

- **`.gitattributes`** marks `assets/fonts/*.woff2` as `binary` so git never attempts a text diff on font files and CRLF normalization is suppressed on Windows clones.
- **`.github/workflows/font-drift-gate.yml`** triggers on every PR that touches `assets/fonts/**`. If any `*.woff2` appears in the diff, at least one of the following must also appear:
  - `scripts/build/generate_noto_subset.py`
  - `scripts/build/noto_subset_hangul.txt`
- **`scripts/dev/check_font_drift.py`** implements the same logic as a pure-stdlib CLI so the gate can be verified locally without CI:
  ```bash
  python3 scripts/dev/check_font_drift.py \
      --changed-files 'assets/fonts/noto-sans-kr-400-ksx1001.woff2'
  # exit 1 — fonts changed without generator/corpus update
  ```
- **Override:** For intentional font swaps that don't change the generator (e.g. an upstream Noto bump committed separately), a maintainer can apply the `font-drift-allowed` label to the PR to bypass the gate.

Revisit the LFS decision if any of the triggers in `WOFF2_LFS_DECISION.md §6` becomes true (≥5 woff2-touching commits in 90 days, total woff2 size >5 MiB, etc.). Next scheduled review: 2027-04-30.
