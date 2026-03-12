#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

LOG_DIR="$REPO_ROOT/logs/cron"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/morning_autopost.log"
LOCK_DIR="$REPO_ROOT/.tmp/cron_morning_autopost.lock"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '[%s] Another run is active. Exit.\n' "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
  exit 0
fi

cleanup() {
  rmdir "$LOCK_DIR" >/dev/null 2>&1 || true
}
trap cleanup EXIT

printf '\n[%s] === Morning autopost cron start ===\n' "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

export CI=1
export TECH_BLOG_AUTO_YES=1
export GIT_TERMINAL_PROMPT=0

HOURS="${HOURS:-24}"
MAX_NEWS="${MAX_NEWS:-15}"
MODE="${MODE:-security}"
USE_AI="${USE_AI:-auto}"
TARGET_DATE="$(date +%Y-%m-%d)"
GH_TRIGGER_WORKFLOWS="${GH_TRIGGER_WORKFLOWS:-true}"
RUN_OPS_ROUNDTABLE="${RUN_OPS_ROUNDTABLE:-true}"
export AUTO_PUBLISH_GEMINI_TIMEOUT="${AUTO_PUBLISH_GEMINI_TIMEOUT:-12}"
export AUTO_PUBLISH_GEMINI_RETRIES="${AUTO_PUBLISH_GEMINI_RETRIES:-1}"

run_cmd() {
  "$@" >> "$LOG_FILE" 2>&1
}

run_cmd git pull --ff-only

run_cmd python3 scripts/fix_malformed_liquid_includes.py

run_cmd python3 scripts/collect_tech_news.py --hours "$HOURS" --output _data/collected_news.json --feed-timeout 15 || true

if [ -f "_data/collected_news.json" ]; then
  cp "_data/collected_news.json" "data/collected_news.json"
fi

run_cmd python3 scripts/auto_publish_news.py --hours "$HOURS" --max-news "$MAX_NEWS" --mode "$MODE" --use-ai "$USE_AI"

POST_FILE="$(ls "_posts/${TARGET_DATE}"-*Digest*.md "_posts/${TARGET_DATE}"-*Weekly*.md 2>/dev/null | sort -u | head -1 || true)"

if [ -n "$POST_FILE" ] && [ -f "$POST_FILE" ]; then
  run_cmd python3 scripts/check_posts.py "$POST_FILE" || true
  run_cmd python3 scripts/validate_post_quality.py "$POST_FILE" --warn-below 85 --fail-below 80 || true
fi

run_cmd python3 scripts/verify_images_unified.py --recent 14 || true

if [ "$RUN_OPS_ROUNDTABLE" = "true" ]; then
  if [ -n "${SENTRY_AUTH_TOKEN:-}" ] && [ -n "${SENTRY_ORG:-}" ] && [ -n "${SENTRY_PROJECT:-}" ]; then
    run_cmd python3 scripts/ops_health_orchestrator.py --auto-recover-gha --gha-rerun-limit 3 --json-output "logs/cron/ops-roundtable-${TARGET_DATE}.json" || true
  else
    run_cmd python3 scripts/ops_health_orchestrator.py --auto-recover-gha --gha-rerun-limit 3 --skip-sentry --json-output "logs/cron/ops-roundtable-${TARGET_DATE}.json" || true
  fi
fi

git add "_posts/${TARGET_DATE}"*.md 2>/dev/null || true
git add "assets/images/${TARGET_DATE}"*.svg 2>/dev/null || true
git add "_data/collected_news.json" "data/collected_news.json" "_data/published_news_urls.json" 2>/dev/null || true

PUSHED=false

if ! git diff --staged --quiet; then
  git commit -m "feat: 09:00 daily auto publish and quality checks - ${TARGET_DATE}" >> "$LOG_FILE" 2>&1 || true
  if git push >> "$LOG_FILE" 2>&1; then
    PUSHED=true
  fi
fi

if [ "$GH_TRIGGER_WORKFLOWS" = "true" ] && command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    CURRENT_BRANCH="$(git branch --show-current)"
    if [ "$PUSHED" = "true" ]; then
      gh workflow run "slack-post-notify.yml" --ref "$CURRENT_BRANCH" >> "$LOG_FILE" 2>&1 || true
      gh workflow run "buttondown-notify.yml" --ref "$CURRENT_BRANCH" >> "$LOG_FILE" 2>&1 || true
    fi
    gh workflow run "monitoring.yml" --ref "$CURRENT_BRANCH" >> "$LOG_FILE" 2>&1 || true
  fi
fi

printf '[%s] === Morning autopost cron end ===\n' "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
