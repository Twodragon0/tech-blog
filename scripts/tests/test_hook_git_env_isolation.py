"""The linked-worktree hook must not leak caller Git identity into fixtures."""

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_linked_worktree_hook_isolates_fixture_git_commands(tmp_path):
    env = os.environ.copy()
    local_vars = subprocess.check_output(
        ["git", "rev-parse", "--local-env-vars"], cwd=ROOT, text=True
    ).splitlines()
    for key in local_vars:
        env.pop(key, None)
    env.update(
        GIT_AUTHOR_NAME="Test",
        GIT_AUTHOR_EMAIL="test@invalid.local",
        GIT_COMMITTER_NAME="Test",
        GIT_COMMITTER_EMAIL="test@invalid.local",
    )

    def git(cwd, *args):
        return subprocess.check_output(
            ["git", *args], cwd=cwd, env=env, text=True
        ).strip()

    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(
        repo,
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "--allow-empty",
        "-m",
        "initial",
    )
    work = tmp_path / "linked"
    git(repo, "worktree", "add", "-b", "hook-test", str(work))
    scripts = work / "scripts"
    tests = scripts / "tests"
    tests.mkdir(parents=True)
    (scripts / "check_filename_entities.py").write_text("raise SystemExit(0)\n")
    (scripts / "check_svg_precommit.sh").write_text("exit 0\n")
    (tests / "test_fixture.py").write_text("""import os, subprocess
from pathlib import Path

def test_nested_git(tmp_path):
    child = tmp_path / "child"
    child.mkdir()
    def git(*args):
        subprocess.run(["git", *args], cwd=child, check=True, capture_output=True)
    git("init")
    (child / "seed").write_text("fixture only")
    git("add", "seed")
    git("-c", "core.hooksPath=/dev/null", "commit", "-m", "seed")
    git("config", "core.bare", "true")
""")
    bindir = work / ".venv" / "bin"
    bindir.mkdir(parents=True)
    python = bindir / "python3"
    python.write_text(f'#!/bin/sh\nexec {shlex.quote(sys.executable)} "$@"\n')
    python.chmod(0o755)
    hook = work / "pre-commit"
    shutil.copyfile(ROOT / ".githooks" / "pre-commit", hook)
    git(work, "add", "scripts")
    gitdir = Path(git(work, "rev-parse", "--absolute-git-dir"))
    index = gitdir / "index"
    before = (
        git(work, "rev-parse", "HEAD"),
        index.read_bytes(),
        git(work, "config", "core.bare"),
    )
    hook_env = env.copy()
    hook_env.update(
        GIT_DIR=str(gitdir), GIT_WORK_TREE=str(work), GIT_INDEX_FILE=str(index)
    )
    result = subprocess.run(
        ["sh", str(hook)], cwd=work, env=hook_env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 passed" in result.stdout
    assert before == (
        git(work, "rev-parse", "HEAD"),
        index.read_bytes(),
        git(work, "config", "core.bare"),
    )
    assert hook_env["GIT_DIR"] == str(gitdir)


def test_installer_generates_the_same_isolated_pytest_block():
    block = """    unset $(git rev-parse --local-env-vars)
    python3 -m pytest "$REPO_ROOT/scripts/tests/" -x -q 2>&1"""
    assert block in (ROOT / "scripts/install-hooks.sh").read_text()
    assert block in (ROOT / ".githooks/pre-commit").read_text()
