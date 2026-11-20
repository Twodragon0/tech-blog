"""Payload for test_conftest_git_env_isolation.py — deliberately not collected.

The filename does not match ``test_*.py``, so the suite never runs this on its
own. That test runs it in a separate pytest process whose environment carries
a decoy repository's GIT_DIR and GIT_INDEX_FILE, as a pre-commit hook's does.
The steps are the ones this suite's git fixtures take: init, config, add,
commit.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def _git(repo: Path, *args: str) -> str:
    # No env=: this has to inherit whatever conftest.py left in os.environ.
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def test_git_in_a_tmp_repo_stays_in_that_repo(tmp_path: Path) -> None:
    repo = tmp_path / "own"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "probe")
    _git(repo, "config", "user.email", "probe@invalid.local")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "fixture.md").write_text("fixture only\n", encoding="utf-8")
    _git(repo, "add", "fixture.md")
    _git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "fixture")

    git_dir = Path(_git(repo, "rev-parse", "--absolute-git-dir"))
    assert git_dir.resolve() == (repo / ".git").resolve()
    assert _git(repo, "log", "--format=%an %s") == "probe fixture"
