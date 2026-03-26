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
# Collect staged SVG files
STAGED_SVGS=$(git diff --cached --name-only --diff-filter=ACM | grep '\.svg$' || true)

if [[ -z "$STAGED_POSTS" && -z "$STAGED_SCRIPTS" && -z "$STAGED_SVGS" ]]; then
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

  # Check for truncated table summaries in digest posts
  echo "📋 Checking table summary completeness..."
  TRUNC_COUNT=0
  while IFS= read -r f; do
    # Only check Digest posts
    if echo "$f" | grep -q "Digest"; then
      # Find table rows with 핵심 내용 or 주요 키워드 that end with particles or mid-sentence
      TRUNC=$(grep -nE '\|[^|]{30,}\|[^|]*\s+(의|에|를|을|이|가|은|는|와|과|로|으로|에서|한|된|인|할|위한|하기|대한)\s*\|' "$REPO_ROOT/$f" 2>/dev/null || true)
      if [ -n "$TRUNC" ]; then
        echo "⚠️  $f: truncated table cell detected"
        echo "$TRUNC" | head -3
        TRUNC_COUNT=$((TRUNC_COUNT + 1))
      fi
    fi
  done <<< "$STAGED_POSTS"
  if [ "$TRUNC_COUNT" -gt "0" ]; then
    echo "❌ $TRUNC_COUNT post(s) have truncated table summaries — fix before committing"
    exit 1
  fi
  echo "✅ Table summaries OK"
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

# SVG text density optimization (only when SVG files are staged)
if [ -n "$STAGED_SVGS" ]; then
    SVG_OPTIMIZER="$REPO_ROOT/scripts/optimize_svg_text_density.py"
    if [ -f "$SVG_OPTIMIZER" ]; then
        echo ""
        echo "🔧 Running SVG text density optimization..."
        python3 "$SVG_OPTIMIZER" --quiet 2>/dev/null || true
        # Re-stage optimized SVGs
        while IFS= read -r f; do
            git add "$REPO_ROOT/$f" 2>/dev/null || true
        done <<< "$STAGED_SVGS"
    fi
fi

# SVG quality check (only when SVG files are staged)
if [ -n "$STAGED_SVGS" ]; then
    SVG_CHECKER="$REPO_ROOT/scripts/check_svg_quality.py"
    if [ -f "$SVG_CHECKER" ]; then
        echo ""
        echo "🖼️  Running SVG quality check..."
        SVG_FILES=()
        while IFS= read -r f; do
            SVG_FILES+=("$REPO_ROOT/$f")
        done <<< "$STAGED_SVGS"
        if python3 "$SVG_CHECKER" --ci "${SVG_FILES[@]}"; then
            echo "✅ SVG quality check passed"
        else
            echo "❌ SVG quality check failed — fix before committing"
            exit 1
        fi
    fi
fi
