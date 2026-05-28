#!/bin/sh
# Blogwatcher Raster Completeness Verification
#
# Validates that the latest auto-publish commit by blogwatcher includes
# all 5 raster image variants (PNG, WebP, AVIF for both OG and card sizes)
# alongside the SVG cover image.
#
# Spec: After eee7139a (fix: blogwatcher raster generation), all auto-publish
# commits must include:
#   1. {basename}_og.png
#   2. {basename}_og.webp
#   3. {basename}_og.avif
#   4. {basename}_card.webp
#   5. {basename}_card.avif
#
# Exit codes:
#   0 - All raster variants present
#   1 - One or more raster variants missing
#   2 - No blogwatcher auto-publish commit found in recent history
#   3 - Commit found but marked as publish-skipped (publishSkip pragma)
#
# Usage:
#   sh scripts/verify_blogwatcher_rasters.sh
#   sh scripts/verify_blogwatcher_rasters.sh --commit SHA
#
# To run manually:
#   python3 scripts/verify_blogwatcher_rasters.sh
#   python3 scripts/verify_blogwatcher_rasters.sh --commit 3d6d7119
#

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  exit 2
fi

# Parse optional --commit flag
COMMIT_SHA=""
if [ "$1" = "--commit" ] && [ -n "$2" ]; then
  COMMIT_SHA="$2"
fi

# Find the target commit
if [ -z "$COMMIT_SHA" ]; then
  # Search for the latest auto-publish commit by github-actions[bot]
  COMMIT_SHA="$(git log --all --author='github-actions\[bot\]' --grep='auto publish digest via blogwatcher' --format='%H' --max-count=1 2>/dev/null)"

  if [ -z "$COMMIT_SHA" ]; then
    # No matching commit found
    exit 2
  fi
fi

# Check if the commit message contains publishSkip pragma
COMMIT_MSG="$(git log -1 --format='%B' "$COMMIT_SHA" 2>/dev/null)"
if echo "$COMMIT_MSG" | grep -q 'publishSkip'; then
  exit 3
fi

# Extract the SVG filename from the commit's file list
# Look for files in assets/images/ directory changed in this commit
SVG_PATH="$(git show --name-only --format='' "$COMMIT_SHA" 2>/dev/null | grep '^assets/images/.*\.svg$' | head -1)"

if [ -z "$SVG_PATH" ]; then
  # No SVG found in assets/images
  exit 2
fi

# Extract basename (remove path and .svg extension)
# e.g., assets/images/2026-05-27-Example_Title.svg -> 2026-05-27-Example_Title
SVG_BASENAME=$(basename "$SVG_PATH" .svg)

# Define the 5 required raster variants
RASTERS="
${SVG_BASENAME}_og.png
${SVG_BASENAME}_og.webp
${SVG_BASENAME}_og.avif
${SVG_BASENAME}_card.webp
${SVG_BASENAME}_card.avif
"

# Check if all raster files exist in the repo at that commit
MISSING_COUNT=0
COLOR_RED=""
COLOR_GREEN=""
COLOR_RESET=""

# Detect if output is to a TTY (terminal) for color codes
if [ -t 1 ]; then
  COLOR_RED=$(printf '\033[31m')
  COLOR_GREEN=$(printf '\033[32m')
  COLOR_RESET=$(printf '\033[0m')
fi

for raster in $RASTERS; do
  # Use git ls-tree to check if file exists in the commit
  if git ls-tree -r --name-only "$COMMIT_SHA" -- "assets/images/$raster" 2>/dev/null | grep -q "$raster"; then
    printf "%s✓ %s%s\n" "$COLOR_GREEN" "$raster" "$COLOR_RESET"
  else
    printf "%s✗ %s (MISSING)%s\n" "$COLOR_RED" "$raster" "$COLOR_RESET"
    MISSING_COUNT=$((MISSING_COUNT + 1))
  fi
done

# Exit with appropriate code
if [ "$MISSING_COUNT" -gt 0 ]; then
  exit 1
fi

exit 0
