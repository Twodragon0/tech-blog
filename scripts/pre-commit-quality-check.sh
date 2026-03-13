#!/usr/bin/env bash
# Pre-commit quality check for _posts/*.md files.
# Can be used directly as .git/hooks/pre-commit or symlinked there.
#
# Usage:
#   chmod +x scripts/pre-commit-quality-check.sh
#   ln -sf ../../scripts/pre-commit-quality-check.sh .git/hooks/pre-commit

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
VALIDATOR="$REPO_ROOT/scripts/validate_post_quality.py"
FAIL_BELOW=60
WARN_BELOW=80

# Collect staged _posts/*.md files
STAGED_POSTS=$(git diff --cached --name-only --diff-filter=ACM | grep '^_posts/.*\.md$' || true)

if [[ -z "$STAGED_POSTS" ]]; then
  exit 0
fi

echo "==> Post quality check (fail < $FAIL_BELOW, warn < $WARN_BELOW)"
echo ""

if [[ ! -f "$VALIDATOR" ]]; then
  echo "WARNING: $VALIDATOR not found, skipping quality check."
  exit 0
fi

# Build absolute paths for staged files
ABSOLUTE_POSTS=()
while IFS= read -r f; do
  ABSOLUTE_POSTS+=("$REPO_ROOT/$f")
done <<< "$STAGED_POSTS"

python3 "$VALIDATOR" \
  --fail-below "$FAIL_BELOW" \
  --warn-below "$WARN_BELOW" \
  --quiet \
  "${ABSOLUTE_POSTS[@]}"

# Check for missing front matter closing ---
echo "📏 Checking front matter structure..."
FM_POSTS=$(git diff --cached --name-only --diff-filter=ACM -- '_posts/*.md' 2>/dev/null || true)
if [ -n "$FM_POSTS" ]; then
    FM_SCRIPT="$REPO_ROOT/scripts/fix_missing_front_matter_close.py"
    if [ -f "$FM_SCRIPT" ]; then
        FM_RESULT=$(cd "$REPO_ROOT" && python3 "$FM_SCRIPT" --dry-run $FM_POSTS 2>&1 || true)
        FM_FIXES=$(echo "$FM_RESULT" | grep -c "Would fix" || true)
        if [ "$FM_FIXES" -gt "0" ]; then
            echo "⚠️  $FM_FIXES post(s) missing front matter closing ---"
            echo "   Run: python3 scripts/fix_missing_front_matter_close.py --fix"
            echo "$FM_RESULT" | grep "Would fix" || true
            exit 1
        fi
    fi
fi
echo "✅ Front matter structure OK"
