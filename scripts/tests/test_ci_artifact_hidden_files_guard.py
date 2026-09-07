#!/usr/bin/env python3
"""CI config guard: a dot-path artifact upload must set include-hidden-files.

``actions/upload-artifact`` v4+ excludes hidden files unless
``include-hidden-files: true`` is set, and a leading-dot path segment makes
everything under it hidden. The step then uploads nothing and **still reports
success**, so the only signal is one informational line in a green job's log.

Measured 2026-09-07, three live instances across two workflows:

- ``ai-blogwatcher.yml`` / "Upload rejected draft" — run 34074671646 rejected a
  truncated digest, ``auto_publish_news.py`` copied the draft to
  ``.digest-gate-failure/`` exactly as designed, and the upload logged
  ``include-hidden-files: false`` / ``No files were found with the provided
  path`` for 0 artifacts. The diagnostic added after the 2026-08-27 truncation
  incident — whose sole purpose was to preserve that draft — had never once
  produced an artifact, so the 09-07 draft was destroyed the same way.
- ``gsc-queue-refresh.yml`` / two ``.omc/**`` uploads — runs 31367562521,
  31300312257, 31245244315 and 31157540151 all reported **success with 0
  artifacts**. ``if-no-files-found: warn`` did fire; a warning inside a green
  job is not read.

Direction: presence. A dot path requires the flag; non-dot paths are
unconstrained (the default is correct for them). Repo-wide, not per-file — the
gsc pair is why: fixing only the workflow that happened to be under
investigation would have left two identical holes open.

Notes for the next author
-------------------------
This parses YAML rather than line-scanning. That is deliberate: an
indentation/comment-based extractor is the usual source of vacuous CI guards,
and this repo already depends on PyYAML in
``test_ci_blogwatcher_selfheal_reverify_guard.py``, so no dependency is added.

The collector must NOT filter steps by ``include-hidden-files`` — that is the
property under assertion, and pre-filtering on it would make every violation
invisible while the suite stayed green.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, NamedTuple

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

# Lower bound on collected upload steps. A parser that silently matched nothing
# would otherwise report a clean pass. 9 were present on 2026-09-07; keep the
# floor below that so ordinary churn does not trip it.
MIN_EXPECTED_UPLOAD_STEPS = 6


class UploadStep(NamedTuple):
    workflow: str
    job: str
    step: str
    path: str
    include_hidden: Any


def _has_dot_segment(path: str) -> bool:
    """True when any segment of any line of ``path`` starts with a dot.

    ``path`` is multi-line in several workflows (one glob per line), and only
    one of those lines needs to be hidden for the upload to lose files. ``.``
    and ``..`` are ordinary relative-path segments, not hidden names.
    """
    for line in path.splitlines():
        for segment in line.strip().replace("\\", "/").split("/"):
            if segment.startswith(".") and segment not in (".", ".."):
                return True
    return False


def _upload_steps(directory: Path | None = None) -> list[UploadStep]:
    """Every actions/upload-artifact step in ``directory``.

    Selection is on `uses:` alone. Do not narrow it by `with:` contents.

    ``directory`` resolves at CALL time, not at def time. Writing
    ``directory: Path = WORKFLOW_DIR`` binds the default once when this module
    is imported, so a mutation probe that monkeypatches ``WORKFLOW_DIR`` would
    keep reading the real workflows — the control would pass, every mutation
    would report MISSED, and the guard would look untestable rather than
    unverified.
    """
    directory = WORKFLOW_DIR if directory is None else directory
    found: list[UploadStep] = []
    files = sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml"))
    for wf in files:
        doc = yaml.safe_load(wf.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            continue
        for job_name, job in (doc.get("jobs") or {}).items():
            if not isinstance(job, dict):
                continue
            for step in job.get("steps") or []:
                if not isinstance(step, dict):
                    continue
                if "actions/upload-artifact" not in str(step.get("uses") or ""):
                    continue
                with_block = step.get("with") or {}
                found.append(
                    UploadStep(
                        workflow=wf.name,
                        job=str(job_name),
                        step=str(step.get("name") or "(unnamed)"),
                        path=str(with_block.get("path") or ""),
                        include_hidden=with_block.get("include-hidden-files"),
                    )
                )
    return found


def test_workflow_dir_exists():
    """Canary: a moved workflow dir must fail loudly, not vacuously pass."""
    assert WORKFLOW_DIR.is_dir(), f"{WORKFLOW_DIR} not found"


def test_scanner_finds_the_upload_steps():
    """A collector matching nothing would make every assertion below vacuous."""
    steps = _upload_steps()
    assert len(steps) >= MIN_EXPECTED_UPLOAD_STEPS, (
        f"only {len(steps)} upload-artifact step(s) found under {WORKFLOW_DIR}. "
        "If uploads were genuinely removed, lower MIN_EXPECTED_UPLOAD_STEPS; "
        "otherwise the YAML walk is broken and the guard proves nothing."
    )


def test_dot_path_uploads_include_hidden_files():
    """The invariant. Presence-direction: dot path => flag must be true."""
    violations = [
        f"{s.workflow} :: {s.job} :: {s.step} -> path={s.path!r} "
        f"include-hidden-files={s.include_hidden!r}"
        for s in _upload_steps()
        if _has_dot_segment(s.path) and s.include_hidden is not True
    ]
    assert not violations, (
        "upload-artifact step(s) point at a dot-path without "
        "`include-hidden-files: true`. v4+ drops hidden files and the step still "
        "reports success, so the artifact is silently empty:\n  "
        + "\n  ".join(violations)
        + "\n\nAdd `include-hidden-files: true`, or move the path out of a "
        "dot-directory. Do not 'fix' this by relaxing if-no-files-found."
    )


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (".digest-gate-failure/", True),
        (".omc/state/gsc-queue.json", True),
        (".omc/reports/gsc-daily-action-*.md", True),
        ("reports/svg-lint.json", False),
        ("assets/images/*.svg", False),
        ("./reports/", False),  # a bare "." segment is not a hidden name
        ("../out/", False),
        ("reports/\n.digest-gate-failure/", True),  # multi-line: one is enough
        ("", False),
    ],
)
def test_has_dot_segment_classifies_paths(path: str, expected: bool):
    """Pins the classifier itself — the guard is only as good as this predicate."""
    assert _has_dot_segment(path) is expected
