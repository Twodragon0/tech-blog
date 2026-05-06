# SEO Canonical Fix — 2026-05-06

## Symptom

Google Search Console reported on tech.2twodragon.com:

- 17 pages "Not Found (404)"
- 4 pages "Page with redirect"
- 126 pages "Crawled — currently not indexed"

Sibling subdomain `investing.2twodragon.com` indexed normally on the same Vercel
account, ruling out account-level issues.

## Root cause

`_includes/head.html` emitted canonical/og/JSON-LD URLs through Jekyll's
`absolute_url` filter. `absolute_url` prepends both `site.url` AND
`site.baseurl`. On the GH Pages backup the build runs with
`--baseurl "/tech-blog"`, so every emitted URL looked like:

```
<link rel="canonical" href="https://tech.2twodragon.com/tech-blog/">
<meta property="og:url"   content="https://tech.2twodragon.com/tech-blog/">
<meta property="og:image" content="https://tech.2twodragon.com/tech-blog/assets/images/...">
```

The host is the Vercel apex but the path includes the GH-Pages-only
`/tech-blog/` segment, which 404s on Vercel. Googlebot crawled the GH Pages
backup, followed the canonical, hit a 404, and refused to index. The same
pattern leaked into:

- `_includes/head.html` — canonical_url, share_url, og_image_url, JSON-LD
  url/mainEntityOfPage/logo/image
- `sitemap.xml` — every `<loc>` entry plus `<image:loc>`

## Fix (commit `312faeb5`)

Replace `{{ ... | absolute_url }}` and `{{ site.url }}{{ site.baseurl }}{{ ... }}`
with `{{ site.url }}{{ page.url }}` for any URL that should always point to
the canonical Vercel host:

```liquid
{# CANONICAL/SHARE/SITEMAP — ALWAYS site.url only, NEVER site.baseurl #}
{% assign canonical_url = site.url | append: page.url %}
{% assign share_url     = site.url | append: page.url %}
{% assign og_image_url  = site.url | append: og_image %}
```

Same-origin asset paths (favicon, RSS feed link, embedded `<img>` src) **keep**
`relative_url` so they load from whichever origin actually serves the page.

## Why this matters

- Vercel build (`baseurl=""`):   canonical = `https://tech.2twodragon.com{page.url}` ✓
- GH Pages backup (`baseurl="/tech-blog"`): canonical = same URL ✓
  (tells Google "the canonical lives on Vercel — the backup is duplicate")

## Anti-pattern hook

`.claude/hooks/canonical-url-gate.sh` warns whenever a SEO-emitting template
introduces `absolute_url` or `site.baseurl` near canonical/og/`<loc>`/share
fields. Wired into `.claude/settings.json` PostToolUse for Write|Edit on
`head.html`, `sitemap.xml`, `feed.xml`, `llms.txt`, `llms-full.txt`.

## Verification

```bash
# Both URLs must equal the production canonical:
curl -s https://twodragon0.github.io/tech-blog/ | grep -E 'canonical|og:url'
# canonical=https://tech.2twodragon.com/  ✓
# og:url   =https://tech.2twodragon.com/  ✓

curl -s https://twodragon0.github.io/tech-blog/sitemap.xml | grep -c '/tech-blog/'
# 0  ✓
```

## Follow-up actions for the user

1. GSC → URL inspection → Request indexing for the 10 priority posts.
2. GSC → Submit sitemap (already at `/sitemap.xml`).
3. Vercel dashboard → Settings → Security → consider disabling Attack
   Challenge Mode so Googlebot can fetch fresh content (memory:
   `feedback_vercel_challenge_mode.md`).
4. Bing Webmaster + Naver Search Advisor — register and submit sitemap.
