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
# Collect staged script files for template test
STAGED_SCRIPTS=$(git diff --cached --name-only --diff-filter=ACM | grep -E 'scripts/auto_publish_news\.py|scripts/tests/' || true)

if [[ -z "$STAGED_POSTS" && -z "$STAGED_SCRIPTS" ]]; then
  exit 0
fi

# Post quality checks (only when posts are staged)
if [[ -n "$STAGED_POSTS" ]]; then
  echo "==> Post quality check (fail < $FAIL_BELOW, warn < $WARN_BELOW)"
  echo ""

  if [[ ! -f "$VALIDATOR" ]]; then
    echo "WARNING: $VALIDATOR not found, skipping quality check."
  else
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
  fi

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
fi

# Run template tests when auto_publish_news.py or tests are modified
if [ -n "$STAGED_SCRIPTS" ]; then
    echo ""
    echo "🧪 Running template tests (script changes detected)..."
    if python3 -m pytest "$REPO_ROOT/scripts/tests/" -q --no-header --tb=line 2>/dev/null; then
        echo "✅ Template tests passed"
    else
        echo "❌ Template tests failed — fix before committing"
        exit 1
    fi
fi
