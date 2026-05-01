# Lighthouse Perf Gate

Per-PR Lighthouse comparison that fails when LCP regresses by more than 200 ms vs the base branch.

## What it does

`.github/workflows/lighthouse-ci.yml` runs on every PR that touches files which can affect rendering performance. For each gated PR it:

1. Builds the PR head and the PR base (`bundle exec jekyll build`).
2. Serves each build on `localhost:4000` and runs Lighthouse 3 times against each of two URLs:
   - `/` (homepage)
   - `/posts/2026/04/29/Tech_Security_Weekly_Digest_CVE_AI_Ransomware_Update/` (representative post page)
3. Computes the median LCP per URL across the 3 runs.
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
- 2 URLs × 2 builds × 3 Lighthouse runs × ~30 s = ~6 min
- Setup / caching / artifact upload = ~2 min
- **Total: ~10–15 min CI minutes per gated PR**

For repos near the 2,000-minutes-per-month free GitHub Actions tier this adds ~50 minutes per 5 perf-touching PRs.

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
