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
TARGET_DATE="$(date +%Y-%m-%d)"

git pull --ff-only >> "$LOG_FILE" 2>&1

python3 scripts/collect_tech_news.py --hours "$HOURS" --output _data/collected_news.json --feed-timeout 15 >> "$LOG_FILE" 2>&1 || true

if [ -f "_data/collected_news.json" ]; then
  cp "_data/collected_news.json" "data/collected_news.json"
fi

python3 scripts/auto_publish_news.py --hours "$HOURS" --max-news "$MAX_NEWS" --mode "$MODE" >> "$LOG_FILE" 2>&1

POST_FILE="$(ls "_posts/${TARGET_DATE}"-*Digest*.md "_posts/${TARGET_DATE}"-*Weekly*.md 2>/dev/null | sort -u | head -1 || true)"

if [ -n "$POST_FILE" ] && [ -f "$POST_FILE" ]; then
  python3 scripts/check_posts.py "$POST_FILE" >> "$LOG_FILE" 2>&1 || true
  python3 scripts/validate_post_quality.py "$POST_FILE" --warn-below 85 --fail-below 80 >> "$LOG_FILE" 2>&1 || true
fi

python3 scripts/verify_images_unified.py --recent 14 >> "$LOG_FILE" 2>&1 || true

git add "_posts/${TARGET_DATE}"*.md 2>/dev/null || true
git add "assets/images/${TARGET_DATE}"*.svg 2>/dev/null || true
git add "_data/collected_news.json" "data/collected_news.json" "_data/published_news_urls.json" 2>/dev/null || true

if ! git diff --staged --quiet; then
  git commit -m "feat: 09:00 daily auto publish and quality checks - ${TARGET_DATE}" >> "$LOG_FILE" 2>&1 || true
  git push >> "$LOG_FILE" 2>&1 || true
fi

printf '[%s] === Morning autopost cron end ===\n' "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
