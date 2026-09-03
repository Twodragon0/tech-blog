#!/usr/bin/env python3
"""Tests for scripts/check_front_matter_growth.py.

The gate this replaced was an inline YAML snippet warning above 1,000 chars — a
threshold 261 of 261 posts violated, in a step that could not exit non-zero. Being
untestable inline is part of how it rotted unnoticed, so the replacement lives in a
script and these tests cover both directions: it must FAIL on growth and on breaching
the cap, and it must PASS on legacy size, shrinkage, and new posts under the cap.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_front_matter_growth import (  # noqa: E402
    DEFAULT_MAX_CHARS,
    check,
    front_matter_len,
    main,
)

SCRIPT = REPO_ROOT / "scripts" / "check_front_matter_growth.py"


# ---------------------------------------------------------------------------
# front_matter_len
# ---------------------------------------------------------------------------


def test_front_matter_len_counts_inner_block_only():
    text = "---\ntitle: hi\n---\nbody text here"
    assert front_matter_len(text) == len("title: hi")


def test_front_matter_len_none_when_absent():
    assert front_matter_len("no front matter at all") is None


def test_front_matter_len_ignores_later_triple_dashes():
    text = "---\na: 1\n---\nbody\n---\nnot front matter\n---\n"
    assert front_matter_len(text) == len("a: 1")


# ---------------------------------------------------------------------------
# check() — the pure decision function
# ---------------------------------------------------------------------------


def _write(tmp_path: Path, name: str, fm_chars: int) -> str:
    """Create a post whose front matter is exactly `fm_chars` long."""
    posts = tmp_path / "_posts"
    posts.mkdir(exist_ok=True)
    filler = "x" * max(0, fm_chars - len("t: "))
    body = f"---\nt: {filler}\n---\nbody\n"
    (posts / name).write_text(body, encoding="utf-8")
    return str((posts / name).relative_to(tmp_path))


def test_check_flags_missing_front_matter(tmp_path, monkeypatch):
    import check_front_matter_growth as mod

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    posts = tmp_path / "_posts"
    posts.mkdir()
    (posts / "a.md").write_text("no front matter", encoding="utf-8")
    violations, _ = mod.check(None, ["_posts/a.md"], DEFAULT_MAX_CHARS)
    assert any("no front matter block" in v for v in violations)


def test_check_flags_cap_breach(tmp_path, monkeypatch):
    import check_front_matter_growth as mod

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    rel = _write(tmp_path, "a.md", 500)
    violations, _ = mod.check(None, [rel], 100)
    assert any("exceeds the 100-char cap" in v for v in violations)


def test_check_passes_under_cap_without_baseline(tmp_path, monkeypatch):
    import check_front_matter_growth as mod

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    rel = _write(tmp_path, "a.md", 50)
    violations, _ = mod.check(None, [rel], 100)
    assert violations == []


def test_check_notes_deleted_file_without_failing(tmp_path, monkeypatch):
    import check_front_matter_growth as mod

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    violations, notes = mod.check(None, ["_posts/gone.md"], DEFAULT_MAX_CHARS)
    assert violations == []
    assert any("deleted or moved" in n for n in notes)


# ---------------------------------------------------------------------------
# Ratchet behaviour against a real git baseline
# ---------------------------------------------------------------------------


def _clean_env() -> dict[str, str]:
    """The caller's environment with every ``GIT_*`` variable removed.

    Load-bearing, not hygiene. Git exports ``GIT_INDEX_FILE`` and ``GIT_DIR`` to
    hooks, so when the pre-commit hook runs pytest, anything this file spawns
    inherits them and operates on the *real* repository instead of the throwaway
    one under ``tmp_path``. Both directions were measured 2026-09-02:

    * the fixtures' ``git add -A`` wrote to the caller's index, taking it from
      3,349 entries to 2 and leaving ``_posts/a.md`` pointing at a blob that the
      temp dir's deletion made unreachable — every later commit then died with
      ``fatal: unable to read ca41b6a1...``;
    * the checker invocations below resolved ``GIT_DIR`` to the outer repo, so
      ``git diff`` against the fixture's ``base`` ref exited 128 and
      ``test_growth_fails`` failed — but only under the hook, which is why the
      same command passed when run by hand.

    Recovery from the first is ``git reset`` (mixed): it rebuilds the index from
    HEAD and leaves the working tree alone.
    """
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(repo: Path, *args: str) -> None:
    """Run git against the throwaway repo, with the caller's git env stripped.

    `env=` is load-bearing, not hygiene. Git exports `GIT_INDEX_FILE` (and
    `GIT_DIR`) to hooks, so when the pre-commit hook runs pytest these fixtures
    inherit them: `cwd=repo` still resolves the object store to the temp repo,
    but `git add -A` writes the index to the *caller's* `GIT_INDEX_FILE`.

    Measured 2026-09-02: running this file with `GIT_INDEX_FILE` pointed at a
    copy of the real index took it from **3,349 entries to 2** — `add -A` writes
    a complete index for the temp repo, so afterwards every tracked path in the
    real tree reads as deleted. The temp dir is then removed, leaving an entry
    for `_posts/a.md` whose blob is unreachable, and the next commit dies with
    `fatal: unable to read ca41b6a1...`. Recovery is `git reset` (mixed).
    """
    subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, env=_clean_env()
    )


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "_posts").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    return repo


def _commit_post(repo: Path, name: str, fm_chars: int, message: str) -> None:
    filler = "x" * max(0, fm_chars - len("t: "))
    (repo / "_posts" / name).write_text(
        f"---\nt: {filler}\n---\nbody\n", encoding="utf-8"
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", message)


@pytest.fixture()
def script_in_repo(git_repo: Path) -> Path:
    """Copy the script in so its REPO_ROOT resolves to the temp repo."""
    dest = git_repo / "scripts"
    dest.mkdir(exist_ok=True)
    (dest / SCRIPT.name).write_text(
        SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    return dest / SCRIPT.name


def test_growth_fails(git_repo: Path, script_in_repo: Path):
    _commit_post(git_repo, "a.md", 200, "base")
    _git(git_repo, "branch", "-M", "base")
    _git(git_repo, "checkout", "-qb", "topic")
    _commit_post(git_repo, "a.md", 400, "grow")
    proc = subprocess.run(
        [sys.executable, str(script_in_repo), "--changed", "base"],
        cwd=git_repo,
        env=_clean_env(),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "grew 200 -> 400" in proc.stdout


def test_shrinkage_passes(git_repo: Path, script_in_repo: Path):
    _commit_post(git_repo, "a.md", 400, "base")
    _git(git_repo, "branch", "-M", "base")
    _git(git_repo, "checkout", "-qb", "topic")
    _commit_post(git_repo, "a.md", 200, "shrink")
    proc = subprocess.run(
        [sys.executable, str(script_in_repo), "--changed", "base"],
        cwd=git_repo,
        env=_clean_env(),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "shrank 400 -> 200" in proc.stdout


def test_legacy_size_is_grandfathered(git_repo: Path, script_in_repo: Path):
    """An oversized post that does not change must not fail — that is the ratchet."""
    _commit_post(git_repo, "a.md", 2500, "base")
    _git(git_repo, "branch", "-M", "base")
    _git(git_repo, "checkout", "-qb", "topic")
    # touch the body only
    path = git_repo / "_posts" / "a.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nmore body\n", encoding="utf-8"
    )
    _git(git_repo, "add", "-A")
    _git(git_repo, "commit", "-qm", "body edit")
    proc = subprocess.run(
        [sys.executable, str(script_in_repo), "--changed", "base"],
        cwd=git_repo,
        env=_clean_env(),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_new_post_is_noted_not_failed(git_repo: Path, script_in_repo: Path):
    _commit_post(git_repo, "a.md", 200, "base")
    _git(git_repo, "branch", "-M", "base")
    _git(git_repo, "checkout", "-qb", "topic")
    _commit_post(git_repo, "b.md", 300, "new post")
    proc = subprocess.run(
        [sys.executable, str(script_in_repo), "--changed", "base"],
        cwd=git_repo,
        env=_clean_env(),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "new post" in proc.stdout


def test_new_post_over_cap_fails(git_repo: Path, script_in_repo: Path):
    """New posts have no baseline, so the absolute cap is what bounds them."""
    _commit_post(git_repo, "a.md", 100, "base")
    _git(git_repo, "branch", "-M", "base")
    _git(git_repo, "checkout", "-qb", "topic")
    _commit_post(git_repo, "b.md", 500, "huge new post")
    proc = subprocess.run(
        [
            sys.executable,
            str(script_in_repo),
            "--changed",
            "base",
            "--max-chars",
            "200",
        ],
        cwd=git_repo,
        env=_clean_env(),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "exceeds the 200-char cap" in proc.stdout


def test_unresolvable_base_is_an_error_not_a_pass(git_repo: Path, script_in_repo: Path):
    """The whole point: a broken diff must never read as "nothing changed"."""
    _commit_post(git_repo, "a.md", 100, "base")
    proc = subprocess.run(
        [sys.executable, str(script_in_repo), "--changed", "no-such-ref"],
        cwd=git_repo,
        env=_clean_env(),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "Refusing to report 'no changes'" in proc.stderr


# ---------------------------------------------------------------------------
# Live corpus canary
# ---------------------------------------------------------------------------


def test_live_corpus_is_under_the_cap():
    """If this ever fails, the cap needs a decision — not a silent bump."""
    assert main(["--all"]) == 0, (
        "some post now exceeds the front-matter cap. Trim it, or raise --max-chars "
        "deliberately and say why in the same PR."
    )
