#!/bin/sh
# Install project git hooks.
#
# The hooks live in .githooks/ (tracked in git) and git runs them in place. This
# script only sets core.hooksPath=.githooks; it embeds no hook text. A copy goes
# stale: the copy in .git/hooks/ kept running while every gate added after it
# never ran locally, and the pre-commit text that used to be embedded here had
# drifted from .githooks/pre-commit as well, so re-running the installer would
# have reverted it. scripts/tests/test_install_hooks_uses_tracked_hook.py fails
# if hook text is embedded here again.
#
# Run once per clone:  bash scripts/install-hooks.sh
# Editing .githooks/* needs no re-run.
#
# Linked worktrees: core.hooksPath is stored in the shared repo config and the
# relative path resolves against the root of the worktree that runs the hook, so
# every worktree runs its own checked-out .githooks/. Copying or symlinking into
# .git/hooks/ does not do that: that directory is shared, and a relative symlink
# in it resolves into the main checkout. If core.hooksPath is unavailable
# (git < 2.9), the fallback is a stub in .git/hooks/<hook> that contains only
#   exec "$(git rev-parse --show-toplevel)/.githooks/<hook>" "$@"

set -e
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Pointing core.hooksPath at a directory without a pre-commit would switch every
# hook off without a word, so check before touching the config.
if [ ! -f "$REPO_ROOT/.githooks/pre-commit" ]; then
  echo "[install-hooks] ERROR: $REPO_ROOT/.githooks/pre-commit not found; core.hooksPath left unchanged." >&2
  exit 1
fi

# git ignores a hook that is not executable. Done before the config write so a
# failure leaves core.hooksPath untouched, and only for the hook files: a
# non-hook file added to .githooks/ later must not pick up the bit.
for hook in pre-commit pre-push; do
  if [ -f "$REPO_ROOT/.githooks/$hook" ]; then
    chmod +x "$REPO_ROOT/.githooks/$hook"
  fi
done

previous="$(git -C "$REPO_ROOT" config --get core.hooksPath || true)"
if [ -n "$previous" ] && [ "$previous" != ".githooks" ]; then
  echo "[install-hooks] Replacing core.hooksPath=$previous"
fi
echo "[install-hooks] Configuring core.hooksPath=.githooks ..."
git -C "$REPO_ROOT" config core.hooksPath .githooks

echo "[install-hooks] Done."
echo ""
echo "  pre-commit : $REPO_ROOT/.githooks/pre-commit (via core.hooksPath)"
if [ -f "$REPO_ROOT/.githooks/pre-push" ]; then
  echo "  pre-push   : $REPO_ROOT/.githooks/pre-push (via core.hooksPath)"
fi
echo ""
echo "  Emergency push bypass: SKIP_VARIANT_CHECK=1 git push"
echo "  Disable auto-commit of raster variants: TECH_BLOG_NO_AUTO_COMMIT=1"
