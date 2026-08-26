#!/usr/bin/env python3
"""CI regression guard: the image trigger must be at least as wide as the scan.

Both image workflows sweep the whole corpus and are triggered by a `paths`
filter. Whenever that filter is narrower than what the steps actually read, a
change lands inside the scan and outside the trigger — the workflow stays green
by never running, which is indistinguishable from passing. This repo has now
hit that shape three times on the same two files:

- pre-#489: `assets/images/*.svg` (depth-1 only) vs `rglob("*.svg")` — 156 SVGs
  under diagrams/, mermaid/, _unused_archive/ were scanned but not triggerable.
- 2026-08-10: widened to `**.svg`, fixing the depth axis.
- 2026-08-26: still narrow on the EXTENSION axis. check_orphan_cover_rasters.py
  reads only `<slug>_{og,card}.{png,webp,avif}`, and verify_images_unified.py
  scans {.svg,.png,.webp,.jpg,.jpeg} — none of which `**.svg` matches. Commit
  9bf4c2e5, "remove 45 orphan cover rasters from renamed covers", changed 45
  files that all matched `_(og|card)\\.(png|webp|avif)$` and none of the 51
  patterns: the commit remediating the orphan-raster problem could not trigger
  the gate for it.

So this guard does not assert a literal pattern — a literal is what kept getting
fixed on one axis and left broken on another. It asserts BEHAVIOUR: representative
paths of every kind these workflows read must match some pattern in the filter.
Add a new asset type the steps scan, and this fails until the trigger covers it.

Direction: coverage. Narrowing the filter, or broadening a scan without the
trigger, trips this.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = (
    REPO_ROOT / ".github" / "workflows" / "svg-lint.yml",
    REPO_ROOT / ".github" / "workflows" / "check-svg.yml",
)

# One representative path per asset kind the steps read, with the reader that
# makes it in-scope. These are the scan surface; the trigger must cover them.
SCANNED_SAMPLES = (
    ("assets/images/2026-01-01-Post.svg", "cover SVG — every --all cover gate"),
    ("assets/images/diagrams/flow.svg", "verify_images_unified.py rglob, depth >= 2"),
    ("assets/images/2026-01-01-Post_og.png", "check_orphan_cover_rasters.py"),
    ("assets/images/2026-01-01-Post_og.webp", "check_orphan_cover_rasters.py"),
    ("assets/images/2026-01-01-Post_og.avif", "check_orphan_cover_rasters.py"),
    ("assets/images/2026-01-01-Post_card.webp", "check_orphan_cover_rasters.py"),
    ("assets/images/photo.jpg", "verify_images_unified.py:198 ext set"),
)


def _gh_glob_matches(path: str, pattern: str) -> bool:
    """GitHub Actions path-filter semantics: `**` crosses `/`, `*` does not."""
    rx = re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.fullmatch(rx, path) is not None


def _filters(workflow: Path) -> dict[str, list[str]]:
    doc = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    on = doc.get(True, doc.get("on")) or {}
    out = {}
    for event in ("push", "pull_request"):
        block = on.get(event)
        if isinstance(block, dict) and block.get("paths"):
            out[event] = block["paths"]
    return out


def test_workflows_exist():
    for wf in WORKFLOWS:
        assert wf.is_file(), f"{wf} not found"


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda p: p.name)
def test_both_events_are_path_filtered(workflow: Path):
    events = _filters(workflow)
    assert set(events) == {"push", "pull_request"}, (
        f"{workflow.name}: expected path-filtered push AND pull_request, got "
        f"{sorted(events)}. If an event lost its filter it now runs always "
        "(harmless) or lost the event entirely (not harmless) — check which."
    )


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda p: p.name)
@pytest.mark.parametrize(("sample", "reader"), SCANNED_SAMPLES, ids=lambda v: v.split("/")[-1] if "/" in str(v) else v)
def test_trigger_covers_every_scanned_asset_kind(
    workflow: Path, sample: str, reader: str
):
    for event, patterns in _filters(workflow).items():
        assert any(_gh_glob_matches(sample, p) for p in patterns), (
            f"{workflow.name} ({event}): no pattern matches {sample!r}, which "
            f"{reader} reads. The steps scan it, the trigger cannot see it — so "
            "a change to that asset leaves the workflow green by not running. "
            "That is how 9bf4c2e5 (45 orphan rasters) escaped the orphan-raster "
            "gate. Widen the filter rather than narrowing the scan."
        )


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda p: p.name)
def test_schedule_survives_as_the_backstop(workflow: Path):
    """The filter is the fast path; the daily sweep is what covers bot pushes.

    A GITHUB_TOKEN push triggers no workflow at all, so for the cron — the
    dominant producer of these assets — no `paths` value is wide enough. Only
    the schedule sees those commits.
    """
    doc = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    on = doc.get(True, doc.get("on")) or {}
    assert on.get("schedule"), (
        f"{workflow.name} lost its schedule. Path filters cannot substitute: the "
        "blogwatcher pushes with GITHUB_TOKEN and that triggers nothing, so the "
        "daily sweep is the only thing that ever inspects a bot-published cover."
    )


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda p: p.name)
def test_workflow_file_retriggers_itself(workflow: Path):
    """Editing the gate must run the gate."""
    rel = f".github/workflows/{workflow.name}"
    for event, patterns in _filters(workflow).items():
        assert any(_gh_glob_matches(rel, p) for p in patterns), (
            f"{workflow.name} ({event}) no longer lists itself, so a change to "
            "the gate ships without the gate running once"
        )


# ---------------------------------------------------------------------------
# visual-baseline pair
#
# Deliberately NOT subject to the extension-axis assertions above. Audited
# 2026-08-26: svg_visual_baseline.py reads exactly two surfaces — the 32
# hardcoded `.svg` paths in TARGET_SVGS and tests/visual-baselines/ — and
# rasterises them via rsvg-convert. It reads no raster under assets/images/, so
# `assets/images/**` would be wider than the scan rather than narrower. What
# these two DO need is that their own read surfaces stay reachable.
# ---------------------------------------------------------------------------

VISUAL_BASELINE = (
    REPO_ROOT / ".github" / "workflows" / "visual-baseline-refresh.yml",
    REPO_ROOT / ".github" / "workflows" / "visual-baseline-verify.yml",
)
BASELINE_SCRIPT = REPO_ROOT / "scripts" / "svg_visual_baseline.py"


def _target_svgs() -> list[str]:
    """Every quoted path in TARGET_SVGS, parsed from source (PIL may be absent).

    Matches any quoted path, NOT just `*.svg`. An earlier version filtered on
    `\\.svg"` here, which made ``test_target_svgs_is_still_a_hardcoded_svg_only
    _sample`` vacuous: a `.png` added to the list was dropped by this extractor
    before the assertion could see it, so the mutation that the assertion exists
    to catch passed. The extractor is the assertion's haystack — it must not
    pre-filter on the property being asserted.
    """
    src = BASELINE_SCRIPT.read_text(encoding="utf-8")
    block = src.split("TARGET_SVGS", 1)[1].split("\n]", 1)[0]
    return re.findall(r'"([^"]+/[^"]+)"', block)


def test_target_svgs_is_still_a_hardcoded_svg_only_sample():
    """The premise behind exempting these two from the extension axis."""
    targets = _target_svgs()
    assert targets, "TARGET_SVGS could not be parsed; re-derive this exemption"
    assert all(t.endswith(".svg") for t in targets), (
        "TARGET_SVGS now contains a non-SVG entry. The visual-baseline workflows "
        "are exempt from the raster assertions above ONLY because this sample is "
        "SVG-only — re-check their filters before extending the sample."
    )


@pytest.mark.parametrize("workflow", VISUAL_BASELINE, ids=lambda p: p.name)
def test_visual_baseline_trigger_reaches_its_own_read_surfaces(workflow: Path):
    """Both TARGET_SVGS and the baseline directory must be reachable."""
    sample_target = _target_svgs()[0]
    for event, patterns in _filters(workflow).items():
        for surface, why in (
            (sample_target, "a TARGET_SVGS entry"),
            ("tests/visual-baselines/manifest.json", "the baseline store"),
        ):
            assert any(_gh_glob_matches(surface, p) for p in patterns), (
                f"{workflow.name} ({event}): nothing matches {surface!r}, which is "
                f"{why} this workflow reads. A change there would not run it."
            )


@pytest.mark.parametrize("workflow", VISUAL_BASELINE, ids=lambda p: p.name)
def test_visual_baseline_workflow_retriggers_itself(workflow: Path):
    rel = f".github/workflows/{workflow.name}"
    for event, patterns in _filters(workflow).items():
        assert any(_gh_glob_matches(rel, p) for p in patterns), (
            f"{workflow.name} ({event}) does not list itself. refresh/--capture "
            "auto-commits on main, so an unreviewed change to it would take "
            "effect without the workflow having run once under its new form."
        )
