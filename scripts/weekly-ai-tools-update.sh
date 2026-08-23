#!/usr/bin/env bash
# ==============================================================================
# Weekly AI Tools Auto-Updater (AGY, Claude Code, OMC / OpenCode, OpenClaw)
# Runs weekly via cron on Mac mini 24/7 automation server.
# ==============================================================================
set -euo pipefail

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/Users/namyongkim/.local/bin:$PATH"
export TZ="Asia/Seoul"

LOG_DIR="/Users/namyongkim/Desktop/tech-blog/logs"
LOG_FILE="${LOG_DIR}/ai-tools-update.log"
LOCK_DIR="/tmp/ai-tools-update.lock"

# Concurrency lock (macOS compatible atomic mkdir)
if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
    PID=$(cat "${LOCK_DIR}/pid" 2>/dev/null || echo "")
    if [ -n "${PID}" ] && kill -0 "${PID}" 2>/dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] [WARN] Another update process (PID ${PID}) is running. Exiting." >> "${LOG_FILE}"
        exit 0
    else
        # Stale lock cleanup
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

log "INFO" "========================================================"
log "INFO" "🚀 Starting Weekly AI Tools & Engine Auto-Update..."
log "INFO" "========================================================"

# 1. Update Antigravity (AGY)
log "INFO" "[1/5] Updating Antigravity CLI (agy)..."
if command -v agy >/dev/null 2>&1; then
    PREV_AGY=$(agy --version 2>&1 || echo "unknown")
    if agy update >> "${LOG_FILE}" 2>&1; then
        NEW_AGY=$(agy --version 2>&1 || echo "unknown")
        log "INFO" "✅ agy updated successfully: ${PREV_AGY} -> ${NEW_AGY}"
    else
        log "WARN" "⚠️ agy update encountered a non-fatal status. (Current: ${PREV_AGY})"
    fi
else
    log "WARN" "⚠️ agy command not found on PATH."
fi

# 2. Update Claude Code
log "INFO" "[2/5] Updating Claude Code CLI (claude)..."
if command -v claude >/dev/null 2>&1; then
    PREV_CLAUDE=$(claude --version 2>&1 || echo "unknown")
    if claude update >> "${LOG_FILE}" 2>&1; then
        NEW_CLAUDE=$(claude --version 2>&1 || echo "unknown")
        log "INFO" "✅ claude updated successfully: ${PREV_CLAUDE} -> ${NEW_CLAUDE}"
    else
        log "WARN" "⚠️ claude update encountered a non-fatal status. (Current: ${PREV_CLAUDE})"
    fi
else
    log "WARN" "⚠️ claude command not found on PATH."
fi

# 3. Update Global NPM Packages (OMC, OpenClaw, Codex, Sisyphus)
log "INFO" "[3/5] Updating Global NPM packages (OMC, OpenClaw, Codex)..."
if command -v npm >/dev/null 2>&1; then
    npm update -g oh-my-claude-sisyphus oh-my-opencode openclaw @openai/codex clawhub >> "${LOG_FILE}" 2>&1 || true
    log "INFO" "✅ Global NPM packages updated (oh-my-claude-sisyphus, oh-my-opencode, openclaw, @openai/codex)."
else
    log "WARN" "⚠️ npm command not found on PATH."
fi

# 4. Update OpenCode (Homebrew Formula)
log "INFO" "[4/5] Upgrading OpenCode via Homebrew..."
if command -v brew >/dev/null 2>&1; then
    brew upgrade opencode >> "${LOG_FILE}" 2>&1 || true
    OPENCODE_VER=$(opencode --version 2>&1 || echo "unknown")
    log "INFO" "✅ opencode version: ${OPENCODE_VER}"
else
    log "WARN" "⚠️ brew command not found on PATH."
fi

# 5. Rotate Logs (keep last 5,000 lines)
if [ -f "${LOG_FILE}" ] && [ "$(wc -l < "${LOG_FILE}")" -gt 5000 ]; then
    tail -n 3000 "${LOG_FILE}" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "${LOG_FILE}"
    log "INFO" "🧹 Log file rotated (truncated to recent 3,000 lines)."
fi

log "INFO" "========================================================"
log "INFO" "🎉 Weekly AI Tools Update Completed Successfully."
log "INFO" "========================================================"
