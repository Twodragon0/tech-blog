#!/usr/bin/env python3
"""Guard: the post-quality gate blocks, self-heals first, and fails closed.

Promoted from advisory on 2026-09-08. The measurement that licensed it: all 216
published digests score at or above **90** against a target of **80**, so
nothing legitimate sits near the line, and the gate already carried a self-heal
(``upgrade_digest_post_quality``) — which is what
``INLINE_PUBLISH_GATES``' ``blocking => self_heal`` invariant requires.

Contrast with the other advisory gate in the same publisher, which is
deliberately NOT promoted: ``run_qa_gate`` would reject **141 of 216** existing
digests, and 140 of those come from ``validate_trend_analysis`` comparing two
populations that differ by design. See
``.omc/plans/advisory-gate-promotion-2026-09-08.md``.

Three behaviours are pinned here:

1. The re-score after the auto-upgrade is UNCONDITIONAL. It used to be skipped
   when the upgrader reported no change, so an under-target post that could not
   be repaired was logged as a warning and published anyway.
2. The gate returns a score rather than raising, so the blocking decision stays
   in the publisher next to the other gates and the registry.
3. An unmeasurable score FAILS CLOSED. The old blanket ``except Exception:
   return`` made "could not check" indistinguishable from "passed", which is
   harmless for an advisory and wrong for a blocker.
"""

from __future__ import annotations

import re
from pathlib import Path

import auto_publish_news as apn
import pytest

from scripts.news import content_generator as cg

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLISHER = REPO_ROOT / "scripts" / "auto_publish_news.py"


@pytest.fixture
def post(tmp_path):
    p = tmp_path / "2026-12-31-Tech_Security_Weekly_Digest_Probe.md"
    p.write_text("---\ntitle: t\n---\n\n본문.\n", encoding="utf-8")
    return p


def _patch(monkeypatch, scores, *, upgraded=True):
    """Drive the gate with a scripted score sequence."""
    seen = {"upgrades": 0}
    it = iter(scores)

    def fake_upgrade(path):
        seen["upgrades"] += 1
        return upgraded

    monkeypatch.setattr(
        cg,
        "_post_quality_helpers",
        lambda: (fake_upgrade, lambda p: {"total": next(it)}),
    )
    return seen


def test_a_passing_score_skips_the_upgrade(monkeypatch, post):
    seen = _patch(monkeypatch, [94])
    assert cg._run_post_quality_gate(post, target=80) == 94
    assert seen["upgrades"] == 0, "a passing post must not be rewritten"


def test_the_upgrade_runs_and_the_healed_score_is_returned(monkeypatch, post):
    seen = _patch(monkeypatch, [70, 88])
    assert cg._run_post_quality_gate(post, target=80) == 88
    assert seen["upgrades"] == 1


def test_the_rescore_is_unconditional_even_when_the_upgrade_reports_nothing(
    monkeypatch, post
):
    """The regression this promotion depends on.

    With the old early return, a post the upgrader could not fix never got
    re-scored — the caller had no score to block on.
    """
    _patch(monkeypatch, [55, 55], upgraded=False)
    assert cg._run_post_quality_gate(post, target=80) == 55


def test_an_unimportable_scorer_returns_none_not_a_pass(monkeypatch, post):
    monkeypatch.setattr(cg, "_post_quality_helpers", lambda: (None, None))
    assert cg._run_post_quality_gate(post, target=80) is None, (
        "returning a number here would let an unmeasurable post through"
    )


def test_helpers_resolve_under_the_real_import_paths():
    """Control: the dual-path import is not vacuous.

    Both spellings are live in this repo — `auto_publish_news` runs with
    `scripts/` on sys.path, pytest imports this module as
    `scripts.news.content_generator` with only the repo root. If neither
    resolved, every publish would fail closed.
    """
    upgrade, validate = cg._post_quality_helpers()
    assert callable(upgrade) and callable(validate)


# --- wiring guards on the publisher ------------------------------------------


def _source() -> str:
    return PUBLISHER.read_text(encoding="utf-8")


def test_the_target_is_a_single_constant():
    """The call and the comparison must not drift apart."""
    assert apn.POST_QUALITY_TARGET == 80
    source = _source()
    assert "target=POST_QUALITY_TARGET" in source, (
        "the gate is called with a literal target again; it can now disagree "
        "with the threshold the block compares against"
    )
    assert not re.search(r"quality_score\s*<\s*\d", source), (
        "the block compares against a literal instead of POST_QUALITY_TARGET"
    )


def test_the_block_fails_closed_on_an_unmeasurable_score():
    assert re.search(
        r"if quality_score is None or quality_score < POST_QUALITY_TARGET:", _source()
    ), (
        "the None case is no longer blocked, so a post whose score could not be "
        "measured would publish unchecked"
    )


def test_the_registry_records_this_gate_as_blocking():
    entry = [e for e in apn.INLINE_PUBLISH_GATES if e[0] == "_run_post_quality_gate"]
    assert entry, "the gate vanished from the registry"
    _symbol, _canonical, blocking, self_heal = entry[0]
    assert blocking, "the registry still calls this advisory"
    assert self_heal, "a blocking gate without a self-heal costs a publish day"
