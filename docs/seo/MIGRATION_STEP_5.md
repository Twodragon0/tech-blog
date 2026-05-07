# GH Pages Permanent Migration — Step 5: DNS + Custom Domain Cutover

**Status**: Pending user action (DNS + GitHub repo settings)
**Created**: 2026-05-06
**Owner**: Repo administrator

This is the final step of the GH Pages permanent migration plan
(option A). Steps 1–4 are already shipped on `main`:

| # | Commit | What |
|---|--------|------|
| 1 | `da63f3dd` | `deploy-pages.yml` uses `build.sh` + installs `librsvg2-bin`/`cairosvg`/`Pillow`/`fonttools`/`terser` so the GH Pages build matches the Vercel pipeline (covers, woff2 subsets, JS minification). |
| 2 | `73da62de` | `jekyll-redirect-from` + 137 posts gain `redirect_from:` blocks converted from the 181 entries in `vercel.json` `redirects`. |
| 3 | `b6b70d94` | `robots.txt` `Disallow: /llms.txt` + `/llms-full.txt` (replaces the Vercel-only `X-Robots-Tag` header). |
| 4 | `f728f740` | `chatbot_enabled=false` + `search_api_enabled=false` feature flags. Chat widget gated, `serverSearch()` short-circuited. `api/*` source kept for rollback. |

Step 5 is **DNS + repo settings** and must NOT be committed automatically
because the workflow still passes `BASEURL=${{ steps.pages.outputs.base_path }}`
which resolves to `/tech-blog` while the apex/CNAME isn't registered.
Committing a `CNAME` file at that moment would cause the deploy job to
emit absolute URLs starting with `/tech-blog/` even though the apex
serves at `/`, breaking every page.

The cutover is therefore manual and ordered. **Do these in sequence, not
in parallel.**

## Pre-flight checklist (do once before starting)

- [ ] `_config.yml` `url:` is `https://tech.2twodragon.com` (verified — no
      change needed).
- [ ] `_config.yml` `baseurl:` is `""` (verified).
- [ ] Step 1 commit (`da63f3dd`) is on `main` and the `Deploy Jekyll to
      GitHub Pages` workflow has at least one green run.
- [ ] You have admin access to the DNS provider for `2twodragon.com` and
      to `github.com/Twodragon0/tech-blog/settings/pages`.
- [ ] Decide a DNS TTL window. Lower the existing record's TTL to 300s
      (5 min) at least 24 h before the cutover so rollback is fast.

## Step 5a — Add the CNAME file

Create the file on a feature branch (or directly on `main` only if the
DNS in 5b is already pointing at the right destination — see the rollback
note at the bottom).

```bash
echo "tech.2twodragon.com" > CNAME
git add CNAME
git commit -m "feat(migration): add CNAME for tech.2twodragon.com (GH Pages step 5)"
```

Do **not** push until 5b–5c are scheduled. The GH Pages workflow will
detect this file and fail to deploy until the custom domain is also
registered in repo settings (next step), so pushing it first is harmless
in practice — but it's cleaner to land it together.

## Step 5b — Register the custom domain in GitHub Pages

1. Go to https://github.com/Twodragon0/tech-blog/settings/pages
2. Under **Custom domain** enter `tech.2twodragon.com` and click **Save**.
3. GitHub will run a DNS pre-check. It will show "DNS check in progress"
   — that's expected because the DNS record from 5c hasn't propagated
   yet.
