#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CRON_SCRIPT="$REPO_ROOT/scripts/morning_autopost_cron.sh"
LOG_DIR="$REPO_ROOT/logs/cron"
mkdir -p "$LOG_DIR"

if [ ! -f "$CRON_SCRIPT" ]; then
  echo "missing script: $CRON_SCRIPT" >&2
  exit 1
fi

CRON_LINE="0 9 * * * /usr/bin/env bash \"$CRON_SCRIPT\""
CRON_TAG="# tech-blog-morning-autopost"

EXISTING="$(crontab -l 2>/dev/null || true)"

FILTERED="$(printf '%s\n' "$EXISTING" | grep -v "$CRON_TAG" || true)"

{
  printf '%s\n' "$FILTERED"
  printf '%s %s\n' "$CRON_LINE" "$CRON_TAG"
} | sed '/^$/N;/^\n$/D' | crontab -

echo "installed cron entry: $CRON_LINE"
echo "check with: crontab -l"
