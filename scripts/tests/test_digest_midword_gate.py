#!/usr/bin/env python3
"""Guard: the mid-word cell gate, its allow-list, and its grandfather baseline.

The publish gate's ``_TRUNCATION_PARTICLES`` only fires when a truncated table
cell happens to end in a dangling particle. On 2026-09-07 the rejected digest
had TWO cut cells in the same table — ``…시스템에 가`` (blocked) and
``…괜찮아서 틈`` (accepted, because ``틈`` is not a particle). A corpus sweep
then found 44 mid-word cells across 37 already-published digests.

Design notes worth keeping
--------------------------
The obvious wider heuristic does not work. "Cell has no sentence terminator"
flags 3127 of the 7134 corpus cells over 30 characters, because table cells are
legitimately noun phrases (``s Analyzer, CloudTrail``, ``까지 step-by-step
가이드 제공``). Measured before wiring anything.

What does work is a lone trailing Hangul syllable, deny-by-default, with a
reasoned allow-list — the shape ``check_card_title_language`` already uses. Of
the 96 corpus cells with such a tail, 52 end in one of 18 complete words and 44
are genuine cuts.

The 44 are baselined rather than repaired: their source text is gone, so
finishing the words would mean inventing them. The baseline keeps the gate
BLOCKING for everything new instead of leaving it dormant.
"""

from __future__ import annotations

import re
from pathlib import Path

import digest_quality_report as dqr
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE = REPO_ROOT / "scripts" / "digest_midword_baseline.txt"

# Frozen at the count measured on 2026-09-07. A ratchet, not a target: the
# generator no longer emits these, so this number must only ever go DOWN.
BASELINE_MAX = 44


def _post_with_cell(tmp_path: Path, cell: str) -> Path:
    """A minimal Digest post carrying one table row."""
    post = tmp_path / "2026-12-31-Tech_Security_Weekly_Digest_Probe.md"
    post.write_text(
        "---\ntitle: t\n---\n\n| 제목 | 출처 | 핵심 내용 |\n"
        "|------|------|----------|\n"
        f"| [t](https://example.invalid/x) | src | {cell} |\n",
        encoding="utf-8",
    )
    return post


_CUT_CELL = "공격 표면 점검과 로그 보존 절차 그리고 대응 담당자 배정 및 후속 조"
_ALLOWED_CELL = "VPC 설정과 Security Group 그리고 IAM 정책 등"


def test_baseline_file_exists():
    """Canary: a missing baseline silently disables the grandfathering, which
    would make the gate fail on 44 historical posts rather than pass wrongly —
    still worth failing loudly instead of guessing."""
    assert BASELINE.is_file(), f"{BASELINE} not found"


def test_a_new_mid_word_cell_is_blocked(tmp_path):
    post = _post_with_cell(tmp_path, _CUT_CELL)
    messages = dqr.check_file(post)
    assert any("MID-WORD" in m for m in messages), (
        f"a cell ending mid-word was accepted at the publish gate: {messages}"
    )


def test_control_an_allow_listed_tail_is_not_blocked(tmp_path):
    """Control for the test above.

    Without it, an assertion that "the gate flags things" passes just as well
    for a gate that flags everything — and this one is deny-by-default, so
    over-flagging is the likely failure mode.
    """
    post = _post_with_cell(tmp_path, _ALLOWED_CELL)
    assert dqr.check_file(post) == [], (
        "`등` legitimately ends a Korean noun phrase; flagging it would make the "
        "gate fire on 13 corpus cells that are correct"
    )


def test_short_cells_are_out_of_scope(tmp_path):
    """The 30-character floor is what keeps table headers and labels out."""
    post = _post_with_cell(tmp_path, "짧은 셀 조")
    assert dqr.check_file(post) == []


