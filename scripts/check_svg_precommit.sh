#!/bin/sh
# SVG Quality Gate — pre-commit fragment
# Checks NEW/MODIFIED SVGs in assets/images/ root level only.
#
# Post-date header SVGs (YYYY-MM-DD-*) must fall within a healthy size band:
#   - min 8 KB   : guard against degenerate/empty/placeholder SVGs
#   - max 24 KB  : guard against regression to the old 31+ KB dense dashboard
#                  layouts with truncated SHA256 dumps, 40+ text nodes, etc.
#
# The card-signal-map "golden" format introduced in commit 7f7ae7b1 is
# intentionally compact (~9.5-10 KB) because it trades dense text labels
# for clean topic cards + threat-map nodes. Warning below 15KB is therefore
# obsolete and was producing false positives on every healthy regen.
#
# Small known SVGs (section-*, news-fallback.svg, *-mermaid-*) are exempt.
#
# Usage: called by .git/hooks/pre-commit (via install-hooks.sh)
# Exit code: 0 always (warnings only, does not block commit)

MIN_BYTES=8192     # 8 KB
MAX_BYTES=24576    # 24 KB

CHANGED_SVGS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^assets/images/[^/]+\.svg$' || true)

if [ -z "$CHANGED_SVGS" ]; then
  exit 0
fi

SVG_WARN=0
for f in $CHANGED_SVGS; do
  base=$(basename "$f")

  # Skip known small/exempt filenames
  case "$base" in
    section-*|news-fallback.svg|*-mermaid-*|*-og.svg)
      continue
      ;;
  esac

  # Only check files matching the post-date pattern: YYYY-MM-DD-*
  if echo "$base" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}-'; then
    size=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null || echo 0)
    if [ "$size" -lt "$MIN_BYTES" ]; then
      echo "[svg-gate] WARN: $f is ${size} bytes (< ${MIN_BYTES})."
      echo "           Likely degenerate/empty. Regenerate with the bulk tool:"
      echo "           python3 scripts/bulk_regenerate_old_svgs.py --execute --lane digest"
      SVG_WARN=1
    elif [ "$size" -gt "$MAX_BYTES" ]; then
      echo "[svg-gate] WARN: $f is ${size} bytes (> ${MAX_BYTES})."
      echo "           Likely a regression to the old dense dashboard format."
      echo "           Golden card-signal-map targets ~9.5-10 KB."
      SVG_WARN=1
    fi
  fi
done

if [ "$SVG_WARN" -eq 1 ]; then
  echo "[svg-gate] One or more header SVGs are outside the ${MIN_BYTES}-${MAX_BYTES} byte quality band."
  echo "           To commit anyway: git commit --no-verify"
fi

exit 0
