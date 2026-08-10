# Lighthouse Perf Gate

Per-PR Lighthouse comparison that fails when LCP regresses by more than 200 ms vs the base branch.

## What it does

`.github/workflows/lighthouse-ci.yml` runs on every PR that touches files which can affect rendering performance. For each gated PR it:

1. Builds the PR head and the PR base (`bundle exec jekyll build`).
2. Resolves the URLs to measure from the PR diff (see [Which URLs get measured](#which-urls-get-measured)) — the homepage plus at most one post page.
3. Serves each build on `localhost:4000` and for each resolved URL performs:
   - 1 discarded warm-cache prerun (warms OS file cache, Node module cache, and the server's slab)
   - 5 measured Lighthouse runs
4. Computes the median LCP per URL across the 5 measured runs.
5. Calls `scripts/dev/compare_lighthouse_runs.py --threshold-lcp-ms 200`, which compares head-median vs base-median per URL and exits 1 if any URL exceeds the threshold.
6. Uploads both LHR JSON sets, the resolved URL list, and the Markdown comparison as a workflow artifact (`lighthouse-{run_id}`).
7. Comments on the PR with the comparison table (deduplicated via `comment-id: lighthouse-perf-gate` so re-runs update the same comment).
8. Writes the job's wall clock and the measured URL list to the run's step summary, so the gate's real cost stays observable instead of being re-estimated.

CLS, TBT, FCP are reported alongside LCP for context but are **informational only** — they do not gate the workflow.

## Trigger paths

The workflow runs only when the PR touches files that can plausibly affect rendering:

- `_posts/**`
- `_includes/**`, `_layouts/**`, `_sass/**`, `assets/**`
- `_config.yml`, `Gemfile.lock`, `vercel.json`
- `_plugins/**`
- `scripts/dev/compare_lighthouse_runs.py`, `scripts/dev/resolve_lighthouse_urls.py`
- `.github/workflows/lighthouse-ci.yml`

PRs that only touch docs or unrelated scripts skip the gate entirely.

## Which URLs get measured

`scripts/dev/resolve_lighthouse_urls.py` derives the list from the PR's file list (via `gh api .../pulls/N/files`, which has three-dot semantics — commits landed on main since the branch point are not attributed to the PR):

| PR touches | Measured |
|---|---|
| a post that exists in **both** builds | `/` + that post's URL |
| several posts | `/` + the newest-dated one (`MAX_POST_URLS`, default 1) |
| a **new** post (absent from base) | `/` only |
| no post (`assets/**`, `_includes/**`, …) | `/` + `DEFAULT_POST_URL` |
| — and `DEFAULT_POST_URL` no longer exists | `/` only |

Two properties are load-bearing:

**A post URL must exist in both builds.** The runs are served with `npx serve … --single`, which answers an unknown path with `index.html` — the homepage — at HTTP 200 with no redirect. Lighthouse then records the *requested* URL while measuring the *homepage*. A head-only URL would therefore be compared against the base homepage and produce a delta with a plausible sign and no meaning. So the resolver intersects the candidates across `_site_head` and `_site_base`, and the local measurement steps only run when both builds succeeded.

**The URL date is read off the build, never recomputed.** `_config.yml` pins `timezone: UTC`, so a post authored at KST 00:00–08:59 lands on the previous UTC day and its filename date ≠ its URL date. The resolver globs `posts/*/*/*/<slug>/index.html` in the built site instead of doing the date arithmetic. `redirect_from` stubs match that same glob, so candidates whose first 4 KB contain `http-equiv="refresh"` are discarded — 12 slugs in the current build have both a canonical page and a 3-level redirect stub, and the stub is a ~770-byte meta-refresh page that would measure as trivially fast.

Posts with a custom `permalink:` in front matter are not resolvable by slug and fall through to `DEFAULT_POST_URL`.

The invariants above are pinned by `scripts/tests/test_ci_lighthouse_perf_gate_guard.py`; each assertion was verified to fail against a mutated copy of the workflow before shipping.

## The gate compared head against head until 2026-08-08

Both builds are served on `localhost:4000`, one after the other. `npx serve` answers a busy port by **silently binding a random free one** while Lighthouse keeps requesting `:4000` — so the base sweep measured the head build. Three sampled runs (`31150717334`, `30882267998`, `30332794243`) all log:

```
INFO  Accepting connections at http://localhost:4000       # head
INFO  Accepting connections at http://localhost:45733      # base — nothing requests this
```

From PR #326 until this fix every comparison was a build against itself. That is why the post-page row always came back at ±2 ms, and why the two "regressions" the gate ever reported (+721 ms in PR #326, +901 ms on 2026-08-08) were both on the homepage with **no content difference at all** — see below.

A teardown-and-wait is *not* enough — run `31244446805` still found the head listener holding `:4000` when the base sweep started. So the race is removed rather than managed:

1. **Separate ports.** Head is served on `:4000`, base on `:4001`. `compare_lighthouse_runs._normalise_url` strips any localhost port, so the rows still pair up.
2. `--no-port-switching` — serve fails loudly instead of drifting, if a port is ever contended anyway.
3. A `build-id.txt` written into each site dir and read back **over HTTP** before any measurement. If the port answers `head` when the base sweep is starting, the job errors out rather than producing a confident, meaningless number. This is the check that caught the bug in the first place.

Teardown also kills the listening child (`pkill -P`), not just the `npx` wrapper.

## The homepage row is bimodal

Independently of the port bug, the homepage's LCP is bistable under Lighthouse's Lantern simulation. From one artifact (`lighthouse-31243194526`), five runs of the *same* build on the *same* side:

| | fast runs (3/5) | slow runs (2/5) |
|---|---|---|
| **observed** FCP | 213 ms | 248 ms |
| **simulated** FCP | 258 ms | 1101 ms |
| simulated LCP | 838 ms | 1721 ms |
| benchmarkIndex | 2436 | 2390 |
| network waterfall | 32 requests | identical 32 requests |

A 35 ms observed difference is amplified ~24× by the simulator. Same bytes, same request set, same CPU. The post page measured 833–843 ms across all 20 samples in the same job, so this is specific to the homepage — the same bistability `lighthouse.yml` documents for the mobile preset, at smaller magnitude.

Consequence: with a 5-run median, whichever mode wins a side's five samples decides the row, and a ±200 ms threshold sits well inside the gap. The gate ran on 0 of the last 30 merged PRs, which is why nobody hit this. Re-running the identical commit turned `/ +901 ms FAIL` into `/ +7 ms PASS`.

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

## Runner cost

### Per run — unchanged by the `_posts/**` change

Measured, not estimated: the 20 most recent `lighthouse-ci.yml` runs took **7.2–8.0 min** wall clock (median ~7.8 min), all `pull_request`-triggered. (An earlier revision of this document estimated 14–20 min; that was never observed.)

`MAX_POST_URLS` is 1, so a gated PR still sweeps exactly **2 URLs** — the same count as the old hard-coded pair. Adding `_posts/**` changed *how often* the gate runs, not how long a run takes. Re-check the number from the "Lighthouse perf gate cost" block in any run's step summary rather than trusting this paragraph.

Each extra URL beyond the cap costs 12 Lighthouse runs (2 sides × [1 warm + 5 measured]) ≈ +3 min, against a 30-minute job timeout.

### Per month — this is the part that changed

Of the **last 30 merged PRs**: **0** touched any pre-existing trigger path, and **16** touched `_posts/**`. The gate was effectively dormant. After the change roughly half of PRs are gated:

| | before | after |
|---|---|---|
| gated share of the last 30 merged PRs | 0 / 30 | 16 / 30 |
| CI minutes over those 30 PRs | ~0 | ~125 |

Against the 2,000-minutes-per-month free GitHub Actions tier that is ~6% of the budget at the repo's current PR rate. If a specific PR does not warrant it, the `perf-regression-allowed` label skips the job entirely (see below).

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
- `scripts/dev/resolve_lighthouse_urls.py` — derives the measured URL list from the PR diff
- `scripts/tests/test_compare_lighthouse_runs.py` — unit tests for the comparison script
- `scripts/tests/test_resolve_lighthouse_urls.py` — unit tests for the resolver
- `scripts/tests/test_ci_lighthouse_perf_gate_guard.py` — CI regression guard for this workflow
- `docs/optimization/LIGHTHOUSE_PERF_GATE.md` — this document

## Related

- `.github/workflows/lighthouse.yml` — the absolute-threshold check. It runs on
  **both** `push` to main and `pull_request` against main (plus
  `workflow_dispatch`), with the *same* `paths` filter on both triggers, so a
  content-only PR does not trigger it. Coexists with this workflow; covers a
  different concern — absolute budgets vs. head-to-base regression.

  It gates on:

  | Gate | Value | Source |
  |------|-------|--------|
  | accessibility / best-practices / seo | ≥ 0.80 / 0.75 / 0.90 | `manifest[].summary` (category scores) |
  | cumulative-layout-shift | ≤ 0.05 | LHR at `manifest[].jsonPath` |

  Logged for triage but **not gated**: `performance`, `largest-contentful-paint`,
  `total-blocking-time`, `benchmarkIndex` — all on one `[observed, not gated]`
  line per URL.

  The step **fails closed**: an empty or absent manifest (Lighthouse measured
  nothing) exits 1 rather than reporting success on a run that asserted nothing.
  An unreadable LHR at `jsonPath` likewise fails rather than skipping the metric
  budget.

  The gate values are protected by
  `scripts/tests/test_ci_lighthouse_gate_guard.py`; loosening one without
  updating that guard fails the build. Replaying 60 real `lighthouse-results`
  artifacts through the gate as configured: **0 red**.

### Why `performance` is not gated

The composite score is ~30% weighted on TBT, and TBT on a GitHub runner tracks
whatever CPU the VM lottery hands out. Measured over 60 runs of this workflow on
unchanged content: benchmarkIndex 1966–3439, TBT 0–2452 ms, performance
0.55–0.86. Run `29005388708` (2026-07-09) scored 30 and went red on nothing.

### Why `largest-contentful-paint` is not gated (yet)

LCP is **bimodal** on this runner and the split is not caused by anything CI
controls. Over the same 60 runs, 55 measured 4218–4373 ms and 5 measured
6921–9695 ms. The outliers are not a cold cache, a slow server or a slow CPU —
their *observed* (unthrottled) metrics are indistinguishable from a passing run's:

| | run `31150603094` | run `31151236111` |
|---|---|---|
| observed FCP | 147 ms | 147 ms |
| benchmarkIndex | 3294 | 3293 |
| **simulated LCP** | **4297 ms** | **9693 ms** |

The 5396 ms gap is produced inside Lighthouse's Lantern *simulation* of a
~1.66 MB page over the mobile preset (1.6 Mbps / 150 ms RTT / 4× CPU), which is
bistable for this page — the worst outlier amplifies observed FCP 42×. A
warm-cache prerun of the kind `lighthouse-ci.yml` uses does **not** address it:
outliers skew toward the *fastest* runners (median benchmarkIndex 3293 vs 2250,
median observed FCP 176 ms vs 1335 ms), the opposite of a cold-start signature.

Any budget placed between the two modes reds ~8.3% of runs while catching
nothing, so LCP is logged instead of gated.

**Re-adding an LCP budget.** Reduce the page's transfer weight first — the
`assets/fonts/` set is ~1374 KB across 4 files, and tier-2 (972 KB) declares the
same `unicode-range` as tier-1 (402 KB), so all four land before FCP. Once
weight is down, collect a fresh sample from the `[observed, not gated]` log
lines, confirm the bimodality is gone, then set the budget and update
`test_ci_lighthouse_gate_guard.py::test_lcp_stays_observable_but_ungated` in the
same PR. Do not re-add a budget from the old numbers.
