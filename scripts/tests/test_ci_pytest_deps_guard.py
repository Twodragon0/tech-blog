#!/usr/bin/env python3
"""CI regression guard: the deps that stop 4 tests from skipping must stay declared.

Until 2026-08-18 `scripts/requirements-ci.txt` installed neither Pillow nor
fontTools, so the CI pytest run reported `4204 passed, 7 skipped` and four of
those seven skips were dependency-caused:

    test_auto_publish_news.py::TestGenerateAndCommitRasterVariants
      ::test_all_five_rasters_emitted_from_og_png          importorskip("PIL")
      ::test_idempotent_skips_existing_variants            importorskip("PIL")
    test_font_tier_split.py
      ::test_woff2_cmaps_match_the_declared_split[400]     importorskip("fontTools")
      ::test_woff2_cmaps_match_the_declared_split[700]     importorskip("fontTools")

`importorskip` fails open, which is the trap: the two raster tests were written
to reproduce the 2026-05-27/28 blogwatcher bug where Pillow was missing on the
cron runner and raster variants were therefore never emitted — and they skipped
for that same missing dependency, so the regression they exist to catch was
never actually gated. Dropping either line from requirements-ci.txt would
restore that silence without turning a single check red.

This guard is static on purpose: it pins the declaration, not the import. A test
that merely imported PIL would itself pass in any environment that happens to
have Pillow (every developer laptop here does), which is precisely the blind
spot being closed.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = REPO_ROOT / "scripts" / "requirements-ci.txt"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "jekyll.yml"
RASTER_TEST = REPO_ROOT / "scripts" / "tests" / "test_auto_publish_news.py"
FONT_TEST = REPO_ROOT / "scripts" / "tests" / "test_font_tier_split.py"


def _requirement_lines() -> list[str]:
    text = REQUIREMENTS.read_text(encoding="utf-8")
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _find(prefix: str) -> str:
    """Return the single requirement line whose distribution name matches `prefix`."""
    matches = [
        line
        for line in _requirement_lines()
        if re.match(rf"^{re.escape(prefix)}\b", line, re.IGNORECASE)
    ]
    assert len(matches) == 1, (
        f"expected exactly one {prefix} requirement in {REQUIREMENTS.name}, "
        f"found {matches!r}"
    )
    return matches[0]


# ---------------------------------------------------------------------------
# Non-vacuity: assert the skipping tests still exist before pinning their deps
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "needle"),
    [
        (RASTER_TEST, 'importorskip("PIL"'),
        (FONT_TEST, 'importorskip("fontTools"'),
    ],
    ids=["raster-pil", "font-fonttools"],
)
def test_guarded_tests_still_use_importorskip(path: Path, needle: str) -> None:
    """If the importorskip calls are gone this guard has nothing left to protect.

    Removing them is a legitimate change — it makes the dependency hard —
    but then this file should be deleted in the same commit rather than left
    asserting a requirement nothing consumes.
    """
    assert needle in path.read_text(encoding="utf-8"), (
        f"{path.name} no longer contains {needle!r}; if the skip guard was "
        f"intentionally removed, delete {Path(__file__).name} too"
    )


# ---------------------------------------------------------------------------
# The declarations themselves
# ---------------------------------------------------------------------------


def test_pillow_is_declared_with_an_avif_capable_floor() -> None:
    """AVIF encoding landed in Pillow 11.3.0; a lower floor cannot run the tests.

    `_generate_and_commit_raster_variants` writes _og.avif and _card.avif, so a
    Pillow that imports but reports `features.check("avif") is False` fails the
    raster tests rather than skipping them. 11.3.0 was verified as the floor
    where that check returns True.
    """
    line = _find("Pillow")
    match = re.search(r">=\s*(\d+)\.(\d+)", line)
    assert match, f"Pillow requirement {line!r} declares no >= floor"
    major, minor = int(match.group(1)), int(match.group(2))
    assert (major, minor) >= (11, 3), (
        f"Pillow floor {major}.{minor} predates native AVIF encoding (11.3.0); "
        f"the raster variant tests would fail rather than skip"
    )


def test_fonttools_is_declared_with_the_woff_extra() -> None:
    """The `[woff]` extra is the load-bearing part — it is what pulls in brotli.

    Plain `fonttools` installs and imports cleanly, so `importorskip("fontTools")`
    passes, and then `TTFont(woff2)` raises because woff2 decompression has no
    brotli. Dropping the extra would convert 2 skips into 2 failures, which is
    at least loud; dropping the whole line restores the silent skip.
    """
    line = _find("fonttools")
    assert "[woff]" in line.lower(), (
        f"fonttools requirement {line!r} is missing the [woff] extra; "
        f"without brotli, fontTools cannot open the shipped .woff2 files"
    )


# ---------------------------------------------------------------------------
# Wiring: the file has to actually reach the pytest run
# ---------------------------------------------------------------------------


def test_pytest_job_installs_requirements_ci() -> None:
    """requirements-ci.txt is only load-bearing if the job running pytest installs it."""
    import yaml

    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    steps = workflow["jobs"]["build"]["steps"]
    run_blocks = [step.get("run", "") for step in steps]

    installs = [r for r in run_blocks if "requirements-ci.txt" in r]
    assert installs, (
        f"{WORKFLOW.name} build job no longer installs scripts/requirements-ci.txt; "
        f"the pytest run would fall back to whatever the runner image ships"
    )

    pytest_runs = [r for r in run_blocks if "pytest scripts/tests" in r]
    assert pytest_runs, (
        f"{WORKFLOW.name} build job no longer runs `pytest scripts/tests/`; "
        f"this guard's premise is gone"
    )

    assert run_blocks.index(installs[0]) < run_blocks.index(pytest_runs[0]), (
        "requirements-ci.txt is installed after pytest runs, so the deps are "
        "not present when the tests decide whether to skip"
    )
