#!/usr/bin/env python3
"""The digest quality gate must preserve the draft it rejects.

Deleting a rejected draft is correct — a truncated post must not reach the
corpus. Deleting it *and* keeping no copy is what made the 2026-08-27 cron
failure unreproducible: the run reported a single 60-character fragment,

    L410 TRUNCATED: ...정부 복지에 의

and by the time anyone looked the file was gone, so "did our truncation helpers
produce this, or was the model's output already cut?" could not be answered.

Two invariants here, and the second is the one that rots silently:

1. The draft and the issue list are written before the unlink.
2. The directory the script writes to is the directory the workflow uploads.
   Change one and the artifact is quietly empty on the one run that needed it —
   `if-no-files-found: ignore` means the job will not complain either.
"""

from __future__ import annotations

import re
from pathlib import Path

import auto_publish_news
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"
GITIGNORE = REPO_ROOT / ".gitignore"

STEP_NAME = "Upload rejected draft"
DEFAULT_DIR = ".digest-gate-failure"


# --------------------------------------------------------------------------
# The preservation helper
# --------------------------------------------------------------------------
def test_draft_and_issues_are_written(tmp_path, monkeypatch):
    post = tmp_path / "2026-08-27-Tech_Security_Weekly_Digest.md"
    post.write_text("---\ntitle: x\n---\n| a | 정부 복지에 의 |\n", encoding="utf-8")
    dest = tmp_path / "diag"
    monkeypatch.setenv("DIGEST_GATE_FAILURE_DIR", str(dest))

    saved = auto_publish_news._preserve_rejected_post(post, ["L410 TRUNCATED: ...의"])

    assert saved is not None and saved.is_file()
    assert saved.read_text(encoding="utf-8") == post.read_text(encoding="utf-8"), (
        "the preserved copy differs from the rejected draft"
    )
    issues = dest / "2026-08-27-Tech_Security_Weekly_Digest.issues.txt"
    assert issues.is_file()
    assert "L410 TRUNCATED" in issues.read_text(encoding="utf-8")


def test_preservation_happens_before_the_unlink(tmp_path, monkeypatch):
    """Order matters: reading a deleted file yields nothing to preserve."""
    post = tmp_path / "2026-08-27-Digest.md"
    post.write_text("body\n", encoding="utf-8")
    dest = tmp_path / "diag"
    monkeypatch.setenv("DIGEST_GATE_FAILURE_DIR", str(dest))

    saved = auto_publish_news._preserve_rejected_post(post, ["issue"])
    post.unlink()  # what the caller does next

    assert saved.is_file() and saved.read_text(encoding="utf-8") == "body\n"


def test_failure_to_preserve_does_not_raise(tmp_path, monkeypatch):
    """Best-effort: a diagnostics problem must not replace the real error."""
    missing = tmp_path / "gone.md"  # never created -> read_text raises OSError
    monkeypatch.setenv("DIGEST_GATE_FAILURE_DIR", str(tmp_path / "diag"))
    assert auto_publish_news._preserve_rejected_post(missing, ["issue"]) is None


def test_default_directory_is_used_when_env_is_unset(tmp_path, monkeypatch):
    post = tmp_path / "p.md"
    post.write_text("x\n", encoding="utf-8")
    monkeypatch.delenv("DIGEST_GATE_FAILURE_DIR", raising=False)
    monkeypatch.chdir(tmp_path)

    saved = auto_publish_news._preserve_rejected_post(post, [])
    assert saved.parent.name == DEFAULT_DIR, (
        f"default directory is {saved.parent.name!r}; the workflow's `path:` is "
        f"pinned to {DEFAULT_DIR!r} by test_workflow_uploads_the_directory_the_script_writes"
    )


