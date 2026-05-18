# GSC Recrawl Automation — Setup Runbook (PR-1 + PR-2)

**Status**: Setup checklist for the URL Inspection observability layer
plus the daily priority action report.
**Scope**: This runbook covers PR-1 (read-only inspection) and PR-2
(priority scoring + daily markdown report). Subsequent PRs (targeted
IndexNow re-ping, observability/alerts) are deferred.

The automation lives in:

- `scripts/gsc_inspect.py` — calls Search Console URL Inspection API (PR-1)
- `scripts/gsc_priority.py` — scores and ranks URLs from the state file (PR-2)
- `.github/workflows/gsc-queue-refresh.yml` — daily 06:00 UTC cron (PR-1 + PR-2)
- `requirements-gsc.txt` — isolated Python deps
- `.omc/state/gsc-queue.json` — generated state (gitignored, artifact-only)
- `.omc/state/gsc-queue-history/YYYY-MM-DD.json` — prior-day snapshots used
  for the "consecutive stuck runs" priority component (gitignored)
- `.omc/reports/gsc-daily-action-YYYY-MM-DD.md` — operator action report
  (gitignored, artifact-only)

## Why this layer exists

The Indexing API CANNOT be used for blog content — it accepts `JobPosting` or
`BroadcastEvent` schemas only. The URL Inspection API is **read-only**, so it
does NOT trigger a recrawl. What it DOES give us is an authoritative,
per-URL view of `coverageState`, `lastCrawlTime`, `indexingState`, and
`verdict` — the inputs to a priority queue that tells the human operator
which URLs to manually re-submit in the GSC UI.

See `.omc/plans/gsc-recrawl-automation.md` for the full design.

## Manual prerequisites (do these once)

### 1. Create a Google Cloud project (or reuse existing)

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., `gsc-tech-blog`) or pick an existing one.
3. Note the project ID — it becomes part of the API quota dimension.

### 2. Enable the Search Console API

In the Cloud Console:

1. Navigate to **APIs & Services → Library**.
2. Search for **"Google Search Console API"**.
3. Click **Enable**.
4. Do NOT enable the Indexing API — we deliberately do not use it.

### 3. Create a service account

1. In Cloud Console go to **IAM & Admin → Service Accounts → Create**.
2. Name: `gsc-recrawl-bot` (description: "GSC URL Inspection — read-only").
3. Skip project-level role grants (none needed; permission comes from GSC).
4. After creation, open the service account → **Keys → Add Key → JSON**.
5. Download the JSON key file. Treat it as a secret — do not commit it.

### 4. Grant the service account read access to your GSC property

