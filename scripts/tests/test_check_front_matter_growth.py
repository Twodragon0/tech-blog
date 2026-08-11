#!/usr/bin/env python3
"""Tests for scripts/check_front_matter_growth.py.

The gate this replaced was an inline YAML snippet warning above 1,000 chars — a
threshold 261 of 261 posts violated, in a step that could not exit non-zero. Being
untestable inline is part of how it rotted unnoticed, so the replacement lives in a
script and these tests cover both directions: it must FAIL on growth and on breaching
the cap, and it must PASS on legacy size, shrinkage, and new posts under the cap.
"""

from __future__ import annotations

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


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


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
    (repo / "_posts" / name).write_text(f"---\nt: {filler}\n---\nbody\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", message)


@pytest.fixture()
def script_in_repo(git_repo: Path) -> Path:
    """Copy the script in so its REPO_ROOT resolves to the temp repo."""
    dest = git_repo / "scripts"
    dest.mkdir(exist_ok=True)
    (dest / SCRIPT.name).write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    return dest / SCRIPT.name


def test_growth_fails(git_repo: Path, script_in_repo: Path):
    _commit_post(git_repo, "a.md", 200, "base")
    _git(git_repo, "branch", "-M", "base")
    _git(git_repo, "checkout", "-qb", "topic")
    _commit_post(git_repo, "a.md", 400, "grow")
    proc = subprocess.run(
        [sys.executable, str(script_in_repo), "--changed", "base"],
        cwd=git_repo, capture_output=True, text=True,
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
        cwd=git_repo, capture_output=True, text=True,
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
    path.write_text(path.read_text(encoding="utf-8") + "\nmore body\n", encoding="utf-8")
    _git(git_repo, "add", "-A")
    _git(git_repo, "commit", "-qm", "body edit")
    proc = subprocess.run(
        [sys.executable, str(script_in_repo), "--changed", "base"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_new_post_is_noted_not_failed(git_repo: Path, script_in_repo: Path):
    _commit_post(git_repo, "a.md", 200, "base")
    _git(git_repo, "branch", "-M", "base")
    _git(git_repo, "checkout", "-qb", "topic")
    _commit_post(git_repo, "b.md", 300, "new post")
    proc = subprocess.run(
        [sys.executable, str(script_in_repo), "--changed", "base"],
        cwd=git_repo, capture_output=True, text=True,
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
        [sys.executable, str(script_in_repo), "--changed", "base", "--max-chars", "200"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "exceeds the 200-char cap" in proc.stdout


def test_unresolvable_base_is_an_error_not_a_pass(git_repo: Path, script_in_repo: Path):
    """The whole point: a broken diff must never read as "nothing changed"."""
    _commit_post(git_repo, "a.md", 100, "base")
    proc = subprocess.run(
        [sys.executable, str(script_in_repo), "--changed", "no-such-ref"],
        cwd=git_repo, capture_output=True, text=True,
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
