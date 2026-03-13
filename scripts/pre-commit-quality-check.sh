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
  "${ABSOLUTE_POSTS[@]}"