def test_call_site_preserves_before_it_unlinks():
    """Order in the source, not just in the helper.

    The two tests above exercise `_preserve_rejected_post` directly, so they
    stay green even if the call is moved below `post_path.unlink(...)` — at
    which point it preserves nothing and the artifact is an empty file. Only
    reading the call site catches that.
    """
    source = (REPO_ROOT / "scripts" / "auto_publish_news.py").read_text(
        encoding="utf-8"
    )
    # Indent-anchored so the `def _preserve_rejected_post(post_path...)` line —
    # which sits at column 0 and always precedes the unlink — cannot be mistaken
    # for the call. A plain `.find()` matched the definition instead, and this
    # test passed with the call moved below the unlink: vacuous, and it reported
    # as a healthy guard until a mutation probe said otherwise.
    # `post_path` is NOT required on the same line: ruff wraps a call whose
    # argument list is long, and requiring adjacency made this guard miss the
    # post-quality gate's multi-line call entirely — reporting "1 preserve but
    # 2 unlinks", i.e. a real gate looked like a missing one. The indent anchor
    # is what still excludes the column-0 `def`, which is the vacuity this
    # pattern exists to prevent.
    calls = [
        m.start()
        for m in re.finditer(r"^[ \t]+_preserve_rejected_post\(", source, re.M)
    ]
    unlinks = [
        m.start()
        for m in re.finditer(
            r"^[ \t]+post_path\.unlink\(missing_ok=True\)", source, re.M
        )
    ]
    # One preserve/unlink pair per blocking gate. There were two gates from
    # 2026-09-08, when the post-quality gate was promoted from advisory, so
    # asserting "exactly one" would now fail for a correct publisher. What must
    # hold is that EVERY unlink has a preserve ahead of it — checked pairwise in
    # source order rather than by count alone, so a second unlink cannot borrow
    # the first gate's preserve.
    assert len(calls) == len(unlinks), (
        f"{len(calls)} _preserve_rejected_post call(s) but {len(unlinks)} "
        "unlink(s) — one of the blocking gates deletes the draft without "
        "preserving it, and its artifact will be empty."
    )
    assert calls, "no gate preserves the draft before deleting it"
    for i, (preserve, unlink) in enumerate(zip(calls, unlinks)):
        assert preserve < unlink, (
            f"pair {i}: _preserve_rejected_post is called after "
            "post_path.unlink(), so it copies a file that no longer exists and "
            "the artifact is empty."
        )
    # And the pairs must not interleave: preserve[i] < unlink[i] < preserve[i+1].
    for i in range(len(unlinks) - 1):
        assert unlinks[i] < calls[i + 1], (
            f"gate {i}'s unlink runs after gate {i + 1}'s preserve; the pairing "
            "above is then meaningless"
        )


# --------------------------------------------------------------------------
# CI wiring
# --------------------------------------------------------------------------
def _upload_step() -> dict:
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    steps = doc["jobs"]["auto-publish"]["steps"]
    matches = [s for s in steps if STEP_NAME in (s.get("name") or "")]
    if len(matches) != 1:
        pytest.fail(f"expected exactly one {STEP_NAME!r} step, found {len(matches)}")
    return matches[0]


def test_workflow_uploads_the_directory_the_script_writes():
    """The lockstep that decides whether the artifact has anything in it."""
    path = str(_upload_step()["with"]["path"]).rstrip("/")
    assert path == DEFAULT_DIR, (
        f"the workflow uploads {path!r} but the script writes to {DEFAULT_DIR!r}. "
        "With `if-no-files-found: ignore` this mismatch produces an empty "
        "artifact and a green step on exactly the run that needed the evidence."
    )


def test_upload_runs_on_failure():
    step = _upload_step()
    assert step.get("if") == "failure()", (
        f"the upload condition is {step.get('if')!r}. It must be failure(): the "
        "gate only rejects on a failing run, and always() would warn about a "
        "missing directory on every healthy one."
    )


def test_upload_action_is_sha_pinned():
    uses = _upload_step()["uses"]
    assert re.fullmatch(r"actions/upload-artifact@[0-9a-f]{40}", uses), (
        f"upload-artifact is not 40-char SHA pinned: {uses!r}"
    )


def test_diagnostics_directory_is_gitignored():
    """The rejected draft is a build artifact, not corpus content."""
    ignored = GITIGNORE.read_text(encoding="utf-8").splitlines()
    assert any(line.strip().rstrip("/") == DEFAULT_DIR for line in ignored), (
        f"{DEFAULT_DIR} is not in .gitignore, so a rejected draft could be "
        "picked up by the auto-commit step and land in the corpus — which is "
        "precisely what the gate deleted it to prevent."
    )
