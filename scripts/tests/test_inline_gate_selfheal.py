#!/usr/bin/env python3
"""Guard: the inline digest quality gate heals mid-word cells before deleting.

``digest_quality_report.check_file`` runs inside ``auto_publish_news.py`` and a
failure there **deletes the draft** and ends the cron run. It is the earliest
publish gate, has the largest blast radius, and until this change was the only
one with no self-heal — the six self-heal-then-block steps in
``ai-blogwatcher.yml`` all run after the post exists, so they never got a turn.
Two publish days were lost that way (2026-08-27, 2026-09-06).

The gate is deny-by-default over an 18-word allow-list, so false positives are
measured, not hypothetical: 10 live feed titles end in a complete word the
allow-list does not carry (``7개 주요 Bitcoin 채굴 풀``, ``2026년 초``). Any of
those landing in a trend cell used to cost a day; with the heal it costs a few
characters.

What is deliberately NOT healed: ``ENGLISH_HEADER``, ``INCOMPLETE_HIGHLIGHT``
and ``SUMMARY_QUALITY``. No deterministic fixer exists for them, and healing
what you cannot fix only hides it.
"""

from __future__ import annotations

import re
from pathlib import Path

import digest_quality_report as dqr
import pytest
import rewind_midword_cells as rw

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLISHER = REPO_ROOT / "scripts" / "auto_publish_news.py"

# Filler long enough to clear the gate's 30-character floor.
FILLER = "보안 점검 절차와 로그 보존 그리고 대응 담당자 배정"

# The gate's own particle list, read from the regex so it cannot drift.
GATE_PARTICLES = sorted(
    re.search(r"\\s\+\((.+?)\)", dqr._TRUNCATION_PARTICLES.pattern).group(1).split("|")
)


def _post(tmp_path: Path, *cells: str) -> Path:
    rows = "".join(
        f"| [t{i}](https://example.invalid/{i}) | src | {c} |\n"
        for i, c in enumerate(cells)
    )
    post = tmp_path / "2026-12-31-Tech_Security_Weekly_Digest_Probe.md"
    post.write_text(
        "---\ntitle: t\n---\n\n| 제목 | 출처 | 핵심 내용 |\n"
        "|------|------|----------|\n" + rows,
        encoding="utf-8",
    )
    return post


def _gate_rejects(cell: str) -> str | None:
    if len(cell) <= 30:
        return None
    if dqr._TRUNCATION_PARTICLES.search(cell):
        return "particle"
    m = dqr._SINGLE_SYLLABLE_TAIL.search(cell)
    if m and m.group(1) not in dqr._SINGLE_SYLLABLE_ALLOW:
        return f"lone:{m.group(1)}"
    return None


def test_the_gate_particle_list_was_actually_parsed():
    """Canary: a regex reshuffle that empties this list would make the
    per-particle test below vacuous — it would loop zero times and pass."""
    assert len(GATE_PARTICLES) >= 15, GATE_PARTICLES
    assert {"의", "를", "위한", "대한"} <= set(GATE_PARTICLES)


@pytest.mark.parametrize("particle", GATE_PARTICLES)
def test_rewind_clears_every_gate_particle(particle):
    """The two helpers cover different lists; only their union covers the gate.

    ``_drop_dangling_lone_syllable`` catches the single-syllable particles the
    generator's ``_DANGLING_SUFFIXES_RE`` lacks (``할``, ``인``), and that regex
    catches the multi-syllable ones a lone-syllable rule cannot see (``위한``,
    ``하기``, ``대한``, ``으로``, ``에서``). Asserted per particle instead of
    trusting the reasoning.
    """
    cell = f"{FILLER} {particle}"
    assert _gate_rejects(cell) == "particle", f"fixture is not a violation: {cell!r}"
    healed = rw.rewind_cell(cell)
    assert _gate_rejects(healed) is None, (
        f"{particle!r} survives the rewind, so the self-heal would loop into a "
        f"block: {healed!r}"
    )


@pytest.mark.parametrize("syllable", ["조", "가", "서", "관", "최", "틈"])
def test_rewind_clears_a_lone_syllable(syllable):
    cell = f"{FILLER} {syllable}"
    assert _gate_rejects(cell), f"fixture is not a violation: {cell!r}"
    assert _gate_rejects(rw.rewind_cell(cell)) is None


@pytest.mark.parametrize(
    "cell",
    [f"{FILLER} {p}" for p in ("의", "위한", "할", "조", "최")],
)
def test_rewind_never_invents_text(cell):
    """The result must be a prefix of the input.

    This is the property that makes the heal safe to run unattended: it cannot
    hallucinate a completion, only drop a dangling token.
    """
    healed = rw.rewind_cell(cell)
    assert cell.startswith(healed), f"{healed!r} is not a prefix of {cell!r}"


