#!/usr/bin/env bash
# Verify the production site is accessible to Googlebot.
#
# Run after disabling Vercel Attack Challenge Mode to confirm GSC will be
# able to crawl and index pages. Exits 0 when all probes return HTTP 200,
# non-zero when any probe returns 429/challenge or other error.
#
# Usage:
#   bash scripts/check_googlebot_access.sh
#
# Background:
#   When Attack Challenge Mode is enabled, every URL returns
#   `HTTP 429` + `x-vercel-mitigated: challenge`, blocking Googlebot from
#   reading the sitemap or any post page. See
#   docs/troubleshooting/VERCEL_SECURITY_CHECKPOINT_FIX.md.

set -uo pipefail

DOMAIN="${1:-https://tech.2twodragon.com}"
UA="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

# Probe paths: homepage, sitemap, robots.txt, one recent post.
declare -a PATHS=(
  "/"
  "/sitemap.xml"
  "/robots.txt"
  "/posts/2026/05/03/Tech_Security_Weekly_Digest_Ransomware_Azure_CVE_Vulnerability/"
)

fail=0
echo "Probing ${DOMAIN} as Googlebot..."
echo

for path in "${PATHS[@]}"; do
  url="${DOMAIN}${path}"
  # Capture status code and the mitigation header in one request.
  response="$(curl -sIL -A "$UA" -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")"
  mitigation="$(curl -sIL -A "$UA" "$url" 2>/dev/null | grep -i "^x-vercel-mitigated" | tr -d '\r' || true)"

  if [ "$response" = "200" ]; then
    printf "  [OK]    %s  %s\n" "$response" "$path"
  else
    printf "  [FAIL]  %s  %s\n" "$response" "$path"
    if [ -n "$mitigation" ]; then
      printf "          %s\n" "$mitigation"
    fi
    fail=1
  fi
done

echo
if [ "$fail" = "0" ]; then
  echo "All probes 200. Googlebot can crawl the site."
  exit 0
else
  cat <<'EOF'
At least one probe failed.
If responses include x-vercel-mitigated: challenge, Attack Challenge Mode
is still enabled. Disable it at:
  https://vercel.com/<team>/<project>/settings/security
See docs/troubleshooting/VERCEL_SECURITY_CHECKPOINT_FIX.md for details.
EOF
  exit 1
fi
