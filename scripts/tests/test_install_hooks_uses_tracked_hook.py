#!/usr/bin/env python3
"""scripts/install-hooks.sh must install the tracked hook, not a copy of it.

The installer used to embed its own copy of the pre-commit hook as a heredoc and
write it over .githooks/pre-commit. The copy drifted: the step 11
quality_floor_posts exemption and step 19 (excerpt promises) were added to
.githooks/pre-commit only, so re-running the installer would have reverted both
and left a tracked file modified. On a checkout installed before core.hooksPath
was set, git never read .githooks/ at all and kept running an old copy in
.git/hooks/pre-commit, so none of the later gates ran locally.

The installer now only sets core.hooksPath=.githooks. This file pins that:

* statically, the installer carries no hook text;
* in a throwaway repo, the hook git resolves after installing is the tracked
  file, it runs instead of a stale .git/hooks/pre-commit, the tracked files are
  left byte-identical, and a linked worktree runs its own checked-out copy.

Isolation: every subprocess here runs with all GIT_* variables removed, HOME in
a temp dir and cwd inside tmp_path. Git exports GIT_DIR and GIT_INDEX_FILE to
hooks, so this has to stay safe when pytest itself runs under a hook (see
test_hook_git_env_isolation.py): a leaked GIT_DIR makes `git config` write to the
real repository's shared config. The installer is never run against the real
repository.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts" / "install-hooks.sh"
TRACKED_HOOKS = ROOT / ".githooks"

TRACKED_HOOK = '#!/bin/sh\necho tracked >> "$HOOK_LOG"\n'
STALE_HOOK = '#!/bin/sh\necho stale >> "$HOOK_LOG"\n'


class Sandbox:
    """A throwaway repo plus the scrubbed environment every command in it uses."""

    def __init__(self, base: Path) -> None:
        self.base = base
        home = base / "home"
        home.mkdir()
        self.log = base / "hook.log"
        # No GIT_* (a hook-exported GIT_DIR would point git at the real repo)
        # and no user git config (this machine has a global commit.gpgsign).
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(
            HOME=str(home), XDG_CONFIG_HOME=str(home), HOOK_LOG=str(self.log)
        )
        assert not any(k.startswith("GIT_") for k in self.env)
        self.repo = base / "repo"
        self.repo.mkdir()
        self.git(self.repo, "init", "-q")
        self.git(self.repo, "config", "user.name", "Test")
        self.git(self.repo, "config", "user.email", "test@invalid.local")
        top = Path(self.git(self.repo, "rev-parse", "--show-toplevel")).resolve()
        assert top == self.repo.resolve(), f"sandbox resolved to {top}"

    def run(
        self, cwd: Path, *argv: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        resolved = cwd.resolve()
        assert self.base.resolve() in (resolved, *resolved.parents), (
            f"refusing to run {argv} outside the sandbox: {cwd}"
        )
        return subprocess.run(
            argv, cwd=cwd, env=self.env, capture_output=True, text=True, check=check
        )

    def git(self, cwd: Path, *args: str) -> str:
        return self.run(cwd, "git", *args).stdout.strip()

    def install(self, cwd: Path, shell: str = "sh") -> subprocess.CompletedProcess[str]:
        return self.run(cwd, shell, str(INSTALLER), check=False)

    def commit(self, cwd: Path) -> None:
        self.git(cwd, "commit", "-q", "--allow-empty", "-m", "x")

    def runs(self) -> list[str]:
        """Which hooks ran, in order. Each sentinel hook appends its own label."""
        return self.log.read_text().splitlines() if self.log.exists() else []

    def seed_tracked_hooks(self) -> None:
        """Commit .githooks/ before core.hooksPath exists, so no hook fires."""
        hooks = self.repo / ".githooks"
        hooks.mkdir()
        (hooks / "pre-commit").write_text(TRACKED_HOOK)
        (hooks / "pre-commit").chmod(0o755)
        # git ignores a hook without the executable bit; the installer must fix it.
        (hooks / "pre-push").write_text("#!/bin/sh\nexit 0\n")
        (hooks / "pre-push").chmod(0o644)
        self.git(self.repo, "add", "-A")
        self.git(self.repo, "commit", "-q", "-m", "seed")

    def write_stale_copy(self) -> Path:
        """The copy an old installer left in .git/hooks/ (what actually ran)."""
        hooks = self.repo / ".git" / "hooks"
        hooks.mkdir(exist_ok=True)
        stale = hooks / "pre-commit"
        stale.write_text(STALE_HOOK)
        stale.chmod(0o755)
        return stale


def _code(text: str) -> str:
    """Comment-only lines dropped: the header explains the old heredoc in prose."""
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def test_installer_embeds_no_hook_text():
    text = INSTALLER.read_text(encoding="utf-8")
    code = _code(text)
    assert text.count("#!") == 1, (
        "scripts/install-hooks.sh has a second shebang, which means a hook body is "
        "embedded in it again. The hook lives only in .githooks/; the installer "
        "just sets core.hooksPath."
    )
    assert not re.search(r"<<-?\s*[\"'\\]?\w", code), (
        "scripts/install-hooks.sh contains a here-document. A hook written from "
        "the installer drifts from .githooks/pre-commit and overwrites it on the "
        "next run."
    )
    assert "python3" not in code and "pytest" not in code, (
        "scripts/install-hooks.sh runs gate commands itself, which means hook "
        "logic is embedded in it. Put it in .githooks/pre-commit."
    )
    assert "core.hooksPath" in code and ".githooks" in code, (
        "scripts/install-hooks.sh no longer points core.hooksPath at .githooks, so "
        "git would not run the tracked hooks."
    )


def test_tracked_hooks_are_executable():
    """git skips a non-executable hook with only a hint, so a mode slip means no gates.

    Checks the mode recorded in the index (what fresh clones and new worktrees
    get), not the working-tree bit, and only for the hook files: a stray
    .DS_Store or editor backup in .githooks/ must not fail this.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    listed = subprocess.run(
        ["git", "ls-files", "-s", "--", ".githooks/pre-commit", ".githooks/pre-push"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    # The suite always runs from a git checkout (locally and actions/checkout).
    assert listed.returncode == 0, listed.stderr
    modes = {
        line.split("\t")[1]: line.split()[0] for line in listed.stdout.splitlines()
    }
    assert set(modes) == {".githooks/pre-commit", ".githooks/pre-push"}, modes
    not_executable = sorted(path for path, mode in modes.items() if mode != "100755")
    assert not_executable == [], (
        f"{not_executable} are not 100755 in the index; git would not run them. "
        "Fix with: git update-index --chmod=+x <path>"
    )


@pytest.mark.parametrize("shell", ["sh", "bash"])
def test_installer_makes_git_run_the_tracked_hook(tmp_path, shell):
    if shutil.which(shell) is None:
        pytest.skip(f"{shell} is not installed")
    sb = Sandbox(tmp_path)
    sb.seed_tracked_hooks()
    stale = sb.write_stale_copy()
    hooks_dir = stale.parent
    leftovers = sorted(p.name for p in hooks_dir.iterdir())
    tracked_before = {p.name: p.read_bytes() for p in (sb.repo / ".githooks").iterdir()}

    # Before installing: core.hooksPath is unset, so git runs the stale copy and
    # never looks at .githooks/. This is the state the fix has to get out of.
    sb.commit(sb.repo)
    assert sb.runs() == ["stale"]

    for _ in range(2):  # re-running must be harmless
        result = sb.install(sb.repo, shell)
        assert result.returncode == 0, result.stdout + result.stderr

    assert sb.git(sb.repo, "config", "--get", "core.hooksPath") == ".githooks"
    resolved = sb.git(sb.repo, "rev-parse", "--git-path", "hooks/pre-commit")
    assert (sb.repo / resolved).samefile(sb.repo / ".githooks" / "pre-commit")

    # The tracked files are untouched (an embedded copy would overwrite them) and
    # nothing was written into .git/hooks/.
    tracked_after = {p.name: p.read_bytes() for p in (sb.repo / ".githooks").iterdir()}
    assert tracked_after == tracked_before
    assert sorted(p.name for p in hooks_dir.iterdir()) == leftovers
    assert stale.read_text() == STALE_HOOK
    assert os.access(sb.repo / ".githooks" / "pre-push", os.X_OK)

    # After installing: git runs the tracked hook and no longer the stale copy.
    sb.commit(sb.repo)
    assert sb.runs() == ["stale", "tracked"]


def test_installer_leaves_the_real_tracked_hooks_byte_identical(tmp_path):
    """The old installer rewrote .githooks/pre-commit from its embedded text."""
    sb = Sandbox(tmp_path)
    shutil.copytree(TRACKED_HOOKS, sb.repo / ".githooks")

    result = sb.install(sb.repo)

    assert result.returncode == 0, result.stdout + result.stderr
    for source in TRACKED_HOOKS.iterdir():
        installed = sb.repo / ".githooks" / source.name
        assert installed.read_bytes() == source.read_bytes(), (
            f"the installer changed .githooks/{source.name}; the tracked hook is "
            "the source of truth and must not be rewritten"
        )


def test_linked_worktree_runs_its_own_checked_out_hook(tmp_path):
    sb = Sandbox(tmp_path)
    sb.seed_tracked_hooks()
    linked = tmp_path / "linked"
    sb.git(sb.repo, "worktree", "add", "-q", "-b", "linked", str(linked))

    # Installing from a linked worktree writes the shared repo config.
    result = sb.install(linked)
    assert result.returncode == 0, result.stdout + result.stderr
    assert sb.git(sb.repo, "config", "--get", "core.hooksPath") == ".githooks"

    # Give the linked worktree a different version of the hook. A symlink or copy
    # in the shared .git/hooks/ would run the main checkout's version for both.
    (linked / ".githooks" / "pre-commit").write_text(
        '#!/bin/sh\necho tracked-linked >> "$HOOK_LOG"\n'
    )
    sb.commit(linked)
    sb.commit(sb.repo)
    assert sb.runs() == ["tracked-linked", "tracked"]

    for tree in (sb.repo, linked):
        resolved = sb.git(tree, "rev-parse", "--git-path", "hooks/pre-commit")
        assert (tree / resolved).samefile(tree / ".githooks" / "pre-commit")


def test_installer_refuses_when_the_tracked_pre_commit_is_missing(tmp_path):
    """core.hooksPath at a directory without the hook would switch every hook off."""
    sb = Sandbox(tmp_path)

    result = sb.install(sb.repo)

    assert result.returncode != 0
    assert ".githooks/pre-commit" in result.stderr
    unset = sb.run(sb.repo, "git", "config", "--get", "core.hooksPath", check=False)
    assert unset.returncode == 1 and unset.stdout == ""
