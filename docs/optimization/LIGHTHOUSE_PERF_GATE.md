# Lighthouse Perf Gate

Per-PR Lighthouse comparison that fails when LCP regresses by more than 200 ms vs the base branch.

## What it does

`.github/workflows/lighthouse-ci.yml` runs on every PR that touches files which can affect rendering performance. For each gated PR it:

1. Builds the PR head and the PR base (`bundle exec jekyll build`).
2. Serves each build on `localhost:4000` and for each of two URLs:
   - `/` (homepage)
   - `/posts/2026/04/29/Tech_Security_Weekly_Digest_CVE_AI_Ransomware_Update/` (representative post page)

   …performs:
   - 1 discarded warm-cache prerun (warms OS file cache, Node module cache, and the server's slab)
   - 5 measured Lighthouse runs
3. Computes the median LCP per URL across the 5 measured runs.
4. Calls `scripts/dev/compare_lighthouse_runs.py --threshold-lcp-ms 200`, which compares head-median vs base-median per URL and exits 1 if any URL exceeds the threshold.
5. Uploads both LHR JSON sets + the Markdown comparison as a workflow artifact (`lighthouse-{run_id}`).
6. Comments on the PR with the comparison table (deduplicated via `comment-id: lighthouse-perf-gate` so re-runs update the same comment).

CLS, TBT, FCP are reported alongside LCP for context but are **informational only** — they do not gate the workflow.

## Trigger paths

The workflow runs only when the PR touches files that can plausibly affect rendering:

- `_includes/**`, `_layouts/**`, `_sass/**`, `assets/**`
- `_config.yml`, `Gemfile.lock`, `vercel.json`
- `_plugins/**`
- `scripts/dev/compare_lighthouse_runs.py`
- `.github/workflows/lighthouse-ci.yml`

PRs that only touch posts, docs, or unrelated scripts skip the gate entirely.

## Threshold

| Metric | Threshold | Gating? |
|--------|-----------|---------|
| LCP    | head − base ≤ 200 ms | yes |
| CLS    | informational only | no |
| TBT    | informational only | no |
| FCP    | informational only | no |

The 200 ms LCP threshold matches the Core Web Vitals "good"-range tolerance (LCP < 2.5 s, with ~10% jitter expected between runs even at constant code).

## How to read the artifact

After the workflow runs, download the `lighthouse-{run_id}` artifact from the workflow run page:

- `lighthouse-comparison.md` — the same Markdown table posted as a PR comment
- `lhci-base/` — raw Lighthouse JSON for each base-branch run
- `lhci-head/` — raw Lighthouse JSON for each head-branch run

The raw LHRs include the full audit set (network, render, JS coverage, etc.) so you can drill into the cause of any regression.

## How to override the threshold for a single PR

Apply the label `perf-regression-allowed` to the PR. The workflow's `if:` clause skips the entire job when this label is present:

```yaml
if: github.event_name == 'workflow_dispatch' || !contains(github.event.pull_request.labels.*.name, 'perf-regression-allowed')
```

Use this only when an intentional tradeoff regresses LCP (e.g., shipping a heavy interactive widget that the product accepts as net-positive). Document the rationale in the PR description.

## How to re-run after fixing a regression

Push a new commit to the PR branch — the workflow re-runs automatically and the comment updates in place (replacement, not append). Or trigger manually:

```bash
gh workflow run lighthouse-ci.yml --ref <branch>
```

## Runner cost estimate

Per gated PR:

- 2 Jekyll builds × ~60 s = ~2 min
- 2 URLs × 2 builds × 1 warm prerun × ~30 s = ~2 min (discarded, not counted in CI gate time)
- 2 URLs × 2 builds × 5 Lighthouse runs × ~30 s = ~10 min
- Setup / caching / artifact upload = ~2 min
- **Total: ~14–20 min CI minutes per gated PR** (was ~10–15 min with 3 runs)

For repos near the 2,000-minutes-per-month free GitHub Actions tier this adds ~80–100 minutes per 5 perf-touching PRs (was ~50 minutes).

## Stability tuning

### Why warm-cache prerun + 5 medians?

**Empirical trigger**: PR #326 (which introduced this workflow) self-tested its own gate and produced a **+721 ms false positive** on the homepage: 1 s LCP baseline → 1.7 s head, on a no-op-rendering commit. The root cause was cold-runner jitter — the very first Lighthouse run on a cold GitHub Actions runner is systematically slower because:

1. The OS page cache is empty (kernel must read Chrome / Node / Jekyll static files from disk).
2. Node's module loader has not yet warmed the V8 code cache for lighthouse internals.
3. The `serve` process's internal slab allocator has not pre-faulted memory pages.

When the homepage LCP is sub-1-second, a single 700 ms cold-start outlier is enough to skew a 3-run median by more than 200 ms — the entire gate threshold.

**Fix 1 — Discarded warm-cache prerun**: Before each measured sequence, one additional Lighthouse run is fired with `--output-path=/dev/null`. This run is **never written to disk and never included in the median**. Its sole purpose is to warm the three caches above so that all 5 measured runs start from the same warm state.

**Fix 2 — 5 medians instead of 3**: Per the [Lighthouse stability documentation](https://github.com/GoogleChrome/lighthouse/blob/main/docs/variability.md), 5 runs give a substantially more stable median than 3, especially for sub-1-second LCP values where absolute noise is proportionally larger. The odd run count also eliminates tie-break ambiguity in the median computation.

**Threshold unchanged**: The 200 ms LCP regression threshold is not adjusted — the goal is to make the gate reliable at the existing threshold, not to relax it.

**CI cost**: +1 warm × 2 URLs × 2 builds = +4 runs; +2 measured × 2 URLs × 2 builds = +8 runs; total +12 runs ≈ +6 min CI per gated PR.

## Local diagnosis

You can run the comparison script directly against any two Lighthouse output directories:

```bash
python3 scripts/dev/compare_lighthouse_runs.py \
  --base-dir lhci-base \
  --head-dir lhci-head \
  --threshold-lcp-ms 200 \
  --output-md /tmp/lh.md
```

Exit code 0 = no regression. Exit code 1 = at least one URL exceeded the threshold.

## Files

- `.github/workflows/lighthouse-ci.yml` — the workflow
- `scripts/dev/compare_lighthouse_runs.py` — the comparison script
- `scripts/tests/test_compare_lighthouse_runs.py` — unit tests for the script
- `docs/optimization/LIGHTHOUSE_PERF_GATE.md` — this document

## Related

- `.github/workflows/lighthouse.yml` — the existing absolute-threshold check (Performance ≥ 0.5, etc.) that runs on push to main. Coexists with this workflow; covers different concern.
