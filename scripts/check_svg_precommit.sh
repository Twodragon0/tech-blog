#!/bin/sh
# SVG Quality Gate — pre-commit fragment
# Checks NEW/MODIFIED SVGs in assets/images/ root level only.
#
# Post-date header SVGs (YYYY-MM-DD-*) must fall within a healthy size band.
# We support three profiles:
#   1. Lane / digest layouts        → 5-24 KB
#   2. High-quality cover layouts   → 18-73 KB
#   3. Weekly/monthly rollup covers → 38-82 KB
#
# The card-signal-map "golden" format is ~9.5-10 KB. The lighter lane layouts
# introduced later (tutorial 3-pillar, postmortem ECG timeline, roadmap
# S-curve, comparison versus-split) land in the 5.3-6.3 KB range because
# they trade dense visual density for focused single-concept clarity.
# The high-quality cover pipeline intentionally generates ~29-32 KB cinematic
# SVGs with richer gradients, filters, and animated accents; those should not
# be warned as regressions.
# Rollup covers (WEEKLY ROLLUP / MONTHLY INDEX) embed a dense 7-or-30 day
# timeline strip with per-day severity ticks, so they intentionally land in
# the 40-80 KB range — see scripts/lib/svg_rollup_generator.py.
#
# Small known SVGs (section-*, news-fallback.svg, *-mermaid-*) are exempt.
#
# Usage: called by .git/hooks/pre-commit (via install-hooks.sh)
# Exit code: 0 always (warnings only, does not block commit)

STD_MIN_BYTES=5000
STD_MAX_BYTES=24576
HQ_MIN_BYTES=18000
HQ_MAX_BYTES=73728
ROLLUP_MIN_BYTES=38000
ROLLUP_MAX_BYTES=83968

CHANGED_SVGS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^assets/images/[^/]+\.svg$' || true)

if [ -z "$CHANGED_SVGS" ]; then
  exit 0
fi

is_high_quality_cover() {
  grep -qE 'sceneGlow1|sceneGlow2|@keyframes [^ ]*floatUp|clipPath id="[^"]*clip"|profile: high-quality-cover|id="bgSpread[A-Z0-9]*"|id="heroPanel[A-Z0-9]*"|id="bandA[A-Z0-9]+"' "$1"
}

is_rollup_cover() {
  # Weekly rollup or monthly index: produced by scripts/upgrade_rollup_cover.py
  # via scripts/lib/svg_rollup_generator.py. Distinguishable by either the
  # visible WEEKLY ROLLUP / MONTHLY INDEX header band, or the bgRoll / hdrGrad
  # gradient ids unique to the rollup defs block.
  grep -qE '>WEEKLY ROLLUP<|>MONTHLY INDEX<|id="bgRoll[A-Z0-9]+"|id="hdrGrad[A-Z0-9]+"' "$1"
}

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
    if is_rollup_cover "$f"; then
      if [ "$size" -lt "$ROLLUP_MIN_BYTES" ]; then
        echo "[svg-gate] WARN: $f is ${size} bytes (< ${ROLLUP_MIN_BYTES}) for a rollup cover SVG."
        echo "           Weekly/monthly rollup covers normally land around 50-75 KB."
        SVG_WARN=1
      elif [ "$size" -gt "$ROLLUP_MAX_BYTES" ]; then
        echo "[svg-gate] WARN: $f is ${size} bytes (> ${ROLLUP_MAX_BYTES}) for a rollup cover SVG."
        echo "           Review for accidental bloat in the timeline strip or defs block."
        SVG_WARN=1
      fi
    elif is_high_quality_cover "$f"; then
      if [ "$size" -lt "$HQ_MIN_BYTES" ]; then
        echo "[svg-gate] WARN: $f is ${size} bytes (< ${HQ_MIN_BYTES}) for a high-quality cover SVG."
        echo "           The cinematic cover profile normally lands around 29-32 KB."
        SVG_WARN=1
      elif [ "$size" -gt "$HQ_MAX_BYTES" ]; then
        echo "[svg-gate] WARN: $f is ${size} bytes (> ${HQ_MAX_BYTES}) for a high-quality cover SVG."
        echo "           Review for accidental bloat or duplicated scene markup."
        SVG_WARN=1
      fi
    else
      if [ "$size" -lt "$STD_MIN_BYTES" ]; then
        echo "[svg-gate] WARN: $f is ${size} bytes (< ${STD_MIN_BYTES})."
        echo "           Likely degenerate/empty. Regenerate with the bulk tool:"
        echo "           python3 scripts/bulk_regenerate_old_svgs.py --execute --lane digest"
        SVG_WARN=1
      elif [ "$size" -gt "$STD_MAX_BYTES" ]; then
        echo "[svg-gate] WARN: $f is ${size} bytes (> ${STD_MAX_BYTES}) for a lane/digest SVG."
        echo "           Likely a regression to the old dense dashboard format."
        echo "           Golden card-signal-map targets ~9.5-10 KB."
        SVG_WARN=1
      fi
    fi
  fi
done

if [ "$SVG_WARN" -eq 1 ]; then
  echo "[svg-gate] One or more header SVGs are outside their expected size band."
  echo "           To commit anyway: git commit --no-verify"
fi

exit 0