1. Open [Search Console](https://search.google.com/search-console/).
2. Pick the property covering `tech.2twodragon.com`. A Domain Property
   (`sc-domain:2twodragon.com`) is preferred because it spans both Vercel and
   GitHub Pages origins.
3. **Settings → Users and permissions → Add user**.
4. Email: the service-account address ending in `…@<project>.iam.gserviceaccount.com`.
5. Permission level: **Restricted** is sufficient for `urlInspection.index.inspect`
   (the API only requires the readonly `webmasters.readonly` scope).
6. Verify access by running `scripts/gsc_inspect.py --limit 1` locally
   (see "Local testing" below).

### 5. Add the JSON key as a GitHub repo secret

1. Open the repo's **Settings → Secrets and variables → Actions → New repository secret**.
2. Name: `GSC_SERVICE_ACCOUNT_JSON`.
3. Value: paste the **raw JSON** content of the key file (NOT base64 — the
   script accepts both raw JSON and a path; raw JSON is simpler in CI).
4. Save. The workflow `gsc-queue-refresh.yml` will detect the secret and run.
   Without it, the workflow logs a clear warning and exits cleanly.

### 6. (Optional) Add the GSC site URL as a repo variable

If the site URL ever differs from the default `https://tech.2twodragon.com`
or you want to use a Domain Property (`sc-domain:2twodragon.com`):

1. **Settings → Secrets and variables → Actions → Variables → New**.
2. Name: `GSC_SITE_URL`.
3. Value: e.g., `sc-domain:2twodragon.com`.

The variable is non-secret (URL only) and overrides the script default.

## Local testing

```bash
# Install isolated deps in a venv (not the main requirements tree)
python3 -m venv .venv-gsc && source .venv-gsc/bin/activate
pip install -r requirements-gsc.txt

# Authenticate: point at the downloaded service-account key
export GSC_SERVICE_ACCOUNT_JSON="$HOME/keys/gsc-tech-blog.json"

# Smoke test: inspect 1 URL
python3 scripts/gsc_inspect.py --limit 1

# Full run: ~193 URLs, takes about 30-60 seconds
python3 scripts/gsc_inspect.py
cat .omc/state/gsc-queue.json | jq '.totals'
```

The script prints a single summary line on success:

```
inspected=193 indexed=50 discovered=100 crawled=30 errors=13
```

## Quota guidance

| Resource | Cap | This workflow's usage |
|---|---|---|
| URL Inspection — per site per day | 2 000 | ~193 / day = 10 % budget |
| URL Inspection — per site per minute | 600 | ~400 QPM in practice |
| Self-imposed daily budget (`--daily-budget`) | 500 | Safety stop |

A daily run inspecting all 193 URLs costs roughly 10 % of the daily quota.
The script sleeps 150 ms between calls to stay below the per-minute cap and
falls back to exponential backoff on HTTP 429 / 5xx.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Workflow logs `GSC_SERVICE_ACCOUNT_JSON secret is NOT set` | Step 5 not done | Add the secret per §5 |
| `failed to build Search Console client` | Bad JSON in the secret | Re-copy raw JSON (no base64) |
| All URLs return 403 | Service account not added to GSC property | Repeat §4 with correct email |
| Many 429s | Hit per-minute throttle | Wait 15 min, retry; lower `--daily-budget` |
| `no URLs found in sitemap` | Sitemap fetch failed or empty | Check the sitemap URL manually |

## Daily action report (PR-2)

After the inspection step succeeds, the workflow archives today's queue
to `.omc/state/gsc-queue-history/YYYY-MM-DD.json` and runs
`scripts/gsc_priority.py` to render a markdown action report at
`.omc/reports/gsc-daily-action-YYYY-MM-DD.md`.

### What the report contains

1. A timestamp header + coverage-state distribution table
2. **Top-N priority URLs** — the daily operator playbook
3. Suggested actions — copy-pasteable steps for the GSC UI
4. Full ranked list (collapsible `<details>`)
5. The priority-score formula coefficients

### Priority-score components

| Component | Max points | What it rewards |
|---|---|---|
| `recency` | 40 | Newer posts (linear decay over 365 days) |
| `engagement` | 0 (reserved) | Hook for future Plausible/GA4 integration (PR-5) |
| `sitemap_age` | 20 | Long time since Google last crawled the URL |
| `stuck_penalty` | 15 + up to 15 | URLs stuck in `Discovered/Crawled — currently not indexed` across consecutive prior days |

Total cap ≈ 80 points. Indexed URLs receive 0 from `stuck_penalty`; the
score is informational for indexed URLs but they naturally rank below
stuck ones.

### How to use the report

1. Find the latest workflow run under **Actions → GSC Queue Refresh**.
2. In the run's artifacts panel, download `gsc-action-{run_id}` — the
   markdown report is inside.
3. Open the report, copy each URL in the Top-N table into the GSC UI's
   URL Inspection tool, and click **Request Indexing**.
4. Stop when GSC starts rate-limiting (undocumented ~10-12/day cap per
   property).

The report is also surfaced as a workflow-summary excerpt under the
job's "Daily action report — top of report" section, so you can scan it
without downloading the artifact.

### Local dry-run

```bash
python3 scripts/gsc_priority.py --dry-run
# or use a synthetic state file:
python3 scripts/gsc_priority.py --state path/to/state.json --dry-run
```

The `--dry-run` flag prints the report to stdout and writes no files.

## What this does NOT do (yet)

PR-1 + PR-2 are read-only observability + an operator action report.
The pipeline does NOT:

- Trigger Google to recrawl any URL (no public API for this)
- Send targeted IndexNow re-pings to Bing/Naver (PR-3)
- Open GitHub issues on hard failure (PR-4)
- Persist state to the repo (artifacts only — explicit choice)
