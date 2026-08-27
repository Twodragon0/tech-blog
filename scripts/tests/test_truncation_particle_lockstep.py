#!/usr/bin/env python3
"""The truncation detector and the truncation trimmer must know the same particles.

`digest_quality_report.py` blocks publication when a digest table cell ends in a
dangling Korean particle. `content_generator._truncate_korean_sentence` is what
produces those cells and strips the particle before emitting. The two carry
separate hand-written lists, so any particle the gate knows and the trimmer does
not is a cell the generator will happily emit and the gate will then reject —
a self-inflicted red cron with no bad input required.

Measured 2026-08-27: the trimmer was missing `위한`, `하기`, `대한`.

Direction: the trimmer's set must be a superset of the detector's. It may strip
more (harmless — the cell just gets shorter); it must never strip less.

This does NOT claim to explain the 2026-08-27 cron failure. That cell ended in
`의`, which both lists already carried, so its truncation came from somewhere
else — most likely the model's own output limit, which no Python truncator here
would produce. This test pins a latent instance of the same failure mode, not
that incident's root cause.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DETECTOR = REPO_ROOT / "scripts" / "digest_quality_report.py"
GENERATOR = REPO_ROOT / "scripts" / "news" / "content_generator.py"

# The trimmer inside _truncate_korean_sentence: `\s+(...)$`, anchored so it only
# removes a standalone trailing token.
_TRIMMER_RE = re.compile(r'r"\\s\+\(([^)]+)\)\$"')
_DETECTOR_RE = re.compile(r'_TRUNCATION_PARTICLES = re\.compile\(\s*r"\\s\+\(([^)]+)\)')


def _detector_particles() -> set[str]:
    text = DETECTOR.read_text(encoding="utf-8")
    match = _DETECTOR_RE.search(text)
    assert match, (
        "_TRUNCATION_PARTICLES not found in digest_quality_report.py. Either the "
        "gate changed shape or this regex went stale — check which before "
        "assuming the former, because a lockstep test that extracts nothing "
        "passes vacuously."
    )
    return set(match.group(1).split("|"))


def _trimmer_particles() -> set[str]:
    text = GENERATOR.read_text(encoding="utf-8")
    matches = _TRIMMER_RE.findall(text)
    assert len(matches) == 1, (
        f"expected exactly one `\\s+(...)$` particle list in content_generator.py, "
        f"found {len(matches)}. A second copy is another place for the two sets to "
        "drift apart; fold them together or extend this test to cover both."
    )
    return set(matches[0].split("|"))


def test_both_lists_are_extracted():
    """Guard the extractors themselves — empty sets would pass everything."""
    assert len(_detector_particles()) > 10
    assert len(_trimmer_particles()) > 10


def test_trimmer_covers_every_particle_the_gate_rejects():
    detector = _detector_particles()
    trimmer = _trimmer_particles()
    missing = detector - trimmer
    assert not missing, (
        f"the publication gate rejects cells ending in {sorted(missing)} but the "
        "generator never strips them, so it can emit a cell that is guaranteed to "
        "be rejected. Add them to the `\\s+(...)$` list in "
        "_truncate_korean_sentence."
    )
