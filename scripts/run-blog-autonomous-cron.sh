#!/usr/bin/env bash
# ==============================================================================
# Daily Autonomous Tech Blog Modernizer & Publishing Loop (AGY + CCG)
# Runs via cron on 24/7 Mac mini automation server.
# ==============================================================================
set -euo pipefail

REPO_DIR="/Users/namyongkim/Desktop/tech-blog"
LOG_DIR="${REPO_DIR}/logs"
LOG_FILE="${LOG_DIR}/blog-autonomous.log"
LOCK_DIR="/tmp/blog-autonomous-modernizer.lock"
VENV_PYTHON="${REPO_DIR}/.venv/bin/python"

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/Users/namyongkim/.local/bin:$PATH"
export TZ="Asia/Seoul"
export CI="1"
export TECH_BLOG_AUTO_YES="1"

mkdir -p "${LOG_DIR}"

# Atomic concurrency lock
if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
    PID=$(cat "${LOCK_DIR}/pid" 2>/dev/null || echo "")
    if [ -n "${PID}" ] && kill -0 "${PID}" 2>/dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] [WARN] Another blog modernizer process (PID ${PID}) is active. Exiting." >> "${LOG_FILE}"
        exit 0
    else
        rm -rf "${LOCK_DIR}"
        mkdir "${LOCK_DIR}" 2>/dev/null || exit 0
    fi
fi
echo "$$" > "${LOCK_DIR}/pid"
trap 'rm -rf "${LOCK_DIR}"' EXIT INT TERM

log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] [${level}] $*" | tee -a "${LOG_FILE}"
}

cd "${REPO_DIR}"

log "INFO" "========================================================"
log "INFO" "🚀 Starting Daily Tech Blog Autonomous Modernization..."
log "INFO" "========================================================"

# 1. Ensure latest main state
log "INFO" "[1/4] Checking Git working tree..."
if [ -d .git ]; then
    git stash push -m "auto-stash-before-cron" >> "${LOG_FILE}" 2>&1 || true
    git pull --rebase --autostash origin main >> "${LOG_FILE}" 2>&1 || true
fi

# 2. Run Autonomous Post Modernizer
log "INFO" "[2/4] Executing Autonomous Post Modernizer (AGY + CCG)..."
if "${VENV_PYTHON}" "${REPO_DIR}/scripts/autonomous_post_modernizer.py" --threshold 85 --limit 3 >> "${LOG_FILE}" 2>&1; then
    log "INFO" "✅ Post Modernizer completed successfully."
else
    log "WARN" "⚠️ Post Modernizer encountered issues or had zero eligible candidates."
fi

# 3. Ingest & Auto-Publish Daily DevSecOps News
log "INFO" "[3/4] Ingesting RSS feeds and auto-publishing daily news..."
"${VENV_PYTHON}" "${REPO_DIR}/scripts/collect_tech_news.py" --hours 24 >> "${LOG_FILE}" 2>&1 || true
"${VENV_PYTHON}" "${REPO_DIR}/scripts/auto_publish_news.py" >> "${LOG_FILE}" 2>&1 || true

# 4. Git Commit & Push if any changes occurred
log "INFO" "[4/4] Checking for changes to commit and push..."
if [ -n "$(git status --porcelain _posts/ assets/images/ _data/ 2>/dev/null)" ]; then
    git add _posts/ assets/images/ _data/
    COMMIT_MSG="perf(posts): autonomous modernization and daily news publish $(date '+%Y-%m-%d')"
    git commit -m "${COMMIT_MSG}" >> "${LOG_FILE}" 2>&1
    if git push origin main >> "${LOG_FILE}" 2>&1; then
        log "INFO" "🚀 Changes pushed to GitHub successfully: ${COMMIT_MSG}"
    else
        log "WARN" "⚠️ Git push failed or remote was unreachable."
    fi
else
    log "INFO" "✨ No post changes needed. Clean working tree."
fi

# Log rotation
if [ -f "${LOG_FILE}" ] && [ "$(wc -l < "${LOG_FILE}")" -gt 5000 ]; then
    tail -n 3000 "${LOG_FILE}" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "${LOG_FILE}"
    log "INFO" "🧹 Log file rotated (3,000 lines retained)."
fi

log "INFO" "========================================================"
log "INFO" "🎉 Daily Tech Blog Autonomous Run Completed."
log "INFO" "========================================================"
