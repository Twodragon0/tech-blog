"""conftest.py keeps every test's git commands inside that test's own repo.

Git exports GIT_DIR and GIT_INDEX_FILE to the hooks it runs, and in a linked
worktree GIT_DIR is an absolute path into the shared .git. When the pre-commit
hook ran this suite from one, the fixtures' git commands acted on the
developer's checkout: fixture posts were staged and committed there, and the
shared .git/config was left with core.bare=true and the fixtures' user.name
and user.email. An autouse fixture in conftest.py now removes those variables
before every test.

The test below rebuilds that environment around a throwaway decoy repository.
Nothing in this file points at the real checkout.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROBE = Path(__file__).parent / "fixtures" / "git_env_probe.py"

# Keeps the developer's global git config out of the decoy: no hooks, no commit
# signing, and no detached auto-maintenance that could still be writing into
# the decoy when it is snapshotted. CI runners have no identity, so set one.
_DECOY_CONFIG = (
    "core.hooksPath=/dev/null",
    "commit.gpgsign=false",
    "maintenance.auto=false",
    "user.name=decoy",
    "user.email=decoy@invalid.local",
)


def _git(cwd: Path, env: dict[str, str], *args: str) -> str:
    pinned = [arg for setting in _DECOY_CONFIG for arg in ("-c", setting)]
    return subprocess.run(
        ["git", *pinned, *args],
        cwd=cwd,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _files(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()
    }


def _changed(before: dict[str, bytes], after: dict[str, bytes]) -> list[str]:
    return sorted(
        k for k in before.keys() | after.keys() if before.get(k) != after.get(k)
    )


def _run_probe(
    tmp_path: Path, name: str, env: dict[str, str], *extra: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            f"--basetemp={tmp_path / name}",
            *extra,
            str(PROBE),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )


def test_leaked_hook_git_env_cannot_reach_another_repository(tmp_path: Path) -> None:
    # Every GIT_* removed, so even with conftest.py broken this test's own git
    # commands cannot be aimed at the real checkout.
    clean = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

    # The decoy: a repository with a linked worktree, the shape of the checkout
    # the hook ran in.
    decoy = tmp_path / "decoy"
    main, linked = decoy / "main", decoy / "linked"
    main.mkdir(parents=True)
    _git(main, clean, "init", "-q")
    _git(main, clean, "commit", "-q", "--allow-empty", "-m", "decoy")
    _git(main, clean, "worktree", "add", "-q", "-b", "linked", str(linked))
    gitdir = _git(linked, clean, "rev-parse", "--absolute-git-dir")

    # What git exports to a pre-commit hook running in that worktree.
    leaked = {**clean, "GIT_DIR": gitdir, "GIT_INDEX_FILE": f"{gitdir}/index"}
    before = _files(decoy)

    run = _run_probe(tmp_path, "with-conftest", leaked)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "1 passed" in run.stdout, run.stdout
    changed = _changed(before, _files(decoy))
    assert not changed, f"a test's git commands wrote into the decoy: {changed}"

    # Control: the same run without conftest.py does reach the decoy, so the
    # assertions above measure the fixture, not an environment git ignores.
    control = _run_probe(tmp_path, "without-conftest", leaked, "--noconftest")
    assert control.returncode != 0, control.stdout
    assert _changed(before, _files(decoy)), "the leak no longer reaches the decoy"
