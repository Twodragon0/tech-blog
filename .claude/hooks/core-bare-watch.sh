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
# Cost
# ----
# The first version claimed "~5ms" for one `git config` read. That was an
# estimate, never measured, and it was wrong by three orders of magnitude.
# Measured on this machine, 20 iterations each:
#
#     shell loop, no subprocess         19 ms
#     /bin/echo (bare process spawn)   106 ms
#     jq                               109 ms
#     git config core.bare            1110 ms
#     git -C <path> config core.bare  1467 ms
#     whole hook, original             1722 ms   <- per Bash tool call
#     reading .git/config in bash       15 ms   <- i.e. the loop baseline
#
# `git config` costs the same 1.7s in a two-file scratch repo, so this is the
# cost of spawning `git` here (process spawn is already 106ms; something scans
# each exec), not anything about this repository. Shrinking the repo would not
# help; not spawning git is what helps.
#
# So the common path now reads `.git/config` with shell builtins and spends the
# `git` call only to confirm an alarm — which is rare, and where being right
# matters more than being fast. Verified against `git config core.bare` across
# a normal checkout, bare=true, bare absent, and a linked worktree (where .git
# is a pointer file and the config lives in the common dir): 5/5 agree.
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

# Read core.bare out of .git/config with builtins only — no subprocess.
# Prints the value, "absent" when the key is not set, or "UNKNOWN" when the
# config cannot be located (not a repo, unreadable). Handles a linked worktree,
# where .git is a `gitdir:` pointer file and the shared config lives in the
# common dir rather than under worktrees/<name>/.
_fast_core_bare() {
  local gitdir cfg section="" line key val
  if [ -d "$REPO/.git" ]; then
    gitdir="$REPO/.git"
  elif [ -f "$REPO/.git" ]; then
    gitdir="$(sed -n 's/^gitdir: //p' "$REPO/.git" 2>/dev/null)"
    [ -n "$gitdir" ] || { echo "UNKNOWN"; return; }
    case "$gitdir" in */worktrees/*) gitdir="${gitdir%/worktrees/*}" ;; esac
  else
    echo "UNKNOWN"; return
  fi
  cfg="$gitdir/config"
  [ -r "$cfg" ] || { echo "UNKNOWN"; return; }
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%[;#]*}"
    if [ "${line:0:1}" = "[" ]; then
      section="${line#\[}"; section="${section%%]*}"; section="${section%% *}"
      continue
    fi
    case "$line" in
      *=*)
        key="${line%%=*}"; val="${line#*=}"
        key="${key//[[:space:]]/}"; val="${val//[[:space:]]/}"
        if [ "$section" = "core" ] && [ "$key" = "bare" ]; then
          printf '%s\n' "$val"; return
        fi
        ;;
    esac
  done < "$cfg"
  echo "absent"
}

FAST="$(_fast_core_bare)"

# Not a repo, or the config is unreadable: nothing to watch, and no reason to
# pay for a git call to confirm an absence.
[ "$FAST" = "UNKNOWN" ] && exit 0

# The overwhelmingly common case. Normalise "absent" to git's own default so
# the state file does not churn between the two spellings.
case "$FAST" in
  false|no|off|0|absent) NOW="false" ;;
  *)
    # Only here — about to tell someone their repo is broken — is the 1.7s
    # `git` call worth it. A false alarm on this is expensive to the reader.
    NOW="$(git -C "$REPO" config core.bare 2>/dev/null || echo "false")"
    ;;
esac

# `read` builtin rather than $(cat ...): a subprocess costs ~106ms here, which
# on the common path is a third of the hook's whole budget.
PREV=""
[ -r "$STATE" ] && read -r PREV < "$STATE" 2>/dev/null

if [ "$NOW" != "$PREV" ]; then
  # Only on a transition do we pay for stdin + jq (109ms). Parsing the payload
  # on every call would put that cost back on the common path the fast read
  # above exists to keep free.
  PAYLOAD="$(cat 2>/dev/null || true)"
  if command -v jq >/dev/null 2>&1; then
    # tr before head: a multi-line command would otherwise embed newlines and
    # break the one-line-per-transition format this log is meant to be grepped
    # as. Observed on the first live firing — the suspect was a 3-line heredoc.
    CMD="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.command // "?"' 2>/dev/null \
          | tr '\n\t' '  ' | head -c 200)"
  else
    CMD="(jq unavailable)"
  fi

  mkdir -p "$LOG_DIR" 2>/dev/null || exit 0
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
