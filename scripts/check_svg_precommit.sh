#!/bin/sh
# SVG Quality Gate — pre-commit fragment
# Checks NEW/MODIFIED SVGs in assets/images/ root level only.
# Post-date header SVGs (YYYY-MM-DD-*) must be >=15KB.
# Small known SVGs (section-*, news-fallback.svg, *-mermaid-*) are exempt.
#
# Usage: called by .git/hooks/pre-commit (via install-hooks.sh)
# Exit code: 0 always (warnings only, does not block commit)

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
    if [ "$size" -lt 15360 ]; then
      echo "[svg-gate] WARN: $f is ${size} bytes (< 15KB)."
      echo "           Header SVGs should use the high-quality signal-map template (>=15KB)."
      echo "           Regenerate with: python3 scripts/generate_post_images.py --post $f"
      SVG_WARN=1
    fi
  fi
done

if [ "$SVG_WARN" -eq 1 ]; then
  echo "[svg-gate] One or more header SVGs are below the 15KB quality threshold."
  echo "           To commit anyway: git commit --no-verify"
fi

exit 0
