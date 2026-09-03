#!/bin/bash
# core-bare-watch.sh — record every transition of git `core.bare` on this repo.
#
# Why this exists
# ---------------
# On 2026-09-02 `core.bare = true` was set on this repository twice, by
# something nobody identified. The symptom is alarming and misleading: with no
# work tree to diff the index against, `git status` reports every tracked path
# as deleted (3,356 of them here), which reads as catastrophic data loss. The
# files are fine; only the flag is wrong. Recovery is one command.
#
# What was ruled out by measurement (2026-09-03), so it is not worth re-testing:
#   * `git worktree add`/`remove`, 25 sequential and 25 concurrent pairs — no flip
#   * `git worktree prune`, `git gc --prune=now`                        — no flip
#   * `git init` inheriting GIT_DIR, incl. with core.bare absent        — no flip
#     (git writes `core.bare = false` there; the obvious theory is wrong)
#   * `grep -rn 'core.bare|init --bare|clone --bare|--mirror'` over the repo — 0 hits
# The remaining candidate is tooling outside the repo — harness worktree
# commands and whatever else touches .git/config — which only observation can
# catch. Hence a watcher rather than another reproduction attempt.
#
# Direction: observe and report, never repair. Auto-running
# `git config core.bare false` would erase the evidence and make the flip
# recur forever undiagnosed.
#
# Cost: one `git config` read per Bash tool call, ~5ms.
#
# Resolution note: matched to `Bash` per the current wiring, so a flip caused by
# a non-Bash path is bracketed between two Bash calls rather than pinned to one.
# Widening the matcher to `*` narrows that bracket at the cost of a subprocess
# per tool call.

set -uo pipefail

LOG_DIR="${HOME}/.claude"
LOG="${LOG_DIR}/core-bare-watch.log"
STATE="${LOG_DIR}/core-bare-watch.state"

REPO="${CLAUDE_PROJECT_DIR:-$PWD}"

# The tool payload arrives on stdin; keeping the command gives the log a
# suspect. Missing jq must not break the hook, so fall back to a marker.
PAYLOAD="$(cat 2>/dev/null || true)"
if command -v jq >/dev/null 2>&1; then
  # tr before head: a multi-line command would otherwise embed newlines and
  # break the one-line-per-transition format this log exists to be grepped as.
  # Observed on the first live firing, where the suspect was a 3-line heredoc.
  CMD="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.command // "?"' 2>/dev/null \
        | tr '\n\t' '  ' | head -c 200)"
else
  CMD="(jq unavailable)"
fi

NOW="$(git -C "$REPO" config core.bare 2>/dev/null || echo "(absent)")"
# Not a git repo, or git unavailable: nothing to watch, stay silent.
[ -n "$NOW" ] || exit 0

mkdir -p "$LOG_DIR" 2>/dev/null || exit 0
PREV="$(cat "$STATE" 2>/dev/null || echo "")"

if [ "$NOW" != "$PREV" ]; then
  printf '%s\t%s -> %s\trepo=%s\tafter=%s\n' \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "${PREV:-(first observation)}" "$NOW" "$REPO" "$CMD" \
    >> "$LOG"
  printf '%s' "$NOW" > "$STATE"
fi

if [ "$NOW" = "true" ]; then
  cat >&2 <<EOF
core.bare is TRUE on $REPO — git now reports every tracked file as deleted.
Nothing was lost; the work tree is intact.

  Fix:    git -C "$REPO" config core.bare false
  Verify: git -C "$REPO" rev-parse --is-inside-work-tree   # expect: true

The transition is recorded in $LOG with the command that preceded it — please
read that line before fixing, it is the only evidence of the cause we get.
EOF
  exit 2
fi

exit 0
