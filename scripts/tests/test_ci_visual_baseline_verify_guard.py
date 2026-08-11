#!/usr/bin/env python3
"""CI regression guard: baseline capture and verify must stay paired and matched.

`visual-baseline-refresh.yml` records the 30 baseline PNGs on every push to main and
**auto-commits** them. Until 2026-08-10 nothing ran `--verify`, so the recording had no
playback: a change to a generator that altered how these covers render would have been
committed as the new truth post-merge with no step having objected. Verifying on the PR
is the only moment both the old and the new render exist.

Two properties make the pair work, and both are easy to break silently:

1. **Verify must exist and must not be soft.** `--verify` is the only consumer of the
   baselines; if it is dropped, or wrapped in `|| true` / `continue-on-error`, capture
   keeps auto-committing and the system is back to recording with no playback.
2. **Both jobs must run on the same runner image.** Both files pin `ubuntu-22.04` and
   say so in comments. librsvg and fontconfig differ across images, so a mismatch
   produces false positives — verified locally: running verify on macOS against these
   Linux-captured baselines reports 30/30 DIFF at a uniform ~1.5 % with an identical
   `max_block=1134px`, a platform delta rather than drift. That is also why this gate
   cannot be validated on a developer machine; CI is its first real test.

Scope note for future readers: `TARGET_SVGS` in the script is a hardcoded 30-cover
list, so a green verify is a canary, not corpus coverage. If that list ever becomes
dynamic, revisit whether `pull_request`-only triggering is still right — the
blogwatcher cron publishes covers by pushing straight to main, which no PR trigger can
observe (see `test_ci_svg_lint_schedule_guard.py`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
VERIFY = WORKFLOWS / "visual-baseline-verify.yml"
REFRESH = WORKFLOWS / "visual-baseline-refresh.yml"
SCRIPT = REPO_ROOT / "scripts" / "svg_visual_baseline.py"
MANIFEST = REPO_ROOT / "tests" / "visual-baselines" / "manifest.json"


def _yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _runs_on(path: Path) -> str:
    jobs = _yaml(path)["jobs"]
    (job,) = jobs.values()
    return job["runs-on"]


def _uncommented(text: str) -> str:
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def test_verify_workflow_exists():
    assert VERIFY.is_file(), (
        f"{VERIFY.name} is gone. Baseline capture auto-commits on main, so without a "
        "verify step a generator change silently becomes the new baseline."
    )


def test_verify_actually_invokes_the_verify_flag():
    body = _uncommented(VERIFY.read_text(encoding="utf-8"))
    assert "svg_visual_baseline.py --verify" in body, (
        "the workflow no longer runs `svg_visual_baseline.py --verify`; it would be a "
        "green tick over nothing"
    )


def test_verify_is_not_soft():
    """A soft verify is the same failure mode this workflow was created to fix."""
    parsed = _yaml(VERIFY)
    (job,) = parsed["jobs"].values()
    assert not job.get("continue-on-error"), "verify job is continue-on-error"
    for step in job["steps"]:
        if "--verify" in (step.get("run") or ""):
            assert not step.get("continue-on-error"), "verify step is continue-on-error"
            assert "|| true" not in step["run"], "verify is wrapped in '|| true'"
            return
    pytest.fail("no step runs --verify")


def test_capture_and_verify_share_the_same_runner():
    """A runner mismatch between capture and verify manufactures false positives."""
    assert _runs_on(VERIFY) == _runs_on(REFRESH), (
        f"verify runs on {_runs_on(VERIFY)} but capture runs on {_runs_on(REFRESH)}. "
        "librsvg/fontconfig differ across images, so every baseline would report a diff "
        "that has nothing to do with the change under review."
    )


def test_runner_is_pinned_not_latest():
    for path in (VERIFY, REFRESH):
        assert _runs_on(path) != "ubuntu-latest", (
            f"{path.name} uses ubuntu-latest. That is a moving target migrating toward "
            "24.04; capture and verify would drift apart on GitHub's schedule, not ours."
        )


def test_capture_and_verify_install_the_same_deps():
    """Pillow/numpy versions affect the pixel comparison as much as the renderer does."""
    for path in (VERIFY, REFRESH):
        body = _uncommented(path.read_text(encoding="utf-8"))
        assert "requirements-visual.txt" in body, (
            f"{path.name} no longer installs requirements-visual.txt; capture and verify "
            "could end up on different Pillow/numpy versions"
        )
        assert "librsvg2-bin" in body, f"{path.name} no longer installs librsvg2-bin"


def test_verify_triggers_on_the_generators_it_protects():
    """The baselines record generator output; editing a generator must run verify."""
    triggers = _yaml(VERIFY)
    section = triggers[True] if True in triggers else triggers["on"]
    paths = set(section["pull_request"]["paths"])
    for required in (
        "scripts/lib/svg_l20_hero.py",
        "scripts/svg_visual_baseline.py",
        "tests/visual-baselines/**",
        ".github/workflows/visual-baseline-verify.yml",
    ):
        assert required in paths, f"{required} missing from the verify trigger paths"


def test_diff_report_is_uploaded_on_failure():
    """Without the artifact, a failure says "30 DIFF" and gives no way to look."""
    (job,) = _yaml(VERIFY)["jobs"].values()
    upload = [s for s in job["steps"] if "upload-artifact" in (s.get("uses") or "")]
    assert upload, "no upload-artifact step; a red verify would be undiagnosable"
    assert upload[0].get("if") == "failure()", (
        "the diff artifact should upload on failure (uploading always just burns storage)"
    )


def test_manifest_is_present_and_non_empty():
    """Canary on the premise: verify iterates the manifest, so an empty one is vacuous."""
    assert MANIFEST.is_file(), f"{MANIFEST} missing — verify would exit early"
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert len(manifest) >= 20, (
        f"manifest has only {len(manifest)} entries; verify would pass while checking "
        "almost nothing. Re-capture, or reconsider the gate."
    )


def test_pass_criteria_stay_tight():
    """Loosening the thresholds is the quiet way to neuter a pixel-diff gate."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert "DEFAULT_THRESHOLD_PCT = 0.5" in src, (
        "the default pixel-diff threshold moved. Raising it is how a visual gate stops "
        "objecting without anyone deleting it — justify the new value here if intended."
    )
    assert "MAX_CONTIGUOUS_BLOCK = 100" in src, (
        "the contiguous-block cap moved. The percentage alone cannot catch a small, "
        "sharply localised change (a swapped emblem), which is what this bounds."
    )
