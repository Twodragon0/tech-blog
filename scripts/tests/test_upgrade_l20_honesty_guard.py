#!/usr/bin/env python3
"""The L20 spec writer must refuse to write a NEW honesty FAIL.

Most ``_data/l20_covers/*.yml`` specs have drifted away from the honest on-disk
corpus, so a blind ``--all`` re-render reintroduces covers whose bands assert
attack/CVE/breach evidence the owning post does not have. That is not
hypothetical: 49 covers regressed exactly this way after PR #387, and the
recovery was manual.

The svg-lint honesty gate already blocks such a corpus in CI — but only after
it is on disk and committed, so the gate tells you to undo N files rather than
preventing N files. This guard covers the write itself.

The refusal has to be loud in the exit code too. A run that skips the covers it
was asked to write, then exits 0, reports success for work it did not do.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts import upgrade_l20_cover as _mod  # noqa: E402

SPEC_DIR = REPO / "_data" / "l20_covers"

# A cover class that asserts an attack the owning post has no evidence for.
# Measured 2026-08-21 against the AWS-security/FinOps course post: `hero:
# ransomware_lock` and `hero: code_injection` both score FAIL, while
# `container_escape` PASSes because that post really does cover containers —
# the scorer is judging evidence, not vocabulary.
OVERCLAIM = "ransomware_lock"


def _a_spec():
    """The first committed L20 spec, loaded through the real loader."""
    paths = sorted(SPEC_DIR.glob("*.yml"))
    assert paths, f"no L20 specs under {SPEC_DIR}; this guard has nothing to test"
    return _mod.load_spec(paths[0])


# ---------------------------------------------------------------------------
# Non-vacuity: the corpus this guard protects must currently be honest
# ---------------------------------------------------------------------------


def test_committed_specs_render_honestly() -> None:
    """If a real spec already FAILs, every assertion below is ambiguous."""
    dishonest = []
    for path in sorted(SPEC_DIR.glob("*.yml")):
        spec = _mod.load_spec(path)
        if _mod.honesty_regression(spec, _mod.render(spec)) is not None:
            dishonest.append(spec.filename)
    assert not dishonest, (
        f"spec(s) already render a non-baselined honesty FAIL: {dishonest}. Fix "
        "the spec (or baseline it deliberately) before trusting this guard's "
        "negative cases."
    )


# ---------------------------------------------------------------------------
# The guard fires
# ---------------------------------------------------------------------------


def test_overclaiming_hero_is_reported() -> None:
    spec = _a_spec()
    mutated = dataclasses.replace(spec, hero={**spec.hero, "visual": OVERCLAIM})
    violations = _mod.honesty_regression(mutated, _mod.render(mutated))
    assert violations is not None, (
        f"hero visual {OVERCLAIM!r} on {spec.filename} was accepted; the guard "
        "cannot see the regression class it exists for"
    )
    assert OVERCLAIM in violations, violations


def test_write_refuses_and_leaves_the_file_untouched(tmp_path, monkeypatch) -> None:
    """The refusal must happen BEFORE the write, not be reported after it.

    ``output_path`` is redirected into tmp_path first. Pointing this at the real
    ``assets/images/`` entry would be a test that corrupts the corpus the moment
    the guard it checks is absent — which is exactly the condition under which
    it runs (verified: a mutation run that stripped the guard wrote a dishonest
    cover into the working tree).
    """
    spec = _a_spec()
    mutated = dataclasses.replace(spec, hero={**spec.hero, "visual": OVERCLAIM})
    target = tmp_path / spec.filename
    monkeypatch.setattr(
        type(mutated), "output_path", property(lambda _self: target), raising=False
    )

    with pytest.raises(_mod.HonestyRefusal) as excinfo:
        _mod.write(mutated)

    assert excinfo.value.filename == spec.filename
    assert not target.exists(), (
        "the cover was written despite the refusal — the guard runs too late to "
        "be a write guard"
    )


def test_honest_spec_is_not_refused() -> None:
    spec = _a_spec()
    assert _mod.honesty_regression(spec, _mod.render(spec)) is None


# ---------------------------------------------------------------------------
# Escape hatches stay escape hatches
# ---------------------------------------------------------------------------


def test_force_bypasses_the_guard(tmp_path, monkeypatch) -> None:
    """`--force` exists for a wrong scorer, and must not silently do nothing."""
    spec = _a_spec()
    mutated = dataclasses.replace(spec, hero={**spec.hero, "visual": OVERCLAIM})
    written = {}

    class _Sink:
        def write_text(self, text, encoding="utf-8"):
            written["bytes"] = len(text.encode(encoding))

    monkeypatch.setattr(
        type(mutated), "output_path", property(lambda _self: _Sink()), raising=False
    )
    size = _mod.write(mutated, force=True)
    assert size > 0 and written.get("bytes") == size


def test_dry_run_never_writes_and_never_refuses() -> None:
    """A dry run is for inspection; refusing there would block reading a spec."""
    spec = _a_spec()
    mutated = dataclasses.replace(spec, hero={**spec.hero, "visual": OVERCLAIM})
    assert _mod.write(mutated, dry_run=True) == 0


def test_baselined_cover_is_exempt(monkeypatch, tmp_path) -> None:
    """Grandfathered legacy FAILs must not trip the guard — only new ones do.

    The committed baseline is empty today (emptied 2026-06-23 when the 16 then-
    failing covers were corrected), so the exemption branch has no live input
    and is asserted against a temporary baseline instead.
    """
    spec = _a_spec()
    mutated = dataclasses.replace(spec, hero={**spec.hero, "visual": OVERCLAIM})
    assert _mod.honesty_regression(mutated, _mod.render(mutated)) is not None

    baseline = tmp_path / "baseline.txt"
    baseline.write_text(f"assets/images/{spec.filename}\n", encoding="utf-8")
    monkeypatch.setattr(_mod, "_HONESTY_BASELINE", baseline)
    assert _mod.honesty_regression(mutated, _mod.render(mutated)) is None


def test_guard_fails_open_when_the_scorer_is_unavailable(monkeypatch, capsys) -> None:
    """Defense-in-depth, not the only gate: an import error must not brick the CLI.

    svg-lint still scores the on-disk corpus, so failing open here costs a
    layer rather than the property. It must be visible, though.
    """
    spec = _a_spec()
    mutated = dataclasses.replace(spec, hero={**spec.hero, "visual": OVERCLAIM})
    monkeypatch.setitem(sys.modules, "scripts.score_cover_honesty", None)
    assert _mod.honesty_regression(mutated, _mod.render(mutated)) is None
    assert "honesty guard unavailable" in capsys.readouterr().err