def test_a_measured_false_positive_is_healed_instead_of_blocking(tmp_path):
    """`채굴 풀` is a real feed title ending in a complete word.

    `풀` is not on the allow-list, so the gate rejects it — and before this
    change that deleted the draft and lost the day.
    """
    cell = "이번 주 주요 소식으로는 국내외 7개 주요 Bitcoin 채굴 풀"
    post = _post(tmp_path, cell)
    assert any("MID-WORD" in m for m in dqr.check_file(post)), (
        "fixture no longer reproduces the false positive"
    )

    edits = rw.rewind_post(post)
    assert len(edits) == 1, edits
    assert dqr.check_file(post) == [], (
        "the heal did not clear the gate, so the publish would still be lost"
    )
    assert "채굴" in post.read_text(encoding="utf-8")


def test_a_genuine_cut_is_healed_too(tmp_path):
    """The 2026-09-06 blocker, verbatim."""
    post = _post(
        tmp_path, "AI는 사람이 설계한 규칙보다 대규모 최적화로 성장하는 시스템에 가"
    )
    assert dqr.check_file(post), "fixture is not a violation"
    assert rw.rewind_post(post)
    assert dqr.check_file(post) == []


def test_an_unhealable_issue_still_blocks(tmp_path):
    """An English trend header has no fixer, so it must survive the heal.

    Without this, a future widening of the heal could make the gate green while
    the defect ships.
    """
    # The rule only inspects bold cells (`^\*\*[A-Za-z0-9 /\-&.]+\*\*$`) — a
    # bare English sentence is not a trend header and is not flagged.
    post = _post(tmp_path, "**Weekly Threat Landscape**")
    before = dqr.check_file(post)
    assert any("ENGLISH_HEADER" in m for m in before), before
    rw.rewind_post(post)
    after = dqr.check_file(post)
    assert any("ENGLISH_HEADER" in m for m in after), (
        "the English header disappeared without a fixer having run; the gate "
        f"would now pass a defect it cannot repair: {after}"
    )


def test_a_clean_post_is_left_byte_identical(tmp_path):
    post = _post(tmp_path, "쿠버네티스 런타임 보안 강화 방안을 단계별로 정리했습니다.")
    original = post.read_bytes()
    assert rw.rewind_post(post) == []
    assert post.read_bytes() == original


def test_only_the_flagged_cell_is_touched(tmp_path):
    """Padding and neighbouring cells must survive.

    The fixer replaces the offending segment in place rather than rebuilding
    the row, so an unrelated cell's whitespace is not reflowed.
    """
    good = "정상적인 셀 내용이며 충분히 길어서 게이트의 30자 하한을 넘습니다."
    bad = f"{FILLER} 조"
    post = _post(tmp_path, good, bad)
    rw.rewind_post(post)
    text = post.read_text(encoding="utf-8")
    assert f"| {good} |" in text, "an untouched cell was reformatted"
    assert f"| {bad} |" not in text


def test_a_baselined_cell_is_not_healed(tmp_path, monkeypatch):
    """Healing a grandfathered cell would make its baseline entry stale.

    ``test_no_baseline_entry_is_stale`` treats a stale entry as a defect, and
    rightly so, so the fixer must mirror ``check_file`` and skip exempted cells.
    """
    cell = f"{FILLER} 조"
    post = _post(tmp_path, cell)
    key = dqr.midword_key(post.name, cell)
    monkeypatch.setattr(rw, "load_midword_baseline", lambda *a, **k: frozenset({key}))
    assert rw.rewind_post(post) == [], (
        "a baselined cell was rewritten, which desynchronises the baseline"
    )


# --- wiring guards on the publisher ------------------------------------------


def _publisher_source() -> str:
    return PUBLISHER.read_text(encoding="utf-8")


def test_publisher_exists():
    assert PUBLISHER.is_file(), f"{PUBLISHER} not found"


def test_heal_runs_before_the_post_is_deleted():
    src = _publisher_source()
    heal = src.find("from rewind_midword_cells import rewind_post")
    unlink = src.find("post_path.unlink(missing_ok=True)")
    assert heal != -1, "the self-heal import is gone; the gate deletes again"
    assert unlink != -1, "the delete moved; re-anchor this guard"
    assert heal < unlink, (
        "the heal now runs after the delete, so it can never save a draft"
    )


def test_heal_is_scoped_to_the_two_healable_issue_kinds():
    src = _publisher_source()
    match = re.search(
        r'if any\(\("TRUNCATED" in qi or "MID-WORD" in qi\) for qi in quality_issues\)',
        src,
    )
    assert match, (
        "the heal trigger changed. It must stay scoped to TRUNCATED/MID-WORD — "
        "the other issue kinds have no deterministic fixer, and running a "
        "rewind for them would report a heal that fixed nothing."
    )


def test_the_reverify_is_unguarded():
    """The re-check must decide the outcome on its own.

    A `try`/`or []`/`if` around it is how a self-heal turns into a bypass: the
    post ships with the issue still present. This repo has hit that shape
    before, which is why the six workflow steps end on a bare re-verify.
    """
    src = _publisher_source()
    reverify = re.search(
        r"\n(\s*)quality_issues = _check_digest_quality\(post_path\)\n",
        src[src.find("healed:") :],
    )
    assert reverify, "the re-verification after the heal is gone"
    line = reverify.group(0).strip()
    assert line == "quality_issues = _check_digest_quality(post_path)", line
