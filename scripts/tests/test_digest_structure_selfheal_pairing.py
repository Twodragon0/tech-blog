#!/usr/bin/env python3
"""Guard: the structure checker and its self-heal must cover the same cases.

The publish path is `check_digest_structure` -> `restore_digest_structure` ->
`check_digest_structure` (bare re-verify), and the corpus gate re-checks the
same property later with `test_every_digest_checkbox_lives_under_the_global_checklist`.
If any of those three disagree about *which* checkboxes are misplaced, the
self-heal reports success on a post that a later gate blocks.

That is not hypothetical. On 2026-09-06 the cron lost a publish day exactly this
way, and the self-heal step's own conclusion was ``success``:

    [digest-structure] FAIL — structural violations found in 1 digest post(s).
    ::warning:: … attempting restore_digest_structure self-heal.
    [digest-structure] OK — 1 digest post(s) checked, 0 violations.
    ...
    FAILED test_every_digest_checkbox_lives_under_the_global_checklist
      {'2026-09-06-…Patch_Agent.md': 'doc-wide=8 in-section=5'}

Root cause: the checker inspected only ``split("## 실무 체크리스트")[0]`` — the
half BEFORE the heading — and the fixer keyed on item regions (``### N.N`` …
next top-level section). A checkbox under ``## 참고 자료`` was outside every item
region AND after the heading, so neither half saw it. Measured before the fix:
the fixer reported ``rewrote 0/1`` and changed zero bytes.

Fixing only one half would have been a regression, not a fix: a checker that
sees the trailing case while the fixer cannot repair it just moves the lost day
from the corpus gate to the structure gate. Both are asserted here together.

Full trace: .omc/research/digest_structure_selfheal_gap_2026_09_08.md
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import check_digest_structure as cds
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXER = REPO_ROOT / "scripts" / "restore_digest_structure.py"

_FM = "---\ntitle: t\n---\n\n"
_DELIVERABLE = "## 실무 체크리스트\n\n- [ ] 전역 조치\n"

# Each is a real placement the pair used to handle inconsistently.
MISPLACED = {
    "item_body": _FM
    + "## 1. 보안\n\n### 1.1 기사\n\n본문.\n\n- [ ] 항목별 조치\n\n"
    + _DELIVERABLE,
    # After the heading: invisible to the old checker AND the old fixer.
    "after_the_checklist": _FM
    + "## 1. 보안\n\n### 1.1 기사\n\n본문.\n\n"
    + _DELIVERABLE
    + "\n## 참고 자료\n\n- [ ] 뒤쪽 항목\n",
    # Before the heading but outside any item region: the old checker flagged it
    # and the old fixer could not repair it, so the heal "succeeded" and the
    # bare re-verify blocked anyway.
    "non_item_top_section": _FM
    + "## 📊 빠른 참조\n\n- [ ] 요약 체크\n\n## 1. 보안\n\n### 1.1 기사\n\n본문.\n\n"
    + _DELIVERABLE,
    # A ticked box: the corpus guard's old `- [ ]` literal could not match it.
    "ticked_box": _FM
    + "## 1. 보안\n\n### 1.1 기사\n\n- [x] 완료된 항목\n\n"
    + _DELIVERABLE,
}

CLEAN = {
    # Prose advisory bullets are legitimate content and must not be touched.
    "prose_advisory": _FM
    + "## 1. 보안\n\n### 1.1 기사\n\n본문.\n\n- 산문 권고\n\n"
    + _DELIVERABLE,
    "checklist_only": _FM + "## 1. 보안\n\n### 1.1 기사\n\n본문.\n\n" + _DELIVERABLE,
}


def _corpus_rule(text: str) -> tuple:
    clean = "\n".join(cds._strip_code_fences(cds._body(text).split("\n")))
    return cds.misplaced_checkbox_counts(clean)


def _run_fixer(post: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(FIXER), str(post)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


def _write(tmp_path: Path, text: str) -> Path:
    post = tmp_path / "2026-12-31-Tech_Security_Weekly_Digest_Probe.md"
    post.write_text(text, encoding="utf-8")
    return post


@pytest.mark.parametrize("name", sorted(MISPLACED))
def test_checker_flags_every_misplacement(name):
    """Control for the pairing test: these fixtures really are violations."""
    violations = cds.check_text(MISPLACED[name])
    assert any("outside the global" in v for v in violations), (
        f"{name} is not detected, so the pairing assertion below would be "
        f"vacuous: {violations}"
    )


@pytest.mark.parametrize("name", sorted(MISPLACED))
def test_the_fixer_repairs_what_the_checker_flags(name):
    """checker FAIL -> heal -> checker OK -> corpus rule OK, in one pass."""
    tmp = Path(__import__("tempfile").mkdtemp())
    post = _write(tmp, MISPLACED[name])

    result = _run_fixer(post)
    assert result.returncode == 0, result.stderr[-400:]
    healed = post.read_text(encoding="utf-8")

    assert cds.check_text(healed) == [], (
        f"{name}: the fixer left a violation the bare re-verify will block on — "
        "that turns a corpus-gate failure into a structure-gate failure, the "
        f"same lost day one step earlier: {cds.check_text(healed)}"
    )
    doc_wide, in_section = _corpus_rule(healed)
    assert doc_wide == in_section, f"{name}: corpus gate would still block"
    assert "- [ ] 전역 조치" in healed, (
        f"{name}: the global checklist is the intended deliverable and must "
        "survive the heal"
    )


@pytest.mark.parametrize("name", sorted(CLEAN))
def test_a_clean_post_is_left_byte_identical(name):
    """The other half of the control.

    "The fixer repairs violations" also passes for a fixer that rewrites
    everything, and this one runs unattended on every cron publish.
    """
    tmp = Path(__import__("tempfile").mkdtemp())
    post = _write(tmp, CLEAN[name])
    original = post.read_bytes()

    assert cds.check_text(CLEAN[name]) == [], "fixture is not clean"
    assert _run_fixer(post).returncode == 0
    assert post.read_bytes() == original, f"{name} was modified"


def test_the_violation_message_keeps_its_counts_after_the_kind_separator():
    """`_kind` keys the structure ratchet on the text before ": ".

    With the counts embedded in the kind, editing an unrelated line that shifts
    a count would read as "one violation disappeared + one new appeared" — the
    spurious block the ratchet exists to remove.
    """
    violations = cds.check_text(MISPLACED["item_body"])
    misplaced = [v for v in violations if "outside the global" in v][0]
    assert ": " in misplaced, misplaced
    kind = cds._kind(misplaced)
    assert "doc-wide" not in kind and "in-section" not in kind, kind