@pytest.mark.parametrize("word", sorted(dqr._SINGLE_SYLLABLE_ALLOW))
def test_allow_list_entries_are_single_syllables(word):
    """A multi-character entry would silently never match the tail regex."""
    assert len(word) == 1 and re.match(r"[가-힣]", word), (
        f"{word!r} cannot match a lone-syllable tail, so the entry is dead"
    )


def test_allow_list_excludes_the_words_measured_as_cuts():
    """`수` and `시` look like nouns but every corpus occurrence was a cut.

    Pinned because they are the two most tempting additions: `할 수` reads like
    a complete "can", and `시` is a common noun — but the cells were `할 수`
    from 할 수 있다, and 시간 / 시작 / 시장.
    """
    for word in ("수", "시", "남", "제"):
        assert word not in dqr._SINGLE_SYLLABLE_ALLOW, (
            f"{word!r} was allow-listed, which un-flags a measured mid-word cut"
        )


def test_baseline_does_not_grow():
    n = len(dqr.load_midword_baseline(BASELINE))
    assert n <= BASELINE_MAX, (
        f"digest_midword_baseline.txt grew to {n} (> {BASELINE_MAX}). A new "
        "mid-word cell was grandfathered instead of fixed. The generator no "
        "longer produces these, so a fresh hit is either a new truncation "
        "source or a word that belongs in _SINGLE_SYLLABLE_ALLOW — check the "
        "actual cell. If a growth is genuinely intentional, raise BASELINE_MAX "
        "in the same commit so the intent is reviewable."
    )


def test_no_baseline_entry_is_stale():
    """Every grandfathered entry must still match a real cell.

    A stale entry is not harmless: it means the cell was edited or the detector
    changed, and nobody would notice the baseline drifting out of sync with the
    corpus it is supposed to describe.
    """
    live = set()
    for post in dqr.find_digest_posts(None):
        for mc in dqr.analyze_post(post)["midword_cells"]:
            live.add(dqr.midword_key(post.name, mc["text"]))
    stale = sorted(dqr.load_midword_baseline(BASELINE) - live)
    assert not stale, (
        "baseline entries that no longer match any cell (fixed, or the detector "
        "moved) — drop them so the count ratchets down:\n  " + "\n  ".join(stale)
    )


def test_baseline_key_is_not_line_based():
    """Line numbers shift on any edit; the key must survive that."""
    key = dqr.midword_key("2026-01-01-X.md", "가" * 80)
    assert "\t" in key
    assert not re.search(r"\d+", key.split("\t", 1)[1]), (
        "the key's second field looks like it carries a line number"
    )


def test_corpus_path_fails_ci_on_an_unbaselined_cell(tmp_path, capsys):
    """The `--all --ci` path must fail too, not just the publish path.

    Added after a mutation run: deleting `or fresh_midword` from
    `generate_report`'s `has_issues` left every other test in this file green.
    That mutation turns the gate dormant — it would keep counting mid-word cells
    in the report while `--ci` exited 0, which is the exact failure mode this
    repo has hit repeatedly.
    """
    post = _post_with_cell(tmp_path, _CUT_CELL)
    report = dqr.generate_report([post], baseline=frozenset())
    assert report["midword_cells_total"] == 1, report
    assert report["posts_with_issues"] == 1, (
        "the corpus report did not count the post as having issues, so "
        "`--all --ci` would exit 0 with a mid-word cell present"
    )
    assert dqr.print_report(report) is False, (
        "print_report returned all-clean, which is what `--ci` keys its exit code on"
    )
    capsys.readouterr()


def test_corpus_path_respects_the_baseline(tmp_path):
    """Contrast: a grandfathered cell must not fail CI."""
    post = _post_with_cell(tmp_path, _CUT_CELL)
    issues = dqr.analyze_post(post)
    key = dqr.midword_key(post.name, issues["midword_cells"][0]["text"])
    report = dqr.generate_report([post], baseline=frozenset({key}))
    assert report["midword_cells_total"] == 0
    assert report["midword_baselined"] == 1
    assert report["posts_with_issues"] == 0
