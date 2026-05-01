# woff2 → Git LFS Migration: Cost-Benefit Analysis

**Status:** Proposed (decision document, no code change)
**Branch:** `plan/woff2-lfs-migration`
**Author:** planner agent (auto)
**Date:** 2026-04-30
**Related PRs:** [#323](https://github.com/Twodragon0/tech-blog/pull/323) (self-host woff2), [#328](https://github.com/Twodragon0/tech-blog/pull/328) (build.sh stamp-file regen), [#329](https://github.com/Twodragon0/tech-blog/pull/329) (perf-gate jitter)

---

## Executive Summary

**Recommendation: STAY in the main pack with a small enforcement discipline. Do NOT migrate to Git LFS now.**

The four `assets/fonts/*.woff2` artifacts total ~1.34 MiB and have been touched in only 2 commits across the repo's entire history. PR #328 already eliminates accidental regeneration via a stamp-file gate, so the historical bloat rate is effectively 0 bytes/year under steady state. Migrating to LFS today would add per-build LFS bandwidth on Vercel and a contributor onboarding step (`git lfs install`) without measurably reducing clone time today (1.34 MiB is ~0.23 % of a 580 MiB pack). Revisit only if a future change pushes regeneration cadence above ~10 woff2-changing commits per year, or if upstream Noto syllable corpus drift forces frequent re-subsetting.

---

## 1. Current State Metrics

All numbers gathered from this worktree, `HEAD = 2d36d259`, on 2026-04-30.

### 1.1 Repo size baseline

```
$ git count-objects -vH
count: 10559
size: 250.78 MiB
in-pack: 24696
packs: 8
size-pack: 579.81 MiB
prune-packable: 638
```

The total packed history is **579.81 MiB**, dominated by `assets/images/` (cover SVG/AVIF/WEBP/PNG) — not by fonts.

### 1.2 woff2 working-tree footprint

| File | Size (bytes) | Tier | Loading |
|------|--------------|------|---------|
| `assets/fonts/noto-sans-kr-400-tier1.woff2` | 204,116 | 1 (eager) | preload |
| `assets/fonts/noto-sans-kr-400-tier2.woff2` | 489,548 | 2 (lazy) | FontFace + idleCallback |
| `assets/fonts/noto-sans-kr-700-tier1.woff2` | 208,216 | 1 (eager) | preload |
| `assets/fonts/noto-sans-kr-700-tier2.woff2` | 505,684 | 2 (lazy) | FontFace + idleCallback |
| **Total** | **1,407,564 (~1.34 MiB)** | | |

### 1.3 woff2 history depth

```
$ git log --all --oneline -- 'assets/fonts/*.woff2' | wc -l
2
```

Exactly **two commits** have ever touched these files:

| SHA | Branch | Subject |
|-----|--------|---------|
| `4759fb6a` | feature branch (squashed) | feat(fonts): self-host Noto Sans KR via 2-tier woff2 subset |
| `12bd01d6` | main | perf(fonts): 2-tier Hangul woff2 subset (eager top-1k ~200 KB + lazy remainder) (#323) |

History bloat from woff2 today ≈ **1 set** of 1.34 MiB (the squash on main; the feature-branch ancestor is unreachable from main's first-parent chain after the squash-merge in PR #323). Conservative upper bound: **2 sets ≈ 2.7 MiB** if both blob sets remain reachable.

### 1.4 LFS state

```
$ cat .gitattributes
NO_GITATTRIBUTES

$ git lfs ls-files
git: 'lfs' is not a git command.
```

The repo currently has **no `.gitattributes`** and **Git LFS is not even installed locally**. Migrating would require: install LFS client, `git lfs install`, add `.gitattributes` rule, `git lfs migrate import --include="assets/fonts/*.woff2" --include-ref=refs/heads/main`, force-push migrated history, and require all collaborators to re-clone or re-fetch.

### 1.5 Build/deploy cadence

```
$ git log --since='7 days ago'  --oneline main | wc -l → 102
$ git log --since='30 days ago' --oneline main | wc -l → 316
```

That averages **~10–14 commits/day on main**. Vercel auto-deploys every push, so build frequency is in the same range. (Auto-publish-news cron pushes inflate this; human-authored cadence is closer to 3–5/day.)

---

## 2. Cost-Benefit per Option

### Option A — Stay in main pack (current state) + drift discipline (RECOMMENDED)

| Dimension | Cost / Benefit |
|-----------|----------------|
| Repo size today | 1.34 MiB working tree, ≤2.7 MiB pack history (0.23 %–0.46 % of pack) |
| Per-build cost | **0 s, 0 bytes** of extra network — woff2 already in the checkout |
| Clone cost | +1.34 MiB amortized over full history (~50 ms on a 100 Mbit link) |
| Bloat trajectory | **~0 bytes/year** because PR #328's stamp-file gate skips regen unless `generate_noto_2tier_subset.py` or `noto_subset_top1k.txt` is newer than `.noto-subset.stamp` |
| Vercel | No change. Free tier. |
| Contributor onboarding | No change. `git clone` + `bundle exec jekyll serve` works. |
| Drift risk | Low: any change to woff2 must be paired with a change to the corpus or the generator (CI-enforceable; see §5) |

### Option B — Migrate to Git LFS now

| Dimension | Cost / Benefit |
|-----------|----------------|
| One-time migration | `git lfs migrate import` rewrites refs; force-push to `main` required; **breaks every existing clone** (collaborators must re-clone) |
| Per-build cost on Vercel | ~5–10 s LFS pull per build, ~1.34 MiB bandwidth × ~10 builds/day × 30 = **~400 MiB/month** of LFS bandwidth; within GitHub's 1 GiB free quota today, but 40 % consumed by 4 fonts |
| Per-build cost on GitHub Actions | `actions/checkout@v4` with `lfs: true` adds ~5–10 s per workflow run; **20+ workflows** in `.github/workflows/` makes this multiplicative |
| Clone cost (cold) | Faster: pointer files (~130 bytes each) instead of 1.34 MiB blob |
| Contributor onboarding | **Adds friction**: must `git lfs install` once and `git lfs pull` after clone, otherwise local Jekyll serves 130-byte "fonts" → broken text rendering |
| Future bloat avoided | None. Stamp-file already prevents bloat in Option A. |
| Vercel free-tier risk | Vercel honors LFS, but bandwidth is metered. If LFS is enabled and a future change causes daily woff2 churn, the 1 GiB/month GitHub LFS bandwidth quota can flip to **paid** at $0.0875/GiB without warning. |

### Option C — External font CDN (e.g., Cloudflare R2)

| Dimension | Cost / Benefit |
|-----------|----------------|
| Repo size | woff2 leaves repo entirely (-1.34 MiB working tree) |
| Per-build cost | 0 s (assets fetched at runtime by browser) |
| Runtime cost | **+1 third-party DNS+TLS handshake** before first paint — exactly the regression PR #323 *removed* by self-hosting |
| Reliability | Single-point-of-failure on R2 region availability |
| Privacy | Ships visitor IP to a third-party CDN |
| Verdict | **Out of scope.** PR #323 explicitly chose self-hosting for performance (eliminating Google Fonts waterfall) and privacy. R2 reintroduces that cost class. |

---

## 3. Operational Implications

### 3.1 Local clone

| Scenario | Option A (stay) | Option B (LFS) |
|----------|------------------|----------------|
| Cold `git clone` over 100 Mbit | ~30 s end-to-end | ~25 s clone + 2 s `git lfs pull` (assuming LFS configured) |
| Cold `git clone` without LFS configured | works | **silent breakage**: woff2 are pointer text files; Jekyll serves them with `Content-Type: font/woff2` and the browser fails decode |
| Onboarding script needed | None | `bash scripts/setup.sh` would have to add `git lfs install` |

### 3.2 CI (GitHub Actions)

20+ workflows checkout the repo. None currently set `lfs: true` on `actions/checkout@v4`. Migrating to LFS requires a coordinated update to **every** workflow that touches fonts (currently: `jekyll.yml`, `lighthouse.yml`, `lighthouse-ci.yml`, `deploy-pages.yml`, `check-svg.yml` if it ever expanded). Workflows that don't touch fonts (most monitoring/cron jobs) can skip LFS to save time but must explicitly opt out.

Net CI overhead: **+5–10 s per font-relevant workflow run × ~10 runs/day ≈ 1–2 minutes/day** of paid Actions time.

### 3.3 Vercel build time

- Without LFS (today): woff2 are plain blobs in the checkout. Build cost = 0.
- With LFS: Vercel pulls LFS objects after `git clone`. Adds ~5–10 s to a ~90 s cold build (~6–11 % regression). Bandwidth: 1.34 MiB × ~10 builds/day = ~400 MiB/month — well under the 1 GiB GitHub free quota, but **shared with any other LFS-tracked file you add later**.

### 3.4 Pre-commit hooks

`scripts/check_svg_precommit.sh` only inspects SVG content; it does not read woff2 bytes. Both options work without hook changes.

### 3.5 PR #328 interaction

PR #328 added `build.sh` lines 41–60: a stamp-file gate that re-runs `scripts/build/generate_noto_2tier_subset.py` only when the generator or the corpus is newer than `.noto-subset.stamp`. On a fresh Vercel checkout the woff2 already exist and the stamp is absent, so regeneration runs once per cold deploy (~10 s) and writes the stamp; subsequent same-SHA builds skip it. Crucially, **regen does not commit the woff2 back** — it just produces them locally on the build container. So the bloat-rate argument is even stronger: under Option A, the woff2 in the repo only change when a human commits them, and that has happened twice in the project's lifetime.

---

## 4. Recommendation

**Option A — Stay in the main pack — with a one-line drift discipline added in a follow-up PR.**

### Rationale (in order of weight)

1. **Bloat is already mitigated.** PR #328's stamp-file gate means accidental regeneration commits cannot happen unless the generator or corpus changes. Historical evidence: 2 commits ever touched these files in the repo's lifetime. Future projection: ≤1 commit/year unless we deliberately retune the tier-1 corpus.
2. **Vercel build time matters more than repo size at this scale.** 1.34 MiB is 0.23 % of the existing 580 MiB pack — clone time savings are negligible. But adding an LFS pull on every Vercel deploy is a measurable +5–10 s regression for **every single build**, on a project that ships 10+ builds/day.
3. **LFS adds contributor friction without payback.** Without `git lfs install`, fonts silently break locally. The setup-worktrees workflow (TIP 1 in CLAUDE.md) creates 3–5 worktrees per developer, each of which must independently know how to `git lfs pull`. Net friction is real; net benefit is invisible.

### Caveats

- If a future PR retunes the tier-1 corpus monthly (e.g., dynamic frequency analysis), revisit. Trigger: §6.
- If the woff2 family grows to include additional weights (300, 500, 600), the per-file count and total size change; revisit at >5 MiB total or >10 files.
- If the project ever adds another large binary asset (>5 MiB) that *does* benefit from LFS (e.g., a PDF whitepaper, a video), enable LFS for that file family but keep woff2 in the main pack.

---

## 5. Implementation Checklist (Discipline, NOT Migration)

The following micro-discipline is what we recommend in place of LFS migration. Each item is a separate small PR, none of which is part of *this* PR.

### 5.1 Add `.gitattributes` to mark woff2 as binary (1-line PR)

```gitattributes
# Treat woff2 as binary — prevents text-mode diffs and CRLF mangling
assets/fonts/*.woff2 binary
```

Benefit: `git diff` shows `Binary files differ` instead of attempting a textual diff; rules out CRLF normalization on Windows clones.

### 5.2 Add a CI gate that fails when woff2 changes without a corresponding source change

A new step in `.github/workflows/jekyll.yml` (or a dedicated `font-drift-gate.yml`):

```yaml
- name: woff2 drift gate
  run: |
    BASE="${{ github.event.pull_request.base.sha || 'HEAD~1' }}"
    if git diff --name-only "$BASE"..HEAD | grep -q '^assets/fonts/.*\.woff2$'; then
      if ! git diff --name-only "$BASE"..HEAD | grep -qE '^scripts/build/(generate_noto_2tier_subset\.py|noto_subset_top1k\.txt)$'; then
        echo "::error::woff2 changed without a corresponding generator or corpus change. Re-run scripts/build/generate_noto_2tier_subset.py from a clean tree, or revert the woff2 change."
        exit 1
      fi
    fi
```

Benefit: humans cannot accidentally commit a regenerated-but-unchanged woff2 (e.g., from a stale stamp) without also changing the source-of-truth files.

### 5.3 Update `docs/optimization/NOTO_SANS_SELF_HOST_RUNBOOK.md` with a "Why not LFS?" section pointing to this document

Single section, ≤200 words. Links here.

### 5.4 (NOT RECOMMENDED) If LFS migration is later approved, the steps would be

> Reference only — do not run today.

```bash
# Prerequisites
brew install git-lfs                # macOS
git lfs install                      # in every worktree

# Add .gitattributes BEFORE migration
echo 'assets/fonts/*.woff2 filter=lfs diff=lfs merge=lfs -text' >> .gitattributes
git add .gitattributes

# Rewrite history on main only
git lfs migrate import \
  --include="assets/fonts/*.woff2" \
  --include-ref=refs/heads/main

# Verify
git lfs ls-files

# Force-push (DESTRUCTIVE — coordinate with all collaborators first)
git push --force origin main

# Update Vercel: Settings → Git → Enable Git LFS support (verify in dashboard)
# Update CI: every workflow that touches fonts must add lfs: true to actions/checkout@v4
# Update onboarding docs: README.md must say "git lfs install" is required after clone
```

---

## 6. Decision Deadline / Triggers — When to Revisit

Reopen this analysis if **any** of the following becomes true:

| Trigger | Threshold | Why it changes the math |
|---------|-----------|-------------------------|
| woff2 commit cadence | ≥5 woff2-touching commits in any rolling 90-day window | Bloat trajectory is no longer ~0; pack growth begins to matter |
| Total woff2 working-tree size | >5 MiB | Crosses the threshold where clone-time savings start to be perceptible |
| Vercel cold-build time budget | <60 s p95 | Even an extra 5 s LFS pull becomes a measurable budget eater |
| Another binary family added | New file family >5 MiB and >10 files | Justifies enabling LFS at the repo level; woff2 can ride along once the cost is paid |
| GitHub LFS bandwidth observed | Project ever uses >800 MiB/month from any other LFS-tracked asset | Adding woff2 (~400 MiB/month) would push past the 1 GiB free quota |
| Contributor count grows | >5 active external contributors | Onboarding friction multiplies; LFS may become net-positive if the LFS install step is automated in `scripts/setup.sh` |

Owner: site maintainer. Re-review cadence: **annually, or on first trigger**, whichever comes first. Next scheduled re-review: **2027-04-30**.

---

## Appendix: Raw Evidence

```
$ git rev-parse HEAD
2d36d259  (worktree branch plan/woff2-lfs-migration based off main HEAD)

$ git count-objects -vH
count: 10559
size: 250.78 MiB
in-pack: 24696
packs: 8
size-pack: 579.81 MiB
prune-packable: 638
garbage: 1
size-garbage: 64 bytes

$ ls -la assets/fonts/*.woff2 | awk '{print $5, $9}'
204116 assets/fonts/noto-sans-kr-400-tier1.woff2
489548 assets/fonts/noto-sans-kr-400-tier2.woff2
208216 assets/fonts/noto-sans-kr-700-tier1.woff2
505684 assets/fonts/noto-sans-kr-700-tier2.woff2

$ git log --all --oneline -- 'assets/fonts/*.woff2'
12bd01d6 perf(fonts): 2-tier Hangul woff2 subset (eager top-1k ~200 KB + lazy remainder) (#323)
4759fb6a feat(fonts): self-host Noto Sans KR via 2-tier woff2 subset (eager top-1k + lazy remainder)

$ cat .gitattributes 2>/dev/null || echo NO_GITATTRIBUTES
NO_GITATTRIBUTES

$ git lfs ls-files 2>&1 | head -1
git: 'lfs' is not a git command.   # LFS not installed

$ git log --since='7 days ago'  --oneline main | wc -l
102
$ git log --since='30 days ago' --oneline main | wc -l
316
```
