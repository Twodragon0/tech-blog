# Apex domain cutover checklist

> **Superseded 2026-11-20 — decision: `tech.2twodragon.com` stays canonical.**
> The apex `2twodragon.com` does not host the blog. After the WordPress host
> (FastComet) is retired, the apex serves only 301s from the `tech-blog` Vercel
> project, scoped by `has: host` in `vercel.json`:
> the 52 migrated/mapped security posts → their `tech.2twodragon.com` URLs
> (`data/wp_redirect_map.json`), `/` → the tech home, every other WordPress path →
> the same path on the static archive `legacy.2twodragon.com`
> (`wordpress-archive-redirects.csv`; only `/category/` and `/portfolio/` differ).
> `ads.txt`/`robots.txt` are served on the apex, not redirected (AdSense reads the
> root-domain `ads.txt` for `tech.*` inventory).
> Do not change `_config.yml` `url`, canonicals, or API/Sentry origins to the apex;
> `scripts/tests/test_domain_decision.py` fails if that happens.
> The inventory below is kept for the archive and DNS facts it records.

Observed 2026-11-20. The published WordPress site is still served from
`https://2twodragon.com/`. The Vercel `tech-blog` project serves
`https://tech.2twodragon.com/`. Do not switch the apex DNS record until the
WordPress content and commerce disposition is decided and a restorable backup
has been verified.

## Current inventory

- Hosting.kr is the registrar. Cloudflare (`aaron` and `april` nameservers)
  manages DNS; FastComet/cPanel hosts WordPress.
- Cloudflare apex A record points to `139.162.90.4` and is proxied. `www` is a
  proxied CNAME to the apex. `tech` is a DNS-only CNAME to Vercel.
- The apex has Cloudflare Email Routing MX records plus SPF and Google TXT
  records. Preserve these records and all unrelated subdomains.
- Cloudflare SSL mode is Full (strict), Always Use HTTPS is on, and the zone
  has an HTTP-to-HTTPS redirect rule. No existing apex-to-tech redirect was
  found in the zone dynamic redirect ruleset.
- WordPress sitemaps expose 299 post URLs, 9 page URLs, 4 product URLs, and
  4 portfolio URLs, including shop, cart, checkout, and account routes. The
  WordPress post paths have no exact path overlap with the tech sitemap.
- A public static archive is prepared for `legacy.2twodragon.com`: 298 post
  pages plus historical pages and commerce shutdown notices. The exact
  314-path redirect map is in `wordpress-archive-redirects.csv`; the media
  path has one wildcard redirect. A separate, private WordPress files/database
  backup is still required for orders and customer records.
- Vercel has the apex and `www` assigned to `tech-blog`, but their DNS still
  points to WordPress. The project-specific Vercel verification asks for
  DNS-only CNAME records for `@` and `www`, both pointing to
  `0b63e47ee450a93e.vercel-dns-017.com.`. Cloudflare supports apex CNAME
  flattening. Verify the current Vercel recommendation again at cutover.

## Cutover sequence

1. Export and verify a complete WordPress files/database backup, including
   WooCommerce orders and customer data, outside the live hosting account.
2. Publish and verify the static archive at `legacy.2twodragon.com`, including
   representative posts, images, historical pages, and commerce notices.
   Verify the old URL redirect map in the Vercel preview deployment.
3. Deploy and verify this repository's apex canonical, sitemap, API origin,
   monitoring, and security metadata changes on Vercel.
4. Configure old URL redirects before changing DNS. Keep the old WordPress
   origin available until redirects and any archive are verified.
5. Replace only the Cloudflare apex A record with the Vercel-provided
   DNS-only CNAME. Replace the `www` CNAME target with the Vercel-provided
   DNS-only target and configure `www` to redirect to the apex. Preserve MX/TXT and other host
   records. Verify TLS, home page, representative posts, APIs, `robots.txt`,
   sitemap, old URL redirects, and mail routing.
6. In Search Console, confirm the apex property, submit the apex sitemap,
   monitor indexing and redirect errors, and retain permanent old URL
   redirects. Retire WordPress hosting only after the backup and migration
   checks have passed.

## Rollback

Restore the previous apex A record (`139.162.90.4`, proxied) and the `www`
CNAME (`2twodragon.com`, proxied) while the WordPress origin remains
available. Recheck the homepage, shop, and mail
routing. Revert the Vercel canonical deployment if traffic is restored to
WordPress for a sustained period.
