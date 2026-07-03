# GSC Service-Account Key Rotation Runbook

Rotation procedure for the `GSC_SERVICE_ACCOUNT_JSON` GitHub secret — the Google
Cloud **service-account key** used by the Search Console read-only tooling. Flagged
by the 2026-07-01 workflow security review (finding LOW-5) as the most damaging
secret in the repo if leaked, so it needs a defined rotation cadence.

Initial creation is documented in [`../seo/GSC_RECRAWL_SETUP.md`](../seo/GSC_RECRAWL_SETUP.md).
This runbook is only about **rotating** the existing key.

## What this secret is

| Property | Value |
|----------|-------|
| GitHub secret | `GSC_SERVICE_ACCOUNT_JSON` (raw JSON, not base64) |
| Service account | `…@<project>.iam.gserviceaccount.com` (project e.g. `gsc-tech-blog`) |
| Granted scope | `https://www.googleapis.com/auth/webmasters.readonly` only |
| GCP project roles | **none** — access comes solely from the GSC property grant |
| GSC access level | Restricted user on the `tech.2twodragon.com` property |
| Consumers | `.github/workflows/gsc-queue-refresh.yml`, `scripts/gsc_inspect.py`, `scripts/gsc_checkpoint.py` |

Blast radius if leaked: **read-only** Search Console data for one property. It
holds no project-level IAM roles, cannot write, and cannot touch other GCP
resources. Contained by design — but a long-lived JSON key should still rotate.

## Rotation cadence

- **Every 90 days** (calendar reminder), AND
- **immediately** on any suspected exposure (key committed, CI log leak, laptop
  compromise, contributor offboarding).

## Zero-downtime rotation (GCP allows up to 10 active keys per SA)

1. **Create a new key.** GCP Console → *IAM & Admin → Service Accounts* → the GSC
   SA → *Keys → Add Key → Create new key → JSON*. Download the JSON. Treat it as
   a secret (never commit).
   - CLI equivalent:
     ```bash
     gcloud iam service-accounts keys create /tmp/gsc-new.json \
       --iam-account="<sa-name>@<project>.iam.gserviceaccount.com"
     ```
2. **Update the GitHub secret.** Repo → *Settings → Secrets and variables →
   Actions* → `GSC_SERVICE_ACCOUNT_JSON` → *Update* → paste the raw JSON.
   - CLI equivalent (run locally, not in CI):
     ```bash
     gh secret set GSC_SERVICE_ACCOUNT_JSON < /tmp/gsc-new.json
     ```
3. **Verify the new key works BEFORE deleting the old one.** Trigger the
   workflow and confirm a green run:
   ```bash
   gh workflow run gsc-queue-refresh.yml
   gh run watch "$(gh run list --workflow gsc-queue-refresh.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
   ```
   Or locally with the new key:
   ```bash
   GSC_SERVICE_ACCOUNT_JSON="$(cat /tmp/gsc-new.json)" python3 scripts/gsc_inspect.py --limit 1
   ```
   A successful inspection (HTTP 200, `coverageState` returned) confirms the new
   key + the GSC property grant are intact.
4. **Delete the OLD key** (only after step 3 is green):
   ```bash
   gcloud iam service-accounts keys list \
     --iam-account="<sa-name>@<project>.iam.gserviceaccount.com"
   gcloud iam service-accounts keys delete <OLD_KEY_ID> \
     --iam-account="<sa-name>@<project>.iam.gserviceaccount.com"
   ```
5. **Scrub the local copy:** `shred -u /tmp/gsc-new.json` (or `rm -P` on macOS).

## Post-rotation checklist

- [ ] New key verified via a green `gsc-queue-refresh.yml` run (evidence: run URL).
- [ ] Old key **deleted** in GCP (not just disabled).
- [ ] Local JSON files removed/shredded.
- [ ] Next rotation reminder set (+90 days).
- [ ] If rotating due to exposure: audit the SA's Search Console access log and
      rotate any other secret that shared the exposure channel.

## Least-privilege invariant (do not weaken)

The SA must keep **only** `webmasters.readonly` and **no** project-level IAM
role. If a future task needs write (e.g. the Indexing API), create a *separate*
narrowly-scoped SA rather than broadening this one — the Indexing API is
deliberately NOT enabled for blog content (see the setup runbook).