4. Leave **Enforce HTTPS** unchecked at this point (GitHub can't issue
   a Let's Encrypt cert until DNS resolves).

## Step 5c — Update DNS

In your DNS provider's dashboard for `2twodragon.com`, edit the existing
record for the `tech` subdomain.

- **From** (Vercel apex CNAME, e.g.) `cname.vercel-dns.com`
- **To** (GitHub Pages apex CNAME) `twodragon0.github.io`
- TTL: 300s (already lowered in pre-flight)

If the record was an `A`/`AAAA` set instead, replace it with the GitHub
Pages apex IPs:

```
A   tech   185.199.108.153
A   tech   185.199.109.153
A   tech   185.199.110.153
A   tech   185.199.111.153
AAAA tech 2606:50c0:8000::153
AAAA tech 2606:50c0:8001::153
AAAA tech 2606:50c0:8002::153
AAAA tech 2606:50c0:8003::153
```

(Reference: GitHub docs § "Managing a custom domain for your GitHub
Pages site".)

Wait 5–15 min and re-check `dig +short tech.2twodragon.com`. When the
new target appears, return to repo settings: GitHub Pages will
auto-issue the cert and the **Enforce HTTPS** checkbox unlocks. Tick it.

## Step 5d — Drop the workflow's `BASEURL` arg

Once GH Pages is serving on the apex, the `BASEURL` env var in
`.github/workflows/deploy-pages.yml` becomes wrong: it still injects
`/tech-blog` because that's what `actions/configure-pages` returns when
no custom domain is configured. After step 5b registers the custom
domain, `steps.pages.outputs.base_path` becomes `""` automatically — so
this commit is purely defensive belt-and-braces. You can either:

**Option D-1** (defensive — recommended): leave the workflow as-is.
`actions/configure-pages` already emits the correct empty `base_path`
when a custom domain is registered. No further commit needed.

**Option D-2** (explicit): hard-code an empty BASEURL.

```diff
       - name: Build with Jekyll (via build.sh for parity with Vercel)
         run: |
           chmod +x build.sh
           ./build.sh
         env:
           JEKYLL_ENV: production
-          BASEURL: ${{ steps.pages.outputs.base_path }}
+          BASEURL: ""
```

Verify with `curl -sI https://tech.2twodragon.com/feed.xml` returns
`200` and the body links use `https://tech.2twodragon.com/posts/...`,
not `.../tech-blog/posts/...`.

## Step 5e — Verify the redirect_from artefacts

The 137 posts modified in step 2 should now serve 301 stubs at the
legacy URLs. Spot-check three:

```bash
curl -sI https://tech.2twodragon.com/posts/2025/04/SKT_Security_Issue_Complete_Response_Guide_IMEI_Check_USIMeSIM_Replace_And_MFA_Importance/ | head -3
# Expect: HTTP/2 301 ... Location: /posts/2025/04/29/SKT_Security_...
```

```bash
curl -sI https://tech.2twodragon.com/posts/2025/05/Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/
curl -sI https://tech.2twodragon.com/posts/2026/04/12/Tech_Security_Weekly_Digest_Data_GPT_Cloud_AI/
```

If any return 404, re-run
`python3 scripts/convert_vercel_redirects_to_jekyll.py --dry-run` and
investigate the skipped list.

## Step 5f — (Later) remove `vercel.json` redirects + api/*

After GH Pages has been the live origin for 7 days with no regressions:

1. Delete `vercel.json` `redirects` block (kept duplicating the work
   `jekyll-redirect-from` now does).
2. Delete `api/chat.js`, `api/search.js`, `api/markdown.js`,
   `api/lib/` (client calls already disabled in step 4).
3. Update `vercel.json` `functions` block to remove the entries.

Do this on a separate PR with its own rollback plan.

## Rollback

If anything breaks during 5b–5c (e.g. cert issuance hangs > 30 min, or
some posts 404), the fastest path back is:

1. **DNS**: revert the record in 5c to its previous Vercel target. With
   TTL 300s, propagation is < 5 min.
2. **GitHub Pages**: leave the custom domain registered — it's harmless
   when DNS doesn't resolve to GH Pages.
3. **CNAME file** (if committed): `git revert` the commit.
4. Investigate logs at
   https://github.com/Twodragon0/tech-blog/actions/workflows/deploy-pages.yml
   and the GH Pages deploy URL
   `https://twodragon0.github.io/tech-blog/`. Steps 1–4 stay live on
   the backup origin so triage isn't time-pressured.

## Why this isn't automated

- DNS changes are the user's responsibility — the repo has no
  credential to mutate them.
- GH Pages settings are a per-repo manual toggle. The closest API
  (`PUT /repos/{owner}/{repo}/pages` with `cname` field) requires the
  same admin context as the dashboard click and offers no extra
  guarantees.
- The CNAME file's effect depends on those external preconditions, so
  committing it autonomously would be unsafe.

The workflow already builds correctly today; the only thing missing is
the operator pulling the trigger.
